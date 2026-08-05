# Contributing a Recipe

Thanks for adding to the recipe repository! To keep things consistent:

1. Recipes are organized by cuisine under `recipes/<cuisine>/`, e.g. `recipes/italian/`, `recipes/mexican/`. If your recipe's cuisine doesn't have a folder yet, create one (lowercase, kebab-case if multi-word, e.g. `recipes/middle-eastern/`).
2. Copy [`recipes/TEMPLATE.md`](recipes/TEMPLATE.md) into that folder as a new file named in `kebab-case.md` matching the recipe title (e.g. `recipes/italian/carbonara.md`).
3. Fill in the title, description, servings, prep/cook time, tags, ingredients, and numbered instructions.
4. Add a link to your new recipe under the matching cuisine section (or a new one) in the `README.md` table, keeping recipes alphabetized within each cuisine and cuisines alphabetized overall.
5. Open a pull request. Please keep one recipe per file and one recipe per PR when possible.

## Style guidelines

- Use `##` for section headers (`Ingredients`, `Instructions`).
- Write ingredients as a bulleted list with quantities first (e.g. `2 cups flour`).
- Write instructions as a numbered list of clear, actionable steps.
- Keep tags lowercase and comma-separated (e.g. `soup, vegetarian, quick`). Don't repeat the cuisine as a tag since the folder already conveys it.
