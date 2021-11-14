import * as path from 'path';
import * as apigatewayv2 from '@aws-cdk/aws-apigatewayv2';
import * as apigatewayv2Integrations from '@aws-cdk/aws-apigatewayv2-integrations';
import * as cognito from '@aws-cdk/aws-cognito';
import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as iam from '@aws-cdk/aws-iam';
import * as lambdaPython from '@aws-cdk/aws-lambda-python';
import * as secretsmanager from '@aws-cdk/aws-secretsmanager';
import * as ssm from '@aws-cdk/aws-ssm';
import * as core from '@aws-cdk/core';
import {
  BuildConfig,
  SERVICE_PREFIX,
  XChangeLambdaFunctionDefaultProps,
} from '../../../helper/helper';

interface Oauth2LambdaStackDependencyProps extends core.StackProps {
  buildConfig: BuildConfig;
  apiGateway: apigatewayv2.HttpApi;
  userPool: cognito.IUserPool;
  userTable: dynamodb.ITable;
  cognitoAuthCodeTable: dynamodb.ITable;
}

export class Oauth2LambdaStack extends core.Stack {
  constructor(
    scope: core.Construct,
    id: string,
    props: Oauth2LambdaStackDependencyProps,
  ) {
    super(scope, id, props);
    const buildConfig: BuildConfig = props.buildConfig;
    const apiGateway: apigatewayv2.HttpApi = props.apiGateway;
    const userPool: cognito.IUserPool = props.userPool;
    const userTable: dynamodb.ITable = props.userTable;
    const cognitoAuthCodeTable: dynamodb.ITable = props.cognitoAuthCodeTable;

    // Secret Manager
    const linkedInSecret = secretsmanager.Secret.fromSecretCompleteArn(
      this,
      id + 'SecretManager',
      buildConfig.externalParameters.linkedInSecretManagerArn,
    );

    // Layer
    const authLayer = lambdaPython.PythonLayerVersion.fromLayerVersionArn(
      this,
      id + 'authLayer',
      ssm.StringParameter.valueForStringParameter(
        this,
        `/arn/sso/${buildConfig.stage}/authLayer`,
      ),
    );

    const federateTokenExchangeLambda = new lambdaPython.PythonFunction(
      this,
      id + 'FederateTokenExchangeLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'FederateTokenExchange',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Oauth2',
          'FederateTokenExchange',
        ),
        layers: [authLayer],
        environment: {
          USER_POOL_ID: userPool.userPoolId,
          USER_TABLE_NAME: userTable.tableName,
          LINKEDIN_SECRET_ARN: linkedInSecret.secretName,
          AUTH_CODE_TABLE_NAME: cognitoAuthCodeTable.tableName,
        },
        initialPolicy: [
          new iam.PolicyStatement({
            actions: ['cognito-idp:DescribeUserPoolClient'],
            resources: [userPool.userPoolArn],
          }),
        ],
      },
    );
    linkedInSecret.grantRead(federateTokenExchangeLambda);
    userTable.grantReadWriteData(federateTokenExchangeLambda);
    cognitoAuthCodeTable.grantReadWriteData(federateTokenExchangeLambda);
    const federateTokenExchangeLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: federateTokenExchangeLambda,
      });

    //  The code that defines your stack goes here;
    const tokenLambda = new lambdaPython.PythonFunction(
      this,
      id + 'TokenLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'Token',
        entry: path.join('./', 'code', 'lambda', 'function', 'Oauth2', 'Token'),
        layers: [authLayer],
        environment: {
          USER_POOL_ID: userPool.userPoolId,
          USER_TABLE_NAME: userTable.tableName,
          AUTH_CODE_TABLE_NAME: cognitoAuthCodeTable.tableName,
        },
        initialPolicy: [
          new iam.PolicyStatement({
            actions: ['cognito-idp:DescribeUserPoolClient'],
            resources: [userPool.userPoolArn],
          }),
        ],
      },
    );
    userTable.grantReadWriteData(tokenLambda);
    cognitoAuthCodeTable.grantReadWriteData(tokenLambda);
    const tokenLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: tokenLambda,
      });

    const userinfoLambda = new lambdaPython.PythonFunction(
      this,
      id + 'UserInfoLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'UserInfo',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Oauth2',
          'UserInfo',
        ),
        layers: [authLayer],
      },
    );
    const userinfoLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: userinfoLambda,
      });

    apiGateway.addRoutes({
      path: '/oauth2/federateTokenExchange',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: federateTokenExchangeLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/oauth2/token',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: tokenLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/oauth2/userinfo',
      methods: [apigatewayv2.HttpMethod.GET],
      integration: userinfoLambdaIntegration,
    });
  }
}
