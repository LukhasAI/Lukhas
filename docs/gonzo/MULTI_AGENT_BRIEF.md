

# 🔧 Multi-Agent Brief — Phase B/GA Run-Up (Parallel Worktrees)

## Current state (quick context)

* **v0.9.0-rc** is tagged & live. Guardian PDP + RL headers merged. OpenAPI guard + health signals in place.
* **Monitoring stack** (Grafana + Prometheus alerts + runbook) landed.
* **PR #381** (Codex Phase-B gate) opened.
* CI guards: `compat-enforce=0`, `openapi-headers-guard`, `ruff-phaseA`, **`ruff-phaseB-hotpaths ≤120`**.

---

## 1) Worktree layout (required: avoid stepping on each other)

> Run these locally (or adapt to your env); each agent owns a separate worktree + branch.

```bash
# root repo (already exists)
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git fetch --all --prune

# Claude Code — Ops/observability/CI polish
git worktree add ../Lukhas-claude      main
cd ../Lukhas-claude
git checkout -b feat/ops/ga-guard-pack

# Codex — Phase-B lint/refactor (scoped)
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git worktree add ../Lukhas-codex-B1    main
cd ../Lukhas-codex-B1
git checkout -b fix/codex10/ruffB1

# Copilot — DX/docs/examples polish
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git worktree add ../Lukhas-copilot-dx2 main
cd ../Lukhas-copilot-dx2
git checkout -b docs/copilot/quickstart-polish
```

---

## 2) Path ownership (no-collision rules)

**Codex (lint/refactor – Phase-B.1):**

* ✅ May change (lint/import/one-liner fixes only):

  * `lukhas/core/reliability/{idempotency.py, ratelimit.py}`
  * `lukhas/observability/{tracing.py, guardian_metrics.py}`
  * `MATRIZ/core/{orchestrator.py}`
  * `MATRIZ/interfaces/api_server.py`
* 🚫 Do **not** touch runtime in:

  * `lukhas/adapters/openai/api.py`, `lukhas/adapters/openai/auth.py`, `lukhas/adapters/openai/policy_pdp.py`
  * Any files under `lukhas/adapters/openai/` **except** import order/whitespace

**Claude Code (ops/CI/observability):**

* ✅ May change:

  * `.github/workflows/*`, `scripts/*`, `docs/releases/*`, `lukhas/observability/*`, `lukhas/adapters/openai/api.py` (only for **headers/health/metrics/telemetry**)
* 🚫 Do not mass-format or import-shuffle Codex’s hot-path files in the same PR.

**Copilot (docs & DX):**

* ✅ May change:

  * `README.md`, `examples/sdk/*`, `.github/workflows/newman-golden-flows.yml`, `docs/**`
* 🚫 No changes in production Python runtime (lukhas/core, adapters, MATRIZ).

---

## 3) Acceptance criteria per agent

### Codex — **Phase-B.1 hot-path cleanup**

* Goal: reduce **E402/E70x** in hot paths; leave logic unchanged.
* Budget: tighten `ruff-phaseB-hotpaths` from **≤120 → ≤90** in this PR.
* Target files (15–20):

  * `lukhas/core/reliability/idempotency.py`
  * `lukhas/core/reliability/ratelimit.py`
  * `lukhas/observability/tracing.py`
  * `lukhas/observability/guardian_metrics.py`
  * `MATRIZ/core/orchestrator.py`
  * `MATRIZ/interfaces/api_server.py`
* Commands:

  ```bash
  python -m ruff check lukhas/core/reliability \
                       lukhas/observability \
                       MATRIZ/core MATRIZ/interfaces/api_server.py \
                       --select E402,E701,E702,E722,F401,F402 --fix --unsafe-fixes

  # Verify hot-path gate
  python -m ruff check lukhas/adapters/openai lukhas/core/reliability lukhas/observability MATRIZ/core MATRIZ/interfaces/api_server.py --statistics --no-cache

  # Smoke sanity
  pytest tests/smoke/test_openai_facade.py -q
  ```
* PR title:

  * `chore(lint): Phase-B.1 hot-path E402/E70x cleanup; tighten gate ≤90`

### Claude Code — **GA guard pack**

* Ship in one PR:

  1. **CI**: Add badge/comment to surface `ruff-phaseB-hotpaths` budget & smoke % on PRs.
  2. **Ops**: Prometheus **recording rules** for PDP latency SLO and denial rate SLI.
  3. **Health artifacts**: include Guardian/RL signals in `docs/audits/health/latest.{json,md}`.
* Verify:

  ```bash
  # Health audit
  python3 scripts/generate_system_health_report.py
  # CI dry-run (if you have act): act -j matriz-validate (optional)
  ```
* PR title:

  * `feat(ops): GA guard pack — PR health badge, recording rules, health artifacts`

### Copilot — **DX polish** ✅ **Done via #383**

* ✅ Added "Try it in 30s" block to **root README** (curl examples for models & embeddings)
* ✅ Added **Postman collection v2** + **environment** (BASE_URL, API_KEY)
* ✅ Added **API cookbooks** (Responses, Dreams) with cURL/JS/Python/TS recipes
* ✅ Added **CI smoke workflow** (`dx-examples-smoke.yml`) — boots façade, compiles SDKs, runs Newman
* ✅ Added **release notes** scaffolding for DX Polish Pack
* PR: [#383 (merged)](https://github.com/LukhasAI/Lukhas/pull/383)

**Follow-up enhancements (non-blocking, docs-only)**:
* Node_modules caching for faster CI
* README badge for dx-examples-smoke workflow
* "See Also" box linking cookbooks, SDKs, Postman
* Concurrency group to prevent PR spam

---

## 4) CI gates you will trip (and how to keep them green)

* `ruff-phaseA` (unchanged): stays green.
* `ruff-phaseB-hotpaths` (new budget **≤120** today; Codex PR will lower to ≤90).
* `facade-smoke` (requires auth): use the shared **auth fixture** in tests.
* `openapi-spec` + `openapi-diff` + `openapi-headers-guard`: no spec JSON in git; CI generates & checks.
* `compat-enforce`: must stay `0`.

---

## 5) Ready-to-paste PR bodies

**Codex**

```
## Problem
Hot paths still carry E402/E70x debt; wide codemods are risky.

## Solution
Scoped cleanups in adapters/core/observability/MATRIZ (imports + one-liners), no logic changes. Tighten hot-path lint budget to ≤90.

## Impact
Lower lint noise on critical surfaces; safer future refactors.

## Verification
- Ruff hot-path stats: clean under ≤90
- Façade smoke: pass with auth fixture
- No runtime changes outside formatting/import order
```

**Claude Code**

```
## What
- PR health badge comment (ruff hot-path budget + smoke %)
- Prometheus recording rules (PDP latency SLO, denial % SLI)
- Health artifacts include Guardian/RL signals

## Why
GA readiness needs visible SLO/SLI and automatic PR feedback.

## Verification
- Health report updated under docs/audits/health/latest.*
- Recording rules load (Prometheus reload OK)
- PR comment shows budget/smoke badges
```

**Copilot**

```
## DX improvements
- 30s quickstart in README (curl/Node/Python)
- Postman environment with env var wiring
- SDK examples: streaming & error-envelope alignment

## Why
Reduce time-to-first-success; mirror OpenAI ergonomics.

## Verification
- Examples run locally
- README links valid
```

---

## 6) Daily sync ritual (90 seconds)

1. `git fetch --all --prune`
2. `git status` in your worktree
3. Re-run your **lint target** and **one smoke file**
4. If you must touch a file owned by another agent: leave it and drop a note in the PR (we’ll reassign).

---

## 7) Done signals (paste with your PR)

* Branch name + link
* 3 verification commands output (ruff stats, 1 smoke test, health/spec check for Claude)
* Any files you deliberately left untouched to avoid conflicts

---
