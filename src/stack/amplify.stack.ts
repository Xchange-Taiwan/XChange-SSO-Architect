import * as amplify from '@aws-cdk/aws-amplify';
import * as core from '@aws-cdk/core';
import { SERVICE_PREFIX } from '../helper/helper';

export class AmplifyStack extends core.Stack {
  public readonly amplifyApp!: amplify.App;

  constructor(scope: core.Construct, id: string, props?: core.StackProps) {
    super(scope, id, props);

    // Amplify App
    this.amplifyApp = new amplify.App(this, 'AmplifyApp', {
      appName: SERVICE_PREFIX + 'Amplify_App',
      sourceCodeProvider: new amplify.GitHubSourceCodeProvider({
        owner: 'Xchange-Taiwan',
        repository: 'XChange-SSO',
        oauthToken: core.SecretValue.secretsManager('prod/github/oauth'),
      }),
      autoBranchCreation: {
        // Automatically connect branches that match a pattern set
        patterns: ['feature/*', 'fix/*'],
      },
      autoBranchDeletion: true, // Automatically disconnect a branch when you delete a branch from your repository
    });
    // SPA Redirect
    this.amplifyApp.addCustomRule(
      amplify.CustomRule.SINGLE_PAGE_APPLICATION_REDIRECT,
    );

    const domain = this.amplifyApp.addDomain('xchange.com.tw', {
      enableAutoSubdomain: true, // in case subdomains should be auto registered for branches
      autoSubdomainCreationPatterns: ['*', 'pr*'], // regex for branches that should auto register subdomains
    });

    const accessControl =
      amplify.BasicAuth.fromGeneratedPassword('xchangeProduct');

    // Add Branch
    const main = this.amplifyApp.addBranch('main');
    const staging = this.amplifyApp.addBranch('staging', {
      basicAuth: accessControl,
    });
    const dev = this.amplifyApp.addBranch('dev', {
      basicAuth: accessControl,
    });

    domain.mapSubDomain(main, 'sso');
    domain.mapSubDomain(staging, 'sso-staging');
    domain.mapSubDomain(dev, 'sso-dev');
  }
}
