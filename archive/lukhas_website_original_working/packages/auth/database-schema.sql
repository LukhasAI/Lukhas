-- ΛiD Authentication System Database Schema
-- PostgreSQL implementation for production-ready authentication
-- Supports all core authentication features with proper indexing and constraints

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Enum types for better type safety
CREATE TYPE user_tier AS ENUM ('T1', 'T2', 'T3', 'T4', 'T5');
CREATE TYPE user_status AS ENUM ('pending', 'active', 'suspended', 'deleted');
CREATE TYPE device_type AS ENUM ('platform', 'cross-platform', 'mobile', 'desktop', 'unknown');
CREATE TYPE session_status AS ENUM ('active', 'expired', 'revoked');
CREATE TYPE security_event_type AS ENUM (
  'login_attempt', 'login_success', 'login_failure',
  'logout', 'password_change', 'email_change',
  'mfa_enabled', 'mfa_disabled', 'passkey_added', 'passkey_removed',
  'session_created', 'session_expired', 'session_revoked',
  'suspicious_activity', 'account_locked', 'account_unlocked',
  'magic_link_sent', 'magic_link_used', 'rate_limit_hit',
  'token_refresh', 'token_revocation', 'data_export',
  'privacy_setting_change', 'security_alert'
);

-- 1. USERS TABLE
-- Core user information with tier-based access control
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(320) UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  email_verified_at TIMESTAMP WITH TIME ZONE,
  
  -- User tier and status
  tier user_tier NOT NULL DEFAULT 'T1',
  status user_status NOT NULL DEFAULT 'pending',
  
  -- Profile information
  display_name VARCHAR(255),
  given_name VARCHAR(100),
  family_name VARCHAR(100),
  picture_url TEXT,
  locale VARCHAR(10) DEFAULT 'en',
  timezone VARCHAR(50) DEFAULT 'UTC',
  
  -- Password-related (for password-based auth if needed)
  password_hash TEXT, -- bcrypt hash
  password_changed_at TIMESTAMP WITH TIME ZONE,
  password_reset_required BOOLEAN DEFAULT FALSE,
  
  -- Organization membership
  organization_id UUID,
  organization_role VARCHAR(50),
  
  -- Preferences and settings
  preferences JSONB DEFAULT '{}',
  feature_flags JSONB DEFAULT '{}',
  
  -- Audit fields
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_login_at TIMESTAMP WITH TIME ZONE,
  login_count INTEGER DEFAULT 0,
  
  -- Soft delete
  deleted_at TIMESTAMP WITH TIME ZONE,
  
  -- Constraints
  CONSTRAINT users_email_check CHECK (email ~* '^[^@]+@[^@]+\.[^@]+$'),
  CONSTRAINT users_display_name_check CHECK (LENGTH(display_name) >= 1)
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_tier ON users(tier) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_status ON users(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_organization ON users(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login_at);

-- 2. SESSIONS TABLE
-- Active user sessions with device tracking
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_handle_id UUID, -- References device_handles table
  
  -- Session identification
  session_token VARCHAR(255) UNIQUE NOT NULL,
  session_token_hash VARCHAR(64) NOT NULL, -- SHA-256 hash for lookup
  
  -- Session metadata
  status session_status DEFAULT 'active',
  ip_address INET NOT NULL,
  user_agent TEXT,
  
  -- Geolocation (optional)
  country_code VARCHAR(2),
  city VARCHAR(100),
  
  -- Session lifetime
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Session data
  scopes TEXT[] DEFAULT '{}',
  roles TEXT[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  
  -- Revocation tracking
  revoked_at TIMESTAMP WITH TIME ZONE,
  revocation_reason VARCHAR(255),
  
  -- Constraints
  CONSTRAINT sessions_expires_after_created CHECK (expires_at > created_at),
  CONSTRAINT sessions_token_length CHECK (LENGTH(session_token) >= 32)
);

-- Indexes for sessions table
CREATE UNIQUE INDEX idx_sessions_token_hash ON sessions(session_token_hash);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_device_handle ON sessions(device_handle_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_ip_address ON sessions(ip_address);

-- 3. PASSKEYS TABLE
-- WebAuthn credential storage
CREATE TABLE passkeys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- WebAuthn credential data
  credential_id BYTEA UNIQUE NOT NULL,
  credential_id_b64 TEXT UNIQUE NOT NULL, -- Base64url encoded for easy lookup
  public_key BYTEA NOT NULL,
  algorithm INTEGER NOT NULL, -- COSE algorithm identifier
  
  -- User handle for discoverable credentials
  user_handle VARCHAR(255) NOT NULL,
  
  -- Authenticator information
  aaguid UUID, -- Authenticator AAGUID
  device_type device_type DEFAULT 'unknown',
  device_label VARCHAR(255) NOT NULL,
  
  -- WebAuthn flags and counters
  sign_count BIGINT DEFAULT 0,
  uv_required BOOLEAN DEFAULT TRUE, -- User verification required
  rk BOOLEAN DEFAULT TRUE, -- Resident key (discoverable)
  
  -- Transport methods
  transports TEXT[] DEFAULT '{}', -- ['usb', 'nfc', 'ble', 'internal']
  
  -- Attestation data
  attestation_type VARCHAR(20), -- 'none', 'basic', 'self', 'attca'
  attestation_data BYTEA,
  
  -- Backup eligibility and state
  backup_eligible BOOLEAN DEFAULT FALSE,
  backup_state BOOLEAN DEFAULT FALSE,
  
  -- Usage tracking
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_used_at TIMESTAMP WITH TIME ZONE,
  use_count INTEGER DEFAULT 0,
  
  -- Soft delete
  deleted_at TIMESTAMP WITH TIME ZONE,
  
  -- Constraints
  CONSTRAINT passkeys_credential_id_length CHECK (LENGTH(credential_id) >= 16),
  CONSTRAINT passkeys_public_key_length CHECK (LENGTH(public_key) >= 32),
  CONSTRAINT passkeys_device_label_length CHECK (LENGTH(device_label) >= 1)
);

-- Indexes for passkeys table
CREATE UNIQUE INDEX idx_passkeys_credential_id ON passkeys(credential_id) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_passkeys_credential_id_b64 ON passkeys(credential_id_b64) WHERE deleted_at IS NULL;
CREATE INDEX idx_passkeys_user_id ON passkeys(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_passkeys_user_handle ON passkeys(user_handle);
CREATE INDEX idx_passkeys_aaguid ON passkeys(aaguid);
CREATE INDEX idx_passkeys_device_type ON passkeys(device_type);
CREATE INDEX idx_passkeys_created_at ON passkeys(created_at);
CREATE INDEX idx_passkeys_last_used ON passkeys(last_used_at);

-- 4. REFRESH_TOKENS TABLE
-- Refresh token family tracking for secure token rotation
CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_handle_id UUID, -- References device_handles table
  
  -- Refresh token family tracking
  family_id VARCHAR(255) NOT NULL,
  token_hash VARCHAR(64) UNIQUE NOT NULL, -- SHA-256 hash of token
  
  -- Token metadata
  sequence_number INTEGER NOT NULL DEFAULT 1,
  parent_token_id UUID REFERENCES refresh_tokens(id),
  
  -- Lifetime and usage
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  used_at TIMESTAMP WITH TIME ZONE,
  
  -- Security tracking
  ip_address INET NOT NULL,
  user_agent TEXT,
  
  -- Revocation
  revoked_at TIMESTAMP WITH TIME ZONE,
  revocation_reason VARCHAR(255),
  
  -- Metadata
  scopes TEXT[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  
  -- Constraints
  CONSTRAINT refresh_tokens_expires_after_created CHECK (expires_at > created_at),
  CONSTRAINT refresh_tokens_sequence_positive CHECK (sequence_number > 0)
);

-- Indexes for refresh_tokens table
CREATE UNIQUE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_family_id ON refresh_tokens(family_id);
CREATE INDEX idx_refresh_tokens_device_handle ON refresh_tokens(device_handle_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_created_at ON refresh_tokens(created_at);
CREATE INDEX idx_refresh_tokens_parent_token ON refresh_tokens(parent_token_id);

-- 5. DEVICE_HANDLES TABLE
-- Device fingerprinting and binding
CREATE TABLE device_handles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Device identification
  device_id VARCHAR(255) UNIQUE NOT NULL, -- Stable device identifier
  device_fingerprint VARCHAR(64), -- Hash of device characteristics
  
  -- Device metadata
  device_type device_type DEFAULT 'unknown',
  device_name VARCHAR(255), -- User-friendly name
  platform VARCHAR(100),
  browser VARCHAR(100),
  os VARCHAR(100),
  
  -- Network information
  ip_address INET,
  country_code VARCHAR(2),
  city VARCHAR(100),
  
  -- Trust level
  trusted BOOLEAN DEFAULT FALSE,
  trust_score DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
  
  -- Usage tracking
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_seen_ip INET,
  use_count INTEGER DEFAULT 0,
  
  -- Soft delete
  deleted_at TIMESTAMP WITH TIME ZONE,
  
  -- Additional metadata
  metadata JSONB DEFAULT '{}',
  
  -- Constraints
  CONSTRAINT device_handles_device_id_length CHECK (LENGTH(device_id) >= 8),
  CONSTRAINT device_handles_trust_score_range CHECK (trust_score BETWEEN 0.0 AND 1.0)
);

-- Indexes for device_handles table
CREATE UNIQUE INDEX idx_device_handles_device_id ON device_handles(device_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_device_handles_user_id ON device_handles(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_device_handles_fingerprint ON device_handles(device_fingerprint);
CREATE INDEX idx_device_handles_trusted ON device_handles(trusted) WHERE deleted_at IS NULL;
CREATE INDEX idx_device_handles_created_at ON device_handles(created_at);
CREATE INDEX idx_device_handles_last_used ON device_handles(last_used_at);

-- 6. BACKUP_CODES TABLE
-- Recovery codes for account access
CREATE TABLE backup_codes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Code data
  code_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of the code
  code_partial VARCHAR(8) NOT NULL, -- First few chars for user reference
  
  -- Usage tracking
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  used_at TIMESTAMP WITH TIME ZONE,
  
  -- Context when used
  used_ip_address INET,
  used_user_agent TEXT,
  
  -- Constraints
  CONSTRAINT backup_codes_partial_length CHECK (LENGTH(code_partial) = 8)
);

-- Indexes for backup_codes table
CREATE INDEX idx_backup_codes_user_id ON backup_codes(user_id);
CREATE INDEX idx_backup_codes_hash ON backup_codes(code_hash);
CREATE INDEX idx_backup_codes_used_at ON backup_codes(used_at);
CREATE INDEX idx_backup_codes_created_at ON backup_codes(created_at);

-- 7. SECURITY_EVENTS TABLE
-- Comprehensive security audit log
CREATE TABLE security_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
  
  -- Event classification
  event_type security_event_type NOT NULL,
  event_category VARCHAR(50), -- 'auth', 'session', 'security', 'privacy'
  severity VARCHAR(20) DEFAULT 'info', -- 'info', 'warning', 'error', 'critical'
  
  -- Event details
  description TEXT,
  result VARCHAR(20), -- 'success', 'failure', 'blocked'
  error_code VARCHAR(50),
  
  -- Context information
  ip_address INET,
  user_agent TEXT,
  country_code VARCHAR(2),
  city VARCHAR(100),
  
  -- Request details
  endpoint VARCHAR(255),
  method VARCHAR(10),
  status_code INTEGER,
  
  -- Device and session context
  device_handle_id UUID REFERENCES device_handles(id) ON DELETE SET NULL,
  device_fingerprint VARCHAR(64),
  
  -- Risk assessment
  risk_score DECIMAL(3,2), -- 0.0 to 1.0
  risk_factors TEXT[],
  
  -- Timing
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Additional data
  metadata JSONB DEFAULT '{}',
  
  -- Data retention
  expires_at TIMESTAMP WITH TIME ZONE,
  
  -- Constraints
  CONSTRAINT security_events_risk_score_range CHECK (risk_score IS NULL OR risk_score BETWEEN 0.0 AND 1.0)
);

-- Indexes for security_events table
CREATE INDEX idx_security_events_user_id ON security_events(user_id);
CREATE INDEX idx_security_events_session_id ON security_events(session_id);
CREATE INDEX idx_security_events_type ON security_events(event_type);
CREATE INDEX idx_security_events_category ON security_events(event_category);
CREATE INDEX idx_security_events_severity ON security_events(severity);
CREATE INDEX idx_security_events_result ON security_events(result);
CREATE INDEX idx_security_events_ip_address ON security_events(ip_address);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);
CREATE INDEX idx_security_events_event_timestamp ON security_events(event_timestamp);
CREATE INDEX idx_security_events_risk_score ON security_events(risk_score) WHERE risk_score IS NOT NULL;
CREATE INDEX idx_security_events_expires_at ON security_events(expires_at) WHERE expires_at IS NOT NULL;

-- Composite indexes for common queries
CREATE INDEX idx_security_events_user_type_created ON security_events(user_id, event_type, created_at);
CREATE INDEX idx_security_events_ip_type_created ON security_events(ip_address, event_type, created_at);

-- Additional tables for enhanced functionality

-- EMAIL_VERIFICATION_TOKENS
-- Temporary tokens for email verification
CREATE TABLE email_verification_tokens (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  email VARCHAR(320) NOT NULL,
  token_hash VARCHAR(64) UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  used_at TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT email_verification_expires_after_created CHECK (expires_at > created_at)
);

CREATE INDEX idx_email_verification_tokens_hash ON email_verification_tokens(token_hash);
CREATE INDEX idx_email_verification_tokens_user_id ON email_verification_tokens(user_id);
CREATE INDEX idx_email_verification_tokens_expires_at ON email_verification_tokens(expires_at);

-- RATE_LIMIT_ENTRIES
-- Rate limiting state (can be moved to Redis in production)
CREATE TABLE rate_limit_entries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  key_hash VARCHAR(64) UNIQUE NOT NULL,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  
  -- Rate limit counters
  count INTEGER DEFAULT 0,
  daily_count INTEGER DEFAULT 0,
  
  -- Reset times
  reset_time TIMESTAMP WITH TIME ZONE NOT NULL,
  daily_reset_time TIMESTAMP WITH TIME ZONE NOT NULL,
  
  -- Block status
  blocked BOOLEAN DEFAULT FALSE,
  block_expires_at TIMESTAMP WITH TIME ZONE,
  
  -- Metadata
  tier user_tier,
  endpoint VARCHAR(255),
  ip_address INET,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_rate_limit_entries_key_hash ON rate_limit_entries(key_hash);
CREATE INDEX idx_rate_limit_entries_user_id ON rate_limit_entries(user_id);
CREATE INDEX idx_rate_limit_entries_reset_time ON rate_limit_entries(reset_time);
CREATE INDEX idx_rate_limit_entries_blocked ON rate_limit_entries(blocked) WHERE blocked = TRUE;

-- Functions and Triggers

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at trigger to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rate_limit_entries_updated_at BEFORE UPDATE ON rate_limit_entries
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up expired tokens and sessions
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS INTEGER AS $$
DECLARE
  cleanup_count INTEGER := 0;
BEGIN
  -- Clean up expired sessions
  DELETE FROM sessions WHERE expires_at < NOW() - INTERVAL '7 days';
  GET DIAGNOSTICS cleanup_count = ROW_COUNT;
  
  -- Clean up expired refresh tokens
  DELETE FROM refresh_tokens WHERE expires_at < NOW() - INTERVAL '7 days';
  
  -- Clean up expired email verification tokens
  DELETE FROM email_verification_tokens WHERE expires_at < NOW();
  
  -- Clean up expired rate limit entries
  DELETE FROM rate_limit_entries WHERE reset_time < NOW() - INTERVAL '1 day' AND NOT blocked;
  
  -- Clean up old security events (based on expires_at)
  DELETE FROM security_events WHERE expires_at IS NOT NULL AND expires_at < NOW();
  
  RETURN cleanup_count;
END;
$$ LANGUAGE plpgsql;

-- Views for common queries

-- Active sessions view
CREATE VIEW active_sessions AS
SELECT 
  s.*,
  u.email,
  u.tier,
  u.display_name,
  dh.device_name,
  dh.trusted
FROM sessions s
JOIN users u ON s.user_id = u.id
LEFT JOIN device_handles dh ON s.device_handle_id = dh.id
WHERE s.status = 'active' 
  AND s.expires_at > NOW()
  AND u.deleted_at IS NULL;

-- User security summary view
CREATE VIEW user_security_summary AS
SELECT 
  u.id,
  u.email,
  u.tier,
  u.status,
  COUNT(DISTINCT s.id) FILTER (WHERE s.status = 'active' AND s.expires_at > NOW()) as active_sessions,
  COUNT(DISTINCT p.id) FILTER (WHERE p.deleted_at IS NULL) as passkey_count,
  COUNT(DISTINCT dh.id) FILTER (WHERE dh.deleted_at IS NULL) as device_count,
  COUNT(DISTINCT bc.id) FILTER (WHERE bc.used_at IS NULL) as unused_backup_codes,
  u.last_login_at,
  u.login_count
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN passkeys p ON u.id = p.user_id
LEFT JOIN device_handles dh ON u.id = dh.user_id
LEFT JOIN backup_codes bc ON u.id = bc.user_id
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.email, u.tier, u.status, u.last_login_at, u.login_count;

-- Grant appropriate permissions (adjust for your application user)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO lukhas_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO lukhas_app;

-- Insert default data if needed
-- This would typically be done by your application initialization

COMMENT ON TABLE users IS 'Core user accounts with tier-based access control';
COMMENT ON TABLE sessions IS 'Active user sessions with device tracking';
COMMENT ON TABLE passkeys IS 'WebAuthn/FIDO2 passkey credentials';
COMMENT ON TABLE refresh_tokens IS 'Refresh tokens with family tracking for secure rotation';
COMMENT ON TABLE device_handles IS 'Device fingerprinting and trust management';
COMMENT ON TABLE backup_codes IS 'Recovery codes for account access';
COMMENT ON TABLE security_events IS 'Comprehensive security audit log';

COMMENT ON COLUMN users.tier IS 'User tier: T1 (Explorer), T2 (Builder), T3 (Studio), T4 (Enterprise), T5 (Core Team)';
COMMENT ON COLUMN sessions.session_token_hash IS 'SHA-256 hash of session token for secure lookup';
COMMENT ON COLUMN passkeys.credential_id IS 'WebAuthn credential ID (raw bytes)';
COMMENT ON COLUMN refresh_tokens.family_id IS 'Refresh token family identifier for tracking rotations';
COMMENT ON COLUMN device_handles.trust_score IS 'Device trust score from 0.0 (untrusted) to 1.0 (fully trusted)';
COMMENT ON COLUMN security_events.risk_score IS 'Event risk score from 0.0 (low risk) to 1.0 (high risk)';

-- Performance monitoring query (for development/monitoring)
/*
-- Query to check table sizes and index usage
SELECT 
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats 
WHERE schemaname = 'public' 
  AND tablename IN ('users', 'sessions', 'passkeys', 'refresh_tokens', 'device_handles', 'backup_codes', 'security_events')
ORDER BY tablename, attname;
*/