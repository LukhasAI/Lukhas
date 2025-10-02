-- LUKHAS Audit Trail Schema
-- Minimal JSONB tables for quick persistence
-- Can be replaced with normalized schema later if desired

-- Decision traces
CREATE TABLE IF NOT EXISTS decision_trace (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_decision_trace_user ON decision_trace ((payload->>'user_id'));
CREATE INDEX IF NOT EXISTS idx_decision_trace_session ON decision_trace ((payload->>'session_id'));
CREATE INDEX IF NOT EXISTS idx_decision_trace_created ON decision_trace (created_at DESC);

-- Trace spans
CREATE TABLE IF NOT EXISTS trace_span (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trace_span_trace ON trace_span ((payload->>'trace_id'));
CREATE INDEX IF NOT EXISTS idx_trace_span_module ON trace_span ((payload->>'module'));

-- Evidence links
CREATE TABLE IF NOT EXISTS evidence_link (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_evidence_link_trace ON evidence_link ((payload->>'trace_id'));
CREATE INDEX IF NOT EXISTS idx_evidence_link_span ON evidence_link ((payload->>'span_id'));
CREATE INDEX IF NOT EXISTS idx_evidence_link_scope ON evidence_link ((payload->>'consent_scope'));

-- Governance events
CREATE TABLE IF NOT EXISTS governance_event (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_governance_event_trace ON governance_event ((payload->>'trace_id'));
CREATE INDEX IF NOT EXISTS idx_governance_event_decision ON governance_event ((payload->>'decision'));

-- Feedback events
CREATE TABLE IF NOT EXISTS feedback_event (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  payload JSONB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_event_trace ON feedback_event ((payload->>'trace_id'));
CREATE INDEX IF NOT EXISTS idx_feedback_event_rating ON feedback_event (((payload->>'rating_0_10')::int));

-- Comments
COMMENT ON TABLE decision_trace IS 'Complete decision traces with timing and outcome metadata';
COMMENT ON TABLE trace_span IS 'Individual operation spans within traces';
COMMENT ON TABLE evidence_link IS 'Evidence sources with consent metadata';
COMMENT ON TABLE governance_event IS 'Governance decisions and policy enforcement events';
COMMENT ON TABLE feedback_event IS 'User feedback linked to traces';
