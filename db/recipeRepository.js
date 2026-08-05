'use strict';

/**
 * Data-access layer for recipes. Ingredients and instructions are stored as
 * JSON-encoded arrays of strings so callers work with plain JS arrays.
 */
class RecipeRepository {
  /**
   * @param {import('node:sqlite').DatabaseSync} db
   */
  constructor(db) {
    this.db = db;
  }

  _rowToRecipe(row) {
    if (!row) return null;
    return {
      id: row.id,
      title: row.title,
      description: row.description,
      ingredients: JSON.parse(row.ingredients),
      instructions: JSON.parse(row.instructions),
      created_at: row.created_at,
      updated_at: row.updated_at,
    };
  }

  list() {
    const rows = this.db
      .prepare('SELECT * FROM recipes ORDER BY created_at DESC, id DESC')
      .all();
    return rows.map((row) => this._rowToRecipe(row));
  }

  getById(id) {
    const row = this.db
      .prepare('SELECT * FROM recipes WHERE id = ?')
      .get(id);
    return this._rowToRecipe(row);
  }

  create({ title, description = null, ingredients, instructions }) {
    const result = this.db
      .prepare(
        `INSERT INTO recipes (title, description, ingredients, instructions)
         VALUES (?, ?, ?, ?)`
      )
      .run(
        title,
        description,
        JSON.stringify(ingredients),
        JSON.stringify(instructions)
      );
    return this.getById(Number(result.lastInsertRowid));
  }

  update(id, { title, description, ingredients, instructions }) {
    const existing = this.getById(id);
    if (!existing) return null;

    const next = {
      title: title !== undefined ? title : existing.title,
      description: description !== undefined ? description : existing.description,
      ingredients: ingredients !== undefined ? ingredients : existing.ingredients,
      instructions: instructions !== undefined ? instructions : existing.instructions,
    };

    this.db
      .prepare(
        `UPDATE recipes
         SET title = ?, description = ?, ingredients = ?, instructions = ?, updated_at = datetime('now')
         WHERE id = ?`
      )
      .run(
        next.title,
        next.description,
        JSON.stringify(next.ingredients),
        JSON.stringify(next.instructions),
        id
      );

    return this.getById(id);
  }

  delete(id) {
    const result = this.db.prepare('DELETE FROM recipes WHERE id = ?').run(id);
    return result.changes > 0;
  }
}

module.exports = { RecipeRepository };
