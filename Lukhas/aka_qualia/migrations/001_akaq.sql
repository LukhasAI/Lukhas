-- AkaQualia Wave C Schema Migration
-- WAVE_C.md lines 203-235
-- Database schema for akaq_scene and akaq_glyph tables

-- =====================================================
-- Scene Storage Table
-- =====================================================

CREATE TABLE IF NOT EXISTS akaq_scene (
    -- Primary identification
    scene_id TEXT PRIMARY KEY,              -- ULID for distributed consistency
    user_id TEXT NOT NULL,                  -- User identifier (privacy hashed in production)

    -- Temporal tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    timestamp_raw REAL NOT NULL,            -- Original timestamp from PhenomenalScene

    -- Configuration versioning
    cfg_version TEXT NOT NULL DEFAULT 'wave_c_v1.0.0',

    -- Core phenomenological data
    proto_tone REAL NOT NULL,               -- ProtoQualia.tone [-1.0, 1.0]
    proto_arousal REAL NOT NULL,            -- ProtoQualia.arousal [0.0, 1.0]
    proto_clarity REAL NOT NULL,            -- ProtoQualia.clarity [0.0, 1.0]
    proto_embodiment REAL NOT NULL,         -- ProtoQualia.embodiment [0.0, 1.0]
    proto_colorfield TEXT NOT NULL,         -- ProtoQualia.colorfield
    proto_temporal_feel TEXT NOT NULL,      -- ProtoQualia.temporal_feel enum
    proto_agency_feel TEXT NOT NULL,        -- ProtoQualia.agency_feel enum
    proto_narrative_gravity REAL NOT NULL,  -- ProtoQualia.narrative_gravity [0.0, 1.0]

    -- Scene context
    subject TEXT NOT NULL,                  -- Scene.subject
    object TEXT NOT NULL,                   -- Scene.object
    context_json TEXT NOT NULL,             -- Scene.context as JSON
    transform_chain_json TEXT NOT NULL,     -- Scene.transform_chain as JSON

    -- Risk assessment
    risk_score REAL NOT NULL,               -- RiskProfile.score [0.0, 1.0]
    risk_reasons_json TEXT NOT NULL,        -- RiskProfile.reasons as JSON
    risk_severity TEXT NOT NULL,            -- RiskProfile.severity enum

    -- Regulation policy
    policy_json TEXT NOT NULL,              -- Complete RegulationPolicy as JSON

    -- Processing metrics
    metrics_json TEXT NOT NULL,             -- Complete Metrics as JSON

    -- Consciousness signature for integrity
    consciousness_signature TEXT,           -- Hash of consciousness elements

    -- GDPR compliance
    privacy_level INTEGER DEFAULT 1,       -- 1=standard, 2=sensitive, 3=highly_sensitive
    retention_until TIMESTAMP WITH TIME ZONE, -- Auto-deletion timestamp

    -- Indexing for performance
    created_index TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Glyph Storage Table
-- =====================================================

CREATE TABLE IF NOT EXISTS akaq_glyph (
    -- Primary identification
    glyph_id TEXT PRIMARY KEY,              -- ULID for distributed consistency
    scene_id TEXT NOT NULL,                 -- Foreign key to akaq_scene

    -- Glyph core data
    glyph_key TEXT NOT NULL,                -- PhenomenalGlyph.key (normalized)
    glyph_attrs_json TEXT NOT NULL,         -- PhenomenalGlyph.attrs as JSON

    -- Derived analytics (for fast querying)
    priority REAL,                          -- Computed glyph priority [0.0, 1.0]
    triggers_json TEXT,                     -- Trigger conditions that fired

    -- Temporal tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint
    FOREIGN KEY (scene_id) REFERENCES akaq_scene(scene_id) ON DELETE CASCADE
);

-- =====================================================
-- Performance Indexes
-- =====================================================

-- User-based querying (most common)
CREATE INDEX IF NOT EXISTS idx_akaq_scene_user_created
ON akaq_scene(user_id, created_at DESC);

-- Glyph key analysis
CREATE INDEX IF NOT EXISTS idx_akaq_glyph_key_scene
ON akaq_glyph(glyph_key, scene_id);

-- Scene lookup by consciousness metrics (for drift analysis)
CREATE INDEX IF NOT EXISTS idx_akaq_scene_consciousness
ON akaq_scene(user_id, proto_tone, proto_arousal, created_at DESC);

-- Risk-based filtering
CREATE INDEX IF NOT EXISTS idx_akaq_scene_risk
ON akaq_scene(user_id, risk_score DESC, risk_severity);

-- GDPR compliance queries
CREATE INDEX IF NOT EXISTS idx_akaq_scene_retention
ON akaq_scene(retention_until)
WHERE retention_until IS NOT NULL;

-- Glyph priority analysis
CREATE INDEX IF NOT EXISTS idx_akaq_glyph_priority
ON akaq_glyph(priority DESC, created_at DESC);

-- =====================================================
-- GDPR Compliance Functions
-- =====================================================

-- Function to anonymize user data (for right to erasure)
CREATE OR REPLACE FUNCTION anonymize_user_scenes(target_user_id TEXT)
RETURNS INTEGER AS $$
DECLARE
    affected_rows INTEGER;
BEGIN
    -- Replace user_id with anonymized version
    UPDATE akaq_scene
    SET user_id = 'ANONYMIZED_' || SUBSTRING(MD5(user_id || CURRENT_TIMESTAMP::TEXT), 1, 8),
        subject = 'ANONYMIZED',
        object = 'ANONYMIZED',
        context_json = '{}',
        consciousness_signature = NULL
    WHERE user_id = target_user_id;

    GET DIAGNOSTICS affected_rows = ROW_COUNT;
    RETURN affected_rows;
END;
$$ LANGUAGE plpgsql;

-- Function to delete expired scenes (for data retention)
CREATE OR REPLACE FUNCTION cleanup_expired_scenes()
RETURNS INTEGER AS $$
DECLARE
    deleted_rows INTEGER;
BEGIN
    DELETE FROM akaq_scene
    WHERE retention_until IS NOT NULL
    AND retention_until < CURRENT_TIMESTAMP;

    GET DIAGNOSTICS deleted_rows = ROW_COUNT;
    RETURN deleted_rows;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Views for Analytics
-- =====================================================

-- View for consciousness drift analysis
CREATE OR REPLACE VIEW consciousness_drift_analysis AS
SELECT
    s1.user_id,
    s1.scene_id as current_scene,
    s2.scene_id as prev_scene,
    s1.created_at as current_time,
    s2.created_at as prev_time,
    -- Compute drift metrics
    ABS(s1.proto_tone - s2.proto_tone) as tone_drift,
    ABS(s1.proto_arousal - s2.proto_arousal) as arousal_drift,
    ABS(s1.proto_clarity - s2.proto_clarity) as clarity_drift,
    ABS(s1.proto_embodiment - s2.proto_embodiment) as embodiment_drift,
    -- Temporal distance
    EXTRACT(EPOCH FROM (s1.created_at - s2.created_at)) as time_delta_seconds
FROM akaq_scene s1
JOIN akaq_scene s2 ON s1.user_id = s2.user_id
WHERE s1.created_at > s2.created_at
AND s2.created_at = (
    SELECT MAX(created_at)
    FROM akaq_scene s3
    WHERE s3.user_id = s1.user_id
    AND s3.created_at < s1.created_at
);

-- View for glyph frequency analysis
CREATE OR REPLACE VIEW glyph_frequency_stats AS
SELECT
    glyph_key,
    COUNT(*) as frequency,
    AVG(priority) as avg_priority,
    MIN(created_at) as first_seen,
    MAX(created_at) as last_seen,
    COUNT(DISTINCT akaq_glyph.scene_id) as unique_scenes
FROM akaq_glyph
JOIN akaq_scene ON akaq_glyph.scene_id = akaq_scene.scene_id
GROUP BY glyph_key
ORDER BY frequency DESC;

-- =====================================================
-- Migration Metadata
-- =====================================================

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Record this migration
INSERT INTO schema_migrations (version, description)
VALUES ('001_akaq', 'Initial AkaQualia Wave C schema with consciousness tracking and GDPR compliance')
ON CONFLICT (version) DO NOTHING;

-- =====================================================
-- Comments for Documentation
-- =====================================================

COMMENT ON TABLE akaq_scene IS
'Phenomenological scene storage for AkaQualia consciousness system.
Implements Wave C specification with GDPR compliance and consciousness tracking.';

COMMENT ON TABLE akaq_glyph IS
'Symbolic glyph mappings generated from phenomenological scenes.
Supports fast pattern analysis and consciousness archaeology.';

COMMENT ON COLUMN akaq_scene.consciousness_signature IS
'Deterministic hash of consciousness elements for integrity verification';

COMMENT ON COLUMN akaq_scene.retention_until IS
'GDPR retention limit - scenes auto-deleted after this timestamp';

COMMENT ON VIEW consciousness_drift_analysis IS
'Analyzes temporal drift in consciousness states between consecutive scenes';

COMMENT ON VIEW glyph_frequency_stats IS
'Statistical analysis of glyph occurrence patterns for consciousness patterns';
