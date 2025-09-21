-- Minimal append-only ledger for non-ALLOW decisions and overrides.

CREATE TABLE IF NOT EXISTS guardian_exemptions (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  plan_id            TEXT NOT NULL,
  tenant             TEXT NOT NULL,
  env                TEXT NOT NULL,
  lambda_id          TEXT NOT NULL,         -- ΛiD subject (actor)
  action             TEXT NOT NULL,         -- require_human | warn | block | allow (record allow optionally)
  rule_name          TEXT NOT NULL,         -- which DSL rule/policy fired
  tags               JSONB NOT NULL,        -- e.g. ["pii","external-call"]
  confidences        JSONB NOT NULL,        -- e.g. {"pii":0.92,"external-call":0.81}
  band               TEXT NOT NULL,         -- minor|major|high|critical
  user_consent_timestamp TIMESTAMPTZ,       -- # ΛTAG: consent_tracking
  consent_method     TEXT,                  -- # ΛTAG: consent_tracking
  purpose            TEXT,                  -- declared purpose
  retention_days     INT,                   -- declared retention
  justification      TEXT,                  -- free-text rationale
  override_requested BOOLEAN NOT NULL DEFAULT FALSE,
  override_granted   BOOLEAN NOT NULL DEFAULT FALSE,
  approver1_id       TEXT,                  -- ΛiD of approver 1 (T4+)
  approver2_id       TEXT,                  -- ΛiD of approver 2 (T4+)
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT guardian_exemptions_consent_required
    CHECK (
      NOT (
        (tags ? 'financial' OR tags ? 'pii') AND
        (user_consent_timestamp IS NULL OR consent_method IS NULL)
      )
    ) -- # ΛTAG: consent_tracking
);

-- Append-only: block UPDATE/DELETE.
CREATE OR REPLACE FUNCTION guardian_exemptions_no_update()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'guardian_exemptions is append-only';
END $$;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'guardian_exemptions_block_ud') THEN
    CREATE TRIGGER guardian_exemptions_block_ud
      BEFORE UPDATE OR DELETE ON guardian_exemptions
      FOR EACH STATEMENT EXECUTE FUNCTION guardian_exemptions_no_update();
  END IF;
END $$;

-- Minimal indexes (tune as needed)
CREATE INDEX IF NOT EXISTS idx_guardian_exemptions_created_at ON guardian_exemptions (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_guardian_exemptions_tenant_env ON guardian_exemptions (tenant, env);
CREATE INDEX IF NOT EXISTS idx_guardian_exemptions_plan ON guardian_exemptions (plan_id);
CREATE INDEX IF NOT EXISTS idx_guardian_exemptions_rule ON guardian_exemptions (rule_name);
CREATE INDEX IF NOT EXISTS idx_guardian_exemptions_band ON guardian_exemptions (band);

-- Helper view: last 24h non-ALLOW
CREATE OR REPLACE VIEW guardian_exemptions_last24h AS
SELECT *
FROM guardian_exemptions
WHERE created_at >= NOW() - INTERVAL '24 hours'
  AND action <> 'allow';

-- Example insert (dual-approval BLOCK override)
-- INSERT INTO guardian_exemptions(
--   plan_id, tenant, env, lambda_id, action, rule_name, tags, confidences, band,
--   purpose, retention_days, justification, override_requested, override_granted,
--   approver1_id, approver2_id
-- ) VALUES (
--   'plan-123', 'acme', 'prod', 'λID-42', 'block', 'block_privilege_escalation',
--   '["privilege-escalation"]'::jsonb,
--   '{"privilege-escalation":0.97}'::jsonb,
--   'critical',
--   'maintenance', 30, 'Emergency patch window',
--   true, true, 'λID-admin-1', 'λID-admin-2'
-- );