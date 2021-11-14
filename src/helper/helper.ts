import * as lambda from '@aws-cdk/aws-lambda';
import * as core from '@aws-cdk/core';
import * as aws from 'aws-sdk';

export const SERVICE_PREFIX = 'XChange_SSO_Architect_';
export const STACK_PREFIX = 'XChangeSSO';
export const REMOVAL_POLICY = core.RemovalPolicy.DESTROY;
export const REGION = 'ap-southeast-1';

export const QOOBITLambdaFunctionDefaultProps = {
  index: 'app.py',
  runtime: lambda.Runtime.PYTHON_3_8,
  handler: 'lambda_handler',
  memorySize: 512,
  timeout: core.Duration.seconds(6),
};

export const XChangeLambdaFunctionDefaultProps = {
  index: 'app.py',
  runtime: lambda.Runtime.PYTHON_3_8,
  handler: 'lambda_handler',
  memorySize: 512,
  timeout: core.Duration.seconds(6),
};

export interface XChangeSSOEnvConfigSet {
  deploymentAccount: core.Environment;
  // development: BuildConfig;
  // staging: BuildConfig;
  production: BuildConfig;
}
export interface BuildConfig {
  stage: string;
  backendAccount: core.Environment;
  frontendAccount: core.Environment;
  removalPolicy: core.RemovalPolicy;
  externalParameters: {
    linkedInSecretManagerArn: string;
    wildcardXchangeDomainCertificateArn: string;
  };
}

const getCrossAccountCredentials = async (
  developmentArn: string,
): Promise<any> => {
  return new Promise((resolve, reject) => {
    const timestamp = new Date().getTime();
    const params = {
      RoleArn: developmentArn,
      RoleSessionName: `sdk-session-${timestamp}`,
    };
    const sts = new aws.STS();
    sts.assumeRole(params, (err, data) => {
      if (err) {
        reject(err);
      } else {
        if (data.Credentials) {
          resolve({
            accessKeyId: data.Credentials.AccessKeyId,
            secretAccessKey: data.Credentials.SecretAccessKey,
            sessionToken: data.Credentials.SessionToken,
          });
        }
        resolve(() => {});
      }
    });
  });
};

export const getBuildConfigSet = async (): Promise<any> => {
  let ssm: aws.SSM | undefined = undefined;

  /**
   * if in CodeBuild, process.env.CDK_DEVELOPMENT_ARN will undefined
   * but in local development, must set export CDK_DEVELOPMENT_ARN="arn:aws:iam::XXXXX:role/OrganizationAccountAccessRole"
   *
   */
  const developmentArn = process.env.CDK_DEVELOPMENT_ARN;
  if (developmentArn) {
    console.log('Local Development Role use:', developmentArn);
    // Set Cross Account SDK Credential
    const accessparams: {
      accessKeyId: string;
      secretAccessKey: string;
      sessionToken: string;
    } = await getCrossAccountCredentials(developmentArn);
    if (accessparams) {
      ssm = new aws.SSM(accessparams);
    }
  }

  if (!ssm) {
    ssm = new aws.SSM();
  }

  const ssmPaths: { [key: string]: string } = {
    deploymentAccountID: '/account/sso/deployment',
    productionSsoBackendAccountID: '/account/sso/prod/backend',
    productionSsoFrontendAccountID: '/account/sso/frontend',
    productionBackendWildcardXchangeDomainCertificateArn:
      '/arn/sso/production/backend/wildcardXchangeDomain',
    productionLinkedInSecretManagerArn:
      '/arn/sso/production/backend/linkedInSecretManager',
  };

  const ssmValues: { [key: string]: string } = {};

  for (const key in ssmPaths) {
    const ssmPath = ssmPaths[key];
    const ssmGetParameterResponse = await ssm
      .getParameter({
        Name: ssmPath,
      })
      .promise();
    const ssmValue = ssmGetParameterResponse.Parameter?.Value;
    if (!ssmValue) {
      throw new Error(`Parameter: ${ssmPath} isn't exist!`);
    }
    ssmValues[key] = ssmValue;
  }

  const buildConfigSet: XChangeSSOEnvConfigSet = {
    deploymentAccount: {
      account: ssmValues.deploymentAccountID,
      region: REGION,
    },
    production: {
      stage: 'production',
      removalPolicy: core.RemovalPolicy.RETAIN,
      backendAccount: {
        account: ssmValues.productionSsoBackendAccountID,
        region: REGION,
      },
      frontendAccount: {
        account: ssmValues.productionSsoFrontendAccountID,
        region: REGION,
      },
      externalParameters: {
        linkedInSecretManagerArn: ssmValues.productionLinkedInSecretManagerArn,
        wildcardXchangeDomainCertificateArn:
          ssmValues.productionBackendWildcardXchangeDomainCertificateArn,
      },
    },
  };

  console.log('Set Build Config:');
  console.log(buildConfigSet);
  return buildConfigSet;
};
