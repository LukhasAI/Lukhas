/**
 * LUKHAS AI ΛiD Authentication System - SAML SSO Integration Tests
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Integration tests for SAML 2.0 Single Sign-On functionality
 */

import { 
  SAMLProvider, 
  SAMLProviderFactory,
  type SAMLConfig,
  type SAMLAssertion,
  type SAMLResponse 
} from '@/packages/auth/sso/saml-provider';
import { server } from '@/tests/setup-integration';
import { http, HttpResponse } from 'msw';
import crypto from 'crypto';

describe('SAML SSO Integration', () => {
  let samlProvider: SAMLProvider;
  let mockSAMLConfig: SAMLConfig;

  beforeEach(() => {
    mockSAMLConfig = {
      entityId: 'https://auth.lukhas.ai',
      ssoUrl: 'https://idp.example.com/saml/sso',
      sloUrl: 'https://idp.example.com/saml/slo',
      certificate: `-----BEGIN CERTIFICATE-----
MIICXjCCAcegAwIBAgIJAK8Z8Z8Z8Z8ZMA0GCSqGSIb3DQEBCwUAMEkxCzAJBgNV
BAYTAlVTMQswCQYDVQQIDAJDQTEQMA4GA1UEBwwHU2FuIEpvc2UxEDAOBgNVBAoM
B0x1a2hhcyBBSUMATAOBgNVBAMMBUx1a2hhcw==
-----END CERTIFICATE-----`,
      privateKey: `-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC0Z8Z8Z8Z8Z8Z
-----END PRIVATE KEY-----`,
      nameIdFormat: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
      attributeMapping: {
        email: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
        firstName: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
        lastName: 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname',
        groups: 'http://schemas.microsoft.com/ws/2008/06/identity/claims/groups',
      },
      signatureAlgorithm: 'http://www.w3.org/2001/04/xmldsig-more#rsa-sha256',
      digestAlgorithm: 'http://www.w3.org/2001/04/xmlenc#sha256',
      authnRequestSigned: true,
      wantAssertionsSigned: true,
      wantResponseSigned: true,
      allowUnencryptedAssertion: false,
      clockTolerance: 300,
    };

    samlProvider = SAMLProviderFactory.create(mockSAMLConfig);
  });

  describe('SAML AuthnRequest Generation', () => {
    it('should generate valid SAML AuthnRequest', async () => {
      const relayState = 'test-relay-state';
      const authnRequest = await samlProvider.generateAuthnRequest(relayState);

      expect(authnRequest.id).toBeDefined();
      expect(authnRequest.url).toContain(mockSAMLConfig.ssoUrl);
      expect(authnRequest.xml).toContain('AuthnRequest');
      expect(authnRequest.xml).toContain(mockSAMLConfig.entityId);
      expect(authnRequest.relayState).toBe(relayState);

      // Parse XML to validate structure
      const parser = new DOMParser();
      const doc = parser.parseFromString(authnRequest.xml, 'text/xml');
      
      const authnReq = doc.getElementsByTagName('samlp:AuthnRequest')[0];
      expect(authnReq).toBeDefined();
      expect(authnReq.getAttribute('ID')).toBe(authnRequest.id);
      expect(authnReq.getAttribute('Issuer')).toBe(mockSAMLConfig.entityId);
      expect(authnReq.getAttribute('Destination')).toBe(mockSAMLConfig.ssoUrl);
    });

    it('should include proper NameIDPolicy in AuthnRequest', async () => {
      const authnRequest = await samlProvider.generateAuthnRequest();

      expect(authnRequest.xml).toContain('NameIDPolicy');
      expect(authnRequest.xml).toContain(mockSAMLConfig.nameIdFormat);
      expect(authnRequest.xml).toContain('AllowCreate="true"');
    });

    it('should sign AuthnRequest when configured', async () => {
      const authnRequest = await samlProvider.generateAuthnRequest();

      // Should contain signature elements
      expect(authnRequest.xml).toContain('ds:Signature');
      expect(authnRequest.xml).toContain('ds:SignedInfo');
      expect(authnRequest.xml).toContain('ds:SignatureValue');
      expect(authnRequest.xml).toContain(mockSAMLConfig.signatureAlgorithm);
    });

    it('should generate unique request IDs', async () => {
      const request1 = await samlProvider.generateAuthnRequest();
      const request2 = await samlProvider.generateAuthnRequest();

      expect(request1.id).not.toBe(request2.id);
      expect(request1.id).toMatch(/^_[a-f0-9]{32}$/);
      expect(request2.id).toMatch(/^_[a-f0-9]{32}$/);
    });

    it('should handle ForceAuthn parameter', async () => {
      const authnRequest = await samlProvider.generateAuthnRequest('relay', true);

      expect(authnRequest.xml).toContain('ForceAuthn="true"');
    });

    it('should include proper timestamps', async () => {
      const before = new Date();
      const authnRequest = await samlProvider.generateAuthnRequest();
      const after = new Date();

      const parser = new DOMParser();
      const doc = parser.parseFromString(authnRequest.xml, 'text/xml');
      const issueInstant = doc.getElementsByTagName('samlp:AuthnRequest')[0]
        .getAttribute('IssueInstant');

      const timestamp = new Date(issueInstant!);
      expect(timestamp.getTime()).toBeGreaterThanOrEqual(before.getTime());
      expect(timestamp.getTime()).toBeLessThanOrEqual(after.getTime());
    });
  });

  describe('SAML Response Processing', () => {
    let mockSAMLResponseXML: string;

    beforeEach(() => {
      // Mock SAML Response XML
      mockSAMLResponseXML = `
        <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                        xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                        ID="_test_response_id"
                        InResponseTo="_test_request_id"
                        Version="2.0"
                        IssueInstant="2024-01-01T12:00:00Z"
                        Destination="https://auth.lukhas.ai/saml/acs">
          <saml:Issuer>https://idp.example.com</saml:Issuer>
          <samlp:Status>
            <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
          </samlp:Status>
          <saml:Assertion ID="_test_assertion_id"
                          Version="2.0"
                          IssueInstant="2024-01-01T12:00:00Z">
            <saml:Issuer>https://idp.example.com</saml:Issuer>
            <saml:Subject>
              <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">
                test@example.com
              </saml:NameID>
              <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
                <saml:SubjectConfirmationData NotOnOrAfter="2024-01-01T13:00:00Z"
                                              Recipient="https://auth.lukhas.ai/saml/acs"
                                              InResponseTo="_test_request_id"/>
              </saml:SubjectConfirmation>
            </saml:Subject>
            <saml:Conditions NotBefore="2024-01-01T11:55:00Z"
                             NotOnOrAfter="2024-01-01T13:00:00Z">
              <saml:AudienceRestriction>
                <saml:Audience>https://auth.lukhas.ai</saml:Audience>
              </saml:AudienceRestriction>
            </saml:Conditions>
            <saml:AuthnStatement AuthnInstant="2024-01-01T12:00:00Z">
              <saml:AuthnContext>
                <saml:AuthnContextClassRef>
                  urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
                </saml:AuthnContextClassRef>
              </saml:AuthnContext>
            </saml:AuthnStatement>
            <saml:AttributeStatement>
              <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress">
                <saml:AttributeValue>test@example.com</saml:AttributeValue>
              </saml:Attribute>
              <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname">
                <saml:AttributeValue>Test</saml:AttributeValue>
              </saml:Attribute>
              <saml:Attribute Name="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname">
                <saml:AttributeValue>User</saml:AttributeValue>
              </saml:Attribute>
              <saml:Attribute Name="http://schemas.microsoft.com/ws/2008/06/identity/claims/groups">
                <saml:AttributeValue>T4_Users</saml:AttributeValue>
                <saml:AttributeValue>Analytics_Team</saml:AttributeValue>
              </saml:Attribute>
            </saml:AttributeStatement>
          </saml:Assertion>
        </samlp:Response>
      `;
    });

    it('should process valid SAML Response successfully', async () => {
      const base64Response = Buffer.from(mockSAMLResponseXML).toString('base64');
      
      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(true);
      expect(result.user).toBeDefined();
      expect(result.user!.email).toBe('test@example.com');
      expect(result.user!.firstName).toBe('Test');
      expect(result.user!.lastName).toBe('User');
      expect(result.user!.groups).toEqual(['T4_Users', 'Analytics_Team']);
      expect(result.sessionIndex).toBeDefined();
    });

    it('should validate SAML Response signature', async () => {
      // Create signed response
      const signedResponseXML = await samlProvider.signXML(mockSAMLResponseXML);
      const base64Response = Buffer.from(signedResponseXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(true);
      expect(result.signatureValid).toBe(true);
    });

    it('should reject SAML Response with invalid signature', async () => {
      // Tamper with the response
      const tamperedXML = mockSAMLResponseXML.replace(
        'test@example.com',
        'hacker@evil.com'
      );
      const base64Response = Buffer.from(tamperedXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/signature|invalid/i);
    });

    it('should validate assertion conditions', async () => {
      // Test with expired assertion
      const expiredXML = mockSAMLResponseXML.replace(
        'NotOnOrAfter="2024-01-01T13:00:00Z"',
        'NotOnOrAfter="2020-01-01T13:00:00Z"'
      );
      const base64Response = Buffer.from(expiredXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/expired|condition/i);
    });

    it('should validate audience restriction', async () => {
      // Test with wrong audience
      const wrongAudienceXML = mockSAMLResponseXML.replace(
        'https://auth.lukhas.ai',
        'https://evil.com'
      );
      const base64Response = Buffer.from(wrongAudienceXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/audience|invalid/i);
    });

    it('should validate InResponseTo field', async () => {
      const base64Response = Buffer.from(mockSAMLResponseXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_wrong_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/request.*id|mismatch/i);
    });

    it('should handle SAML error responses', async () => {
      const errorResponseXML = `
        <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                        ID="_error_response_id"
                        Version="2.0"
                        IssueInstant="2024-01-01T12:00:00Z">
          <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
            https://idp.example.com
          </saml:Issuer>
          <samlp:Status>
            <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Requester">
              <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:AuthnFailed"/>
            </samlp:StatusCode>
            <samlp:StatusMessage>Authentication failed</samlp:StatusMessage>
          </samlp:Status>
        </samlp:Response>
      `;

      const base64Response = Buffer.from(errorResponseXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/authentication.*failed/i);
    });
  });

  describe('SAML Single Logout (SLO)', () => {
    it('should generate valid logout request', async () => {
      const nameId = 'test@example.com';
      const sessionIndex = 'test-session-index';
      const relayState = 'logout-relay-state';

      const logoutRequest = await samlProvider.generateLogoutRequest(
        nameId,
        sessionIndex,
        relayState
      );

      expect(logoutRequest.id).toBeDefined();
      expect(logoutRequest.url).toContain(mockSAMLConfig.sloUrl);
      expect(logoutRequest.xml).toContain('LogoutRequest');
      expect(logoutRequest.xml).toContain(nameId);
      expect(logoutRequest.xml).toContain(sessionIndex);
      expect(logoutRequest.relayState).toBe(relayState);
    });

    it('should process logout response correctly', async () => {
      const logoutResponseXML = `
        <samlp:LogoutResponse xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                              ID="_logout_response_id"
                              InResponseTo="_logout_request_id"
                              Version="2.0"
                              IssueInstant="2024-01-01T12:00:00Z">
          <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
            https://idp.example.com
          </saml:Issuer>
          <samlp:Status>
            <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
          </samlp:Status>
        </samlp:LogoutResponse>
      `;

      const base64Response = Buffer.from(logoutResponseXML).toString('base64');

      const result = await samlProvider.processLogoutResponse(
        base64Response,
        '_logout_request_id'
      );

      expect(result.success).toBe(true);
      expect(result.loggedOut).toBe(true);
    });

    it('should handle IdP-initiated logout request', async () => {
      const logoutRequestXML = `
        <samlp:LogoutRequest xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
                             xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
                             ID="_idp_logout_request_id"
                             Version="2.0"
                             IssueInstant="2024-01-01T12:00:00Z"
                             Destination="https://auth.lukhas.ai/saml/slo">
          <saml:Issuer>https://idp.example.com</saml:Issuer>
          <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">
            test@example.com
          </saml:NameID>
          <samlp:SessionIndex>test-session-index</samlp:SessionIndex>
        </samlp:LogoutRequest>
      `;

      const base64Request = Buffer.from(logoutRequestXML).toString('base64');

      const result = await samlProvider.processLogoutRequest(base64Request);

      expect(result.success).toBe(true);
      expect(result.nameId).toBe('test@example.com');
      expect(result.sessionIndex).toBe('test-session-index');
      expect(result.responseXML).toBeDefined();
    });
  });

  describe('SAML Metadata Generation', () => {
    it('should generate valid SP metadata', async () => {
      const metadata = await samlProvider.generateMetadata();

      expect(metadata).toContain('EntityDescriptor');
      expect(metadata).toContain('SPSSODescriptor');
      expect(metadata).toContain(mockSAMLConfig.entityId);
      expect(metadata).toContain('AssertionConsumerService');
      expect(metadata).toContain('SingleLogoutService');

      // Parse and validate XML structure
      const parser = new DOMParser();
      const doc = parser.parseFromString(metadata, 'text/xml');
      
      const entityDescriptor = doc.getElementsByTagName('md:EntityDescriptor')[0];
      expect(entityDescriptor.getAttribute('entityID')).toBe(mockSAMLConfig.entityId);

      const spssoDescriptor = doc.getElementsByTagName('md:SPSSODescriptor')[0];
      expect(spssoDescriptor.getAttribute('AuthnRequestsSigned')).toBe('true');
      expect(spssoDescriptor.getAttribute('WantAssertionsSigned')).toBe('true');
    });

    it('should include proper certificate in metadata', async () => {
      const metadata = await samlProvider.generateMetadata();

      expect(metadata).toContain('KeyDescriptor');
      expect(metadata).toContain('X509Certificate');
      expect(metadata).toContain('use="signing"');
      expect(metadata).toContain('use="encryption"');
    });

    it('should include supported NameID formats', async () => {
      const metadata = await samlProvider.generateMetadata();

      expect(metadata).toContain('NameIDFormat');
      expect(metadata).toContain(mockSAMLConfig.nameIdFormat);
    });
  });

  describe('SAML Error Handling', () => {
    it('should handle malformed SAML responses gracefully', async () => {
      const malformedXML = '<invalid>xml</structure>';
      const base64Response = Buffer.from(malformedXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/malformed|invalid.*xml/i);
    });

    it('should handle missing required attributes', async () => {
      const incompleteXML = mockSAMLResponseXML.replace(
        /<saml:AttributeStatement>[\s\S]*?<\/saml:AttributeStatement>/,
        '<saml:AttributeStatement></saml:AttributeStatement>'
      );
      const base64Response = Buffer.from(incompleteXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/missing.*attribute|email/i);
    });

    it('should handle network timeouts during metadata fetching', async () => {
      // Mock network timeout
      server.use(
        http.get('https://idp.example.com/metadata', () => {
          return new Promise(() => {}); // Never resolves (timeout)
        })
      );

      const configWithMetadataUrl = {
        ...mockSAMLConfig,
        metadataUrl: 'https://idp.example.com/metadata',
      };

      await expect(
        SAMLProviderFactory.createFromMetadata(configWithMetadataUrl)
      ).rejects.toThrow(/timeout|network/i);
    });

    it('should validate certificate expiration', async () => {
      // Mock expired certificate
      const expiredCertConfig = {
        ...mockSAMLConfig,
        certificate: `-----BEGIN CERTIFICATE-----
MIICXjCCAcegAwIBAgIJAK8Z8Z8Z8Z8ZMA0GCSqGSIb3DQEBCwUAMEkxCzAJBgNV
BAYTAlVTMQswCQYDVQQIDAJDQTEQMA0GA1UEBwwHU2FuIEpvc2UxEDAOBgNVBAoM
B0x1a2hhcyBBSUMATAOBgNVBAMMBUx1a2hhcw==
-----END CERTIFICATE-----`,
      };

      const expiredProvider = SAMLProviderFactory.create(expiredCertConfig);
      const result = await expiredProvider.validateConfiguration();

      expect(result.valid).toBe(false);
      expect(result.errors).toContain(
        expect.stringMatching(/certificate.*expired/i)
      );
    });
  });

  describe('SAML Security Features', () => {
    it('should enforce clock tolerance for time validation', async () => {
      // Create response with time slightly in the future
      const futureTime = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes future
      const futureXML = mockSAMLResponseXML.replace(
        'IssueInstant="2024-01-01T12:00:00Z"',
        `IssueInstant="${futureTime.toISOString()}"`
      );

      const base64Response = Buffer.from(futureXML).toString('base64');

      // Should be rejected (exceeds clock tolerance)
      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/time|clock|future/i);
    });

    it('should prevent XML External Entity (XXE) attacks', async () => {
      const xxeXML = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE samlp:Response [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    &xxe;
  </saml:Issuer>
</samlp:Response>`;

      const base64Response = Buffer.from(xxeXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/security|external.*entity|xxe/i);
    });

    it('should validate response destination URL', async () => {
      const wrongDestinationXML = mockSAMLResponseXML.replace(
        'Destination="https://auth.lukhas.ai/saml/acs"',
        'Destination="https://evil.com/saml/acs"'
      );

      const base64Response = Buffer.from(wrongDestinationXML).toString('base64');

      const result = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );

      expect(result.success).toBe(false);
      expect(result.error).toMatch(/destination|url/i);
    });

    it('should prevent SAML response replay attacks', async () => {
      const base64Response = Buffer.from(mockSAMLResponseXML).toString('base64');

      // First processing should succeed
      const result1 = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );
      expect(result1.success).toBe(true);

      // Second processing should fail (replay attack)
      const result2 = await samlProvider.processResponse(
        base64Response,
        '_test_request_id'
      );
      expect(result2.success).toBe(false);
      expect(result2.error).toMatch(/replay|already.*processed/i);
    });
  });

  describe('SAML Performance and Reliability', () => {
    it('should process SAML responses within performance targets', async () => {
      const base64Response = Buffer.from(mockSAMLResponseXML).toString('base64');

      const startTime = process.hrtime.bigint();
      await samlProvider.processResponse(base64Response, '_test_request_id');
      const endTime = process.hrtime.bigint();

      const duration = Number(endTime - startTime) / 1000000; // Convert to ms

      // Should process SAML response in under 50ms
      expect(duration).toBeLessThan(50);
    });

    it('should handle concurrent SAML operations', async () => {
      const promises = Array.from({ length: 10 }, (_, i) =>
        samlProvider.generateAuthnRequest(`relay-${i}`)
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(10);
      results.forEach((result, index) => {
        expect(result.relayState).toBe(`relay-${index}`);
        expect(result.id).toBeDefined();
      });

      // All IDs should be unique
      const ids = results.map(r => r.id);
      const uniqueIds = new Set(ids);
      expect(uniqueIds.size).toBe(ids.length);
    });

    it('should cache IdP metadata efficiently', async () => {
      // Mock metadata endpoint
      let requestCount = 0;
      server.use(
        http.get('https://idp.example.com/metadata', () => {
          requestCount++;
          return HttpResponse.xml(`
            <md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                                 entityID="https://idp.example.com">
              <md:IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
                <md:SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                                        Location="https://idp.example.com/saml/sso"/>
              </md:IDPSSODescriptor>
            </md:EntityDescriptor>
          `);
        })
      );

      const configWithMetadata = {
        ...mockSAMLConfig,
        metadataUrl: 'https://idp.example.com/metadata',
        metadataCacheTTL: 3600, // 1 hour
      };

      // Create multiple providers with same metadata URL
      await Promise.all([
        SAMLProviderFactory.createFromMetadata(configWithMetadata),
        SAMLProviderFactory.createFromMetadata(configWithMetadata),
        SAMLProviderFactory.createFromMetadata(configWithMetadata),
      ]);

      // Should only fetch metadata once due to caching
      expect(requestCount).toBe(1);
    });
  });
});