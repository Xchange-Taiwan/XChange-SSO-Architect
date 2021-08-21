import * as acm from '@aws-cdk/aws-certificatemanager';
import * as core from '@aws-cdk/core';
import { DomainAcmStack } from '../stack/acm.stack';
interface DomainAcmStageDependencyProps extends core.StackProps {
  organizations: {
    [key: string]: core.Environment;
  };
  wildcardXchangeDomainCertificateArn: string;
}
export class DomainAcmStage extends core.Stage {
  public readonly wildcardXchangeDomainCertificate!: acm.ICertificate;
  constructor(
    scope: core.Construct,
    id: string,
    props: DomainAcmStageDependencyProps,
  ) {
    super(scope, id, props);
    const organizations: {
      [key: string]: core.Environment;
    } = props.organizations;
    const wildcardXchangeDomainCertificateArn: string =
      props.wildcardXchangeDomainCertificateArn;

    const domainAcmStack = new DomainAcmStack(this, id + 'DomainAcmStack', {
      organizations,
      wildcardXchangeDomainCertificateArn,
    });

    this.wildcardXchangeDomainCertificate =
      domainAcmStack.wildcardXchangeDomainCertificate;
  }
}
