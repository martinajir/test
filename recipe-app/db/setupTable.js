// Creates the Recipes DynamoDB table if it doesn't already exist. Run this
// once against DynamoDB Local (`npm run setup-table`) or against a real AWS
// account before using the app, unless the table is provisioned some other
// way (e.g. Infrastructure as Code).
const {
  DynamoDBClient,
  CreateTableCommand,
  DescribeTableCommand,
  waitUntilTableExists,
} = require('@aws-sdk/client-dynamodb');

const TABLE_NAME = process.env.RECIPES_TABLE_NAME || 'Recipes';
const REGION = process.env.AWS_REGION || 'us-east-1';

const clientConfig = { region: REGION };
if (process.env.DYNAMODB_ENDPOINT) {
  clientConfig.endpoint = process.env.DYNAMODB_ENDPOINT;
  clientConfig.credentials = {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || 'local',
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || 'local',
  };
}

const client = new DynamoDBClient(clientConfig);

async function tableExists() {
  try {
    await client.send(new DescribeTableCommand({ TableName: TABLE_NAME }));
    return true;
  } catch (err) {
    if (err.name === 'ResourceNotFoundException') return false;
    throw err;
  }
}

async function main() {
  if (await tableExists()) {
    console.log(`Table "${TABLE_NAME}" already exists. Skipping creation.`);
    return;
  }

  await client.send(
    new CreateTableCommand({
      TableName: TABLE_NAME,
      AttributeDefinitions: [{ AttributeName: 'id', AttributeType: 'S' }],
      KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
      BillingMode: 'PAY_PER_REQUEST',
    })
  );

  await waitUntilTableExists({ client, maxWaitTime: 30 }, { TableName: TABLE_NAME });
  console.log(`Created table "${TABLE_NAME}".`);
}

if (require.main === module) {
  main().catch((err) => {
    console.error('Failed to set up table:', err);
    process.exit(1);
  });
}

module.exports = { tableExists };
