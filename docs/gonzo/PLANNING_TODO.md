BRIEF FOR CLAUDE CODE

Objective: Allocate and drive all pending TODOs from:
	•	TODO/critical_todos.md
	•	TODO/high_todos.md
	•	TODO/med_todos.md
	•	TODO/low_todos.md

…across Jules-01..10, Codex-01..10, Copilot, and Claude Code, with end-to-end synchronization (enumeration → assignment → execution → verification → reporting), while updating agents.md and guarding against duplication, regressions, or phantom completions.

⸻

0) Operating Principles (T4 lens)
	•	Skepticism first: never trust a TODO file without checking the codebase and git history. Treat lists as claims, not facts.
	•	Prioritize truth over speed: status = proven by grep/tests/CI, not by wishful comments.
	•	Atomic commits, observable deltas: every change must be traceable to a TaskID with reproducible verification.
	•	Batch size discipline: aim 25–30 items/agent/cycle (bump to 40 only for mechanical edits).
	•	No silent merges: PRs without TaskID, scope, and checks are blocked.

⸻

1) One-time Setup (required before assignment)
	1.	Create a run manifest
	•	Path: .lukhas_runs/<YYYY-MM-DD>/manifest.json
	•	Contains a snapshot of all TODOs (see schema below), tool versions, commit hash, and agent roster.
	2.	Standardize IDs
	•	TaskID format: TODO-{PRIORITY}-{MODULE}-{HASH8} (example: TODO-CRIT-IDENTITY-1a2b3c4d).
	•	BatchID format: BATCH-{AGENT}-{DATE}-{SEQ} (example: BATCH-JULES-03-2025-09-15-01).
	3.	Agent Roster & Capabilities (update agents.md)
	•	Record strengths, limits, and ownership zones. Example:
	•	Jules-01..03 → Identity/Governance/Guardian (complex, cross-module)
	•	Jules-04..05 → Orchestration/Consciousness (complex logic)
	•	Jules-06..08 → QI/Entropy/QRG scaffolding (experimental, guarded)
	•	Jules-09..10 → Dashboards/Monitoring/Docs wiring
	•	Codex-01..06 → mechanical fixes (imports, undefined names, renames, docstring enforcement)
	•	Codex-07..10 → codegen stubs, template wiring, perf micro-tweaks
	•	Copilot → inline refactors & quick fix-ups inside dev loops (never primary owner)
	•	Claude Code → allocator, verifier, integrator, reviewer of risky changes

⸻

2) Enumeration (prove ground truth)

Goal: build a canonical list of ALL actionable TODOs, then reconcile with code.

Steps:
	1.	Parse all four TODO markdown files into a structured list.
	2.	Cross-check live codebase for:
	•	TODO, FIXME, HACK, # TODO: markers
	•	known error tags (e.g., F821, import errors)
	3.	Cross-check recent PRs/commits for “Completed/Implemented” claims and confirm with grep/tests.
	4.	De-duplicate (title, file path, line proximity, semantic similarity).
	5.	Create manifest.json with the schema below.

Manifest Schema (excerpt):

{
  "run_id": "LUKHAS-RUN-2025-09-15-A",
  "created_at": "2025-09-15T09:00:00Z",
  "root_sha": "<git_head_sha>",
  "todos": [
    {
      "task_id": "TODO-CRIT-IDENTITY-1a2b3c4d",
      "priority": "critical|high|med|low",
      "title": "Implement persistent storage logic",
      "file": "candidate/governance/identity/core/trace/activity_logger.py",
      "line_hint": 225,
      "module": "identity/trace",
      "trinity": "Identity|Guardian|Consciousness|null",
      "status": "open|completed|blocked|wip",
      "source": "critical_todos.md|high_todos.md|med_todos.md|low_todos.md|code_scan",
      "evidence": {
        "grep": "matched string or none",
        "last_commit": "sha or null"
      },
      "acceptance": [
        "unit tests cover happy/failure paths",
        "integration path exercised",
        "docs or inline docstring updated"
      ],
      "risk": "low|med|high",
      "est": {
        "type": "mechanical|logic|integration",
        "size": "XS|S|M|L"
      }
    }
  ]
}

Tooling (suggested):
	•	rg -n "TODO|FIXME|HACK" -g '!node_modules'
	•	Python script to parse the 4 markdowns into structured entries and merge with grep results.
	•	Optional: flake8 or ruff scans to pull surfaced errors into the manifest as TODOs (F821, etc.).

⸻

3) Classification & Sizing (turn chaos into queues)
	•	Heuristics:
	•	Mechanical (imports, F821, renames, docstrings) → Codex.
	•	Cross-module logic (Identity, Guardian, Consent/QRG, Tiering) → Jules-01..05.
	•	Consciousness/awareness engines & safety → Jules-04..05 with Claude review.
	•	Dashboards/visuals/tests wiring → Jules-09..10 (Codex can assist).
	•	QI/Entropy/Quantum stubs → Jules-06..08, gated behind feature flags and tests.
	•	Sizing buckets: XS (≤15m), S (≤1h), M (≤3h), L (>3h).
	•	Batch targets: 25–30 tasks per agent per cycle; up to 40 tasks when >80% are mechanical.

⸻

4) Assignment Plan (who does what)

Create per-agent task bundles under .lukhas_runs/<DATE>/batches/:
	•	File: BATCH-JULES-03-2025-09-15-01.json
	•	Fields: batch_id, agent, tasks[], dependencies[], branch_name, checks[].

Branch naming:
	•	feat/jules03/identity-trace-batch01
	•	fix/codex07/f821-governance-batch01

Initial distribution (example):
	•	Critical: 60% Jules, 30% Claude-paired Jules, 10% Codex (only mechanical criticals).
	•	High: 40% Jules, 40% Codex, 20% Copilot assist.
	•	Med/Low: 20% Jules, 60% Codex, 20% Copilot assist.

⸻

5) Execution Protocol (repeatable, verifiable)

For each batch:
	1.	Pre-flight checks
	•	Sync with main → create branch → run poetry install / pip install -e .[dev]
	•	Run ruff/flake8, pytest -q, and any integration smoke tests.
	2.	Apply changes task-by-task:
	•	Each commit = one TaskID (atomic).
	•	Commit message:
feat(trace): Implement persistent storage logic (TODO-CRIT-IDENTITY-1a2b3c4d)
Body: context, approach, tests added/updated, risk notes.
	3.	Self-verification
	•	Re-run checks; update task status to wip → completed with evidence.
	•	Update manifest.json and batch file status fields.
	4.	PR creation
	•	Title: [BATCH] jules03 identity-trace batch01 (25 tasks)
	•	Template includes: BatchID, TaskIDs, test report summary, risk assessment, artifacts.
	5.	Review gates
	•	Claude Code reviews all critical and any Guardian/Identity/Consciousness PRs.
	•	Require green CI; block on failing coverage deltas or missing tests.
	6.	Merge discipline
	•	Squash by TaskID preserved in squash message list.
	•	Post-merge: update agents.md and .lukhas_runs/<DATE>/progress.json.

⸻

6) Synchronization & Source of Truth
	•	agents.md must always reflect:
	•	Ownership map (who owns which module/batch right now)
	•	Active branches per agent
	•	Links to open PRs and last CI status
	•	Batch totals: assigned / completed / blocked
	•	Single truth lives in .lukhas_runs/<DATE>/:
	•	manifest.json (full todo catalog)
	•	batches/*.json (assignments)
	•	progress.json (rollup metrics)
	•	reports/*.md (daily summary, blockers, next actions)

⸻

7) Guardrails (avoid common multi-agent failure modes)
	•	Duplicate work: a task is “locked” when added to an open batch; the allocator refuses to assign it elsewhere.
	•	Bit-rot: batches expire after 72h; if unmerged, rebase or re-plan.
	•	Spec drift: any TODO that lacks an acceptance test must add one or document why (explicit waiver).
	•	Risk gating: QI/cryptography/Guardian safety code must ship behind feature flags + kill switch.
	•	Consistency: Tier boundaries, consent model, and ΛTRACE/ΛTIER references must use the canonical schemas.
	•	Dashboards: must read live stats or stubbed providers (no magic numbers).

⸻

8) Verification Matrix (examples per hotspot)
	•	Identity/Trace:
	•	New persistence layer → integration test writes/reads records; audit chain linking verified via deterministic hash chain.
	•	Consent/Tier:
	•	Load tier boundaries from consent_tiers.json; negative tests for out-of-range; ZK proof stub gated.
	•	Guardian/Ethics:
	•	Safety boundaries reconcile with global ΛTIER; intent analysis integration mocked then real; escalation paths tested.
	•	QI/Entropy/QRG:
	•	Entropy sources mocked; SurfaceCode stubs compile behind flag; replay/session logic has stateful tests.
	•	Dashboards:
	•	Streamlit widgets guarded; undefined refs removed; CI snapshot tests prevent regressions.

⸻

9) Reporting & Telemetry
	•	Daily report → reports/2025-09-15.md:
	•	New TODOs discovered vs. closed
	•	PRs merged / blocked (with reasons)
	•	Coverage delta, lint debt delta
	•	High-risk areas and mitigations
	•	Progress JSON for dashboards:

{
  "date": "2025-09-15",
  "counts": { "critical": {"open": 150, "wip": 40, "done": 32}, "high": {...} },
  "agents": { "jules03": {"assigned": 28, "done": 14}, "codex07": {"assigned": 32, "done": 22} }
}


⸻

10) Concrete Allocation Starter (first sweep)
	•	Jules-01: Identity core (ΛTRACE persistence; audit chain linking) – 25–30
	•	Jules-02: Consent/Scopes (tier boundaries, validation, history → ΛTRACE) – 25–30
	•	Jules-03: SSO/biometrics/symbolic challenge (gated, mocked) – 25
	•	Jules-04: Awareness protocol reconciliation with ΛTIER – 20–25 (complex)
	•	Jules-05: Guardian ethics advanced intent + governance forwarding – 20–25
	•	Jules-06: QRG generator & session replay scaffolding – 25 (flagged)
	•	Jules-07: Wallet/QI bridges (init placeholders, interfaces) – 25 (flagged)
	•	Jules-08: Quantum entropy stubs + interfaces (no prod) – 20–25 (flagged)
	•	Jules-09: Compliance/Guardian dashboards (data wiring) – 25–30
	•	Jules-10: Tests: integration identity imports + e2e glue – 25–30
	•	Codex-01..06: F821/undefined names/imports/renames/docstrings – 6×30–40
	•	Codex-07..10: dashboard widgets, perf micro-tweaks, stub factories – 4×30
	•	Copilot: opportunistic inline fixes in active PRs (never owns a TaskID)
	•	Claude Code: allocator + reviewer for criticals, merges, and weekly re-planning

⸻

11) Minimal Command Playbook (for Claude to run)

# enumerate
rg -n "TODO|FIXME|HACK" -g '!node_modules' > .lukhas_runs/2025-09-15/grep.txt
python tools/ci/build_manifest.py \
  --todo-md TODO/critical_todos.md TODO/high_todos.md TODO/med_todos.md TODO/low_todos.md \
  --grep .lukhas_runs/2025-09-15/grep.txt \
  --out .lukhas_runs/2025-09-15/manifest.json

# split into batches
python tools/ci/split_batches.py \
  --manifest .lukhas_runs/2025-09-15/manifest.json \
  --strategy rules/allocation_rules.yaml \
  --out .lukhas_runs/2025-09-15/batches/

# validate batches & lock tasks
python tools/ci/lock_batches.py --dir .lukhas_runs/2025-09-15/batches/

# run CI locally
ruff check .
pytest -q

(If the helper scripts don’t exist yet, generate them from this spec; keep them simple and pure-Python.)

⸻

12) PR Template (strict)

Title: [BATCH] <agent> <area> <batch> (<N> tasks)

Summary:
- BatchID: <id>
- Agent: <agent>
- Tasks: <TaskID list>
- Modules: <areas>
- Risk: <low/med/high>

Verification:
- Tests: <added/updated list>
- CI: <links>
- Evidence: grep before/after, screenshots if UI
- Flags: <feature_flag_names> with defaults

Notes:
- Dependencies/blocked-by:
- Follow-ups created:


⸻

13) End Conditions (how we know we’re done)
	•	manifest.json has 0 open items (all done or consciously waived with rationale).
	•	agents.md reflects final state (owners, PR links, outcomes).
	•	All critical tasks: tests present, feature flags where appropriate, governance alignment verified.
	•	Daily reports show monotonically decreasing open counts; no “rediscovered” duplicates.

⸻

Final nudge (T4 honesty)
	•	If a TODO can’t be verified in code or tests, it’s not done—no matter what the markdown says.
	•	If two agents can “probably” touch the same file, they will. Lock tasks and expire stale batches.
	•	Don’t fear waiving a TODO with a clear rationale and a scheduled follow-up. Fear merging silent inconsistencies.

⸻
