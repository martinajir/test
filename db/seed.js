'use strict';

const { openDatabase } = require('./database');
const { RecipeRepository } = require('./recipeRepository');

const SEED_RECIPES = [
  {
    title: 'Corn Chowder',
    description: 'A simple, hearty corn chowder.',
    ingredients: [
      '4 slices bacon, chopped (optional)',
      '1 tablespoon butter',
      '1 onion, diced',
      '2 stalks celery, diced',
      '2 cloves garlic, minced',
      '1 lb potatoes, peeled and diced',
      '4 cups corn kernels (fresh, frozen, or canned)',
      '4 cups chicken or vegetable broth',
      '1 cup heavy cream or whole milk',
      'Salt and pepper, to taste',
      'Chopped chives or parsley, for garnish',
    ],
    instructions: [
      'In a large pot over medium heat, cook the bacon until crisp. Remove and set aside, leaving the fat in the pot (or melt the butter if skipping bacon).',
      'Add the onion and celery, and saute until softened, about 5 minutes.',
      'Stir in the garlic and cook for 1 minute more.',
      'Add the potatoes, corn, and broth. Bring to a boil, then reduce heat and simmer until the potatoes are tender, about 15-20 minutes.',
      'Use an immersion blender to puree about a third of the soup for a creamier texture, or mash some potatoes and corn against the side of the pot.',
      'Stir in the cream (or milk), and season with salt and pepper. Simmer for another 5 minutes.',
      'Serve hot, topped with the reserved bacon and chopped chives or parsley.',
    ],
  },
  {
    title: 'Borscht',
    description: 'A classic Ukrainian beet soup, served hot or cold.',
    ingredients: [
      '1 tablespoon oil or butter',
      '1 onion, diced',
      '2 carrots, grated',
      '3 medium beets, peeled and grated',
      '2 potatoes, peeled and diced',
      '1/4 head cabbage, shredded',
      '2 cloves garlic, minced',
      '6 cups beef, vegetable, or chicken broth',
    ],
    instructions: [
      'Heat the oil or butter in a large pot over medium heat.',
      'Add the onion and carrots, and cook until softened, about 5 minutes.',
      'Stir in the beets, garlic, and broth. Bring to a boil, then reduce heat and simmer for about 20 minutes.',
      'Add the potatoes and cabbage, and continue simmering until all the vegetables are tender, about 15 more minutes.',
      'Season with salt and pepper to taste, and serve hot with a dollop of sour cream, or chill and serve cold.',
    ],
  },
];

/**
 * Seeds the database with the recipes already documented in the README.
 * Safe to re-run: it skips recipes that already exist by title.
 */
function seed(db = openDatabase()) {
  const repo = new RecipeRepository(db);
  const existingTitles = new Set(repo.list().map((r) => r.title));

  let inserted = 0;
  for (const recipe of SEED_RECIPES) {
    if (existingTitles.has(recipe.title)) continue;
    repo.create(recipe);
    inserted += 1;
  }

  return inserted;
}

if (require.main === module) {
  const db = openDatabase();
  const count = seed(db);
  console.log(`Seeded ${count} recipe(s).`);
  db.close();
}

module.exports = { seed, SEED_RECIPES };
