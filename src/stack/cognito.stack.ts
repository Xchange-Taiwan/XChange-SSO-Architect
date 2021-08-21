import * as path from 'path';
import * as cognito from '@aws-cdk/aws-cognito';
import * as iam from '@aws-cdk/aws-iam';
import * as lambda from '@aws-cdk/aws-lambda';
import * as lambdaPython from '@aws-cdk/aws-lambda-python';
import * as ssm from '@aws-cdk/aws-ssm';
import * as core from '@aws-cdk/core';
import {
  SERVICE_PREFIX,
  XChangeLambdaFunctionDefaultProps,
} from '../helper/helper';

interface CognitoStackDependencyProps extends core.StackProps {
  generalLayerStringParameter: ssm.IStringParameter;
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
    // dependencies
    const generalLayerStringParameter: ssm.IStringParameter =
      props.generalLayerStringParameter;
    // // fetch the Arn from param store
    // const authLayerArn = ssm.StringParameter.valueForStringParameter(
    //   this,
    //   '/layer/xchange_sso/auth',
    // );

    // generate layer version from arn
    const authLayer = lambda.LayerVersion.fromLayerVersionArn(
      this,
      id + 'authLayer',
      generalLayerStringParameter.stringValue,
    );

    // Authorizer
    this.userPool = new cognito.UserPool(this, id + 'SSOUserPool', {
      /**
       *  The default removal policy is RETAIN, which means that cdk destroy will not attempt to delete
       * the new table, and it will remain in your account until manually deleted. By setting the policy to
       * DESTROY, cdk destroy will delete the table (even if it has data in it)
       */
      removalPolicy: core.RemovalPolicy.DESTROY, // NOT recommended for production code

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
      new iam.Policy(this, id + 'defineAuthChallengeLambda--userpool-policy', {
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
