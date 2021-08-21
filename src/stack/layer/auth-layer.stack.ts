import * as path from 'path';
import * as lambdaPython from '@aws-cdk/aws-lambda-python';
import * as ssm from '@aws-cdk/aws-ssm';
import * as core from '@aws-cdk/core';
import { SERVICE_PREFIX } from '../../helper/helper';
import { APP_REMOVALPOLICY } from '../../main';

export class AuthLayerStack extends core.Stack {
  public readonly generalLayer: lambdaPython.PythonLayerVersion;
  public readonly generalLayerStringParameter: ssm.StringParameter;
  constructor(scope: core.Construct, id: string, props?: core.StackProps) {
    super(scope, id, props);
    //  The code that defines your stack goes here;
    this.generalLayer = new lambdaPython.PythonLayerVersion(
      this,
      id + 'AuthLayer',
      {
        layerVersionName: SERVICE_PREFIX + 'AuthLayer',
        entry: path.join('./', 'code', 'lambda', 'layer', 'auth'),
        removalPolicy: APP_REMOVALPOLICY,
      },
    );

    // Because of [lambda] deployment failure on updates to cross-stack layers https://github.com/aws/aws-cdk/issues/1972
    // Record the versionArn into SSM
    this.generalLayerStringParameter = new ssm.StringParameter(
      this,
      id + 'GeneralLayerVersionArn',
      {
        parameterName: '/layer/xchange_sso/auth',
        stringValue: this.generalLayer.layerVersionArn,
      },
    );
  }
}
