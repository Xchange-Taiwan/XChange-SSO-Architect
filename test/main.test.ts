import '@aws-cdk/assert/jest';
import { App } from '@aws-cdk/core';
import { PipelineStack } from './../src/stack/pipeline.stack.ts';

test('Snapshot', () => {
  const app = new App();
  const stack = new PipelineStack(app, 'test');

  expect(stack).toHaveResource('AWS::CodePipeline::Pipeline');
  expect(
    app.synth().getStackArtifact(stack.artifactId).template,
  ).toMatchSnapshot();
});
