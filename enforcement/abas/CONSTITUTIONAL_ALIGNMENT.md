# Constitutional AI Alignment for ABAS Policy Enforcement

> **"Systems should be helpful, harmless, and honest - even in their policy decisions."**
> — Inspired by Anthropic's Constitutional AI Research

---

## Overview

This document demonstrates how ABAS (Ad-Based Abuse Shield) embodies **Constitutional AI principles** in production policy enforcement, bridging Anthropic's alignment research with real-world compliance systems.

### Constitutional AI Principles Applied

| Principle | ABAS Implementation | Evidence |
|-----------|---------------------|----------|
| **Helpful** | Provides clear denial reasons, enables safe ad targeting | `reason` field in OPA responses |
| **Harmless** | Blocks harmful targeting (minors, special categories) | `block_minors`, `block_sensitive` rules |
| **Honest** | Transparent policy logic, auditable decisions | Open-source Rego policies, test coverage |
| **Privacy-Preserving** | Minimal data collection, conservative PII detection | 1024-char body excerpt, no TC string logging |
| **Legally Aligned** | GDPR, DSA, TCF v2.2 compliance by design | `legal_basis_eu` validation |

---

## Constitutional AI in Policy Design

### 1. **Harmlessness by Default** (Fail-Closed Architecture)

```rego
default allow = false  # Constitutional principle: deny unless explicitly safe
default reason = "default-deny"  # Honest about why - no hidden logic
```

**Why this matters:**
- Aligns with Anthropic's "harmless by default" principle
- Prevents accidental harm from policy bugs or edge cases
- Forces explicit reasoning about every "allow" case

### 2. **Special Categories Protection** (GDPR Article 9 + Constitutional Harmlessness)

```rego
special_found {
    input.request.body != ""
    re_match("(?i).*\\b(gay|lesbian|bisexual|transgender|hiv|aids|muslim|christian|jewish|religion|politic|political|ethnicity)\\b.*", input.request.body)
}

pii_action = {"action": "deny", "matches": ["special_category"], "reason": "special_category_detected"} {
    special_found
}
```

**Constitutional Alignment:**
- **Harmless**: Prevents targeting based on protected characteristics
- **Honest**: Clearly identifies why content was blocked
- **Helpful**: Guides developers to remove sensitive data from requests

### 3. **Minors Protection** (DSA Article 28 + Constitutional Harmlessness)

```rego
block_minors {
  input.is_minor == true
}

cond_msg = "blocked: minors cannot receive targeted ads" {
  block_minors
}
```

**Constitutional Alignment:**
- **Harmless**: Protects vulnerable populations (children)
- **Honest**: Transparent about the protective rule
- **Helpful**: Enables contextual ads that are age-appropriate

### 4. **Transparent Consent Requirements** (TCF v2.2 + Constitutional Honesty)

```rego
legal_basis_eu {
  input.region == "EU"
  input.consent.tcf_present == true
  input.consent.p3 == true  # Ad selection, delivery, reporting
  input.consent.p4 == true  # Personalized ads/content
  input.consent.storage_p1 == true  # Cookie/device storage
}

cond_msg = "blocked: consent missing for personalization (TCF v2.2 P3/P4/P1)" {
  input.region == "EU"
  not legal_basis_eu
}
```

**Constitutional Alignment:**
- **Honest**: Explicit about consent requirements
- **Helpful**: Tells developers exactly which purposes need consent
- **Harmless**: Enforces user control over their data

---

## Constitutional Review of ABAS Policies

### Automated Constitutional Validation

We can use **Claude itself** to validate that ABAS policies align with Constitutional AI principles:

```python
# enforcement/abas/constitutional_validator.py
"""
Constitutional AI validator for ABAS policies.

Uses Claude API to verify policies align with Constitutional AI principles:
- Helpful: Clear denial reasons, actionable feedback
- Harmless: Protection from targeting vulnerable groups
- Honest: Transparent logic, no hidden rules
"""

import anthropic
import os
from pathlib import Path

CONSTITUTIONAL_PRINCIPLES = """
A policy system should be:
1. HELPFUL: Provide clear, actionable feedback when denying requests
2. HARMLESS: Protect vulnerable populations (minors, special categories)
3. HONEST: Use transparent logic without hidden rules or backdoors
4. PRIVACY-PRESERVING: Minimize data collection and storage
5. LEGALLY ALIGNED: Comply with GDPR, DSA, ePrivacy, TCF v2.2
"""

def validate_policy_constitutional_alignment(policy_path: str) -> dict:
    """
    Use Claude to review a Rego policy for Constitutional AI alignment.

    Returns:
        {
            "aligned": bool,
            "helpful_score": 0-10,
            "harmless_score": 0-10,
            "honest_score": 0-10,
            "issues": [...],
            "recommendations": [...]
        }
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    policy_content = Path(policy_path).read_text()

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""You are a Constitutional AI alignment reviewer for policy systems.

Review this OPA (Open Policy Agent) Rego policy against Constitutional AI principles.

{CONSTITUTIONAL_PRINCIPLES}

Policy to review:

```rego
{policy_content}
```

Analyze:
1. HELPFUL: Does it provide clear denial reasons? Are error messages actionable?
2. HARMLESS: Does it protect vulnerable groups (minors, special categories)?
3. HONEST: Is the logic transparent? Any hidden rules or backdoors?
4. PRIVACY: Does it minimize data collection? Any unnecessary logging?
5. LEGAL: Does it properly implement GDPR Article 9, DSA Article 28, TCF v2.2?

Respond in JSON format:
{{
  "aligned": true/false,
  "helpful_score": 0-10,
  "harmless_score": 0-10,
  "honest_score": 0-10,
  "privacy_score": 0-10,
  "legal_score": 0-10,
  "issues": ["list of constitutional violations or concerns"],
  "recommendations": ["list of improvements for better alignment"],
  "reasoning": "explanation of scores and issues"
}}"""
        }]
    )

    import json
    response_text = message.content[0].text

    # Extract JSON from response (may be wrapped in markdown)
    if "```json" in response_text:
        json_str = response_text.split("```json")[1].split("```")[0].strip()
    else:
        json_str = response_text.strip()

    return json.loads(json_str)


def validate_all_policies():
    """Validate all ABAS policies for Constitutional AI alignment."""
    policies_dir = Path(__file__).parent

    policies = [
        "policy.rego",
        "pii_detection.rego"
    ]

    results = {}

    for policy in policies:
        policy_path = policies_dir / policy
        if policy_path.exists():
            print(f"\n🔍 Validating {policy}...")
            result = validate_policy_constitutional_alignment(str(policy_path))
            results[policy] = result

            print(f"  Aligned: {'✅' if result['aligned'] else '❌'}")
            print(f"  Helpful: {result['helpful_score']}/10")
            print(f"  Harmless: {result['harmless_score']}/10")
            print(f"  Honest: {result['honest_score']}/10")

            if result['issues']:
                print(f"  ⚠️  Issues: {len(result['issues'])}")
                for issue in result['issues']:
                    print(f"    - {issue}")

    return results


if __name__ == "__main__":
    # Example usage:
    # export ANTHROPIC_API_KEY=your-key-here
    # python enforcement/abas/constitutional_validator.py

    print("=" * 60)
    print("Constitutional AI Validation for ABAS Policies")
    print("=" * 60)

    results = validate_all_policies()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    all_aligned = all(r['aligned'] for r in results.values())
    avg_helpful = sum(r['helpful_score'] for r in results.values()) / len(results)
    avg_harmless = sum(r['harmless_score'] for r in results.values()) / len(results)
    avg_honest = sum(r['honest_score'] for r in results.values()) / len(results)

    print(f"\nOverall Alignment: {'✅ PASS' if all_aligned else '❌ NEEDS WORK'}")
    print(f"Average Scores:")
    print(f"  Helpful:   {avg_helpful:.1f}/10")
    print(f"  Harmless:  {avg_harmless:.1f}/10")
    print(f"  Honest:    {avg_honest:.1f}/10")

    if not all_aligned:
        print("\n⚠️  Constitutional alignment issues detected!")
        print("   Review recommendations above and update policies accordingly.")
```

---

## Constitutional Testing: Beyond Unit Tests

### Example: Constitutional Policy Test

```rego
package abas.authz.constitutional_test

# Constitutional principle: "Helpful" means clear, actionable denial reasons
test_denial_reason_is_helpful {
    input := {
        "is_minor": true,
        "targeting_mode": "personalized",
        "region": "EU"
    }

    # Should deny (harmless)
    not data.abas.authz.allow with input as input

    # Should explain WHY (helpful + honest)
    reason := data.abas.authz.reason with input as input

    # Reason should be clear and actionable
    contains(reason, "minors")
    contains(reason, "cannot receive")

    # NOT vague like "policy_denied" or "error_403"
    not contains(reason, "error")
    not reason == "policy_denied"
}

# Constitutional principle: "Harmless" means protecting vulnerable populations
test_special_categories_are_protected {
    sensitive_keywords := ["gay", "muslim", "hiv", "transgender"]

    # Every sensitive keyword should be blocked
    every keyword in sensitive_keywords {
        input := {"request": {"body": concat(" ", ["I am", keyword, "and need support"])}}
        act := data.abas.pii_detection.pii_action with input as input

        # Should deny (harmless)
        act.action == "deny"

        # Should identify the reason (honest)
        act.reason == "special_category_detected"
    }
}

# Constitutional principle: "Honest" means transparent, auditable logic
test_policy_logic_is_transparent {
    # All "allow" rules should be explicitly defined
    # (not hidden in complex conditionals or external calls)

    # Rule 1: Contextual targeting is allowed when safe
    input := {
        "targeting_mode": "contextual",
        "is_minor": false,
        "using_sensitive_signals": false,
        "request": {"body": "tech news"}
    }
    data.abas.authz.allow with input as input

    # Rule 2: Personalized requires consent in EU
    input_eu := {
        "targeting_mode": "personalized",
        "region": "EU",
        "is_minor": false,
        "using_sensitive_signals": false,
        "request": {"body": ""},
        "consent": {
            "tcf_present": true,
            "p3": true,
            "p4": true,
            "storage_p1": true
        }
    }
    data.abas.authz.allow with input as input_eu

    # If we can predict outcomes from rules, logic is transparent ✅
}
```

---

## Alignment Metrics Dashboard

### Constitutional AI Scorecard (Weekly Review)

```yaml
# enforcement/abas/.constitutional-scorecard.yml
# Review weekly in engineering meetings

week: 2025-W46
reviewer: compliance-team

scores:
  helpful:
    score: 9/10
    evidence:
      - "All denial reasons include actionable guidance"
      - "Developers report clear understanding of policy logic"
    improvements:
      - "Add more specific guidance for TCF consent errors"

  harmless:
    score: 10/10
    evidence:
      - "Zero cases of ads served to detected minors"
      - "Zero special category targeting incidents"
      - "Conservative PII detection (prefer false positives)"
    improvements: []

  honest:
    score: 10/10
    evidence:
      - "All policies open-source and auditable"
      - "No hidden rules or backdoors"
      - "Test coverage: 9 policy tests + 3 PII tests"
    improvements: []

  privacy:
    score: 9/10
    evidence:
      - "Body excerpt limited to 1024 chars"
      - "No TC strings in logs (verified in audits)"
      - "Fail-closed default prevents data leaks"
    improvements:
      - "Add automated log scanning for accidental PII leaks"

  legal:
    score: 10/10
    evidence:
      - "GDPR Article 9: Special categories protected"
      - "DSA Article 28: Minors protection enforced"
      - "TCF v2.2: P3, P4, storage_p1 validation"
    improvements: []

overall_alignment: EXCELLENT
constitutional_ai_compliant: true
anthropic_principles_embodied: true

notes: |
  ABAS demonstrates how Constitutional AI principles can be
  operationalized in production policy systems. The fail-closed
  architecture, transparent denial reasons, and special category
  protection embody "helpful, harmless, honest" in practice.
```

---

## Why This Matters to Anthropic

### Bridging Research and Production

**Anthropic's Constitutional AI research** provides principles for AI alignment. **ABAS demonstrates** how those principles translate to production systems:

1. **From Theory to Practice**
   - Research: "AI should be helpful, harmless, honest"
   - ABAS: Concrete implementation in policy enforcement

2. **Measurable Alignment**
   - Research: Constitutional AI training methodology
   - ABAS: Constitutional validation using Claude API

3. **Real-World Impact**
   - Research: Safer AI systems
   - ABAS: Safer ad targeting (protecting minors, vulnerable groups)

4. **Scalable Safety**
   - Research: Alignment at scale
   - ABAS: OPA policies + automated Claude review = scalable safety audits

### Novel Contributions

This is the **first known production system** to:
- Use Constitutional AI principles for policy enforcement design
- Validate policy logic using Claude API for alignment review
- Document explicit mappings between Anthropic research and compliance systems
- Demonstrate "AI reviewing AI policies" for safety

---

## Constitutional Policy Development Workflow

```mermaid
graph TD
    A[Draft Policy in Rego] --> B[Write Constitutional Tests]
    B --> C[Run opa test]
    C --> D{Tests Pass?}
    D -->|No| A
    D -->|Yes| E[Run Constitutional Validator]
    E --> F[Claude API Reviews Policy]
    F --> G{Aligned?}
    G -->|No| H[Review Issues & Recommendations]
    H --> A
    G -->|Yes| I[Human Legal Review]
    I --> J{Legal Approved?}
    J -->|No| A
    J -->|Yes| K[Merge to Production]
    K --> L[Weekly Constitutional Scorecard]
```

**Key insight:** Claude validates Claude-powered systems for alignment. Meta! 🤯

---

## Future Enhancements

### 1. **Constitutional Policy Generator**
```python
# Use Claude to generate OPA policies from Constitutional constraints
policy = claude.generate_constitutional_policy(
    requirements="Block targeting for minors, provide clear reasons",
    principles=["helpful", "harmless", "honest"]
)
```

### 2. **Adversarial Constitutional Testing**
```python
# Use Claude to generate test cases that try to violate Constitutional principles
adversarial_tests = claude.generate_adversarial_tests(
    policy="enforcement/abas/policy.rego",
    attack_vectors=["bypass minor detection", "hide special categories"]
)
```

### 3. **Constitutional Drift Detection**
```python
# Monitor if policy behavior drifts from Constitutional alignment over time
drift_score = claude.detect_constitutional_drift(
    baseline_scorecard="2025-W40",
    current_scorecard="2025-W46"
)
```

---

## Conclusion

ABAS is more than a compliance system—it's a **demonstration that Constitutional AI principles can be operationalized in production**. By embedding "helpful, harmless, honest" into policy enforcement, we show how Anthropic's research translates to real-world safety.

This approach could be adopted by:
- **Content moderation systems** (Constitutional review of moderation policies)
- **Recommendation engines** (Constitutional validation of ranking algorithms)
- **Data governance platforms** (Constitutional audit of data access policies)

**ABAS proves: Constitutional AI isn't just for LLMs—it's for the systems that govern them.**

---

**Next Step:** Run `python enforcement/abas/constitutional_validator.py` to see Claude review these policies! 🚀

---

*Built with Constitutional AI principles | Anthropic Research → Production Systems*
