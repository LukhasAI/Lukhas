# Lukhas Identity Storage Layer - Deployment Guide

**Version**: 1.0
**Last Updated**: 2025-11-14
**Author**: agent-identity-specialist

## Overview

The Lukhas Identity system uses a dual-storage architecture for optimal performance and durability:

- **Redis**: Ephemeral state (tokens, sessions, challenges) - High performance, automatic TTL expiry
- **PostgreSQL**: Durable state (WebAuthn credentials, user profiles) - Encrypted at rest, ACID guarantees

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Lukhas Identity System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐              ┌─────────────────────────┐ │
│  │ RedisTokenStore  │              │   WebAuthnStore         │ │
│  │                  │              │                         │ │
│  │ - OAuth2 tokens  │              │ - FIDO2 credentials     │ │
│  │ - Refresh tokens │              │ - Public keys           │ │
│  │ - Session data   │              │ - Signature counters    │ │
│  │ - Challenges     │              │ - User relationships    │ │
│  │ - Revocations    │              │                         │ │
│  └────────┬─────────┘              └──────────┬──────────────┘ │
│           │                                   │                 │
│           │ TTL expiry                        │ AES-GCM-256     │
│           │ <10ms revocation                  │ encryption      │
│           │                                   │                 │
└───────────┼───────────────────────────────────┼─────────────────┘
            │                                   │
            ▼                                   ▼
   ┌────────────────┐                 ┌─────────────────┐
   │  Redis 7.x     │                 │  Postgres 15+   │
   │                │                 │                 │
   │  - Port: 6379  │                 │  - Port: 5432   │
   │  - DB: 0       │                 │  - DB: lukhas   │
   │  - No auth     │                 │  - SSL required │
   └────────────────┘                 └─────────────────┘
```

---

## Prerequisites

### Redis 7.x

**Installation (macOS)**:
```bash
brew install redis
brew services start redis

# Verify
redis-cli ping
# Expected: PONG
```

**Installation (Linux - Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install redis-server

# Enable persistence (optional for tokens, but recommended)
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify
redis-cli ping
```

**Installation (Docker)**:
```bash
docker run -d \
  --name lukhas-redis \
  -p 6379:6379 \
  redis:7-alpine redis-server --appendonly yes

# Verify
docker exec lukhas-redis redis-cli ping
```

### PostgreSQL 15+

**Installation (macOS)**:
```bash
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb lukhas_identity
```

**Installation (Linux - Ubuntu/Debian)**:
```bash
sudo apt update
sudo apt install postgresql-15

# Start service
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb lukhas_identity
sudo -u postgres psql -c "CREATE USER lukhas WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lukhas_identity TO lukhas;"
```

**Installation (Docker)**:
```bash
docker run -d \
  --name lukhas-postgres \
  -e POSTGRES_USER=lukhas \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=lukhas_identity \
  -p 5432:5432 \
  postgres:15-alpine

# Enable pgcrypto extension (for future UUID generation)
docker exec lukhas-postgres psql -U lukhas -d lukhas_identity -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
```

---

## Environment Configuration

Create a `.env` file or set environment variables:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50
REDIS_SOCKET_TIMEOUT=5.0

# PostgreSQL Configuration
DB_URL=postgresql://lukhas:your_secure_password@localhost:5432/lukhas_identity
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Encryption Configuration
# WARNING: Generate a secure 32-byte key and store in KMS or secure vault!
IDENTITY_ENCRYPTION_KEY=<base64-encoded-32-byte-key>
# Example: openssl rand -base64 32

# KMS Configuration (optional, recommended for production)
KMS_KEY_ARN=arn:aws:kms:us-east-1:123456789012:key/abcd-1234-5678-90ef
# Or use local key with version tracking
KMS_KEY_ID=local-key-v1

# Issuer Configuration
LUKHAS_ISSUER=https://ai
```

### Generating Encryption Key

**Option 1: Local Development (NOT for production)**:
```bash
# Generate random 32-byte key
openssl rand -base64 32

# Set in environment
export IDENTITY_ENCRYPTION_KEY="<generated-key>"
```

**Option 2: Production (AWS KMS)**:
```bash
# Create KMS key
aws kms create-key \
  --description "Lukhas Identity WebAuthn encryption key" \
  --key-usage ENCRYPT_DECRYPT

# Get key ARN
aws kms describe-key --key-id <key-id> --query 'KeyMetadata.Arn'

# Generate data key
aws kms generate-data-key \
  --key-id <key-arn> \
  --key-spec AES_256

# Store plaintext key in secure parameter store
aws ssm put-parameter \
  --name /lukhas/identity/encryption-key \
  --value "<plaintext-key>" \
  --type SecureString \
  --key-id <key-arn>
```

---

## Database Schema

The WebAuthn store automatically creates tables on first run. Schema:

```sql
CREATE TABLE webauthn_credentials (
    -- Primary key
    id VARCHAR(64) PRIMARY KEY,  -- Credential ID (base64url)

    -- User relationship
    lid VARCHAR(64) NOT NULL,  -- User ΛID (indexed)

    -- Encrypted credential data
    public_key_encrypted BYTEA NOT NULL,  -- AES-GCM encrypted COSE key
    aaguid_encrypted BYTEA,  -- Encrypted authenticator GUID

    -- Signature counter (clone detection)
    sign_count INTEGER DEFAULT 0 NOT NULL,

    -- Metadata
    credential_type VARCHAR(32) DEFAULT 'public-key' NOT NULL,
    transports TEXT,  -- JSON array
    attestation_format VARCHAR(32),
    user_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_used_at TIMESTAMP,

    -- Encryption metadata
    encryption_key_id VARCHAR(64) NOT NULL,  -- KMS key ID
    nonce BYTEA NOT NULL,  -- AES-GCM nonce (12 bytes)

    -- Audit
    registered_from_ip VARCHAR(45),  -- IPv6-compatible
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX idx_webauthn_credentials_lid ON webauthn_credentials(lid);
CREATE INDEX idx_webauthn_credentials_created_at ON webauthn_credentials(created_at);
```

---

## Application Integration

### Python Code Example

```python
from core.identity.storage import RedisTokenStore, WebAuthnStore

# Initialize stores
redis_store = RedisTokenStore(
    redis_url="redis://localhost:6379/0",
    max_connections=50
)

webauthn_store = WebAuthnStore(
    db_url="postgresql://lukhas:password@localhost/lukhas_identity",
    encryption_key=base64.b64decode(os.getenv("IDENTITY_ENCRYPTION_KEY")),
    kms_key_id=os.getenv("KMS_KEY_ID")
)

# Store OAuth2 token (1-hour TTL)
await redis_store.store_token(
    jti="tok_abc123",
    metadata={
        "sub": "usr_alice",
        "scope": "openid profile",
        "client_id": "lukhas_web"
    },
    ttl_seconds=3600
)

# Introspect token
token_data = await redis_store.introspect_token("tok_abc123")
if token_data["active"]:
    print(f"Token valid for user: {token_data['sub']}")

# Revoke token (immediate, <10ms)
await redis_store.revoke_token("tok_abc123", reason="user_logout")

# Store WebAuthn credential
await webauthn_store.store_credential(
    credential_id="cred_xyz789",
    lid="usr_alice",
    public_key=credential_public_key_bytes,  # From WebAuthn registration
    aaguid=authenticator_aaguid,
    transports=["usb", "nfc"],
    attestation_format="packed"
)

# Retrieve credential for authentication
cred = await webauthn_store.get_credential("cred_xyz789")
if cred:
    # Use cred.public_key to verify WebAuthn assertion
    pass
```

---

## Performance Tuning

### Redis

**Connection Pool**:
- `max_connections=50`: Sufficient for 1000 req/s
- `socket_timeout=5.0`: Fail fast on network issues
- `retry_on_timeout=True`: Retry transient failures

**Memory Management**:
```bash
# Set maxmemory policy (evict expired keys first)
redis-cli config set maxmemory-policy allkeys-lru
redis-cli config set maxmemory 2gb
```

**Persistence** (optional for tokens, but useful for debugging):
```bash
# Enable AOF (Append-Only File)
redis-cli config set appendonly yes
redis-cli config set appendfsync everysec
```

### PostgreSQL

**Connection Pool** (via SQLAlchemy):
```python
engine = create_engine(
    db_url,
    pool_size=20,  # Base pool size
    max_overflow=40,  # Additional connections under load
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
)
```

**Indexes**:
```sql
-- Already created by WebAuthnStore, but verify:
CREATE INDEX CONCURRENTLY idx_webauthn_credentials_lid ON webauthn_credentials(lid);
CREATE INDEX CONCURRENTLY idx_webauthn_credentials_created_at ON webauthn_credentials(created_at);
```

**Vacuuming** (automatic, but verify):
```sql
-- Check autovacuum settings
SELECT name, setting FROM pg_settings WHERE name LIKE 'autovacuum%';

-- Manual vacuum if needed
VACUUM ANALYZE webauthn_credentials;
```

---

## Monitoring & Health Checks

### Redis Health Check

```python
health = redis_store.health_check()
print(health)
# {"status": "healthy", "pool": {"max_connections": 50, ...}}
```

**Prometheus Metrics** (to be implemented in Task 47):
- `redis_connections_active`
- `redis_token_operations_total{operation="store|get|revoke"}`
- `redis_revocation_latency_seconds`

### PostgreSQL Health Check

```python
health = webauthn_store.health_check()
print(health)
# {"status": "healthy", "kms_key_id": "local-key-v1"}
```

**Prometheus Metrics** (to be implemented):
- `postgres_credentials_total`
- `postgres_query_duration_seconds{operation="store|get|update"}`
- `postgres_connection_pool_size`

---

## Security Considerations

### Redis

1. **Network Security**:
   - Bind to `127.0.0.1` for local-only access
   - Use Redis AUTH if exposed: `requirepass your_secure_password`
   - Enable TLS for production: `tls-port 6380`

2. **Data Sensitivity**:
   - Tokens in Redis are **JWTs** (already signed, but not encrypted)
   - Revocation records contain timestamps only (no PII)
   - TTL auto-expires data (no manual cleanup needed)

3. **Persistence**:
   - AOF disabled by default (tokens are ephemeral)
   - Enable RDB snapshots for debugging: `save 900 1`

### PostgreSQL

1. **Encryption at Rest**:
   - Credentials encrypted with AES-GCM-256
   - KMS envelope encryption recommended
   - Nonce stored per-row for security

2. **Network Security**:
   - Require SSL: `sslmode=require` in connection string
   - Client certificates (mTLS) for production
   - Firewall rules (allow only app servers)

3. **Access Control**:
   - Dedicated `lukhas` user with minimal privileges
   - No superuser access for application
   - Row-level security (RLS) for multi-tenancy (future)

4. **Backup & Disaster Recovery**:
   - Daily pg_dump: `pg_dump lukhas_identity > backup.sql`
   - Point-in-time recovery (PITR) via WAL archiving
   - Test restore procedure monthly

---

## Disaster Recovery

### Token Revocation Loss (Redis Failure)

**Impact**: Revoked tokens may briefly be accepted until Redis recovers.

**Mitigation**:
- Redis cluster with replication (master-replica setup)
- Sentinel for automatic failover
- Short token TTLs (1 hour max) limit exposure window

**Recovery**:
```bash
# Restart Redis
redis-cli shutdown
redis-server /etc/redis/redis.conf

# Verify
redis-cli ping
```

### Credential Loss (Postgres Failure)

**Impact**: Users cannot authenticate with WebAuthn.

**Mitigation**:
- PostgreSQL streaming replication (hot standby)
- Daily backups with encryption
- Multi-region replication for critical systems

**Recovery**:
```bash
# Restore from backup
psql lukhas_identity < backup.sql

# Or use PITR
pg_restore -d lukhas_identity backup.dump
```

---

## Migration & Rollback

### Upgrading from In-Memory Storage

**Current State**: WebAuthn manager uses in-memory dict (prototype).

**Migration Steps**:
1. Deploy PostgreSQL schema (automatic on first run)
2. Export existing credentials (if any) from memory
3. Import to WebAuthnStore via API
4. Switch over (feature flag: `USE_POSTGRES_WEBAUTHN=true`)
5. Monitor for 24 hours
6. Remove in-memory code

**Rollback Plan**:
1. Set feature flag: `USE_POSTGRES_WEBAUTHN=false`
2. Restore in-memory manager
3. Debug Postgres issue offline

---

## Testing

### Unit Tests

```bash
# Run storage tests
pytest tests/identity/storage/ -v --asyncio-mode=auto

# Coverage report
pytest tests/identity/storage/ --cov=core.identity.storage --cov-report=html
```

### Integration Tests

```bash
# Start test Redis & Postgres
docker-compose -f docker-compose.test.yml up -d

# Run integration tests
pytest tests/integration/identity/ -v

# Cleanup
docker-compose -f docker-compose.test.yml down
```

### Performance Tests

```bash
# Benchmark token operations (target: <5ms p95)
python scripts/benchmark_token_store.py

# Benchmark WebAuthn operations (target: <50ms p95)
python scripts/benchmark_webauthn_store.py
```

---

## Troubleshooting

### Redis Connection Errors

**Symptom**: `redis.exceptions.ConnectionError: Error connecting to localhost:6379`

**Solutions**:
```bash
# Check if Redis is running
redis-cli ping

# Check port binding
lsof -i :6379

# Restart Redis
brew services restart redis  # macOS
sudo systemctl restart redis-server  # Linux
```

### PostgreSQL Connection Errors

**Symptom**: `psycopg2.OperationalError: could not connect to server`

**Solutions**:
```bash
# Check if Postgres is running
pg_isready

# Check connection string
psql postgresql://lukhas:password@localhost/lukhas_identity -c "SELECT 1;"

# Check firewall
sudo ufw allow 5432/tcp  # Linux
```

### Decryption Errors

**Symptom**: `cryptography.exceptions.InvalidTag`

**Causes**:
- Encryption key mismatch (wrong key used)
- Corrupted ciphertext in database
- Nonce reuse (should never happen)

**Solutions**:
```bash
# Verify encryption key
python -c "import base64, os; print(len(base64.b64decode(os.getenv('IDENTITY_ENCRYPTION_KEY'))))"
# Expected: 32

# Check database integrity
psql lukhas_identity -c "SELECT id, LENGTH(public_key_encrypted), LENGTH(nonce) FROM webauthn_credentials LIMIT 5;"
```

---

## References

- [Redis Documentation](https://redis.io/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [WebAuthn Specification](https://www.w3.org/TR/webauthn-2/)
- [RFC 7662 - OAuth2 Token Introspection](https://datatracker.ietf.org/doc/html/rfc7662)
- [AES-GCM Encryption](https://csrc.nist.gov/publications/detail/sp/800-38d/final)

---

## Change Log

| Version | Date       | Changes                                    |
|---------|------------|--------------------------------------------|
| 1.0     | 2025-11-14 | Initial deployment guide                   |

---

**Next Steps**: Proceed to [Task 42: Asymmetric Key Management + JWKS](JWKS_AND_KEY_ROTATION.md)
