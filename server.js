#!/usr/bin/env node
'use strict';

/**
 * A simple Node.js web server (no external dependencies) for the test repo.
 *
 * Routes:
 *   GET /            Home page with links to available endpoints
 *   GET /joke        Returns a random pirate joke
 *   GET /add         Adds two numbers passed as query params `a` and `b`
 *   GET /healthz     Basic health check
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const PORT = process.env.PORT || 5000;
const JOKES_FILE = path.join(__dirname, 'pirate-jokes.txt');

function loadJokes() {
  const contents = fs.readFileSync(JOKES_FILE, 'utf-8');
  return contents
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => /^\d+\./.test(line))
    .map((line) => line.slice(line.indexOf('.') + 1).trim());
}

function sendJson(res, statusCode, body) {
  const data = JSON.stringify(body, null, 2);
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(data);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (url.pathname === '/' && req.method === 'GET') {
    sendJson(res, 200, {
      message: 'Ahoy! Welcome to the simple web server.',
      endpoints: {
        '/joke': 'Get a random pirate joke',
        '/add?a=<num>&b=<num>': 'Add two numbers',
        '/healthz': 'Health check',
      },
    });
  } else if (url.pathname === '/joke' && req.method === 'GET') {
    const jokes = loadJokes();
    if (jokes.length === 0) {
      sendJson(res, 404, { error: 'No jokes found' });
      return;
    }
    const joke = jokes[Math.floor(Math.random() * jokes.length)];
    sendJson(res, 200, { joke });
  } else if (url.pathname === '/add' && req.method === 'GET') {
    const aRaw = url.searchParams.get('a');
    const bRaw = url.searchParams.get('b');
    if (aRaw === null || bRaw === null) {
      sendJson(res, 400, { error: "Please provide both 'a' and 'b' query params" });
      return;
    }
    const a = Number(aRaw);
    const b = Number(bRaw);
    if (Number.isNaN(a) || Number.isNaN(b)) {
      sendJson(res, 400, { error: "'a' and 'b' must be numbers" });
      return;
    }
    sendJson(res, 200, { a, b, sum: a + b });
  } else if (url.pathname === '/healthz' && req.method === 'GET') {
    sendJson(res, 200, { status: 'ok' });
  } else {
    sendJson(res, 404, { error: 'Not found' });
  }
});

if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`Server listening on http://localhost:${PORT}`);
  });
}

module.exports = server;
