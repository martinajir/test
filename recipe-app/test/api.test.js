// Minimal smoke test for the recipe API, run with `npm test`.
// Uses an isolated in-memory-like temp DB file so it never touches recipes.db.
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const http = require('http');

const TMP_DB = path.join(__dirname, 'test.db');
if (fs.existsSync(TMP_DB)) fs.unlinkSync(TMP_DB);
process.env.RECIPE_DB_PATH = TMP_DB;

const app = require('../server');

async function run() {
  const server = app.listen(0);
  const { port } = server.address();
  const base = `http://localhost:${port}`;

  try {
    // No recipes initially
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

    // Get one
    res = await fetch(`${base}/api/recipes/${created.id}`);
    assert.strictEqual(res.status, 200);

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

    res = await fetch(`${base}/api/recipes/${created.id}`);
    assert.strictEqual(res.status, 404);

    console.log('All tests passed.');
  } finally {
    server.close();
    if (fs.existsSync(TMP_DB)) fs.unlinkSync(TMP_DB);
    if (fs.existsSync(TMP_DB + '-wal')) fs.unlinkSync(TMP_DB + '-wal');
    if (fs.existsSync(TMP_DB + '-shm')) fs.unlinkSync(TMP_DB + '-shm');
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
