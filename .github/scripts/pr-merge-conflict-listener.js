'use strict';

const COMMENT_MARKER = '<!-- pr-merge-conflict-listener -->';
const CONFLICT_LABEL = {
  name: 'merge-conflict',
  color: 'd73a4a',
  description: 'This pull request has merge conflicts',
};
const MAX_MERGEABILITY_ATTEMPTS = 6;
const MERGEABILITY_RETRY_DELAY_MS = 2000;

const delay = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

async function getPullRequestNumbers(github, context) {
  if (context.payload.pull_request) {
    return [context.payload.pull_request.number];
  }

  const { owner, repo } = context.repo;
  const options = {
    owner,
    repo,
    state: 'open',
    per_page: 100,
  };

  if (context.eventName === 'push') {
    options.base = context.ref.replace(/^refs\/heads\//, '');
  }

  const pullRequests = await github.paginate(github.rest.pulls.list, options);
  return pullRequests.map((pullRequest) => pullRequest.number);
}

async function getMergeability(
  github,
  context,
  pullNumber,
  sleep,
  maxAttempts,
) {
  const { owner, repo } = context.repo;

  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    const { data: pullRequest } = await github.rest.pulls.get({
      owner,
      repo,
      pull_number: pullNumber,
    });

    if (pullRequest.mergeable !== null) {
      return pullRequest;
    }

    if (attempt < maxAttempts) {
      await sleep(MERGEABILITY_RETRY_DELAY_MS);
    }
  }

  return null;
}

async function ensureConflictLabel(github, context) {
  const { owner, repo } = context.repo;

  try {
    await github.rest.issues.getLabel({
      owner,
      repo,
      name: CONFLICT_LABEL.name,
    });
  } catch (error) {
    if (error.status !== 404) {
      throw error;
    }

    await github.rest.issues.createLabel({
      owner,
      repo,
      ...CONFLICT_LABEL,
    });
  }
}

async function findListenerComment(github, context, pullNumber) {
  const { owner, repo } = context.repo;
  const comments = await github.paginate(github.rest.issues.listComments, {
    owner,
    repo,
    issue_number: pullNumber,
    per_page: 100,
  });

  return comments.find(
    (comment) =>
      comment.user?.type === 'Bot' && comment.body?.includes(COMMENT_MARKER),
  );
}

function conflictComment(baseBranch) {
  return `${COMMENT_MARKER}
## Merge conflict detected

This pull request cannot currently be merged into \`${baseBranch}\`. Resolve the conflicts and push the updated branch; this listener will check it again automatically.`;
}

function resolvedComment(baseBranch) {
  return `${COMMENT_MARKER}
## Merge conflict resolved

This pull request no longer has merge conflicts with \`${baseBranch}\`.`;
}

async function setComment(github, context, pullNumber, existingComment, body) {
  if (existingComment?.body === body) {
    return;
  }

  const { owner, repo } = context.repo;
  if (existingComment) {
    await github.rest.issues.updateComment({
      owner,
      repo,
      comment_id: existingComment.id,
      body,
    });
    return;
  }

  await github.rest.issues.createComment({
    owner,
    repo,
    issue_number: pullNumber,
    body,
  });
}

async function markConflicting(github, context, pullRequest, existingComment) {
  const { owner, repo } = context.repo;
  const pullNumber = pullRequest.number;
  const hasConflictLabel = pullRequest.labels.some(
    (label) => label.name === CONFLICT_LABEL.name,
  );

  if (!hasConflictLabel) {
    await ensureConflictLabel(github, context);
    await github.rest.issues.addLabels({
      owner,
      repo,
      issue_number: pullNumber,
      labels: [CONFLICT_LABEL.name],
    });
  }

  await setComment(
    github,
    context,
    pullNumber,
    existingComment,
    conflictComment(pullRequest.base.ref),
  );
}

async function markResolved(github, context, pullRequest, existingComment) {
  const { owner, repo } = context.repo;
  const pullNumber = pullRequest.number;
  const hasConflictLabel = pullRequest.labels.some(
    (label) => label.name === CONFLICT_LABEL.name,
  );

  if (hasConflictLabel) {
    await github.rest.issues.removeLabel({
      owner,
      repo,
      issue_number: pullNumber,
      name: CONFLICT_LABEL.name,
    });
  }

  if (existingComment) {
    await setComment(
      github,
      context,
      pullNumber,
      existingComment,
      resolvedComment(pullRequest.base.ref),
    );
  }
}

async function listener({
  github,
  context,
  core,
  sleep = delay,
  maxAttempts = MAX_MERGEABILITY_ATTEMPTS,
}) {
  const pullNumbers = await getPullRequestNumbers(github, context);
  const unknownPullNumbers = [];

  for (const pullNumber of pullNumbers) {
    const pullRequest = await getMergeability(
      github,
      context,
      pullNumber,
      sleep,
      maxAttempts,
    );

    if (!pullRequest) {
      unknownPullNumbers.push(pullNumber);
      continue;
    }

    const existingComment = await findListenerComment(
      github,
      context,
      pullNumber,
    );

    if (
      pullRequest.mergeable === false ||
      pullRequest.mergeable_state === 'dirty'
    ) {
      await markConflicting(github, context, pullRequest, existingComment);
      core.info(`Pull request #${pullNumber} has merge conflicts.`);
    } else {
      await markResolved(github, context, pullRequest, existingComment);
      core.info(`Pull request #${pullNumber} has no merge conflicts.`);
    }
  }

  if (unknownPullNumbers.length > 0) {
    throw new Error(
      `GitHub did not calculate mergeability for pull request(s): ${unknownPullNumbers
        .map((number) => `#${number}`)
        .join(', ')}`,
    );
  }
}

module.exports = listener;
module.exports._private = {
  COMMENT_MARKER,
  CONFLICT_LABEL,
  conflictComment,
  getPullRequestNumbers,
  resolvedComment,
};
