---
status: wip
type: documentation
---
You are in the Lukhas repo. Execute the following plan idempotently (re-run safe), making small atomic commits per concern. Do NOT touch runtime code under lukhas/ or candidate/.

GOALS
- Prep the repo for a neutral + strategic deep search.
- Add schemas, provenance updater, SBOM, SLO stubs.
- Add CI gates (audit-validate, contracts-smoke).
- Enforce CI safety (SELF_HEALING_DISABLED, would-change artifacts).
- Seed Tier-1 scope for MATRIZ conversion.

PHASE 0 — Preflight
1) Ensure Python venv + tools:
   - Create .venv if missing; install: jsonschema, ruamel.yaml, cyclonedx-bom, pipdeptree, pytest, coverage
2) Create (if missing) dirs:
   - tools/ci, schemas, reports/{sbom,slo,audit,deep_search}, reports/matriz/traces, AUDIT, AUDIT/NODE_CONTRACTS, tests/{smoke,matriz}
3) Write/append git-safe .gitkeep as needed.

PHASE 1 — Minimal JSON Schemas
Create two minimal schemas referenced by the JSONs (extend later):
- schemas/architecture_master.schema.json
- schemas/dependency_matrix.schema.json
Both should require: schema_version, provenance, and (respectively) lanes / module_dependency_matrix. Allow additionalProperties: true.

PHASE 2 — Provenance Updater + Integrity Check
Create tools/ci/update_and_validate_json.py that:
- Loads these JSONs if present:
  LUKHAS_ARCHITECTURE_MASTER.json,
  DEPENDENCY_MATRIX.json,
  SECURITY_ARCHITECTURE.json,
  CONSCIOUSNESS_METRICS.json,
  PERFORMANCE_BASELINES.json,
  BUSINESS_METRICS.json,
  EVOLUTION_ROADMAP.json,
  VISUALIZATION_CONFIG.json
- For each file: set/merge top-level "provenance" with:
  { git_sha, timestamp_utc, scope_hash, generated_by: {tool:"claude-code", model:"Opus 4.1"} }
  and set "schema_url" to corresponding schema when applicable.
- Build set of canonical module_uids from LUKHAS_ARCHITECTURE_MASTER.json (lanes.*.modules[].module_uid if present, else lane+name).
- Validate DEPENDENCY_MATRIX.json keys are known module_uids; fail with a clear error list if unknown.
- Validate instances against schemas using jsonschema. Exit non-zero on validation failure.

Commit: chore(audit): add schemas + provenance updater + integrity checks

PHASE 3 — SBOM + Deps Snapshots + SLO stubs
1) Generate CycloneDX SBOM to reports/sbom/cyclonedx.json (fall back gracefully).
2) Export pip dependency tree to reports/sbom/pipdeps.json.
3) Create reports/slo/slo_stub.json with one stub per module_uid in DEPENDENCY_MATRIX:
   {latency_p95_ms:"TBD", error_rate_pct:"TBD", availability_pct:"TBD"}.

Commit: chore(audit): add SBOM, deps snapshot, and SLO stubs

PHASE 4 — Makefile Helpers
Add (if missing) targets:
- audit-validate: runs tools/ci/update_and_validate_json.py
- sbom: runs cyclonedx-bom to refresh reports/sbom/cyclonedx.json
Keep existing content; append safely.

Commit: chore(audit): add Makefile targets (audit-validate, sbom)

PHASE 5 — CI Gates (GitHub Actions)
Edit .github/workflows/ci.yml (create if missing) to include:
- job audit-validate (runs before pre-commit/lint):
  * checkout, setup-python 3.11
  * pip install jsonschema cyclonedx-bom pipdeptree
  * python tools/ci/update_and_validate_json.py
  * cyclonedx-bom -o reports/sbom/cyclonedx.json || true
- job contracts-smoke (after pre-commit), that:
  * checkout + Python 3.11
  * pip install pytest
  * pytest -q -k "contracts or golden"
- Ensure existing jobs list audit-validate in needs for pre-commit/lint (don’t remove current needs).
- Add env guard for any dashboard/self-healing jobs:
  SELF_HEALING_DISABLED=1 (default), and prefer invoking dashboard with:
  --mode single --ci-mode --generate-artifacts (no writes).

Commit: ci(audit): add audit-validate + contracts-smoke gates and CI safety guard

PHASE 6 — Tier-1 Focus & Stubs
1) Create AUDIT/TIER1.txt with these module_uids (one per line; edit if file exists):
   lukhas.memory
   lukhas.consciousness
   lukhas.orchestration
   lukhas.api
   lukhas.identity
2) For each Tier-1 uid, create AUDIT/NODE_CONTRACTS/<uid>.json if missing, with fields:
   {
     "module_uid": "...",
     "version": "v1",
     "inputs": [],
     "outputs": [],
     "trace": {"propagate": true, "id_key": "trace_id"},
     "glyph": {"enabled": true, "version": "TBD"},
     "backpressure": {"strategy":"bounded","max_inflight":128},
     "timeouts_ms": 200,
     "invariants": ["idempotent writes by trace_id"],
     "errors": [{"code":"RETRYABLE","retriable":true},{"code":"NOT_FOUND","retriable":false}],
     "provenance": { "git_sha":"<fill>", "timestamp_utc":"<now>", "generated_by":{"tool":"claude-code"}}
   }
3) Golden traces: if reports/matriz/traces/ empty, create one sample JSON trace file (valid JSON with {trace_id,timestamp,events:[]}) and add tests:
   - tests/smoke/test_health.py (assert True)
   - tests/matriz/test_golden_placeholder.py (assert at least one golden trace exists)

Commit: feat(matriz): seed Tier-1 contracts + golden trace placeholders

PHASE 7 — Auditor Entry & Index (if missing)
- AUDIT/INDEX.md with pointers to:
  reports/deep_search/PY_INDEX.txt,
  reports/deep_search/IMPORT_SAMPLES.txt,
  reports/deep_search/CANDIDATE_USED_BY_LUKHAS.txt,
  reports/deep_search/WRONG_CORE_IMPORTS.txt,
  AUDIT/CODE_SAMPLES.txt
- Generate PY_INDEX.txt and IMPORT_SAMPLES.txt for {lukhas,MATRIZ,ops,AUDIT} (skip .venv, .git).
- Cross-lane scans:
  * lukhas/** importing candidate/** → CANDIDATE_USED_BY_LUKHAS.txt
  * wrong core imports → WRONG_CORE_IMPORTS.txt
- Random 25-file sample → AUDIT/CODE_SAMPLES.txt
- Make targets audit-nav (echo commit/start) and audit-scan (list deep_search files).

Commit: chore(audit): add auditor entrypoint + indexes + cross-lane scans

PHASE 8 — Run & Show Results
1) Run: make audit-validate
2) Run: make sbom
3) Print a short summary:
   - Which JSONs validated
   - Any missing module_uids / referential errors
   - SBOM generated: yes/no
   - SLO stubs written: count of modules
   - Tier-1 contracts present: N/5
4) If any step fails, stop and open a file FIXME.md at repo root with a bullet list of concrete next actions (max 8 bullets), then commit it as docs.

OUTPUT STYLE
- After each phase, show a short unified diff (only changed files).
- Keep commits atomic by phase, as specified.
- If a file already exists with equivalent content, skip and note “already up to date”.
- Echo final checklist with ✅/❌ for: schemas, updater, SBOM, SLO stubs, CI gates, Tier-1, auditor entry.
