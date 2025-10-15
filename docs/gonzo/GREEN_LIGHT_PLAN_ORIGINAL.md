

# Greenlight Plan (Option A: Deploy to Staging/Local Now)

**Status**: ✅ All monitoring artifacts created and validated  
**Date**: 2025-10-15  

---

## Who Does What (Immediately)

* **Codex (Hot-paths):** Continue Phase-B slices (#388/#389) in parallel—no runtime overlap with monitoring.
* **Copilot (DX/Observability):** Deploy rules + alerts + dashboard to staging; kick off baseline collection.

**Preflight (1–2 min)**

```bash
# Validate YAML/JSON locally
python3 -c "import yaml; yaml.safe_load(open('lukhas/observability/rules/guardian-rl.rules.yml'))"
python3 -c "import yaml; yaml.safe_load(open('lukhas/observability/rules/guardian-rl.alerts.yml'))"
python3 -m json.tool lukhas/observability/grafana/guardian-rl-dashboard.json > /dev/null
```

(These steps match the post-merge deployment guide.) 

**Deploy (5–10 min)**

```bash
# Option A1: local stack (if available)
docker-compose -f docker/monitoring/docker-compose.yml up -d

# Option A2: staging Prometheus
scp lukhas/observability/rules/*.yml user@prometheus:/etc/prometheus/rules.d/
ssh user@prometheus 'curl -X POST http://localhost:9090/-/reload'

# Import Grafana dashboard (API token required)
curl -X POST http://grafana:3000/api/dashboards/db \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @lukhas/observability/grafana/guardian-rl-dashboard.json
```

**Baseline & soak**

```bash
# 6h baseline collection (generates docs/audits/rc-soak/BASELINE_METRICS_v0.9.0-rc.md)
bash scripts/rc_soak_health_check.sh

# Then begin 48–72h RC soak; run the daily check (e.g., GH Actions cron)
bash scripts/rc_soak_health_check.sh
```

**What you should see in Grafana (7 panels):**

* PDP latency P50/P95/P99 (<10ms target)
* Denial rate overall/by scope (<15% target)
* RL hit rate (<10% target) & near-exhaustion ratio
* Combined Guardian+RL health score (>0.80 target)

# Go/No-Go gates for GA

* PDP P95 < **10ms** stable
* Denial rate < **15%**
* RL hit rate < **10%**
* Health score > **0.80**
* No CRITICAL alerts firing during soak

# Watchlist (common snags & quick fixes)

* **No metrics?** Verify Prometheus rule files are under the server’s rules dir and reload succeeded.
* **Cardinality spike?** We already aggregate on stable labels; if series explode, temporarily drop the per-principal rules group and reload.
* **RL headers missing?** Recheck façade is on the latest `main` (PR #380 merged) and that the OpenAPI headers guard is passing in CI.



## ✅ Staging Deployment (5 minutes)

---
# Create deployment and health-check scripts, workflow, and Makefile fragment for the user to download.

import os, json, textwrap, datetime, pathlib

base = "/mnt/data"
files = {}

# 1) monitoring_deploy.sh
monitoring_deploy = """#!/usr/bin/env bash
set -euo pipefail

# === Monitoring Deploy Helper ===
# Deploy Prometheus rules/alerts and import Grafana dashboard.
# Local mode expects Prometheus rules directory mounted locally.
# Environment:
#   PROMETHEUS_RULES_DIR   (e.g., /etc/prometheus/rules.d)  [required for local copy]
#   PROMETHEUS_URL         (e.g., http://localhost:9090)    [required for reload + queries]
#   GRAFANA_URL            (e.g., http://localhost:3000)    [optional for dashboard import]
#   GRAFANA_API_KEY        (Grafana API token)              [optional for dashboard import]
#   REPO_ROOT              (repo path; default: current dir)
#   DRY_RUN                (set to 1 for dry run)
#
# Usage:
#   PROMETHEUS_RULES_DIR=/etc/prometheus/rules.d PROMETHEUS_URL=http://localhost:9090 \\
#   GRAFANA_URL=http://localhost:3000 GRAFANA_API_KEY=*** \\
#   ./scripts/monitoring_deploy.sh
#
# Notes:
# - For remote Prometheus hosts, copy the *.yml files to the remote rules dir yourself,
#   then run the reload step below against PROMETHEUS_URL on the remote.
# - This script is idempotent and safe to rerun.

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
RULES_SRC_DIR="$REPO_ROOT/lukhas/observability/rules"
GRAFANA_DASH="$REPO_ROOT/lukhas/observability/grafana/guardian-rl-dashboard.json"

echo "==> Monitoring Deploy"
echo "Repo root: $REPO_ROOT"
echo "Rules src: $RULES_SRC_DIR"

if [[ "${DRY_RUN:-0}" != "1" ]]; then
  if [[ -n "${PROMETHEUS_RULES_DIR:-}" ]]; then
    echo "-- Copying Prometheus rules to ${PROMETHEUS_RULES_DIR}"
    cp -v "${RULES_SRC_DIR}"/*.yml "${PROMETHEUS_RULES_DIR}/"
  else
    echo "!! PROMETHEUS_RULES_DIR not set; skipping local copy (ok if you deploy rules remotely)"
  fi
else
  echo "[DRY RUN] Would copy rules to ${PROMETHEUS_RULES_DIR:-<unset>}"
fi

if [[ -n "${PROMETHEUS_URL:-}" ]]; then
  echo "-- Reloading Prometheus @ ${PROMETHEUS_URL}"
  if [[ "${DRY_RUN:-0}" != "1" ]]; then
    curl -fsS -X POST "${PROMETHEUS_URL}/-/reload" || { echo "Prometheus reload failed"; exit 1; }
  else
    echo "[DRY RUN] Would POST ${PROMETHEUS_URL}/-/reload"
  fi
else
  echo "!! PROMETHEUS_URL not set; cannot trigger reload."
fi

if [[ -n "${GRAFANA_URL:-}" && -n "${GRAFANA_API_KEY:-}" ]]; then
  echo "-- Importing Grafana dashboard"
  if [[ "${DRY_RUN:-0}" != "1" ]]; then
    curl -fsS -X POST "${GRAFANA_URL%/}/api/dashboards/db" \
      -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
      -H "Content-Type: application/json" \
      --data-binary @"${GRAFANA_DASH}" >/dev/null
    echo "Dashboard imported."
  else
    echo "[DRY RUN] Would import dashboard ${GRAFANA_DASH} into ${GRAFANA_URL}"
  fi
else
  echo "!! GRAFANA_URL or GRAFANA_API_KEY not set; skipping dashboard import (you can import manually)."
fi

echo "==> Done."
"""

# 2) rc_soak_health_check.sh
rc_soak = """#!/usr/bin/env bash
set -euo pipefail

# === RC Soak Health Check ===
# Collects health signals from the façade and Prometheus, writes MD+JSON reports.
# Env:
#   LUKHAS_API_URL   (default: http://localhost:8000)
#   PROMETHEUS_URL   (e.g., http://localhost:9090) [optional for extra SLIs]
#   OUT_DIR          (default: docs/audits/rc-soak)
#   REPO_ROOT        (default: current dir)
#
# Usage:
#   LUKHAS_API_URL=http://localhost:8000 PROMETHEUS_URL=http://localhost:9090 ./scripts/rc_soak_health_check.sh

REPO_ROOT="${REPO_ROOT:-$(pwd)}"
OUT_DIR="${OUT_DIR:-$REPO_ROOT/docs/audits/rc-soak}"
API_URL="${LUKHAS_API_URL:-http://localhost:8000}"
PROM_URL="${PROMETHEUS_URL:-}"

mkdir -p "${OUT_DIR}"

ts="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
json_out="${OUT_DIR}/SOAK_${ts}.json"
md_out="${OUT_DIR}/SOAK_${ts}.md"

echo "==> Fetching /healthz from ${API_URL}"
health_json=$(curl -fsS "${API_URL%/}/healthz" || echo "{}")

# Optional Prometheus queries
prom_data="{}"
if [[ -n "${PROM_URL}" ]]; then
  echo "==> Querying Prometheus @ ${PROM_URL}"
  # Example: denial rate 15m, PDP p95 latency 15m, RL hit rate 15m
  q_denial='sum(increase(guardian_denied_total[15m])) / clamp_min(sum(increase(guardian_decision_total[15m])), 1)'
  q_p95='histogram_quantile(0.95, sum by (le) (rate(guardian_decision_latency_seconds_bucket[15m])))'
  q_rl='sum(increase(rate_limited_total[15m])) / clamp_min(sum(increase(http_requests_total[15m])), 1)'
  # shellcheck disable=SC2016
  prom_data=$(jq -n --arg denial "$(curl -fsS --get --data-urlencode "query=${q_denial}" "${PROM_URL%/}/api/v1/query" | jq -r '.data.result[0].value[1] // empty')" \
                     --arg p95 "$(curl -fsS --get --data-urlencode "query=${q_p95}"    "${PROM_URL%/}/api/v1/query" | jq -r '.data.result[0].value[1] // empty')" \
                     --arg rl  "$(curl -fsS --get --data-urlencode "query=${q_rl}"     "${PROM_URL%/}/api/v1/query" | jq -r '.data.result[0].value[1] // empty')" \
                     '{denial_rate_15m: ($denial|tonumber?), pdp_p95_15m: ($p95|tonumber?), rl_hit_rate_15m: ($rl|tonumber?)}')
fi

# Build combined JSON
version=$(git -C "${REPO_ROOT}" describe --tags --always --dirty=+ | sed 's/^v//')
sha=$(git -C "${REPO_ROOT}" rev-parse --short HEAD || echo "unknown")
report=$(jq -n --arg ts "${ts}" --arg version "${version}" --arg sha "${sha}" \
             --argjson health "${health_json}" --argjson prom "${prom_data}" \
             '{timestamp: $ts, version: $version, git_sha: $sha, health: $health, prom: $prom}')

echo "${report}" > "${json_out}"

# Minimal MD
cat > "${md_out}" <<EOF
# RC Soak Health — ${ts}

**Version:** ${version} (${sha})

- Guardian PDP loaded: $(echo "${health_json}" | jq -r '.checks.guardian_pdp.pdp_loaded // "n/a"')
- Denials (last window): $(echo "${health_json}" | jq -r '.checks.guardian_pdp.denials // "n/a"')
- Rate limiter backend:  $(echo "${health_json}" | jq -r '.checks.rate_limiter.backend // "n/a"')

$(if [[ -n "${PROM_URL}" ]]; then
  echo "## Prometheus (15m window)"
  echo "- Denial rate: $(echo "${prom_data}" | jq -r '.denial_rate_15m // "n/a"')"
  echo "- PDP p95 latency (s): $(echo "${prom_data}" | jq -r '.pdp_p95_15m // "n/a"')"
  echo "- RL hit rate: $(echo "${prom_data}" | jq -r '.rl_hit_rate_15m // "n/a"')"
fi)
EOF

echo "Wrote:"
echo "  - ${json_out}"
echo "  - ${md_out}"
"""

# 3) GitHub Actions workflow for daily soak
workflow = """name: RC Soak Daily

on:
  schedule:
    - cron: "0 2 * * *"   # 02:00 UTC daily
  workflow_dispatch: {}

jobs:
  rc-soak:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install jq and curl
        run: sudo apt-get update && sudo apt-get install -y jq curl
      - name: Run soak health check
        env:
          LUKHAS_API_URL: ${{ secrets.RC_FACADE_URL }}
          PROMETHEUS_URL: ${{ secrets.RC_PROM_URL }}
        run: |
          bash -euxo pipefail <<'BASH'
          mkdir -p scripts
          if [[ -f scripts/rc_soak_health_check.sh ]]; then
            chmod +x scripts/rc_soak_health_check.sh
          else
            echo "Missing scripts/rc_soak_health_check.sh in repo. Exiting."; exit 1
          fi
          ./scripts/rc_soak_health_check.sh
          BASH
      - name: Upload soak artifacts
        uses: actions/upload-artifact@v4
        with:
          name: rc-soak-health-${{ github.run_number }}
          path: docs/audits/rc-soak/
          retention-days: 14
"""

# 4) Makefile fragment
makefrag = """# === Monitoring Helpers ===
.PHONY: monitoring-deploy rc-soak

monitoring-deploy:
\t@echo "Deploying monitoring (rules + alerts + dashboard)"
\t@chmod +x scripts/monitoring_deploy.sh || true
\t@./scripts/monitoring_deploy.sh

rc-soak:
\t@echo "Running RC soak health check"
\t@chmod +x scripts/rc_soak_health_check.sh || true
\t@./scripts/rc_soak_health_check.sh
"""

# Create directories and write files
paths = {
    "scripts/monitoring_deploy.sh": monitoring_deploy,
    "scripts/rc_soak_health_check.sh": rc_soak,
    ".github/workflows/rc-soak-daily.yml": workflow,
    "Makefile.fragment": makefrag,
}

for rel, content in paths.items():
    full = os.path.join(base, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    if rel.endswith(".sh"):
        os.chmod(full, 0o755)

list(paths.keys())
---

1. **Add env** (local or CI job vars)

```
export PROMETHEUS_RULES_DIR=/etc/prometheus/rules.d
export PROMETHEUS_URL=http://localhost:9090
export GRAFANA_URL=http://localhost:3000
export GRAFANA_API_KEY=<grafana_api_token>
```

2. **Add the files** above to your repo and commit.

3. **Run deploy**

```bash
chmod +x scripts/monitoring_deploy.sh
./scripts/monitoring_deploy.sh
# Copies rules, reloads Prometheus, imports Grafana dashboard.
```

4. **Sanity check**

```bash
curl -fsS ${PROMETHEUS_URL}/api/v1/rules | jq '.status'
# expect "success"

curl -fsS ${GRAFANA_URL}/api/search?query=guardian | jq '.[0].title'
# expect the Guardian/RL dashboard title
```

---

## 🌙 Nightly Soak (optional but recommended)

1. **Commit the workflow** `.github/workflows/rc-soak-daily.yml`.
2. **Add repo secrets**:

* `RC_FACADE_URL` → your façade (e.g., `https://staging.lukhas.ai`)
* `RC_PROM_URL` → your Prometheus (`https://prom.staging...`)

3. **Run locally anytime**

```bash
chmod +x scripts/rc_soak_health_check.sh
./scripts/rc_soak_health_check.sh
# writes docs/audits/rc-soak/SOAK_<timestamp>.{json,md}
```

---

## 🤝 Agent setup update (per your new plan)

* We’ll operate with **two agents only**:

  * **Copilot** → covers all prior “Claude Code” responsibilities (Testing/API/Observability/CI/DX).
  * **Codex** → scoped lint/refactors and hot-path code hygiene.
* I’ve structured everything above to avoid collisions (no runtime code touched).
  If you want, I can also output quick patches for:

  * Updating `TEAM_STATUS.md` to reflect “Copilot + Codex only”.
  * Tuning the multi-agent brief to reference separate **worktrees** per agent (that’s still the best practice).

---
sweet — here are two ready-to-apply patches that (1) collapse the team to **Copilot + Codex only**, and (2) codify the **worktree + lock** protocol to avoid collisions.

### How to apply

```bash
# from repo root
git checkout -b chore/docs-update-agents-workflow
# paste & save each diff below to /tmp/patch-TEAM_STATUS.diff and /tmp/patch-MULTI_AGENT_BRIEF.diff
git apply --whitespace=fix /tmp/patch-TEAM_STATUS.diff
git apply --whitespace=fix /tmp/patch-MULTI_AGENT_BRIEF.diff
git add docs/gonzo/audits/TEAM_STATUS.md docs/gonzo/MULTI_AGENT_BRIEF.md
git commit -m "docs(ops): two-agent plan (Copilot+Codex), worktree & lock protocol"
```

---

## Patch 1 — `docs/gonzo/audits/TEAM_STATUS.md`

```diff
*** a/docs/gonzo/audits/TEAM_STATUS.md
--- b/docs/gonzo/audits/TEAM_STATUS.md
@@
-# Team Status
-
-This document tracks active agents, ownership, and branch/worktree coordination.
+# Team Status (Two-Agent Mode)
+
+This document tracks **active agents**, **ownership**, and **worktree/lock coordination** in the post-RC flow.  
+As of v0.9.0-rc, we operate with **two agents only**: **Copilot** and **Codex**.
 
 ## Active Agents & Ownership
-
-| Agent        | Worktree                     | Branch                         | Ownership                                               | Status |
-|--------------|------------------------------|--------------------------------|---------------------------------------------------------|--------|
-| Claude Code  | `Lukhas` (root)              | `main`                         | Testing/API, Observability, CI, DX (Phase 2 complete)  | ✅     |
-| Codex        | `../Lukhas-codex-B1`         | `fix/codex10/ruffB1`           | Hot-path lint/refactor (reliability, observability)    | 🟢     |
-| GitHub Copilot | `../Lukhas-copilot-dx2`    | `docs/copilot/quickstart-polish` | DX/docs/examples (Phase 2 complete)                   | ✅     |
+| Agent   | Default Worktree             | Typical Branch Prefix         | Ownership (live)                                                                 | Status |
+|--------|-------------------------------|-------------------------------|-----------------------------------------------------------------------------------|--------|
+| **Copilot** | `../Lukhas-copilot`         | `ops/` `docs/` `feat/`        | Testing/API façade, Observability/CI, DX/docs, Release ops, Health artifacts      | 🟢 Active |
+| **Codex**   | `../Lukhas-codex`           | `fix/codex10/*` `chore/*`     | Hot-path hygiene (adapters/reliability/observability/MATRIZ), codemods, lint gates| 🟢 Active |
 
 ## Current CI Gates (must stay green)
 
 - `ruff-phaseA` (stable)
-- `ruff-phaseB-hotpaths` (≤120 diagnostics)
+- `ruff-phaseB-hotpaths` (≤120 diagnostics; target ≤50 displayed in PR badge)
 - `facade-smoke` (authenticated default)
 - `openapi-spec` + `openapi-headers-guard`
 - `compat-enforce` (0 hits)
 
+## Worktree & Lock Protocol
+
+- Use **one worktree per agent** to avoid git index collisions:
+  - Copilot → `../Lukhas-copilot`
+  - Codex → `../Lukhas-codex`
+- Claim a logical area via lightweight lock files:
+  - Create: `.dev/locks/<area>.lock` (text file with: agent, branch, date, scope)
+  - Remove on merge: delete the lock in the same PR
+- Typical areas: `adapters`, `reliability`, `observability`, `matriz-core`, `docs`, `ci`
+- `.gitignore` already ignores `.dev/locks/*.lock` and local `Lukhas-*` worktrees.
+
 ## Branch & PR Hygiene
 
 - Keep slices ≤20 files when fixing E402/E70x (Phase-B.x).
 - Prefer rebase over merge; rerere is enabled globally.
 - Follow T4 commit format (Problem → Solution → Impact → Task/Ref).
 
+## Retired / Archived
+
+| Item | Action | Reference |
+|------|--------|-----------|
+| `feat-jules-ruff-complete` | Archived & removed | Tag: `archive/feat-jules-ruff-complete-20251014` |
+
 ## Status Notes
-
-- Phase-B.1 active (Codex). DX polish and GA guard pack complete on main.
+- Phase-B.1 active (**Codex**). GA guard pack + DX polish merged via **Copilot**.
+- Monitoring stack (rules, alerts, dashboard) is ready; deploy per runbook.
```

---

## Patch 2 — `docs/gonzo/MULTI_AGENT_BRIEF.md`

```diff
*** a/docs/gonzo/MULTI_AGENT_BRIEF.md
--- b/docs/gonzo/MULTI_AGENT_BRIEF.md
@@
-# Multi-Agent Brief
-
-This brief coordinates Claude Code, Codex, and GitHub Copilot across worktrees.
+# Multi-Agent Brief (Two-Agent Mode)
+
+This brief coordinates **Copilot** and **Codex** across **separate worktrees** with a lightweight lock protocol.  
+Goal: zero collisions, fast iteration, clean CI.
 
-## Agents
+## Agents & Scope
 
-1) **Claude Code** — Testing/API, Observability, CI, DX  
-2) **Codex** — Hot-path lint/refactor, codemods, hygiene  
-3) **GitHub Copilot** — Docs/examples/SDKs/quickstarts
+1) **Copilot**  
+   - Owns: Testing/API façade, Observability (rules/alerts/dashboards), CI workflows, DX/docs, releases, health artifacts.  
+   - Safe areas: `.github/workflows/**`, `scripts/**`, `docs/**`, `lukhas/observability/**`, `lukhas/adapters/openai/api.py` (non-breaking ops), `Makefile` targets.  
+   - Avoid: invasive refactors in Codex hot-paths unless coordinated via locks.
+
+2) **Codex**  
+   - Owns: Hot-path hygiene (E402/E70x), codemods, import canonicalization in `lukhas/adapters/openai/**`, `lukhas/core/reliability/**`, `lukhas/observability/**`, `MATRIZ/core/**`.  
+   - Strategy: ≤20-file slices, rebase-first, CI gate `ruff-phaseB-hotpaths` enforced (≤120 diagnostics; target ≤50).
 
 ## Worktrees
 
-- Recommend one worktree per agent to avoid index churn:
-  - Root: `Lukhas` (main)
-  - Codex: `../Lukhas-codex-*`
-  - Copilot: `../Lukhas-copilot-*`
+- **One worktree per agent**:
+  - Copilot → `../Lukhas-copilot`
+  - Codex → `../Lukhas-codex`
+- Keep branches small and purpose-scoped:
+  - Copilot: `ops/*`, `docs/*`, `feat/*`
+  - Codex: `fix/codex10/*`, `chore/*`
 
 ## Lock Protocol
 
-- Lightweight locks live under `.dev/locks/`. Put a simple text file like `adapters.lock` with:
-  - agent, branch, date, scope
-- Remove the lock in the PR that merges the work.
+- Create `.dev/locks/<area>.lock` before you start (content: agent, branch, date, scope).
+- Remove the lock in the same PR that merges the work.
+- Typical areas: `adapters`, `reliability`, `observability`, `matriz-core`, `docs`, `ci`.
+- `.gitignore` ignores `.dev/locks/*.lock`; never commit workstation-specific paths.
 
 ## Collision Rules
 
 - Copilot avoids structural import rewrites in hot-paths unless lock taken.
 - Codex avoids changing CI/DX/docs without quick sync (or take `docs`/`ci` lock).
 - If both need `lukhas/adapters/openai/api.py`: Copilot may add **non-breaking** ops hooks (headers, health, tracing); Codex may alter **import topology**; coordinate via `adapters.lock`.
 
 ## CI Guardrails (must remain green)
 
 - `ruff-phaseA` — repo-wide baseline
 - `ruff-phaseB-hotpaths` — adapters/reliability/observability/MATRIZ core (≤120; target ≤50)
 - `facade-smoke` — uses shared auth fixture (authenticated by default)
 - `openapi-spec` + `openapi-headers-guard`
 - `compat-enforce` — must be 0
 - Nightly strict-mode rehearsal (delta tracked)
 
 ## PR & Commit Etiquette
 
 - T4 style: **Problem → Solution → Impact → Refs**.
 - Prefer **rebase**; `rerere` is enabled for smoother repeats.
 - Keep changes reviewable (<20 files per slice for Phase-B).
 - Include verification commands in PR body (ruff stats, pytest focus).
 
 ## Ownership Map (Globs)
 
 - Copilot:
   - `.github/workflows/**`, `docs/**`, `scripts/**`, `lukhas/observability/**`, `docs/postman/**`
   - `lukhas/adapters/openai/api.py` (observability/error envelope/headers/health only)
 - Codex:
   - `lukhas/adapters/openai/**`, `lukhas/core/reliability/**`, `lukhas/observability/**`, `MATRIZ/core/**`, `MATRIZ/interfaces/api_server.py`
   - Test renames to track lane changes; import canonicalization & TID252.
 
 ## Day-2 Ops (post-RC)
 
 - Copilot deploys monitoring (Prom/Grafana), keeps dashboards/alerting in sync.
 - Codex reduces lint debt in **hot-paths** first; CI threshold remains 120 until PR badge target ≤50 is reached.
 - Health artifacts: `docs/audits/health/latest.{json,md}` always updated by Copilot jobs.
 
 ## Acceptance Criteria
 
 - CI green across all guardrails above.
 - No lock violations (locks created/removed in PR).
 - Codex: each Phase-B.x slice shrinks hot-path diagnostics (badge shows progress).
 - Copilot: observability changes are additive (no runtime breakage).
```

---
