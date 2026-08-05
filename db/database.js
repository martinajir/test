'use strict';

const path = require('node:path');
const fs = require('node:fs');
const { DatabaseSync } = require('node:sqlite');

const DB_DIR = path.join(__dirname, '..', 'data');
const DB_PATH = path.join(DB_DIR, 'recipes.db');

const SCHEMA = `
  CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
  );
`;

/**
 * Opens (creating if necessary) the SQLite database used to store recipes
 * and ensures the schema exists.
 * @param {string} [dbPath] Optional override, mainly used by tests to run
 *   against an in-memory database.
 * @returns {import('node:sqlite').DatabaseSync}
 */
function openDatabase(dbPath = DB_PATH) {
  if (dbPath !== ':memory:' && !fs.existsSync(DB_DIR)) {
    fs.mkdirSync(DB_DIR, { recursive: true });
  }

  const db = new DatabaseSync(dbPath);
  db.exec(SCHEMA);
  return db;
}

module.exports = { openDatabase, DB_PATH };
