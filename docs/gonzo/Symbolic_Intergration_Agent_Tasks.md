Symbolic Intergration Agent Tasks
⸻

Global header (paste at the top of any task)

MODE: T4 / 0.01% code surgeon
PRINCIPLES: tiny changes, big leverage; fail closed; explicit invariants; tests-first

REPO ASSUMPTIONS:
- Python services use pytest; JS frontends use vitest/jest if present.
- If a referenced path doesn’t exist, create it with minimal, documented scaffolding.
- Wire new logic behind a feature flag: LUKHAS_EXPERIMENTAL=1.

STYLE:
- Small PR: 1 feature = 1 PR. Conventional commits.
- Add docstring + usage block to each new module (LUKHΛS template).

DEFINITION OF DONE (DoD):
- All new code is unit-tested and documented; CI passes; feature flag default OFF.
- No API/ABI breaks without explicit migration notes.


⸻

Collapse Engine

1) Embedding→Entropy mapping (early drift catch)

TASK: Convert unusual vector embedding shifts into entropy increments for collapse tracking.

EDIT:
- Modify/extend: core/monitoring/collapse_tracker.py
- Add: lukhas/trace/embedding_entropy.py (new)
  - def embedding_entropy_delta(prev_vecs: np.ndarray, curr_vecs: np.ndarray, labels: list[str]) -> float:
    # cluster shift, silhouette drop, center displacement -> mapped to [0,1] entropy delta

INTEGRATIONS:
- Where collapse_tracker computes entropy, add hook:
  delta = embedding_entropy_delta(prev_batch.embeddings, curr_batch.embeddings, curr_batch.symbols)
  entropy += delta

TESTS:
- tests/collapse/test_embedding_entropy.py
  - synthetic clusters; verify higher center shifts ⇒ higher delta; stable clusters ⇒ ~0 delta.

ACCEPTANCE:
- New function covered ≥90%.
- Feature flag toggles the hook on/off.
- No regressions in existing collapse metrics.

REFERENCE: Audit §Collapse Engine, pp.1–2.  [oai_citation:1‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

2) Constraint check before any merge/compression

TASK: Prevent invalid merges with a minimal constraint solver.

EDIT:
- core/symbolic/collapse/collapse_engine.py
  - before merge(consolidate|compress|fuse), call constraint_check(candidate_nodes)
- Add: core/symbolic/constraints/constraint_engine.py (new)
  - def constraint_check(nodes) -> bool:
    # Examples: "distinct_person_ids", "legal_facts_not_unified", "time_order_preserved"

TESTS:
- tests/collapse/test_constraint_merge_guard.py
  - merging nodes with distinct person_id must fail.
  - time-inconsistent history must fail.
  - valid merges pass.

ACCEPTANCE:
- Merge ops abort with explicit error + audit log when constraints fail.
- Constraint rules are config-driven (YAML/JSON in core/symbolic/constraints/rules/).

REFERENCE: Audit §Collapse Engine, pp.1–2.  [oai_citation:2‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

3) Tie collapse outcomes to TraceRepair + edge-case simulator

TASK: Invoke trace_repair_engine post-collapse; expand simulator for multi-collapse scenarios.

EDIT:
- candidate/qi/states/integrity_probe.py
  - after collapse event, call TraceRepairEngine.realign(symbols_changed)
- lukhas/tools/collapse_simulator.py
  - add scenarios combining memory+ethical+identity collapses; concurrency spikes.

TESTS:
- tests/collapse/test_post_collapse_repair.py
  - verify repair invoked when symbol context shifts.
- tests/collapse/test_simulator_edgecases.py
  - ensure no deadlocks; proper logging for compound scenarios.

ACCEPTANCE:
- Repair path executed and logged for ≥1 simulated scenario.
- Simulator can run compound scenarios via CLI (python collapse_simulator.py --compound).

REFERENCE: Audit §Collapse Engine, pp.1–2.  [oai_citation:3‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)


⸻

EQNOX (neural↔symbolic spine)

4) Symbolic Bridge (ground any neural output)

TASK: Bridge raw model outputs to typed symbols; and symbols back to actuator-ready commands.

EDIT:
- Add: core/bridge/symbolic_bridge.py
  - def to_symbol(payload: dict|np.ndarray, modality: str) -> dict: ...
  - def from_symbol(symbol_plan: dict) -> dict: ...
- Touch: candidate/aka_qualia/core.py
  - pipe all sub-symbolic outputs through to_symbol before reasoning.
  - ground plans via from_symbol before execution.

TESTS:
- tests/bridge/test_symbolic_bridge.py
  - round-trip properties; unknown modality -> explicit error.

ACCEPTANCE:
- AkaQualia loop calls bridge in both directions (behind feature flag).
- Typed symbols appear in logs for one existing pathway.

REFERENCE: Audit §EQNOX, p.3.  [oai_citation:4‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

5) Global Constraint Engine (pre‑execution plan verifier)

TASK: Add plan verification via logic constraints (safety, physics, policy).

EDIT:
- core/symbolic/constraints/plan_verifier.py (new)
  - verify(plan: dict) -> (ok: bool, violations: list[str])
- core/orchestration/agent_orchestrator.py
  - before dispatch, require ok=True; else abort with violations.

TESTS:
- tests/constraints/test_plan_verifier.py
  - forbidden action (policy) ⇒ blocked; allowed action ⇒ passes.

ACCEPTANCE:
- One real plan path now verified; violations logged & surfaced to Guardian.

REFERENCE: Audit §EQNOX, p.3.  [oai_citation:5‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

6) Consensus Arbitration Service (agent conflicts)

TASK: Resolve conflicting agent outputs deterministically.

EDIT:
- candidate/core/orchestration/consensus_arbitrator.py (new)
  - def arbitrate(proposals: list[dict]) -> dict:
    # scoring by guardian_ethics_score, confidence, recency; tie-break by ΛiD role
- agent_orchestrator.py
  - on conflict, call arbitrate().

TESTS:
- tests/orchestration/test_consensus_arbitrator.py
  - construct conflicting proposals; expect stable choice & explanation.

ACCEPTANCE:
- Conflict path covered by tests; logs include rationale.

REFERENCE: Audit §EQNOX & §Latent Orchestration, pp.3 & 9.  [oai_citation:6‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

7) Integrity check hook in AkaQualia loop

TASK: Add drift/integrity micro-check per reasoning tick.

EDIT:
- candidate/aka_qualia/core.py
  - after each cycle: if IntegrityProbe.run_consistency_check() is False: trigger soft reset / repair.

TESTS:
- tests/qualia/test_integrity_hook.py
  - simulate integrity False ⇒ repair path invoked.

ACCEPTANCE:
- Integrity hook is observable in logs; gated by feature flag.

REFERENCE: Audit §EQNOX & §DriftScore, pp.3 & 7.  [oai_citation:7‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)


⸻

ΛiD (identity & consent)

8) Implement symbolic_id_encoder + API tier middleware

TASK: Create Symbolic Identity Hash + enforce ΛTIER on API.

EDIT:
- identity/symbolic_id_encoder.py (new)
  - def encode_seed_to_sid(seed: str) -> str: # SHA-256 + checksum; returns SID
- oneiric_core/identity/auth_middleware.py
  - require JWT ⇒ resolve SID ⇒ enforce ΛTIER permission map.

TESTS:
- tests/identity/test_symbolic_id_encoder.py
- tests/identity/test_auth_middleware_tiers.py

ACCEPTANCE:
- Encoder deterministic; middleware blocks unauthorized tier.

REFERENCE: Audit §ΛiD, pp.4–5.  [oai_citation:8‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

9) Consent Policy Engine (constraint logic)

TASK: Enforce user consent via declarative rules.

EDIT:
- identity/consent/policy_engine.py (new)
  - def allowed(request: dict, policy_rules: list[dict]) -> (bool, reason)
- Integrate into relevant service entrypoints (e.g., Oneiric generation).

TESTS:
- tests/identity/test_consent_policy_engine.py
  - time- and purpose-bounded policies; denial reasons surfaced.

ACCEPTANCE:
- Requests violating policy cleanly rejected & logged.

REFERENCE: Audit §ΛiD, p.4.  [oai_citation:9‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

10) Identity Drift Monitor

TASK: Track evolution of user symbolic persona.

EDIT:
- identity/drift_monitor.py (new)
  - def identity_drift(old_profile: dict, new_activity: dict) -> float
- Periodically persist drift in user_profile table.

TESTS:
- tests/identity/test_identity_drift.py
  - controlled activity shift ⇒ expected drift increase.

ACCEPTANCE:
- Drift value appears in audit logs; threshold triggers “review” flag.

REFERENCE: Audit §ΛiD, p.4.  [oai_citation:10‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)


⸻

Guardian (ethics)

11) Prolog-like ethics engine

TASK: Encode constitutional rules as logical clauses; solve dilemmas.

EDIT:
- ethics/logic/ethics_engine.py (new)
  - def evaluate(context: dict) -> (allowed: bool, rationale: list[str])
  - tiny Datalog/Prolog subset (or pythonic rule DSL)
- Guardian decision path: call ethics_engine before final allow.

TESTS:
- tests/ethics/test_ethics_engine_rules.py
  - conflicting duties; priority ordering resolves; rationale is human-readable.

ACCEPTANCE:
- At least 5 core rules encoded; engine used in one real decision path.

REFERENCE: Audit §Guardian, p.6.  [oai_citation:11‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

12) Drift Monitor Service (adaptive thresholds)

TASK: Replace fixed 0.15 with context-aware bands.

EDIT:
- ethics/guardian_reflector.py (new or extend)
  - def ethical_drift_band(score: float, phase: str) -> str  # 'minor'|'major'|'critical'
  - map band → action: log|nudge|safe-mode|human-review

TESTS:
- tests/ethics/test_guardian_drift_bands.py
  - band transitions; correct action dispatch.

ACCEPTANCE:
- Guardian actions vary by band; thresholds configurable.

REFERENCE: Audit §Guardian, p.6.  [oai_citation:12‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

13) Multimodal safety tagging

TASK: Extend filters to image/audio symbolic tags.

EDIT:
- ethics/filters/multimodal.py (new)
  - def tag_image(bytes) -> set[str]; def tag_audio(bytes) -> set[str]
- Guardian ingests tags; applies same rulebook.

TESTS:
- tests/ethics/test_multimodal_tags.py
  - synthetic fixtures ⇒ expected tags; policy blocks when tag present.

ACCEPTANCE:
- One end-to-end blocked case demonstrated via tags.

REFERENCE: Audit §Guardian, p.6.  [oai_citation:13‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)


⸻

DriftScore (unified, actionable)

14) Drift Management Module (single interface)

TASK: Centralize ethical/memory/identity drift scoring.

EDIT:
- monitoring/drift_manager.py (new)
  - def compute(kind:str, prev:dict, curr:dict) -> dict  # {score:float, top_symbols:[...]}
- Wire IntegrityProbe to use drift_manager deltas.

TESTS:
- tests/drift/test_drift_manager.py
  - cross-domain consistency; top_symbols returned.

ACCEPTANCE:
- One caller migrated (IntegrityProbe); reports include top symbols.

REFERENCE: Audit §DriftScore, p.7.  [oai_citation:14‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

15) Autonomous Drift Correction

TASK: Auto-trigger repair when drift exceeds epsilon.

EDIT:
- drift_manager.py
  - def on_exceed(kind, score, context): routes to TraceRepairEngine / memory reconsolidation
- Register callback in IntegrityProbe.

TESTS:
- tests/drift/test_autorepair.py
  - injected drift ⇒ repair invoked; reduces drift on next cycle.

ACCEPTANCE:
- Repair loop demonstrably closes in a test scenario.

REFERENCE: Audit §DriftScore, p.7.  [oai_citation:15‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)


⸻

Oneiric Core

16) Symbolic Dream Interpreter

TASK: Convert dreams (text/image seeds) into structured symbols.

EDIT:
- oneiric_core/analysis/symbolic_interpreter.py (new)
  - def interpret(dream: dict) -> dict  # {symbols:[...], arcs:[...]}
- Persist symbols with each dream entry.

TESTS:
- oneiric_core/tests/test_symbolic_interpreter.py
  - controlled inputs ⇒ expected symbol set.

ACCEPTANCE:
- Journal view shows stored symbols for a new dream.

REFERENCE: Audit §Oneiric Core, p.9.  [oai_citation:16‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

17) Guardian constraints during dream gen

TASK: Enforce user consent/ethics on generated content.

EDIT:
- oneiric_core/generation/engine.py
  - before finalizing output: ethics_engine.evaluate + consent policy check
  - if violation ⇒ regenerate or redact

TESTS:
- oneiric_core/tests/test_dream_guardrails.py
  - user policy “no violence” ⇒ outputs comply.

ACCEPTANCE:
- Block/regenerate flow observable in logs; policy honored.

REFERENCE: Audit §Oneiric Core, p.9.  [oai_citation:17‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

18) Drift Dream Test (sandboxed repair probe)

TASK: Generate a dream focused on a drifting symbol; analyze alignment.

EDIT:
- oneiric_core/tools/drift_dream_test.py (new CLI)
  - --symbol LOYALTY --user <sid> ⇒ produce dream + interpret + drift delta

TESTS:
- oneiric_core/tests/test_drift_dream_tool.py
  - synthetic scenario ⇒ tool reports symbol alignment trend.

ACCEPTANCE:
- Tool runs end-to-end and writes a concise report to /tmp or DB.

REFERENCE: Audit §Oneiric Core, p.9.  [oai_citation:18‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

19) Symbol preferences + identity loop

TASK: Let users override symbol meanings; feed back into ΛiD.

EDIT:
- Frontend: add “Edit Meaning” in Symbol Explorer (POST /symbol_prefs)
- Backend: oneiric_core/api/symbol_prefs.py (new)
  - persist per-user overrides; expose to interpreter + identity drift monitor

TESTS:
- oneiric_core/tests/test_symbol_prefs.py
  - override applied; interpreter respects override.

ACCEPTANCE:
- UI shows and uses personal meanings; ΛiD profile updated.

REFERENCE: Audit §Oneiric Core, p.9.  [oai_citation:19‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)


⸻

Latent Modules (high leverage)

20) Meta‑Reasoning Controller

TASK: Add a meta layer to detect loops/conflicts across agents.

EDIT:
- candidate/core/orchestration/meta_controller.py (new)
  - def monitor(tick_state) -> list[issue]; def resolve(issue) -> action
- Hook into agent_orchestrator main loop.

TESTS:
- tests/orchestration/test_meta_controller.py
  - simulate oscillation ⇒ controller breaks loop.

ACCEPTANCE:
- One synthetic conflict auto-resolved with logged rationale.

REFERENCE: Audit §Latent Orchestration, p.9.  [oai_citation:20‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

21) Symbolic Inference Engine (KB)

TASK: Introduce a small rule/query store for facts & ethics.

EDIT:
- core/knowledge/kb.py (new)
  - add_fact, query(pattern) with simple unification
- Guardian + Plan Verifier can query kb for precedent.

TESTS:
- tests/knowledge/test_kb.py
  - queries return expected matches; no exponential blowup on small sets.

ACCEPTANCE:
- One path (ethics or plan) queries KB successfully.

REFERENCE: Audit §Symbolic KB, p.10.  [oai_citation:21‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

22) Chrono Regulation Module (bio rhythms)

TASK: Schedule maintenance (collapse, drift audits) on rhythms.

EDIT:
- bio/oscillators/chrono.py (new)
  - def phase(now) -> {'ACTIVE'|'MAINTENANCE'|'REFLECTION'}
- A small scheduler triggers heavy tasks in MAINTENANCE.

TESTS:
- tests/bio/test_chrono.py
  - phases computed correctly; tasks only run in MAINTENANCE.

ACCEPTANCE:
- One heavy task (collapse sweep) moved to maintenance windows.

REFERENCE: Audit §Bio Regulator, p.10.  [oai_citation:22‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)

23) LLM Guardrail (neural interface)

TASK: Force external LLM I/O through a symbolic contract.

EDIT:
- core/bridge/llm_guardrail.py (new)
  - def call_llm(prompt, schema: dict) -> dict  # validates to JSON schema; strips unsafe fields
- Replace direct LLM calls in any adapter to go through guardrail.

TESTS:
- tests/bridge/test_llm_guardrail.py
  - invalid LLM output ⇒ rejected; valid ⇒ accepted.

ACCEPTANCE:
- At least one adapter now guarded end-to-end.

REFERENCE: Audit §Neural Interface, p.11.  [oai_citation:23‡LUKHΛS AGI Architecture Audit and Symbolic Integration Report.pdf](file-service://file-U4FG4rJx8DfjAmmazAU5KU)


⸻

Suggested execution order (minimize rework)
	1.	Drift backbone: #14, #15, #7 — gives you safe self‑correction everywhere.  ￼
	2.	Constraints & ethics: #5, #11, #12, #13 — harden decision safety nets.  ￼
	3.	Bridging & orchestration: #4, #6, #20 — get stable multi‑agent flow.  ￼
	4.	Identity & consent: #8, #9, #10 — lock governance.  ￼
	5.	Oneiric upgrades: #16–#19 — turn dreams into a safe alignment lab.  ￼
	6.	Latent boosters: #21–#23 — elevate reasoning, rhythm, and neural hygiene.  ￼

⸻

One-liner PR templates (commit discipline)
	•	feat(collapse): map embedding shifts to entropy (#NNN)
	•	feat(eqnoX): add global plan verifier w/ constraint rules (#NNN)
	•	feat(id): add symbolic_id_encoder + tier middleware (#NNN)
	•	feat(guardian): prolog-like ethics engine + drift bands (#NNN)
	•	feat(drift): unify drift manager + auto repair loop (#NNN)
	•	feat(oneiric): symbolic_interpreter + consent guardrails (#NNN)
	•	feat(orch): consensus arbitrator + meta controller (#NNN)

⸻

If you want, I can also drop these into a .copilot_tasks.md with checkboxes and per‑task context links from your /docs so Copilot stays on‑rails while you parallelize work across agents. The meta‑skill here is to keep each prompt small, testable, and behind a feature flag so the system never drifts faster than it can repair.