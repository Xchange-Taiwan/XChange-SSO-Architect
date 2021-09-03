import * as core from '@aws-cdk/core';
import { BuildConfig } from '../helper/helper';
import { AmplifyStack } from '../stack/amplify.stack';

interface FrontendStageDependencyProps extends core.StageProps {
  buildConfig: BuildConfig;
}
export class FrontendStage extends core.Stage {
  constructor(
    scope: core.Construct,
    id: string,
    props: FrontendStageDependencyProps,
  ) {
    super(scope, id, props);
    const buildConfig: BuildConfig = props.buildConfig;

    new AmplifyStack(this, id + 'AmplifyStack', {
      env: buildConfig.frontendAccount,
    });
  }
}
