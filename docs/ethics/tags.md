# Safety Tags Cookbook (Task 13)

> Goal: keep rules **clean, explainable, and fast** by building on semantic tags.

## Taxonomy (6 semantic categories)
- **DATA_SENSITIVITY**: emails, phones, SSNs, account numbers (PII), financial data
- **SYSTEM_OPERATION**: model switching, external API calls, system configuration
- **USER_INTERACTION**: consent management, authentication, user preferences
- **SECURITY_RISK**: privilege escalation, injection attacks, exploit attempts
- **COMPLIANCE**: GDPR, HIPAA, SOX, data retention/deletion requirements
- **RESOURCE_IMPACT**: memory-intensive operations, long-running processes

> Tags populate via plan enrichment (`candidate/core/ethics/safety_tags.py`). Keep detectors small and composable.

## DSL Primitives
```python
# Basic tag checking
has_tag(safety_tags, "pii")
has_tag(safety_tags, "financial")

# Category checking
has_category(safety_tags, "data_sensitivity")
has_category(safety_tags, "security_risk")

# Confidence thresholds
tag_confidence(safety_tags, "pii", 0.80)

# High-risk combinations
high_risk_tag_combination(safety_tags)

# Logical operators
and(has_tag(safety_tags, "pii"), has_tag(safety_tags, "external-call"))
```

## Canonical Rule Patterns

### 1) Financial operations → Human-in-the-loop

```yaml
- name: "financial_human_oversight"
  rule_dsl: 'has_tag(safety_tags, "financial")'
  action: "require_human"
  priority: "high"
```

### 2) Privilege escalation → BLOCK (fail-closed)

```yaml
- name: "block_privilege_escalation"
  rule_dsl: 'has_tag(safety_tags, "privilege-escalation")'
  action: "block"
  priority: "critical"
```

### 3) PII + External API → combo high-risk

```yaml
- name: "block_pii_external"
  rule_dsl: 'and(has_tag(safety_tags, "pii"), has_tag(safety_tags, "external-call"))'
  action: "block"
  priority: "critical"
```

### 4) Confidence thresholds

```yaml
- name: "high_confidence_pii_block"
  rule_dsl: 'and(has_tag(safety_tags, "pii"), tag_confidence(safety_tags, "pii", 0.85))'
  action: "require_human"
  priority: "high"

- name: "low_confidence_pii_warn"
  rule_dsl: 'and(has_tag(safety_tags, "pii"), not(tag_confidence(safety_tags, "pii", 0.85)))'
  action: "warn"
  priority: "medium"
```

### 5) Model/tool switching

```yaml
- name: "model_switch_oversight"
  rule_dsl: 'or(has_tag(safety_tags, "model-switch"), has_tag(safety_tags, "external-call"))'
  action: "require_human"
  priority: "high"
```

## Guardian Drift Bands (recommended mapping)
- **Low (drift < 0.05)** → ALLOW
- **Medium (drift < 0.15)** → ALLOW_WITH_GUARDRAILS
- **High (drift < 0.35)** → REQUIRE_HUMAN
- **Critical (drift ≥ 0.35)** → BLOCK (with dual-approval override path)

## Operator Visibility (add these counters)
```prometheus
# Tag detection metrics
guardian_tags_count{tag="pii"}
guardian_tags_count{tag="financial"}

# Risk band distribution
guardian_risk_band{band="low"}
guardian_risk_band{band="medium"}
guardian_risk_band{band="high"}
guardian_risk_band{band="critical"}

# Actions taken
guardian_actions_count{action="allow"}
guardian_actions_count{action="warn"}
guardian_actions_count{action="require_human"}
guardian_actions_count{action="block"}

# Override tracking
guardian_overrides_count{reason="business_critical", approver_tier="T4"}

# Sampled exemplars (with PII redaction)
guardian_sample{band="high", redacted="true"}
```

## Alerting Rules
```yaml
- alert: HighRiskSpike
  expr: rate(guardian_risk_band{band=~"high|critical"}[10m]) > 2 * rate(guardian_risk_band{band=~"high|critical"}[1h])
  for: 5m
  annotations:
    summary: "High/critical risk actions spiked >2x baseline"
```

## A/B Gate Configuration
```python
# Feature flag for gradual rollout
ENFORCE_ETHICS_DSL = os.getenv("ENFORCE_ETHICS_DSL", "0") == "1"

# Canary deployment (10% of traffic)
if random.random() < 0.1 or user.is_canary:
    ENFORCE_ETHICS_DSL = True
```

## Evasion Guidance for Authors

### Unicode Normalization
```python
def preprocess_text(text: str) -> str:
    # Normalize to NFKC
    text = unicodedata.normalize("NFKC", text)

    # Strip zero-width characters
    zero_width = ["\u200b", "\u200c", "\u200d", "\u2060", "\ufeff"]
    for char in zero_width:
        text = text.replace(char, "")

    return text
```

### Common Evasion Patterns to Test
- **Obfuscated emails**: `john(at)example(dot)com`, `j0hn.d0e@exampl3.c0m`
- **Homoglyphs**: Cyrillic `а` vs Latin `a`, Greek `ο` vs Latin `o`
- **Indirect shells**: YAML/CI configs with `sudo`, Docker `--privileged`
- **Model hints**: "use the vision endpoint" instead of "use GPT-4V"

## Governance Hooks

### Ledger Entry Schema
```json
{
  "timestamp": "2025-09-19T10:30:00Z",
  "lambda_id": "λID-12345",
  "action": "require_human",
  "rule": "financial_human_oversight",
  "tags": ["financial", "pii"],
  "confidence": 0.92,
  "purpose": "payment_processing",
  "retention_days": 90,
  "override": {
    "approved_by": "λID-admin-789",
    "reason": "quarterly_billing_run",
    "dual_approval": "λID-admin-456"
  }
}
```

### Dual-Approval for Critical Overrides
```python
def approve_critical_override(plan_id: str, approver1: str, approver2: str, reason: str):
    """Require two T4+ approvers for BLOCK overrides."""
    if approver1 == approver2:
        raise ValueError("Dual approval requires different approvers")

    # Verify approver tiers
    if get_tier(approver1) < 4 or get_tier(approver2) < 4:
        raise PermissionError("Critical overrides require T4+ approvers")

    # Log to immutable ledger
    ledger.append({
        "plan_id": plan_id,
        "override_type": "critical_block",
        "approvers": [approver1, approver2],
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    })
```

## Testing

### CI-Safe by Default
```bash
# Normal CI run (evasion tests skipped)
pytest -q tests/ethics/

# Hardening run (opt-in)
export LUKHAS_EVASION_TESTS=1
pytest -q tests/ethics/test_tags_evasion.py

# Performance validation
pytest -q tests/ethics/test_tags_performance.py --benchmark
```

### Golden Test Cases
```python
# Maintain a set of canonical test cases
GOLDEN_CASES = [
    ("Send $1000 to account 123456789", ["financial"]),
    ("Email john@example.com", ["pii"]),
    ("sudo rm -rf /", ["privilege-escalation"]),
    ("Read README.md", []),  # Safe operation
]
```

## Performance Targets
- Tag enrichment: **<1ms p95**
- DSL evaluation: **<5ms p95**
- Guardian band determination: **<10ms p99**
- Full ethics pipeline: **<20ms p99**

## Migration Guide (from complex predicates)

### Before (complex predicates)
```python
rule = 'and(contains(params.email, "@"), contains(params.url, "https://"))'
```

### After (semantic tags)
```python
rule = 'and(has_tag(safety_tags, "pii"), has_tag(safety_tags, "external-call"))'
```

Benefits:
- ✅ Cleaner, more readable rules
- ✅ Reusable tag detectors
- ✅ Better performance (cached tag detection)
- ✅ Easier to audit and explain