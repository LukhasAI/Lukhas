> **Note**: This is a vendor-neutral version of claude.me for compatibility with any AI tool or development environment.


# Enforcement Module - LUKHAS Policy & Standards Enforcement

**Module**: enforcement
**Lane**: L2 Integration
**Team**: Core
**Purpose**: Policy enforcement, standards validation, and automated quality control for LUKHAS systems

---

## Overview

The enforcement module provides automated policy enforcement, standards validation, and quality control across the LUKHAS AI platform. This module ensures compliance with brand guidelines, tone standards, technical requirements, and governance policies.

**Key Features**:
- Tone system enforcement (3-layer validation)
- Author reference guard (no personal names in code/docs)
- Standards validation automation
- Policy compliance checking
- Automated quality gates
- Violation detection and reporting

---

## Architecture

### Module Structure

```
enforcement/
├── README.md                    # Module overview
├── module.manifest.json         # Module metadata
├── tone/
│   └── author_reference_guard.py  # Guards against personal name references
├── docs/                        # Documentation
├── tests/
│   ├── conftest.py
│   ├── test_enforcement_unit.py
│   └── test_enforcement_integration.py
└── config/                      # Configuration
```

---

## Core Components

### 1. Author Reference Guard

**Purpose**: Prevents personal name references in code, comments, and documentation.

**File**: `enforcement/tone/author_reference_guard.py`

**Why This Matters**: LUKHAS maintains a professional, vendor-neutral approach. Personal names in code create attribution issues, maintenance challenges, and unprofessional appearance.

```python
from enforcement.tone import AuthorReferenceGuard

# Create guard
guard = AuthorReferenceGuard(
    scan_paths=[".", "docs/", "lukhas/"],
    exclude_patterns=["*.git*", "node_modules/", "*.pyc"],
)

# Scan for violations
violations = guard.scan()

# violations = [
#     {
#         "file": "consciousness/core.py",
#         "line": 42,
#         "violation": "# Written by John Doe",
#         "type": "author_reference",
#         "severity": "warning",
#     },
# ]

# Auto-fix violations
guard.fix_violations(
    strategy="remove",  # or "replace_with_team", "comment_out"
)
```

**Detected Patterns**:
- `# Written by {name}`
- `# Author: {name}`
- `@author {name}` (docstring tags)
- `Created by {name}`
- Personal email addresses in code

**Exceptions**:
- LICENSE files
- CONTRIBUTORS.md
- Git commit metadata (not scanned)
- External third-party code

---

### 2. Tone System Enforcement

**Purpose**: Validates compliance with LUKHAS 3-Layer Tone System.

```python
from enforcement import ToneEnforcer, ToneViolation

# Create tone enforcer
enforcer = ToneEnforcer(
    check_poetic_limit=True,      # ≤40 words
    check_blocklist=True,          # Banned terms
    check_reading_level=True,      # Grade 6-8 for plain
    check_layer_balance=True,      # Proper layer distribution
)

# Validate content
violations = enforcer.validate_content(
    content=documentation_text,
    content_type="public_docs",  # or "internal_docs", "api_reference"
)

# violations = [
#     ToneViolation(
#         type="poetic_overlimit",
#         location="line 42",
#         message="Poetic expression exceeds 40-word limit (52 words)",
#         severity="error",
#     ),
#     ToneViolation(
#         type="blocklist_term",
#         location="line 15",
#         message="Banned term 'revolutionary' detected",
#         severity="error",
#         suggestion="Remove superlative or use evidence-backed claim",
#     ),
# ]
```

---

### 3. Standards Validation

**Purpose**: Validates compliance with LUKHAS technical and documentation standards.

```python
from enforcement import StandardsValidator

# Create validator
validator = StandardsValidator(
    standards=[
        "t4_compliance",           # T4/0.01% quality standards
        "constellation_framework", # Constellation integration required
        "matriz_integration",      # MATRIZ pipeline compliance
        "opentelemetry_spans",     # Required spans present
    ],
)

# Validate module
compliance = validator.validate_module(
    module_path="consciousness/",
    module_manifest="consciousness/module.manifest.json",
)

# compliance = {
#     "t4_compliance": {
#         "score": 0.95,
#         "violations": [],
#     },
#     "constellation_framework": {
#         "stars_integrated": 8,
#         "missing_stars": [],
#     },
#     "matriz_integration": {
#         "stages_implemented": 7,
#         "missing_stages": [],
#     },
#     "opentelemetry_spans": {
#         "required_spans_present": True,
#         "missing_spans": [],
#     },
# }
```

---

### 4. Policy Compliance Checker

**Purpose**: Validates compliance with governance policies and ethical guidelines.

```python
from enforcement import PolicyChecker

# Create policy checker
checker = PolicyChecker(
    policies=[
        "no_personal_data",         # No PII in code/logs
        "consent_required",         # User consent for data
        "guardian_integration",     # Safety checks present
        "audit_trail_complete",     # Complete audit logging
    ],
)

# Check compliance
compliance = checker.check_component(
    component="identity/",
    check_code=True,
    check_docs=True,
    check_tests=True,
)

# compliance = {
#     "no_personal_data": True,
#     "consent_required": True,
#     "guardian_integration": True,
#     "audit_trail_complete": False,  # Violation
#     "violations": [
#         {
#             "policy": "audit_trail_complete",
#             "file": "identity/auth.py",
#             "line": 156,
#             "message": "Authentication event not logged to audit trail",
#         },
#     ],
# }
```

---

### 5. Quality Gates

**Purpose**: Automated quality gates for CI/CD pipeline integration.

```python
from enforcement import QualityGates

# Create quality gates
gates = QualityGates(
    gates=[
        {
            "name": "tone_compliance",
            "enforcer": ToneEnforcer(),
            "fail_on_error": True,
        },
        {
            "name": "author_references",
            "enforcer": AuthorReferenceGuard(),
            "fail_on_error": False,  # Warning only
        },
        {
            "name": "standards_compliance",
            "enforcer": StandardsValidator(),
            "fail_on_error": True,
        },
        {
            "name": "policy_compliance",
            "enforcer": PolicyChecker(),
            "fail_on_error": True,
        },
    ],
)

# Run all gates
results = gates.run_all(
    target_path=".",
    fail_fast=False,  # Run all gates even if one fails
)

# results = {
#     "passed": False,
#     "gates": {
#         "tone_compliance": {"passed": True, "violations": []},
#         "author_references": {"passed": False, "violations": [...]},  # Warning
#         "standards_compliance": {"passed": True, "violations": []},
#         "policy_compliance": {"passed": False, "violations": [...]},  # Error
#     },
#     "summary": {
#         "total_gates": 4,
#         "passed": 2,
#         "failed": 2,
#         "warnings": 1,
#     },
# }

# Exit with appropriate code for CI/CD
sys.exit(0 if results["passed"] else 1)
```

---

## Integration with CI/CD

### GitHub Actions Integration

```yaml
# .github/workflows/enforcement.yml
name: Enforcement Checks

on: [push, pull_request]

jobs:
  enforcement:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Enforcement Checks
        run: |
          python -m enforcement.quality_gates \
            --config enforcement/config/quality_gates.yaml \
            --fail-on-error

      - name: Report Violations
        if: failure()
        run: |
          python -m enforcement.report \
            --format github \
            --output enforcement_report.md
```

---

### Pre-Commit Hook Integration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: author-reference-guard
        name: Author Reference Guard
        entry: python -m enforcement.tone.author_reference_guard
        language: python
        pass_filenames: false

      - id: tone-compliance
        name: Tone System Compliance
        entry: python -m enforcement.tone_enforcer
        language: python
        files: \.(md|rst)$
```

---

## Configuration

```yaml
enforcement:
  author_reference_guard:
    enabled: true
    scan_paths:
      - "."
      - "docs/"
      - "lukhas/"
    exclude_patterns:
      - "*.git*"
      - "node_modules/"
      - "*.pyc"
      - "LICENSE"
      - "CONTRIBUTORS.md"
    auto_fix: false
    fix_strategy: "remove"  # or "replace_with_team", "comment_out"

  tone_enforcer:
    enabled: true
    check_poetic_limit: true
    poetic_word_limit: 40
    check_blocklist: true
    check_allowlist: true
    check_reading_level: true
    target_reading_level: "6-8"
    check_layer_balance: true
    layer_balance:
      poetic_min: 0.25
      poetic_max: 0.40
      academic_min: 0.20
      academic_max: 0.40
      user_friendly_min: 0.40
      user_friendly_max: 0.60

  standards_validator:
    enabled: true
    standards:
      - t4_compliance
      - constellation_framework
      - matriz_integration
      - opentelemetry_spans
    min_t4_score: 0.65
    required_constellation_stars: 8
    required_matriz_stages: 7

  policy_checker:
    enabled: true
    policies:
      - no_personal_data
      - consent_required
      - guardian_integration
      - audit_trail_complete

  quality_gates:
    enabled: true
    fail_fast: false
    report_format: "json"  # or "markdown", "html"
    export_results: true
```

---

## Observability

**Required Spans**:
- `lukhas.enforcement.operation`

**Metrics**:
- Violation count by type
- Gate pass/fail rates
- Enforcement execution time
- Auto-fix success rate

---

## Testing

### Unit Tests (`test_enforcement_unit.py`)
- Author reference detection accuracy
- Tone validation correctness
- Standards checking logic
- Policy compliance rules

### Integration Tests (`test_enforcement_integration.py`)
- CI/CD integration
- Pre-commit hook execution
- Multi-gate orchestration
- Auto-fix end-to-end workflows

---

## Use Cases

### 1. Pre-Commit Validation
```bash
# Run enforcement checks before commit
python -m enforcement.quality_gates --pre-commit
```

### 2. CI/CD Quality Gates
```bash
# Run in CI/CD pipeline
python -m enforcement.quality_gates --ci --fail-on-error
```

### 3. Documentation Review
```bash
# Validate documentation compliance
python -m enforcement.tone_enforcer docs/ --report
```

### 4. Codebase Cleanup
```bash
# Remove author references across codebase
python -m enforcement.tone.author_reference_guard --auto-fix
```

---

## Development Guidelines

### Adding New Enforcement Rules
1. Define rule in appropriate enforcer (tone, standards, policy)
2. Implement detection logic
3. Add to quality gates configuration
4. Write unit tests for rule
5. Document rule and rationale
6. Test in CI/CD pipeline

### Best Practices
- Keep enforcement rules maintainable and clear
- Provide helpful violation messages
- Offer auto-fix where possible
- Document exceptions explicitly
- Test enforcement on real codebase samples

---

## Related Modules

- **tone/**: 3-Layer Tone System (enforced by this module)
- **branding/**: Brand guidelines and vocabularies (enforced)
- **governance/**: Governance policies (enforced)
- **guardian/**: Safety and ethics (integrated with policy checks)

---

## Quick Reference

| Component | Purpose | Configuration |
|-----------|---------|---------------|
| `AuthorReferenceGuard` | Remove personal names | `author_reference_guard.enabled` |
| `ToneEnforcer` | Validate 3-layer tone system | `tone_enforcer.check_poetic_limit` |
| `StandardsValidator` | Validate technical standards | `standards_validator.min_t4_score` |
| `PolicyChecker` | Validate governance policies | `policy_checker.policies` |
| `QualityGates` | Orchestrate all enforcement | `quality_gates.fail_fast` |

---

**Module Status**: L2 Integration
**Schema Version**: 1.0.0
**Complexity**: Low (rule-based validation)
**MATRIZ Compatibility**: Standard
**Last Updated**: 2025-10-02
**Philosophy**: Automated enforcement ensures quality scales—what's measured and enforced becomes the standard.
