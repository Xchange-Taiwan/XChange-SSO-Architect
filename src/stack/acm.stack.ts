import * as acm from '@aws-cdk/aws-certificatemanager';
import * as iam from '@aws-cdk/aws-iam';
import * as core from '@aws-cdk/core';
interface DomainAcmStackDependencyProps extends core.StackProps {
  organizations: {
    [key: string]: core.Environment;
  };
  wildcardXchangeDomainCertificateArn: string;
}
export class DomainAcmStack extends core.Stack {
  public readonly wildcardXchangeDomainCertificate!: acm.ICertificate;
  constructor(
    scope: core.Construct,
    id: string,
    props: DomainAcmStackDependencyProps,
  ) {
    super(scope, id, props);
    const organizations: {
      [key: string]: core.Environment;
    } = props.organizations;
    const wildcardXchangeDomainCertificateArn: string =
      props.wildcardXchangeDomainCertificateArn;

    this.wildcardXchangeDomainCertificate = acm.Certificate.fromCertificateArn(
      this,
      id + 'WildcardXchangeDomainCertificate',
      wildcardXchangeDomainCertificateArn,
    );

    const acmSsoBackendProdReadRole = new iam.Role(
      this,
      id + 'acmSsoBackendProdReadRole',
      {
        assumedBy: new iam.AccountPrincipal(
          organizations.ssoDevelopment.account,
        ),
        roleName: 'acm-sso-backend-prod-read-role',
      },
    );

    // cross account all AWSCertificateManager read
    // acmSsoBackendProdReadRole.addManagedPolicy(
    //   iam.ManagedPolicy.fromAwsManagedPolicyName(
    //     'AWSCertificateManagerReadOnly',
    //   ),
    // );

    // cross account specific resource
    acmSsoBackendProdReadRole.addToPolicy(
      new iam.PolicyStatement({
        sid: 'CertificateManagerReadOnly',
        effect: iam.Effect.ALLOW,
        actions: [
          'acm:DescribeCertificate',
          'acm:ListCertificates',
          'acm:GetCertificate',
          'acm:ListTagsForCertificate',
          'acm:GetAccountConfiguration',
        ],
        resources: [wildcardXchangeDomainCertificateArn],
      }),
    );
  }
}
