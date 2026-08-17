# test

Public test repo used for experimenting with GitHub Copilot workflows and sandbox tooling.

## About

This repository is a lightweight scratch space — not a production project. It's used to try things out, test automation, and validate tooling behavior.

## Pull request closed webhook listener

`pull_request_closed_listener.py` is a dependency-free HTTP listener for GitHub
`pull_request` webhooks. It validates each delivery's
`X-Hub-Signature-256` header, ignores unrelated events and actions, and logs
whether a closed pull request was merged or closed without merging.

Set a high-entropy webhook secret and start the listener:

```shell
WEBHOOK_SECRET="replace-with-your-secret" python3 pull_request_closed_listener.py
```

The listener uses `http://127.0.0.1:3000/webhook` by default. Set `HOST` and
`PORT` to change the bind address, and use `GET /health` for a readiness check.

In the repository's **Settings > Webhooks**, configure:

- **Payload URL:** The public HTTPS URL that forwards to `/webhook`
- **Content type:** `application/json`
- **Secret:** The same value as `WEBHOOK_SECRET`
- **Events:** Select **Pull requests**

Run the tests with:

```shell
python3 -m unittest -v
```

The implementation follows GitHub's public documentation for
[handling webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/handling-webhook-deliveries),
[validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries),
and the
[`pull_request` event payload](https://docs.github.com/en/webhooks/webhook-events-and-payloads#pull_request).

## Recipe: Corn Chowder

A simple, hearty corn chowder.

### Ingredients

- 4 slices bacon, chopped (optional)
- 1 tablespoon butter
- 1 onion, diced
- 2 stalks celery, diced
- 2 cloves garlic, minced
- 1 lb potatoes, peeled and diced
- 4 cups corn kernels (fresh, frozen, or canned)
- 4 cups chicken or vegetable broth
- 1 cup heavy cream or whole milk
- Salt and pepper, to taste
- Chopped chives or parsley, for garnish

### Instructions

1. In a large pot over medium heat, cook the bacon until crisp. Remove and set aside, leaving the fat in the pot (or melt the butter if skipping bacon).
2. Add the onion and celery, and sauté until softened, about 5 minutes.
3. Stir in the garlic and cook for 1 minute more.
4. Add the potatoes, corn, and broth. Bring to a boil, then reduce heat and simmer until the potatoes are tender, about 15–20 minutes.
5. Use an immersion blender to purée about a third of the soup for a creamier texture, or mash some potatoes and corn against the side of the pot.
6. Stir in the cream (or milk), and season with salt and pepper. Simmer for another 5 minutes.
7. Serve hot, topped with the reserved bacon and chopped chives or parsley.

## Recipe: Borscht

A classic Ukrainian beet soup, served hot or cold.

### Ingredients

- 1 tablespoon oil or butter
- 1 onion, diced
- 2 carrots, grated
- 3 medium beets, peeled and grated
- 2 potatoes, peeled and diced
- 1/4 head cabbage, shredded
- 2 cloves garlic, minced
- 6 cups beef, vegetable, or chicken broth
- 1 tablespoon tomato paste
- 1 tablespoon vinegar or lemon juice
- Salt and pepper, to taste
- Sour cream and fresh dill, for garnish

### Instructions

1. Heat the oil in a large pot over medium heat. Sauté the onion and carrots until softened, about 5 minutes.
2. Add the grated beets and tomato paste, stirring to combine, and cook for another 5 minutes.
3. Pour in the broth and bring to a boil. Add the potatoes and simmer until nearly tender, about 10 minutes.
4. Stir in the cabbage and garlic, and simmer until the vegetables are fully tender, about 10 more minutes.
5. Stir in the vinegar or lemon juice, and season with salt and pepper.
6. Serve hot or chilled, topped with a dollop of sour cream and fresh dill.
