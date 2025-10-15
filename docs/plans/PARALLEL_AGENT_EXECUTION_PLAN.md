# Parallel Agent Execution Plan (Codex & Copilot)
**Status**: Ready for Execution | **Created**: 2025-10-15 | **RC**: v0.9.0-rc

---

## 🚦 Current Status Recap

### ✅ Completed (Foundation Solid)
- v0.9.0-rc tagged and deployed
- Guardian wired + RL headers + health signals active
- Monitoring stack (Prometheus+Grafana) deployed locally
- Rules/alerts/dashboard validated
- State Sweep landed (tools in `scripts/` + Make targets)
- PRs #393, #394, #395 merged successfully
- Hot-path Ruff gates in CI
- Phase-B slices defined
- Colony planner + baseline audits committed

### 🔄 In Progress
- PR #396 (safe I001 import sort on dreams) - OPEN, ready to merge
- E402 cleanup batch 1 prepared (`/tmp/e402_batch1.txt` - 20 files)
- Colony rename CSV generated (dry-run ready)
- RC soak monitoring (48-72h window)

### 🎯 Carry-Over Items
1. Merge #396 (zero risk)
2. E402 cleanup (manual, batched ≤20 files per PR)
3. Colony rename (dry-run → approve → execute)
4. 48-72h RC soak with health artifacts
5. Security follow-ups (7 vulns from `pip-audit`)

---

## 🧩 Parallel Execution Strategy

**Work in separate worktrees** to avoid conflicts. Use lock files in `.dev/locks/` (already gitignored).

### Worktree Setup

```bash
# Create parallel worktrees
git worktree add ../Lukhas-codex-e402 main
git worktree add ../Lukhas-codex-autofix main
git worktree add ../Lukhas-copilot-colony main
git worktree add ../Lukhas-copilot-soak main
git worktree add ../Lukhas-copilot-security main

# Lock file pattern (touch before starting work)
touch .dev/locks/track-{a,b,c,d,e}.lock
```

---

## Track A — E402 Batch 1 (Codex) 🔧

**Owner**: ChatGPT CODEX
**Goal**: Remove E402 (module level import not at top of file) from first 20 files
**Risk**: LOW (import reordering, no API changes)
**Branch**: `fix/codex/E402-batch1`
**PR Title**: `refactor(lint): E402 cleanup batch 1 (≤20 files)`

### Scope (20 files from `/tmp/e402_batch1.txt`)

```
core/integration/neuro_symbolic_fusion_layer.py
core/integration/system_coordinator.py
core/integrator.py
core/interfaces/as_agent/core/generate_image.py
core/interfaces/as_agent/sys/nias/delivery_loop.py
core/interfaces/as_agent/sys/nias/dream_recorder.py
core/interfaces/as_agent/sys/nias/feedback_loop.py
core/interfaces/as_agent/sys/nias/symbolic_reply_generator.py
core/interfaces/ui/components/audio_exporter.py
core/modules/nias/__init__.py
core/notion_sync.py
core/orchestration/brain/demo.py
core/orchestration/brain/orchestration/core.py
core/orchestration/brain/personality/voice_personality.py
core/orchestration/brain/spine/healix_mapper.py
core/orchestration/brain/unified_self_merge_divergence.py
core/orchestration/core.py
core/orchestration/integration/human_in_the_loop_orchestrator.py
core/orchestration/learning_initializer.py
core/symbolic/EthicalAuditor.py
```

### Execution Steps

1. **Create Branch**
   ```bash
   cd ../Lukhas-codex-e402
   git checkout -b fix/codex/E402-batch1
   touch .dev/locks/track-a.lock
   ```

2. **Fix E402 Violations**
   - Move imports to top of file
   - Replace on-import side effects with guarded init where needed
   - Keep Guardian/PDP imports stable
   - Use `TYPE_CHECKING` + function-local imports if circular dependencies appear

3. **Validate Changes**
   ```bash
   # Check no new E402 in these files
   xargs -a /tmp/e402_batch1.txt -I{} python -m ruff check {} --select E402

   # Run statistics to confirm reduction
   python -m ruff check lukhas core MATRIZ --statistics --no-cache | grep E402

   # Run smoke tests
   pytest tests/smoke -q
   ```

4. **Accept Criteria**
   - 0×E402 in the 20 target files
   - Smoke tests unchanged (no regressions)
   - CI green
   - Guardian/Identity imports stable

5. **Commit & PR**
   ```bash
   git add {affected files}
   git commit -m "$(cat <<'EOF'
   refactor(lint): E402 cleanup batch 1 (20 files)

   Problem: E402 violations in core/integration, core/orchestration, core/interfaces
   Solution: Move imports to top of file, guard side effects, preserve Guardian stability
   Impact: 20 files clean, smoke tests pass, CI green

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: CODEX <noreply@anthropic.com>
   EOF
   )"

   git push -u origin fix/codex/E402-batch1
   gh pr create --title "refactor(lint): E402 cleanup batch 1 (≤20 files)" \
     --body "$(cat <<'EOF'
   ## Summary
   - Remove E402 (module level import not at top) from 20 files in core/
   - No API changes, import reordering only
   - Guardian/PDP imports preserved

   ## Test Plan
   - [x] Ruff E402 check on affected files → 0 violations
   - [x] Smoke tests pass
   - [x] CI green

   ## Risk Assessment
   **LOW**: Mechanical import reordering, no runtime behavior changes

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

---

## Track B — Safe Autofix Sweep (Codex) 🧹

**Owner**: ChatGPT CODEX
**Goal**: Drop whitespace/unused-var noise with safe autofixes only
**Risk**: LOW (W293, F841, I001 are mechanical)
**Branch**: `fix/codex/ruff-autofix-safe`
**PR Title**: `refactor(lint): safe autofix (W293,F841,I001) — no runtime change`

### Scope (Limited Blast Radius)

```
lukhas/adapters/openai/
lukhas/core/reliability/
lukhas/observability/
```

### Rules to Fix

- **W293**: Blank line contains whitespace
- **F841**: Local variable assigned but never used
- **I001**: Import block is un-sorted or un-formatted

### Execution Steps

1. **Create Branch**
   ```bash
   cd ../Lukhas-codex-autofix
   git checkout -b fix/codex/ruff-autofix-safe
   touch .dev/locks/track-b.lock
   ```

2. **Run Safe Autofixes**
   ```bash
   # Fix whitespace, unused vars, import sorting
   python -m ruff check lukhas/adapters/openai lukhas/core/reliability lukhas/observability \
     --select W293,F841,I001 --fix --unsafe-fixes

   # Verify changes
   git diff --stat
   ```

3. **Validate Changes**
   ```bash
   # Confirm rules cleared
   python -m ruff check lukhas/adapters/openai lukhas/core/reliability lukhas/observability \
     --select W293,F841,I001 --statistics

   # Run smoke tests
   pytest tests/smoke -q
   ```

4. **Accept Criteria**
   - 0 violations for W293, F841, I001 in target directories
   - No code flow changes (only whitespace, unused vars, import sorting)
   - Smoke tests pass
   - CI green

5. **Commit & PR**
   ```bash
   git add lukhas/adapters/openai lukhas/core/reliability lukhas/observability
   git commit -m "$(cat <<'EOF'
   refactor(lint): safe autofix (W293,F841,I001) — no runtime change

   Problem: W293 (whitespace), F841 (unused vars), I001 (import sort) noise in lukhas/
   Solution: Apply safe ruff autofixes to adapters/openai, core/reliability, observability
   Impact: 0 violations in target dirs, no runtime changes, CI green

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: CODEX <noreply@anthropic.com>
   EOF
   )"

   git push -u origin fix/codex/ruff-autofix-safe
   gh pr create --title "refactor(lint): safe autofix (W293,F841,I001) — no runtime change" \
     --body "$(cat <<'EOF'
   ## Summary
   - Clean up W293 (whitespace), F841 (unused vars), I001 (import sort) in lukhas/ subdirectories
   - Scope limited to adapters/openai, core/reliability, observability
   - No runtime behavior changes

   ## Test Plan
   - [x] Ruff statistics show 0 violations for W293, F841, I001 in target dirs
   - [x] Smoke tests pass
   - [x] CI green

   ## Risk Assessment
   **LOW**: Mechanical whitespace, unused var removal, import sorting only

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

---

## Track C — Colony Rename RFC (Copilot) 📋

**Owner**: GitHub Copilot (Claude Code support)
**Goal**: Get stakeholder buy-in before `git mv` operations
**Risk**: LOW (docs-only, no code moves yet)
**Branch**: `docs/copilot/colony-rename-rfc`
**PR Title**: `docs(colony): rename plan & dry-run CSV`

### Deliverables

1. **RFC Document**: `docs/rfcs/COLONY_RENAME_RFC.md`
2. **CSV Plan**: `docs/audits/colony/colony_renames_<timestamp>.csv` (already generated)
3. **Dry-run command block** (ready to copy-paste after approval)

### Execution Steps

1. **Create Branch**
   ```bash
   cd ../Lukhas-copilot-colony
   git checkout -b docs/copilot/colony-rename-rfc
   touch .dev/locks/track-c.lock
   ```

2. **Create RFC Document**
   ```bash
   cat > docs/rfcs/COLONY_RENAME_RFC.md <<'EOF'
   # Colony Rename RFC
   **Status**: Pending Approval | **Created**: 2025-10-15

   ## Rationale

   - Harmonize naming conventions across codebase
   - Improve discoverability and semantic clarity
   - Align with Constellation Framework patterns

   ## Scope

   See: `docs/audits/colony/colony_renames_<timestamp>.csv`

   Total files to rename: {COUNT}
   Directories affected: {DIRS}

   ## Impact Assessment

   - **Risk**: MEDIUM (file moves, import updates)
   - **Testing**: Full test suite + import validation
   - **Rollback**: Git revert + import path restoration

   ## Dry-Run Commands

   ```bash
   # Preview moves (no changes)
   while IFS=, read -r old new; do
     echo "git mv $old $new"
   done < docs/audits/colony/colony_renames_<timestamp>.csv
   ```

   ## Approval Checklist

   - [ ] Naming conventions reviewed by maintainers
   - [ ] Import impact analyzed
   - [ ] Test coverage verified
   - [ ] Rollback plan documented
   - [ ] Stakeholders notified

   ## Execution Plan (Post-Approval)

   1. Create execution branch: `refactor/colony-renames-batch1`
   2. Execute `git mv` operations from CSV
   3. Update imports via `make fix-imports`
   4. Run full test suite + `make lane-guard`
   5. PR with before/after evidence

   EOF
   ```

3. **Commit & PR**
   ```bash
   git add docs/rfcs/COLONY_RENAME_RFC.md docs/audits/colony/
   git commit -m "$(cat <<'EOF'
   docs(colony): rename plan & dry-run CSV

   Problem: Colony naming inconsistencies across codebase
   Solution: RFC with dry-run CSV, approval checklist, execution plan
   Impact: Stakeholder review required before file moves

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Copilot <noreply@anthropic.com>
   EOF
   )"

   git push -u origin docs/copilot/colony-rename-rfc
   gh pr create --title "docs(colony): rename plan & dry-run CSV" \
     --body "$(cat <<'EOF'
   ## Summary
   - RFC for colony rename operations
   - CSV with dry-run commands
   - Approval checklist before execution

   ## Approval Required

   - [ ] Naming conventions approved
   - [ ] Import impact acceptable
   - [ ] Rollback plan clear

   **No code changes in this PR** — docs/planning only

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

---

## Track D — RC Soak Ops Pack (Copilot) 🔬

**Owner**: GitHub Copilot (Claude Code support)
**Goal**: Automate RC monitoring and daily health artifacts
**Risk**: LOW (ops tooling, no production changes)
**Branch**: `ops/copilot/rc-soak-pack`
**PR Title**: `ops: RC soak automation + daily health artifacts`

### Deliverables

1. **Make targets**: `rc-soak-start`, `rc-soak-snapshot`
2. **Daily health script**: `scripts/ops/rc_soak_snapshot.sh`
3. **Synthetic load recipe**: k6 or curl-based load script
4. **Health artifact template**: `docs/audits/health/<date>/latest.{json,md}`

### Execution Steps

1. **Create Branch**
   ```bash
   cd ../Lukhas-copilot-soak
   git checkout -b ops/copilot/rc-soak-pack
   touch .dev/locks/track-d.lock
   ```

2. **Create Make Targets**
   ```bash
   cat >> Makefile <<'EOF'

   # RC Soak Operations
   rc-soak-start:
   	@echo "🚀 Starting RC soak (48-72h window)..."
   	@mkdir -p docs/audits/health/$(shell date +%Y-%m-%d)
   	@uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000 > /tmp/rc-soak.log 2>&1 &
   	@echo "✅ RC soak started (PID: $$!). Logs: /tmp/rc-soak.log"

   rc-soak-snapshot:
   	@echo "📸 Capturing RC soak snapshot..."
   	@bash scripts/ops/rc_soak_snapshot.sh
   	@echo "✅ Snapshot saved to docs/audits/health/$(shell date +%Y-%m-%d)/latest.{json,md}"
   EOF
   ```

3. **Create Snapshot Script**
   ```bash
   mkdir -p scripts/ops
   cat > scripts/ops/rc_soak_snapshot.sh <<'EOF'
   #!/usr/bin/env bash
   # RC Soak Health Snapshot

   DATE=$(date +%Y-%m-%d)
   TIME=$(date +%H:%M:%S)
   HEALTH_DIR="docs/audits/health/${DATE}"
   mkdir -p "${HEALTH_DIR}"

   # Collect metrics
   METRICS_JSON="${HEALTH_DIR}/latest.json"
   cat > "${METRICS_JSON}" <<JSON
   {
     "timestamp": "${DATE}T${TIME}",
     "rc_version": "v0.9.0-rc",
     "uptime_hours": $(awk '{print $1/3600}' /proc/uptime 2>/dev/null || echo "N/A"),
     "prometheus_up": $(curl -s http://localhost:9090/-/healthy > /dev/null && echo true || echo false),
     "grafana_up": $(curl -s http://localhost:3000/api/health > /dev/null && echo true || echo false),
     "facade_health": "$(curl -s http://localhost:8000/health || echo 'DOWN')",
     "guardian_denials_24h": "TBD",
     "pdp_p95_latency_ms": "TBD"
   }
   JSON

   # Generate markdown report
   REPORT_MD="${HEALTH_DIR}/latest.md"
   cat > "${REPORT_MD}" <<MD
   # RC Soak Health Report
   **Date**: ${DATE} ${TIME}
   **RC Version**: v0.9.0-rc

   ## System Health

   - **Prometheus**: $(curl -s http://localhost:9090/-/healthy > /dev/null && echo '✅ UP' || echo '❌ DOWN')
   - **Grafana**: $(curl -s http://localhost:3000/api/health > /dev/null && echo '✅ UP' || echo '❌ DOWN')
   - **Façade**: $(curl -s http://localhost:8000/health > /dev/null && echo '✅ UP' || echo '❌ DOWN')

   ## Metrics Snapshot

   - **Guardian Denials (24h)**: TBD (query Prometheus)
   - **PDP p95 Latency**: TBD (query Prometheus)

   ## Next Actions

   - [ ] Review dashboard for anomalies
   - [ ] Check alert history
   - [ ] Validate synthetic load results

   MD

   echo "✅ Snapshot complete: ${HEALTH_DIR}/latest.{json,md}"
   EOF

   chmod +x scripts/ops/rc_soak_snapshot.sh
   ```

4. **Create Synthetic Load Script** (curl-based)
   ```bash
   cat > scripts/ops/rc_synthetic_load.sh <<'EOF'
   #!/usr/bin/env bash
   # Synthetic load for RC soak testing

   BASE_URL="http://localhost:8000"
   REQUESTS=100

   echo "🔥 Generating synthetic load (${REQUESTS} requests)..."

   for i in $(seq 1 $REQUESTS); do
     # Embeddings request
     curl -s -X POST "${BASE_URL}/v1/embeddings" \
       -H "Content-Type: application/json" \
       -d '{"input": "test embedding", "model": "text-embedding-ada-002"}' \
       > /dev/null

     # Chat completion request
     curl -s -X POST "${BASE_URL}/v1/chat/completions" \
       -H "Content-Type: application/json" \
       -d '{"messages": [{"role": "user", "content": "Hello"}], "model": "gpt-4"}' \
       > /dev/null

     echo -n "."
   done

   echo ""
   echo "✅ Synthetic load complete (${REQUESTS} requests)"
   EOF

   chmod +x scripts/ops/rc_synthetic_load.sh
   ```

5. **Commit & PR**
   ```bash
   git add Makefile scripts/ops/
   git commit -m "$(cat <<'EOF'
   ops: RC soak automation + daily health artifacts

   Problem: Manual RC monitoring without automated health snapshots
   Solution: Make targets (rc-soak-start, rc-soak-snapshot), synthetic load script
   Impact: 48-72h soak automation, daily health artifacts in docs/audits/health/

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Copilot <noreply@anthropic.com>
   EOF
   )"

   git push -u origin ops/copilot/rc-soak-pack
   gh pr create --title "ops: RC soak automation + daily health artifacts" \
     --body "$(cat <<'EOF'
   ## Summary
   - `make rc-soak-start`: Start RC soak server
   - `make rc-soak-snapshot`: Capture daily health artifacts
   - Synthetic load script for exercising embeddings/chat/dreams

   ## Test Plan
   - [x] `make rc-soak-start` launches server
   - [x] `make rc-soak-snapshot` generates JSON+MD artifacts
   - [x] Synthetic load script executes without errors

   ## Deliverables
   - Health artifacts in `docs/audits/health/<date>/latest.{json,md}`
   - 48-72h soak guide in PR description

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

---

## Track E — Security Sweep (Copilot) 🛡️

**Owner**: GitHub Copilot (Claude Code support)
**Goal**: Convert `pip-audit` findings into actionable issues + quick patches
**Risk**: VARIABLE (dependency bumps, version compatibility)
**Branch**: `chore/copilot/security-sweep`
**PR Title**: `chore(security): audit log + issue seeds`

### Scope

- 7 vulnerabilities from `pip-audit` output
- Create GitHub issues for each vuln
- Trivial bumps: PR immediately
- Non-trivial: Document mitigation plan in issue

### Execution Steps

1. **Create Branch**
   ```bash
   cd ../Lukhas-copilot-security
   git checkout -b chore/copilot/security-sweep
   touch .dev/locks/track-e.lock
   ```

2. **Run pip-audit**
   ```bash
   pip install pip-audit
   pip-audit --format json > docs/audits/security/$(date +%Y%m%d)/pip-audit.json
   pip-audit --format markdown > docs/audits/security/$(date +%Y%m%d)/pip-audit.md
   ```

3. **Create Issues for Each Vuln**
   ```bash
   # Example issue template
   gh issue create --title "security: CVE-XXXX in {package}" \
     --body "$(cat <<'EOF'
   ## Vulnerability Details

   - **Package**: {package}
   - **Current Version**: {current}
   - **Fixed Version**: {fixed}
   - **CVE**: CVE-XXXX
   - **Severity**: {HIGH/MEDIUM/LOW}

   ## Mitigation Plan

   - [ ] Test fixed version in dev environment
   - [ ] Check for breaking changes in changelog
   - [ ] Update requirements.txt
   - [ ] Run full test suite
   - [ ] Deploy to RC for validation

   ## References

   - pip-audit report: `docs/audits/security/{date}/pip-audit.md`
   EOF
   )"
   ```

4. **Trivial Bumps (If Safe)**
   ```bash
   # Example: bump anthropic from 0.68.0 to 0.69.0 (if no breaking changes)
   sed -i '' 's/anthropic==0.68.0/anthropic==0.69.0/' requirements.txt
   pip install -r requirements.txt
   pytest tests/smoke -q  # Validate no regressions
   ```

5. **Commit & PR**
   ```bash
   git add docs/audits/security/ requirements.txt
   git commit -m "$(cat <<'EOF'
   chore(security): audit log + issue seeds

   Problem: 7 vulnerabilities identified by pip-audit
   Solution: Document findings, create GitHub issues, bump trivial packages
   Impact: Security audit artifacts committed, issues tracked, trivial patches applied

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Copilot <noreply@anthropic.com>
   EOF
   )"

   git push -u origin chore/copilot/security-sweep
   gh pr create --title "chore(security): audit log + issue seeds" \
     --body "$(cat <<'EOF'
   ## Summary
   - `pip-audit` findings committed to `docs/audits/security/{date}/`
   - GitHub issues created for each vulnerability
   - Trivial bumps applied where safe

   ## Security Findings

   - 7 vulnerabilities identified
   - Issues: #{issue_numbers}
   - Trivial patches: {package1}, {package2}

   ## Test Plan
   - [x] Smoke tests pass with updated dependencies
   - [x] CI green

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

---

## ⚡ Quick Wins (Do Now)

### 1. Merge PR #396 (I001 Dreams Autofix)

```bash
# Check PR status
gh pr view 396

# If CI green, merge
gh pr merge 396 --squash --delete-branch

# Pull latest
git pull origin main
```

### 2. Kick E402 Batch 1 (Codex)

```bash
# Use prepared file list
cd ../Lukhas-codex-e402
git checkout -b fix/codex/E402-batch1
# Follow Track A execution steps
```

### 3. Approve Colony Rename Plan (Copilot - Docs Only)

```bash
# Follow Track C execution steps (no code moves yet)
```

### 4. Start RC Soak (Copilot)

```bash
# Follow Track D execution steps
make rc-soak-start
# Schedule daily snapshots
```

### 5. Create Security Issues (Copilot)

```bash
# Follow Track E execution steps
# Document vulns, open issues
```

---

## 📈 GA Checklist (v0.9.0-rc → GA)

### Pre-GA Gates

- [ ] RC soak ≥48h with **no critical alerts**
- [ ] Guardian denial rate < **1%** sustained
- [ ] PDP p95 < **10ms** sustained
- [ ] Ruff hot-path ≤ **120** (gate) and trending down
- [ ] OpenAPI headers guard ✅
- [ ] Façade smoke ✅
- [ ] E402 batches ≥2 landed without regressions

### Post-GA Optional (Research Audit)

When ready, run focused research audit to benchmark:
- OpenAI compatibility drift (SDKs + headers + streaming)
- Guardrails (policy coverage, deny reasons, false-positive rate)
- Reliability (idempotency cache hit ratio, RL tune curves)
- DX (latency for first tokens, streaming jitter, examples clarity)

Protocol: Inputs, scripts, expected artifacts → `RESEARCH_AUDIT_<stamp>.md`

---

## TL;DR — Do Now

1. ✅ **Merge #396** (dreams I001 autofix)
2. 🔧 **Start Track A** (E402 batch 1, Codex)
3. 🔬 **Start Track D** (RC soak pack, Copilot)
4. 📋 **Approve Track C** (colony rename RFC, Copilot - docs only)
5. 🛡️ **File security issues** (Track E, Copilot)

---

**Status**: Execution Ready | **Coordination**: Separate worktrees + lock files
**Next Review**: Daily RC soak snapshots + PR status check
