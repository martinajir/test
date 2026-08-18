const COMMENT_MARKER = "<!-- merge-conflict-listener -->";
const DEFAULT_POLL_ATTEMPTS = 6;
const DEFAULT_POLL_DELAY_MS = 2_000;

const delay = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));

function commentBody(pullRequest) {
  return `${COMMENT_MARKER}
## Merge conflict detected

This pull request conflicts with \`${pullRequest.base.ref}\`. Resolve the conflicts before merging.

This notice will be removed automatically when the pull request becomes mergeable.`;
}

async function listPullRequests({ github, context }) {
  const { owner, repo } = context.repo;

  if (context.payload.pull_request) {
    return [
      {
        number: context.payload.pull_request.number,
        closed: context.payload.pull_request.state === "closed",
      },
    ];
  }

  const parameters = {
    owner,
    repo,
    state: "open",
    per_page: 100,
  };

  if (context.eventName === "push") {
    parameters.base = context.ref.replace("refs/heads/", "");
  }

  const pullRequests = await github.paginate(
    github.rest.pulls.list,
    parameters,
  );

  return pullRequests.map((pullRequest) => ({
    number: pullRequest.number,
    closed: false,
  }));
}

async function getMergeability({
  github,
  context,
  pullNumber,
  maxAttempts,
  sleep,
}) {
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
      await sleep(DEFAULT_POLL_DELAY_MS);
    }
  }

  return null;
}

async function findListenerComment({ github, context, pullNumber }) {
  const { owner, repo } = context.repo;
  const comments = await github.paginate(github.rest.issues.listComments, {
    owner,
    repo,
    issue_number: pullNumber,
    per_page: 100,
  });

  return comments.find(
    (comment) =>
      comment.user?.type === "Bot" && comment.body?.includes(COMMENT_MARKER),
  );
}

async function removeListenerComment({
  github,
  context,
  core,
  pullNumber,
}) {
  const comment = await findListenerComment({
    github,
    context,
    pullNumber,
  });

  if (!comment) {
    return;
  }

  await github.rest.issues.deleteComment({
    ...context.repo,
    comment_id: comment.id,
  });
  core.info(`Removed the conflict notice from pull request #${pullNumber}.`);
}

async function addOrUpdateListenerComment({
  github,
  context,
  core,
  pullRequest,
}) {
  const comment = await findListenerComment({
    github,
    context,
    pullNumber: pullRequest.number,
  });
  const body = commentBody(pullRequest);

  if (!comment) {
    await github.rest.issues.createComment({
      ...context.repo,
      issue_number: pullRequest.number,
      body,
    });
    core.info(`Added a conflict notice to pull request #${pullRequest.number}.`);
    return;
  }

  if (comment.body !== body) {
    await github.rest.issues.updateComment({
      ...context.repo,
      comment_id: comment.id,
      body,
    });
    core.info(
      `Updated the conflict notice on pull request #${pullRequest.number}.`,
    );
  }
}

async function run({
  github,
  context,
  core,
  maxAttempts = DEFAULT_POLL_ATTEMPTS,
  sleep = delay,
}) {
  const pullRequests = await listPullRequests({ github, context });
  const unresolved = [];

  for (const pullRequest of pullRequests) {
    if (pullRequest.closed) {
      await removeListenerComment({
        github,
        context,
        core,
        pullNumber: pullRequest.number,
      });
      continue;
    }

    const currentPullRequest = await getMergeability({
      github,
      context,
      pullNumber: pullRequest.number,
      maxAttempts,
      sleep,
    });

    if (!currentPullRequest) {
      unresolved.push(pullRequest.number);
      continue;
    }

    if (currentPullRequest.mergeable === false) {
      await addOrUpdateListenerComment({
        github,
        context,
        core,
        pullRequest: currentPullRequest,
      });
    } else {
      await removeListenerComment({
        github,
        context,
        core,
        pullNumber: currentPullRequest.number,
      });
      core.info(`Pull request #${currentPullRequest.number} is mergeable.`);
    }
  }

  if (unresolved.length > 0) {
    throw new Error(
      `GitHub did not calculate mergeability for pull request(s): ${unresolved
        .map((number) => `#${number}`)
        .join(", ")}`,
    );
  }
}

module.exports = run;
module.exports.COMMENT_MARKER = COMMENT_MARKER;
