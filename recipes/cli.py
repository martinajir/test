"""Command-line interface for the recipe database.

Usage:
    python -m recipes.cli init
    python -m recipes.cli seed
    python -m recipes.cli list
    python -m recipes.cli show "Corn Chowder"
    python -m recipes.cli add "Recipe Title" --description "..." \
        --ingredient "1 cup flour" --ingredient "2 eggs" \
        --step "Mix ingredients." --step "Bake at 350F."
    python -m recipes.cli delete "Recipe Title"
"""

from __future__ import annotations

import argparse
import sqlite3
import sys

from recipes import db


def cmd_init(args: argparse.Namespace) -> None:
    db.init_db()
    print(f"Initialized database at {db.DEFAULT_DB_PATH}")


def cmd_seed(args: argparse.Namespace) -> None:
    db.init_db()

    seed_recipes = [
        {
            "title": "Corn Chowder",
            "description": "A simple, hearty corn chowder.",
            "ingredients": [
                "4 slices bacon, chopped (optional)",
                "1 tablespoon butter",
                "1 onion, diced",
                "2 stalks celery, diced",
                "2 cloves garlic, minced",
                "1 lb potatoes, peeled and diced",
                "4 cups corn kernels (fresh, frozen, or canned)",
                "4 cups chicken or vegetable broth",
                "1 cup heavy cream or whole milk",
                "Salt and pepper, to taste",
                "Chopped chives or parsley, for garnish",
            ],
            "instructions": [
                "In a large pot over medium heat, cook the bacon until crisp. "
                "Remove and set aside, leaving the fat in the pot (or melt the "
                "butter if skipping bacon).",
                "Add the onion and celery, and saute until softened, about 5 minutes.",
                "Stir in the garlic and cook for 1 minute more.",
                "Add the potatoes, corn, and broth. Bring to a boil, then reduce "
                "heat and simmer until the potatoes are tender, about 15-20 minutes.",
                "Use an immersion blender to puree about a third of the soup for a "
                "creamier texture, or mash some potatoes and corn against the side "
                "of the pot.",
                "Stir in the cream (or milk), and season with salt and pepper. "
                "Simmer for another 5 minutes.",
                "Serve hot, topped with the reserved bacon and chopped chives or "
                "parsley.",
            ],
        },
        {
            "title": "Borscht",
            "description": "A classic Ukrainian beet soup, served hot or cold.",
            "ingredients": [
                "1 tablespoon oil or butter",
                "1 onion, diced",
                "2 carrots, grated",
                "3 medium beets, peeled and grated",
                "2 potatoes, peeled and diced",
                "1/4 head cabbage, shredded",
                "2 cloves garlic, minced",
                "6 cups beef, vegetable, or chicken broth",
                "1 tablespoon tomato paste",
                "1 tablespoon vinegar or lemon juice",
                "Salt and pepper, to taste",
                "Sour cream and fresh dill, for garnish",
            ],
            "instructions": [
                "Heat the oil in a large pot over medium heat. Saute the onion and "
                "carrots until softened, about 5 minutes.",
                "Add the grated beets and tomato paste, stirring to combine, and "
                "cook for another 5 minutes.",
                "Pour in the broth and bring to a boil. Add the potatoes and "
                "simmer until nearly tender, about 10 minutes.",
                "Stir in the cabbage and garlic, and simmer until the vegetables "
                "are fully tender, about 10 more minutes.",
                "Stir in the vinegar or lemon juice, and season with salt and "
                "pepper.",
                "Serve hot or chilled, topped with a dollop of sour cream and "
                "fresh dill.",
            ],
        },
    ]

    added, skipped = 0, 0
    for recipe in seed_recipes:
        try:
            db.add_recipe(
                recipe["title"],
                recipe["ingredients"],
                recipe["instructions"],
                description=recipe["description"],
            )
            added += 1
        except sqlite3.IntegrityError:
            skipped += 1

    print(f"Seeded {added} recipe(s); skipped {skipped} already present.")


def cmd_list(args: argparse.Namespace) -> None:
    recipes = db.list_recipes()
    if not recipes:
        print("No recipes found. Run `python -m recipes.cli seed` to add some.")
        return
    for recipe in recipes:
        print(f"- {recipe['title']}")


def cmd_show(args: argparse.Namespace) -> None:
    recipe = db.get_recipe(args.title)
    if recipe is None:
        print(f"No recipe found matching '{args.title}'.", file=sys.stderr)
        sys.exit(1)

    print(f"# {recipe['title']}\n")
    if recipe["description"]:
        print(f"{recipe['description']}\n")
    print("## Ingredients")
    for item in recipe["ingredients"]:
        print(f"- {item}")
    print("\n## Instructions")
    for i, step in enumerate(recipe["instructions"], start=1):
        print(f"{i}. {step}")


def cmd_add(args: argparse.Namespace) -> None:
    db.init_db()
    try:
        db.add_recipe(
            args.title,
            args.ingredient or [],
            args.step or [],
            description=args.description or "",
        )
    except sqlite3.IntegrityError:
        print(f"A recipe titled '{args.title}' already exists.", file=sys.stderr)
        sys.exit(1)
    print(f"Added recipe '{args.title}'.")


def cmd_delete(args: argparse.Namespace) -> None:
    if db.delete_recipe(args.title):
        print(f"Deleted recipe '{args.title}'.")
    else:
        print(f"No recipe found matching '{args.title}'.", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="recipes", description="Manage the recipe database.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create the database schema.").set_defaults(func=cmd_init)
    subparsers.add_parser("seed", help="Seed the database with starter recipes.").set_defaults(
        func=cmd_seed
    )
    subparsers.add_parser("list", help="List all recipe titles.").set_defaults(func=cmd_list)

    show_parser = subparsers.add_parser("show", help="Show a recipe's full details.")
    show_parser.add_argument("title")
    show_parser.set_defaults(func=cmd_show)

    add_parser = subparsers.add_parser("add", help="Add a new recipe.")
    add_parser.add_argument("title")
    add_parser.add_argument("--description", default="")
    add_parser.add_argument("--ingredient", action="append", help="Repeatable.")
    add_parser.add_argument("--step", action="append", help="Repeatable.")
    add_parser.set_defaults(func=cmd_add)

    delete_parser = subparsers.add_parser("delete", help="Delete a recipe by title.")
    delete_parser.add_argument("title")
    delete_parser.set_defaults(func=cmd_delete)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
