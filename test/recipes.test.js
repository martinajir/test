'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { openDatabase } = require('../db/database');
const { createApp } = require('../src/app');

function makeApp() {
  const db = openDatabase(':memory:');
  return createApp(db);
}

async function request(app, method, path, body) {
  const server = app.listen(0);
  const { port } = server.address();
  try {
    const res = await fetch(`http://127.0.0.1:${port}${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    const text = await res.text();
    const json = text ? JSON.parse(text) : null;
    return { status: res.status, body: json };
  } finally {
    server.close();
  }
}

test('GET /recipes returns an empty list initially', async () => {
  const app = makeApp();
  const res = await request(app, 'GET', '/recipes');
  assert.equal(res.status, 200);
  assert.deepEqual(res.body, []);
});

test('POST /recipes creates a recipe', async () => {
  const app = makeApp();
  const res = await request(app, 'POST', '/recipes', {
    title: 'Pancakes',
    description: 'Fluffy breakfast pancakes',
    ingredients: ['flour', 'milk', 'eggs'],
    instructions: ['Mix', 'Cook', 'Serve'],
  });

  assert.equal(res.status, 201);
  assert.equal(res.body.title, 'Pancakes');
  assert.deepEqual(res.body.ingredients, ['flour', 'milk', 'eggs']);
  assert.ok(res.body.id);
});

test('POST /recipes rejects missing fields', async () => {
  const app = makeApp();
  const res = await request(app, 'POST', '/recipes', { title: 'Incomplete' });
  assert.equal(res.status, 400);
});

test('GET /recipes/:id returns a single recipe', async () => {
  const app = makeApp();
  const created = await request(app, 'POST', '/recipes', {
    title: 'Tea',
    ingredients: ['water', 'tea leaves'],
    instructions: ['Boil water', 'Steep tea'],
  });

  const res = await request(app, 'GET', `/recipes/${created.body.id}`);
  assert.equal(res.status, 200);
  assert.equal(res.body.title, 'Tea');
});

test('GET /recipes/:id returns 404 for unknown id', async () => {
  const app = makeApp();
  const res = await request(app, 'GET', '/recipes/9999');
  assert.equal(res.status, 404);
});

test('PUT /recipes/:id updates a recipe', async () => {
  const app = makeApp();
  const created = await request(app, 'POST', '/recipes', {
    title: 'Toast',
    ingredients: ['bread'],
    instructions: ['Toast it'],
  });

  const res = await request(app, 'PUT', `/recipes/${created.body.id}`, {
    title: 'Buttered Toast',
    ingredients: ['bread', 'butter'],
  });

  assert.equal(res.status, 200);
  assert.equal(res.body.title, 'Buttered Toast');
  assert.deepEqual(res.body.ingredients, ['bread', 'butter']);
  assert.deepEqual(res.body.instructions, ['Toast it']);
});

test('PUT /recipes/:id returns 404 for unknown id', async () => {
  const app = makeApp();
  const res = await request(app, 'PUT', '/recipes/9999', { title: 'Nope' });
  assert.equal(res.status, 404);
});

test('DELETE /recipes/:id removes a recipe', async () => {
  const app = makeApp();
  const created = await request(app, 'POST', '/recipes', {
    title: 'Soup',
    ingredients: ['water'],
    instructions: ['Boil'],
  });

  const delRes = await request(app, 'DELETE', `/recipes/${created.body.id}`);
  assert.equal(delRes.status, 204);

  const getRes = await request(app, 'GET', `/recipes/${created.body.id}`);
  assert.equal(getRes.status, 404);
});

test('DELETE /recipes/:id returns 404 for unknown id', async () => {
  const app = makeApp();
  const res = await request(app, 'DELETE', '/recipes/9999');
  assert.equal(res.status, 404);
});
