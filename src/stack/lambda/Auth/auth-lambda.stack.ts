import * as path from 'path';
import * as apigatewayv2 from '@aws-cdk/aws-apigatewayv2';
import * as apigatewayv2Integrations from '@aws-cdk/aws-apigatewayv2-integrations';
import * as cognito from '@aws-cdk/aws-cognito';
import * as dynamodb from '@aws-cdk/aws-dynamodb';
import * as iam from '@aws-cdk/aws-iam';
import * as lambdaPython from '@aws-cdk/aws-lambda-python';
import * as ssm from '@aws-cdk/aws-ssm';
import * as core from '@aws-cdk/core';
import {
  BuildConfig,
  SERVICE_PREFIX,
  XChangeLambdaFunctionDefaultProps,
} from '../../../helper/helper';

interface AuthLambdaStackDependencyProps extends core.StackProps {
  buildConfig: BuildConfig;
  apiGateway: apigatewayv2.HttpApi;
  userPool: cognito.IUserPool;
  userTable: dynamodb.ITable;
  cognitoAuthCodeTable: dynamodb.ITable;
}

export class AuthLambdaStack extends core.Stack {
  constructor(
    scope: core.Construct,
    id: string,
    props: AuthLambdaStackDependencyProps,
  ) {
    super(scope, id, props);
    const buildConfig: BuildConfig = props.buildConfig;

    // dependencies
    const apiGateway: apigatewayv2.HttpApi = props.apiGateway;
    const userPool: cognito.IUserPool = props.userPool;
    const userTable: dynamodb.ITable = props.userTable;
    const cognitoAuthCodeTable: dynamodb.ITable = props.cognitoAuthCodeTable;

    // Layer
    const authLayer = lambdaPython.PythonLayerVersion.fromLayerVersionArn(
      this,
      id + 'authLayer',
      ssm.StringParameter.valueForStringParameter(
        this,
        `/arn/sso/${buildConfig.stage}/authLayer`,
      ),
    );

    //  The code that defines your stack goes here;
    const loginLambda = new lambdaPython.PythonFunction(
      this,
      id + 'LoginLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'Login',
        entry: path.join('./', 'code', 'lambda', 'function', 'Auth', 'Login'),
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
    userTable.grantReadWriteData(loginLambda);
    cognitoAuthCodeTable.grantReadWriteData(loginLambda);
    const loginLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: loginLambda,
      });

    const registerLambda = new lambdaPython.PythonFunction(
      this,
      id + 'RegisterLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'Register',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Auth',
          'Register',
        ),
        layers: [authLayer],
        environment: {
          USER_POOL_ID: userPool.userPoolId,
          USER_TABLE_NAME: userTable.tableName,
        },
        initialPolicy: [
          new iam.PolicyStatement({
            actions: ['cognito-idp:DescribeUserPoolClient'],
            resources: [userPool.userPoolArn],
          }),
        ],
      },
    );
    userTable.grantReadWriteData(registerLambda);
    const registerLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: registerLambda,
      });

    const confirmRegisterLambda = new lambdaPython.PythonFunction(
      this,
      id + 'ConfirmRegisterLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'ConfirmRegister',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Auth',
          'ConfirmRegister',
        ),
        layers: [authLayer],
      },
    );
    const confirmRegisterLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: confirmRegisterLambda,
      });

    const resendConfirmLambda = new lambdaPython.PythonFunction(
      this,
      id + 'ResendConfirmLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'ResendConfirm',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Auth',
          'ResendConfirm',
        ),
        layers: [authLayer],
      },
    );
    const resendConfirmLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: resendConfirmLambda,
      });

    const requestResetPasswordLambda = new lambdaPython.PythonFunction(
      this,
      id + 'RequestResetPasswordLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'RequestResetPassword',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Auth',
          'RequestResetPassword',
        ),
        layers: [authLayer],
      },
    );
    const requestResetPasswordLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: requestResetPasswordLambda,
      });

    const resetPasswordLambda = new lambdaPython.PythonFunction(
      this,
      id + 'ResetPasswordLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'ResetPassword',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Auth',
          'ResetPassword',
        ),
        layers: [authLayer],
      },
    );
    const resetPasswordLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: resetPasswordLambda,
      });

    const changePasswordLambda = new lambdaPython.PythonFunction(
      this,
      id + 'ChangePasswordLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'ChangePassword',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Auth',
          'ChangePassword',
        ),
        layers: [authLayer],
      },
    );
    const changePasswordLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: changePasswordLambda,
      });

    const refreshLambda = new lambdaPython.PythonFunction(
      this,
      id + 'RefreshLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'Refresh',
        entry: path.join('./', 'code', 'lambda', 'function', 'Auth', 'Refresh'),
        layers: [authLayer],
      },
    );
    const refreshLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: refreshLambda,
      });

    const logoutLambda = new lambdaPython.PythonFunction(
      this,
      id + 'LogoutLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'Logout',
        entry: path.join('./', 'code', 'lambda', 'function', 'Auth', 'Logout'),
        layers: [authLayer],
        environment: {
          USER_POOL_ID: userPool.userPoolId,
        },
        initialPolicy: [
          new iam.PolicyStatement({
            actions: ['cognito-idp:DescribeUserPoolClient'],
            resources: [userPool.userPoolArn],
          }),
        ],
      },
    );
    const logoutLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: logoutLambda,
      });

    const logoutAllLambda = new lambdaPython.PythonFunction(
      this,
      id + 'logoutAllLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'LogoutAll',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Auth',
          'LogoutAll',
        ),
        layers: [authLayer],
        environment: {
          USER_POOL_ID: userPool.userPoolId,
        },
        initialPolicy: [
          new iam.PolicyStatement({
            actions: ['cognito-idp:DescribeUserPoolClient'],
            resources: [userPool.userPoolArn],
          }),
        ],
      },
    );
    const logoutAllLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: logoutAllLambda,
      });

    const checkEmailNotTakenLambda = new lambdaPython.PythonFunction(
      this,
      id + 'checkEmailNotTaken',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'CheckEmailNotTaken',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'Auth',
          'CheckEmailNotTaken',
        ),
        layers: [authLayer],
        environment: {
          USER_POOL_ID: userPool.userPoolId,
        },
        initialPolicy: [
          new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
              'cognito-idp:AdminGetUser',
              'cognito-idp:DescribeUserPoolClient',
            ],
            resources: [userPool.userPoolArn],
          }),
        ],
      },
    );
    const checkEmailNotTakenLambdaIntegration =
      new apigatewayv2Integrations.LambdaProxyIntegration({
        handler: checkEmailNotTakenLambda,
      });

    apiGateway.addRoutes({
      path: '/login',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: loginLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/refresh',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: refreshLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/register',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: registerLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/register/confirm',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: confirmRegisterLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/register/resend',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: resendConfirmLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/password',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: resetPasswordLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/password/request',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: requestResetPasswordLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/password/change',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: changePasswordLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/logout',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: logoutLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/logoutAll',
      methods: [apigatewayv2.HttpMethod.POST],
      integration: logoutAllLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });

    apiGateway.addRoutes({
      path: '/check',
      methods: [apigatewayv2.HttpMethod.GET],
      integration: checkEmailNotTakenLambdaIntegration,
      authorizer: new apigatewayv2.HttpNoneAuthorizer(),
      authorizationScopes: [],
    });
  }
}
