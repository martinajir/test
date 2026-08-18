'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const listener = require('./pr-merge-conflict-listener');

function createHarness({
  eventName = 'pull_request_target',
  ref = 'refs/heads/main',
  pullRequestNumber = 17,
  pullRequests = [],
  pullResponses,
  comments = [],
  labelExists = true,
}) {
  const calls = {
    addLabels: [],
    createComment: [],
    createLabel: [],
    listPulls: [],
    removeLabel: [],
    updateComment: [],
  };
  let responseIndex = 0;

  const github = {
    paginate: async (method, options) => {
      if (method === github.rest.pulls.list) {
        calls.listPulls.push(options);
        return pullRequests;
      }
      return comments;
    },
    rest: {
      pulls: {
        list: Symbol('pulls.list'),
        get: async () => ({
          data: pullResponses[
            Math.min(responseIndex++, pullResponses.length - 1)
          ],
        }),
      },
      issues: {
        listComments: Symbol('issues.listComments'),
        getLabel: async () => {
          if (!labelExists) {
            const error = new Error('Not Found');
            error.status = 404;
            throw error;
          }
        },
        createLabel: async (options) => calls.createLabel.push(options),
        addLabels: async (options) => calls.addLabels.push(options),
        removeLabel: async (options) => calls.removeLabel.push(options),
        createComment: async (options) => calls.createComment.push(options),
        updateComment: async (options) => calls.updateComment.push(options),
      },
    },
  };

  const context = {
    eventName,
    ref,
    repo: { owner: 'octo', repo: 'example' },
    payload:
      eventName === 'pull_request_target'
        ? { pull_request: { number: pullRequestNumber } }
        : {},
  };

  return {
    calls,
    context,
    core: { info: () => {} },
    github,
  };
}

test('labels and comments on a conflicting pull request', async () => {
  const harness = createHarness({
    labelExists: false,
    pullResponses: [
      {
        number: 17,
        mergeable: false,
        mergeable_state: 'dirty',
        base: { ref: 'main' },
        labels: [],
      },
    ],
  });

  await listener({ ...harness, sleep: async () => {}, maxAttempts: 1 });

  assert.equal(harness.calls.createLabel.length, 1);
  assert.deepEqual(harness.calls.addLabels[0].labels, ['merge-conflict']);
  assert.match(
    harness.calls.createComment[0].body,
    /Merge conflict detected/,
  );
});

test('removes the label and updates the listener comment after resolution', async () => {
  const harness = createHarness({
    pullResponses: [
      {
        number: 17,
        mergeable: true,
        mergeable_state: 'clean',
        base: { ref: 'main' },
        labels: [{ name: 'merge-conflict' }],
      },
    ],
    comments: [
      {
        id: 42,
        user: { type: 'Bot' },
        body: `${listener._private.COMMENT_MARKER}\nOld status`,
      },
    ],
  });

  await listener({ ...harness, sleep: async () => {}, maxAttempts: 1 });

  assert.equal(harness.calls.removeLabel.length, 1);
  assert.equal(harness.calls.updateComment[0].comment_id, 42);
  assert.match(
    harness.calls.updateComment[0].body,
    /Merge conflict resolved/,
  );
  assert.equal(harness.calls.createComment.length, 0);
});

test('checks only pull requests based on the pushed branch', async () => {
  const harness = createHarness({
    eventName: 'push',
    ref: 'refs/heads/release',
    pullRequests: [{ number: 31 }],
    pullResponses: [
      {
        number: 31,
        mergeable: true,
        mergeable_state: 'behind',
        base: { ref: 'release' },
        labels: [],
      },
    ],
  });

  await listener({ ...harness, sleep: async () => {}, maxAttempts: 1 });

  assert.equal(harness.calls.listPulls[0].base, 'release');
  assert.equal(harness.calls.createComment.length, 0);
});

test('checks all open pull requests during a scheduled scan', async () => {
  const harness = createHarness({
    eventName: 'schedule',
    pullRequests: [{ number: 31 }],
    pullResponses: [
      {
        number: 31,
        mergeable: true,
        mergeable_state: 'clean',
        base: { ref: 'release' },
        labels: [],
      },
    ],
  });

  await listener({ ...harness, sleep: async () => {}, maxAttempts: 1 });

  assert.equal(harness.calls.listPulls[0].base, undefined);
});

test('fails after GitHub repeatedly returns unknown mergeability', async () => {
  const harness = createHarness({
    pullResponses: [
      {
        number: 17,
        mergeable: null,
        mergeable_state: 'unknown',
        base: { ref: 'main' },
        labels: [],
      },
    ],
  });

  await assert.rejects(
    listener({ ...harness, sleep: async () => {}, maxAttempts: 2 }),
    /did not calculate mergeability.*#17/,
  );
});
