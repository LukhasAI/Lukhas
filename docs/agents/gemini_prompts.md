# Gemini: Infrastructure & CI Designer Prompt (T4 / 0.01%)

Use this prompt when delegating infrastructure tasks to Gemini (IDE, Cloud, or API).

## Context

- **Repo**: LukhasAI/Lukhas
- **Your Role**: Infrastructure & CI Designer
- **Mission**: Build supply-chain security (SLSA), coverage pipelines, performance baselines, and monitoring dashboards
- **Standards**: T4/0.01% reliability, SLSA Level 2+, human-in-loop review
- **Collaboration**: Works with Claude Code (refactoring), Copilot (suggestions), Codex (batch automation)

## Task Pack Location

**📋 Complete Task Pack**: `docs/agents/tasks/GEMINI_PACK.md`

This file contains 5 comprehensive infrastructure tasks with:
- Executive summary and "What You've Learned About LUKHAS"
- Detailed task prompts for each infrastructure component
- Exact commands and file templates
- Validation steps and acceptance criteria
- Success metrics and safety gates

## Recommended Execution Strategy

### **Option 1: Parallel Cloud Execution** (Most Efficient) ⚡

Run tasks in parallel using Gemini Cloud or API for maximum speed:

```bash
# Terminal 1: SLSA Attestation PoC (Task 01)
gemini-api --task "Create SLSA attestation PoC per docs/agents/tasks/GEMINI_PACK.md Task 01" \
  --output-dir ./gemini_task01 &

# Terminal 2: Coverage Pipeline (Task 02)
gemini-api --task "Create coverage pipeline per docs/agents/tasks/GEMINI_PACK.md Task 02" \
  --output-dir ./gemini_task02 &

# Terminal 3: Performance Baselines (Task 03)
gemini-api --task "Create benchmarks per docs/agents/tasks/GEMINI_PACK.md Task 03" \
  --output-dir ./gemini_task03 &

# Wait for all tasks to complete
wait
```

**Why Parallel**:
- ✅ Tasks 01-03 are independent (no dependencies)
- ✅ Each operates on different file paths
- ✅ Reduces total time from ~5 days to ~2 days
- ✅ Review all outputs together before committing

### **Option 2: Ephemeral Worktree Execution** (Safest) 🛡️

Run each task in an isolated worktree to prevent main contamination:

```bash
# Task 01: SLSA in worktree
WT="/tmp/gemini_slsa"
git worktree add "$WT" origin/main
pushd "$WT"
  git checkout -b task/gemini-slsa-poc
  # Run Gemini Task 01 here
  # Create PR from worktree
popd
git worktree remove "$WT" --force

# Repeat for Tasks 02-05 in separate worktrees
```

**Why Ephemeral Worktrees**:
- ✅ Zero risk of contaminating main branch
- ✅ Each task has clean environment
- ✅ Easy to discard if task fails
- ✅ Lane-guard validation built-in

### **Option 3: Sequential IDE Execution** (Interactive)

Run tasks one-by-one in Gemini IDE chat for hands-on control:

```
You: Read docs/agents/tasks/GEMINI_PACK.md and execute Task 01 (SLSA Attestation PoC)
Gemini: [executes and creates files]
You: Review output, approve, move to Task 02
```

**Why Sequential**:
- ✅ Human review between tasks
- ✅ Immediate feedback on each task
- ✅ Easy to adjust based on learnings
- ⚠️ Slower (5+ days total)

## Gemini IDE Chat Prompt (Copy/Paste)

```
@gemini

I need you to build infrastructure for the LUKHAS AI platform. You are the Infrastructure & CI Designer working on supply-chain security, coverage pipelines, and monitoring.

**Your Task Pack**: Read `docs/agents/tasks/GEMINI_PACK.md` completely.

**Execution Strategy**: Parallel cloud execution (most efficient)

**Tasks to Execute** (in order of priority):

1. **Task 01 - SLSA Attestation PoC** (P1, ~1-2 days)
   - Create SLSA attestation pipeline for 10 modules
   - Use cosign + in-toto for signing
   - Branch: `task/gemini-slsa-poc`
   - **Start with this**: Copy the exact prompt from GEMINI_PACK.md Task 01

2. **Task 02 - Coverage Pipeline** (P1, ~1-2 days, can run parallel with Task 01)
   - Add pytest --cov + Codecov integration
   - Per-module threshold enforcement (75%+)
   - Branch: `task/gemini-coverage-pipeline`
   - **Parallel execution OK**: Independent from Task 01

3. **Task 03 - Performance Baselines** (P2, ~1-2 days, can run parallel with Tasks 01-02)
   - Create pytest-benchmark suite
   - Nightly CI job for regression detection
   - Branch: `task/gemini-benchmarking`
   - **Parallel execution OK**: Independent from Tasks 01-02

4. **Task 04 - Datadog Monitoring** (P2, ~3-5 days)
   - Create dashboard JSON with WaveC, lane-guard, endocrine widgets
   - Configure alert rules
   - Branch: `task/gemini-monitoring`
   - **Depends on**: Tasks 01-03 complete (needs metrics from those tasks)

5. **Task 05 - Key Management Runbook** (P2, ~1 day)
   - Document cosign/in-toto key generation
   - 90-day rotation procedure
   - Branch: `task/gemini-key-runbook`
   - **Can run parallel**: Documentation task

**Recommended Approach**:

Phase 1 (Parallel):
- Run Tasks 01, 02, 03 simultaneously in separate cloud instances or worktrees
- Total time: ~2 days instead of 5 days

Phase 2 (Sequential):
- Run Task 04 after reviewing Tasks 01-03 outputs (needs their metrics)
- Run Task 05 in parallel with Task 04
- Total time: ~3 days

**For each task**:
1. Read the task prompt from GEMINI_PACK.md
2. Create the branch specified
3. Execute all requirements (files, workflows, scripts, runbooks)
4. Run validation commands
5. Create PR with artifacts attached
6. Tag reviewers: @security_team, @ops_team

**Critical Safety Rules**:
- ✅ Never commit private keys (use GitHub Secrets)
- ✅ Always run lane-guard validation
- ✅ Human review required before merge
- ✅ No auto-merge on any infrastructure PRs
- ✅ Test all workflows in CI before approving

**Success Metrics** (track these):
- SLSA coverage: 0% → 80% (10 modules attested)
- Code coverage: 30% → 75% for production lanes
- Performance baselines: Established for MATRIZ (<250ms p95)
- Monitoring: Datadog dashboard with 12+ widgets
- Key rotation: 90-day cycle documented

**Artifacts Created** (reference these):
- `docs/agents/tasks/GEMINI_PACK.md` - Your complete task pack
- `docs/gonzo/AGENT_TASKS_TO_CREATE.md` - Original specifications
- `claude.me` - Multi-Agent Delegation section (context)
- `scripts/codemods/replace_labs_with_provider.py` - Codemod script (context)
- `scripts/automation/run_codmod_and_prs.sh` - Batch automation (Codex uses this)

**Integration with Other Agents**:
- **Claude Code**: Handles 10 high-priority files manually
- **Codex**: Handles 137 files via batch automation
- **You (Gemini)**: Monitor coverage after their changes, run SLSA attestation on their PRs

**Questions to Ask Me** (if needed):
1. Do you have access to GitHub Secrets for COSIGN_KEY, IN_TOTO_KEY?
2. Do you have Codecov account configured for this repo?
3. Do you have Datadog API keys for dashboard creation?
4. Should I use ephemeral worktrees or cloud parallel execution?

**Ready?** Start by reading GEMINI_PACK.md Task 01 and confirm you understand the SLSA attestation requirements. Then proceed with your chosen execution strategy (I recommend parallel cloud execution for speed).

Let's build T4 infrastructure! 🚀
```

## Quick Reference: File Locations

### Task Packs (All Agents)
- **Gemini (You)**: `docs/agents/tasks/GEMINI_PACK.md` (~700 lines, 5 tasks)
- **Claude Code**: `docs/agents/tasks/CLAUDE_CODE_PACK.md` (~800 lines, 10 tasks)
- **GitHub Copilot**: `docs/agents/tasks/GITHUB_COPILOT_PACK.md` (~500 lines, 6 templates)
- **Codex**: `docs/agents/tasks/CODEX_PACK.md` (~600 lines, 4 tasks)

### Source Documentation
- **Original Specs**: `docs/gonzo/AGENT_TASKS_TO_CREATE.md` (2,065 lines)
- **System Context**: `claude.me` (Multi-Agent Delegation section)
- **Architecture**: `lukhas_context.md` (for other AI tools)

### Scripts (Reference Only)
- **Codemod**: `scripts/codemods/replace_labs_with_provider.py`
- **Batch Automation**: `scripts/automation/run_codmod_and_prs.sh`
- **Lane Guard**: `scripts/run_lane_guard_worktree.sh`

## Task Priority Matrix

| Task | Priority | Time | Can Parallelize | Depends On |
|------|----------|------|-----------------|------------|
| Task 01 (SLSA) | P1 | 1-2 days | ✅ Yes | None |
| Task 02 (Coverage) | P1 | 1-2 days | ✅ Yes | None |
| Task 03 (Benchmarks) | P2 | 1-2 days | ✅ Yes | None |
| Task 04 (Monitoring) | P2 | 3-5 days | ⚠️ Partial | Tasks 01-03 (for metrics) |
| Task 05 (Key Mgmt) | P2 | 1 day | ✅ Yes | None |

**Optimal Parallel Groups**:
- **Group A** (start first): Tasks 01 + 02 + 03 + 05 (parallel, ~2 days)
- **Group B** (start after A): Task 04 (needs metrics from Group A, ~3 days)

**Total Time**:
- Sequential: ~9-12 days
- Parallel: ~5-7 days ⚡

## Validation Checklist (Before Creating PRs)

For each task, verify:

### SLSA (Task 01)
- [ ] `config/slsa_modules.yml` lists 10 modules
- [ ] `.github/workflows/slsa-attest-matrix.yml` runs in CI
- [ ] `scripts/verify_attestation.py` successfully verifies signature
- [ ] `security_posture_report.json` shows 100% coverage for PoC
- [ ] Public key committed to `docs/gonzo/cosign_pub.pem`

### Coverage (Task 02)
- [ ] `.github/workflows/coverage.yml` runs pytest --cov
- [ ] `scripts/ci/check_coverage.py` enforces 75%+ threshold
- [ ] Codecov integration shows module-level breakdown
- [ ] Coverage badge appears in README.md
- [ ] Test PR demonstrates coverage gate blocking <75%

### Benchmarks (Task 03)
- [ ] `benchmarks/test_matriz_performance.py` runs successfully
- [ ] Nightly workflow at 02:00 UTC configured
- [ ] Baseline files committed in `benchmarks/baselines/`
- [ ] `compare_benchmarks.py` detects >10% regressions
- [ ] Sample benchmark report shows MATRIZ <250ms p95

### Monitoring (Task 04)
- [ ] Dashboard JSON validated with `cat ... | jq '.'`
- [ ] Alert rules configured for critical thresholds
- [ ] `export_metrics.py` instruments WaveC, lane-guard, endocrine
- [ ] Screenshot of imported dashboard attached to PR
- [ ] Test alerts triggered in dry-run mode

### Key Management (Task 05)
- [ ] `KEY_MANAGEMENT_RUNBOOK.md` reviewed by Security
- [ ] `rotate_keys.sh` tested in dry-run mode
- [ ] `verify_key_age.py` correctly calculates age
- [ ] Weekly workflow creates Issue when keys >80 days
- [ ] Audit log template committed

## Security & Safety Notes

### Secrets Management
**NEVER commit these** (use GitHub Secrets):
- `COSIGN_KEY` (cosign private key)
- `IN_TOTO_KEY` (in-toto private key)
- `CODECOV_TOKEN` (Codecov API token)
- `DD_API_KEY` (Datadog API key)

**Safe to commit** (public keys):
- `docs/gonzo/cosign_pub.pem` (cosign public key)
- `docs/gonzo/in_toto_pub.pem` (in-toto public key)

### GitHub Secrets Setup Commands

```bash
# SLSA keys (generate first with: cosign generate-key-pair)
gh secret set COSIGN_KEY --repo LukhasAI/Lukhas --body "$(cat cosign.key)"
gh secret set IN_TOTO_KEY --repo LukhasAI/Lukhas --body "$(cat in_toto_key.pem)"

# Codecov (get from https://app.codecov.io/gh/LukhasAI/Lukhas)
gh secret set CODECOV_TOKEN --repo LukhasAI/Lukhas --body "your-token-here"

# Datadog (get from https://app.datadoghq.com/organization-settings/api-keys)
gh secret set DD_API_KEY --repo LukhasAI/Lukhas --body "your-dd-api-key"
gh secret set DD_APP_KEY --repo LukhasAI/Lukhas --body "your-dd-app-key"
```

### Human-in-Loop Checkpoints

**Before Task 01 (SLSA)**:
- [ ] Confirm Security team availability for key generation
- [ ] Confirm GitHub Secrets permissions configured
- [ ] Confirm module list in PoC is approved

**Before Task 02 (Coverage)**:
- [ ] Confirm Codecov account created
- [ ] Confirm 75% threshold acceptable to Engineering
- [ ] Confirm per-module thresholds in config/coverage_thresholds.yml

**Before Task 04 (Monitoring)**:
- [ ] Confirm Datadog account access
- [ ] Confirm alert thresholds with Ops team
- [ ] Confirm PagerDuty/Slack integration details

**Before ANY PR Merge**:
- [ ] Human Security review completed
- [ ] Human Ops review completed
- [ ] All validation commands pass
- [ ] No auto-merge enabled

## Support & Troubleshooting

### If SLSA workflow fails
1. Check `COSIGN_KEY` and `IN_TOTO_KEY` are configured in GitHub Secrets
2. Verify cosign is installed in CI (use `sigstore/cosign-installer@v3`)
3. Check module names in `config/slsa_modules.yml` match actual paths

### If Coverage upload fails
1. Verify `CODECOV_TOKEN` configured in GitHub Secrets
2. Check Codecov is enabled for repo at https://app.codecov.io
3. Ensure coverage.xml file is generated before upload step

### If Benchmarks show inconsistent results
1. Use `benchmark.pedantic()` with warmup rounds
2. Run on dedicated CI runners (not shared)
3. Increase rounds for statistical significance

### If Datadog metrics not appearing
1. Verify DogStatsD agent running (`systemctl status datadog-agent`)
2. Check metric names use `lukhas.*` namespace
3. Verify tags are included in metric calls

## Post-Completion Checklist

After all 5 tasks complete:

- [ ] All 5 PRs created and reviewed
- [ ] GitHub Secrets configured (4 secrets minimum)
- [ ] Security posture report shows 80%+ SLSA coverage (target)
- [ ] Coverage enforced at 75%+ for production lanes
- [ ] Nightly benchmarks running at 02:00 UTC
- [ ] Datadog dashboard imported with 12+ widgets
- [ ] Key rotation runbook reviewed by Security
- [ ] All artifacts archived and attached to PRs
- [ ] Claude Code can proceed with refactoring (monitoring in place)

---

**Ready to start?** Copy the "Gemini IDE Chat Prompt" above and paste into your Gemini IDE, Cloud, or API interface. Recommend **parallel cloud execution** for maximum efficiency! ⚡
