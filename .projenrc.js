const { AwsCdkTypeScriptApp } = require('projen');
const project = new AwsCdkTypeScriptApp({
  cdkVersion: '1.119.0',
  defaultReleaseBranch: 'main',
  name: 'XChange-SSO-Architect',
  cdkDependencies: [
    '@aws-cdk/aws-codepipeline',
    '@aws-cdk/aws-codepipeline-actions',
    '@aws-cdk/pipelines',
    '@aws-cdk/aws-lambda',
    '@aws-cdk/aws-lambda-python',
    '@aws-cdk/aws-cognito',
    '@aws-cdk/aws-apigatewayv2',
    '@aws-cdk/aws-apigatewayv2-authorizers',
    '@aws-cdk/aws-apigatewayv2-integrations',
    '@aws-cdk/aws-certificatemanager',
    '@aws-cdk/aws-secretsmanager',
    '@aws-cdk/aws-codebuild',
    '@aws-cdk/aws-dynamodb',
    '@aws-cdk/aws-amplify',
    '@aws-cdk/aws-ssm',
    '@aws-cdk/aws-kms',
    '@aws-cdk/aws-iam',
  ],
  deps: ['aws-sdk'],
  context: {
    '@aws-cdk/core:newStyleStackSynthesis': true,
  },
  devDeps: ['prettier', 'eslint-config-prettier', 'eslint-plugin-prettier', 'cdk-assume-role-credential-plugin@^1.2.1'],
  gitignore: ['.DS_Store', '.lambda-core', '.config'],

  // cdkDependencies: undefined,        /* Which AWS CDK modules (those that start with "@aws-cdk/") this app uses. */
  // deps: [],                          /* Runtime dependencies of this module. */
  // description: undefined,            /* The description is just a string that helps people understand the purpose of the package. */
  // devDeps: [],                       /* Build dependencies for this module. */
  // packageName: undefined,            /* The "name" in package.json. */
  // projectType: ProjectType.UNKNOWN,  /* Which type of project this is (library/app). */
  // release: undefined,                /* Add release management to this project. */
});
project.synth();
