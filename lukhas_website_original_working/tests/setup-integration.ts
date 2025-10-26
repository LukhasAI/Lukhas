/**
 * LUKHAS AI ΛiD Authentication System - Integration Test Setup
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Setup file for integration tests - includes database and external service mocks
 */

import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// Mock database for integration tests
const mockDatabase = {
  users: new Map(),
  sessions: new Map(),
  passkeys: new Map(),
  refreshTokens: new Map(),
  securityEvents: new Map(),
  rateLimitEntries: new Map(),
};

// MSW server for mocking external services
export const server = setupServer(
  // Mock SAML IdP endpoints
  http.post('https://idp.example.com/saml/sso', () => {
    return HttpResponse.xml(`
      <samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
        <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
          <saml:Subject>
            <saml:NameID>test@example.com</saml:NameID>
          </saml:Subject>
          <saml:AttributeStatement>
            <saml:Attribute Name="email">
              <saml:AttributeValue>test@example.com</saml:AttributeValue>
            </saml:Attribute>
          </saml:AttributeStatement>
        </saml:Assertion>
      </samlp:Response>
    `);
  }),

  // Mock OIDC endpoints
  http.get('https://oidc.example.com/.well-known/openid-configuration', () => {
    return HttpResponse.json({
      issuer: 'https://oidc.example.com',
      authorization_endpoint: 'https://oidc.example.com/auth',
      token_endpoint: 'https://oidc.example.com/token',
      userinfo_endpoint: 'https://oidc.example.com/userinfo',
      jwks_uri: 'https://oidc.example.com/.well-known/jwks.json',
    });
  }),

  http.post('https://oidc.example.com/token', () => {
    return HttpResponse.json({
      access_token: 'mock-access-token',
      id_token: 'mock-id-token',
      refresh_token: 'mock-refresh-token',
      expires_in: 3600,
    });
  }),

  // Mock SCIM endpoints
  http.get('https://scim.example.com/v2/Users', () => {
    return HttpResponse.json({
      schemas: ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
      totalResults: 1,
      startIndex: 1,
      itemsPerPage: 1,
      Resources: [
        {
          schemas: ['urn:ietf:params:scim:schemas:core:2.0:User'],
          id: 'test-user-id',
          userName: 'test@example.com',
          emails: [{ value: 'test@example.com', primary: true }],
          active: true,
        },
      ],
    });
  }),

  // Mock email service
  http.post('https://api.sendgrid.com/v3/mail/send', () => {
    return HttpResponse.json({ message: 'success' });
  }),
);

// Setup and teardown
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  server.resetHandlers();
  // Clear mock database
  Object.values(mockDatabase).forEach(map => map.clear());
});

afterAll(() => {
  server.close();
});

// Export mock database for tests
export { mockDatabase };

// Global test utilities for integration tests
globalThis.mockDatabase = mockDatabase;

globalThis.createMockDatabaseInterface = () => ({
  // User operations
  async getUserById(id: string) {
    const user = mockDatabase.users.get(id);
    return { success: !!user, data: user };
  },
  
  async getUserByEmail(email: string) {
    const user = Array.from(mockDatabase.users.values()).find(u => u.email === email);
    return { success: !!user, data: user };
  },
  
  async createUser(data: any) {
    const user = { id: `user-${Date.now()}`, ...data, created_at: new Date(), updated_at: new Date() };
    mockDatabase.users.set(user.id, user);
    return { success: true, data: user };
  },
  
  async updateUser(id: string, data: any) {
    const user = mockDatabase.users.get(id);
    if (!user) return { success: false, error: 'User not found' };
    const updatedUser = { ...user, ...data, updated_at: new Date() };
    mockDatabase.users.set(id, updatedUser);
    return { success: true, data: updatedUser };
  },
  
  // Session operations
  async createSession(data: any) {
    const session = { id: `session-${Date.now()}`, ...data, created_at: new Date(), updated_at: new Date() };
    mockDatabase.sessions.set(session.id, session);
    return { success: true, data: session };
  },
  
  async getSessionByToken(token: string) {
    const session = Array.from(mockDatabase.sessions.values()).find(s => s.session_token === token);
    return { success: !!session, data: session };
  },
  
  // Security events
  async createSecurityEvent(data: any) {
    const event = { id: `event-${Date.now()}`, ...data, created_at: new Date() };
    mockDatabase.securityEvents.set(event.id, event);
    return { success: true, data: event };
  },
  
  // Health check
  async healthCheck() {
    return { success: true };
  },
  
  // Cleanup operations
  async cleanupExpiredSessions() { return { success: true }; },
  async cleanupExpiredRefreshTokens() { return { success: true }; },
  async cleanupExpiredSecurityEvents() { return { success: true }; },
  async cleanupExpiredRateLimitEntries() { return { success: true }; },
});