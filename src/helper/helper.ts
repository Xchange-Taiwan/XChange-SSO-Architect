import * as lambda from '@aws-cdk/aws-lambda';
import * as core from '@aws-cdk/core';
import * as aws from 'aws-sdk';

export const SERVICE_PREFIX = 'XChange_SSO_Architect_';

export const XChangeLambdaFunctionDefaultProps = {
  index: 'app.py',
  runtime: lambda.Runtime.PYTHON_3_8,
  handler: 'lambda_handler',
  memorySize: 512,
  timeout: core.Duration.seconds(6),
};

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

export const getBuildConfig = async (): Promise<any> => {
  let ssm: aws.SSM | undefined = undefined;

  /**
   * if in CodeBuild, process.env.CDK_DEVELOPMENT_ARN will undefined
   * but in local developmen, must set export CDK_DEVELOPMENT_ARN="'arn:aws:iam::XXXXXXXXXXXXX:role/OrganizationAccountAccessRole'"
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

  // Get ssm value
  const domainAcmAccountIDRes = await ssm
    .getParameter({
      Name: '/account/share/domainAcm',
    })
    .promise();
  const domainAcmAccountID = domainAcmAccountIDRes.Parameter?.Value;
  if (!domainAcmAccountID) {
    throw new Error("Parameter: /account/share/domainAcm isn't exist!");
  }

  const ssoDevelopmentAccountIDRes = await ssm
    .getParameter({
      Name: '/account/sso/development',
    })
    .promise();
  const ssoDevelopmentAccountID = ssoDevelopmentAccountIDRes.Parameter?.Value;
  if (!ssoDevelopmentAccountID) {
    throw new Error("Parameter: /account/sso/development isn't exist!");
  }

  const ssoBackendProdAccountIDRes = await ssm
    .getParameter({
      Name: '/account/sso/prod/backend',
    })
    .promise();
  const ssoBackendProdAccountID = ssoBackendProdAccountIDRes.Parameter?.Value;
  if (!ssoBackendProdAccountID) {
    throw new Error("Parameter: /account/sso/prod/backend isn't exist!");
  }

  const ssoFrontendAccountIDRes = await ssm
    .getParameter({
      Name: '/account/sso/frontend',
    })
    .promise();
  const ssoFrontendAccountID = ssoFrontendAccountIDRes.Parameter?.Value;
  if (!ssoFrontendAccountID) {
    throw new Error("Parameter: /account/sso/frontend isn't exist!");
  }

  const wildcardXchangeDomainCertificateArnRes = await ssm
    .getParameter({
      Name: '/arn/share/domainAcm/wildcardXchangeDomain',
    })
    .promise();
  const wildcardXchangeDomainCertificateArn =
    wildcardXchangeDomainCertificateArnRes.Parameter?.Value;
  if (!wildcardXchangeDomainCertificateArn) {
    throw new Error(
      "Parameter: /arn/share/domainAcm/wildcardXchangeDomain isn't exist!",
    );
  }

  const linkedInSecretArnRes = await ssm
    .getParameter({
      Name: '/arn/share/secret/linkedIn',
    })
    .promise();
  const linkedInSecretArn = linkedInSecretArnRes.Parameter?.Value;
  if (!linkedInSecretArn) {
    throw new Error("Parameter: /arn/share/secret/linkedIn isn't exist!");
  }

  const organizations = {
    domainAcm: {
      account: domainAcmAccountID,
      region: 'ap-southeast-1',
    },
    ssoDevelopment: {
      account: ssoDevelopmentAccountID,
      region: 'ap-southeast-1',
    },
    ssoBackendProd: {
      account: ssoBackendProdAccountID,
      region: 'ap-southeast-1',
    },
    ssoFrontend: {
      account: ssoFrontendAccountID,
      region: 'ap-southeast-1',
    },
  };

  const buildConfig = {
    organizations,
    wildcardXchangeDomainCertificateArn,
    linkedInSecretArn,
  };
  console.log('Set Build Config:');
  console.log(buildConfig);
  return buildConfig;
};
