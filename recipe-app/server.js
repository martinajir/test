const express = require('express');
const path = require('path');
const {
  listRecipes,
  getRecipe,
  createRecipe,
  updateRecipe,
  deleteRecipe,
} = require('./db/recipesRepo');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function toArray(value) {
  if (Array.isArray(value)) return value;
  return String(value)
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);
}

function isNonEmpty(value) {
  if (Array.isArray(value)) return value.length > 0;
  return typeof value === 'string' && value.trim().length > 0;
}

// List all recipes
app.get('/api/recipes', async (req, res, next) => {
  try {
    const recipes = await listRecipes();
    res.json(recipes);
  } catch (err) {
    next(err);
  }
});

// Get a single recipe
app.get('/api/recipes/:id', async (req, res, next) => {
  try {
    const recipe = await getRecipe(req.params.id);
    if (!recipe) return res.status(404).json({ error: 'Recipe not found' });
    res.json(recipe);
  } catch (err) {
    next(err);
  }
});

// Create a recipe
app.post('/api/recipes', async (req, res, next) => {
  try {
    const { title, ingredients, instructions } = req.body || {};

    if (!title || typeof title !== 'string' || !title.trim()) {
      return res.status(400).json({ error: 'title is required' });
    }
    if (!isNonEmpty(ingredients)) {
      return res.status(400).json({ error: 'ingredients is required' });
    }
    if (!isNonEmpty(instructions)) {
      return res.status(400).json({ error: 'instructions is required' });
    }

    const recipe = await createRecipe({
      title: title.trim(),
      ingredients: toArray(ingredients),
      instructions: toArray(instructions),
    });
    res.status(201).json(recipe);
  } catch (err) {
    next(err);
  }
});

// Update a recipe
app.put('/api/recipes/:id', async (req, res, next) => {
  try {
    const { title, ingredients, instructions } = req.body || {};
    const updates = {};
    if (title !== undefined) updates.title = String(title).trim();
    if (ingredients !== undefined) updates.ingredients = toArray(ingredients);
    if (instructions !== undefined) updates.instructions = toArray(instructions);

    const recipe = await updateRecipe(req.params.id, updates);
    if (!recipe) return res.status(404).json({ error: 'Recipe not found' });
    res.json(recipe);
  } catch (err) {
    next(err);
  }
});

// Delete a recipe
app.delete('/api/recipes/:id', async (req, res, next) => {
  try {
    const deleted = await deleteRecipe(req.params.id);
    if (!deleted) return res.status(404).json({ error: 'Recipe not found' });
    res.status(204).end();
  } catch (err) {
    next(err);
  }
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Recipe collection app listening on http://localhost:${PORT}`);
  });
}

module.exports = app;
