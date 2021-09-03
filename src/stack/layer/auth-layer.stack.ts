import * as path from 'path';
import * as lambdaPython from '@aws-cdk/aws-lambda-python';
import * as ssm from '@aws-cdk/aws-ssm';
import * as core from '@aws-cdk/core';
import { BuildConfig, SERVICE_PREFIX } from '../../helper/helper';
interface AuthLayerStackDependencyProps extends core.StackProps {
  buildConfig: BuildConfig;
}
export class AuthLayerStack extends core.Stack {
  public readonly authLayer!: lambdaPython.PythonLayerVersion;
  constructor(
    scope: core.Construct,
    id: string,
    props: AuthLayerStackDependencyProps,
  ) {
    super(scope, id, props);
    const buildConfig: BuildConfig = props.buildConfig;
    //  The code that defines your stack goes here;
    this.authLayer = new lambdaPython.PythonLayerVersion(
      this,
      id + 'AuthLayer',
      {
        layerVersionName: SERVICE_PREFIX + 'AuthLayer',
        entry: path.join('./', 'code', 'lambda', 'layer', 'auth'),
        removalPolicy: buildConfig.removalPolicy,
      },
    );

    // Because of [lambda] deployment failure on updates to cross-stack layers https://github.com/aws/aws-cdk/issues/1972
    new ssm.StringParameter(this, id + 'VersionArn', {
      parameterName: `/arn/sso/${buildConfig.stage}/authLayer`,
      stringValue: this.authLayer.layerVersionArn,
    });
  }
}
