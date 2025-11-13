# GEMINI TASK PACK — Infrastructure, SLSA & Monitoring
**Agent**: Gemini (Infrastructure & CI Designer)
**Mission**: Build supply-chain security (SLSA), coverage pipelines, performance baselines, and monitoring dashboards
**Standards**: T4/0.01% reliability, SLSA Level 2+, human-in-loop review
**Collaboration**: Works with Claude Code (refactoring), Copilot (suggestions), Codex (batch automation)

---

## Executive Summary

### What Gemini Does
Gemini is the **Infrastructure & CI Designer** for LUKHAS AI. While Claude Code handles surgical code refactors and Copilot provides real-time suggestions, Gemini focuses on:

1. **Supply-Chain Security (SLSA)**: Attestation pipelines with `cosign` and `in-toto` to verify artifact provenance
2. **Coverage Pipelines**: Per-module coverage enforcement with Codecov integration
3. **Performance Baselines**: Nightly benchmarks for MATRIZ cognitive cycles and endocrine updates
4. **Monitoring Dashboards**: Datadog/NewRelic dashboards for WaveC snapshots, lane-guard failures, and endocrine metrics
5. **Key Management**: Secure key generation, rotation runbooks, and secret handling for CI

### What You've Learned About LUKHAS

**Lane-Based Architecture**:
- **candidate/** (2,877 files): Experimental research lane
- **core/** (253 components): Integration/testing lane
- **lukhas/** (692 components): Production lane
- **Import Rules**: `lukhas/` can import `core/`, `matriz/`; `candidate/` can import `core/`, `matriz/` only

**Critical Import Boundaries**:
- NO imports from `candidate/` → `lukhas/` (enforced by `make lane-guard`)
- NO imports from `labs` at top-level in production code
- Use ProviderRegistry pattern for runtime dependency injection

**Constellation Framework (8-Star System)**:
- ⚛️ Identity, ✦ Memory, 🔬 Vision, 🌱 Bio, 🌙 Dream, ⚖️ Ethics, 🛡️ Guardian, ⚛️ Quantum

**MATRIZ Cognitive Engine**:
- Performance targets: <250ms p95 latency, <100MB memory, 50+ ops/sec throughput
- Symbolic DNA with node-based processing
- Endocrine system for distributed state coordination

**Testing Standards**:
- **T4 Testing**: Unit → Integration → E2E → Smoke (4 test tiers)
- **Coverage**: 75%+ for production promotion, 30% minimum enforced
- **Smoke Tests**: 15 critical tests run on every commit

### Mission
Establish a **T4 infrastructure foundation** that provides:
1. **SLSA Level 2+ attestations** for 80% of critical modules
2. **Per-module coverage enforcement** with Codecov gate blocking PRs <75%
3. **Nightly performance baselines** tracking MATRIZ and endocrine regressions
4. **Real-time monitoring dashboards** with alert rules for lane-guard failures, WaveC rollbacks, and endocrine anomalies
5. **Key management runbooks** for secure rotation of cosign/in-toto keys

### Success Criteria
- ✅ SLSA PoC workflow runs for 10 modules, produces verified attestations
- ✅ `verify_attestation.py` successfully verifies signatures and SHA256
- ✅ Coverage pipeline enforces module-level thresholds, blocks PRs <75%
- ✅ Nightly benchmarks establish baselines for MATRIZ cycle time and endocrine update latency
- ✅ Datadog dashboard shows WaveC snapshots, lane-guard failures, endocrine metrics
- ✅ Security posture report shows 80%+ SLSA coverage

---

## Task Execution Pattern for Gemini

Each task follows this workflow:

### Standard Branch & PR Naming
- Branch: `task/gemini-<task-name>`
- PR Title: `chore(<scope>): <short description>`
- Example: `task/gemini-slsa-poc` → `chore(slsa): add attestation PoC for 10 modules`

### Standard Workflow
1. **Create branch**: `git checkout -b task/gemini-<task-name> origin/main`
2. **Implement files**: Add scripts, workflows, config, runbooks
3. **Test locally**: Run PoC commands, verify outputs
4. **Create PR**: Include artifacts, runbook, verification output
5. **Human review**: Security/Ops review before merge
6. **Never auto-merge**: All PRs require explicit human approval

### Standard Commit Message Format
```
chore(<scope>): <imperative subject ≤72 chars>

Problem:
- Current state and gaps

Solution:
- What this change implements

Impact:
- Security/coverage/monitoring improvements

🤖 Generated with Gemini
Co-Authored-By: Gemini <noreply@google.com>
```

---

## Task 01: SLSA Attestation PoC (10 Modules)

### Why
Currently LUKHAS has **0% SLSA attestation coverage**. This task establishes a proof-of-concept attestation pipeline for 10 critical modules to verify artifact provenance and integrity using `cosign` and `in-toto`.

### Gemini Prompt (Copy/Paste)

```
Context: LUKHAS AI platform needs supply-chain security with SLSA attestations
Task: Create SLSA attestation PoC for 10 critical modules

Requirements:
1. Create config/slsa_modules.yml listing 10 PoC modules:
   - core
   - matriz
   - lukhas
   - candidate/consciousness
   - core/identity
   - core/adapters
   - core/governance
   - core/observability
   - serve/api
   - lukhas_website

2. Create .github/workflows/slsa-attest-matrix.yml:
   - Matrix build for all modules in config/slsa_modules.yml
   - Use cosign to sign artifacts
   - Use in-toto to create provenance links
   - Upload attestation artifacts to workflow runs

3. Create scripts/automation/run_slsa_for_module.sh:
   - Takes --module <name> --outdir <path>
   - Builds module artifact (tar.gz)
   - Creates in-toto link with SHA256
   - Signs with cosign
   - Outputs <module>-attestation.json

4. Create scripts/verify_attestation.py:
   - Takes --att <attestation.json> --cosign-pub <pub-key>
   - Verifies cosign signature
   - Verifies SHA256 integrity
   - Reports in-toto link presence
   - Exits 0 on success, 1 on failure

5. Create scripts/automation/collect_attestations.py:
   - Scans --att-dir for all attestation files
   - Verifies each with cosign public key
   - Produces security_posture_report.json:
     {
       "total_modules": 10,
       "attested": 10,
       "verified": 10,
       "coverage_percent": 100.0,
       "failed": []
     }

6. Create docs/gonzo/SLSA_RUNBOOK.md:
   - Key generation instructions (cosign, in-toto)
   - GitHub Secrets setup (COSIGN_KEY, IN_TOTO_KEY)
   - Verification commands
   - Key rotation procedure (90-day cycle recommended)
   - Security best practices (never commit private keys)

Secrets Required (configure in GitHub repository settings):
- COSIGN_KEY: cosign private key (generate with: cosign generate-key-pair)
- IN_TOTO_KEY: RSA private key (generate with: openssl genpkey -algorithm RSA)
- COSIGN_PASSPHRASE: (optional) passphrase for cosign key

Standards:
- Use SLSA Level 2+ provenance format
- All attestations must be verifiable offline with public key
- Include SHA256 checksums for all artifacts
- Store public keys in docs/gonzo/ (committed to repo)
- Never commit private keys to repository
```

### Expected Files Created

```
config/slsa_modules.yml
.github/workflows/slsa-attest-matrix.yml
scripts/automation/run_slsa_for_module.sh
scripts/verify_attestation.py
scripts/automation/collect_attestations.py
docs/gonzo/SLSA_RUNBOOK.md
docs/gonzo/cosign_pub.pem  # Public key for verification
```

### Validation Commands

```bash
# 1. Generate test keys locally
cosign generate-key-pair
openssl genpkey -algorithm RSA -out in_toto_key.pem -pkeyopt rsa_keygen_bits:2048

# 2. Set environment variables
export COSIGN_KEY=$(pwd)/cosign.key
export IN_TOTO_KEY=$(pwd)/in_toto_key.pem

# 3. Run attestation for one module
bash scripts/automation/run_slsa_for_module.sh --module core --outdir ./slsa_out

# 4. Verify the attestation
python3 scripts/verify_attestation.py --att ./slsa_out/core-attestation.json --cosign-pub ./cosign.pub

# 5. Collect all attestations
python3 scripts/automation/collect_attestations.py --att-dir ./slsa_out --cosign-pub ./cosign.pub --out security_posture_report.json

# 6. Check the report
cat security_posture_report.json | jq '.coverage_percent'
# Expected: 100.0
```

### Acceptance Criteria

- [ ] PoC workflow runs successfully for all 10 modules in CI
- [ ] `verify_attestation.py` successfully verifies cosign signatures
- [ ] `collect_attestations.py` produces security_posture_report.json with 100% coverage
- [ ] SLSA_RUNBOOK.md reviewed by Security and Ops teams
- [ ] GitHub Secrets configured (COSIGN_KEY, IN_TOTO_KEY)
- [ ] Public keys committed to docs/gonzo/cosign_pub.pem
- [ ] Sample attestation artifacts attached to PR for review

### Commit Message Template

```
chore(slsa): add SLSA attestation PoC for 10 modules

Problem:
- LUKHAS has 0% SLSA attestation coverage
- No supply-chain verification for critical artifacts
- Missing key management runbook

Solution:
- Add SLSA attestation workflow for 10 PoC modules
- Implement cosign signing and in-toto provenance
- Create verify_attestation.py for offline verification
- Add collect_attestations.py for security posture reporting
- Provide SLSA_RUNBOOK.md with key generation/rotation

Impact:
- Establishes SLSA Level 2+ attestation baseline
- Enables verification of artifact provenance
- Provides security posture metrics (target: 80% coverage)

Files Created:
- config/slsa_modules.yml
- .github/workflows/slsa-attest-matrix.yml
- scripts/automation/run_slsa_for_module.sh
- scripts/verify_attestation.py
- scripts/automation/collect_attestations.py
- docs/gonzo/SLSA_RUNBOOK.md

🤖 Generated with Gemini
Co-Authored-By: Gemini <noreply@google.com>
```

---

## Task 02: Coverage Pipeline + Codecov Gate

### Why
LUKHAS currently has **30% minimum coverage** (fail_under in pyproject.toml) but needs **per-module enforcement** to ensure production code maintains 75%+ coverage before promotion from candidate → core → lukhas lanes.

### Gemini Prompt (Copy/Paste)

```
Context: LUKHAS AI needs per-module coverage enforcement with Codecov integration
Task: Create coverage pipeline that blocks PRs below 75% coverage threshold

Requirements:
1. Create .github/workflows/coverage.yml:
   - Run pytest with --cov flag for all modules
   - Generate coverage.xml report
   - Upload to Codecov with module-level annotations
   - Fail workflow if overall coverage <75%

2. Create scripts/ci/check_coverage.py:
   - Parse coverage.xml
   - Enforce per-module thresholds from config/coverage_thresholds.yml
   - Output detailed report with module-level percentages
   - Exit 1 if any module below threshold

3. Create config/coverage_thresholds.yml:
   - Define per-module targets:
     lukhas/: 75%
     core/: 75%
     matriz/: 80%
     candidate/: 30%  # Research code, lower bar
     tests/: 90%      # Test infrastructure must be well-tested

4. Update .codecov.yml:
   - Configure Codecov PR comments
   - Set project coverage target: 75%
   - Enable module-level breakdown in PR comments
   - Block PRs if coverage decreases

5. Add coverage badge to README.md:
   - [![codecov](https://codecov.io/gh/LukhasAI/Lukhas/branch/main/graph/badge.svg)](https://codecov.io/gh/LukhasAI/Lukhas)

6. Create docs/gonzo/COVERAGE_RUNBOOK.md:
   - How to configure Codecov integration
   - How to update coverage thresholds
   - How to run coverage locally
   - How to debug coverage failures

Codecov Configuration:
- Requires CODECOV_TOKEN in GitHub Secrets
- Configure at https://app.codecov.io/gh/LukhasAI/Lukhas

Standards:
- Production code (lukhas/, core/) must maintain 75%+ coverage
- Research code (candidate/) can have lower bar (30%)
- Test infrastructure must be well-tested (90%+)
- Coverage must not decrease on PRs
```

### Expected Files Created

```
.github/workflows/coverage.yml
scripts/ci/check_coverage.py
config/coverage_thresholds.yml
.codecov.yml
docs/gonzo/COVERAGE_RUNBOOK.md
README.md  # Updated with coverage badge
```

### Validation Commands

```bash
# 1. Run coverage locally
pytest --cov=. --cov-report=xml --cov-report=term

# 2. Check per-module coverage
python3 scripts/ci/check_coverage.py --coverage-xml coverage.xml --thresholds config/coverage_thresholds.yml

# 3. Verify Codecov configuration
# (After merging, check PR comments for coverage reports)

# 4. Test coverage gate
# Create a test PR with reduced coverage and verify it blocks merge
```

### Acceptance Criteria

- [ ] Coverage workflow runs on all PRs
- [ ] check_coverage.py enforces per-module thresholds
- [ ] Codecov integration shows module-level breakdown in PR comments
- [ ] Coverage badge appears in README.md
- [ ] COVERAGE_RUNBOOK.md reviewed by Engineering team
- [ ] Test PR demonstrates coverage gate blocking <75% coverage

### Commit Message Template

```
chore(coverage): add per-module coverage enforcement with Codecov gate

Problem:
- LUKHAS has 30% minimum coverage, too low for production code
- No per-module enforcement for lane-specific thresholds
- Missing Codecov integration for PR gating

Solution:
- Add coverage.yml workflow with pytest --cov
- Implement check_coverage.py for per-module thresholds
- Configure Codecov with 75% project target
- Add coverage badge to README
- Provide COVERAGE_RUNBOOK.md for operators

Impact:
- Production code (lukhas/, core/) must maintain 75%+ coverage
- Research code (candidate/) can remain at 30%
- PRs blocked if coverage decreases below threshold
- Visible coverage metrics on every PR

Files Created:
- .github/workflows/coverage.yml
- scripts/ci/check_coverage.py
- config/coverage_thresholds.yml
- .codecov.yml
- docs/gonzo/COVERAGE_RUNBOOK.md

🤖 Generated with Gemini
Co-Authored-By: Gemini <noreply@google.com>
```

---

## Task 03: Performance Baselines + Nightly Benchmarks

### Why
LUKHAS needs **performance regression detection** for MATRIZ cognitive cycles and endocrine updates. Currently there are no automated benchmarks tracking latency/throughput baselines.

### Gemini Prompt (Copy/Paste)

```
Context: LUKHAS AI needs nightly performance benchmarks for MATRIZ and endocrine systems
Task: Create benchmark suite with baseline tracking and regression detection

Requirements:
1. Create benchmarks/ directory structure:
   benchmarks/
   ├── test_matriz_performance.py
   ├── test_endocrine_performance.py
   ├── baselines/
   │   ├── matriz_baseline.json
   │   └── endocrine_baseline.json
   └── README.md

2. Create benchmarks/test_matriz_performance.py:
   - Use pytest-benchmark
   - Test MATRIZ cognitive cycle latency (target: <250ms p95)
   - Test MATRIZ throughput (target: 50+ ops/sec)
   - Test memory usage (target: <100MB)
   - Export results to baselines/matriz_baseline.json

3. Create benchmarks/test_endocrine_performance.py:
   - Test endocrine update latency
   - Test WaveC snapshot creation time
   - Test rollback performance
   - Export results to baselines/endocrine_baseline.json

4. Create .github/workflows/benchmarks-nightly.yml:
   - Run nightly at 02:00 UTC
   - Execute pytest benchmarks/ --benchmark-json=benchmark_results.json
   - Compare against baselines/
   - Upload artifacts (benchmark_results.json, comparison report)
   - Post GitHub Issue if regression detected (>10% slower)

5. Create scripts/ci/compare_benchmarks.py:
   - Takes --current <results.json> --baseline <baseline.json>
   - Calculates percentage change for each metric
   - Generates markdown comparison report
   - Exits 1 if any metric regressed >10%

6. Create docs/gonzo/BENCHMARKING_RUNBOOK.md:
   - How to run benchmarks locally
   - How to update baselines
   - How to interpret regression reports
   - Performance targets for each subsystem

Performance Targets:
- MATRIZ cognitive cycle: <250ms p95 latency
- MATRIZ throughput: 50+ ops/sec
- MATRIZ memory: <100MB
- Endocrine update: <100ms p95
- WaveC snapshot: <50ms

Standards:
- Use pytest-benchmark for consistent measurement
- Track min/max/mean/p95/p99 percentiles
- Regression threshold: 10% slower triggers alert
- Baselines updated quarterly or after major optimizations
```

### Expected Files Created

```
benchmarks/test_matriz_performance.py
benchmarks/test_endocrine_performance.py
benchmarks/baselines/matriz_baseline.json
benchmarks/baselines/endocrine_baseline.json
benchmarks/README.md
.github/workflows/benchmarks-nightly.yml
scripts/ci/compare_benchmarks.py
docs/gonzo/BENCHMARKING_RUNBOOK.md
```

### Validation Commands

```bash
# 1. Run benchmarks locally
pip install pytest-benchmark
pytest benchmarks/ --benchmark-json=benchmark_results.json

# 2. Compare against baseline
python3 scripts/ci/compare_benchmarks.py --current benchmark_results.json --baseline benchmarks/baselines/matriz_baseline.json

# 3. Verify nightly workflow syntax
yamllint .github/workflows/benchmarks-nightly.yml

# 4. Check performance targets
# MATRIZ cycle should be <250ms p95
# MATRIZ throughput should be >50 ops/sec
```

### Acceptance Criteria

- [ ] Benchmark suite runs successfully locally
- [ ] Nightly workflow triggers at 02:00 UTC
- [ ] compare_benchmarks.py detects regressions >10%
- [ ] Baseline files committed with initial measurements
- [ ] BENCHMARKING_RUNBOOK.md reviewed by Engineering team
- [ ] Sample benchmark report attached to PR

### Commit Message Template

```
chore(benchmarks): add nightly performance baselines for MATRIZ and endocrine

Problem:
- No automated performance regression detection
- Missing baselines for MATRIZ cognitive cycle latency
- No tracking of endocrine update performance

Solution:
- Add pytest-benchmark suite for MATRIZ and endocrine
- Create nightly workflow at 02:00 UTC
- Implement compare_benchmarks.py for regression detection
- Establish baselines for latency/throughput/memory
- Provide BENCHMARKING_RUNBOOK.md for operators

Impact:
- Automated detection of >10% performance regressions
- Visible baselines for MATRIZ (<250ms p95, 50+ ops/sec, <100MB)
- Nightly reports track endocrine update latency
- GitHub Issues auto-created on regression

Files Created:
- benchmarks/test_matriz_performance.py
- benchmarks/test_endocrine_performance.py
- benchmarks/baselines/*.json
- .github/workflows/benchmarks-nightly.yml
- scripts/ci/compare_benchmarks.py
- docs/gonzo/BENCHMARKING_RUNBOOK.md

🤖 Generated with Gemini
Co-Authored-By: Gemini <noreply@google.com>
```

---

## Task 04: Datadog Monitoring Dashboard

### Why
LUKHAS needs **real-time monitoring** for WaveC snapshots, lane-guard failures, and endocrine metrics. Currently there is no observability into production system health.

### Gemini Prompt (Copy/Paste)

```
Context: LUKHAS AI needs Datadog dashboard for WaveC, lane-guard, and endocrine monitoring
Task: Create Datadog dashboard with alert rules for critical system metrics

Requirements:
1. Create docs/gonzo/monitoring/datadog_wavec_endocrine.json:
   - Dashboard with 4 widget groups:
     A. WaveC Metrics:
        - lukhas.wavec.snapshot.count (timeseries)
        - lukhas.wavec.rollback.rate (gauge)
        - lukhas.wavec.snapshot.latency (histogram, p95/p99)
     B. Lane-Guard Metrics:
        - lukhas.lane_guard.failures (counter)
        - lukhas.lane_guard.violations (by module, top list)
     C. Endocrine Metrics:
        - lukhas.endocrine.update.latency (histogram)
        - lukhas.endocrine.state.size_bytes (gauge)
        - lukhas.endocrine.sync.conflicts (counter)
     D. System Health:
        - lukhas.api.request.latency (p95)
        - lukhas.api.error.rate (gauge)

2. Create docs/gonzo/monitoring/alert_rules.json:
   - Alert: WaveC rollback rate >5% (triggers PagerDuty)
   - Alert: Lane-guard failures >10 per hour (Slack notification)
   - Alert: Endocrine update latency >200ms p95 (Email notification)
   - Alert: API error rate >1% (PagerDuty)

3. Create scripts/monitoring/export_metrics.py:
   - Instrument LUKHAS code with statsd/DogStatsD
   - Export WaveC, lane-guard, endocrine metrics
   - Example usage:
     from scripts.monitoring.export_metrics import metrics
     metrics.increment('lukhas.wavec.snapshot.count')

4. Create docs/gonzo/DATADOG_RUNBOOK.md:
   - How to import dashboard JSON to Datadog
   - How to configure alert rules
   - How to add new metrics to monitoring
   - How to interpret dashboard widgets

Datadog Configuration:
- Requires DD_API_KEY and DD_APP_KEY in environment
- Configure at https://app.datadoghq.com/dashboard/lists

Standards:
- All metrics use lukhas.* namespace
- Use tags for module/lane/environment
- Alert thresholds based on T4 performance targets
- Runbook includes escalation procedures
```

### Expected Files Created

```
docs/gonzo/monitoring/datadog_wavec_endocrine.json
docs/gonzo/monitoring/alert_rules.json
scripts/monitoring/export_metrics.py
docs/gonzo/DATADOG_RUNBOOK.md
```

### Validation Commands

```bash
# 1. Validate dashboard JSON syntax
cat docs/gonzo/monitoring/datadog_wavec_endocrine.json | jq '.'

# 2. Test metrics export locally
python3 scripts/monitoring/export_metrics.py --dry-run

# 3. Import dashboard to Datadog (requires DD_API_KEY)
# Follow instructions in DATADOG_RUNBOOK.md

# 4. Verify metrics are appearing in Datadog
# Check https://app.datadoghq.com/metric/explorer for lukhas.* metrics
```

### Acceptance Criteria

- [ ] Dashboard JSON validated and importable to Datadog
- [ ] Alert rules configured with appropriate thresholds
- [ ] export_metrics.py instruments WaveC, lane-guard, endocrine
- [ ] DATADOG_RUNBOOK.md reviewed by Ops team
- [ ] Screenshot of imported dashboard attached to PR
- [ ] Test alerts triggered successfully (dry-run)

### Commit Message Template

```
chore(monitoring): add Datadog dashboard for WaveC, lane-guard, and endocrine

Problem:
- No real-time observability into LUKHAS system health
- Missing alerts for WaveC rollbacks and lane-guard failures
- No tracking of endocrine update latency in production

Solution:
- Add Datadog dashboard with 4 widget groups (WaveC, lane-guard, endocrine, system)
- Implement alert rules for critical metrics (rollback rate, failures, latency)
- Create export_metrics.py for statsd instrumentation
- Provide DATADOG_RUNBOOK.md for dashboard import and alert config

Impact:
- Real-time visibility into WaveC snapshot count and rollback rate
- Automated alerts for lane-guard failures >10/hour
- Endocrine latency tracking with p95/p99 percentiles
- PagerDuty integration for critical alerts

Files Created:
- docs/gonzo/monitoring/datadog_wavec_endocrine.json
- docs/gonzo/monitoring/alert_rules.json
- scripts/monitoring/export_metrics.py
- docs/gonzo/DATADOG_RUNBOOK.md

🤖 Generated with Gemini
Co-Authored-By: Gemini <noreply@google.com>
```

---

## Task 05: Key Management & Rotation Runbook

### Why
LUKHAS uses cosign and in-toto keys for SLSA attestations. These keys must be **rotated every 90 days** for security. Currently there is no documented rotation procedure.

### Gemini Prompt (Copy/Paste)

```
Context: LUKHAS AI uses cosign/in-toto keys for SLSA attestations
Task: Create comprehensive key management and rotation runbook

Requirements:
1. Create docs/gonzo/KEY_MANAGEMENT_RUNBOOK.md:
   - Section: Key Generation
     - How to generate cosign key pair (cosign generate-key-pair)
     - How to generate in-toto RSA key (openssl genpkey)
     - Security best practices (2048-bit minimum, passphrase protection)

   - Section: GitHub Secrets Configuration
     - Exact gh CLI commands to upload secrets:
       gh secret set COSIGN_KEY --repo LukhasAI/Lukhas --body "$(cat cosign.key)"
       gh secret set IN_TOTO_KEY --repo LukhasAI/Lukhas --body "$(cat in_toto_key.pem)"
     - How to verify secrets are configured

   - Section: Key Rotation Procedure (90-day cycle)
     - Step 1: Generate new key pair on secure host
     - Step 2: Update public key in docs/gonzo/cosign_pub.pem
     - Step 3: Create PR with new public key
     - Step 4: After PR merge, update GitHub Secrets with new private key
     - Step 5: Re-run SLSA attestation workflow to re-sign artifacts
     - Step 6: Revoke old keys and record rotation in audit log

   - Section: Emergency Key Revocation
     - How to immediately revoke compromised keys
     - How to notify users to re-verify artifacts
     - How to re-attest all critical artifacts with new keys

   - Section: Audit Log
     - Template for recording key rotations:
       Date | Key Type | Action | Operator | Notes
       2025-11-02 | cosign | rotated | ops@lukhas.ai | Routine 90-day rotation

2. Create scripts/security/rotate_keys.sh:
   - Interactive script that guides operator through rotation
   - Prompts for confirmation at each step
   - Validates new keys before updating secrets
   - Creates audit log entry

3. Create scripts/security/verify_key_age.py:
   - Checks age of current keys from audit log
   - Warns if keys >80 days old (approaching 90-day rotation)
   - Exits 1 if keys >90 days old (overdue for rotation)

4. Add to .github/workflows/key-age-check.yml:
   - Weekly cron job checking key age
   - Creates GitHub Issue if keys approaching rotation (>80 days)
   - Assigns to @security_team

Standards:
- All private keys must be passphrase-protected
- Keys rotated every 90 days maximum
- Public keys committed to repository for transparency
- Private keys NEVER committed to repository
- Rotation procedure requires two-person approval
```

### Expected Files Created

```
docs/gonzo/KEY_MANAGEMENT_RUNBOOK.md
scripts/security/rotate_keys.sh
scripts/security/verify_key_age.py
.github/workflows/key-age-check.yml
docs/gonzo/key_rotation_audit.log  # Initial audit log template
```

### Validation Commands

```bash
# 1. Validate runbook completeness
# (Manual review - ensure all sections present)

# 2. Test key rotation script (dry-run)
bash scripts/security/rotate_keys.sh --dry-run

# 3. Verify key age check
python3 scripts/security/verify_key_age.py --audit-log docs/gonzo/key_rotation_audit.log

# 4. Test weekly workflow syntax
yamllint .github/workflows/key-age-check.yml
```

### Acceptance Criteria

- [ ] KEY_MANAGEMENT_RUNBOOK.md reviewed by Security team
- [ ] rotate_keys.sh tested in dry-run mode
- [ ] verify_key_age.py correctly calculates key age from audit log
- [ ] Weekly workflow creates GitHub Issue when keys >80 days old
- [ ] Audit log template committed to repository
- [ ] Two-person approval process documented in runbook

### Commit Message Template

```
chore(security): add key management and 90-day rotation runbook

Problem:
- No documented procedure for cosign/in-toto key rotation
- Missing audit log for key lifecycle tracking
- No automated warnings for approaching rotation deadline

Solution:
- Add KEY_MANAGEMENT_RUNBOOK.md with generation/rotation/revocation procedures
- Create rotate_keys.sh interactive rotation script
- Implement verify_key_age.py to check key age from audit log
- Add weekly workflow to warn when keys >80 days old
- Provide audit log template for rotation tracking

Impact:
- Documented 90-day rotation cycle for SLSA keys
- Automated warnings prevent overdue rotations
- Audit trail for compliance and security reviews
- Emergency revocation procedure for compromised keys

Files Created:
- docs/gonzo/KEY_MANAGEMENT_RUNBOOK.md
- scripts/security/rotate_keys.sh
- scripts/security/verify_key_age.py
- .github/workflows/key-age-check.yml
- docs/gonzo/key_rotation_audit.log

🤖 Generated with Gemini
Co-Authored-By: Gemini <noreply@google.com>
```

---

## Common Issues & Solutions

### Issue: SLSA attestation workflow fails with "cosign: command not found"

**Solution**: Install cosign in GitHub Actions workflow:
```yaml
- name: Install cosign
  uses: sigstore/cosign-installer@v3
  with:
    cosign-release: 'v2.2.0'
```

### Issue: Codecov upload fails with "401 Unauthorized"

**Solution**: Verify CODECOV_TOKEN is configured in GitHub Secrets:
```bash
gh secret set CODECOV_TOKEN --repo LukhasAI/Lukhas --body "your-token-here"
```

### Issue: Benchmarks show inconsistent results across runs

**Solution**: Use pytest-benchmark warmup and rounds:
```python
def test_matriz_cycle(benchmark):
    benchmark.pedantic(run_matriz_cycle, warmup_rounds=5, rounds=100)
```

### Issue: Datadog metrics not appearing in dashboard

**Solution**: Verify DogStatsD agent is running and metrics are tagged correctly:
```python
from datadog import statsd
statsd.increment('lukhas.wavec.snapshot.count', tags=['env:production', 'module:core'])
```

### Issue: Key rotation script fails with "permission denied"

**Solution**: Ensure rotate_keys.sh has execute permissions and is run on secure host:
```bash
chmod +x scripts/security/rotate_keys.sh
# Run only on operator workstation, not CI
```

---

## Gemini-Specific Guidelines

### DO:
- ✅ Test all workflows locally before creating PR
- ✅ Include sample outputs (attestations, reports, dashboards) in PR
- ✅ Provide detailed runbooks for operators
- ✅ Use exact `gh` CLI commands for reproducibility
- ✅ Tag all PRs with `security`, `infrastructure`, `T4`, `audit`
- ✅ Request review from Security, Ops, and Engineering teams
- ✅ Include acceptance criteria checklist in PR description
- ✅ Attach artifacts (coverage reports, benchmark results, attestations)

### DON'T:
- ❌ Auto-merge any infrastructure changes
- ❌ Commit private keys to repository (use GitHub Secrets)
- ❌ Skip testing workflows locally before PR
- ❌ Create dashboards without alert rules
- ❌ Implement monitoring without runbooks
- ❌ Rotate keys without recording in audit log
- ❌ Set alert thresholds without Engineering team approval

---

## Integration with Other Agents

### With Claude Code
- Claude Code refactors code to remove `labs` imports
- Gemini ensures coverage remains >75% after refactors
- Gemini monitors lane-guard failures from Claude Code's changes

### With GitHub Copilot
- Copilot suggests workflow YAML snippets
- Gemini reviews and tests workflows before committing
- Copilot generates metric export code, Gemini integrates with Datadog

### With Codex
- Codex runs batch codemods
- Gemini verifies coverage doesn't drop after batch changes
- Gemini re-attests modules after Codex refactors

---

## Success Metrics

Track these metrics to measure infrastructure quality:

### SLSA Coverage
- **Current**: 0% (0 modules attested)
- **Target**: 80% (critical modules attested)
- **Measurement**: `security_posture_report.json` from `collect_attestations.py`

### Code Coverage
- **Current**: 30% overall (fail_under in pyproject.toml)
- **Target**: 75% for production lanes (lukhas/, core/)
- **Measurement**: Codecov dashboard, per-module breakdown

### Performance Baselines
- **MATRIZ Cycle**: <250ms p95 latency
- **MATRIZ Throughput**: 50+ ops/sec
- **MATRIZ Memory**: <100MB
- **Endocrine Update**: <100ms p95
- **Measurement**: Nightly benchmark reports, regression alerts

### Monitoring Coverage
- **WaveC Metrics**: Snapshot count, rollback rate, latency
- **Lane-Guard Metrics**: Failure count, violation breakdown
- **Endocrine Metrics**: Update latency, state size, conflicts
- **Measurement**: Datadog dashboard widget count, alert rule count

### Key Rotation Compliance
- **Current**: No rotation procedure
- **Target**: 100% compliance with 90-day rotation cycle
- **Measurement**: Audit log entries, key age check warnings

---

## Reference Materials

### SLSA Resources
- SLSA Framework: https://slsa.dev/
- cosign Documentation: https://docs.sigstore.dev/cosign/overview/
- in-toto Specification: https://in-toto.io/

### Coverage Resources
- pytest-cov: https://pytest-cov.readthedocs.io/
- Codecov: https://docs.codecov.com/docs

### Benchmarking Resources
- pytest-benchmark: https://pytest-benchmark.readthedocs.io/
- Performance Testing Best Practices: https://pythonspeed.com/articles/

### Monitoring Resources
- Datadog API: https://docs.datadoghq.com/api/
- DogStatsD: https://docs.datadoghq.com/developers/dogstatsd/

### Security Resources
- Key Management Best Practices: https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final
- GitHub Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets

---

## Final Handoff Checklist

Before marking infrastructure tasks complete, ensure:

- [ ] All 5 tasks have PRs created with artifacts attached
- [ ] Security team reviewed SLSA_RUNBOOK.md and KEY_MANAGEMENT_RUNBOOK.md
- [ ] Ops team reviewed COVERAGE_RUNBOOK.md, BENCHMARKING_RUNBOOK.md, DATADOG_RUNBOOK.md
- [ ] GitHub Secrets configured (COSIGN_KEY, IN_TOTO_KEY, CODECOV_TOKEN, DD_API_KEY)
- [ ] Public keys committed to docs/gonzo/cosign_pub.pem
- [ ] Initial baselines established (SLSA PoC, coverage, benchmarks)
- [ ] Datadog dashboard imported and alerts configured
- [ ] Audit log initialized with first key generation entry
- [ ] All workflows tested in CI and passing
- [ ] security_posture_report.json shows progress toward 80% SLSA coverage
- [ ] Claude Code can proceed with refactoring knowing infrastructure is monitored

---

**End of Gemini Task Pack**

Next: Hand off to Claude Code for surgical refactoring (see CLAUDE_CODE_PACK.md)
