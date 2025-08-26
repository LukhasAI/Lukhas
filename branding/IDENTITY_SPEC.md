# ΛiD Identity Specification

## Overview

The **Λid** (Lambda Identity) system provides secure, privacy-preserving identity management for the LUKHAS AI ecosystem. This specification defines the canonical format, alias structure, and security policies for identity representation.

## Identity Format

### Canonical Structure

```text
ΛiD#REALM/ZONE/TOKEN-CHECKSUM
```

**Components:**
- **ΛiD** - Identity namespace prefix (display contexts only)
- **REALM** - Service domain (LUKHAS, MATRIZ)
- **ZONE** - Geographic/regulatory zone (EU, US, APAC)
- **TOKEN** - Versioned HMAC-based identifier
- **CHECKSUM** - CRC32 validation suffix

### Display Rules

**Display Context (UI/Logos):**
```text
ΛiD#LUKHAS/EU/v2.a7f3d9e1-4b2c
```

**Plain Text Context (APIs/URLs):**
```
lid#LUKHAS/EU/v2.a7f3d9e1-4b2c
```

**Accessibility:**
- All display instances must include `aria-label="Lambda Identity"`
- Screen readers announce as "Lambda Identity"
- Alt text uses plain "lid" format

## Realms

Allowed REALM values (see `alias.realms.json`):

- **LUKHAS** - Core AI platform services
- **MATRIZ** - Cognitive architecture and node management

## Zones

Allowed ZONE values (see `alias.zones.json`):

- **EU** - European Union (GDPR compliance)
- **US** - United States (SOC2/CCPA compliance)
- **APAC** - Asia-Pacific (regional data residency)

## Token Structure

### Version Format

```
v{VERSION}.{HMAC_PREFIX}-{SEQUENCE}
```

**Example:** `v2.a7f3d9e1-4b2c`

**Components:**
- **VERSION** - Integer version for rotation (v1, v2, v3...)
- **HMAC_PREFIX** - First 8 chars of HMAC-SHA256
- **SEQUENCE** - 4-char sequence for collision avoidance

### Security Properties

- **No PII** - Tokens contain no personal information
- **Rotatable** - Versioned for seamless key rotation
- **Collision-resistant** - HMAC + sequence prevents duplicates
- **Verifiable** - CRC32 checksum validates format integrity

## Privacy Policy

### Data Protection

1. **No PII in Public Aliases**
   - Names, emails, or personal data never appear in tokens
   - Tokens are cryptographically derived from internal IDs

2. **Revocation Support**
   - All token versions can be individually revoked
   - Emergency rotation replaces all active tokens

3. **Audit Trail**
   - All token generation and rotation events logged
   - Attribution tracked for compliance

### Compliance Alignment

- **GDPR** - Right to erasure via token revocation
- **SOC2** - Comprehensive audit logging
- **CCPA** - Data minimization in public identifiers

## Implementation Requirements

### Token Generation

```typescript
interface TokenGenerator {
  generateAlias(
    realm: 'LUKHAS' | 'MATRIZ',
    zone: 'EU' | 'US' | 'APAC',
    userId: string,
    version?: number
  ): Promise<string>;

  rotateAlias(currentAlias: string): Promise<string>;

  validateAlias(alias: string): Promise<boolean>;
}
```

### Rotation Policy

- **Automatic** - Every 90 days for active users
- **Manual** - User-initiated via security settings
- **Emergency** - Immediate rotation for security incidents
- **Graceful** - Previous version valid for 24h during rotation

## Integration Points

### Authentication Flow

1. **Registration** - Generate initial ΛiD alias
2. **Login** - Resolve alias to internal user ID
3. **Token Refresh** - Validate alias integrity
4. **Profile Updates** - No change to public alias

### API Integration

```typescript
// Resolve alias to user context
GET /api/identity/resolve/:alias
Response: { userId, tier, scopes, metadata }

// Rotate user's alias
POST /api/alias/rotate
Body: { currentAlias, justification }
Response: { newAlias, oldAlias, expiresAt }
```

### Database Schema

```sql
CREATE TABLE identity_aliases (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  alias TEXT NOT NULL UNIQUE,
  realm TEXT NOT NULL CHECK (realm IN ('LUKHAS', 'MATRIZ')),
  zone TEXT NOT NULL CHECK (zone IN ('EU', 'US', 'APAC')),
  token_version INTEGER NOT NULL DEFAULT 1,
  hmac_hash TEXT NOT NULL,
  checksum TEXT NOT NULL,
  active BOOLEAN NOT NULL DEFAULT true,
  revoked_at TIMESTAMP,
  revoked_reason TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP,
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_identity_aliases_user_active ON identity_aliases(user_id, active);
CREATE INDEX idx_identity_aliases_alias ON identity_aliases(alias);
CREATE INDEX idx_identity_aliases_realm_zone ON identity_aliases(realm, zone);
```

## Security Considerations

### Threat Model

**Protected Against:**
- PII exposure in public contexts
- Token prediction attacks
- Collision attacks
- Replay attacks (via checksum validation)

**Mitigated Risks:**
- User enumeration (tokens reveal no patterns)
- Data correlation across services (zoned isolation)
- Compliance violations (no PII in tokens)

### Cryptographic Requirements

- **HMAC** - HMAC-SHA256 with 256-bit keys
- **Key Rotation** - Master keys rotated quarterly
- **Key Storage** - HSM or equivalent secure storage
- **Entropy** - Minimum 128 bits per token

## Testing Requirements

### Validation Tests

```typescript
describe('ΛiD Identity System', () => {
  test('generates valid aliases for all realm/zone combinations');
  test('rotates aliases while maintaining user mapping');
  test('validates checksum integrity');
  test('rejects invalid realm/zone combinations');
  test('enforces PII-free tokens');
  test('handles concurrent rotation requests');
});
```

### Load Testing

- **Alias Generation** - 1000 RPS sustained
- **Alias Resolution** - 10,000 RPS sustained
- **Rotation Operations** - 100 RPS sustained
- **Validation** - 50,000 RPS sustained

## Monitoring & Observability

### Metrics

```typescript
interface IdentityMetrics {
  aliasGenerationRate: number;
  aliasResolutionLatency: number;
  rotationSuccessRate: number;
  validationErrorRate: number;
  activeAliasCount: number;
  expiredAliasCount: number;
}
```

### Alerts

- **High rotation rate** - Potential security incident
- **Validation failures** - Token corruption or attacks
- **Resolution latency spikes** - Performance degradation
- **Expired token usage** - Client integration issues

## Compliance & Audit

### Required Logs

```json
{
  "event": "alias_generated",
  "timestamp": "2025-08-23T10:30:00Z",
  "userId": "internal-uuid",
  "alias": "lid#LUKHAS/EU/v1.a7f3d9e1-4b2c",
  "realm": "LUKHAS",
  "zone": "EU",
  "version": 1,
  "metadata": {
    "requestId": "req-123",
    "clientIP": "192.168.1.1",
    "userAgent": "LUKHAS-Client/1.0"
  }
}
```

### Audit Requirements

- **Retention** - 7 years for compliance
- **Integrity** - Tamper-evident logging
- **Access Control** - SOC2 compliant audit access
- **Export** - Machine-readable compliance reports

## Migration Path

### Phase 1: Implementation
- Deploy token generation system
- Implement alias resolution APIs
- Create rotation endpoints

### Phase 2: Integration
- Update authentication flows
- Migrate existing user identifiers
- Deploy UI components

### Phase 3: Optimization
- Performance tuning
- Monitoring deployment
- Compliance validation

## Version History

- **v1.0** - Initial specification
- **v1.1** - Added zone-based compliance requirements
- **v1.2** - Enhanced security considerations
- **v2.0** - Current specification with rotation support

---

*This specification aligns with LUKHAS branding policy - Λ symbol used only in display contexts, with plain "lid" for APIs and accessibility.*
