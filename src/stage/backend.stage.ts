import * as core from '@aws-cdk/core';
import { BuildConfig } from '../helper/helper';
import { ApiGatewayStack } from '../stack/api-gateway.stack';
import { CognitoStack } from '../stack/cognito.stack';
import { DynamoDBStack } from '../stack/dynamoDB.stack';
import { AuthLambdaStack } from '../stack/lambda/Auth/auth-lambda.stack';
import { Oauth2LambdaStack } from '../stack/lambda/OAuth2/oauth2-lambda.stack';
interface BackendStageDependencyProps extends core.StackProps {
  buildConfig: BuildConfig;
}
export class BackendStage extends core.Stage {
  constructor(
    scope: core.Construct,
    id: string,
    props: BackendStageDependencyProps,
  ) {
    super(scope, id, props);
    const buildConfig: BuildConfig = props.buildConfig;

    const cognitoStack = new CognitoStack(this, id + 'CognitoStack', {
      env: buildConfig.backendAccount,
      buildConfig,
    });

    const apiGatewayStack = new ApiGatewayStack(this, id + 'ApiGatewayStack', {
      env: buildConfig.backendAccount,
      buildConfig,
      userPool: cognitoStack.userPool,
      userPoolClient: cognitoStack.crmClient,
    });

    const dynamoDBStack = new DynamoDBStack(this, id + 'DynamoDBStack', {
      env: buildConfig.backendAccount,
      buildConfig,
    });

    // Lambda
    new AuthLambdaStack(this, id + 'AuthLambdaStack', {
      env: buildConfig.backendAccount,
      buildConfig,
      apiGateway: apiGatewayStack.apiGateway,
      userPool: cognitoStack.userPool,
      userTable: dynamoDBStack.cognitoUserTable,
      cognitoAuthCodeTable: dynamoDBStack.cognitoAuthCodeTable,
    });

    new Oauth2LambdaStack(this, id + 'Oauth2LambdaStack', {
      env: buildConfig.backendAccount,
      buildConfig,
      apiGateway: apiGatewayStack.apiGateway,
      userPool: cognitoStack.userPool,
      userTable: dynamoDBStack.cognitoUserTable,
      cognitoAuthCodeTable: dynamoDBStack.cognitoAuthCodeTable,
    });
  }
}
