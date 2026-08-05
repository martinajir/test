'use strict';

const { getDb } = require('../src/db');
const { migrate } = require('../src/db/schema');
const { createRecipe, listRecipes } = require('../src/db/recipes-repository');

const RECIPES = [
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
      '1 tablespoon tomato paste',
      '1 tablespoon vinegar or lemon juice',
      'Salt and pepper, to taste',
      'Sour cream and fresh dill, for garnish',
    ],
    instructions: [
      'Heat the oil in a large pot over medium heat. Saute the onion and carrots until softened, about 5 minutes.',
      'Add the grated beets and tomato paste, stirring to combine, and cook for another 5 minutes.',
      'Pour in the broth and bring to a boil. Add the potatoes and simmer until nearly tender, about 10 minutes.',
      'Stir in the cabbage and garlic, and simmer until the vegetables are fully tender, about 10 more minutes.',
      'Stir in the vinegar or lemon juice, and season with salt and pepper.',
      'Serve hot or chilled, topped with a dollop of sour cream and fresh dill.',
    ],
  },
];

const db = getDb();
migrate(db);

const existingTitles = new Set(listRecipes(db).map((r) => r.title));

for (const recipe of RECIPES) {
  if (existingTitles.has(recipe.title)) {
    console.log(`Skipping "${recipe.title}" (already seeded).`);
    continue;
  }
  createRecipe(db, recipe);
  console.log(`Seeded "${recipe.title}".`);
}

console.log('Seeding complete.');
