const CONFLICT_LABEL = "merge-conflict";
const COMMENT_MARKER = "<!-- pr-merge-conflict-listener -->";
const COMMENT_BODY = `${COMMENT_MARKER}
This pull request currently has merge conflicts. Please update the branch with the latest base branch and resolve the conflicts before merging.`;

function isNotFound(error) {
  return error?.status === 404;
}

async function ensureConflictLabel(github, owner, repo) {
  try {
    await github.rest.issues.getLabel({
      owner,
      repo,
      name: CONFLICT_LABEL,
    });
  } catch (error) {
    if (!isNotFound(error)) {
      throw error;
    }

    try {
      await github.rest.issues.createLabel({
        owner,
        repo,
        name: CONFLICT_LABEL,
        color: "d73a4a",
        description: "This pull request has merge conflicts",
      });
    } catch (createError) {
      // Another concurrent run may have created the repository label.
      if (createError.status !== 422) {
        throw createError;
      }
    }
  }
}

async function getMergeability(github, owner, repo, pullNumber, sleep) {
  for (let attempt = 0; attempt < 6; attempt += 1) {
    const { data: pull } = await github.rest.pulls.get({
      owner,
      repo,
      pull_number: pullNumber,
    });

    if (pull.mergeable !== null) {
      return pull.mergeable;
    }

    if (attempt < 5) {
      await sleep(5000);
    }
  }

  return null;
}

async function addConflictNotice(github, owner, repo, pullNumber) {
  await github.rest.issues.addLabels({
    owner,
    repo,
    issue_number: pullNumber,
    labels: [CONFLICT_LABEL],
  });

  const comments = await github.paginate(github.rest.issues.listComments, {
    owner,
    repo,
    issue_number: pullNumber,
    per_page: 100,
  });

  if (!comments.some((comment) => comment.body?.includes(COMMENT_MARKER))) {
    await github.rest.issues.createComment({
      owner,
      repo,
      issue_number: pullNumber,
      body: COMMENT_BODY,
    });
  }
}

async function removeConflictLabel(github, owner, repo, pullNumber) {
  try {
    await github.rest.issues.removeLabel({
      owner,
      repo,
      issue_number: pullNumber,
      name: CONFLICT_LABEL,
    });
  } catch (error) {
    if (!isNotFound(error)) {
      throw error;
    }
  }
}

async function getPullNumbers(github, context) {
  if (context.payload.pull_request) {
    return [context.payload.pull_request.number];
  }

  const pulls = await github.paginate(github.rest.pulls.list, {
    owner: context.repo.owner,
    repo: context.repo.repo,
    state: "open",
    base: context.payload.repository.default_branch,
    per_page: 100,
  });

  return pulls.map((pull) => pull.number);
}

async function run({ github, context, core, sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)) }) {
  const { owner, repo } = context.repo;
  const pullNumbers = await getPullNumbers(github, context);

  if (pullNumbers.length === 0) {
    core.info("No open pull requests to inspect.");
    return;
  }

  for (const pullNumber of pullNumbers) {
    const mergeable = await getMergeability(
      github,
      owner,
      repo,
      pullNumber,
      sleep,
    );

    if (mergeable === null) {
      core.warning(`Mergeability for pull request #${pullNumber} is still unknown.`);
    } else if (mergeable) {
      await removeConflictLabel(github, owner, repo, pullNumber);
      core.info(`Pull request #${pullNumber} has no merge conflicts.`);
    } else {
      await ensureConflictLabel(github, owner, repo);
      await addConflictNotice(github, owner, repo, pullNumber);
      core.warning(`Pull request #${pullNumber} has merge conflicts.`);
    }
  }
}

module.exports = run;
module.exports.constants = {
  COMMENT_MARKER,
  CONFLICT_LABEL,
};
