import * as core from '@aws-cdk/core';
import { AmplifyStack } from '../stack/amplify.stack';

export class SSOFrontend extends core.Stage {
  constructor(scope: core.Construct, id: string, props?: core.StackProps) {
    super(scope, id, props);

    new AmplifyStack(this, id + 'AmplifyStack');
  }
}
