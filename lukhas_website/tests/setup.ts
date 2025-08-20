/**
 * LUKHAS AI ΛiD Authentication System - Test Setup
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Main Jest setup file for unit tests
 */

import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';
import { setupJestCanvasMock } from 'jest-canvas-mock';

// Mock crypto for Node.js environment
if (typeof globalThis.crypto === 'undefined') {
  const { webcrypto } = require('crypto');
  globalThis.crypto = webcrypto as Crypto;
}

// Mock TextEncoder/TextDecoder for Node.js environment
if (typeof globalThis.TextEncoder === 'undefined') {
  globalThis.TextEncoder = TextEncoder;
  globalThis.TextDecoder = TextDecoder as any;
}

// Setup canvas mock for components that use canvas
setupJestCanvasMock();

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: {},
      asPath: '/',
      push: jest.fn(() => Promise.resolve(true)),
      replace: jest.fn(() => Promise.resolve(true)),
      reload: jest.fn(() => Promise.resolve(true)),
      back: jest.fn(() => Promise.resolve(true)),
      prefetch: jest.fn(() => Promise.resolve()),
      beforePopState: jest.fn(() => Promise.resolve()),
      isFallback: false,
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
    };
  },
}));

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      refresh: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      prefetch: jest.fn(),
    };
  },
  useSearchParams() {
    return new URLSearchParams();
  },
  usePathname() {
    return '/';
  },
}));

// Mock environment variables
process.env.NODE_ENV = 'test';
process.env.AUTH_PASSWORD_ENABLED = 'false';
process.env.AUTH_MAGIC_LINK_TTL_SECONDS = '600';
process.env.AUTH_ACCESS_TTL_MINUTES = '15';
process.env.AUTH_REFRESH_TTL_DAYS = '30';
process.env.AUTH_REFRESH_ROTATE = 'true';
process.env.AUTH_REFRESH_REUSE_DETECT = 'true';
process.env.AUTH_REQUIRE_UV = 'true';
process.env.AUTH_RPID = 'localhost';
process.env.AUTH_ALLOWED_ORIGINS = 'https://localhost:3000';
process.env.JWT_PRIVATE_KEY = 'test-private-key';
process.env.JWT_PUBLIC_KEY = 'test-public-key';
process.env.JWT_KEY_ID = 'test-key-2025';
process.env.LUKHAS_ID_SECRET = 'test-secret-key-with-minimum-32-chars';

// Global test utilities
globalThis.createMockUser = (overrides = {}) => ({
  id: 'test-user-id',
  email: 'test@lukhas.ai',
  tier: 'T1',
  status: 'active',
  created_at: new Date(),
  updated_at: new Date(),
  last_login_at: new Date(),
  login_count: 1,
  email_verified: true,
  ...overrides,
});

globalThis.createMockSession = (overrides = {}) => ({
  id: 'test-session-id',
  user_id: 'test-user-id',
  session_token: 'test-session-token',
  session_token_hash: 'test-session-hash',
  ip_address: '127.0.0.1',
  user_agent: 'Test Agent',
  expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000),
  created_at: new Date(),
  updated_at: new Date(),
  status: 'active',
  scopes: ['matriz:read'],
  roles: ['viewer'],
  metadata: {},
  ...overrides,
});

// Configure test timeout
jest.setTimeout(30000);

// Global error handler
process.on('unhandledRejection', (error) => {
  console.error('Unhandled promise rejection in test:', error);
});

// Clean up after each test
afterEach(() => {
  jest.clearAllTimers();
  jest.useRealTimers();
});