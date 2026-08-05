'use strict';

const { test, before, beforeEach } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { DatabaseSync } = require('node:sqlite');

const { migrate } = require('../src/db/schema');
const { createApp } = require('../src/app');

let server;
let baseUrl;
let db;

function request(method, path, body) {
  return new Promise((resolve, reject) => {
    const data = body !== undefined ? JSON.stringify(body) : undefined;
    const req = http.request(
      `${baseUrl}${path}`,
      {
        method,
        headers: data ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } : {},
      },
      (res) => {
        let chunks = '';
        res.on('data', (chunk) => (chunks += chunk));
        res.on('end', () => {
          let parsed;
          try {
            parsed = chunks ? JSON.parse(chunks) : undefined;
          } catch {
            parsed = chunks;
          }
          resolve({ status: res.statusCode, body: parsed });
        });
      }
    );
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

beforeEach(() => {
  db = new DatabaseSync(':memory:');
  migrate(db);
  const app = createApp(db);
  server = http.createServer(app);
  server.listen(0);
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

test('GET /recipes returns an empty list initially', async () => {
  const res = await request('GET', '/recipes');
  assert.equal(res.status, 200);
  assert.deepEqual(res.body, []);
  server.close();
});

test('POST /recipes creates a recipe with ingredients and instructions', async () => {
  const res = await request('POST', '/recipes', {
    title: 'Tomato Soup',
    description: 'Simple tomato soup',
    ingredients: ['2 cans tomatoes', '1 onion'],
    instructions: ['Simmer everything', 'Blend and serve'],
  });
  assert.equal(res.status, 201);
  assert.equal(res.body.title, 'Tomato Soup');
  assert.deepEqual(res.body.ingredients, ['2 cans tomatoes', '1 onion']);
  assert.deepEqual(res.body.instructions, ['Simmer everything', 'Blend and serve']);
  server.close();
});

test('POST /recipes without a title returns 400', async () => {
  const res = await request('POST', '/recipes', { description: 'no title' });
  assert.equal(res.status, 400);
  server.close();
});

test('POST /recipes with duplicate title returns 409', async () => {
  await request('POST', '/recipes', { title: 'Dup Soup' });
  const res = await request('POST', '/recipes', { title: 'Dup Soup' });
  assert.equal(res.status, 409);
  server.close();
});

test('GET /recipes/:id returns 404 for missing recipe', async () => {
  const res = await request('GET', '/recipes/999');
  assert.equal(res.status, 404);
  server.close();
});

test('GET /recipes/:id returns the created recipe', async () => {
  const created = await request('POST', '/recipes', { title: 'Pea Soup', ingredients: ['peas'], instructions: ['cook'] });
  const res = await request('GET', `/recipes/${created.body.id}`);
  assert.equal(res.status, 200);
  assert.equal(res.body.title, 'Pea Soup');
  server.close();
});

test('PUT /recipes/:id updates a recipe', async () => {
  const created = await request('POST', '/recipes', { title: 'Old Title', ingredients: ['a'], instructions: ['b'] });
  const res = await request('PUT', `/recipes/${created.body.id}`, {
    title: 'New Title',
    ingredients: ['a', 'b'],
  });
  assert.equal(res.status, 200);
  assert.equal(res.body.title, 'New Title');
  assert.deepEqual(res.body.ingredients, ['a', 'b']);
  assert.deepEqual(res.body.instructions, ['b']); // unchanged
  server.close();
});

test('PUT /recipes/:id returns 404 for missing recipe', async () => {
  const res = await request('PUT', '/recipes/999', { title: 'Nope' });
  assert.equal(res.status, 404);
  server.close();
});

test('DELETE /recipes/:id removes a recipe', async () => {
  const created = await request('POST', '/recipes', { title: 'Delete Me' });
  const del = await request('DELETE', `/recipes/${created.body.id}`);
  assert.equal(del.status, 204);
  const getRes = await request('GET', `/recipes/${created.body.id}`);
  assert.equal(getRes.status, 404);
  server.close();
});

test('DELETE /recipes/:id returns 404 for missing recipe', async () => {
  const res = await request('DELETE', '/recipes/999');
  assert.equal(res.status, 404);
  server.close();
});
