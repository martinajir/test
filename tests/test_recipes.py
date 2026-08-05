"""Tests for the recipes database module."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from recipes import db


class RecipeDbTests(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp_dir.name) / "test_recipes.db"
        db.init_db(self.db_path)

    def tearDown(self):
        self._tmp_dir.cleanup()

    def test_init_db_creates_empty_tables(self):
        self.assertEqual(db.list_recipes(self.db_path), [])

    def test_add_and_get_recipe(self):
        db.add_recipe(
            "Test Soup",
            ["1 cup water", "1 pinch salt"],
            ["Boil water.", "Add salt."],
            description="A minimal test recipe.",
            db_path=self.db_path,
        )

        recipe = db.get_recipe("Test Soup", db_path=self.db_path)
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe["title"], "Test Soup")
        self.assertEqual(recipe["description"], "A minimal test recipe.")
        self.assertEqual(recipe["ingredients"], ["1 cup water", "1 pinch salt"])
        self.assertEqual(recipe["instructions"], ["Boil water.", "Add salt."])

    def test_get_recipe_is_case_insensitive(self):
        db.add_recipe("Test Soup", ["water"], ["Boil it."], db_path=self.db_path)
        self.assertIsNotNone(db.get_recipe("test soup", db_path=self.db_path))

    def test_get_missing_recipe_returns_none(self):
        self.assertIsNone(db.get_recipe("Nonexistent", db_path=self.db_path))

    def test_duplicate_title_raises_integrity_error(self):
        db.add_recipe("Dup", ["a"], ["b"], db_path=self.db_path)
        with self.assertRaises(sqlite3.IntegrityError):
            db.add_recipe("Dup", ["a"], ["b"], db_path=self.db_path)

    def test_list_recipes_sorted_by_title(self):
        db.add_recipe("Zebra Stew", ["a"], ["b"], db_path=self.db_path)
        db.add_recipe("Apple Pie", ["a"], ["b"], db_path=self.db_path)
        titles = [r["title"] for r in db.list_recipes(self.db_path)]
        self.assertEqual(titles, ["Apple Pie", "Zebra Stew"])

    def test_delete_recipe(self):
        db.add_recipe("To Delete", ["a"], ["b"], db_path=self.db_path)
        self.assertTrue(db.delete_recipe("To Delete", db_path=self.db_path))
        self.assertIsNone(db.get_recipe("To Delete", db_path=self.db_path))

    def test_delete_missing_recipe_returns_false(self):
        self.assertFalse(db.delete_recipe("Nope", db_path=self.db_path))

    def test_delete_cascades_ingredients_and_instructions(self):
        db.add_recipe(
            "Cascade Test", ["a", "b"], ["c", "d"], db_path=self.db_path
        )
        db.delete_recipe("Cascade Test", db_path=self.db_path)

        conn = db.get_connection(self.db_path)
        try:
            remaining_ingredients = conn.execute(
                "SELECT COUNT(*) FROM ingredients"
            ).fetchone()[0]
            remaining_instructions = conn.execute(
                "SELECT COUNT(*) FROM instructions"
            ).fetchone()[0]
        finally:
            conn.close()

        self.assertEqual(remaining_ingredients, 0)
        self.assertEqual(remaining_instructions, 0)


if __name__ == "__main__":
    unittest.main()
