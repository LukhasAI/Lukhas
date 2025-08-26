/**
 * SAML 2.0 Provider Implementation
 * Enterprise-grade SAML integration for LUKHAS AI ΛiD System
 *
 * Supports:
 * - SP-initiated and IdP-initiated flows
 * - Okta, Azure AD, Google Workspace
 * - Assertion validation and attribute mapping
 * - Security: replay attack prevention, signature validation
 */

import { createHash, randomBytes } from 'crypto';
import { XMLParser, XMLBuilder } from 'fast-xml-parser';
import { SignedXml } from 'xml-crypto';
import { AuditLogger } from '../audit-logger';
import { SecurityFeatures } from '../security-features';

export interface SAMLConfig {
  entityId: string;
  ssoUrl: string;
  sloUrl?: string;
  certificate: string;
  privateKey?: string;
  assertionConsumerServiceUrl: string;
  signRequests?: boolean;
  encryptAssertions?: boolean;
  nameIdFormat?: string;
  attributeMapping?: Record<string, string>;
  clockTolerance?: number; // seconds
}

export interface SAMLAssertion {
  nameId: string;
  sessionIndex?: string;
  attributes: Record<string, string | string[]>;
  issuer: string;
  audience: string;
  notBefore: Date;
  notOnOrAfter: Date;
  authnInstant: Date;
}

export interface SAMLResponse {
  assertion: SAMLAssertion;
  relayState?: string;
  destination: string;
  issuer: string;
}

export class SAMLProvider {
  private config: SAMLConfig;
  private auditLogger: AuditLogger;
  private security: SecurityFeatures;
  private xmlParser: XMLParser;
  private xmlBuilder: XMLBuilder;
  private pendingRequests = new Map<string, { timestamp: number; relayState?: string }>();

  constructor(config: SAMLConfig, auditLogger: AuditLogger) {
    this.config = config;
    this.auditLogger = auditLogger;
    this.security = new SecurityFeatures();

    this.xmlParser = new XMLParser({
      ignoreAttributes: false,
      attributeNamePrefix: '@_',
      parseAttributeValue: false,
      trimValues: true
    });

    this.xmlBuilder = new XMLBuilder({
      ignoreAttributes: false,
      attributeNamePrefix: '@_',
      format: true
    });

    // Cleanup expired requests every 10 minutes
    setInterval(() => this.cleanupExpiredRequests(), 10 * 60 * 1000);
  }

  /**
   * Generate SP-initiated SAML AuthnRequest
   */
  async generateAuthnRequest(relayState?: string): Promise<{ url: string; requestId: string }> {
    const requestId = this.generateRequestId();
    const timestamp = new Date().toISOString();

    // Store request for validation
    this.pendingRequests.set(requestId, {
      timestamp: Date.now(),
      relayState
    });

    const authnRequest = {
      'samlp:AuthnRequest': {
        '@_xmlns:samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
        '@_xmlns:saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
        '@_ID': requestId,
        '@_Version': '2.0',
        '@_IssueInstant': timestamp,
        '@_Destination': this.config.ssoUrl,
        '@_AssertionConsumerServiceURL': this.config.assertionConsumerServiceUrl,
        '@_ProtocolBinding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
        'saml:Issuer': {
          '@_xmlns:saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
          '#text': this.config.entityId
        },
        'samlp:NameIDPolicy': {
          '@_Format': this.config.nameIdFormat || 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
          '@_AllowCreate': 'true'
        }
      }
    };

    let xmlRequest = this.xmlBuilder.build(authnRequest);

    // Sign request if required
    if (this.config.signRequests && this.config.privateKey) {
      xmlRequest = this.signXml(xmlRequest, this.config.privateKey);
    }

    // Encode and build URL
    const encodedRequest = Buffer.from(xmlRequest).toString('base64');
    const params = new URLSearchParams({
      SAMLRequest: encodedRequest
    });

    if (relayState) {
      params.append('RelayState', relayState);
    }

    const url = `${this.config.ssoUrl}?${params.toString()}`;

    await this.auditLogger.logSecurityEvent('sso_authn_request_generated', {
      requestId,
      destination: this.config.ssoUrl,
      hasRelayState: !!relayState
    });

    return { url, requestId };
  }

  /**
   * Process SAML Response from IdP
   */
  async processResponse(samlResponse: string, relayState?: string): Promise<SAMLResponse> {
    try {
      // Decode base64 response
      const xmlResponse = Buffer.from(samlResponse, 'base64').toString('utf-8');

      // Validate XML signature
      if (!this.validateSignature(xmlResponse, this.config.certificate)) {
        throw new Error('Invalid SAML response signature');
      }

      // Parse XML
      const parsed = this.xmlParser.parse(xmlResponse);
      const response = parsed['samlp:Response'];

      if (!response) {
        throw new Error('Invalid SAML response format');
      }

      // Validate response
      await this.validateResponse(response);

      // Extract assertion
      const assertion = this.extractAssertion(response);

      // Validate assertion
      await this.validateAssertion(assertion);

      // Map attributes
      const mappedAssertion = this.mapAttributes(assertion);

      const result: SAMLResponse = {
        assertion: mappedAssertion,
        relayState,
        destination: response['@_Destination'],
        issuer: response['saml:Issuer']['#text']
      };

      await this.auditLogger.logSecurityEvent('sso_response_processed', {
        nameId: mappedAssertion.nameId,
        issuer: result.issuer,
        sessionIndex: mappedAssertion.sessionIndex,
        attributeCount: Object.keys(mappedAssertion.attributes).length
      });

      return result;

    } catch (error) {
      await this.auditLogger.logSecurityEvent('sso_response_failed', {
        error: error instanceof Error ? error.message : 'Unknown error',
        hasRelayState: !!relayState
      });
      throw error;
    }
  }

  /**
   * Generate Single Logout Request
   */
  async generateLogoutRequest(nameId: string, sessionIndex?: string): Promise<string> {
    if (!this.config.sloUrl) {
      throw new Error('SLO URL not configured');
    }

    const requestId = this.generateRequestId();
    const timestamp = new Date().toISOString();

    const logoutRequest = {
      'samlp:LogoutRequest': {
        '@_xmlns:samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
        '@_xmlns:saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
        '@_ID': requestId,
        '@_Version': '2.0',
        '@_IssueInstant': timestamp,
        '@_Destination': this.config.sloUrl,
        'saml:Issuer': {
          '#text': this.config.entityId
        },
        'saml:NameID': {
          '@_Format': this.config.nameIdFormat || 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
          '#text': nameId
        }
      }
    };

    if (sessionIndex) {
      (logoutRequest['samlp:LogoutRequest'] as any)['samlp:SessionIndex'] = {
        '#text': sessionIndex
      };
    }

    let xmlRequest = this.xmlBuilder.build(logoutRequest);

    if (this.config.signRequests && this.config.privateKey) {
      xmlRequest = this.signXml(xmlRequest, this.config.privateKey);
    }

    await this.auditLogger.logSecurityEvent('sso_logout_request_generated', {
      requestId,
      nameId,
      sessionIndex,
      destination: this.config.sloUrl
    });

    return Buffer.from(xmlRequest).toString('base64');
  }

  /**
   * Generate Service Provider Metadata
   */
  generateMetadata(): string {
    const metadata = {
      'md:EntityDescriptor': {
        '@_xmlns:md': 'urn:oasis:names:tc:SAML:2.0:metadata',
        '@_entityID': this.config.entityId,
        'md:SPSSODescriptor': {
          '@_AuthnRequestsSigned': this.config.signRequests ? 'true' : 'false',
          '@_protocolSupportEnumeration': 'urn:oasis:names:tc:SAML:2.0:protocol',
          'md:NameIDFormat': {
            '#text': this.config.nameIdFormat || 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent'
          },
          'md:AssertionConsumerService': {
            '@_Binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST',
            '@_Location': this.config.assertionConsumerServiceUrl,
            '@_index': '0',
            '@_isDefault': 'true'
          }
        }
      }
    };

    if (this.config.sloUrl) {
      (metadata['md:EntityDescriptor']['md:SPSSODescriptor'] as any)['md:SingleLogoutService'] = {
        '@_Binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect',
        '@_Location': this.config.sloUrl
      };
    }

    return this.xmlBuilder.build(metadata);
  }

  private generateRequestId(): string {
    return '_' + randomBytes(20).toString('hex');
  }

  private validateSignature(xml: string, certificate: string): boolean {
    try {
      const sig = new SignedXml();
      sig.keyInfoProvider = {
        getKeyInfo: () => `<X509Data><X509Certificate>${certificate}</X509Certificate></X509Data>`,
        getKey: () => `-----BEGIN CERTIFICATE-----\n${certificate}\n-----END CERTIFICATE-----`
      };

      return sig.checkSignature(xml);
    } catch (error) {
      return false;
    }
  }

  private signXml(xml: string, privateKey: string): string {
    const sig = new SignedXml();
    sig.signingKey = privateKey;
    sig.addReference("//*[local-name(.)='Response']");
    sig.computeSignature(xml);
    return sig.getSignedXml();
  }

  private async validateResponse(response: any): Promise<void> {
    // Check status
    const status = response['samlp:Status']?.['samlp:StatusCode']?.['@_Value'];
    if (status !== 'urn:oasis:names:tc:SAML:2.0:status:Success') {
      throw new Error(`SAML response failed with status: ${status}`);
    }

    // Check destination
    if (response['@_Destination'] !== this.config.assertionConsumerServiceUrl) {
      throw new Error('Invalid destination in SAML response');
    }

    // Check InResponseTo if present
    const inResponseTo = response['@_InResponseTo'];
    if (inResponseTo) {
      const pendingRequest = this.pendingRequests.get(inResponseTo);
      if (!pendingRequest) {
        throw new Error('Invalid InResponseTo - request not found or expired');
      }
      this.pendingRequests.delete(inResponseTo);
    }
  }

  private extractAssertion(response: any): any {
    const assertion = response['saml:Assertion'];
    if (!assertion) {
      throw new Error('No assertion found in SAML response');
    }
    return assertion;
  }

  private async validateAssertion(assertion: any): Promise<void> {
    const conditions = assertion['saml:Conditions'];
    if (!conditions) {
      throw new Error('No conditions found in assertion');
    }

    // Validate time constraints
    const notBefore = new Date(conditions['@_NotBefore']);
    const notOnOrAfter = new Date(conditions['@_NotOnOrAfter']);
    const now = new Date();
    const tolerance = (this.config.clockTolerance || 60) * 1000; // Convert to milliseconds

    if (now.getTime() < notBefore.getTime() - tolerance) {
      throw new Error('Assertion not yet valid');
    }

    if (now.getTime() >= notOnOrAfter.getTime() + tolerance) {
      throw new Error('Assertion has expired');
    }

    // Validate audience
    const audienceRestriction = conditions['saml:AudienceRestriction'];
    if (audienceRestriction) {
      const audiences = Array.isArray(audienceRestriction['saml:Audience'])
        ? audienceRestriction['saml:Audience']
        : [audienceRestriction['saml:Audience']];

      const validAudience = audiences.some((aud: any) =>
        (aud['#text'] || aud) === this.config.entityId
      );

      if (!validAudience) {
        throw new Error('Invalid audience in assertion');
      }
    }

    // Validate subject confirmation
    const subject = assertion['saml:Subject'];
    if (subject?.['saml:SubjectConfirmation']?.['saml:SubjectConfirmationData']) {
      const confirmationData = subject['saml:SubjectConfirmation']['saml:SubjectConfirmationData'];

      if (confirmationData['@_Recipient'] !== this.config.assertionConsumerServiceUrl) {
        throw new Error('Invalid recipient in subject confirmation');
      }

      const notOnOrAfter = new Date(confirmationData['@_NotOnOrAfter']);
      if (now.getTime() >= notOnOrAfter.getTime() + tolerance) {
        throw new Error('Subject confirmation has expired');
      }
    }
  }

  private mapAttributes(assertion: any): SAMLAssertion {
    const subject = assertion['saml:Subject'];
    const nameId = subject?.['saml:NameID']?.['#text'] || subject?.['saml:NameID'];

    if (!nameId) {
      throw new Error('No NameID found in assertion');
    }

    const conditions = assertion['saml:Conditions'];
    const notBefore = new Date(conditions['@_NotBefore']);
    const notOnOrAfter = new Date(conditions['@_NotOnOrAfter']);

    const authnStatement = assertion['saml:AuthnStatement'];
    const authnInstant = new Date(authnStatement?.['@_AuthnInstant'] || Date.now());
    const sessionIndex = authnStatement?.['@_SessionIndex'];

    // Extract attributes
    const attributes: Record<string, string | string[]> = {};
    const attributeStatement = assertion['saml:AttributeStatement'];

    if (attributeStatement?.['saml:Attribute']) {
      const attrs = Array.isArray(attributeStatement['saml:Attribute'])
        ? attributeStatement['saml:Attribute']
        : [attributeStatement['saml:Attribute']];

      for (const attr of attrs) {
        const name = attr['@_Name'];
        const values = Array.isArray(attr['saml:AttributeValue'])
          ? attr['saml:AttributeValue'].map((v: any) => v['#text'] || v)
          : [attr['saml:AttributeValue']?.['#text'] || attr['saml:AttributeValue']];

        // Apply attribute mapping if configured
        const mappedName = this.config.attributeMapping?.[name] || name;
        attributes[mappedName] = values.length === 1 ? values[0] : values;
      }
    }

    return {
      nameId,
      sessionIndex,
      attributes,
      issuer: assertion['saml:Issuer']?.['#text'] || assertion['saml:Issuer'],
      audience: this.config.entityId,
      notBefore,
      notOnOrAfter,
      authnInstant
    };
  }

  private cleanupExpiredRequests(): void {
    const now = Date.now();
    const maxAge = 10 * 60 * 1000; // 10 minutes

    for (const [requestId, request] of this.pendingRequests.entries()) {
      if (now - request.timestamp > maxAge) {
        this.pendingRequests.delete(requestId);
      }
    }
  }
}

/**
 * Factory for creating SAML providers for different IdPs
 */
export class SAMLProviderFactory {
  static createOktaProvider(config: Omit<SAMLConfig, 'nameIdFormat'>, auditLogger: AuditLogger): SAMLProvider {
    return new SAMLProvider({
      ...config,
      nameIdFormat: 'urn:oasis:names:tc:SAML:2.0:nameid-format:persistent',
      attributeMapping: {
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress': 'email',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname': 'firstName',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname': 'lastName',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name': 'displayName',
        ...config.attributeMapping
      }
    }, auditLogger);
  }

  static createAzureADProvider(config: Omit<SAMLConfig, 'nameIdFormat'>, auditLogger: AuditLogger): SAMLProvider {
    return new SAMLProvider({
      ...config,
      nameIdFormat: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
      attributeMapping: {
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress': 'email',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname': 'firstName',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname': 'lastName',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name': 'displayName',
        'http://schemas.microsoft.com/identity/claims/tenantid': 'tenantId',
        'http://schemas.microsoft.com/identity/claims/objectidentifier': 'objectId',
        ...config.attributeMapping
      }
    }, auditLogger);
  }

  static createGoogleWorkspaceProvider(config: Omit<SAMLConfig, 'nameIdFormat'>, auditLogger: AuditLogger): SAMLProvider {
    return new SAMLProvider({
      ...config,
      nameIdFormat: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
      attributeMapping: {
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress': 'email',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname': 'firstName',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname': 'lastName',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name': 'displayName',
        'https://schemas.google.com/identity/claims/objectid': 'googleId',
        'https://schemas.google.com/identity/claims/domain': 'domain',
        ...config.attributeMapping
      }
    }, auditLogger);
  }
}
