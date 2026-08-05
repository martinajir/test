'use strict';

const express = require('express');
const { createRecipesRouter } = require('./routes/recipes');

/** Builds an Express app wired to the given db connection. Kept separate from
 * server startup so tests can create an app around an in-memory database.
 */
function createApp(db) {
  const app = express();
  app.use(express.json());

  app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
  });

  app.use('/recipes', createRecipesRouter(db));

  // Basic error handler so uncaught errors return JSON instead of HTML.
  // eslint-disable-next-line no-unused-vars
  app.use((err, req, res, next) => {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  });

  return app;
}

module.exports = { createApp };
