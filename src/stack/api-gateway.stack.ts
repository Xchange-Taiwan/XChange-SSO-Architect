import * as apigatewayv2 from '@aws-cdk/aws-apigatewayv2';
import * as apigatewayv2Authorizers from '@aws-cdk/aws-apigatewayv2-authorizers';
import * as acm from '@aws-cdk/aws-certificatemanager';
import * as cognito from '@aws-cdk/aws-cognito';
import * as core from '@aws-cdk/core';
import { SERVICE_PREFIX } from '../helper/helper';

interface ApiGatewayStackDependencyProps extends core.StackProps {
  userPool: cognito.IUserPool;
  userPoolClient: cognito.IUserPoolClient;
  wildcardXchangeDomainCertificateArn: string;
}
export class ApiGatewayStack extends core.Stack {
  public readonly apiGateway!: apigatewayv2.HttpApi;
  constructor(
    scope: core.Construct,
    id: string,
    props: ApiGatewayStackDependencyProps,
  ) {
    // dependencies
    super(scope, id, props);
    // Authorize
    const userPool: cognito.IUserPool = props.userPool;
    const userPoolClient: cognito.IUserPoolClient = props.userPoolClient;
    const wildcardXchangeDomainCertificateArn: string =
      props.wildcardXchangeDomainCertificateArn;

    const wildcardXchangeDomainCertificate = acm.Certificate.fromCertificateArn(
      this,
      id + 'WildcardXchangeDomainCertificate',
      wildcardXchangeDomainCertificateArn,
    );

    const authorizer = new apigatewayv2Authorizers.HttpUserPoolAuthorizer({
      userPool,
      userPoolClient,
    });

    // Custom Domain HttpApi something wrong https://github.com/aws/aws-cdk/issues/13512
    const domainName = 'auth-api.xchange.com.tw';

    const customDomain = new apigatewayv2.DomainName(
      this,
      id + 'CustomDomain',
      {
        domainName,
        certificate: wildcardXchangeDomainCertificate,
      },
    );

    //  The code that defines your stack goes here
    this.apiGateway = new apigatewayv2.HttpApi(this, id + 'HttpAPI', {
      apiName: SERVICE_PREFIX + 'API',

      //Authorizer
      defaultAuthorizer: authorizer,
      defaultAuthorizationScopes: ['aws.cognito.signin.user.admin'],

      // HttpApi something wrong https://github.com/aws/aws-cdk/issues/13512
      // Custom Domain
      defaultDomainMapping: {
        domainName: customDomain,
        mappingKey: 'v1',
      },

      // CORS
      corsPreflight: {
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
        ],
        allowMethods: [
          apigatewayv2.CorsHttpMethod.OPTIONS,
          apigatewayv2.CorsHttpMethod.GET,
          apigatewayv2.CorsHttpMethod.POST,
          apigatewayv2.CorsHttpMethod.PUT,
          apigatewayv2.CorsHttpMethod.PATCH,
          apigatewayv2.CorsHttpMethod.DELETE,
        ],
        allowCredentials: false,
        allowOrigins: ['*'],
        maxAge: core.Duration.days(10),
      },
    });
  }
}
