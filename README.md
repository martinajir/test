# test

Public test repo used for experimenting with GitHub Copilot workflows and sandbox tooling.

## About

This repository is a lightweight scratch space — not a production project. It's used to try things out, test automation, and validate tooling behavior.

## Recipe Database

Recipes now live in a small SQLite-backed database instead of being hardcoded
in this README. The database, schema, and CLI live under `recipes/`.

### Setup

No external dependencies are required (Python 3.9+, stdlib only).

```bash
# Create the database schema
python3 -m recipes.cli init

# Load the starter recipes (Corn Chowder, Borscht)
python3 -m recipes.cli seed
```

This creates `recipes/recipes.db` (ignored by git — each environment builds
its own local copy from the schema + seed data).

### Usage

```bash
# List all recipe titles
python3 -m recipes.cli list

# Show a recipe's full details
python3 -m recipes.cli show "Corn Chowder"

# Add a new recipe
python3 -m recipes.cli add "Fried Rice" \
  --description "Quick weeknight fried rice." \
  --ingredient "3 cups cooked rice" \
  --ingredient "2 eggs" \
  --ingredient "2 tablespoons soy sauce" \
  --step "Scramble the eggs and set aside." \
  --step "Stir-fry the rice, then combine with the eggs and soy sauce."

# Delete a recipe
python3 -m recipes.cli delete "Fried Rice"
```

### Schema

- `recipes` — id, title (unique), description, created_at
- `ingredients` — recipe_id, position, text
- `instructions` — recipe_id, step_number, text

See `recipes/schema.sql` for the full schema and `recipes/db.py` for the
Python data-access layer.

### Tests

```bash
python3 -m unittest discover -s tests -v
```
