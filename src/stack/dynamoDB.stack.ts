import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as core from '@aws-cdk/core';
import { SERVICE_PREFIX } from '../helper/helper';

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

      /**
       *  The default removal policy is RETAIN, which means that cdk destroy will not attempt to delete
       * the new table, and it will remain in your account until manually deleted. By setting the policy to
       * DESTROY, cdk destroy will delete the table (even if it has data in it)
       */
      removalPolicy: core.RemovalPolicy.DESTROY, // NOT recommended for production code
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
