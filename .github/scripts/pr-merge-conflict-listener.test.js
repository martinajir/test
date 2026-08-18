const assert = require("node:assert/strict");
const { test } = require("node:test");

const run = require("./pr-merge-conflict-listener");
const { COMMENT_MARKER, CONFLICT_LABEL } = run.constants;

function createHarness({
  mergeable,
  existingComments = [],
  pullRequestNumber = 42,
  labelExists = true,
} = {}) {
  const calls = [];
  const github = {
    paginate: async (method, params) => method(params),
    rest: {
      issues: {
        addLabels: async (params) => calls.push(["addLabels", params]),
        createComment: async (params) => calls.push(["createComment", params]),
        createLabel: async (params) => calls.push(["createLabel", params]),
        getLabel: async (params) => {
          calls.push(["getLabel", params]);
          if (!labelExists) {
            throw Object.assign(new Error("Not found"), { status: 404 });
          }
        },
        listComments: async () => existingComments,
        removeLabel: async (params) => calls.push(["removeLabel", params]),
      },
      pulls: {
        get: async (params) => {
          calls.push(["getPull", params]);
          return { data: { mergeable } };
        },
        list: async (params) => {
          calls.push(["listPulls", params]);
          return [{ number: pullRequestNumber }];
        },
      },
    },
  };
  const context = {
    repo: { owner: "octo", repo: "example" },
    payload: {
      pull_request: { number: pullRequestNumber },
      repository: { default_branch: "main" },
    },
  };
  const core = {
    info: (message) => calls.push(["info", message]),
    warning: (message) => calls.push(["warning", message]),
  };

  return { calls, context, core, github };
}

test("labels and comments on a conflicting pull request", async () => {
  const harness = createHarness({ mergeable: false, labelExists: false });

  await run({ ...harness, sleep: async () => {} });

  assert.ok(harness.calls.some(([name]) => name === "createLabel"));
  assert.ok(
    harness.calls.some(
      ([name, params]) =>
        name === "addLabels" && params.labels.includes(CONFLICT_LABEL),
    ),
  );
  assert.ok(
    harness.calls.some(
      ([name, params]) =>
        name === "createComment" && params.body.includes(COMMENT_MARKER),
    ),
  );
});

test("does not duplicate an existing conflict comment", async () => {
  const harness = createHarness({
    mergeable: false,
    existingComments: [{ body: `${COMMENT_MARKER}\nAlready posted` }],
  });

  await run({ ...harness, sleep: async () => {} });

  assert.equal(
    harness.calls.filter(([name]) => name === "createComment").length,
    0,
  );
});

test("removes the conflict label when a pull request is mergeable", async () => {
  const harness = createHarness({ mergeable: true });

  await run({ ...harness, sleep: async () => {} });

  assert.ok(
    harness.calls.some(
      ([name, params]) =>
        name === "removeLabel" && params.name === CONFLICT_LABEL,
    ),
  );
});

test("warns without changing labels while mergeability is unknown", async () => {
  const harness = createHarness({ mergeable: null });

  await run({ ...harness, sleep: async () => {} });

  assert.equal(
    harness.calls.filter(([name]) => name === "getPull").length,
    6,
  );
  assert.equal(
    harness.calls.filter(
      ([name]) => name === "addLabels" || name === "removeLabel",
    ).length,
    0,
  );
  assert.ok(harness.calls.some(([name]) => name === "warning"));
});

test("scans open pull requests after the base branch changes", async () => {
  const harness = createHarness({ mergeable: true, pullRequestNumber: 17 });
  delete harness.context.payload.pull_request;

  await run({ ...harness, sleep: async () => {} });

  assert.ok(
    harness.calls.some(
      ([name, params]) =>
        name === "listPulls" &&
        params.base === "main" &&
        params.state === "open",
    ),
  );
  assert.ok(
    harness.calls.some(
      ([name, params]) => name === "getPull" && params.pull_number === 17,
    ),
  );
});
