/**
 * LUKHAS AI ΛiD Authentication System - API Test Setup
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Setup file for API tests - includes SCIM compliance and endpoint testing utilities
 */

import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// SCIM test utilities
globalThis.scimTestUtils = {
  // Generate valid SCIM v2.0 user
  createValidSCIMUser(overrides: any = {}) {
    return {
      schemas: ['urn:ietf:params:scim:schemas:core:2.0:User'],
      id: overrides.id || 'test-user-id',
      userName: overrides.userName || 'test@example.com',
      name: {
        familyName: 'Test',
        givenName: 'User',
        formatted: 'Test User',
      },
      emails: [
        {
          value: overrides.email || 'test@example.com',
          type: 'work',
          primary: true,
        },
      ],
      active: overrides.active !== undefined ? overrides.active : true,
      meta: {
        resourceType: 'User',
        created: new Date().toISOString(),
        lastModified: new Date().toISOString(),
        version: 'W/"1"',
      },
      ...overrides,
    };
  },

  // Generate valid SCIM v2.0 group
  createValidSCIMGroup(overrides: any = {}) {
    return {
      schemas: ['urn:ietf:params:scim:schemas:core:2.0:Group'],
      id: overrides.id || 'test-group-id',
      displayName: overrides.displayName || 'Test Group',
      members: overrides.members || [
        {
          value: 'test-user-id',
          $ref: '/Users/test-user-id',
          display: 'Test User',
        },
      ],
      meta: {
        resourceType: 'Group',
        created: new Date().toISOString(),
        lastModified: new Date().toISOString(),
        version: 'W/"1"',
      },
      ...overrides,
    };
  },

  // Generate SCIM error response
  createSCIMError(status: number, scimType: string, detail: string) {
    return {
      schemas: ['urn:ietf:params:scim:api:messages:2.0:Error'],
      status: status.toString(),
      scimType,
      detail,
    };
  },

  // Generate SCIM list response
  createSCIMListResponse(resources: any[], totalResults?: number) {
    return {
      schemas: ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
      totalResults: totalResults || resources.length,
      startIndex: 1,
      itemsPerPage: resources.length,
      Resources: resources,
    };
  },

  // Generate SCIM patch operation
  createSCIMPatchOp(op: 'add' | 'remove' | 'replace', path: string, value?: any) {
    return {
      schemas: ['urn:ietf:params:scim:api:messages:2.0:PatchOp'],
      Operations: [
        {
          op,
          path,
          ...(value !== undefined && { value }),
        },
      ],
    };
  },

  // Generate SCIM bulk request
  createSCIMBulkRequest(operations: any[]) {
    return {
      schemas: ['urn:ietf:params:scim:api:messages:2.0:BulkRequest'],
      Operations: operations,
    };
  },

  // SCIM compliance validation
  validateSCIMResponse(response: any, resourceType: 'User' | 'Group' | 'ListResponse' | 'Error') {
    const requiredSchemas = {
      User: ['urn:ietf:params:scim:schemas:core:2.0:User'],
      Group: ['urn:ietf:params:scim:schemas:core:2.0:Group'],
      ListResponse: ['urn:ietf:params:scim:api:messages:2.0:ListResponse'],
      Error: ['urn:ietf:params:scim:api:messages:2.0:Error'],
    };

    const errors: string[] = [];

    // Check required schemas
    if (!response.schemas || !Array.isArray(response.schemas)) {
      errors.push('Missing or invalid schemas array');
    } else {
      const requiredSchema = requiredSchemas[resourceType];
      if (!requiredSchema.every(schema => response.schemas.includes(schema))) {
        errors.push(`Missing required schema for ${resourceType}`);
      }
    }

    // Resource-specific validations
    switch (resourceType) {
      case 'User':
        if (!response.id) errors.push('Missing user id');
        if (!response.userName) errors.push('Missing userName');
        break;
      case 'Group':
        if (!response.id) errors.push('Missing group id');
        if (!response.displayName) errors.push('Missing displayName');
        break;
      case 'ListResponse':
        if (typeof response.totalResults !== 'number') errors.push('Missing or invalid totalResults');
        if (!Array.isArray(response.Resources)) errors.push('Missing or invalid Resources array');
        break;
      case 'Error':
        if (!response.status) errors.push('Missing error status');
        if (!response.detail) errors.push('Missing error detail');
        break;
    }

    return { valid: errors.length === 0, errors };
  },
};

// API test utilities
globalThis.apiTestUtils = {
  // Create mock Express app for testing
  createMockApp() {
    const app = {
      routes: new Map(),
      middleware: [],
      
      use(path: string | Function, handler?: Function) {
        if (typeof path === 'function') {
          this.middleware.push(path);
        } else if (handler) {
          this.middleware.push({ path, handler });
        }
      },
      
      get(path: string, handler: Function) {
        this.routes.set(`GET:${path}`, handler);
      },
      
      post(path: string, handler: Function) {
        this.routes.set(`POST:${path}`, handler);
      },
      
      put(path: string, handler: Function) {
        this.routes.set(`PUT:${path}`, handler);
      },
      
      patch(path: string, handler: Function) {
        this.routes.set(`PATCH:${path}`, handler);
      },
      
      delete(path: string, handler: Function) {
        this.routes.set(`DELETE:${path}`, handler);
      },
    };
    
    return app;
  },

  // Create mock request object
  createMockRequest(overrides: any = {}) {
    return {
      method: 'GET',
      url: '/',
      path: '/',
      query: {},
      params: {},
      body: {},
      headers: {
        'content-type': 'application/json',
        'user-agent': 'Test Agent',
      },
      ip: '127.0.0.1',
      ...overrides,
    };
  },

  // Create mock response object
  createMockResponse() {
    const response = {
      statusCode: 200,
      headers: {},
      body: null,
      
      status(code: number) {
        this.statusCode = code;
        return this;
      },
      
      header(name: string, value: string) {
        this.headers[name.toLowerCase()] = value;
        return this;
      },
      
      json(data: any) {
        this.body = data;
        this.headers['content-type'] = 'application/json';
        return this;
      },
      
      send(data: any) {
        this.body = data;
        return this;
      },
      
      end() {
        return this;
      },
    };
    
    return response;
  },

  // Validate HTTP status codes
  validateStatusCode(actual: number, expected: number | number[]) {
    const expectedCodes = Array.isArray(expected) ? expected : [expected];
    return expectedCodes.includes(actual);
  },

  // Validate HTTP headers
  validateHeaders(headers: Record<string, string>, required: string[]) {
    const missing = required.filter(header => !headers[header.toLowerCase()]);
    return { valid: missing.length === 0, missing };
  },

  // Generate test authentication headers
  generateAuthHeaders(token?: string) {
    return {
      Authorization: `Bearer ${token || 'test-token'}`,
      'Content-Type': 'application/scim+json',
      Accept: 'application/scim+json',
    };
  },
};

// Performance testing utilities
globalThis.performanceTestUtils = {
  // Measure function execution time
  async measureExecutionTime<T>(fn: () => Promise<T>): Promise<{ result: T; duration: number }> {
    const start = process.hrtime.bigint();
    const result = await fn();
    const end = process.hrtime.bigint();
    const duration = Number(end - start) / 1000000; // Convert to milliseconds
    
    return { result, duration };
  },

  // Generate load test scenarios
  generateLoadScenarios(baseRPS: number) {
    return [
      { name: 'baseline', rps: baseRPS, duration: '1m' },
      { name: 'ramp-up', rps: baseRPS * 2, duration: '2m' },
      { name: 'peak', rps: baseRPS * 5, duration: '30s' },
      { name: 'sustained', rps: baseRPS * 3, duration: '5m' },
    ];
  },

  // Validate performance targets
  validatePerformanceTarget(actual: number, target: number, tolerance: number = 0.1) {
    const threshold = target * (1 + tolerance);
    return {
      passed: actual <= threshold,
      actual,
      target,
      threshold,
      difference: actual - target,
    };
  },
};

// Setup API test server
const apiServer = setupServer();

beforeAll(() => {
  apiServer.listen({ onUnhandledRequest: 'bypass' });
});

afterEach(() => {
  apiServer.resetHandlers();
});

afterAll(() => {
  apiServer.close();
});

export { apiServer };