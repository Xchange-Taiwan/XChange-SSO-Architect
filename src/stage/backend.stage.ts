import * as core from '@aws-cdk/core';
import { ApiGatewayStack } from '../stack/api-gateway.stack';
import { CognitoStack } from '../stack/cognito.stack';
import { DynamoDBStack } from '../stack/dynamoDB.stack';
import { AuthLambdaStack } from '../stack/lambda/Auth/auth-lambda.stack';
import { Oauth2LambdaStack } from '../stack/lambda/OAuth2/oauth2-lambda.stack';
import { AuthLayerStack } from '../stack/layer/auth-layer.stack';

interface SSOBackendDependencyProps extends core.StackProps {
  wildcardXchangeDomainCertificateArn: string;
  linkedInSecretArn: string;
}
export class SSOBackend extends core.Stage {
  constructor(
    scope: core.Construct,
    id: string,
    props: SSOBackendDependencyProps,
  ) {
    super(scope, id, props);
    const wildcardXchangeDomainCertificateArn: string =
      props.wildcardXchangeDomainCertificateArn;
    const linkedInSecretArn: string = props.linkedInSecretArn;

    // // deplay first => Layer
    const authLayerStack = new AuthLayerStack(this, id + 'AuthLayerStack');

    const cognitoStack = new CognitoStack(this, id + 'CognitoStack', {
      generalLayerStringParameter: authLayerStack.generalLayerStringParameter,
    });

    const apiGatewayStack = new ApiGatewayStack(this, id + 'ApiGatewayStack', {
      userPool: cognitoStack.userPool,
      userPoolClient: cognitoStack.crmClient,
      wildcardXchangeDomainCertificateArn,
    });

    const dynamoDBStack = new DynamoDBStack(this, id + 'DynamoDBStack');

    // Lambda
    new AuthLambdaStack(this, id + 'AuthLambdaStack', {
      apiGateway: apiGatewayStack.apiGateway,
      userPool: cognitoStack.userPool,
      userTable: dynamoDBStack.cognitoUserTable,
      generalLayerStringParameter: authLayerStack.generalLayerStringParameter,
    });

    new Oauth2LambdaStack(this, id + 'Oauth2LambdaStack', {
      apiGateway: apiGatewayStack.apiGateway,
      userPool: cognitoStack.userPool,
      userTable: dynamoDBStack.cognitoUserTable,
      generalLayerStringParameter: authLayerStack.generalLayerStringParameter,
      linkedInSecretArn: linkedInSecretArn,
    });
  }
}
