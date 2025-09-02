-- LUKHAS Data Protection Service Schema
-- Implements persistent storage for data protection policies, keys, and history.

CREATE SCHEMA IF NOT EXISTS protection;

-- Protection Policies table
CREATE TABLE protection.policies (
    policy_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    data_types TEXT[],
    protection_level VARCHAR(50),
    encryption_required BOOLEAN,
    encryption_type VARCHAR(50),
    key_rotation_days INTEGER,
    anonymization_methods TEXT[],
    retain_utility BOOLEAN,
    authorized_roles TEXT[],
    audit_required BOOLEAN,
    gdpr_article_25 BOOLEAN,
    gdpr_article_32 BOOLEAN,
    cache_encrypted BOOLEAN,
    background_processing BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    version VARCHAR(50)
);

-- Encryption Keys table
CREATE TABLE protection.encryption_keys (
    key_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    key_type VARCHAR(50),
    algorithm VARCHAR(50),
    key_size INTEGER,
    created_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    rotation_count INTEGER,
    status VARCHAR(50),
    key_material BYTEA,
    public_key BYTEA,
    salt BYTEA,
    iterations INTEGER,
    authorized_users TEXT[],
    authorized_systems TEXT[],
    identity_context JSONB,
    consciousness_binding BOOLEAN,
    guardian_approval BOOLEAN
);

-- Protection History table
CREATE TABLE protection.history (
    operation_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    original_size INTEGER,
    protected_size INTEGER,
    protection_level VARCHAR(50),
    methods_applied TEXT[],
    processing_time REAL,
    cpu_usage REAL,
    memory_usage REAL,
    encryption_key_id UUID,
    anonymization_score REAL,
    utility_preserved REAL,
    is_reversible BOOLEAN,
    recovery_key_id UUID,
    applied_at TIMESTAMPTZ,
    applied_by VARCHAR(100),
    user_lid VARCHAR(100),
    audit_trail TEXT[],
    identity_verified BOOLEAN,
    consciousness_level VARCHAR(50),
    guardian_approved BOOLEAN
);

-- Business Associate Agreements table
CREATE TABLE protection.baas (
    baa_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    business_associate_name VARCHAR(255) NOT NULL,
    agreement_date DATE NOT NULL,
    expiry_date DATE,
    agreement_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'active'
);
