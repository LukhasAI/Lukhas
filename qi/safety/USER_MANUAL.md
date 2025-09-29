# LUKHΛS Safety & Compliance User Manual

## Overview
The LUKHΛS QI Safety module provides production-ready policy enforcement, consent management, and risk orchestration for AI systems. This manual covers the newly integrated components for enterprise-grade safety and compliance.

## 1. Policy Mutation Fuzzer

### Purpose
Deterministic testing of safety policies against adversarial inputs with corpus-driven mutations.

### Usage
```bash
# Run fuzzing against a specific task
python -m qi.safety.policy_mutate \
  --policy-root qi/safety/policy_packs \
  --jurisdiction global \
  --task generate_summary \
  --n 40 \
  --seed 1337 \
  --require-block pii jailbreak leakage
```

### Key Features
- **Deterministic**: Same seed produces same results
- **Corpus-driven**: Attack patterns defined in `policy_corpus.yaml`
- **Attack types**: PII injection, jailbreak, medical risks, budget blowup, prompt leakage
- **CI/CD ready**: Strict exit codes (0=pass, 1=fail)
- **Rich output**: JSON reports for dashboards

### Configuration
Edit `qi/safety/policy_corpus.yaml` to:
- Add new task seeds
- Define custom attack patterns
- Configure placeholders for dynamic content

## 2. Risk Orchestrator Overlays

### Purpose
Hierarchical policy management with jurisdiction and context-specific overrides.

### Usage
```bash
# Query policies for EU jurisdiction with medical context
python qi/risk/orchestrator_overlays.py \
  qi/risk/overlays \
  --jurisdiction eu \
  --context medical_high_risk
```

### Integration
```python
from qi.risk.orchestrator_overlays import RiskOverlayManager

overlay_mgr = RiskOverlayManager("/path/to/overlays")
policies = overlay_mgr.get_policies(
    jurisdiction="eu",
    context="medical_high_risk"
)

# Hot reload for live updates
overlay_mgr.hot_reload()
```

### Hierarchy
1. Global policies (base)
2. Jurisdiction overrides (e.g., EU GDPR, US CCPA)
3. Context overrides (e.g., medical, financial)

### Configuration
Edit `qi/risk/overlays/overlays.yaml`:
```yaml
jurisdictions:
  eu:
    teq_checks:
      gdpr_consent_required: true
    budget_limits:
      max_tokens: 150000
```

## 3. Consent Ledger

### Purpose
Cryptographically signed consent management with revocation support and audit trails.

### CLI Usage
```bash
# Grant consent
python -m qi.memory.consent_ledger grant \
  --user alice \
  --purpose personalization \
  --fields style_weights avg_len \
  --days 180

# Check consent
python -m qi.memory.consent_ledger check \
  --user alice \
  --purpose personalization \
  --need-fields style_weights \
  --within-days 180

# Revoke consent
python -m qi.memory.consent_ledger revoke \
  --user alice \
  --purpose personalization \
  --reason "user request"

# List user consents
python -m qi.memory.consent_ledger list --user alice
```

### Programmatic Usage
```python
from qi.memory.consent_ledger import record, revoke, is_allowed

# Grant consent
event = record(
    user="alice",
    purpose="analytics",
    fields=["usage_stats", "performance_metrics"],
    duration_days=365,
    meta={"source": "onboarding"}
)

# Check consent
allowed = is_allowed(
    user="alice",
    purpose="analytics",
    require_fields=["usage_stats"],
    within_days=30
)

# Revoke consent
revoke(user="alice", purpose="analytics", reason="opt-out")
```

### TEQ Integration
Add to policy mappings:
```yaml
tasks:
  personalize_reply:
    - kind: require_fresh_consent
      purpose: personalization
      user_key: user_id
      require_fields: [style_weights, avg_len]
      within_days: 180
```

### Fan-out Configuration
Set environment variables for real-time notifications:
```bash
# Webhook notification
export CONSENT_WEBHOOK_URL=https://audit.yourapp/consent

# Kafka streaming
export CONSENT_KAFKA_BROKERS=localhost:9092
export CONSENT_KAFKA_TOPIC=lukhas.consent.events
```

### Features
- **Ed25519 signatures**: Cryptographic proof of consent
- **Merkle chains**: Tamper-evident audit trail
- **Fast lookups**: O(1) index for quick checks
- **Field-level control**: Require specific data fields
- **Freshness checks**: Enforce time-based validity
- **Revocation cascade**: Instant fan-out to webhooks/Kafka

## 4. TEQ Gate Enhancements

### Fresh Consent Checks
The TEQ gate now supports enhanced consent validation:

```yaml
# In policy mappings
- kind: require_fresh_consent
  purpose: personalization
  user_key: user_id          # Key in user_profile
  require_fields:             # Required consent fields
    - style_weights
    - avg_len
  within_days: 180           # Max age of consent
```

### Context Requirements
Ensure your TEQ context includes:
```python
context = {
    "user_profile": {
        "user_id": "alice",
        "age": 25
    },
    "text": "User query here",
    "tokens_planned": 1000
}
```

## 5. CI/CD Integration

### Running Safety CI
```bash
python -m qi.safety.ci_runner \
  --policy-root qi/safety/policy_packs \
  --jurisdiction global \
  --mutations 40 \
  --out-json results.json
```

### CI Pipeline Steps
1. Policy coverage report
2. Policy linter checks
3. TEQ integration tests
4. Mutation fuzzing (per task)
5. JSON report generation

### Exit Codes
- 0: All checks passed
- 1: One or more checks failed
- 2: Consent check failed (specific to consent ledger)

## 6. Best Practices

### Policy Management
- Start with global defaults
- Add jurisdiction overrides for compliance
- Use contexts for domain-specific rules
- Hot-reload in production for zero-downtime updates

### Consent Handling
- Always specify clear purposes
- Request minimum necessary fields
- Set appropriate duration limits
- Implement revocation workflows
- Monitor fan-out events

### Security
- Enable attestation for high-risk operations
- Verify signatures in production
- Use deterministic fuzzing in CI
- Rotate signing keys periodically
- Audit consent events regularly

### Performance
- Consent checks are O(1) via index
- Policy overlays are cached in memory
- Fan-out is best-effort async
- TEQ checks run in parallel where possible

## 7. Troubleshooting

### Common Issues

**Consent not found**
- Check user ID spelling
- Verify purpose matches exactly
- Ensure consent hasn't expired
- Check if revoked

**Policy not applying**
- Verify jurisdiction spelling
- Check overlay file syntax
- Confirm hot-reload succeeded
- Review merge order (global → jurisdiction → context)

**Fuzzer false positives**
- Review corpus attack patterns
- Check require-block settings
- Verify policy mappings
- Examine TEQ check implementations

**Attestation failures**
- Install pynacl: `pip install pynacl`
- Check provenance module imports
- Verify signing keys exist
- Review chain integrity

## 8. Environment Variables

```bash
# Consent Ledger
export LUKHAS_STATE=~/.lukhas/state
export CONSENT_WEBHOOK_URL=https://audit.yourapp/consent
export CONSENT_KAFKA_BROKERS=localhost:9092
export CONSENT_KAFKA_TOPIC=lukhas.consent.events

# Risk Overlays (via code)
overlay_dir = "/path/to/overlays"
```

## 9. Dependencies

Required:
- Python 3.10+
- pydantic (for overlay schemas)
- PyYAML (for configuration)

Optional:
- pynacl (for cryptographic signing)
- requests (for webhook fan-out)
- kafka-python (for Kafka streaming)

## 10. Support

For issues or questions:
- Check logs in `~/.lukhas/state/consent/`
- Review test results in `qi/safety/test_results/`
- Run diagnostics: `python -m qi.safety.ci_runner`
- File issues at: github.com/lukhas/qi-safety
