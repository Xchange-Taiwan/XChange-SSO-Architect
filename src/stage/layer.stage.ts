import * as core from '@aws-cdk/core';
import { BuildConfig } from '../helper/helper';
import { AuthLayerStack } from '../stack/layer/auth-layer.stack';

interface BackendLayerStageDependencyProps extends core.StackProps {
  buildConfig: BuildConfig;
}
export class BackendLayerStage extends core.Stage {
  constructor(
    scope: core.Construct,
    id: string,
    props: BackendLayerStageDependencyProps,
  ) {
    super(scope, id, props);
    const buildConfig: BuildConfig = props.buildConfig;

    new AuthLayerStack(this, id + 'AuthLayerStack', {
      env: buildConfig.backendAccount,
      buildConfig,
    });
  }
}
