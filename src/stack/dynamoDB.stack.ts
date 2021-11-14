import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as core from '@aws-cdk/core';
import { BuildConfig, REMOVAL_POLICY, SERVICE_PREFIX } from '../helper/helper';

interface DynamoDBStackDependencyProps extends core.StackProps {
  buildConfig: BuildConfig;
}
export class DynamoDBStack extends core.Stack {
  public readonly cognitoUserTable!: dynamodb.Table;
  public readonly cognitoAuthCodeTable!: dynamodb.Table;
  constructor(
    scope: core.Construct,
    id: string,
    props: DynamoDBStackDependencyProps,
  ) {
    super(scope, id, props);

    // Define the table
    this.cognitoUserTable = new dynamodb.Table(this, id + 'User', {
      partitionKey: {
        name: 'cognito_id',
        type: dynamodb.AttributeType.STRING,
      },
      sortKey: {
        name: 'federated_id',
        type: dynamodb.AttributeType.STRING,
      },
      tableName: SERVICE_PREFIX + 'Cognito_User',
      removalPolicy: REMOVAL_POLICY,
    });
    this.cognitoUserTable.addGlobalSecondaryIndex({
      partitionKey: {
        name: 'federated_id',
        type: dynamodb.AttributeType.STRING,
      },
      indexName: 'federated_id-index',
    });
    this.cognitoAuthCodeTable = new dynamodb.Table(this, id + 'AuthCode', {
      partitionKey: {
        name: 'auth_code',
        type: dynamodb.AttributeType.STRING,
      },
      tableName: SERVICE_PREFIX + 'Auth_Code',
      timeToLiveAttribute: 'ttl',
      removalPolicy: REMOVAL_POLICY,
    });
  }
}
