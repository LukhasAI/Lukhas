# [D4] ZAP CI/CD Integration Enhancements

**Labels**: `enhancement`, `dast`, `security`, `ci/cd`
**Priority**: Medium
**Milestone**: Q1 2026
**Estimated Effort**: 3-5 days

---

## Problem Statement

The current ZAP DAST workflows (baseline + full/API) provide solid security scanning, but lack advanced features for:
1. **Historical Trend Analysis**: No tracking of vulnerability trends over time
2. **Baseline Comparison**: Cannot compare current scan to previous baseline
3. **Custom Scan Policies**: Limited control over scan rules per environment
4. **Authenticated Scanning**: No authentication context for protected routes
5. **Performance**: Full scans take 35+ minutes, could be optimized

## Proposed Solution

Enhance ZAP workflows with:

### 1. Historical Tracking
- Store scan results in S3/GCS with versioning
- Compare current scan to previous week's baseline
- Fail CI if new vulnerabilities introduced (regression detection)

**Implementation**:
```yaml
# .github/workflows/dast-zap-baseline.yml
- name: Upload scan results
  uses: actions/upload-artifact@v4
  with:
    name: zap-baseline-${{ github.sha }}
    path: zap-baseline-report.html
    retention-days: 90

- name: Compare to baseline
  run: |
    # Download previous scan results from S3
    aws s3 cp s3://lukhas-dast-results/baseline-main.json baseline-prev.json

    # Compare vulnerability counts
    python3 scripts/compare_zap_results.py baseline-prev.json zap-baseline-report.json

    # Fail if NEW vulnerabilities introduced
    if [ $? -ne 0 ]; then
      echo "❌ New vulnerabilities introduced!"
      exit 1
    fi
```

### 2. Authenticated Scanning
- Generate API token for ZAP to authenticate
- Scan protected routes (requires auth)
- Detect authorization bypass vulnerabilities

**Implementation**:
```yaml
- name: Generate auth token
  run: |
    # Get test user token
    export TEST_TOKEN=$(curl -X POST http://localhost:8000/auth/token \
      -d "username=zap-scanner&password=$ZAP_SCANNER_PASSWORD" | jq -r '.token')

    # Configure ZAP authentication
    zap-cli session new zap-session
    zap-cli context new authenticated-context
    zap-cli context set-auth authenticated-context bearer-token $TEST_TOKEN
```

### 3. Custom Scan Policies
- Different policies for staging vs production
- Allowlist known false positives per environment
- Adjust aggressiveness (passive vs active scanning)

**Implementation**:
```bash
# dast/.zap/policies/staging.policy
{
  "scanner.level": "MEDIUM",
  "scanner.strength": "HIGH",
  "passive-scan-rules": ["all"],
  "active-scan-rules": ["sql-injection", "xss", "xxe"],
  "exclude-urls": [
    "http://localhost:8000/docs",  # Swagger UI (intentional)
    "http://localhost:8000/metrics"  # Prometheus (internal only)
  ]
}
```

### 4. Performance Optimization
- Parallel scanning of multiple endpoints
- Smart crawling (skip static assets)
- Incremental scanning (only changed routes)

**Before**: 35 minutes full scan
**After**: 15 minutes (with parallelization and smart crawling)

## Acceptance Criteria

- [ ] Historical scan results stored in S3/GCS with 90-day retention
- [ ] CI fails if new HIGH/CRITICAL vulnerabilities introduced
- [ ] Authenticated scanning enabled (test with protected `/admin` route)
- [ ] Custom scan policies for `main` vs `staging` branches
- [ ] Full scan time reduced to <20 minutes
- [ ] Documentation updated: `docs/dast/ZAP_ADVANCED.md`
- [ ] Slack notification on new vulnerabilities detected

## Implementation Plan

**Phase 1**: Historical Tracking (2 days)
1. Create S3 bucket: `lukhas-dast-results`
2. Add artifact upload step to workflows
3. Implement `scripts/compare_zap_results.py` comparison script
4. Test with intentional vulnerability regression

**Phase 2**: Authenticated Scanning (1 day)
1. Create `zap-scanner` test user in database
2. Configure ZAP authentication context
3. Update workflow to pass auth token
4. Verify protected routes scanned

**Phase 3**: Custom Policies (1 day)
1. Create `dast/.zap/policies/` directory
2. Define `staging.policy` and `production.policy`
3. Update workflows to load policy based on branch
4. Test with different rule sets

**Phase 4**: Performance Optimization (1 day)
1. Enable ZAP AJAX spider (parallel crawling)
2. Add URL exclusion patterns (skip docs, metrics)
3. Implement incremental scanning (git diff-based)
4. Benchmark: measure before/after scan times

## Testing Strategy

```bash
# Test authenticated scanning
pytest tests/dast/test_zap_authenticated.py

# Test policy loading
pytest tests/dast/test_zap_policies.py

# Test historical comparison
pytest tests/dast/test_zap_comparison.py
```

## Monitoring & Alerting

**Metrics**:
- `dast_scan_duration_seconds{scanner="zap",type="baseline|full"}`
- `dast_vulnerabilities_total{severity="high|medium|low"}`
- `dast_scan_failures_total`

**Alerts**:
```yaml
- alert: NewHighSeverityVulnerability
  expr: increase(dast_vulnerabilities_total{severity="high"}[1h]) > 0
  annotations:
    summary: "New HIGH severity vulnerability detected in DAST scan"
    runbook: "https://wiki.lukhas.ai/security/dast-runbook"
```

## Related Issues

- #XXX: ABAS integration with ZAP results (cross-validate findings)
- #XXX: NIAS drift detection for ZAP attack patterns
- #XXX: Security dashboard consolidation (ZAP + Snyk + Trivy)

## References

- [ZAP Authentication Docs](https://www.zaproxy.org/docs/desktop/start/features/authmethods/)
- [ZAP Scan Policies](https://www.zaproxy.org/docs/desktop/ui/dialogs/scanpolicy/)
- [GitHub Actions Artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)
- Gonzo Spec: `docs/gonzo/DAST + NIAS + ABAS + Security Headers .yml` (D4 section)

---

**Created**: 2025-11-13
**Author**: Security Enhancement Team
**Reviewers**: @security-team, @devops-team
