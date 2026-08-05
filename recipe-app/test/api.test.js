// Unit tests for the recipe API using aws-sdk-client-mock to stub DynamoDB,
// so tests run without any real AWS account or DynamoDB Local instance.
const assert = require('assert');
const { mockClient } = require('aws-sdk-client-mock');
const { DynamoDBDocumentClient } = require('@aws-sdk/lib-dynamodb');

const ddbMock = mockClient(DynamoDBDocumentClient);

const app = require('../server');

async function run() {
  const server = app.listen(0);
  const { port } = server.address();
  const base = `http://localhost:${port}`;

  try {
    // No recipes initially
    ddbMock.reset();
    ddbMock.onAnyCommand().resolves({});
    let res = await fetch(`${base}/api/recipes`);
    assert.strictEqual(res.status, 200);
    let list = await res.json();
    assert.strictEqual(list.length, 0, 'expected empty recipe list');

    // Create
    res = await fetch(`${base}/api/recipes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: 'Test Soup',
        ingredients: ['water', 'salt'],
        instructions: ['Boil water', 'Add salt'],
      }),
    });
    assert.strictEqual(res.status, 201);
    const created = await res.json();
    assert.strictEqual(created.title, 'Test Soup');
    assert.deepStrictEqual(created.ingredients, ['water', 'salt']);
    assert.ok(created.id, 'expected generated id');

    // Get one - stub GetCommand to return the item we just "created"
    ddbMock.onAnyCommand().resolves({ Item: created });
    res = await fetch(`${base}/api/recipes/${created.id}`);
    assert.strictEqual(res.status, 200);
    const fetched = await res.json();
    assert.strictEqual(fetched.title, 'Test Soup');

    // Update
    res = await fetch(`${base}/api/recipes/${created.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: 'Updated Soup' }),
    });
    assert.strictEqual(res.status, 200);
    const updated = await res.json();
    assert.strictEqual(updated.title, 'Updated Soup');

    // Validation error
    res = await fetch(`${base}/api/recipes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: '' }),
    });
    assert.strictEqual(res.status, 400);

    // Delete
    res = await fetch(`${base}/api/recipes/${created.id}`, { method: 'DELETE' });
    assert.strictEqual(res.status, 204);

    // Not found - simulate the item no longer existing
    ddbMock.onAnyCommand().resolves({});
    res = await fetch(`${base}/api/recipes/${created.id}`);
    assert.strictEqual(res.status, 404);

    console.log('All tests passed.');
  } finally {
    server.close();
    ddbMock.restore();
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
