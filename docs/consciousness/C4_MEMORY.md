---
status: wip
type: documentation
owner: unknown
module: consciousness
redirect: false
moved_to: null
---

Below is the C4: Memory Schema + Client spec—high-verbose, high-technical, ready to implement. It’s storage-agnostic (SQLite dev / Postgres prod), energy-accounting aware, VIVOX-anchored, and GDPR-prudent.

⸻

C4 — Memory Schema + Client (Aka Qualia)

0) Storage targets & capabilities
	•	Dev: SQLite (simple, file-based).
	•	Prod: PostgreSQL ≥14 with JSONB and pgvector (vector type) for fast similarity on PQ.
	•	ID strategy: ULID (time-sortable, collision-resistant) as scene_id.
	•	Determinism handle: store collapse_hash (VIVOX SHA3-256 of z(t)+context) for idempotency.

⸻

1) SQL schema (Postgres)

-- Enable pgvector (prod)
CREATE EXTENSION IF NOT EXISTS vector;

-- Aka Qualia scenes (one row per step)
CREATE TABLE IF NOT EXISTS akaq_scene (
  scene_id        TEXT PRIMARY KEY,                 -- ULID
  user_id         TEXT NOT NULL,
  ts              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  subject         TEXT,
  object          TEXT,
  proto           JSONB NOT NULL,                   -- full ProtoQualia dict
  proto_vec       VECTOR(5),                        -- [tone, arousal, clarity, embodiment, narrative_gravity]
  risk            JSONB NOT NULL,                   -- {score, severity, reasons[]}
  context         JSONB,                            -- sanitized context
  transform_chain JSONB,                            -- [{op, params, before, after, reason, cfg_version}]
  collapse_hash   TEXT,                             -- VIVOX SHA3-256 for idempotency
  drift_phi       DOUBLE PRECISION,
  congruence_index DOUBLE PRECISION,
  neurosis_risk   DOUBLE PRECISION,
  repair_delta    DOUBLE PRECISION,
  sublimation_rate DOUBLE PRECISION,
  affect_energy_before DOUBLE PRECISION,
  affect_energy_after  DOUBLE PRECISION,
  affect_energy_diff   DOUBLE PRECISION,
  cfg_version     TEXT
);

-- Glyphs emitted for the scene (sparse, many-to-one)
CREATE TABLE IF NOT EXISTS akaq_glyph (
  scene_id  TEXT REFERENCES akaq_scene(scene_id) ON DELETE CASCADE,
  key       TEXT NOT NULL,
  attrs     JSONB,
  PRIMARY KEY (scene_id, key)
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_akaq_scene_user_ts ON akaq_scene(user_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_akaq_scene_severity ON akaq_scene((risk->>'severity'));
CREATE INDEX IF NOT EXISTS idx_akaq_scene_collapse ON akaq_scene(collapse_hash);
CREATE INDEX IF NOT EXISTS idx_akaq_scene_drift ON akaq_scene(drift_phi);
CREATE INDEX IF NOT EXISTS idx_akaq_scene_congruence ON akaq_scene(congruence_index);
CREATE INDEX IF NOT EXISTS idx_akaq_glyph_key ON akaq_glyph(key);

-- Vector similarity (prod queries)
-- Example: CREATE INDEX idx_proto_vec_ivff ON akaq_scene USING ivfflat (proto_vec vector_cosine_ops) WITH (lists = 100);

SQLite variant (dev)
	•	Replace JSONB→JSON, drop VECTOR, store proto_vec as 5 comma-separated floats or JSON; emulate with app-side similarity.

⸻

2) Privacy & compliance (GDPR-friendly)
	•	PII avoidance by default: subject, object hashed (SHA3-256 with rotating salt) unless dev mode.
	•	Context sanitization: whitelist keys (e.g., "safe_palette", "approach_avoid_score").
	•	Right to erasure: cascade delete by user_id across akaq_scene and akaq_glyph.
	•	Config-stamped audits: include cfg_version in each transform_chain step for reproducibility.

⸻

3) Python client (storage-agnostic)

candidate/aka_qualia/memory.py

from typing import List, Dict, Any, Optional
import datetime as dt

class AkaqMemory:
    """
    Storage-agnostic memory client.
    Implementations: SqlMemory (SQLite/Postgres), NoopMemory (tests).
    """

    def save(self, *, user_id: str, scene: Dict[str, Any],
             glyphs: List[Dict[str, Any]], policy: Dict[str, Any],
             metrics: Dict[str, Any], cfg_version: str) -> str:
        """Atomically persist scene+glyphs+metrics. Returns scene_id (ULID)."""

    def fetch_prev_scene(self, *, user_id: str, before_ts: Optional[dt.datetime] = None) -> Optional[Dict[str, Any]]:
        """Most recent scene for user strictly before ts (or now)."""

    def history(self, *, user_id: str, limit: int = 50, since: Optional[dt.datetime] = None) -> List[Dict[str, Any]]:
        """Reverse-chronological slice of scenes."""
    
    def search_by_glyph(self, *, user_id: str, key: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Scenes that emitted a given glyph key."""

    def top_drift(self, *, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scenes ordered by drift_phi desc."""

    def delete_user(self, *, user_id: str) -> int:
        """Delete all data for user (rows count)."""

SQL implementation sketch

candidate/aka_qualia/memory_sql.py

import ulid, json, hashlib, math
from .util import to_proto_vec  # returns list[5] in fixed order

class SqlMemory(AkaqMemory):
    def __init__(self, engine, rotate_salt: str, is_prod: bool):
        self.engine = engine
        self.rotate_salt = rotate_salt
        self.is_prod = is_prod

    def _hash_safe(self, s: Optional[str]) -> Optional[str]:
        if not s or not self.is_prod: return s
        h = hashlib.sha3_256()
        h.update((self.rotate_salt + s).encode())
        return h.hexdigest()

    def save(self, *, user_id, scene, glyphs, policy, metrics, cfg_version) -> str:
        sid = ulid.new().str
        subject = self._hash_safe(scene.get("subject"))
        object_ = self._hash_safe(scene.get("object"))
        proto = scene["proto"]
        proto_vec = to_proto_vec(proto)  # [tone, arousal, clarity, embodiment, narrative_gravity]
        collapse_hash = scene.get("collapse_hash")

        with self.engine.begin() as cx:
            cx.execute(
                """
                INSERT INTO akaq_scene(
                    scene_id, user_id, ts, subject, object, proto, proto_vec, risk, context,
                    transform_chain, collapse_hash, drift_phi, congruence_index, neurosis_risk,
                    repair_delta, sublimation_rate, affect_energy_before, affect_energy_after,
                    affect_energy_diff, cfg_version
                ) VALUES (
                    :scene_id, :user_id, NOW(), :subject, :object, :proto::jsonb, :proto_vec, :risk::jsonb, :context::jsonb,
                    :transform_chain::jsonb, :collapse_hash, :drift_phi, :congruence_index, :neurosis_risk,
                    :repair_delta, :sublimation_rate, :E_before, :E_after, :E_diff, :cfg_version
                )
                """,
                {
                    "scene_id": sid,
                    "user_id": user_id,
                    "subject": subject,
                    "object": object_,
                    "proto": json.dumps(proto),
                    "proto_vec": proto_vec,  # with pgvector binding or JSON for SQLite
                    "risk": json.dumps(scene["risk"]),
                    "context": json.dumps(scene.get("context", {})),
                    "transform_chain": json.dumps(scene.get("transform_chain", [])),
                    "collapse_hash": collapse_hash,
                    "drift_phi": metrics["drift_phi"],
                    "congruence_index": metrics["congruence_index"],
                    "neurosis_risk": metrics["neurosis_risk"],
                    "repair_delta": metrics["repair_delta"],
                    "sublimation_rate": metrics["sublimation_rate"],
                    "E_before": metrics.get("affect_energy_before"),
                    "E_after": metrics.get("affect_energy_after"),
                    "E_diff": metrics.get("affect_energy_diff"),
                    "cfg_version": cfg_version,
                },
            )
            for g in glyphs:
                cx.execute(
                    "INSERT INTO akaq_glyph(scene_id, key, attrs) VALUES (:sid, :k, :a::jsonb)",
                    {"sid": sid, "k": g["key"], "a": json.dumps(g.get("attrs", {}))},
                )

        return sid

Idempotency option: add a unique partial index on (user_id, collapse_hash) when collapse hashing is stable per step; on conflict, return existing scene_id.

⸻

4) App-side vector helpers

candidate/aka_qualia/util.py

def to_proto_vec(proto: dict) -> list[float]:
    return [
        float(proto.get("tone", 0.0)),
        float(proto.get("arousal", 0.0)),
        float(proto.get("clarity", 0.0)),
        float(proto.get("embodiment", 0.0)),
        float(proto.get("narrative_gravity", 0.0)),
    ]


⸻

5) AkaQualia → Memory integration (in core.py)
	•	During step() before routing, compute/attach:
	•	affect_energy_before/after, affect_energy_diff
	•	cfg_version (e.g., akaq@0.3.0+ruleset-2025-09-01)
	•	full transform_chain (each op includes cfg_version + why)
	•	Call memory.save(...) in a try/except that increments akaq_memory_writes_total{status="fail"} on error; do not abort the step.

⸻

6) Queries your dashboards/tests will want

6.1 Last N scenes for a user

SELECT ts, proto, risk, drift_phi, congruence_index, neurosis_risk, repair_delta
FROM akaq_scene
WHERE user_id = $1
ORDER BY ts DESC
LIMIT $2;

6.2 Scenes with high drift or high severity

SELECT scene_id, ts, drift_phi, risk->>'severity' AS severity
FROM akaq_scene
WHERE drift_phi >= 0.15 OR (risk->>'severity') IN ('moderate','high')
ORDER BY ts DESC;

6.3 Find scenes that emitted a given glyph

SELECT s.ts, s.scene_id, g.key, g.attrs
FROM akaq_glyph g
JOIN akaq_scene s USING(scene_id)
WHERE s.user_id = $1 AND g.key = $2
ORDER BY s.ts DESC
LIMIT 100;

6.4 Nearest neighbors in PQ space (prod)

-- Input :target_vec ::vector(5)
SELECT scene_id, ts, 1 - (proto_vec <=> :target_vec) AS cosine_sim
FROM akaq_scene
WHERE user_id = $1
ORDER BY proto_vec <=> :target_vec
LIMIT 20;


⸻

7) Retention, rollups, and cost
	•	Hot window: retain full rows for 30–90 days (configurable).
	•	Cold rollup: downsample to daily medians per user: drift_phi, congruence_index, neurosis_risk, repair_delta, sublimation_rate.
	•	Purge: hard-delete beyond retention unless research flag is on and user consent recorded (tie to your TEQ compliance modules).

⸻

8) Config additions

memory:
  driver: "postgres"        # "sqlite" in dev
  dsn: "postgresql://lukhas:***@localhost:5432/lukhas"
  rotate_salt: "RANDOM_ROTATING_SALT"
  retention_days: 60
  rollup_enabled: true
  vector_index: "ivfflat"   # "" to disable
akaq:
  cfg_version: "akaq@0.3.0+ruleset-2025-09-01"


⸻

9) Tests to add
	•	Unit
	•	test_save_and_fetch_prev_scene: correctness and ordering.
	•	test_transform_chain_persists: op list present and ordered.
	•	test_hashing_when_prod: subject/object hashed only in prod.
	•	Contract
	•	test_vector_similarity_query (skipped on SQLite).
	•	test_unique_by_collapse_hash (if idempotency index enabled).
	•	Fault-injection
	•	Simulate DB outage → save() returns after logging failure; step continues.
	•	Corrupt JSON in attrs → save rejected; sanitize upstream.
	•	Performance
	•	Batch save 1k scenes under 2s (local Postgres); p50 insert < 5ms.

⸻

10) CLI tooling

candidate/aka_qualia/tools/migrate.py
candidate/aka_qualia/tools/erase_user.py

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# Apply migrations
python -m candidate.aka_qualia.tools.migrate --dsn postgresql://...

# GDPR erase
python -m candidate.aka_qualia.tools.erase_user --dsn ... --user u123


⸻

11) Acceptance gates for C4
	•	Writes succeed with atomic scene+glyph transaction; retries on transient errors.
	•	fetch_prev_scene() drives drift_phi computation deterministically across restarts.
	•	Vector similarity (prod) returns plausible neighbors; fallback path on SQLite.
	•	Dashboards can drill from drift spikes to their transform_chain with cfg_version.
	•	GDPR erase deletes all rows for a user, verified by count.

⸻

12) PR Task Queue (C4)

PR#C4.1 — Schema & Migrations
	•	Add SQL for Postgres + SQLite fallback; pgvector optional index.

PR#C4.2 — Memory Client (SQL)
	•	Implement SqlMemory with idempotency on (user_id, collapse_hash) (optional).

PR#C4.3 — Core Wiring
	•	Call memory.save(...) from AkaQualia._log() with full metrics and chain.

PR#C4.4 — Tests + Faults
	•	Unit/contract/perf + outage simulation; ensure counters increment.

PR#C4.5 — Ops Docs
	•	README: retention, erase, rollup, index tuning, vector lists parameter.

⸻

Final nudge from the couch

Memory is where psyches go to either crystallize or delude themselves. With this design, Aka Qualia’s recollections become auditable hypotheses—time-stamped, hashed, vectorized. Once C4 is green, we march to C5 observability polish and C6 ablation & ethics finalization. Keep it cold-eyed: the unconscious is clever, but our logs are cleverer.