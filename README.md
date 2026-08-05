# test

Public test repo used for experimenting with GitHub Copilot workflows and sandbox tooling.

## About

This repository is a lightweight scratch space — not a production project. It's used to try things out, test automation, and validate tooling behavior.

## Recipe Repository

This repo includes a small recipe repository app: a REST API backed by a SQLite
database, instead of recipes hard-coded in this README.

- **Database**: SQLite, accessed via Node's built-in [`node:sqlite`](https://nodejs.org/api/sqlite.html) module (no native build step required). The database file lives at `data/recipes.db` (git-ignored).
- **Schema**: a `recipes` table, plus related `ingredients` and `instructions` tables (one row per ingredient/step), linked by `recipe_id`.
- **API**: Express-based REST API for CRUD operations on recipes.

### Requirements

- Node.js 22.5+ (for built-in `node:sqlite` support)

### Setup

```bash
npm install
npm run setup   # creates the DB schema and seeds it with the starter recipes
npm start        # starts the API on http://localhost:3000 (set PORT to change)
```

You can also run the steps individually:

```bash
npm run migrate  # create/update the database schema
npm run seed     # seed the starter recipes (Corn Chowder, Borscht)
```

### API

| Method | Path            | Description                          |
|--------|-----------------|--------------------------------------|
| GET    | `/health`       | Health check                         |
| GET    | `/recipes`      | List all recipes                     |
| GET    | `/recipes/:id`  | Get one recipe with ingredients/steps|
| POST   | `/recipes`      | Create a recipe                      |
| PUT    | `/recipes/:id`  | Update a recipe                      |
| DELETE | `/recipes/:id`  | Delete a recipe                      |

Example request body for `POST`/`PUT`:

```json
{
  "title": "Tomato Soup",
  "description": "Simple tomato soup",
  "ingredients": ["2 cans tomatoes", "1 onion, diced"],
  "instructions": ["Simmer everything", "Blend and serve"]
}
```

### Tests

```bash
npm test
```

Tests run against an isolated in-memory SQLite database, so they never touch
`data/recipes.db`.

### Project layout

```
src/
  db/            SQLite connection, schema, and recipes data-access layer
  routes/        Express routes
  app.js         Express app factory
  server.js      Entry point (creates DB, runs app)
scripts/
  migrate.js     Creates/updates the database schema
  seed.js        Seeds the starter recipes
test/
  recipes.test.js  API tests (node:test + node:sqlite in-memory)
data/            SQLite database file (git-ignored)
```
