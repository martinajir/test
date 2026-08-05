'use strict';

const { getDb } = require('./db');
const { migrate } = require('./db/schema');
const { createApp } = require('./app');

const PORT = process.env.PORT || 3000;

const db = getDb();
migrate(db);

const app = createApp(db);

app.listen(PORT, () => {
  console.log(`Recipe repository API listening on port ${PORT}`);
});
