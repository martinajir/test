const assert = require("node:assert/strict");
const test = require("node:test");

const run = require("./merge-conflict-listener");

function createFixture({
  eventName = "pull_request_target",
  pullRequests = [],
  comments = [],
} = {}) {
  const calls = {
    created: [],
    deleted: [],
    listedPullRequests: [],
    updated: [],
  };
  const pullRequestQueue = [...pullRequests];
  const storedComments = [...comments];

  const github = {
    paginate: async (method, parameters) => {
      if (method === github.rest.pulls.list) {
        calls.listedPullRequests.push(parameters);
        return pullRequests;
      }

      return storedComments;
    },
    rest: {
      issues: {
        createComment: async (parameters) => {
          calls.created.push(parameters);
          storedComments.push({
            id: storedComments.length + 100,
            body: parameters.body,
            user: { type: "Bot" },
          });
        },
        deleteComment: async (parameters) => {
          calls.deleted.push(parameters);
          const index = storedComments.findIndex(
            (comment) => comment.id === parameters.comment_id,
          );
          storedComments.splice(index, 1);
        },
        listComments: async () => {},
        updateComment: async (parameters) => {
          calls.updated.push(parameters);
        },
      },
      pulls: {
        get: async () => ({
          data:
            pullRequestQueue.length > 1
              ? pullRequestQueue.shift()
              : pullRequestQueue[0],
        }),
        list: async () => {},
      },
    },
  };
  const context = {
    eventName,
    payload:
      eventName === "pull_request_target"
        ? {
            pull_request: {
              number: pullRequests[0]?.number,
              state: pullRequests[0]?.state ?? "open",
            },
          }
        : {},
    ref: "refs/heads/main",
    repo: { owner: "octo", repo: "example" },
  };
  const core = { info: () => {} };

  return { calls, context, core, github, storedComments };
}

test("creates one conflict notice without duplicating it", async () => {
  const pullRequest = {
    number: 12,
    mergeable: false,
    base: { ref: "main" },
  };
  const fixture = createFixture({ pullRequests: [pullRequest] });

  await run(fixture);
  await run(fixture);

  assert.equal(fixture.calls.created.length, 1);
  assert.match(fixture.calls.created[0].body, /Merge conflict detected/);
});

test("removes only the bot conflict notice when a pull request is mergeable", async () => {
  const pullRequest = {
    number: 13,
    mergeable: true,
    base: { ref: "main" },
  };
  const fixture = createFixture({
    pullRequests: [pullRequest],
    comments: [
      {
        id: 1,
        body: run.COMMENT_MARKER,
        user: { type: "User" },
      },
      {
        id: 2,
        body: run.COMMENT_MARKER,
        user: { type: "Bot" },
      },
    ],
  });

  await run(fixture);

  assert.deepEqual(fixture.calls.deleted, [
    { owner: "octo", repo: "example", comment_id: 2 },
  ]);
  assert.equal(fixture.storedComments[0].user.type, "User");
});

test("waits for GitHub to calculate mergeability", async () => {
  const fixture = createFixture({
    pullRequests: [
      { number: 14, mergeable: null, base: { ref: "main" } },
      { number: 14, mergeable: false, base: { ref: "main" } },
    ],
  });
  let sleepCount = 0;

  await run({
    ...fixture,
    sleep: async () => {
      sleepCount += 1;
    },
  });

  assert.equal(sleepCount, 1);
  assert.equal(fixture.calls.created.length, 1);
});

test("checks open pull requests targeting a pushed branch", async () => {
  const fixture = createFixture({
    eventName: "push",
    pullRequests: [{ number: 15, mergeable: true, base: { ref: "main" } }],
  });

  await run(fixture);

  assert.equal(fixture.calls.listedPullRequests[0].base, "main");
});

test("fails when GitHub does not calculate mergeability", async () => {
  const fixture = createFixture({
    pullRequests: [
      { number: 16, mergeable: null, base: { ref: "main" } },
    ],
  });

  await assert.rejects(
    run({ ...fixture, maxAttempts: 2, sleep: async () => {} }),
    /#16/,
  );
});
