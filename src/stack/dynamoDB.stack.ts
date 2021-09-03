import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as core from '@aws-cdk/core';
import { BuildConfig, SERVICE_PREFIX } from '../helper/helper';

interface DynamoDBStackDependencyProps extends core.StackProps {
  buildConfig: BuildConfig;
}
export class DynamoDBStack extends core.Stack {
  public readonly cognitoUserTable!: dynamodb.Table;
  constructor(
    scope: core.Construct,
    id: string,
    props: DynamoDBStackDependencyProps,
  ) {
    super(scope, id, props);
    const buildConfig: BuildConfig = props.buildConfig;

    // 定義資料庫
    this.cognitoUserTable = new dynamodb.Table(this, id + 'User', {
      partitionKey: {
        name: 'cognito_id',
        type: dynamodb.AttributeType.STRING,
      },
      tableName: SERVICE_PREFIX + 'Cognito_User',
      removalPolicy: buildConfig.removalPolicy,
    });
  }
}
