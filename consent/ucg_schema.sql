-- LUKHAS Unified Consent Graph (UCG) Schema
-- Implements capability-based consent with macaroon tokens and audit trails
-- Requirements: metadata-only by default, escalation to content requires explicit consent

-- Extension for better JSON handling and graph operations
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For efficient JSON indexing

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS consent.audit_log CASCADE;
DROP TABLE IF EXISTS consent.capability_tokens CASCADE;
DROP TABLE IF EXISTS consent.consent_grants CASCADE;
DROP TABLE IF EXISTS consent.resources CASCADE;
DROP TABLE IF EXISTS consent.scopes CASCADE;
DROP TABLE IF EXISTS consent.services CASCADE;
DROP SCHEMA IF EXISTS consent CASCADE;

-- Create consent schema
CREATE SCHEMA IF NOT EXISTS consent;

-- Services table: external services that can receive capabilities
CREATE TABLE consent.services (
    service_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL UNIQUE,  -- e.g. 'gmail', 'drive', 'dropbox'
    service_url VARCHAR(500),
    description TEXT,

    -- Service capabilities and trust level
    max_scope_level VARCHAR(20) DEFAULT 'metadata' CHECK (max_scope_level IN ('metadata', 'content', 'admin')),
    trusted BOOLEAN DEFAULT FALSE,

    -- System fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100)
);

-- Scopes table: granular permissions within services
CREATE TABLE consent.scopes (
    scope_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_id UUID NOT NULL REFERENCES consent.services(service_id) ON DELETE CASCADE,

    -- Hierarchical scope definition
    scope_name VARCHAR(100) NOT NULL,           -- e.g. 'email.read', 'files.list', 'files.move'
    scope_level VARCHAR(20) NOT NULL DEFAULT 'metadata' CHECK (scope_level IN ('metadata', 'content', 'admin')),
    parent_scope_id UUID REFERENCES consent.scopes(scope_id),

    -- Description and examples
    description TEXT,
    example_resources TEXT[],                   -- Example resource patterns

    -- Default behavior
    default_ttl_minutes INTEGER DEFAULT 60,    -- Default capability TTL
    requires_elevation BOOLEAN DEFAULT FALSE,  -- Requires explicit user consent

    -- System fields
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT scopes_service_name_unique UNIQUE (service_id, scope_name)
);

-- Resources table: specific resources that can be accessed
CREATE TABLE consent.resources (
    resource_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    service_id UUID NOT NULL REFERENCES consent.services(service_id) ON DELETE CASCADE,

    -- Resource identification
    resource_type VARCHAR(50) NOT NULL,        -- e.g. 'email_thread', 'file', 'folder'
    resource_identifier VARCHAR(500) NOT NULL, -- e.g. email thread ID, file path
    resource_hash VARCHAR(64),                 -- Hash for privacy (optional)

    -- Metadata (for metadata-only access)
    metadata JSONB DEFAULT '{}'::jsonb,        -- Headers, size, modified date, etc.

    -- Access patterns
    owner_lid VARCHAR(100),                    -- Canonical ΛID of resource owner
    sensitivity VARCHAR(20) DEFAULT 'normal' CHECK (sensitivity IN ('public', 'normal', 'sensitive', 'restricted')),

    -- System fields
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ,

    CONSTRAINT resources_service_identifier_unique UNIQUE (service_id, resource_identifier)
);

-- Consent grants: user consent records for service access
CREATE TABLE consent.consent_grants (
    grant_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Who granted consent
    user_lid VARCHAR(100) NOT NULL,            -- Canonical ΛID from identity.users

    -- What was granted
    service_id UUID NOT NULL REFERENCES consent.services(service_id) ON DELETE CASCADE,
    scope_ids UUID[] NOT NULL,                 -- Array of scope IDs granted
    resource_pattern VARCHAR(500),             -- Resource filter pattern (e.g. "emails/*", "files/Documents/*")

    -- Purpose and context
    purpose TEXT NOT NULL,                     -- Human-readable purpose (required)
    client_context JSONB DEFAULT '{}'::jsonb, -- Client app, session, etc.

    -- Timing and lifecycle
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_used_at TIMESTAMPTZ,
    use_count INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired', 'suspended')),
    revoked_at TIMESTAMPTZ,
    revoked_by VARCHAR(100),
    revoke_reason TEXT,

    -- Security
    granted_from_ip INET,
    granted_user_agent TEXT,

    -- Constraints
    CONSTRAINT grants_valid_expiry CHECK (expires_at > granted_at),
    CONSTRAINT grants_scope_not_empty CHECK (array_length(scope_ids, 1) > 0)
);

-- Capability tokens: short-lived tokens representing active capabilities
CREATE TABLE consent.capability_tokens (
    token_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Link to grant
    grant_id UUID NOT NULL REFERENCES consent.consent_grants(grant_id) ON DELETE CASCADE,

    -- Token data (macaroon with caveats)
    token_hash VARCHAR(64) NOT NULL UNIQUE,   -- SHA-256 of token (for revocation)
    macaroon_data TEXT NOT NULL,              -- Serialized macaroon with caveats

    -- Scope and restrictions (caveats)
    scopes VARCHAR(100)[] NOT NULL,           -- Actual scopes in this token
    resource_ids VARCHAR(500)[],              -- Specific resource IDs (if narrowed)
    max_uses INTEGER,                         -- Max number of uses (if limited)

    -- Timing
    issued_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    last_used_at TIMESTAMPTZ,
    use_count INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired', 'exhausted')),
    revoked_at TIMESTAMPTZ,
    revoke_reason TEXT,

    -- Client binding
    client_ip INET,
    client_fingerprint VARCHAR(100),

    CONSTRAINT tokens_valid_expiry CHECK (expires_at > issued_at),
    CONSTRAINT tokens_valid_uses CHECK (max_uses IS NULL OR max_uses > 0)
);

-- Audit log: comprehensive logging for consent operations
CREATE TABLE consent.audit_log (
    log_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,

    -- Event identification
    event_type VARCHAR(50) NOT NULL,          -- 'grant', 'revoke', 'use', 'escalate', 'expire'
    event_subtype VARCHAR(50),                -- 'metadata_access', 'content_escalation', etc.

    -- Actors
    user_lid VARCHAR(100) NOT NULL,           -- Who performed the action
    service_name VARCHAR(100),                -- Which service

    -- What was affected
    grant_id UUID REFERENCES consent.consent_grants(grant_id),
    token_id UUID REFERENCES consent.capability_tokens(token_id),
    resource_identifier VARCHAR(500),         -- Specific resource accessed

    -- Context
    scopes TEXT[],                            -- Scopes involved
    purpose TEXT,                             -- Purpose of access
    client_context JSONB DEFAULT '{}'::jsonb,

    -- Security context
    client_ip INET,
    user_agent TEXT,
    session_id VARCHAR(100),

    -- Timing
    event_at TIMESTAMPTZ DEFAULT NOW(),
    processing_time_ms NUMERIC(8,3),          -- Performance tracking

    -- Result
    success BOOLEAN NOT NULL,
    error_message TEXT,

    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Privacy: hash sensitive data
    resource_hash VARCHAR(64)                 -- Hashed resource ID for privacy
);

-- Indexes for performance
CREATE INDEX services_name_idx ON consent.services (service_name);
CREATE INDEX services_trusted_idx ON consent.services (trusted) WHERE trusted = TRUE;

CREATE INDEX scopes_service_idx ON consent.scopes (service_id);
CREATE INDEX scopes_name_idx ON consent.scopes (scope_name);
CREATE INDEX scopes_level_idx ON consent.scopes (scope_level);
CREATE INDEX scopes_parent_idx ON consent.scopes (parent_scope_id) WHERE parent_scope_id IS NOT NULL;

CREATE INDEX resources_service_idx ON consent.resources (service_id);
CREATE INDEX resources_type_idx ON consent.resources (resource_type);
CREATE INDEX resources_owner_idx ON consent.resources (owner_lid);
CREATE INDEX resources_sensitivity_idx ON consent.resources (sensitivity);

CREATE INDEX grants_user_idx ON consent.consent_grants (user_lid);
CREATE INDEX grants_service_idx ON consent.consent_grants (service_id);
CREATE INDEX grants_status_idx ON consent.consent_grants (status);
CREATE INDEX grants_expires_idx ON consent.consent_grants (expires_at);
CREATE INDEX grants_granted_at_idx ON consent.consent_grants (granted_at DESC);

CREATE INDEX tokens_grant_idx ON consent.capability_tokens (grant_id);
CREATE INDEX tokens_hash_idx ON consent.capability_tokens (token_hash);
CREATE INDEX tokens_status_idx ON consent.capability_tokens (status);
CREATE INDEX tokens_expires_idx ON consent.capability_tokens (expires_at);
CREATE INDEX tokens_client_idx ON consent.capability_tokens (client_ip, client_fingerprint);

CREATE INDEX audit_user_idx ON consent.audit_log (user_lid);
CREATE INDEX audit_event_type_idx ON consent.audit_log (event_type);
CREATE INDEX audit_service_idx ON consent.audit_log (service_name);
CREATE INDEX audit_time_idx ON consent.audit_log (event_at DESC);
CREATE INDEX audit_success_idx ON consent.audit_log (success);

-- GIN indexes for JSON fields
CREATE INDEX grants_context_gin_idx ON consent.consent_grants USING GIN (client_context);
CREATE INDEX resources_metadata_gin_idx ON consent.resources USING GIN (metadata);
CREATE INDEX audit_metadata_gin_idx ON consent.audit_log USING GIN (metadata);

-- Performance monitoring view
CREATE VIEW consent.performance_stats AS
SELECT
    event_type,
    COUNT(*) as event_count,
    ROUND(AVG(processing_time_ms)::numeric, 2) as avg_time_ms,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY processing_time_ms)::numeric, 2) as p95_time_ms,
    ROUND(PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY processing_time_ms)::numeric, 2) as p99_time_ms,
    SUM(CASE WHEN success THEN 1 ELSE 0 END)::float / COUNT(*) * 100 as success_rate_pct
FROM consent.audit_log
WHERE processing_time_ms IS NOT NULL
  AND event_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type;

-- Active grants summary view (for user ledger)
CREATE VIEW consent.active_grants_summary AS
SELECT
    cg.user_lid,
    s.service_name,
    cg.purpose,
    cg.granted_at,
    cg.expires_at,
    cg.last_used_at,
    cg.use_count,
    cg.resource_pattern,
    array_agg(sc.scope_name ORDER BY sc.scope_name) as granted_scopes,
    COUNT(ct.token_id) as active_tokens,
    cg.status,
    cg.grant_id
FROM consent.consent_grants cg
JOIN consent.services s ON cg.service_id = s.service_id
LEFT JOIN consent.scopes sc ON sc.scope_id = ANY(cg.scope_ids)
LEFT JOIN consent.capability_tokens ct ON ct.grant_id = cg.grant_id AND ct.status = 'active'
WHERE cg.status = 'active'
GROUP BY cg.grant_id, cg.user_lid, s.service_name, cg.purpose, cg.granted_at,
         cg.expires_at, cg.last_used_at, cg.use_count, cg.resource_pattern, cg.status;

-- Seed data: core services and scopes
INSERT INTO consent.services (service_name, description, max_scope_level, trusted) VALUES
    ('gmail', 'Gmail email service', 'content', TRUE),
    ('drive', 'Google Drive file storage', 'content', TRUE),
    ('dropbox', 'Dropbox file storage', 'content', TRUE),
    ('icloud', 'Apple iCloud storage', 'content', TRUE),
    ('github', 'GitHub code repository', 'content', TRUE),
    ('studio', 'LUKHAS Studio interface', 'admin', TRUE);

-- Gmail scopes (metadata-first design)
INSERT INTO consent.scopes (service_id, scope_name, scope_level, description, default_ttl_minutes, requires_elevation) VALUES
    ((SELECT service_id FROM consent.services WHERE service_name = 'gmail'), 'email.read.headers', 'metadata', 'Read email headers (from, to, subject, date)', 240, FALSE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'gmail'), 'email.read.content', 'content', 'Read full email content and attachments', 30, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'gmail'), 'email.send', 'content', 'Send emails on behalf of user', 15, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'gmail'), 'email.delete', 'admin', 'Delete emails permanently', 5, TRUE);

-- Drive scopes (metadata-first design)
INSERT INTO consent.scopes (service_id, scope_name, scope_level, description, default_ttl_minutes, requires_elevation) VALUES
    ((SELECT service_id FROM consent.services WHERE service_name = 'drive'), 'files.list.metadata', 'metadata', 'List files with metadata only (name, size, modified)', 120, FALSE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'drive'), 'files.read.content', 'content', 'Download and read file content', 30, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'drive'), 'files.write', 'content', 'Create and modify files', 30, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'drive'), 'files.move', 'content', 'Move and organize files', 15, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'drive'), 'files.share', 'admin', 'Change sharing permissions', 5, TRUE);

-- Dropbox scopes
INSERT INTO consent.scopes (service_id, scope_name, scope_level, description, default_ttl_minutes, requires_elevation) VALUES
    ((SELECT service_id FROM consent.services WHERE service_name = 'dropbox'), 'files.list.metadata', 'metadata', 'List files with metadata only', 120, FALSE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'dropbox'), 'files.read.content', 'content', 'Download file content', 30, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'dropbox'), 'files.write', 'content', 'Upload and modify files', 30, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'dropbox'), 'files.move', 'content', 'Move files and folders', 15, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'dropbox'), 'files.share', 'admin', 'Create and manage shared links', 5, TRUE);

-- Studio scopes (administrative interface)
INSERT INTO consent.scopes (service_id, scope_name, scope_level, description, default_ttl_minutes, requires_elevation) VALUES
    ((SELECT service_id FROM consent.services WHERE service_name = 'studio'), 'consent.read', 'metadata', 'Read consent grants and activity', 480, FALSE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'studio'), 'consent.revoke', 'admin', 'Revoke consent grants', 60, TRUE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'studio'), 'profile.read', 'metadata', 'Read user profile information', 480, FALSE),
    ((SELECT service_id FROM consent.services WHERE service_name = 'studio'), 'profile.write', 'content', 'Update user profile', 30, TRUE);

-- Helper functions for consent operations

-- Function to grant consent and return grant ID
CREATE OR REPLACE FUNCTION consent.grant_consent(
    p_user_lid VARCHAR(100),
    p_service_name VARCHAR(100),
    p_scope_names VARCHAR(100)[],
    p_purpose TEXT,
    p_ttl_minutes INTEGER DEFAULT 60,
    p_resource_pattern VARCHAR(500) DEFAULT NULL,
    p_client_ip INET DEFAULT NULL,
    p_client_context JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID AS $$
DECLARE
    v_service_id UUID;
    v_scope_ids UUID[];
    v_grant_id UUID;
    v_expires_at TIMESTAMPTZ;
    scope_name VARCHAR(100);
BEGIN
    -- Get service ID
    SELECT service_id INTO v_service_id
    FROM consent.services
    WHERE service_name = p_service_name;

    IF v_service_id IS NULL THEN
        RAISE EXCEPTION 'Service not found: %', p_service_name;
    END IF;

    -- Convert scope names to IDs
    v_scope_ids := ARRAY[]::UUID[];
    FOREACH scope_name IN ARRAY p_scope_names
    LOOP
        v_scope_ids := v_scope_ids || (
            SELECT scope_id
            FROM consent.scopes
            WHERE service_id = v_service_id AND scope_name = p_scope_names[1]
        );
    END LOOP;

    IF array_length(v_scope_ids, 1) = 0 THEN
        RAISE EXCEPTION 'No valid scopes found for service %', p_service_name;
    END IF;

    -- Calculate expiry
    v_expires_at := NOW() + (p_ttl_minutes || ' minutes')::INTERVAL;

    -- Create grant
    INSERT INTO consent.consent_grants (
        user_lid, service_id, scope_ids, resource_pattern, purpose,
        expires_at, client_context, granted_from_ip
    ) VALUES (
        p_user_lid, v_service_id, v_scope_ids, p_resource_pattern, p_purpose,
        v_expires_at, p_client_context, p_client_ip
    ) RETURNING grant_id INTO v_grant_id;

    -- Log the grant
    INSERT INTO consent.audit_log (
        event_type, user_lid, service_name, grant_id,
        scopes, purpose, client_ip, success
    ) VALUES (
        'grant', p_user_lid, p_service_name, v_grant_id,
        p_scope_names, p_purpose, p_client_ip, TRUE
    );

    RETURN v_grant_id;
END;
$$ LANGUAGE plpgsql;

-- Function to revoke consent
CREATE OR REPLACE FUNCTION consent.revoke_consent(
    p_user_lid VARCHAR(100),
    p_grant_id UUID DEFAULT NULL,
    p_service_name VARCHAR(100) DEFAULT NULL,
    p_scope_names VARCHAR(100)[] DEFAULT NULL,
    p_revoke_reason TEXT DEFAULT 'User revoked'
)
RETURNS INTEGER AS $$
DECLARE
    v_revoked_count INTEGER := 0;
    grant_record RECORD;
BEGIN
    -- Find matching grants
    FOR grant_record IN
        SELECT cg.grant_id, s.service_name
        FROM consent.consent_grants cg
        JOIN consent.services s ON cg.service_id = s.service_id
        WHERE cg.user_lid = p_user_lid
          AND cg.status = 'active'
          AND (p_grant_id IS NULL OR cg.grant_id = p_grant_id)
          AND (p_service_name IS NULL OR s.service_name = p_service_name)
    LOOP
        -- Revoke the grant
        UPDATE consent.consent_grants
        SET status = 'revoked',
            revoked_at = NOW(),
            revoked_by = p_user_lid,
            revoke_reason = p_revoke_reason
        WHERE grant_id = grant_record.grant_id;

        -- Revoke associated tokens
        UPDATE consent.capability_tokens
        SET status = 'revoked',
            revoked_at = NOW(),
            revoke_reason = p_revoke_reason
        WHERE grant_id = grant_record.grant_id
          AND status = 'active';

        -- Log the revocation
        INSERT INTO consent.audit_log (
            event_type, user_lid, service_name, grant_id,
            purpose, success
        ) VALUES (
            'revoke', p_user_lid, grant_record.service_name, grant_record.grant_id,
            p_revoke_reason, TRUE
        );

        v_revoked_count := v_revoked_count + 1;
    END LOOP;

    RETURN v_revoked_count;
END;
$$ LANGUAGE plpgsql;

-- Function to cleanup expired grants and tokens
CREATE OR REPLACE FUNCTION consent.cleanup_expired()
RETURNS TABLE(expired_grants INTEGER, expired_tokens INTEGER) AS $$
DECLARE
    v_expired_grants INTEGER;
    v_expired_tokens INTEGER;
BEGIN
    -- Update expired grants
    UPDATE consent.consent_grants
    SET status = 'expired'
    WHERE status = 'active'
      AND expires_at < NOW();
    GET DIAGNOSTICS v_expired_grants = ROW_COUNT;

    -- Update expired tokens
    UPDATE consent.capability_tokens
    SET status = 'expired'
    WHERE status = 'active'
      AND expires_at < NOW();
    GET DIAGNOSTICS v_expired_tokens = ROW_COUNT;

    RETURN QUERY SELECT v_expired_grants, v_expired_tokens;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT USAGE ON SCHEMA consent TO PUBLIC;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA consent TO PUBLIC;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA consent TO PUBLIC;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA consent TO PUBLIC;

-- Summary
SELECT 'LUKHAS Consent Graph Schema Created' as status,
       COUNT(*) as services_seeded,
       (SELECT COUNT(*) FROM consent.scopes) as scopes_created
FROM consent.services;
