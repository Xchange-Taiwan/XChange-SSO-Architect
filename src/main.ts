import * as core from '@aws-cdk/core';
import * as pipelines from '@aws-cdk/pipelines';
import { getBuildConfig } from './helper/helper';
import { PipelineStack } from './stack/pipeline-stack.ts';
import { SSOBackend } from './stage/backend.stage';
import { SSOFrontend } from './stage/frontend.stage';

const app = new core.App();
const STACK_PREFIX = 'XChangeSSOArchitect';

async function main() {
  const buildConfig = await getBuildConfig();

  const pipelineStack = new PipelineStack(app, STACK_PREFIX + 'PipelineStack', {
    env: buildConfig.organizations.ssoDevelopment,
  });

  // Because ACM Create domain can't use cross account

  // const shareWave = pipelineStack.pipeline.addWave(
  //   'CreateIAMRoleInSharedResource',
  // );

  // const domainAcmStage = new DomainAcmStage(
  //   app,
  //   STACK_PREFIX + 'DomainAcmStage',
  //   {
  //     env: buildConfig.organizations.domainAcm,
  //     organizations: buildConfig.organizations,
  //     wildcardXchangeDomainCertificateArn:
  //       buildConfig.wildcardXchangeDomainCertificateArn,
  //   },
  // );
  // shareWave.addStage(domainAcmStage);

  const deployWave = pipelineStack.pipeline.addWave(
    'DeployBackendandFrontendCDK',
  );

  deployWave.addStage(
    new SSOBackend(app, STACK_PREFIX + 'SSOBackend', {
      env: buildConfig.organizations.ssoBackendProd,
      wildcardXchangeDomainCertificateArn:
        buildConfig.wildcardXchangeDomainCertificateArn,
      linkedInSecretArn: buildConfig.linkedInSecretArn,
    }),
    {
      pre: [
        new pipelines.ShellStep('SSOBackendPreLayerStackShellStep', {
          commands: [
            'yarn install --frozen-lockfile',
            'yarn build',
            'npx cdk deploy "*LayerStack" --require-approval never',
          ],
        }),
      ],
    },
  );

  deployWave.addStage(
    new SSOFrontend(app, STACK_PREFIX + 'SSOFrontend', {
      env: buildConfig.organizations.ssoFrontend,
    }),
  );

  app.synth();
}

void main();
