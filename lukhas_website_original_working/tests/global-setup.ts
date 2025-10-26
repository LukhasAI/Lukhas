/**
 * LUKHAS AI ΛiD Authentication System - Global Test Setup
 * Phase 6: Comprehensive Testing & Validation
 * 
 * Global setup for all Jest test suites
 */

import crypto from 'crypto';
import { spawn, ChildProcess } from 'child_process';

let testDatabaseProcess: ChildProcess | null = null;

async function globalSetup() {
  console.log('🔧 Setting up LUKHAS AI ΛiD Authentication Test Environment...');

  // Set test environment variables
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
  process.env.LUKHAS_ID_SECRET = 'test-secret-key-with-minimum-32-chars-for-testing';

  // Generate test JWT keys
  const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
  });

  process.env.JWT_PRIVATE_KEY = Buffer.from(privateKey).toString('base64');
  process.env.JWT_PUBLIC_KEY = Buffer.from(publicKey).toString('base64');
  process.env.JWT_KEY_ID = 'test-key-2025';

  // Set up test database (SQLite in-memory for tests)
  process.env.DATABASE_URL = 'sqlite::memory:';

  // Set up test email configuration
  process.env.SMTP_HOST = 'smtp.example.com';
  process.env.SMTP_PORT = '587';
  process.env.SMTP_USER = 'test@lukhas.ai';
  process.env.SMTP_PASSWORD = 'test-password';
  process.env.SMTP_FROM_NAME = 'LUKHAS AI Test';
  process.env.SMTP_FROM_EMAIL = 'test@lukhas.ai';

  // Create test directories
  const fs = require('fs').promises;
  const path = require('path');
  
  const testDirs = [
    'test-results',
    'test-results/coverage',
    'test-results/reports',
    'test-results/artifacts',
  ];

  for (const dir of testDirs) {
    await fs.mkdir(path.join(process.cwd(), dir), { recursive: true });
  }

  // Create test certificates for HTTPS testing
  await createTestCertificates();

  console.log('✅ Test environment setup complete');
}

async function createTestCertificates() {
  const fs = require('fs').promises;
  const path = require('path');

  const certDir = path.join(process.cwd(), 'certs');
  await fs.mkdir(certDir, { recursive: true });

  // Generate self-signed certificate for localhost testing
  const { execSync } = require('child_process');
  
  try {
    // Create certificate configuration
    const configContent = `
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = CA
L = San Francisco
O = LUKHAS AI
CN = localhost

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
`;

    await fs.writeFile(path.join(certDir, 'cert.conf'), configContent);

    // Generate private key
    execSync(`openssl genpkey -algorithm RSA -out ${path.join(certDir, 'localhost.key')} -pkcs8`, { stdio: 'ignore' });

    // Generate certificate
    execSync(`openssl req -new -x509 -key ${path.join(certDir, 'localhost.key')} -out ${path.join(certDir, 'localhost.crt')} -days 365 -config ${path.join(certDir, 'cert.conf')}`, { stdio: 'ignore' });

    // Set environment variables for certificate paths
    process.env.DEV_SSL_CERT = path.join(certDir, 'localhost.crt');
    process.env.DEV_SSL_KEY = path.join(certDir, 'localhost.key');

    console.log('✅ Test certificates created');
  } catch (error) {
    console.warn('⚠️ Could not create test certificates:', error);
    // Continue without certificates - tests will run without HTTPS
  }
}

export default globalSetup;