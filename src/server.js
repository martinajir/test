'use strict';

const { createApp } = require('./app');
const { openDatabase } = require('../db/database');
const { seed } = require('../db/seed');

const PORT = process.env.PORT || 3000;

const db = openDatabase();
seed(db);

const app = createApp(db);

app.listen(PORT, () => {
  console.log(`Recipe repository API listening on port ${PORT}`);
});
