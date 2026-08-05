"""Database helpers for the recipe repository.

Provides a thin wrapper around a SQLite database so the CLI (and any
future tooling) can create, seed, and query recipes without duplicating
connection/schema logic.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "recipes.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with sane defaults."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    """Create the database schema if it doesn't already exist."""
    conn = get_connection(db_path)
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


def add_recipe(
    title: str,
    ingredients: list[str],
    instructions: list[str],
    description: str = "",
    db_path: Path | str = DEFAULT_DB_PATH,
) -> int:
    """Insert a recipe with its ingredients and instructions.

    Returns the new recipe's id. Raises sqlite3.IntegrityError if a
    recipe with the same title already exists.
    """
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO recipes (title, description) VALUES (?, ?)",
            (title, description),
        )
        recipe_id = cur.lastrowid

        conn.executemany(
            "INSERT INTO ingredients (recipe_id, position, text) VALUES (?, ?, ?)",
            [(recipe_id, i, text) for i, text in enumerate(ingredients, start=1)],
        )
        conn.executemany(
            "INSERT INTO instructions (recipe_id, step_number, text) VALUES (?, ?, ?)",
            [(recipe_id, i, text) for i, text in enumerate(instructions, start=1)],
        )
        conn.commit()
        return recipe_id
    finally:
        conn.close()


def list_recipes(db_path: Path | str = DEFAULT_DB_PATH) -> list[sqlite3.Row]:
    """Return all recipes ordered by title."""
    conn = get_connection(db_path)
    try:
        return conn.execute("SELECT * FROM recipes ORDER BY title").fetchall()
    finally:
        conn.close()


def get_recipe(title: str, db_path: Path | str = DEFAULT_DB_PATH) -> dict | None:
    """Fetch a single recipe (with ingredients and instructions) by title."""
    conn = get_connection(db_path)
    try:
        recipe = conn.execute(
            "SELECT * FROM recipes WHERE title = ? COLLATE NOCASE", (title,)
        ).fetchone()
        if recipe is None:
            return None

        ingredients = conn.execute(
            "SELECT text FROM ingredients WHERE recipe_id = ? ORDER BY position",
            (recipe["id"],),
        ).fetchall()
        instructions = conn.execute(
            "SELECT text FROM instructions WHERE recipe_id = ? ORDER BY step_number",
            (recipe["id"],),
        ).fetchall()

        return {
            "id": recipe["id"],
            "title": recipe["title"],
            "description": recipe["description"],
            "ingredients": [row["text"] for row in ingredients],
            "instructions": [row["text"] for row in instructions],
        }
    finally:
        conn.close()


def delete_recipe(title: str, db_path: Path | str = DEFAULT_DB_PATH) -> bool:
    """Delete a recipe by title. Returns True if a recipe was deleted."""
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "DELETE FROM recipes WHERE title = ? COLLATE NOCASE", (title,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
