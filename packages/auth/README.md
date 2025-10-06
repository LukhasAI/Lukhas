---
status: wip
type: documentation
---
# ΛiD Authentication System - Phase 1: Core Infrastructure

[![License](https://img.shields.io/badge/license-LUKHAS--Proprietary-blue.svg)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.1+-blue.svg)](https://www.typescriptlang.org/)
[![Constellation Framework (8 Stars)](https://img.shields.io/badge/Trinity-⚛️🧠🛡️-purple.svg)](https://lukhas.ai)

Enterprise-grade authentication system for LUKHAS AI, implementing the complete ΛiD (Lambda Identity) specification with tier-based access control, advanced security features, and Constellation Framework (8 Stars) integration.

## 🌟 Features

### ✨ Phase 1: Core Infrastructure (Current)

- **🔐 Tier-Based Access Control**: T1-T5 tier system with proper RPM/RPD limits
- **🎟️ Advanced JWT Management**: RS256 with key rotation and JWKS support
- **🔑 WebAuthn Passkeys**: Discoverable credentials with UV=required and AAGUID capture
- **📧 Magic Link Authentication**: One-time tokens with TTL 600s and IP/email throttling
- **⚡ Intelligent Rate Limiting**: Adaptive limits with burst allowance and concurrency control
- **🛡️ Security Features**: Refresh token families, device binding, session rotation, account lockout
- **📊 Comprehensive Auditing**: Security events with risk scoring and compliance tracking

### 🚀 Upcoming Phases

- **Phase 2**: Advanced MFA, biometric integration, OAuth2/OIDC provider
- **Phase 3**: Consciousness-aware authentication, Constellation Framework (8 Stars) deep integration
- **Phase 4**: Zero-knowledge proofs, quantum-resistant cryptography

## 🚀 Quick Start

### Installation

```bash
npm install @lukhas/auth
```

### Basic Usage

```typescript
import { initializeAuth, hasScope, checkRateLimit, generateTokenPair } from '@lukhas/auth';

// Initialize the system
const authSystem = initializeAuth({
  jwt: {
    issuer: 'https://auth.your-domain.com',
    audience: 'https://api.your-domain.com'
  }
});

// Check user permissions
const hasPermission = hasScope(
  'T2',                    // User tier
  'developer',             // User role
  ['matriz:write'],        // User scopes
  'matriz:write'           // Required scope
);

// Check rate limits
const rateLimitResult = checkRateLimit('user-123', 'T2', 'api:read');

// Generate authentication tokens
const tokens = await generateTokenPair(
  'user-123',              // User ID
  'T2',                    // User tier
  ['matriz:read', 'matriz:write'], // Scopes
  'device-456',            // Device handle
  'family-789'             // Token family ID
);
```

## 📚 Tier System

The ΛiD system implements a comprehensive 5-tier access control system:

| Tier | Name | Price | RPM | RPD | Features |
|------|------|-------|-----|-----|----------|
| T1 | Explorer | Free | 30 | 1,000 | Public access, documentation, demos |
| T2 | Builder | $29/mo | 60 | 5,000 | Personal projects, API read/write |
| T3 | Studio | $99/mo | 120 | 20,000 | Team collaboration, org RBAC |
| T4 | Enterprise | $499/mo | 300 | 100,000 | SSO, governance, export |
| T5 | Core Team | Internal | 1,000 | 1,000,000 | Full system access |

## 🔐 Authentication Methods

### Passkey Authentication (WebAuthn)

```typescript
import { registerPasskey, verifyPasskeyRegistration } from '@lukhas/auth';

// Generate registration options
const options = await registerPasskey('user-123', 'user@example.com', 'John Doe');

// Verify registration (after user completes WebAuthn ceremony)
const result = await verifyPasskeyRegistration(
  registrationResponse,
  options.challenge
);
```

### Magic Link Authentication

```typescript
import { sendMagicLink, verifyMagicLink } from '@lukhas/auth';

// Send magic link
const result = await sendMagicLink('user@example.com', 'login', {
  ipAddress: '192.168.1.1',
  userAgent: 'Mozilla/5.0...',
  userId: 'user-123',
  userTier: 'T2'
});

// Verify magic link
const verification = await verifyMagicLink(
  token,
  '192.168.1.1',
  'Mozilla/5.0...'
);
```

### JWT Token Management

```typescript
import { generateAccessToken, verifyToken, getJWKS } from '@lukhas/auth';

// Generate access token
const accessToken = await generateAccessToken(
  'user-123',
  'T2',
  ['matriz:read', 'api:keys:read']
);

// Verify token
const verification = await verifyToken(accessToken);

// Get JWKS for external verification
const jwks = await getJWKS();
```

## 🛡️ Security Features

### Refresh Token Family Tracking

Protects against token reuse attacks by tracking token families and automatically revoking all tokens in a family when reuse is detected.

```typescript
import { securityManager } from '@lukhas/auth';

const familyManager = securityManager.refreshTokenFamilyManager;

// Create token family
const familyId = familyManager.createFamily(
  'user-123',
  'device-456',
  'T2',
  ['matriz:read']
);

// Validate token in family
const validation = familyManager.validateTokenInFamily(familyId, 'token-jti');
```

### Device Binding and Fingerprinting

```typescript
import { securityManager } from '@lukhas/auth';

const deviceManager = securityManager.deviceBindingManager;

// Generate device fingerprint
const fingerprint = deviceManager.generateFingerprint(
  'Mozilla/5.0...',
  '192.168.1.1'
);

// Create or update device
const device = deviceManager.createOrUpdateDevice(
  'user-123',
  fingerprint,
  'Mozilla/5.0...',
  '192.168.1.1',
  'MacBook Pro'
);

// Trust device
deviceManager.trustDevice(device.handle, 'admin-user');
```

### Account Lockout with Exponential Backoff

```typescript
import { securityManager } from '@lukhas/auth';

const lockoutManager = securityManager.accountLockoutManager;

// Record failed attempt
const result = lockoutManager.recordFailedAttempt(
  'user-123',
  '192.168.1.1',
  'Mozilla/5.0...'
);

// Check lockout status
const status = lockoutManager.isAccountLocked('user-123');
```

## ⚡ Rate Limiting

### Basic Rate Limiting

```typescript
import { checkRateLimit, getRateLimitStatus } from '@lukhas/auth';

// Check rate limit
const result = checkRateLimit('user-123', 'T2', 'api:read', '192.168.1.1');

if (!result.allowed) {
  console.log(`Rate limited: ${result.reason}`);
  console.log(`Reset time: ${new Date(result.resetTime)}`);
}

// Get detailed status
const status = getRateLimitStatus('user-123', 'T2');
console.log(`API calls remaining: ${status.remaining.minute}/minute`);
```

### Advanced Rate Limiting with Adaptive Controls

```typescript
import { rateLimitMiddleware } from '@lukhas/auth';

// Create adaptive rate limiting middleware
const middleware = rateLimitMiddleware(
  async (userId) => getUserTier(userId),      // Get user tier
  async () => getSystemLoad(),                // Get system load
  async (userId) => getUserBehaviorScore(userId) // Get behavior score
);

// Use in request processing
const result = await middleware('user-123', 'api:write', '192.168.1.1');
```

## 🏗️ Database Schema

The system includes a comprehensive PostgreSQL schema with optimized indexes and functions:

```sql
-- Run the schema
psql -f packages/auth/schemas/database-schema.sql your_database
```

Key tables:
- `users` - Core user information with tier and role
- `sessions` - Active user sessions with security metadata
- `passkeys` - WebAuthn credentials with authenticator info
- `refresh_tokens` - Refresh tokens with family tracking
- `device_handles` - Device binding and trust management
- `security_events` - Comprehensive audit logging

## 📊 Monitoring and Analytics

### System Health

```typescript
import { getAuthSystemHealth } from '@lukhas/auth';

const health = getAuthSystemHealth();
console.log(health);
// {
//   status: 'healthy',
//   version: '1.0.0',
//   components: { ... },
//   metrics: { ... }
// }
```

### Security Event Monitoring

Security events are automatically logged with structured metadata:

```typescript
// Events are logged automatically, but you can query them
const events = await getSecurityEvents({
  userId: 'user-123',
  eventType: 'FAILED_LOGIN_ATTEMPT',
  timeRange: { start: '2024-01-01', end: '2024-01-31' }
});
```

## 🧪 Testing

The package includes comprehensive test suites:

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run integration tests only
npm test -- --testPathPattern=integration

# Run performance tests
npm test -- --testPathPattern=performance
```

## 🔧 Configuration

### Complete Configuration Example

```typescript
import { initializeAuth, LUKHAS_AUTH_CONFIG } from '@lukhas/auth';

const authSystem = initializeAuth({
  jwt: {
    issuer: 'https://auth.lukhas.ai',
    audience: 'https://api.lukhas.ai',
    accessTokenTTL: 900,  // 15 minutes
    refreshTokenTTL: 2592000,  // 30 days
    algorithm: 'RS256'
  },
  passkeys: {
    rpId: 'lukhas.ai',
    rpName: 'LUKHAS AI',
    origin: 'https://lukhas.ai',
    timeout: 60000,
    userVerification: 'required',
    attestation: 'direct'
  },
  magicLinks: {
    tokenTTL: 600,  // 10 minutes
    maxAttempts: 3,
    throttling: {
      enabled: true,
      windowSizeMs: 3600000,  // 1 hour
      maxAttempts: 5,
      blockDurationMs: 3600000  // 1 hour
    }
  },
  security: {
    maxLoginAttempts: 5,
    lockoutDuration: 300000,  // 5 minutes base
    sessionTimeout: 86400000,  // 24 hours
    requireMFA: false
  }
});
```

### Environment Variables

```bash
# JWT Configuration
JWT_ISSUER=https://auth.lukhas.ai
JWT_AUDIENCE=https://api.lukhas.ai
JWT_PRIVATE_KEY_PATH=/path/to/private.key
JWT_PUBLIC_KEY_PATH=/path/to/public.key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/lukhas_auth

# Redis (for distributed rate limiting)
REDIS_URL=redis://localhost:6379

# Security
LUKHAS_ID_SECRET=your-32-character-secret-key-here
ENCRYPTION_KEY=your-encryption-key-for-sensitive-data
```

## 📖 API Reference

### Core Functions

#### `hasScope(userTier, userRole, userScopes, requiredScope, context?)`
Check if user has permission for a specific scope with deny-by-default security.

#### `checkRateLimit(userId, userTier, operation?, identifier?)`
Check if user is within rate limits for their tier and operation.

#### `generateTokenPair(userId, userTier, scopes, deviceHandle, familyId, options?)`
Generate access and refresh token pair with proper security.

#### `verifyToken(token)`
Verify JWT token and return payload if valid.

### Security Managers

#### `securityManager.performSecurityCheck(userId, ipAddress?, userAgent?, deviceHandle?)`
Comprehensive security validation including lockout, device trust, and threat detection.

#### `securityManager.refreshTokenFamilyManager`
Manage refresh token families for reuse detection.

#### `securityManager.deviceBindingManager`
Handle device fingerprinting, binding, and trust management.

#### `securityManager.sessionRotationManager`
Manage session lifecycle with automatic rotation on security events.

#### `securityManager.accountLockoutManager`
Handle account lockout with exponential backoff.

## 🤝 Contributing

This is a proprietary system for LUKHAS AI. For internal development:

1. Follow the Constellation Framework (8 Stars) principles (⚛️🧠🛡️)
2. Maintain deny-by-default security
3. Ensure comprehensive test coverage
4. Document all security-related changes
5. Follow the tier-based access control model

## 📄 License

LUKHAS Proprietary License - Internal use only.

## 🆘 Support

- **Internal Documentation**: [https://docs.lukhas.ai/auth](https://docs.lukhas.ai/auth)
- **Security Issues**: security@lukhas.ai
- **Development Support**: dev@lukhas.ai

---

**LUKHAS Authentication System** - *Consciousness-Aware Security for the Future*

*"Authentication that evolves with human consciousness and respects the Constellation Framework (8 Stars)."*

⚛️🧠🛡️ **Constellation Framework (8 Stars) Integration** - Identity, Consciousness, Guardian
