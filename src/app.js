'use strict';

const express = require('express');
const { RecipeRepository } = require('../db/recipeRepository');

/**
 * Builds the Express app for the recipe repository API.
 * @param {import('node:sqlite').DatabaseSync} db
 */
function createApp(db) {
  const repo = new RecipeRepository(db);
  const app = express();
  app.use(express.json());

  app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
  });

  app.get('/recipes', (req, res) => {
    res.json(repo.list());
  });

  app.get('/recipes/:id', (req, res) => {
    const recipe = repo.getById(Number(req.params.id));
    if (!recipe) return res.status(404).json({ error: 'Recipe not found' });
    res.json(recipe);
  });

  app.post('/recipes', (req, res) => {
    const { title, description, ingredients, instructions } = req.body || {};

    if (!title || !Array.isArray(ingredients) || !Array.isArray(instructions)) {
      return res.status(400).json({
        error: 'title, ingredients (array), and instructions (array) are required',
      });
    }

    const recipe = repo.create({ title, description, ingredients, instructions });
    res.status(201).json(recipe);
  });

  app.put('/recipes/:id', (req, res) => {
    const id = Number(req.params.id);
    const { title, description, ingredients, instructions } = req.body || {};

    if (ingredients !== undefined && !Array.isArray(ingredients)) {
      return res.status(400).json({ error: 'ingredients must be an array' });
    }
    if (instructions !== undefined && !Array.isArray(instructions)) {
      return res.status(400).json({ error: 'instructions must be an array' });
    }

    const updated = repo.update(id, { title, description, ingredients, instructions });
    if (!updated) return res.status(404).json({ error: 'Recipe not found' });
    res.json(updated);
  });

  app.delete('/recipes/:id', (req, res) => {
    const deleted = repo.delete(Number(req.params.id));
    if (!deleted) return res.status(404).json({ error: 'Recipe not found' });
    res.status(204).end();
  });

  return app;
}

module.exports = { createApp };
