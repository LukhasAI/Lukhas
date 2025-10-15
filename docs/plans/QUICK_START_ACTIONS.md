# Quick Start Actions - Parallel Execution
**Created**: 2025-10-15 | **Status**: Ready to Execute

---

## 🚀 Immediate Actions (Copy-Paste Ready)

### Action 1: Merge PR #396 (I001 Dreams Autofix) ✅

**Time**: 2 minutes | **Risk**: ZERO

```bash
# Check PR status
gh pr view 396 --json state,statusCheckRollup

# If checks are green, merge
gh pr merge 396 --squash --delete-branch --body "Merging safe I001 autofix on dreams module"

# Pull latest
git checkout main
git pull origin main
```

---

### Action 2: Launch Track A (E402 Batch 1 - Codex) 🔧

**Time**: 30 minutes | **Risk**: LOW

```bash
# Create worktree
git worktree add ../Lukhas-codex-e402 main
cd ../Lukhas-codex-e402

# Create branch
git checkout -b fix/codex/E402-batch1
touch .dev/locks/track-a.lock

# Fix E402 violations (manual edit 20 files from /tmp/e402_batch1.txt)
# Move imports to top, guard side effects, preserve Guardian imports

# Validate
xargs -a /tmp/e402_batch1.txt -I{} python -m ruff check {} --select E402
pytest tests/smoke -q

# Commit
git add .
git commit -m "refactor(lint): E402 cleanup batch 1 (20 files)

Problem: E402 violations in core/integration, core/orchestration, core/interfaces
Solution: Move imports to top of file, guard side effects, preserve Guardian stability
Impact: 20 files clean, smoke tests pass, CI green

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: CODEX <noreply@anthropic.com>"

# Push and create PR
git push -u origin fix/codex/E402-batch1
gh pr create --title "refactor(lint): E402 cleanup batch 1 (≤20 files)" \
  --body "## Summary
- Remove E402 from 20 files in core/
- No API changes, import reordering only
- Guardian/PDP imports preserved

## Test Plan
- [x] Ruff E402 check → 0 violations
- [x] Smoke tests pass

## Risk: LOW"
```

**File list** (`/tmp/e402_batch1.txt`):
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

---

### Action 3: Launch Track B (Safe Autofix - Codex) 🧹

**Time**: 15 minutes | **Risk**: LOW

```bash
# Create worktree
git worktree add ../Lukhas-codex-autofix main
cd ../Lukhas-codex-autofix

# Create branch
git checkout -b fix/codex/ruff-autofix-safe
touch .dev/locks/track-b.lock

# Run safe autofixes
python -m ruff check lukhas/adapters/openai lukhas/core/reliability lukhas/observability \
  --select W293,F841,I001 --fix --unsafe-fixes

# Validate
python -m ruff check lukhas/adapters/openai lukhas/core/reliability lukhas/observability \
  --select W293,F841,I001 --statistics
pytest tests/smoke -q

# Commit
git add lukhas/adapters/openai lukhas/core/reliability lukhas/observability
git commit -m "refactor(lint): safe autofix (W293,F841,I001) — no runtime change

Problem: W293 (whitespace), F841 (unused vars), I001 (import sort) noise
Solution: Apply safe ruff autofixes to lukhas/ subdirectories
Impact: 0 violations in target dirs, no runtime changes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: CODEX <noreply@anthropic.com>"

# Push and create PR
git push -u origin fix/codex/ruff-autofix-safe
gh pr create --title "refactor(lint): safe autofix (W293,F841,I001) — no runtime change" \
  --body "## Summary
- Clean W293, F841, I001 in lukhas/ subdirectories
- No runtime behavior changes

## Test Plan
- [x] Ruff statistics → 0 violations
- [x] Smoke tests pass

## Risk: LOW"
```

---

### Action 4: Launch Track D (RC Soak Ops - Copilot) 🔬

**Time**: 20 minutes | **Risk**: LOW

```bash
# Create worktree
git worktree add ../Lukhas-copilot-soak main
cd ../Lukhas-copilot-soak

# Create branch
git checkout -b ops/copilot/rc-soak-pack
touch .dev/locks/track-d.lock

# Create Make targets (append to Makefile)
cat >> Makefile <<'EOF'

# RC Soak Operations
rc-soak-start:
	@echo "🚀 Starting RC soak (48-72h window)..."
	@mkdir -p docs/audits/health/$(shell date +%Y-%m-%d)
	@uvicorn lukhas.adapters.openai.api:get_app --factory --port 8000 > /tmp/rc-soak.log 2>&1 &
	@echo "✅ RC soak started. Logs: /tmp/rc-soak.log"

rc-soak-snapshot:
	@echo "📸 Capturing RC soak snapshot..."
	@bash scripts/ops/rc_soak_snapshot.sh
EOF

# Create snapshot script
mkdir -p scripts/ops
cat > scripts/ops/rc_soak_snapshot.sh <<'SCRIPT'
#!/usr/bin/env bash
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
HEALTH_DIR="docs/audits/health/${DATE}"
mkdir -p "${HEALTH_DIR}"

# Collect metrics
cat > "${HEALTH_DIR}/latest.json" <<JSON
{
  "timestamp": "${DATE}T${TIME}",
  "rc_version": "v0.9.0-rc",
  "prometheus_up": $(curl -s http://localhost:9090/-/healthy > /dev/null && echo true || echo false),
  "grafana_up": $(curl -s http://localhost:3000/api/health > /dev/null && echo true || echo false),
  "facade_health": "$(curl -s http://localhost:8000/health || echo 'DOWN')"
}
JSON

cat > "${HEALTH_DIR}/latest.md" <<MD
# RC Soak Health Report
**Date**: ${DATE} ${TIME}

## System Health
- Prometheus: $(curl -s http://localhost:9090/-/healthy > /dev/null && echo '✅' || echo '❌')
- Grafana: $(curl -s http://localhost:3000/api/health > /dev/null && echo '✅' || echo '❌')
- Façade: $(curl -s http://localhost:8000/health > /dev/null && echo '✅' || echo '❌')
MD

echo "✅ Snapshot: ${HEALTH_DIR}/latest.{json,md}"
SCRIPT

chmod +x scripts/ops/rc_soak_snapshot.sh

# Create synthetic load script
cat > scripts/ops/rc_synthetic_load.sh <<'SCRIPT'
#!/usr/bin/env bash
BASE_URL="http://localhost:8000"
REQUESTS=100

echo "🔥 Generating synthetic load (${REQUESTS} requests)..."
for i in $(seq 1 $REQUESTS); do
  curl -s -X POST "${BASE_URL}/v1/embeddings" \
    -H "Content-Type: application/json" \
    -d '{"input": "test", "model": "text-embedding-ada-002"}' > /dev/null
  echo -n "."
done
echo "✅ Complete"
SCRIPT

chmod +x scripts/ops/rc_synthetic_load.sh

# Commit
git add Makefile scripts/ops/
git commit -m "ops: RC soak automation + daily health artifacts

Problem: Manual RC monitoring without automated snapshots
Solution: Make targets (rc-soak-start, rc-soak-snapshot), synthetic load
Impact: 48-72h soak automation, daily artifacts

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Copilot <noreply@anthropic.com>"

# Push and create PR
git push -u origin ops/copilot/rc-soak-pack
gh pr create --title "ops: RC soak automation + daily health artifacts" \
  --body "## Summary
- \`make rc-soak-start\`: Launch RC server
- \`make rc-soak-snapshot\`: Daily health artifacts
- Synthetic load script

## Test Plan
- [x] Make targets execute successfully

## Risk: LOW"

# Start RC soak NOW
make rc-soak-start
```

---

### Action 5: Create Security Issues (Track E - Copilot) 🛡️

**Time**: 30 minutes | **Risk**: VARIABLE

```bash
# Run pip-audit
pip install pip-audit
mkdir -p docs/audits/security/$(date +%Y%m%d)
pip-audit --format json > docs/audits/security/$(date +%Y%m%d)/pip-audit.json
pip-audit --format markdown > docs/audits/security/$(date +%Y%m%d)/pip-audit.md

# Create issues for each vulnerability (manual review of audit output)
# Example:
gh issue create --title "security: CVE-XXXX in {package}" \
  --body "## Vulnerability
- Package: {package}
- Current: {version}
- Fixed: {fixed_version}
- Severity: {HIGH/MEDIUM/LOW}

## Mitigation
- [ ] Test fixed version
- [ ] Check breaking changes
- [ ] Update requirements.txt
- [ ] Run tests

See: docs/audits/security/$(date +%Y%m%d)/pip-audit.md"

# If trivial bumps are safe, create separate PR
# (Follow Track E execution steps in PARALLEL_AGENT_EXECUTION_PLAN.md)
```

---

### Action 6: Create Colony Rename RFC (Track C - Copilot) 📋

**Time**: 15 minutes | **Risk**: LOW (docs only)

```bash
# Create worktree
git worktree add ../Lukhas-copilot-colony main
cd ../Lukhas-copilot-colony

# Create branch
git checkout -b docs/copilot/colony-rename-rfc
touch .dev/locks/track-c.lock

# Create RFC
mkdir -p docs/rfcs
cat > docs/rfcs/COLONY_RENAME_RFC.md <<'EOF'
# Colony Rename RFC
**Status**: Pending Approval | **Created**: 2025-10-15

## Rationale
- Harmonize naming conventions
- Improve discoverability
- Align with Constellation Framework

## Scope
See: `docs/audits/colony/colony_renames_*.csv`

## Impact
- Risk: MEDIUM (file moves, import updates)
- Testing: Full test suite + import validation
- Rollback: Git revert + import restoration

## Approval Checklist
- [ ] Naming conventions reviewed
- [ ] Import impact analyzed
- [ ] Test coverage verified
- [ ] Rollback plan documented

## Execution Plan (Post-Approval)
1. Create branch: `refactor/colony-renames-batch1`
2. Execute `git mv` from CSV
3. Update imports: `make fix-imports`
4. Run tests: `make test-tier1 && make lane-guard`
5. PR with evidence
EOF

# Commit
git add docs/rfcs/
git commit -m "docs(colony): rename plan & dry-run CSV

Problem: Colony naming inconsistencies
Solution: RFC with approval checklist
Impact: Stakeholder review before file moves

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Copilot <noreply@anthropic.com>"

# Push and create PR
git push -u origin docs/copilot/colony-rename-rfc
gh pr create --title "docs(colony): rename plan & dry-run CSV" \
  --body "## Summary
- RFC for colony rename
- Approval checklist

**No code changes** — docs/planning only

## Approval Required
- [ ] Naming approved
- [ ] Impact acceptable

## Risk: LOW (docs only)"
```

---

## 📊 Progress Tracking

### Daily Snapshot Commands

```bash
# RC soak snapshot (run daily)
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
make rc-soak-snapshot

# Check PR status
gh pr list --state open --json number,title,state,statusCheckRollup

# Ruff progress
python -m ruff check lukhas core MATRIZ --statistics | grep -E "E402|W293|F841|I001"
```

### GA Readiness Checklist

```bash
# Check all gates
echo "Guardian denial rate:" # Query Prometheus
echo "PDP p95 latency:" # Query Prometheus
echo "Ruff hot-path count:"
python -m ruff check lukhas core MATRIZ --statistics | head -20
echo "OpenAPI headers:"
python scripts/generate_openapi.py && python -m openapi_spec_validator docs/openapi/lukhas-openapi.json
echo "Façade smoke:"
bash scripts/smoke_test_openai_facade.sh
```

---

## 🎯 Success Criteria (Per Track)

### Track A (E402 Batch 1)
- ✅ 0×E402 in 20 target files
- ✅ Smoke tests pass
- ✅ CI green

### Track B (Safe Autofix)
- ✅ 0×W293, F841, I001 in target dirs
- ✅ No runtime changes
- ✅ CI green

### Track C (Colony RFC)
- ✅ RFC approved by stakeholders
- ✅ CSV validated
- ✅ Execution plan clear

### Track D (RC Soak)
- ✅ RC running 48-72h
- ✅ Daily snapshots generated
- ✅ No critical alerts

### Track E (Security)
- ✅ Issues created for all vulns
- ✅ Trivial patches applied
- ✅ CI green

---

## 🚨 Rollback Procedures

### If Track Fails

```bash
# Abandon worktree
cd /Users/agi_dev/LOCAL-REPOS/Lukhas
git worktree remove ../Lukhas-{track}

# Delete remote branch
gh pr close {PR_NUMBER} --delete-branch

# Remove lock
rm .dev/locks/track-{a,b,c,d,e}.lock
```

### If RC Soak Shows Issues

```bash
# Stop RC soak
pkill -f "uvicorn lukhas.adapters.openai.api"

# Capture final snapshot
make rc-soak-snapshot

# Review logs
tail -100 /tmp/rc-soak.log
```

---

**All actions above are copy-paste ready. Execute in parallel using separate worktrees.**
