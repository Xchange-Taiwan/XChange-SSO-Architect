import * as core from '@aws-cdk/core';
import * as pipelines from '@aws-cdk/pipelines';
import {
  getBuildConfigSet,
  STACK_PREFIX,
  XChangeSSOEnvConfigSet,
} from './helper/helper';
import { PipelineStack } from './stack/pipeline.stack.ts';
import { BackendStage } from './stage/backend.stage';
import { FrontendStage } from './stage/frontend.stage';
import { BackendLayerStage } from './stage/layer.stage';

const app = new core.App();

async function main() {
  const buildConfigSet: XChangeSSOEnvConfigSet = await getBuildConfigSet();

  const pipelineStack = new PipelineStack(app, STACK_PREFIX + 'PipelineStack', {
    env: buildConfigSet.deploymentAccount,
  });

  // Because of [lambda] deployment failure on updates to cross-stack layers https://github.com/aws/aws-cdk/issues/1972
  pipelineStack.pipeline.addStage(
    new BackendLayerStage(app, STACK_PREFIX + 'BackendLayerStage', {
      env: buildConfigSet.production.backendAccount,
      buildConfig: buildConfigSet.production,
    }),
    {
      pre: [new pipelines.ManualApprovalStep('Promote-To-Prod')],
    },
  );

  const deployWave = pipelineStack.pipeline.addWave(
    'DeployBackendAndFrontendCDK',
  );

  deployWave.addStage(
    new BackendStage(app, STACK_PREFIX + 'BackendStage', {
      env: buildConfigSet.production.backendAccount,
      buildConfig: buildConfigSet.production,
    }),
  );

  deployWave.addStage(
    new FrontendStage(app, STACK_PREFIX + 'FrontendStage', {
      env: buildConfigSet.production.frontendAccount,
      buildConfig: buildConfigSet.production,
    }),
  );

  app.synth();
}

void main();
