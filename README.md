# test

Public test repo used for experimenting with GitHub Copilot workflows and sandbox tooling.

## About

This repository is a lightweight scratch space — not a production project. It's used to try things out, test automation, and validate tooling behavior.

## Recipe Database

Recipes live in **Amazon DynamoDB** instead of being hardcoded in this
README. The data-access layer and CLI live under `recipes/`.

### Setup

Install the runtime dependency (`boto3`):

```bash
pip install -r requirements.txt
```

Configure AWS access via any of boto3's standard mechanisms — environment
variables, a shared `~/.aws/credentials` profile, or an IAM role. No
credentials are hardcoded anywhere in this repo.

Optional environment variables:

| Variable                 | Default     | Purpose                                   |
|---------------------------|-------------|--------------------------------------------|
| `RECIPES_TABLE_NAME`      | `Recipes`   | DynamoDB table name                        |
| `AWS_REGION`              | `us-east-1` | AWS region (falls back to `AWS_DEFAULT_REGION`) |
| `DYNAMODB_ENDPOINT_URL`   | (unset)     | Override endpoint, e.g. for DynamoDB Local  |

```bash
# Create the DynamoDB table (idempotent; on-demand billing, no capacity planning needed)
python3 -m recipes.cli init

# Load the starter recipes (Corn Chowder, Borscht)
python3 -m recipes.cli seed
```

The table uses `title` as its partition key; ingredients and instructions
are stored as ordered list attributes on each item. Recipe title lookups
(`show`, `add`, `delete`) are case-sensitive.

### Local development without AWS

You can point at [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html)
instead of a real AWS account:

```bash
docker run -d -p 8000:8000 amazon/dynamodb-local
export DYNAMODB_ENDPOINT_URL=http://localhost:8000
export AWS_ACCESS_KEY_ID=local
export AWS_SECRET_ACCESS_KEY=local
python3 -m recipes.cli init
```

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

Single DynamoDB table (default name `Recipes`):

- `title` (String, partition key)
- `description` (String)
- `ingredients` (List of String, ordered)
- `instructions` (List of String, ordered)

See `recipes/db.py` for the full data-access layer.

### Tests

Tests use [moto](https://github.com/getmoto/moto) to mock DynamoDB, so no
AWS account or network access is required:

```bash
pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
```
