import * as path from 'path';
import * as apigatewayv2 from '@aws-cdk/aws-apigatewayv2';
import * as apigatewayv2Integrations from '@aws-cdk/aws-apigatewayv2-integrations';
import * as cognito from '@aws-cdk/aws-cognito';
import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as lambdaPython from '@aws-cdk/aws-lambda-python';
import * as secretsmanager from '@aws-cdk/aws-secretsmanager';
import * as ssm from '@aws-cdk/aws-ssm';
import * as core from '@aws-cdk/core';
import {
  SERVICE_PREFIX,
  XChangeLambdaFunctionDefaultProps,
} from '../../../helper/helper';

interface Oauth2LambdaStackDependencyProps extends core.StackProps {
  apiGateway: apigatewayv2.HttpApi;
  userPool: cognito.IUserPool;
  userTable: dynamodb.ITable;
  generalLayerStringParameter: ssm.IStringParameter;
  linkedInSecretArn: string;
}

export class Oauth2LambdaStack extends core.Stack {
  constructor(
    scope: core.Construct,
    id: string,
    props: Oauth2LambdaStackDependencyProps,
  ) {
    super(scope, id, props);
    // dependencies
    const apiGateway: apigatewayv2.HttpApi = props.apiGateway;
    const userPool: cognito.IUserPool = props.userPool;
    const userTable: dynamodb.ITable = props.userTable;
    const generalLayerStringParameter: ssm.IStringParameter =
      props.generalLayerStringParameter;
    const linkedInSecretArn: string = props.linkedInSecretArn;

    // Secret Manager
    const linkedInSecret = secretsmanager.Secret.fromSecretCompleteArn(
      this,
      id + 'SecretManager',
      linkedInSecretArn,
    );

    // generate layer version from arn
    const authLayer = lambdaPython.PythonLayerVersion.fromLayerVersionArn(
      this,
      id + 'authLayer',
      generalLayerStringParameter.stringValue,
    );

    //  The code that defines your stack goes here;
    const oauth2Lambda = new lambdaPython.PythonFunction(
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
          LINKEDIN_SECRET_ARN: linkedInSecret.secretName,
        },
      },
    );
    linkedInSecret.grantRead(oauth2Lambda);
    userTable.grantReadWriteData(oauth2Lambda);
    const oauth2LambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: oauth2Lambda,
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
      path: '/oauth2/token',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: oauth2LambdaIntegration,
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
