/**
 * LUKHAS AI ΛiD Authentication System - OIDC SSO Integration Tests
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Integration tests for OpenID Connect Single Sign-On functionality
 */

import {
  OIDCProvider,
  OIDCProviderFactory,
  discoverOIDCEndpoints,
  type OIDCConfig,
  type OIDCTokens,
  type OIDCClaims,
  type OIDCState
} from '@/packages/auth/sso/oidc-provider';
import { server } from '@/tests/setup-integration';
import { http, HttpResponse } from 'msw';
import { SignJWT, generateKeyPair } from 'jose';

describe('OIDC SSO Integration', () => {
  let oidcProvider: OIDCProvider;
  let mockOIDCConfig: OIDCConfig;
  let testKeyPair: { publicKey: any; privateKey: any };

  beforeAll(async () => {
    // Generate test key pair for JWT signing
    testKeyPair = await generateKeyPair('RS256');
  });

  beforeEach(() => {
    mockOIDCConfig = {
      clientId: 'lukhas-ai-client',
      clientSecret: 'client-secret-123',
      issuer: 'https://oidc.example.com',
      authorizationEndpoint: 'https://oidc.example.com/auth',
      tokenEndpoint: 'https://oidc.example.com/token',
      userinfoEndpoint: 'https://oidc.example.com/userinfo',
      jwksUri: 'https://oidc.example.com/.well-known/jwks.json',
      redirectUri: 'https://auth.lukhas.ai/oidc/callback',
      scopes: ['openid', 'profile', 'email', 'groups'],
      responseType: 'code',
      responseMode: 'query',
      pkceEnabled: true,
      clockTolerance: 300,
      maxAge: 3600,
      acrValues: ['urn:mace:incommon:iap:silver'],
    };

    oidcProvider = OIDCProviderFactory.create(mockOIDCConfig);
  });

  describe('OIDC Discovery', () => {
    it('should discover OIDC endpoints from well-known configuration', async () => {
      const wellKnownConfig = {
        issuer: 'https://oidc.example.com',
        authorization_endpoint: 'https://oidc.example.com/auth',
        token_endpoint: 'https://oidc.example.com/token',
        userinfo_endpoint: 'https://oidc.example.com/userinfo',
        jwks_uri: 'https://oidc.example.com/.well-known/jwks.json',
        end_session_endpoint: 'https://oidc.example.com/logout',
        scopes_supported: ['openid', 'profile', 'email', 'groups'],
        response_types_supported: ['code', 'id_token', 'token id_token'],
        subject_types_supported: ['public'],
        id_token_signing_alg_values_supported: ['RS256'],
        claims_supported: ['sub', 'iss', 'aud', 'exp', 'iat', 'email', 'name', 'groups'],
      };

      server.use(
        http.get('https://oidc.example.com/.well-known/openid-configuration', () => {
          return HttpResponse.json(wellKnownConfig);
        })
      );

      const endpoints = await discoverOIDCEndpoints('https://oidc.example.com');

      expect(endpoints.authorization_endpoint).toBe('https://oidc.example.com/auth');
      expect(endpoints.token_endpoint).toBe('https://oidc.example.com/token');
      expect(endpoints.userinfo_endpoint).toBe('https://oidc.example.com/userinfo');
      expect(endpoints.jwks_uri).toBe('https://oidc.example.com/.well-known/jwks.json');
      expect(endpoints.end_session_endpoint).toBe('https://oidc.example.com/logout');
    });

    it('should handle discovery endpoint failures gracefully', async () => {
      server.use(
        http.get('https://invalid.example.com/.well-known/openid-configuration', () => {
          return new HttpResponse(null, { status: 404 });
        })
      );

      await expect(
        discoverOIDCEndpoints('https://invalid.example.com')
      ).rejects.toThrow(/discovery.*failed|not.*found/i);
    });

    it('should validate discovered configuration', async () => {
      const invalidConfig = {
        issuer: 'https://oidc.example.com',
        // Missing required endpoints
      };

      server.use(
        http.get('https://oidc.example.com/.well-known/openid-configuration', () => {
          return HttpResponse.json(invalidConfig);
        })
      );

      await expect(
        discoverOIDCEndpoints('https://oidc.example.com')
      ).rejects.toThrow(/missing.*endpoint|invalid.*configuration/i);
    });
  });

  describe('Authorization Request Generation', () => {
    it('should generate valid authorization URL with PKCE', async () => {
      const state = 'test-state-123';
      const nonce = 'test-nonce-456';

      const authRequest = await oidcProvider.generateAuthorizationUrl(state, nonce);

      expect(authRequest.url).toBeDefined();
      expect(authRequest.state).toBe(state);
      expect(authRequest.nonce).toBe(nonce);
      expect(authRequest.codeVerifier).toBeDefined();
      expect(authRequest.codeChallenge).toBeDefined();

      const url = new URL(authRequest.url);
      expect(url.hostname).toBe('oidc.example.com');
      expect(url.pathname).toBe('/auth');
      expect(url.searchParams.get('client_id')).toBe(mockOIDCConfig.clientId);
      expect(url.searchParams.get('response_type')).toBe('code');
      expect(url.searchParams.get('scope')).toBe('openid profile email groups');
      expect(url.searchParams.get('redirect_uri')).toBe(mockOIDCConfig.redirectUri);
      expect(url.searchParams.get('state')).toBe(state);
      expect(url.searchParams.get('nonce')).toBe(nonce);
      expect(url.searchParams.get('code_challenge')).toBe(authRequest.codeChallenge);
      expect(url.searchParams.get('code_challenge_method')).toBe('S256');
    });

    it('should include ACR values when configured', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');

      const url = new URL(authRequest.url);
      expect(url.searchParams.get('acr_values')).toBe('urn:mace:incommon:iap:silver');
    });

    it('should include max_age parameter when configured', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');

      const url = new URL(authRequest.url);
      expect(url.searchParams.get('max_age')).toBe('3600');
    });

    it('should generate unique code verifiers and challenges', async () => {
      const request1 = await oidcProvider.generateAuthorizationUrl('state1', 'nonce1');
      const request2 = await oidcProvider.generateAuthorizationUrl('state2', 'nonce2');

      expect(request1.codeVerifier).not.toBe(request2.codeVerifier);
      expect(request1.codeChallenge).not.toBe(request2.codeChallenge);
      expect(request1.codeVerifier).toMatch(/^[A-Za-z0-9._~-]+$/);
      expect(request1.codeChallenge).toMatch(/^[A-Za-z0-9_-]+$/);
    });

    it('should support custom additional parameters', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl(
        'state',
        'nonce',
        { 
          prompt: 'consent',
          ui_locales: 'en-US',
          custom_param: 'custom_value'
        }
      );

      const url = new URL(authRequest.url);
      expect(url.searchParams.get('prompt')).toBe('consent');
      expect(url.searchParams.get('ui_locales')).toBe('en-US');
      expect(url.searchParams.get('custom_param')).toBe('custom_value');
    });
  });

  describe('Token Exchange', () => {
    let mockIdToken: string;
    let mockAccessToken: string;

    beforeEach(async () => {
      // Generate mock ID token
      mockIdToken = await new SignJWT({
        sub: 'user123',
        iss: 'https://oidc.example.com',
        aud: 'lukhas-ai-client',
        exp: Math.floor(Date.now() / 1000) + 3600,
        iat: Math.floor(Date.now() / 1000),
        nonce: 'test-nonce-456',
        email: 'test@example.com',
        name: 'Test User',
        given_name: 'Test',
        family_name: 'User',
        groups: ['T4_Users', 'Analytics_Team']
      })
        .setProtectedHeader({ alg: 'RS256', kid: 'test-key-id' })
        .sign(testKeyPair.privateKey);

      mockAccessToken = 'access_token_123456789';

      // Mock token endpoint
      server.use(
        http.post('https://oidc.example.com/token', async ({ request }) => {
          const body = await request.text();
          const params = new URLSearchParams(body);

          if (params.get('grant_type') !== 'authorization_code') {
            return new HttpResponse(null, { status: 400 });
          }

          if (params.get('client_id') !== mockOIDCConfig.clientId) {
            return new HttpResponse(null, { status: 401 });
          }

          return HttpResponse.json({
            access_token: mockAccessToken,
            token_type: 'Bearer',
            expires_in: 3600,
            id_token: mockIdToken,
            refresh_token: 'refresh_token_123456789',
            scope: 'openid profile email groups'
          });
        })
      );

      // Mock JWKS endpoint
      const publicJwk = await oidcProvider.exportJWK(testKeyPair.publicKey);
      server.use(
        http.get('https://oidc.example.com/.well-known/jwks.json', () => {
          return HttpResponse.json({
            keys: [{ ...publicJwk, kid: 'test-key-id', use: 'sig', alg: 'RS256' }]
          });
        })
      );
    });

    it('should exchange authorization code for tokens', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');
      const authCode = 'auth_code_123456789';

      const tokenResult = await oidcProvider.exchangeCodeForTokens(
        authCode,
        authRequest.codeVerifier,
        'state'
      );

      expect(tokenResult.success).toBe(true);
      expect(tokenResult.tokens).toBeDefined();
      expect(tokenResult.tokens!.accessToken).toBe(mockAccessToken);
      expect(tokenResult.tokens!.idToken).toBe(mockIdToken);
      expect(tokenResult.tokens!.refreshToken).toBe('refresh_token_123456789');
      expect(tokenResult.tokens!.expiresIn).toBe(3600);
      expect(tokenResult.tokens!.scope).toBe('openid profile email groups');
    });

    it('should validate ID token signature', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');
      const authCode = 'auth_code_123456789';

      const tokenResult = await oidcProvider.exchangeCodeForTokens(
        authCode,
        authRequest.codeVerifier,
        'state'
      );

      expect(tokenResult.success).toBe(true);
      expect(tokenResult.idTokenValid).toBe(true);
      expect(tokenResult.claims).toBeDefined();
      expect(tokenResult.claims!.sub).toBe('user123');
      expect(tokenResult.claims!.email).toBe('test@example.com');
      expect(tokenResult.claims!.name).toBe('Test User');
    });

    it('should validate ID token claims', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');
      const authCode = 'auth_code_123456789';

      const tokenResult = await oidcProvider.exchangeCodeForTokens(
        authCode,
        authRequest.codeVerifier,
        'state'
      );

      expect(tokenResult.success).toBe(true);
      expect(tokenResult.claims).toBeDefined();

      const claims = tokenResult.claims!;
      expect(claims.iss).toBe('https://oidc.example.com');
      expect(claims.aud).toBe('lukhas-ai-client');
      expect(claims.nonce).toBe('test-nonce-456');
      expect(claims.exp).toBeGreaterThan(Date.now() / 1000);
      expect(claims.iat).toBeLessThanOrEqual(Date.now() / 1000);
    });

    it('should reject invalid authorization codes', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');

      server.use(
        http.post('https://oidc.example.com/token', () => {
          return HttpResponse.json(
            { error: 'invalid_grant', error_description: 'Invalid authorization code' },
            { status: 400 }
          );
        })
      );

      const tokenResult = await oidcProvider.exchangeCodeForTokens(
        'invalid_code',
        authRequest.codeVerifier,
        'state'
      );

      expect(tokenResult.success).toBe(false);
      expect(tokenResult.error).toMatch(/invalid.*grant|authorization.*code/i);
    });

    it('should validate PKCE code verifier', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');

      server.use(
        http.post('https://oidc.example.com/token', async ({ request }) => {
          const body = await request.text();
          const params = new URLSearchParams(body);

          if (params.get('code_verifier') !== authRequest.codeVerifier) {
            return HttpResponse.json(
              { error: 'invalid_grant', error_description: 'PKCE verification failed' },
              { status: 400 }
            );
          }

          return HttpResponse.json({
            access_token: mockAccessToken,
            token_type: 'Bearer',
            expires_in: 3600,
            id_token: mockIdToken,
          });
        })
      );

      // Test with correct code verifier
      const validResult = await oidcProvider.exchangeCodeForTokens(
        'auth_code_123',
        authRequest.codeVerifier,
        'state'
      );
      expect(validResult.success).toBe(true);

      // Test with wrong code verifier
      const invalidResult = await oidcProvider.exchangeCodeForTokens(
        'auth_code_123',
        'wrong_code_verifier',
        'state'
      );
      expect(invalidResult.success).toBe(false);
      expect(invalidResult.error).toMatch(/pkce|verification.*failed/i);
    });
  });

  describe('UserInfo Endpoint', () => {
    beforeEach(() => {
      server.use(
        http.get('https://oidc.example.com/userinfo', ({ request }) => {
          const authHeader = request.headers.get('Authorization');
          
          if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return new HttpResponse(null, { status: 401 });
          }

          const token = authHeader.substring(7);
          if (token !== 'access_token_123456789') {
            return new HttpResponse(null, { status: 401 });
          }

          return HttpResponse.json({
            sub: 'user123',
            email: 'test@example.com',
            email_verified: true,
            name: 'Test User',
            given_name: 'Test',
            family_name: 'User',
            picture: 'https://example.com/avatar.jpg',
            groups: ['T4_Users', 'Analytics_Team'],
            department: 'Engineering',
            title: 'Senior Developer'
          });
        })
      );
    });

    it('should fetch user information with access token', async () => {
      const userInfo = await oidcProvider.getUserInfo('access_token_123456789');

      expect(userInfo.success).toBe(true);
      expect(userInfo.claims).toBeDefined();
      expect(userInfo.claims!.sub).toBe('user123');
      expect(userInfo.claims!.email).toBe('test@example.com');
      expect(userInfo.claims!.name).toBe('Test User');
      expect(userInfo.claims!.groups).toEqual(['T4_Users', 'Analytics_Team']);
      expect(userInfo.claims!.department).toBe('Engineering');
    });

    it('should handle invalid access tokens', async () => {
      const userInfo = await oidcProvider.getUserInfo('invalid_token');

      expect(userInfo.success).toBe(false);
      expect(userInfo.error).toMatch(/unauthorized|invalid.*token/i);
    });

    it('should merge UserInfo claims with ID token claims', async () => {
      const idTokenClaims: OIDCClaims = {
        sub: 'user123',
        iss: 'https://oidc.example.com',
        aud: 'lukhas-ai-client',
        exp: Math.floor(Date.now() / 1000) + 3600,
        iat: Math.floor(Date.now() / 1000),
        email: 'test@example.com',
        name: 'Test User',
      };

      const userInfo = await oidcProvider.getUserInfo('access_token_123456789');
      const mergedClaims = oidcProvider.mergeClaims(idTokenClaims, userInfo.claims!);

      expect(mergedClaims.sub).toBe('user123');
      expect(mergedClaims.email).toBe('test@example.com');
      expect(mergedClaims.name).toBe('Test User');
      expect(mergedClaims.groups).toEqual(['T4_Users', 'Analytics_Team']);
      expect(mergedClaims.department).toBe('Engineering');
      expect(mergedClaims.iss).toBe('https://oidc.example.com');
    });
  });

  describe('Token Refresh', () => {
    beforeEach(() => {
      server.use(
        http.post('https://oidc.example.com/token', async ({ request }) => {
          const body = await request.text();
          const params = new URLSearchParams(body);

          if (params.get('grant_type') === 'refresh_token') {
            if (params.get('refresh_token') === 'valid_refresh_token') {
              return HttpResponse.json({
                access_token: 'new_access_token_123',
                token_type: 'Bearer',
                expires_in: 3600,
                refresh_token: 'new_refresh_token_123',
                scope: 'openid profile email groups'
              });
            } else {
              return HttpResponse.json(
                { error: 'invalid_grant', error_description: 'Invalid refresh token' },
                { status: 400 }
              );
            }
          }

          return new HttpResponse(null, { status: 400 });
        })
      );
    });

    it('should refresh access token using refresh token', async () => {
      const refreshResult = await oidcProvider.refreshToken('valid_refresh_token');

      expect(refreshResult.success).toBe(true);
      expect(refreshResult.tokens).toBeDefined();
      expect(refreshResult.tokens!.accessToken).toBe('new_access_token_123');
      expect(refreshResult.tokens!.refreshToken).toBe('new_refresh_token_123');
      expect(refreshResult.tokens!.expiresIn).toBe(3600);
    });

    it('should handle invalid refresh tokens', async () => {
      const refreshResult = await oidcProvider.refreshToken('invalid_refresh_token');

      expect(refreshResult.success).toBe(false);
      expect(refreshResult.error).toMatch(/invalid.*grant|refresh.*token/i);
    });

    it('should handle token rotation on refresh', async () => {
      const originalTokens: OIDCTokens = {
        accessToken: 'old_access_token',
        refreshToken: 'valid_refresh_token',
        idToken: 'old_id_token',
        tokenType: 'Bearer',
        expiresIn: 3600,
        scope: 'openid profile email'
      };

      const refreshResult = await oidcProvider.refreshToken(originalTokens.refreshToken);

      expect(refreshResult.success).toBe(true);
      expect(refreshResult.tokens!.accessToken).not.toBe(originalTokens.accessToken);
      expect(refreshResult.tokens!.refreshToken).not.toBe(originalTokens.refreshToken);
    });
  });

  describe('End Session (Logout)', () => {
    it('should generate logout URL with ID token hint', async () => {
      const idToken = 'id_token_123456789';
      const postLogoutRedirectUri = 'https://auth.lukhas.ai/logout-success';
      const state = 'logout-state-123';

      const logoutUrl = await oidcProvider.generateLogoutUrl(
        idToken,
        postLogoutRedirectUri,
        state
      );

      const url = new URL(logoutUrl);
      expect(url.hostname).toBe('oidc.example.com');
      expect(url.pathname).toBe('/logout');
      expect(url.searchParams.get('id_token_hint')).toBe(idToken);
      expect(url.searchParams.get('post_logout_redirect_uri')).toBe(postLogoutRedirectUri);
      expect(url.searchParams.get('state')).toBe(state);
    });

    it('should support logout without post-logout redirect', async () => {
      const idToken = 'id_token_123456789';

      const logoutUrl = await oidcProvider.generateLogoutUrl(idToken);

      const url = new URL(logoutUrl);
      expect(url.searchParams.get('id_token_hint')).toBe(idToken);
      expect(url.searchParams.has('post_logout_redirect_uri')).toBe(false);
      expect(url.searchParams.has('state')).toBe(false);
    });
  });

  describe('OIDC State Management', () => {
    it('should validate state parameter', async () => {
      const originalState = 'secure-state-123';
      const receivedState = 'secure-state-123';

      const isValid = await oidcProvider.validateState(originalState, receivedState);
      expect(isValid).toBe(true);

      const isInvalid = await oidcProvider.validateState(originalState, 'wrong-state');
      expect(isInvalid).toBe(false);
    });

    it('should detect state tampering', async () => {
      const originalState = 'secure-state-123';
      const tamperedState = 'tampered-state-456';

      const isValid = await oidcProvider.validateState(originalState, tamperedState);
      expect(isValid).toBe(false);
    });

    it('should handle missing state parameter', async () => {
      const originalState = 'secure-state-123';

      const isValid = await oidcProvider.validateState(originalState, undefined);
      expect(isValid).toBe(false);
    });

    it('should support state encryption for sensitive data', async () => {
      const sensitiveState: OIDCState = {
        originalUrl: '/dashboard',
        userId: 'user123',
        tier: 'T5',
        timestamp: Date.now()
      };

      const encryptedState = await oidcProvider.encryptState(sensitiveState);
      expect(encryptedState).toBeDefined();
      expect(encryptedState).not.toContain('user123');
      expect(encryptedState).not.toContain('dashboard');

      const decryptedState = await oidcProvider.decryptState(encryptedState);
      expect(decryptedState).toEqual(sensitiveState);
    });
  });

  describe('OIDC Security Features', () => {
    it('should validate ID token expiration', async () => {
      const expiredIdToken = await new SignJWT({
        sub: 'user123',
        iss: 'https://oidc.example.com',
        aud: 'lukhas-ai-client',
        exp: Math.floor(Date.now() / 1000) - 3600, // Expired 1 hour ago
        iat: Math.floor(Date.now() / 1000) - 7200, // Issued 2 hours ago
        nonce: 'test-nonce-456',
      })
        .setProtectedHeader({ alg: 'RS256' })
        .sign(testKeyPair.privateKey);

      const validation = await oidcProvider.validateIdToken(expiredIdToken, 'test-nonce-456');

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/expired|exp/i);
    });

    it('should validate ID token issuer', async () => {
      const wrongIssuerToken = await new SignJWT({
        sub: 'user123',
        iss: 'https://evil.com', // Wrong issuer
        aud: 'lukhas-ai-client',
        exp: Math.floor(Date.now() / 1000) + 3600,
        iat: Math.floor(Date.now() / 1000),
        nonce: 'test-nonce-456',
      })
        .setProtectedHeader({ alg: 'RS256' })
        .sign(testKeyPair.privateKey);

      const validation = await oidcProvider.validateIdToken(wrongIssuerToken, 'test-nonce-456');

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/issuer|iss/i);
    });

    it('should validate ID token audience', async () => {
      const wrongAudienceToken = await new SignJWT({
        sub: 'user123',
        iss: 'https://oidc.example.com',
        aud: 'wrong-client-id', // Wrong audience
        exp: Math.floor(Date.now() / 1000) + 3600,
        iat: Math.floor(Date.now() / 1000),
        nonce: 'test-nonce-456',
      })
        .setProtectedHeader({ alg: 'RS256' })
        .sign(testKeyPair.privateKey);

      const validation = await oidcProvider.validateIdToken(wrongAudienceToken, 'test-nonce-456');

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/audience|aud/i);
    });

    it('should validate nonce to prevent replay attacks', async () => {
      const tokenWithoutNonce = await new SignJWT({
        sub: 'user123',
        iss: 'https://oidc.example.com',
        aud: 'lukhas-ai-client',
        exp: Math.floor(Date.now() / 1000) + 3600,
        iat: Math.floor(Date.now() / 1000),
        // Missing nonce
      })
        .setProtectedHeader({ alg: 'RS256' })
        .sign(testKeyPair.privateKey);

      const validation = await oidcProvider.validateIdToken(tokenWithoutNonce, 'expected-nonce');

      expect(validation.valid).toBe(false);
      expect(validation.error).toMatch(/nonce/i);
    });

    it('should enforce HTTPS for production endpoints', () => {
      const httpsConfig = { ...mockOIDCConfig };
      expect(() => OIDCProviderFactory.create(httpsConfig)).not.toThrow();

      const httpConfig = {
        ...mockOIDCConfig,
        authorizationEndpoint: 'http://oidc.example.com/auth', // HTTP not allowed
      };

      expect(() => OIDCProviderFactory.create(httpConfig)).toThrow(/https.*required/i);
    });

    it('should implement rate limiting for token requests', async () => {
      let requestCount = 0;
      server.use(
        http.post('https://oidc.example.com/token', () => {
          requestCount++;
          if (requestCount > 10) {
            return new HttpResponse(null, { status: 429 }); // Too Many Requests
          }
          return HttpResponse.json({ access_token: 'token', token_type: 'Bearer' });
        })
      );

      // Make many token requests
      const promises = Array.from({ length: 15 }, () =>
        oidcProvider.exchangeCodeForTokens('code', 'verifier', 'state')
      );

      const results = await Promise.allSettled(promises);
      const rejectedCount = results.filter(r => r.status === 'rejected').length;

      expect(rejectedCount).toBeGreaterThan(0);
    });
  });

  describe('OIDC Performance and Reliability', () => {
    it('should cache JWKS keys efficiently', async () => {
      let requestCount = 0;
      const publicJwk = await oidcProvider.exportJWK(testKeyPair.publicKey);

      server.use(
        http.get('https://oidc.example.com/.well-known/jwks.json', () => {
          requestCount++;
          return HttpResponse.json({
            keys: [{ ...publicJwk, kid: 'test-key-id', use: 'sig', alg: 'RS256' }]
          });
        })
      );

      // Validate multiple tokens (should only fetch JWKS once)
      const token = await new SignJWT({
        sub: 'user123',
        iss: 'https://oidc.example.com',
        aud: 'lukhas-ai-client',
        exp: Math.floor(Date.now() / 1000) + 3600,
        iat: Math.floor(Date.now() / 1000),
        nonce: 'test-nonce',
      })
        .setProtectedHeader({ alg: 'RS256', kid: 'test-key-id' })
        .sign(testKeyPair.privateKey);

      await Promise.all([
        oidcProvider.validateIdToken(token, 'test-nonce'),
        oidcProvider.validateIdToken(token, 'test-nonce'),
        oidcProvider.validateIdToken(token, 'test-nonce'),
      ]);

      // Should only fetch JWKS once due to caching
      expect(requestCount).toBe(1);
    });

    it('should handle concurrent authentication flows', async () => {
      const promises = Array.from({ length: 10 }, (_, i) =>
        oidcProvider.generateAuthorizationUrl(`state-${i}`, `nonce-${i}`)
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(10);
      results.forEach((result, index) => {
        expect(result.state).toBe(`state-${index}`);
        expect(result.nonce).toBe(`nonce-${index}`);
        expect(result.url).toBeDefined();
      });

      // All code verifiers should be unique
      const codeVerifiers = results.map(r => r.codeVerifier);
      const uniqueVerifiers = new Set(codeVerifiers);
      expect(uniqueVerifiers.size).toBe(codeVerifiers.length);
    });

    it('should process token exchange within performance targets', async () => {
      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');

      const startTime = process.hrtime.bigint();
      await oidcProvider.exchangeCodeForTokens(
        'auth_code_123',
        authRequest.codeVerifier,
        'state'
      );
      const endTime = process.hrtime.bigint();

      const duration = Number(endTime - startTime) / 1000000; // Convert to ms

      // Should process token exchange in under 100ms
      expect(duration).toBeLessThan(100);
    });

    it('should handle IdP unavailability gracefully', async () => {
      server.use(
        http.post('https://oidc.example.com/token', () => {
          return new HttpResponse(null, { status: 503 }); // Service Unavailable
        })
      );

      const authRequest = await oidcProvider.generateAuthorizationUrl('state', 'nonce');
      const tokenResult = await oidcProvider.exchangeCodeForTokens(
        'auth_code_123',
        authRequest.codeVerifier,
        'state'
      );

      expect(tokenResult.success).toBe(false);
      expect(tokenResult.error).toMatch(/service.*unavailable|server.*error/i);
    });
  });
});