-- LUKHAS Identity Schema for ΛID (LucasID) System
-- Implements canonical storage: namespace:username with separate alias metadata
-- Enforces uniqueness on (namespace, username) as per requirements

-- Extension for better JSON handling and audit trails
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS identity.mfa CASCADE;
DROP TABLE IF EXISTS identity.aliases CASCADE;
DROP TABLE IF EXISTS identity.users CASCADE;
DROP SCHEMA IF EXISTS identity CASCADE;

-- Create identity schema
CREATE SCHEMA IF NOT EXISTS identity;

-- Users table: canonical ΛID storage
-- Stores only namespace:username (no PII, no provider info)
CREATE TABLE identity.users (
    -- Core ΛID components (canonical storage)
    namespace VARCHAR(48),          -- Optional org/community namespace (e.g. 'openai', 'stanford')
    username VARCHAR(32) NOT NULL,  -- User-chosen handle (3-32 chars, a-z0-9_-)

    -- Metadata (separate from uniqueness constraint)
    preferred_locale VARCHAR(16),   -- Optional locale (~us-sf, ~uk-lon)
    preferred_emoji CHAR(4),        -- Optional emoji/sigil (stored as UTF-8)

    -- System fields
    user_uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    tier VARCHAR(2) DEFAULT 'T2' CHECK (tier IN ('T1', 'T2', 'T3', 'T4', 'T5')),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Audit fields (requirement #6: audit trail)
    created_by VARCHAR(100),
    last_login_at TIMESTAMPTZ,
    login_count INTEGER DEFAULT 0,

    -- Privacy fields (requirement #3: data minimization)
    consent_metadata_only BOOLEAN DEFAULT TRUE,
    consent_granted_scopes JSONB DEFAULT '[]'::jsonb,

    -- Uniqueness: (namespace, username) must be unique
    CONSTRAINT users_lid_unique UNIQUE (namespace, username)
);

-- Aliases table: provider login mappings (federated identities)
-- Links OAuth/WebAuthn providers to canonical ΛID
CREATE TABLE identity.aliases (
    alias_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Link to canonical user
    user_uuid UUID NOT NULL REFERENCES identity.users(user_uuid) ON DELETE CASCADE,

    -- Provider information (requirement #2: OAuth aliases are convenience)
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('lukhas', 'google', 'apple', 'github', 'microsoft', 'phone', 'webauthn')),
    provider_user_id VARCHAR(255),     -- Provider's user ID (hashed if PII)
    username_hint VARCHAR(100),        -- Username part used for login UX (not stored raw PII)

    -- Verification status
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMPTZ,

    -- System fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    use_count INTEGER DEFAULT 0,

    -- Provider-specific metadata (encrypted if sensitive)
    provider_metadata JSONB DEFAULT '{}'::jsonb,

    -- Security: prevent duplicate provider mappings per user
    CONSTRAINT aliases_user_provider_unique UNIQUE (user_uuid, provider)
);

-- MFA table: multi-factor authentication options
-- Supports WebAuthn (primary), TOTP, GTΨ (gesture token)
CREATE TABLE identity.mfa (
    mfa_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Link to user
    user_uuid UUID NOT NULL REFERENCES identity.users(user_uuid) ON DELETE CASCADE,

    -- MFA method (requirement #2: WebAuthn primary, GTΨ for consent)
    method VARCHAR(20) NOT NULL CHECK (method IN ('webauthn', 'totp', 'gtpsi', 'backup_codes')),

    -- Method-specific data (encrypted/hashed per requirement #5)
    credential_id VARCHAR(255),        -- WebAuthn credential ID
    public_key_hash TEXT,             -- Hashed public key (requirement #5: edge first)
    encrypted_secret TEXT,            -- TOTP secret (encrypted) or GTΨ model hash

    -- Status
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ,
    use_count INTEGER DEFAULT 0,

    -- Device binding (for WebAuthn/GTΨ)
    device_fingerprint VARCHAR(255),
    device_name VARCHAR(100),

    -- Unique constraint: one credential per method per user
    CONSTRAINT mfa_user_method_unique UNIQUE (user_uuid, method, credential_id)
);

-- Audit log table (requirement #6: logs, audit trail, revocation paths)
CREATE TABLE identity.audit_log (
    log_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Event details
    event_type VARCHAR(50) NOT NULL,   -- 'login', 'resolution', 'grant', 'revoke', 'mfa_use'
    user_uuid UUID REFERENCES identity.users(user_uuid),
    canonical_lid VARCHAR(100),        -- For easy searching

    -- Context
    provider VARCHAR(50),
    client_ip INET,
    user_agent TEXT,
    session_id VARCHAR(100),

    -- Timing
    event_at TIMESTAMPTZ DEFAULT NOW(),
    processing_time_ms NUMERIC(8,3),   -- Performance tracking

    -- Metadata (structured logging)
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Result
    success BOOLEAN,
    error_message TEXT
);

-- Indexes for performance
CREATE INDEX users_username_idx ON identity.users (username);
CREATE INDEX users_namespace_idx ON identity.users (namespace) WHERE namespace IS NOT NULL;
CREATE INDEX users_created_at_idx ON identity.users (created_at);
CREATE INDEX users_tier_idx ON identity.users (tier);

CREATE INDEX aliases_provider_idx ON identity.aliases (provider);
CREATE INDEX aliases_username_hint_idx ON identity.aliases (username_hint);
CREATE INDEX aliases_last_used_idx ON identity.aliases (last_used_at DESC);

CREATE INDEX mfa_method_idx ON identity.mfa (method);
CREATE INDEX mfa_enabled_idx ON identity.mfa (enabled) WHERE enabled = TRUE;

CREATE INDEX audit_event_type_idx ON identity.audit_log (event_type);
CREATE INDEX audit_user_idx ON identity.audit_log (user_uuid);
CREATE INDEX audit_time_idx ON identity.audit_log (event_at DESC);
CREATE INDEX audit_lid_idx ON identity.audit_log (canonical_lid);

-- Performance monitoring view (requirement: p95 < 30ms)
CREATE VIEW identity.performance_stats AS
SELECT
    event_type,
    COUNT(*) as event_count,
    ROUND(AVG(processing_time_ms)::numeric, 2) as avg_time_ms,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY processing_time_ms)::numeric, 2) as p95_time_ms,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY processing_time_ms)::numeric, 2) as p99_time_ms
FROM identity.audit_log
WHERE processing_time_ms IS NOT NULL
  AND event_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type;

-- Reserved namespaces (seeded data)
-- These are verified organizations with special tier privileges
INSERT INTO identity.users (namespace, username, tier, verified, created_by) VALUES
    ('openai', 'reviewer', 'T5', TRUE, 'system_seed'),
    ('stanford', 'alice_smith', 'T3', TRUE, 'system_seed'),
    ('mit', 'prof_johnson', 'T3', TRUE, 'system_seed'),
    (NULL, 'gonzo', 'T2', TRUE, 'system_seed');  -- Personal namespace example

-- Sample aliases for seeded users
INSERT INTO identity.aliases (user_uuid, provider, username_hint, verified) VALUES
    ((SELECT user_uuid FROM identity.users WHERE namespace = 'openai' AND username = 'reviewer'),
     'apple', 'reviewer', TRUE),
    ((SELECT user_uuid FROM identity.users WHERE namespace = 'stanford' AND username = 'alice_smith'),
     'google', 'alice.smith', TRUE),
    ((SELECT user_uuid FROM identity.users WHERE namespace IS NULL AND username = 'gonzo'),
     'lukhas', 'gonzo', TRUE);

-- Sample MFA setups
INSERT INTO identity.mfa (user_uuid, method, enabled) VALUES
    ((SELECT user_uuid FROM identity.users WHERE namespace = 'openai' AND username = 'reviewer'),
     'webauthn', TRUE),
    ((SELECT user_uuid FROM identity.users WHERE namespace = 'stanford' AND username = 'alice_smith'),
     'webauthn', TRUE),
    ((SELECT user_uuid FROM identity.users WHERE namespace IS NULL AND username = 'gonzo'),
     'gtpsi', TRUE);

-- Helper functions for common operations
CREATE OR REPLACE FUNCTION identity.parse_canonical_lid(lid TEXT)
RETURNS TABLE(namespace VARCHAR(48), username VARCHAR(32)) AS $$
BEGIN
    -- Parse namespace:username format
    IF lid ~ ':' THEN
        RETURN QUERY SELECT
            SPLIT_PART(lid, ':', 1)::VARCHAR(48) as namespace,
            SPLIT_PART(lid, ':', 2)::VARCHAR(32) as username;
    ELSE
        RETURN QUERY SELECT
            NULL::VARCHAR(48) as namespace,
            lid::VARCHAR(32) as username;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to lookup user by canonical ΛID
CREATE OR REPLACE FUNCTION identity.get_user_by_lid(lid TEXT)
RETURNS TABLE(
    user_uuid UUID,
    namespace VARCHAR(48),
    username VARCHAR(32),
    tier VARCHAR(2),
    verified BOOLEAN,
    created_at TIMESTAMPTZ
) AS $$
DECLARE
    parsed_namespace VARCHAR(48);
    parsed_username VARCHAR(32);
BEGIN
    SELECT * FROM identity.parse_canonical_lid(lid) INTO parsed_namespace, parsed_username;

    RETURN QUERY
    SELECT u.user_uuid, u.namespace, u.username, u.tier, u.verified, u.created_at
    FROM identity.users u
    WHERE (u.namespace = parsed_namespace OR (u.namespace IS NULL AND parsed_namespace IS NULL))
      AND u.username = parsed_username;
END;
$$ LANGUAGE plpgsql;

-- Audit logging function (requirement #6)
CREATE OR REPLACE FUNCTION identity.log_event(
    p_event_type VARCHAR(50),
    p_user_uuid UUID DEFAULT NULL,
    p_canonical_lid VARCHAR(100) DEFAULT NULL,
    p_provider VARCHAR(50) DEFAULT NULL,
    p_client_ip INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_processing_time_ms NUMERIC DEFAULT NULL,
    p_success BOOLEAN DEFAULT TRUE,
    p_error_message TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID AS $$
DECLARE
    log_uuid UUID;
BEGIN
    INSERT INTO identity.audit_log (
        event_type, user_uuid, canonical_lid, provider,
        client_ip, user_agent, processing_time_ms,
        success, error_message, metadata
    ) VALUES (
        p_event_type, p_user_uuid, p_canonical_lid, p_provider,
        p_client_ip, p_user_agent, p_processing_time_ms,
        p_success, p_error_message, p_metadata
    ) RETURNING log_id INTO log_uuid;

    RETURN log_uuid;
END;
$$ LANGUAGE plpgsql;

-- Cleanup old audit logs (data minimization requirement #3)
CREATE OR REPLACE FUNCTION identity.cleanup_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Keep audit logs for 90 days by default
    DELETE FROM identity.audit_log
    WHERE event_at < NOW() - INTERVAL '90 days';

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT USAGE ON SCHEMA identity TO PUBLIC;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA identity TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA identity TO PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA identity TO PUBLIC;

-- Summary
SELECT 'LUKHAS Identity Schema Created' as status,
       COUNT(*) as users_seeded
FROM identity.users;
