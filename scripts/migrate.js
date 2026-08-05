'use strict';

const { getDb } = require('../src/db');
const { migrate } = require('../src/db/schema');

const db = getDb();
migrate(db);

console.log('Migration complete.');
