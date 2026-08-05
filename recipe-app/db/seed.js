// Seeds the database with the recipes already documented in the repo's README
// (Corn Chowder and Borscht), so the collection starts with real data.
const db = require('./database');

const recipes = [
  {
    title: 'Corn Chowder',
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
    ].join('\n'),
    instructions: [
      'In a large pot over medium heat, cook the bacon until crisp. Remove and set aside, leaving the fat in the pot (or melt the butter if skipping bacon).',
      'Add the onion and celery, and sauté until softened, about 5 minutes.',
      'Stir in the garlic and cook for 1 minute more.',
      'Add the potatoes, corn, and broth. Bring to a boil, then reduce heat and simmer until the potatoes are tender, about 15-20 minutes.',
      'Use an immersion blender to purée about a third of the soup for a creamier texture, or mash some potatoes and corn against the side of the pot.',
      'Stir in the cream (or milk), and season with salt and pepper. Simmer for another 5 minutes.',
      'Serve hot, topped with the reserved bacon and chopped chives or parsley.',
    ].join('\n'),
  },
  {
    title: 'Borscht',
    ingredients: [
      '1 tablespoon oil or butter',
      '1 onion, diced',
      '2 carrots, grated',
      '3 medium beets, peeled and grated',
      '2 potatoes, peeled and diced',
      '1/4 head cabbage, shredded',
      '2 cloves garlic, minced',
      '6 cups beef, vegetable, or chicken broth',
    ].join('\n'),
    instructions: [
      'Heat the oil in a large pot over medium heat. Add the onion and carrots, and cook until softened, about 5 minutes.',
      'Stir in the beets, potatoes, and garlic, and cook for another 2 minutes.',
      'Add the broth, bring to a boil, then reduce heat and simmer until the vegetables are tender, about 20 minutes.',
      'Add the cabbage and simmer for another 10 minutes.',
      'Season to taste and serve hot or cold, with a dollop of sour cream if desired.',
    ].join('\n'),
  },
];

const insert = db.prepare(
  'INSERT INTO recipes (title, ingredients, instructions) VALUES (@title, @ingredients, @instructions)'
);

const countRow = db.prepare('SELECT COUNT(*) AS count FROM recipes').get();

if (countRow.count > 0) {
  console.log(`Database already has ${countRow.count} recipe(s). Skipping seed.`);
} else {
  const insertMany = db.transaction((rows) => {
    for (const row of rows) insert.run(row);
  });
  insertMany(recipes);
  console.log(`Seeded ${recipes.length} recipes.`);
}
