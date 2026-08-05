'use strict';

const express = require('express');
const repo = require('../db/recipes-repository');

function createRecipesRouter(db) {
  const router = express.Router();

  router.get('/', (req, res) => {
    res.json(repo.listRecipes(db));
  });

  router.get('/:id', (req, res) => {
    const recipe = repo.getRecipeById(db, Number(req.params.id));
    if (!recipe) {
      return res.status(404).json({ error: 'Recipe not found' });
    }
    res.json(recipe);
  });

  router.post('/', (req, res) => {
    try {
      const recipe = repo.createRecipe(db, req.body || {});
      res.status(201).json(recipe);
    } catch (err) {
      if (err instanceof repo.ValidationError) {
        return res.status(400).json({ error: err.message });
      }
      if (err.message && err.message.includes('UNIQUE constraint failed')) {
        return res.status(409).json({ error: 'A recipe with this title already exists' });
      }
      throw err;
    }
  });

  router.put('/:id', (req, res) => {
    try {
      const recipe = repo.updateRecipe(db, Number(req.params.id), req.body || {});
      if (!recipe) {
        return res.status(404).json({ error: 'Recipe not found' });
      }
      res.json(recipe);
    } catch (err) {
      if (err instanceof repo.ValidationError) {
        return res.status(400).json({ error: err.message });
      }
      throw err;
    }
  });

  router.delete('/:id', (req, res) => {
    const deleted = repo.deleteRecipe(db, Number(req.params.id));
    if (!deleted) {
      return res.status(404).json({ error: 'Recipe not found' });
    }
    res.status(204).end();
  });

  return router;
}

module.exports = { createRecipesRouter };
