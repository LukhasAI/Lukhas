const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  // Add more setup options before each test is run
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],

  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', { tsconfig: '<rootDir>/tsconfig.json', isolatedModules: true }],
  },

  // Test environment
  testEnvironment: 'jest-environment-jsdom',

  // Ignore patterns to resolve naming conflicts
  modulePathIgnorePatterns: [
    '<rootDir>/past-prototypes/',
    '<rootDir>/node_modules/',
  ],

  // Module name mapping for absolute imports
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^@/packages/(.*)$': '<rootDir>/packages/$1',
    '^@/tests/(.*)$': '<rootDir>/tests/$1',
  },

  // Test patterns
  testMatch: [
    '<rootDir>/tests/**/*.test.{js,jsx,ts,tsx}',
    '<rootDir>/tests/**/*.spec.{js,jsx,ts,tsx}',
  ],

  // Coverage configuration
  collectCoverageFrom: [
    'packages/**/*.{js,ts,tsx}',
    'app/**/*.{js,ts,tsx}',
    'components/**/*.{js,ts,tsx}',
    'lib/**/*.{js,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/past-prototypes/**',
    '!**/.next/**',
    '!**/coverage/**',
    '!**/dist/**',
  ],

  coverageReporters: ['text', 'lcov', 'html', 'json-summary'],

  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
    './packages/auth/': {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95,
    },
  },

  // Test projects for different environments
  projects: [
    {
      displayName: 'unit',
      testMatch: ['<rootDir>/tests/unit/**/*.test.{js,ts,tsx}'],
      testEnvironment: 'jest-environment-jsdom',
      setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
    },
    {
      displayName: 'integration',
      testMatch: ['<rootDir>/tests/integration/**/*.test.{js,ts,tsx}'],
      testEnvironment: 'jest-environment-node',
      setupFilesAfterEnv: ['<rootDir>/tests/setup-integration.ts'],
    },
    {
      displayName: 'security',
      testMatch: ['<rootDir>/tests/security/**/*.test.{js,ts,tsx}'],
      testEnvironment: 'jest-environment-node',
      setupFilesAfterEnv: ['<rootDir>/tests/setup-security.ts'],
    },
    {
      displayName: 'api',
      testMatch: ['<rootDir>/tests/api/**/*.test.{js,ts,tsx}'],
      testEnvironment: 'jest-environment-node',
      setupFilesAfterEnv: ['<rootDir>/tests/setup-api.ts'],
    },
    {
      displayName: 'performance',
      testMatch: ['<rootDir>/tests/performance/**/*.test.{js,ts,tsx}'],
      testEnvironment: 'jest-environment-node',
      setupFilesAfterEnv: ['<rootDir>/tests/setup-performance.ts'],
    },
    {
      displayName: 'accessibility',
      testMatch: ['<rootDir>/tests/accessibility/**/*.test.{js,ts,tsx}'],
      testEnvironment: 'jest-environment-jsdom',
      setupFilesAfterEnv: ['<rootDir>/tests/setup-accessibility.ts'],
    },
  ],

  // Global setup and teardown (temporarily disabled for cleanup)
  // globalSetup: '<rootDir>/tests/global-setup.ts',
  // globalTeardown: '<rootDir>/tests/global-teardown.ts',

  // Transform configuration - let Next.js handle transforms
  // transform: {
  //   '^.+\\.(js|jsx|ts|tsx)$': ['ts-jest', {
  //     tsconfig: 'tsconfig.json',
  //   }],
  // },

  // Mock configuration
  clearMocks: true,
  restoreMocks: true,
  resetMocks: true,

  // Verbose output for debugging
  verbose: true,

  // Timeout configuration
  testTimeout: 30000,
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
