// Data access layer for recipes, backed by DynamoDB. Kept separate from
// server.js so routes stay thin and this module is easy to unit test with
// aws-sdk-client-mock.
const { randomUUID } = require('crypto');
const {
  PutCommand,
  GetCommand,
  ScanCommand,
  DeleteCommand,
} = require('@aws-sdk/lib-dynamodb');
const { ddb, TABLE_NAME } = require('./dynamo');

async function listRecipes() {
  const result = await ddb.send(new ScanCommand({ TableName: TABLE_NAME }));
  const items = result.Items || [];
  // Scan doesn't guarantee order, so sort newest-first like the old API did.
  return items.sort((a, b) => (b.created_at || '').localeCompare(a.created_at || ''));
}

async function getRecipe(id) {
  const result = await ddb.send(new GetCommand({ TableName: TABLE_NAME, Key: { id } }));
  return result.Item || null;
}

async function createRecipe({ title, ingredients, instructions }) {
  const item = {
    id: randomUUID(),
    title,
    ingredients,
    instructions,
    created_at: new Date().toISOString(),
  };
  await ddb.send(new PutCommand({ TableName: TABLE_NAME, Item: item }));
  return item;
}

async function updateRecipe(id, updates) {
  const existing = await getRecipe(id);
  if (!existing) return null;

  const item = { ...existing, ...updates };
  await ddb.send(new PutCommand({ TableName: TABLE_NAME, Item: item }));
  return item;
}

async function deleteRecipe(id) {
  const existing = await getRecipe(id);
  if (!existing) return false;

  await ddb.send(new DeleteCommand({ TableName: TABLE_NAME, Key: { id } }));
  return true;
}

module.exports = { listRecipes, getRecipe, createRecipe, updateRecipe, deleteRecipe };
