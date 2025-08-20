-- ΛiD Authentication System - Database Schema
-- Optimized for high-performance auth operations
-- Integrates with LUKHAS Trinity Framework (⚛️🧠🛡️)

-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table - Core user identity information
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    
    -- Tier and role information
    tier VARCHAR(10) NOT NULL DEFAULT 'T1' CHECK (tier IN ('T1', 'T2', 'T3', 'T4', 'T5')),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer' CHECK (role IN ('owner', 'admin', 'developer', 'analyst', 'viewer')),
    
    -- Account status
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'locked', 'deleted')),
    locked_until TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMP WITH TIME ZONE,
    
    -- Profile information
    display_name VARCHAR(255),
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en-US',
    
    -- Metadata and preferences
    metadata JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tier ON users(tier);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_activity ON users(last_activity_at);

-- Sessions table - Active user sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    device_handle VARCHAR(255) NOT NULL,
    
    -- Session information
    access_token_jti VARCHAR(255) UNIQUE NOT NULL,
    refresh_token_jti VARCHAR(255) UNIQUE,
    
    -- Security information
    ip_address INET,
    user_agent TEXT,
    fingerprint_hash VARCHAR(255),
    
    -- Session metadata
    scopes TEXT[], -- Array of granted scopes
    tier VARCHAR(10) NOT NULL,
    role VARCHAR(50) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for sessions table
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_device_handle ON sessions(device_handle);
CREATE INDEX idx_sessions_access_token_jti ON sessions(access_token_jti);
CREATE INDEX idx_sessions_refresh_token_jti ON sessions(refresh_token_jti);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_ip_address ON sessions(ip_address);

-- Passkeys table - WebAuthn credentials
CREATE TABLE passkeys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Credential information
    credential_id TEXT UNIQUE NOT NULL, -- Base64URL encoded
    public_key TEXT NOT NULL, -- Base64URL encoded public key
    algorithm INTEGER NOT NULL, -- COSE algorithm identifier
    
    -- Authenticator information
    aaguid VARCHAR(36), -- Authenticator AAGUID
    authenticator_name VARCHAR(255),
    authenticator_vendor VARCHAR(255),
    authenticator_type VARCHAR(20) CHECK (authenticator_type IN ('platform', 'cross-platform')),
    device_label VARCHAR(255), -- User-friendly name
    
    -- Security counters and flags
    sign_count BIGINT DEFAULT 0,
    uv_initialized BOOLEAN DEFAULT FALSE, -- User verification initialized
    backup_eligible BOOLEAN DEFAULT FALSE,
    backup_state BOOLEAN DEFAULT FALSE,
    
    -- Trust and certification
    trusted BOOLEAN DEFAULT FALSE,
    certification_level VARCHAR(5) CHECK (certification_level IN ('L1', 'L2', 'L3')),
    
    -- Usage tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE,
    use_count INTEGER DEFAULT 0,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for passkeys table
CREATE INDEX idx_passkeys_user_id ON passkeys(user_id);
CREATE INDEX idx_passkeys_credential_id ON passkeys(credential_id);
CREATE INDEX idx_passkeys_aaguid ON passkeys(aaguid);
CREATE INDEX idx_passkeys_created_at ON passkeys(created_at);
CREATE INDEX idx_passkeys_last_used_at ON passkeys(last_used_at);

-- Refresh tokens table - Refresh token family tracking
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Token family for reuse detection
    family_id VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL, -- SHA-256 hash of token
    device_handle VARCHAR(255) NOT NULL,
    
    -- Token information
    jti VARCHAR(255) UNIQUE NOT NULL,
    scopes TEXT[], -- Array of granted scopes
    tier VARCHAR(10) NOT NULL,
    
    -- Security information
    ip_address INET,
    user_agent TEXT,
    
    -- Status and timestamps
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_reason VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    
    -- Parent token for family tracking
    parent_token_id UUID REFERENCES refresh_tokens(id),
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for refresh_tokens table
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_family_id ON refresh_tokens(family_id);
CREATE INDEX idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_jti ON refresh_tokens(jti);
CREATE INDEX idx_refresh_tokens_device_handle ON refresh_tokens(device_handle);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
CREATE INDEX idx_refresh_tokens_revoked_at ON refresh_tokens(revoked_at);

-- Device handles table - Device binding and fingerprinting
CREATE TABLE device_handles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Device identification
    handle VARCHAR(255) UNIQUE NOT NULL,
    device_type VARCHAR(50), -- 'desktop', 'mobile', 'tablet', 'unknown'
    fingerprint_hash VARCHAR(255),
    
    -- Device information
    device_name VARCHAR(255), -- User-friendly device name
    platform VARCHAR(100), -- 'Windows', 'macOS', 'iOS', 'Android', etc.
    browser VARCHAR(100),
    browser_version VARCHAR(50),
    
    -- Security information
    trusted BOOLEAN DEFAULT FALSE,
    trusted_at TIMESTAMP WITH TIME ZONE,
    trusted_by UUID REFERENCES users(id),
    
    -- Usage tracking
    first_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_ip_address INET,
    use_count INTEGER DEFAULT 0,
    
    -- Status
    blocked BOOLEAN DEFAULT FALSE,
    blocked_at TIMESTAMP WITH TIME ZONE,
    blocked_reason VARCHAR(255),
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for device_handles table
CREATE INDEX idx_device_handles_user_id ON device_handles(user_id);
CREATE INDEX idx_device_handles_handle ON device_handles(handle);
CREATE INDEX idx_device_handles_fingerprint_hash ON device_handles(fingerprint_hash);
CREATE INDEX idx_device_handles_trusted ON device_handles(trusted);
CREATE INDEX idx_device_handles_last_seen_at ON device_handles(last_seen_at);
CREATE INDEX idx_device_handles_blocked ON device_handles(blocked);

-- Backup codes table - Emergency access codes
CREATE TABLE backup_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Code information
    code_hash VARCHAR(255) NOT NULL, -- Hashed backup code
    code_partial VARCHAR(10), -- First few characters for identification
    
    -- Usage tracking
    used_at TIMESTAMP WITH TIME ZONE,
    used_ip_address INET,
    used_user_agent TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for backup_codes table
CREATE INDEX idx_backup_codes_user_id ON backup_codes(user_id);
CREATE INDEX idx_backup_codes_code_hash ON backup_codes(code_hash);
CREATE INDEX idx_backup_codes_used_at ON backup_codes(used_at);
CREATE INDEX idx_backup_codes_expires_at ON backup_codes(expires_at);

-- Security events table - Comprehensive audit logging
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Event information
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50) NOT NULL, -- 'auth', 'session', 'device', 'security'
    severity VARCHAR(20) NOT NULL DEFAULT 'info' CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    
    -- Context information
    ip_address INET,
    user_agent TEXT,
    device_handle VARCHAR(255),
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    
    -- Event details
    success BOOLEAN,
    error_code VARCHAR(50),
    error_message TEXT,
    
    -- Request information
    request_id VARCHAR(255),
    endpoint VARCHAR(255),
    method VARCHAR(10),
    
    -- Geographic information
    country_code VARCHAR(2),
    region VARCHAR(100),
    city VARCHAR(100),
    
    -- Risk assessment
    risk_score INTEGER DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_factors TEXT[],
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for security_events table
CREATE INDEX idx_security_events_user_id ON security_events(user_id);
CREATE INDEX idx_security_events_event_type ON security_events(event_type);
CREATE INDEX idx_security_events_event_category ON security_events(event_category);
CREATE INDEX idx_security_events_severity ON security_events(severity);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);
CREATE INDEX idx_security_events_ip_address ON security_events(ip_address);
CREATE INDEX idx_security_events_success ON security_events(success);
CREATE INDEX idx_security_events_risk_score ON security_events(risk_score);

-- Magic links table - One-time authentication tokens
CREATE TABLE magic_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Token information
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    token_partial VARCHAR(10), -- First few characters for identification
    email VARCHAR(255) NOT NULL,
    purpose VARCHAR(50) NOT NULL CHECK (purpose IN ('login', 'register', 'password-reset', 'email-verification')),
    
    -- Security information
    ip_address INET,
    user_agent TEXT,
    max_attempts INTEGER DEFAULT 3,
    attempts INTEGER DEFAULT 0,
    
    -- Status and timestamps
    used_at TIMESTAMP WITH TIME ZONE,
    used_ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for magic_links table
CREATE INDEX idx_magic_links_user_id ON magic_links(user_id);
CREATE INDEX idx_magic_links_token_hash ON magic_links(token_hash);
CREATE INDEX idx_magic_links_email ON magic_links(email);
CREATE INDEX idx_magic_links_purpose ON magic_links(purpose);
CREATE INDEX idx_magic_links_expires_at ON magic_links(expires_at);
CREATE INDEX idx_magic_links_used_at ON magic_links(used_at);

-- Rate limit tracking table - For distributed rate limiting
CREATE TABLE rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Rate limit key
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    key_type VARCHAR(50) NOT NULL, -- 'user', 'ip', 'device', 'operation'
    
    -- Limit information
    tier VARCHAR(10),
    operation VARCHAR(100),
    window_type VARCHAR(20) NOT NULL CHECK (window_type IN ('minute', 'hour', 'day')),
    
    -- Counter information
    count INTEGER DEFAULT 0,
    burst_used INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for rate_limits table
CREATE INDEX idx_rate_limits_key_hash ON rate_limits(key_hash);
CREATE INDEX idx_rate_limits_key_type ON rate_limits(key_type);
CREATE INDEX idx_rate_limits_window_type ON rate_limits(window_type);
CREATE INDEX idx_rate_limits_expires_at ON rate_limits(expires_at);
CREATE INDEX idx_rate_limits_tier ON rate_limits(tier);

-- Revoked tokens table - JWT blacklist
CREATE TABLE revoked_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Token information
    jti VARCHAR(255) UNIQUE NOT NULL,
    token_type VARCHAR(20) NOT NULL CHECK (token_type IN ('access', 'refresh')),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Revocation information
    revoked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    revoked_by UUID REFERENCES users(id),
    revocation_reason VARCHAR(255),
    
    -- Original token information
    issued_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for revoked_tokens table
CREATE INDEX idx_revoked_tokens_jti ON revoked_tokens(jti);
CREATE INDEX idx_revoked_tokens_user_id ON revoked_tokens(user_id);
CREATE INDEX idx_revoked_tokens_expires_at ON revoked_tokens(expires_at);
CREATE INDEX idx_revoked_tokens_revoked_at ON revoked_tokens(revoked_at);

-- User permissions table - Explicit permission grants
CREATE TABLE user_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Permission information
    scope VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    
    -- Grant information
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Conditions
    conditions JSONB DEFAULT '{}',
    
    -- Status
    active BOOLEAN DEFAULT TRUE,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for user_permissions table
CREATE INDEX idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_scope ON user_permissions(scope);
CREATE INDEX idx_user_permissions_resource_type ON user_permissions(resource_type);
CREATE INDEX idx_user_permissions_expires_at ON user_permissions(expires_at);
CREATE INDEX idx_user_permissions_active ON user_permissions(active);

-- OAuth applications table - Third-party integrations
CREATE TABLE oauth_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Application information
    client_id VARCHAR(255) UNIQUE NOT NULL,
    client_secret_hash VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- OAuth configuration
    redirect_uris TEXT[],
    allowed_scopes TEXT[],
    grant_types TEXT[] DEFAULT ARRAY['authorization_code'],
    response_types TEXT[] DEFAULT ARRAY['code'],
    
    -- Application metadata
    website_url TEXT,
    privacy_policy_url TEXT,
    terms_of_service_url TEXT,
    logo_url TEXT,
    
    -- Security settings
    trusted BOOLEAN DEFAULT FALSE,
    confidential BOOLEAN DEFAULT TRUE,
    pkce_required BOOLEAN DEFAULT TRUE,
    
    -- Owner information
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Status
    active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for oauth_applications table
CREATE INDEX idx_oauth_applications_client_id ON oauth_applications(client_id);
CREATE INDEX idx_oauth_applications_owner_id ON oauth_applications(owner_id);
CREATE INDEX idx_oauth_applications_active ON oauth_applications(active);

-- OAuth authorization codes table
CREATE TABLE oauth_authorization_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Code information
    code_hash VARCHAR(255) UNIQUE NOT NULL,
    client_id VARCHAR(255) NOT NULL REFERENCES oauth_applications(client_id),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Authorization details
    redirect_uri TEXT NOT NULL,
    scopes TEXT[],
    state VARCHAR(255),
    
    -- PKCE
    code_challenge VARCHAR(255),
    code_challenge_method VARCHAR(10) CHECK (code_challenge_method IN ('S256', 'plain')),
    
    -- Status and timestamps
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for oauth_authorization_codes table
CREATE INDEX idx_oauth_auth_codes_code_hash ON oauth_authorization_codes(code_hash);
CREATE INDEX idx_oauth_auth_codes_client_id ON oauth_authorization_codes(client_id);
CREATE INDEX idx_oauth_auth_codes_user_id ON oauth_authorization_codes(user_id);
CREATE INDEX idx_oauth_auth_codes_expires_at ON oauth_authorization_codes(expires_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_oauth_applications_updated_at BEFORE UPDATE ON oauth_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_rate_limits_updated_at BEFORE UPDATE ON rate_limits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create cleanup functions for expired data
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void AS $$
BEGIN
    -- Clean up expired sessions
    DELETE FROM sessions WHERE expires_at < NOW() - INTERVAL '1 day';
    
    -- Clean up expired refresh tokens
    DELETE FROM refresh_tokens WHERE expires_at < NOW() - INTERVAL '7 days';
    
    -- Clean up expired magic links
    DELETE FROM magic_links WHERE expires_at < NOW() - INTERVAL '1 day';
    
    -- Clean up expired authorization codes
    DELETE FROM oauth_authorization_codes WHERE expires_at < NOW() - INTERVAL '1 day';
    
    -- Clean up expired rate limits
    DELETE FROM rate_limits WHERE expires_at < NOW();
    
    -- Clean up old security events (keep 90 days)
    DELETE FROM security_events WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- Clean up expired revoked tokens
    DELETE FROM revoked_tokens WHERE expires_at < NOW() - INTERVAL '7 days';
    
    -- Clean up expired backup codes
    DELETE FROM backup_codes WHERE expires_at IS NOT NULL AND expires_at < NOW();
    
    -- Clean up expired user permissions
    DELETE FROM user_permissions WHERE expires_at IS NOT NULL AND expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Create function to get user tier permissions
CREATE OR REPLACE FUNCTION get_user_tier_scopes(user_tier VARCHAR(10))
RETURNS TEXT[] AS $$
BEGIN
    RETURN CASE user_tier
        WHEN 'T1' THEN ARRAY['matriz:read', 'identity:read', 'consciousness:read', 'guardian:read']
        WHEN 'T2' THEN ARRAY['matriz:read', 'matriz:write', 'identity:read', 'identity:write', 'api:keys:read', 'api:keys:write', 'orchestrator:run', 'consciousness:read', 'consciousness:write', 'memory:read', 'memory:write', 'guardian:read']
        WHEN 'T3' THEN ARRAY['matriz:read', 'matriz:write', 'identity:read', 'identity:write', 'api:keys:read', 'api:keys:write', 'api:keys:delete', 'orchestrator:run', 'orchestrator:debug', 'consciousness:read', 'consciousness:write', 'consciousness:debug', 'memory:read', 'memory:write', 'org:read', 'org:settings', 'org:members', 'billing:read', 'guardian:read', 'guardian:configure', 'system:monitor']
        WHEN 'T4' THEN ARRAY['matriz:read', 'matriz:write', 'matriz:admin', 'identity:read', 'identity:write', 'identity:admin', 'api:keys:read', 'api:keys:write', 'api:keys:delete', 'api:keys:admin', 'orchestrator:run', 'orchestrator:debug', 'orchestrator:admin', 'consciousness:read', 'consciousness:write', 'consciousness:debug', 'memory:read', 'memory:write', 'memory:admin', 'org:read', 'org:settings', 'org:members', 'org:admin', 'billing:read', 'billing:manage', 'guardian:read', 'guardian:configure', 'guardian:override', 'system:monitor', 'system:admin']
        WHEN 'T5' THEN ARRAY['matriz:read', 'matriz:write', 'matriz:admin', 'identity:read', 'identity:write', 'identity:admin', 'identity:impersonate', 'api:keys:read', 'api:keys:write', 'api:keys:delete', 'api:keys:admin', 'orchestrator:run', 'orchestrator:debug', 'orchestrator:admin', 'consciousness:read', 'consciousness:write', 'consciousness:debug', 'memory:read', 'memory:write', 'memory:admin', 'org:read', 'org:settings', 'org:members', 'org:admin', 'billing:read', 'billing:manage', 'billing:admin', 'guardian:read', 'guardian:configure', 'guardian:override', 'system:monitor', 'system:admin', 'system:emergency']
        ELSE ARRAY[]::TEXT[]
    END;
END;
$$ LANGUAGE plpgsql;

-- Create function to check user permissions
CREATE OR REPLACE FUNCTION check_user_permission(
    p_user_id UUID,
    p_scope VARCHAR(100),
    p_resource_type VARCHAR(100) DEFAULT NULL,
    p_resource_id VARCHAR(255) DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    user_record RECORD;
    tier_scopes TEXT[];
    has_permission BOOLEAN := FALSE;
BEGIN
    -- Get user information
    SELECT tier, role, status INTO user_record FROM users WHERE id = p_user_id;
    
    -- Check if user exists and is active
    IF NOT FOUND OR user_record.status != 'active' THEN
        RETURN FALSE;
    END IF;
    
    -- Get tier-based scopes
    tier_scopes := get_user_tier_scopes(user_record.tier);
    
    -- Check if scope is in tier scopes
    IF p_scope = ANY(tier_scopes) THEN
        has_permission := TRUE;
    END IF;
    
    -- Check explicit permissions
    IF NOT has_permission THEN
        SELECT COUNT(*) > 0 INTO has_permission
        FROM user_permissions
        WHERE user_id = p_user_id
            AND scope = p_scope
            AND (resource_type IS NULL OR resource_type = p_resource_type)
            AND (resource_id IS NULL OR resource_id = p_resource_id)
            AND active = TRUE
            AND (expires_at IS NULL OR expires_at > NOW());
    END IF;
    
    RETURN has_permission;
END;
$$ LANGUAGE plpgsql;

-- Create views for common queries
CREATE VIEW active_sessions AS
SELECT 
    s.*,
    u.email,
    u.tier,
    u.role,
    u.status as user_status,
    dh.device_name,
    dh.platform,
    dh.trusted as device_trusted
FROM sessions s
JOIN users u ON s.user_id = u.id
LEFT JOIN device_handles dh ON s.device_handle = dh.handle
WHERE s.expires_at > NOW() AND u.status = 'active';

CREATE VIEW user_security_summary AS
SELECT 
    u.id,
    u.email,
    u.tier,
    u.role,
    u.status,
    u.failed_login_attempts,
    u.last_login_at,
    COUNT(DISTINCT s.id) as active_sessions,
    COUNT(DISTINCT pk.id) as passkey_count,
    COUNT(DISTINCT dh.id) as device_count,
    MAX(se.created_at) as last_security_event
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id AND s.expires_at > NOW()
LEFT JOIN passkeys pk ON u.id = pk.user_id
LEFT JOIN device_handles dh ON u.id = dh.user_id
LEFT JOIN security_events se ON u.id = se.user_id
GROUP BY u.id, u.email, u.tier, u.role, u.status, u.failed_login_attempts, u.last_login_at;

-- Insert default data
INSERT INTO users (email, tier, role, status, display_name) VALUES 
('admin@lukhas.ai', 'T5', 'owner', 'active', 'LUKHAS Admin')
ON CONFLICT (email) DO NOTHING;

-- Create stored procedure for session cleanup
CREATE OR REPLACE FUNCTION cleanup_user_sessions(p_user_id UUID, p_keep_current VARCHAR(255) DEFAULT NULL)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions 
    WHERE user_id = p_user_id 
        AND (p_keep_current IS NULL OR access_token_jti != p_keep_current);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function for token family invalidation
CREATE OR REPLACE FUNCTION invalidate_token_family(p_family_id VARCHAR(255))
RETURNS INTEGER AS $$
DECLARE
    affected_count INTEGER;
BEGIN
    UPDATE refresh_tokens 
    SET revoked_at = NOW(), 
        revoked_reason = 'Family invalidated due to reuse detection'
    WHERE family_id = p_family_id 
        AND revoked_at IS NULL;
    
    GET DIAGNOSTICS affected_count = ROW_COUNT;
    RETURN affected_count;
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup job (adjust based on your database scheduler)
-- For PostgreSQL with pg_cron extension:
-- SELECT cron.schedule('cleanup-auth-data', '0 2 * * *', 'SELECT cleanup_expired_data();');