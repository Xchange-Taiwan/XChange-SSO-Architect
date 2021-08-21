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
  const params = await ssm
    .getParameters({
      Names: [
        '/account/share/domainAcm',
        '/account/sso/development',
        '/account/sso/prod/backend',
        '/account/sso/frontend',
        '/arn/share/domainAcm/wildcardXchangeDomain',
        '/arn/share/secret/linkedIn',
      ],
    })
    .promise();

  let organizations: {
    [key: string]: core.Environment;
  } = {};
  let wildcardXchangeDomainCertificateArn: string = '';
  let linkedInSecretArn: string = '';

  params.Parameters?.forEach((param) => {
    switch (param.Name) {
      case '/account/share/domainAcm': {
        organizations.domainAcm = {
          account: param.Value,
          region: 'ap-southeast-1',
        };
        break;
      }
      case '/account/sso/development': {
        organizations.ssoDevelopment = {
          account: param.Value,
          region: 'ap-southeast-1',
        };
        break;
      }
      case '/account/sso/prod/backend': {
        organizations.ssoBackendProd = {
          account: param.Value,
          region: 'ap-southeast-1',
        };
        break;
      }
      case '/account/sso/frontend': {
        organizations.ssoFrontend = {
          account: param.Value,
          region: 'ap-southeast-1',
        };
        break;
      }
      case '/arn/share/domainAcm/wildcardXchangeDomain': {
        wildcardXchangeDomainCertificateArn = param.Value as string;
        break;
      }
      case '/arn/share/secret/linkedIn': {
        linkedInSecretArn = param.Value as string;
        break;
      }
    }
  });

  const buildConfig = {
    organizations,
    wildcardXchangeDomainCertificateArn,
    linkedInSecretArn,
  };
  console.log('Set Build Config:');
  console.log(buildConfig);
  return buildConfig;
};
