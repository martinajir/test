"""DynamoDB data-access layer for the recipe repository.

Recipes are stored in a single DynamoDB table keyed by recipe title
(partition key). Ingredients and instructions are stored as ordered
list-of-string attributes directly on the item, since DynamoDB has no
notion of separate relational tables.

Configuration is entirely via environment variables so no credentials or
endpoints are hardcoded:

- ``RECIPES_TABLE_NAME`` - DynamoDB table name (default: ``Recipes``).
- ``AWS_REGION`` / ``AWS_DEFAULT_REGION`` - AWS region (default: ``us-east-1``).
- ``DYNAMODB_ENDPOINT_URL`` - optional override, e.g. ``http://localhost:8000``
  for local development against DynamoDB Local, or a moto server in tests.

AWS credentials are resolved via boto3's standard credential chain
(environment variables, shared config/credentials file, IAM role, etc.).
"""

from __future__ import annotations

import os

import boto3
from botocore.exceptions import ClientError

DEFAULT_TABLE_NAME = "Recipes"


class RecipeAlreadyExistsError(Exception):
    """Raised when attempting to add a recipe whose title already exists."""


def _table_name() -> str:
    return os.environ.get("RECIPES_TABLE_NAME", DEFAULT_TABLE_NAME)


def _region_name() -> str:
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"


def get_resource():
    """Return a boto3 DynamoDB resource, honoring local-endpoint overrides."""
    kwargs = {"region_name": _region_name()}
    endpoint_url = os.environ.get("DYNAMODB_ENDPOINT_URL")
    if endpoint_url:
        kwargs["endpoint_url"] = endpoint_url
    return boto3.resource("dynamodb", **kwargs)


def get_table(table_name: str | None = None):
    resource = get_resource()
    return resource.Table(table_name or _table_name())


def init_db(table_name: str | None = None) -> None:
    """Create the DynamoDB table if it doesn't already exist.

    Uses on-demand (PAY_PER_REQUEST) billing so no capacity planning is
    required, and waits for the table to become ACTIVE before returning.
    """
    table_name = table_name or _table_name()
    resource = get_resource()
    client = resource.meta.client

    try:
        client.describe_table(TableName=table_name)
        return  # Table already exists.
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    resource.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "title", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "title", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    client.get_waiter("table_exists").wait(TableName=table_name)


def add_recipe(
    title: str,
    ingredients: list[str],
    instructions: list[str],
    description: str = "",
    table_name: str | None = None,
) -> None:
    """Insert a recipe. Raises RecipeAlreadyExistsError on duplicate titles."""
    table = get_table(table_name)
    try:
        table.put_item(
            Item={
                "title": title,
                "description": description,
                "ingredients": ingredients,
                "instructions": instructions,
            },
            ConditionExpression="attribute_not_exists(title)",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise RecipeAlreadyExistsError(
                f"A recipe titled '{title}' already exists."
            ) from e
        raise


def list_recipes(table_name: str | None = None) -> list[dict]:
    """Return all recipes ordered by title."""
    table = get_table(table_name)
    items: list[dict] = []
    response = table.scan()
    items.extend(response.get("Items", []))
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return sorted(items, key=lambda item: item["title"].lower())


def get_recipe(title: str, table_name: str | None = None) -> dict | None:
    """Fetch a single recipe by exact title (case-sensitive)."""
    table = get_table(table_name)
    response = table.get_item(Key={"title": title})
    item = response.get("Item")
    if item is None:
        return None
    return {
        "title": item["title"],
        "description": item.get("description", ""),
        "ingredients": list(item.get("ingredients", [])),
        "instructions": list(item.get("instructions", [])),
    }


def delete_recipe(title: str, table_name: str | None = None) -> bool:
    """Delete a recipe by exact title. Returns True if a recipe was deleted."""
    table = get_table(table_name)
    response = table.delete_item(Key={"title": title}, ReturnValues="ALL_OLD")
    return "Attributes" in response
