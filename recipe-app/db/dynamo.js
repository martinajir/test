// DynamoDB client setup. Reads standard AWS SDK environment variables
// (AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN),
// plus an optional DYNAMODB_ENDPOINT override for local development/testing
// against DynamoDB Local (e.g. http://localhost:8000).
const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient } = require('@aws-sdk/lib-dynamodb');

const TABLE_NAME = process.env.RECIPES_TABLE_NAME || 'Recipes';
const REGION = process.env.AWS_REGION || 'us-east-1';

const clientConfig = { region: REGION };

if (process.env.DYNAMODB_ENDPOINT) {
  clientConfig.endpoint = process.env.DYNAMODB_ENDPOINT;
  // DynamoDB Local doesn't validate credentials, but the SDK still requires
  // some values to be present.
  clientConfig.credentials = {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || 'local',
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || 'local',
  };
}

const baseClient = new DynamoDBClient(clientConfig);
const ddb = DynamoDBDocumentClient.from(baseClient, {
  marshallOptions: { removeUndefinedValues: true },
});

module.exports = { ddb, TABLE_NAME };
