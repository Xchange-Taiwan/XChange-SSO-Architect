import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as core from '@aws-cdk/core';
import { SERVICE_PREFIX } from '../helper/helper';
import { APP_REMOVALPOLICY } from '../main';

export class DynamoDBStack extends core.Stack {
  public readonly cognitoUserTable!: dynamodb.Table;
  constructor(scope: core.Construct, id: string, props?: core.StackProps) {
    super(scope, id, props);

    // 定義資料庫
    this.cognitoUserTable = new dynamodb.Table(this, id + 'User', {
      partitionKey: {
        name: 'cognito_id',
        type: dynamodb.AttributeType.STRING,
      },
      tableName: SERVICE_PREFIX + 'Cognito_User',
      removalPolicy: APP_REMOVALPOLICY,
    });
    // this.cognitoUserTable.addGlobalSecondaryIndex({
    //   partitionKey: {
    //     name: 'linkedin_id',
    //     type: dynamodb.AttributeType.STRING,
    //   },
    //   indexName: 'linkedin_id-index',
    // });
  }
}
