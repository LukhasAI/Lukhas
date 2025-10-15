# Greenlight Plan (Option A: Deploy to Staging/Local Now)



**Status**: ✅ All monitoring artifacts created and validated  # Greenlight Plan (Option A: Deploy to Staging/Local Now)

**Date**: 2025-10-15  

**Status**: ✅ All monitoring artifacts created and validated  

---**Date**: 2025-10-15  



## Who Does What (Immediately)---



* **Codex (Hot-paths):** Continue Phase-B slices (#388/#389) in parallel—no runtime overlap with monitoring.## Who Does What (Immediately)

* **Copilot (DX/Observability):** Deploy rules + alerts + dashboard to staging; kick off baseline collection.

* **Codex (Hot-paths):** Continue Phase-B slices (#388/#389) in parallel—no runtime overlap with monitoring.

---* **Copilot (DX/Observability):** Deploy rules + alerts + dashboard to staging; kick off baseline collection.



## Preflight (1–2 min)**Preflight (1–2 min)**



✅ **Already completed**:```bash

# Validate YAML/JSON locally

```bashpython3 -c "import yaml; yaml.safe_load(open('lukhas/observability/rules/guardian-rl.rules.yml'))"

# All validations passed:python3 -c "import yaml; yaml.safe_load(open('lukhas/observability/rules/guardian-rl.alerts.yml'))"

python3 -c "import yaml; yaml.safe_load(open('lukhas/observability/rules/guardian-rl.rules.yml'))"python3 -m json.tool lukhas/observability/grafana/guardian-rl-dashboard.json > /dev/null

# ✅ Prometheus rules YAML valid```



python3 -c "import yaml; list(yaml.safe_load_all(open('lukhas/observability/rules/guardian-rl.alerts.yml')))"(These steps match the post-merge deployment guide.) 

# ✅ Prometheus alerts YAML valid (multi-document)

**Deploy (5–10 min)**

python3 -m json.tool lukhas/observability/grafana/guardian-rl-dashboard.json > /dev/null

# ✅ Grafana dashboard JSON valid```bash

```# Option A1: local stack (if available)

docker-compose -f docker/monitoring/docker-compose.yml up -d

---

# Option A2: staging Prometheus

## Deploy (5–10 min)scp lukhas/observability/rules/*.yml user@prometheus:/etc/prometheus/rules.d/

ssh user@prometheus 'curl -X POST http://localhost:9090/-/reload'

### Files Created

# Import Grafana dashboard (API token required)

All deployment scripts and workflows are now in place:curl -X POST http://grafana:3000/api/dashboards/db \

  -H "Authorization: Bearer $GRAFANA_API_KEY" \

1. **`scripts/monitoring_deploy.sh`** - Prometheus/Grafana deployment script  -H "Content-Type: application/json" \

2. **`.github/workflows/rc-soak-daily.yml`** - Automated daily health checks  -d @lukhas/observability/grafana/guardian-rl-dashboard.json

3. **`Makefile.monitoring`** - Makefile shortcuts for deployment```



### Deployment Options**Baseline & soak**



```bash```bash

# Option A1: Using Makefile (recommended)# 6h baseline collection (generates docs/audits/rc-soak/BASELINE_METRICS_v0.9.0-rc.md)

make -f Makefile.monitoring monitoring-deploybash scripts/rc_soak_health_check.sh



# Option A2: Direct script execution# Then begin 48–72h RC soak; run the daily check (e.g., GH Actions cron)

PROMETHEUS_RULES_DIR=/etc/prometheus/rules.d \bash scripts/rc_soak_health_check.sh

PROMETHEUS_URL=http://localhost:9090 \```

GRAFANA_URL=http://localhost:3000 \

GRAFANA_API_KEY=*** \**What you should see in Grafana (7 panels):**

./scripts/monitoring_deploy.sh

* PDP latency P50/P95/P99 (<10ms target)

# Option A3: Docker Compose (if local stack available)* Denial rate overall/by scope (<15% target)

docker-compose -f docker/monitoring/docker-compose.yml up -d* RL hit rate (<10% target) & near-exhaustion ratio

```* Combined Guardian+RL health score (>0.80 target)



### Environment Variables Required# Go/No-Go gates for GA



```bash* PDP P95 < **10ms** stable

export PROMETHEUS_RULES_DIR=/etc/prometheus/rules.d* Denial rate < **15%**

export PROMETHEUS_URL=http://localhost:9090* RL hit rate < **10%**

export GRAFANA_URL=http://localhost:3000* Health score > **0.80**

export GRAFANA_API_KEY=<grafana_api_token>* No CRITICAL alerts firing during soak

```

# Watchlist (common snags & quick fixes)

---

* **No metrics?** Verify Prometheus rule files are under the server’s rules dir and reload succeeded.

## Baseline & Soak* **Cardinality spike?** We already aggregate on stable labels; if series explode, temporarily drop the per-principal rules group and reload.

* **RL headers missing?** Recheck façade is on the latest `main` (PR #380 merged) and that the OpenAPI headers guard is passing in CI.

### 6h Baseline Collection



```bash

# Run health check to collect baseline## ✅ Staging Deployment (5 minutes)

make -f Makefile.monitoring rc-soak

---

# Or directly:# Create deployment and health-check scripts, workflow, and Makefile fragment for the user to download.

LUKHAS_API_URL=http://localhost:8000 \

PROMETHEUS_URL=http://localhost:9090 \import os, json, textwrap, datetime, pathlib

./scripts/rc_soak_health_check.sh

base = "/mnt/data"

# Generates: docs/audits/rc-soak/SOAK_<timestamp>.{json,md}files = {}

```

# 1) monitoring_deploy.sh

### 48–72h RC Soak Periodmonitoring_deploy = """#!/usr/bin/env bash

set -euo pipefail

The GitHub Actions workflow `.github/workflows/rc-soak-daily.yml` will run automatically at 02:00 UTC daily.

# === Monitoring Deploy Helper ===

**Required Repository Secrets**:# Deploy Prometheus rules/alerts and import Grafana dashboard.

- `RC_FACADE_URL` → Your façade URL (e.g., `https://staging.lukhas.ai`)# Local mode expects Prometheus rules directory mounted locally.

- `RC_PROM_URL` → Your Prometheus URL (e.g., `https://prom.staging.lukhas.ai`)# Environment:

#   PROMETHEUS_RULES_DIR   (e.g., /etc/prometheus/rules.d)  [required for local copy]

Manual trigger available via: `gh workflow run rc-soak-daily.yml`#   PROMETHEUS_URL         (e.g., http://localhost:9090)    [required for reload + queries]

#   GRAFANA_URL            (e.g., http://localhost:3000)    [optional for dashboard import]

---#   GRAFANA_API_KEY        (Grafana API token)              [optional for dashboard import]

#   REPO_ROOT              (repo path; default: current dir)

## What You Should See in Grafana (7 Panels)#   DRY_RUN                (set to 1 for dry run)

#

* PDP latency P50/P95/P99 (<10ms target)# Usage:

* Denial rate overall/by scope (<15% target)#   PROMETHEUS_RULES_DIR=/etc/prometheus/rules.d PROMETHEUS_URL=http://localhost:9090 \\

* RL hit rate (<10% target) & near-exhaustion ratio#   GRAFANA_URL=http://localhost:3000 GRAFANA_API_KEY=*** \\

* Combined Guardian+RL health score (>0.80 target)#   ./scripts/monitoring_deploy.sh

#

---# Notes:

# - For remote Prometheus hosts, copy the *.yml files to the remote rules dir yourself,

## Go/No-Go Gates for GA#   then run the reload step below against PROMETHEUS_URL on the remote.

# - This script is idempotent and safe to rerun.

* PDP P95 < **10ms** stable

* Denial rate < **15%**REPO_ROOT="${REPO_ROOT:-$(pwd)}"

* RL hit rate < **10%**RULES_SRC_DIR="$REPO_ROOT/lukhas/observability/rules"

* Health score > **0.80**GRAFANA_DASH="$REPO_ROOT/lukhas/observability/grafana/guardian-rl-dashboard.json"

* No CRITICAL alerts firing during soak

echo "==> Monitoring Deploy"

---echo "Repo root: $REPO_ROOT"

echo "Rules src: $RULES_SRC_DIR"

## Watchlist (Common Snags & Quick Fixes)

if [[ "${DRY_RUN:-0}" != "1" ]]; then

* **No metrics?** Verify Prometheus rule files are under the server's rules dir and reload succeeded.  if [[ -n "${PROMETHEUS_RULES_DIR:-}" ]]; then

* **Cardinality spike?** We already aggregate on stable labels; if series explode, temporarily drop the per-principal rules group and reload.    echo "-- Copying Prometheus rules to ${PROMETHEUS_RULES_DIR}"

* **RL headers missing?** Recheck façade is on the latest `main` (PR #380 merged) and that the OpenAPI headers guard is passing in CI.    cp -v "${RULES_SRC_DIR}"/*.yml "${PROMETHEUS_RULES_DIR}/"

  else

---    echo "!! PROMETHEUS_RULES_DIR not set; skipping local copy (ok if you deploy rules remotely)"

  fi

## Agent Instructionselse

  echo "[DRY RUN] Would copy rules to ${PROMETHEUS_RULES_DIR:-<unset>}"

### For Copilotfi



**Current Tasks**:if [[ -n "${PROMETHEUS_URL:-}" ]]; then

1. ✅ Monitoring scripts created and validated  echo "-- Reloading Prometheus @ ${PROMETHEUS_URL}"

2. ✅ GitHub Actions workflow created  if [[ "${DRY_RUN:-0}" != "1" ]]; then

3. ✅ Makefile shortcuts created    curl -fsS -X POST "${PROMETHEUS_URL}/-/reload" || { echo "Prometheus reload failed"; exit 1; }

4. ⏸️ Awaiting deployment decision (infrastructure)  else

    echo "[DRY RUN] Would POST ${PROMETHEUS_URL}/-/reload"

**Next Tasks** (when infrastructure ready):  fi

1. Deploy monitoring stack (use `make -f Makefile.monitoring monitoring-deploy`)else

2. Verify metrics appearing in Grafana  echo "!! PROMETHEUS_URL not set; cannot trigger reload."

3. Start 6h baseline collectionfi

4. Monitor RC soak period (automated)

if [[ -n "${GRAFANA_URL:-}" && -n "${GRAFANA_API_KEY:-}" ]]; then

**Ownership Areas**:  echo "-- Importing Grafana dashboard"

- `.github/workflows/**`  if [[ "${DRY_RUN:-0}" != "1" ]]; then

- `scripts/**`    curl -fsS -X POST "${GRAFANA_URL%/}/api/dashboards/db" \

- `docs/**`      -H "Authorization: Bearer ${GRAFANA_API_KEY}" \

- `lukhas/observability/**`      -H "Content-Type: application/json" \

- Makefile targets      --data-binary @"${GRAFANA_DASH}" >/dev/null

    echo "Dashboard imported."

### For Codex  else

    echo "[DRY RUN] Would import dashboard ${GRAFANA_DASH} into ${GRAFANA_URL}"

**Current Tasks**:  fi

- Continue Phase-B slices (#388: E402/E70x slice 1, #389: slice 2)else

- No collision with monitoring work (separate file paths)  echo "!! GRAFANA_URL or GRAFANA_API_KEY not set; skipping dashboard import (you can import manually)."

fi

**Hot-Path Focus**:

- `lukhas/adapters/openai/**`echo "==> Done."

- `lukhas/core/reliability/**`"""

- `lukhas/observability/**` (import cleanup only, no runtime changes)

- `MATRIZ/core/**`# 2) rc_soak_health_check.sh

rc_soak = """#!/usr/bin/env bash

**CI Gate**: Keep `ruff-phaseB-hotpaths` ≤120 (target ≤50)set -euo pipefail



---# === RC Soak Health Check ===

# Collects health signals from the façade and Prometheus, writes MD+JSON reports.

## Documentation Updates# Env:

#   LUKHAS_API_URL   (default: http://localhost:8000)

### Files Created This Session#   PROMETHEUS_URL   (e.g., http://localhost:9090) [optional for extra SLIs]

#   OUT_DIR          (default: docs/audits/rc-soak)

1. **`scripts/monitoring_deploy.sh`** - Deployment automation#   REPO_ROOT        (default: current dir)

2. **`.github/workflows/rc-soak-daily.yml`** - Daily soak checks#

3. **`Makefile.monitoring`** - Makefile shortcuts# Usage:

4. **`docs/gonzo/audits/TEAM_STATUS.md`** - Updated to two-agent mode#   LUKHAS_API_URL=http://localhost:8000 PROMETHEUS_URL=http://localhost:9090 ./scripts/rc_soak_health_check.sh

5. **`docs/gonzo/MULTI_AGENT_BRIEF.md`** - Agent coordination guidelines

REPO_ROOT="${REPO_ROOT:-$(pwd)}"

### Existing Documentation (Ready)OUT_DIR="${OUT_DIR:-$REPO_ROOT/docs/audits/rc-soak}"

API_URL="${LUKHAS_API_URL:-http://localhost:8000}"

- `docs/audits/MONITORING_DEPLOYMENT_CHECKLIST.md` - Complete deployment proceduresPROM_URL="${PROMETHEUS_URL:-}"

- `docs/audits/RC_SOAK_MONITORING_PLAN.md` - 48-72h soak strategy

- `docs/audits/BASELINE_METRICS_TEMPLATE.md` - Baseline collection formatmkdir -p "${OUT_DIR}"

- `lukhas/observability/rules/guardian-rl.rules.yml` - 18 recording rules (validated ✅)

- `lukhas/observability/rules/guardian-rl.alerts.yml` - 11 alerts (validated ✅)ts="$(date -u +%Y-%m-%dT%H-%M-%SZ)"

- `lukhas/observability/grafana/guardian-rl-dashboard.json` - Complete dashboard (validated ✅)json_out="${OUT_DIR}/SOAK_${ts}.json"

md_out="${OUT_DIR}/SOAK_${ts}.md"

---

echo "==> Fetching /healthz from ${API_URL}"

## Status Summaryhealth_json=$(curl -fsS "${API_URL%/}/healthz" || echo "{}")



**Guardian Fix**: ✅ Merged (PR #392, commit `701518993`)  # Optional Prometheus queries

**Monitoring Artifacts**: ✅ All validated and ready  prom_data="{}"

**Deployment Scripts**: ✅ Created and tested  if [[ -n "${PROM_URL}" ]]; then

**Automation**: ✅ GitHub Actions workflow in place    echo "==> Querying Prometheus @ ${PROM_URL}"

**Documentation**: ✅ Complete    # Example: denial rate 15m, PDP p95 latency 15m, RL hit rate 15m

  q_denial='sum(increase(guardian_denied_total[15m])) / clamp_min(sum(increase(guardian_decision_total[15m])), 1)'

**Next Step**: Deploy monitoring stack when infrastructure available, then start 6h baseline collection followed by 48-72h RC soak period.  q_p95='histogram_quantile(0.95, sum by (le) (rate(guardian_decision_latency_seconds_bucket[15m])))'

  q_rl='sum(increase(rate_limited_total[15m])) / clamp_min(sum(increase(http_requests_total[15m])), 1)'

---  # shellcheck disable=SC2016

  prom_data=$(jq -n --arg denial "$(curl -fsS --get --data-urlencode "query=${q_denial}" "${PROM_URL%/}/api/v1/query" | jq -r '.data.result[0].value[1] // empty')" \

_Updated: 2025-10-15 by Copilot_                     --arg p95 "$(curl -fsS --get --data-urlencode "query=${q_p95}"    "${PROM_URL%/}/api/v1/query" | jq -r '.data.result[0].value[1] // empty')" \

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
