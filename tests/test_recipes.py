"""Tests for the recipes DynamoDB data-access module.

Uses moto to mock DynamoDB so no real AWS account or network access is
required to run the suite.
"""

import os
import unittest

from moto import mock_aws

os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_SECURITY_TOKEN", "testing")
os.environ.setdefault("AWS_SESSION_TOKEN", "testing")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")

from recipes import db  # noqa: E402  (import after env vars are set)

TEST_TABLE = "RecipesTest"


class RecipeDbTests(unittest.TestCase):
    def setUp(self):
        self.mock_aws = mock_aws()
        self.mock_aws.start()
        db.init_db(table_name=TEST_TABLE)

    def tearDown(self):
        self.mock_aws.stop()

    def test_init_db_creates_empty_table(self):
        self.assertEqual(db.list_recipes(table_name=TEST_TABLE), [])

    def test_init_db_is_idempotent(self):
        db.init_db(table_name=TEST_TABLE)  # Should not raise on second call.
        self.assertEqual(db.list_recipes(table_name=TEST_TABLE), [])

    def test_add_and_get_recipe(self):
        db.add_recipe(
            "Test Soup",
            ["1 cup water", "1 pinch salt"],
            ["Boil water.", "Add salt."],
            description="A minimal test recipe.",
            table_name=TEST_TABLE,
        )

        recipe = db.get_recipe("Test Soup", table_name=TEST_TABLE)
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe["title"], "Test Soup")
        self.assertEqual(recipe["description"], "A minimal test recipe.")
        self.assertEqual(recipe["ingredients"], ["1 cup water", "1 pinch salt"])
        self.assertEqual(recipe["instructions"], ["Boil water.", "Add salt."])

    def test_get_missing_recipe_returns_none(self):
        self.assertIsNone(db.get_recipe("Nonexistent", table_name=TEST_TABLE))

    def test_duplicate_title_raises_recipe_already_exists_error(self):
        db.add_recipe("Dup", ["a"], ["b"], table_name=TEST_TABLE)
        with self.assertRaises(db.RecipeAlreadyExistsError):
            db.add_recipe("Dup", ["a"], ["b"], table_name=TEST_TABLE)

    def test_list_recipes_sorted_by_title(self):
        db.add_recipe("Zebra Stew", ["a"], ["b"], table_name=TEST_TABLE)
        db.add_recipe("Apple Pie", ["a"], ["b"], table_name=TEST_TABLE)
        titles = [r["title"] for r in db.list_recipes(table_name=TEST_TABLE)]
        self.assertEqual(titles, ["Apple Pie", "Zebra Stew"])

    def test_delete_recipe(self):
        db.add_recipe("To Delete", ["a"], ["b"], table_name=TEST_TABLE)
        self.assertTrue(db.delete_recipe("To Delete", table_name=TEST_TABLE))
        self.assertIsNone(db.get_recipe("To Delete", table_name=TEST_TABLE))

    def test_delete_missing_recipe_returns_false(self):
        self.assertFalse(db.delete_recipe("Nope", table_name=TEST_TABLE))


if __name__ == "__main__":
    unittest.main()
