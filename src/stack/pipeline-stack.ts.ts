import * as iam from '@aws-cdk/aws-iam';
import * as core from '@aws-cdk/core';
import * as pipelines from '@aws-cdk/pipelines';
import { SERVICE_PREFIX } from '../helper/helper';

export class PipelineStack extends core.Stack {
  public readonly cdkPipeline!: pipelines.CdkPipeline;
  public readonly pipeline!: pipelines.CodePipeline;
  constructor(scope: core.Construct, id: string, props?: core.StackProps) {
    super(scope, id, props);

    const source = pipelines.CodePipelineSource.gitHub(
      'Xchange-Taiwan/XChange-SSO-Architect',
      'main',
      {
        // This is optional
        authentication: core.SecretValue.secretsManager('prod/github/oauth'),
      },
    );

    this.pipeline = new pipelines.CodePipeline(this, 'Pipeline', {
      pipelineName: SERVICE_PREFIX + 'CDKPipeline',
      // Encrypt artifacts, required for cross-account deployments
      crossAccountKeys: true,
      codeBuildDefaults: {
        rolePolicy: [
          new iam.PolicyStatement({
            actions: ['sts:AssumeRole'],
            resources: ['arn:aws:iam::*:role/cdk-hnb659fds-lookup-role-*'],
          }),
          new iam.PolicyStatement({
            sid: 'SSMReadOnly',
            effect: iam.Effect.ALLOW,
            actions: ['ssm:Get*', 'ssm:List*'],
            resources: ['*'],
          }),
        ],
        buildEnvironment: {
          privileged: true,
        },
      },
      synth: new pipelines.ShellStep('Synth', {
        input: source,
        commands: [
          'yarn install --frozen-lockfile',
          'yarn build',
          'npx cdk synth',
        ],
      }),
    });
  }
}
