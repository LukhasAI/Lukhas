

# AGENTS.md — LUKHΛS “0.01% Surgeon” Runbook (T4)

**Mission:** make small, verifiable changes with explicit proofs. Agents must obey the same guardrails, produce diffs, run tests, and never bypass feature flags.

---

## Global guardrails (apply to all agents)

- **Feature flags (default ON/OFF as shown):**
  - `LUKHAS_EXPERIMENTAL=1` (on), `LUKHAS_LANE=candidate`
  - `ENFORCE_ETHICS_DSL=0` (stage behind flag), `ENABLE_LLM_GUARDRAIL=1`
- **Prohibited edits:** Do not reintroduce legacy `glyph` imports or bypass consent/tier checks.
- **Refuse patterns:** `import glyph`, `from glyph`, `candidate.core.common.glyph` (legacy)
- **Conventional commits:** `feat|fix|refactor|chore(scope): message`
- **Proof artifacts required:** 
  - drift report with `top_symbols`
  - p95 latency report
  - policy ledger line for changed paths
- **One‑PR, one‑feature.** Keep PRs narrowly scoped.

### Acceptance gates (must be satisfied in PR)
- **Safety:** Guardian denials **rate** not worse vs. control.
- **Drift:** unified Δdrift ≤ **0.02** across eval set; include `top_symbols`.
- **Latency:** added overhead ≤ **5% p95** on affected routes.
- **Containment:** collapse sims show ≥ **99.7% isolation**; repair invoked on violation.
- **Governance:** 100% API routes check **ΛTIER + consent**; **ledger entries emitted**.

---

## Agent roles (who does what)

### 1) Claude Code — *Primary Surgeon*
- **Use for:** multi‑file refactors, new modules (Constraints/DSL, Drift Manager), orchestration wiring.
- **Why:** terminal‑native diffs, repo‑wide reasoning, human‑in‑the‑loop approval.
- **Run tests:** `pytest -q` (or `make <target>` from `.copilot_tasks.md`).
- **Default prompt (paste into Claude Code):**
  ```
  You are the primary “0.01% Surgeon” on the LUKHΛS repo.
  Guardrails:
  - Keep all new logic behind flags: LUKHAS_EXPERIMENTAL=1, LUKHAS_LANE=candidate.
  - Do not reintroduce legacy glyph imports or bypass consent/tier checks.
  - Each change must include tests, docs, and telemetry counters.
  Acceptance gates:
  - Δdrift ≤ 0.02 with top_symbols; p95 overhead ≤ 5%; collapse isolation ≥ 99.7%;
    policy ledger emits one line per request path under test.
  Task:
  - Implement exactly the task box selected from `.copilot_tasks.md`.
  - Touch only listed files. Generate minimal, typed interfaces. Propose diffs; await approval.
  After edits:
  - Run appropriate `make` target(s) and `pytest -q`, paste outputs.
  - If any gate fails, propose a rollback or a smaller scope patch.
  ```

### 2) GitHub Copilot — *Pit Crew*
- **Use for:** scaffolding tests/fixtures, docstrings, quick adapters, tiny utilities.
- **Why:** speed in‑editor; can switch models per chat.
- **Copilot Chat starter:**
  ```
  Context: LUKHΛS repo; we follow .copilot_tasks.md (v2).
  Generate only the smallest test/fixture/docstring required for TASK <id>.
  Use feature flags and relative imports. No business logic changes.
  Output a diff-ready snippet and a `pytest -q` command to validate it.
  ```

### 3) OpenAI Codex — *Batch Worker (Sandbox PRs)*
- **Use for:** repo‑wide boilerplate (CLI stubs, dashboard JSON panels, test skeletons), non‑risky mass edits.
- **Why:** spins up a clean sandbox, returns PR + logs.
- **Codex “job card” template (paste as prompt):**
  ```
  Repo: LUKHΛS (root = .)
  Safety gates: Δdrift ≤ 0.02; p95 ≤ +5%; isolation ≥ 99.7%; ledger required.
  Job:
  - Create <X> files and wiring exactly as specified in `.copilot_tasks.md` section <Y>.
  - DO NOT change business logic outside listed paths.
  Deliverables:
  - PR with diffs, test logs (`pytest -q`), and artifact paths produced.
  ```

---

## Task routing map (from `.copilot_tasks.md`)

- **Drift Backbone (14, 15, 7):** Claude Code (primary), Copilot for tests.
- **Constraints & Ethics (5, 11, 12, 13):** Claude Code; Copilot for schema/tests.
- **Bridge & Orchestration (23, 4, 6, 20):** Claude Code; Codex for boilerplate adapters.
- **Identity & Consent (8, 9, 10):** Claude Code; Copilot for middleware tests.
- **Oneiric (16–19):** Claude Code for guardrails; Codex for CLI + UI boilerplate.
- **Collapse Engine (1–3):** Claude Code; Codex for simulator CLI scaffolding.
- **Latent Boosters (21–22):** Codex to seed; Claude Code to harden.

---

## Workflow checklist (every PR)

1. **Branch:** `feat/<task-id>-<slug>`  
2. **Set flags:**  
   ```bash
   export LUKHAS_EXPERIMENTAL=1
   export LUKHAS_LANE=candidate
   export ENABLE_LLM_GUARDRAIL=1
   ```
3. **Implement:** follow the single task box; add counters `{attempts,successes,denials}` + p95 timers.
4. **Tests:** run `make <area>` then `pytest -q`; collect artifacts (SLO, chaos, policy).
5. **Commit:** conventional style; include “Acceptance: GREEN” when all gates met.
6. **PR:** include diffs, logs, artifact snippets, and a one‑paragraph risk/rollback note.

---

## Quick commands

```bash
# Python baseline
uv pip install -r requirements.txt || pip install -r requirements.txt
pytest -q

# Make targets (see .copilot_tasks.md)
make drift | constraints | bridge | orch | id | oneiric | collapse | demo
```

---

## Failure policy

- If any acceptance gate turns **RED**, revert the last change or disable the feature flag for that route and file a follow‑up task with findings.
- Never “ship and watch.” Proof before merge.

---