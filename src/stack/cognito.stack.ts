import * as path from 'path';
import * as cognito from '@aws-cdk/aws-cognito';
import * as iam from '@aws-cdk/aws-iam';
import * as lambdaPython from '@aws-cdk/aws-lambda-python';
import * as ssm from '@aws-cdk/aws-ssm';
import * as core from '@aws-cdk/core';
import {
  BuildConfig,
  SERVICE_PREFIX,
  XChangeLambdaFunctionDefaultProps,
} from '../helper/helper';

interface CognitoStackDependencyProps extends core.StackProps {
  buildConfig: BuildConfig;
}
export class CognitoStack extends core.Stack {
  public readonly userPool!: cognito.UserPool;
  public readonly crmClient!: cognito.UserPoolClient;

  constructor(
    scope: core.Construct,
    id: string,
    props: CognitoStackDependencyProps,
  ) {
    super(scope, id, props);
    const buildConfig: BuildConfig = props.buildConfig;

    // dependencies
    // Layer
    const authLayer = lambdaPython.PythonLayerVersion.fromLayerVersionArn(
      this,
      id + 'authLayer',
      ssm.StringParameter.valueForStringParameter(
        this,
        `/arn/sso/${buildConfig.stage}/authLayer`,
      ),
    );

    // Authorizer
    this.userPool = new cognito.UserPool(this, id + 'SSOUserPool', {
      removalPolicy: buildConfig.removalPolicy,

      userPoolName: SERVICE_PREFIX + 'UserPool',
      selfSignUpEnabled: true,

      signInAliases: {
        username: false,
        email: true,
      },
      autoVerify: { email: true, phone: false },
      signInCaseSensitive: false,

      standardAttributes: {
        email: {
          required: true,
          mutable: false,
        },
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,

      // 密碼政策
      passwordPolicy: {
        minLength: 6,
        requireUppercase: false,
        requireLowercase: false,
        requireDigits: false,
        requireSymbols: false,
        tempPasswordValidity: core.Duration.days(7),
      },
    });

    this.crmClient = this.userPool.addClient('XConnect', {
      authFlows: {
        userPassword: true,
        userSrp: false,

        // use to linkedIn token log in
        custom: true,
      },
      oAuth: {
        flows: {
          authorizationCodeGrant: true,
          implicitCodeGrant: true,
        },
        scopes: [
          cognito.OAuthScope.OPENID,
          cognito.OAuthScope.PROFILE,
          cognito.OAuthScope.EMAIL,
          cognito.OAuthScope.PHONE,
        ],
        callbackUrls: ['https://connect.xchange.com.tw/auth/callback'],
        logoutUrls: ['https://connect.xchange.com.tw/logout'],
      },
    });

    //  The code that defines your stack goes here;
    const customMessageLambda = new lambdaPython.PythonFunction(
      this,
      id + 'CustomMessageLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'CustomMessage',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'CognitoTriggerFunction',
          'CustomMessage',
        ),
        layers: [authLayer],
      },
    );
    const defineAuthChallengeLambda = new lambdaPython.PythonFunction(
      this,
      id + 'DefineAuthChallengeLambda',
      {
        ...XChangeLambdaFunctionDefaultProps,
        functionName: SERVICE_PREFIX + 'DefineAuthChallenge',
        entry: path.join(
          './',
          'code',
          'lambda',
          'function',
          'CognitoTriggerFunction',
          'DefineAuthChallenge',
        ),
      },
    );

    // Binding Cognito Trigger
    this.userPool.addTrigger(
      cognito.UserPoolOperation.CUSTOM_MESSAGE,
      customMessageLambda,
    );

    customMessageLambda.role?.attachInlinePolicy(
      new iam.Policy(this, id + 'customMessageLambda-userpool-policy', {
        statements: [
          new iam.PolicyStatement({
            actions: ['cognito-idp:DescribeUserPool'],
            resources: [this.userPool.userPoolArn],
          }),
        ],
      }),
    );

    this.userPool.addTrigger(
      cognito.UserPoolOperation.DEFINE_AUTH_CHALLENGE,
      defineAuthChallengeLambda,
    );

    defineAuthChallengeLambda.role?.attachInlinePolicy(
      new iam.Policy(this, id + 'defineAuthChallengeLambda-userpool-policy', {
        statements: [
          new iam.PolicyStatement({
            actions: ['cognito-idp:DescribeUserPool'],
            resources: [this.userPool.userPoolArn],
          }),
        ],
      }),
    );
  }
}
