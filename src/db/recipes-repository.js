'use strict';

/**
 * Data access layer for recipes. All functions take a `db` (node:sqlite DatabaseSync
 * instance) as the first argument so callers can use the shared connection or an
 * isolated in-memory one (e.g. in tests).
 */

function listRecipes(db) {
  const rows = db.prepare('SELECT id, title, description, created_at, updated_at FROM recipes ORDER BY title').all();
  return rows;
}

function getRecipeById(db, id) {
  const recipe = db.prepare('SELECT id, title, description, created_at, updated_at FROM recipes WHERE id = ?').get(id);
  if (!recipe) {
    return null;
  }

  const ingredients = db
    .prepare('SELECT description FROM ingredients WHERE recipe_id = ? ORDER BY position')
    .all(id)
    .map((row) => row.description);

  const instructions = db
    .prepare('SELECT description FROM instructions WHERE recipe_id = ? ORDER BY step_number')
    .all(id)
    .map((row) => row.description);

  return { ...recipe, ingredients, instructions };
}

function createRecipe(db, { title, description, ingredients = [], instructions = [] }) {
  if (!title || typeof title !== 'string') {
    throw new ValidationError('title is required and must be a string');
  }
  if (!Array.isArray(ingredients) || !Array.isArray(instructions)) {
    throw new ValidationError('ingredients and instructions must be arrays');
  }

  const insertRecipe = db.prepare(
    'INSERT INTO recipes (title, description) VALUES (?, ?)'
  );
  const insertIngredient = db.prepare(
    'INSERT INTO ingredients (recipe_id, position, description) VALUES (?, ?, ?)'
  );
  const insertInstruction = db.prepare(
    'INSERT INTO instructions (recipe_id, step_number, description) VALUES (?, ?, ?)'
  );

  const runTransaction = db.transaction
    ? db.transaction((fn) => fn())
    : (fn) => fn();

  let recipeId;
  const run = () => {
    const result = insertRecipe.run(title, description ?? null);
    recipeId = Number(result.lastInsertRowid);
    ingredients.forEach((ingredient, index) => {
      insertIngredient.run(recipeId, index, ingredient);
    });
    instructions.forEach((instruction, index) => {
      insertInstruction.run(recipeId, index + 1, instruction);
    });
  };

  // node:sqlite's DatabaseSync doesn't expose a transaction() helper (unlike
  // better-sqlite3), so wrap manually in BEGIN/COMMIT/ROLLBACK.
  db.exec('BEGIN');
  try {
    run();
    db.exec('COMMIT');
  } catch (err) {
    db.exec('ROLLBACK');
    throw err;
  }

  return getRecipeById(db, recipeId);
}

function updateRecipe(db, id, { title, description, ingredients, instructions }) {
  const existing = getRecipeById(db, id);
  if (!existing) {
    return null;
  }

  db.exec('BEGIN');
  try {
    if (title !== undefined || description !== undefined) {
      db.prepare(
        "UPDATE recipes SET title = ?, description = ?, updated_at = datetime('now') WHERE id = ?"
      ).run(title ?? existing.title, description !== undefined ? description : existing.description, id);
    }

    if (Array.isArray(ingredients)) {
      db.prepare('DELETE FROM ingredients WHERE recipe_id = ?').run(id);
      const insertIngredient = db.prepare(
        'INSERT INTO ingredients (recipe_id, position, description) VALUES (?, ?, ?)'
      );
      ingredients.forEach((ingredient, index) => {
        insertIngredient.run(id, index, ingredient);
      });
    }

    if (Array.isArray(instructions)) {
      db.prepare('DELETE FROM instructions WHERE recipe_id = ?').run(id);
      const insertInstruction = db.prepare(
        'INSERT INTO instructions (recipe_id, step_number, description) VALUES (?, ?, ?)'
      );
      instructions.forEach((instruction, index) => {
        insertInstruction.run(id, index + 1, instruction);
      });
    }

    db.exec('COMMIT');
  } catch (err) {
    db.exec('ROLLBACK');
    throw err;
  }

  return getRecipeById(db, id);
}

function deleteRecipe(db, id) {
  const result = db.prepare('DELETE FROM recipes WHERE id = ?').run(id);
  return result.changes > 0;
}

class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
  }
}

module.exports = {
  listRecipes,
  getRecipeById,
  createRecipe,
  updateRecipe,
  deleteRecipe,
  ValidationError,
};
