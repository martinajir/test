const express = require('express');
const path = require('path');
const db = require('./db/database');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

function serializeRecipe(row) {
  return {
    id: row.id,
    title: row.title,
    ingredients: row.ingredients.split('\n'),
    instructions: row.instructions.split('\n'),
    created_at: row.created_at,
  };
}

// List all recipes
app.get('/api/recipes', (req, res) => {
  const rows = db.prepare('SELECT * FROM recipes ORDER BY created_at DESC').all();
  res.json(rows.map(serializeRecipe));
});

// Get a single recipe
app.get('/api/recipes/:id', (req, res) => {
  const row = db.prepare('SELECT * FROM recipes WHERE id = ?').get(req.params.id);
  if (!row) return res.status(404).json({ error: 'Recipe not found' });
  res.json(serializeRecipe(row));
});

// Create a recipe
app.post('/api/recipes', (req, res) => {
  const { title, ingredients, instructions } = req.body || {};

  if (!title || typeof title !== 'string' || !title.trim()) {
    return res.status(400).json({ error: 'title is required' });
  }
  if (!ingredients || (Array.isArray(ingredients) ? ingredients.length === 0 : !String(ingredients).trim())) {
    return res.status(400).json({ error: 'ingredients is required' });
  }
  if (!instructions || (Array.isArray(instructions) ? instructions.length === 0 : !String(instructions).trim())) {
    return res.status(400).json({ error: 'instructions is required' });
  }

  const ingredientsText = Array.isArray(ingredients) ? ingredients.join('\n') : String(ingredients);
  const instructionsText = Array.isArray(instructions) ? instructions.join('\n') : String(instructions);

  const result = db
    .prepare('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)')
    .run(title.trim(), ingredientsText, instructionsText);

  const row = db.prepare('SELECT * FROM recipes WHERE id = ?').get(result.lastInsertRowid);
  res.status(201).json(serializeRecipe(row));
});

// Update a recipe
app.put('/api/recipes/:id', (req, res) => {
  const existing = db.prepare('SELECT * FROM recipes WHERE id = ?').get(req.params.id);
  if (!existing) return res.status(404).json({ error: 'Recipe not found' });

  const { title, ingredients, instructions } = req.body || {};

  const newTitle = title !== undefined ? String(title).trim() : existing.title;
  const newIngredients =
    ingredients !== undefined
      ? Array.isArray(ingredients)
        ? ingredients.join('\n')
        : String(ingredients)
      : existing.ingredients;
  const newInstructions =
    instructions !== undefined
      ? Array.isArray(instructions)
        ? instructions.join('\n')
        : String(instructions)
      : existing.instructions;

  db.prepare('UPDATE recipes SET title = ?, ingredients = ?, instructions = ? WHERE id = ?').run(
    newTitle,
    newIngredients,
    newInstructions,
    req.params.id
  );

  const row = db.prepare('SELECT * FROM recipes WHERE id = ?').get(req.params.id);
  res.json(serializeRecipe(row));
});

// Delete a recipe
app.delete('/api/recipes/:id', (req, res) => {
  const result = db.prepare('DELETE FROM recipes WHERE id = ?').run(req.params.id);
  if (result.changes === 0) return res.status(404).json({ error: 'Recipe not found' });
  res.status(204).end();
});

if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Recipe collection app listening on http://localhost:${PORT}`);
  });
}

module.exports = app;
