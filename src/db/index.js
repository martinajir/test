'use strict';

const path = require('node:path');
const fs = require('node:fs');
const { DatabaseSync } = require('node:sqlite');

const DEFAULT_DB_PATH = path.join(__dirname, '..', '..', 'data', 'recipes.db');

let dbInstance = null;

/**
 * Returns a singleton DatabaseSync connection. Pass a custom dbPath (e.g. ':memory:')
 * for tests to avoid touching the real database file.
 */
function getDb(dbPath = DEFAULT_DB_PATH) {
  if (dbInstance) {
    return dbInstance;
  }

  if (dbPath !== ':memory:') {
    fs.mkdirSync(path.dirname(dbPath), { recursive: true });
  }

  dbInstance = new DatabaseSync(dbPath);
  dbInstance.exec('PRAGMA foreign_keys = ON;');
  return dbInstance;
}

/** Resets the cached connection. Mainly useful for tests. */
function resetDb() {
  if (dbInstance) {
    dbInstance.close();
    dbInstance = null;
  }
}

module.exports = { getDb, resetDb, DEFAULT_DB_PATH };
