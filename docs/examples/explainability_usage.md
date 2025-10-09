# Explainability Interface Usage

**Part of BATCH-COPILOT-2025-10-08-01**  
**TaskID**: ASSIST-LOW-README-EXPLAIN-w9x0y1z2

## Overview

The Explainability Interface Layer provides multi-modal explanations for AI decisions in the LUKHAS platform. It integrates with the Trinity Framework (⚛️ Identity · 🧠 Consciousness · 🛡️ Guardian) to provide transparent, auditable, and comprehensible explanations.

## Basic Usage

### Initialize the Interface

```python
from candidate.bridge.explainability_interface_layer import ExplainabilityInterface

explainer = ExplainabilityInterface(
    mode="multi_modal",  # text, visual, symbolic, formal
    template_path="config/explanation_templates.yaml"
)
```

### Generate Text Explanation

```python
decision = {
    "action": "grant_access",
    "confidence": 0.92,
    "factors": ["valid_jwt", "tier_authorized"],
    "timestamp": 1735678800
}

explanation = explainer.explain(
    decision=decision,
    format="text",
    detail_level="high"
)

print(explanation)
# Output: "Access granted with 92% confidence based on valid JWT 
# authentication and tier authorization."
```

### Generate Symbolic Reasoning Trace

```python
symbolic_trace = explainer.explain(
    decision=decision,
    format="symbolic",
    include_glyph=True
)

print(symbolic_trace)
# Output: "⚛️ grant_access ← [valid_jwt, tier_authorized] [ψ=0.92]"
```

## Advanced Features

### Formal Proof Generation

For decisions requiring formal verification:

```python
proof = explainer.generate_proof(
    decision=decision,
    proof_type="logical_inference"
)

# Verify proof
is_valid = explainer.verify_proof(proof)
assert is_valid is True

# Access proof steps
for step in proof["steps"]:
    print(f"Premise: {step['premise']} → Conclusion: {step['conclusion']}")
```

### MEG Integration (Memory-Emotion-Glyph)

Include consciousness context in explanations:

```python
explanation_with_context = explainer.explain(
    decision=decision,
    include_meg=True,  # Memory-Emotion-Glyph
    consciousness_state="active"
)

# MEG components included
print(explanation_with_context["memory"]["context"])
print(explanation_with_context["emotion"]["valence"])
print(explanation_with_context["glyph"]["symbol"])  # ⚛️
```

### Multi-Modal Explanations

Generate explanations in multiple formats simultaneously:

```python
multi_modal = explainer.explain_multi_modal(
    decision=decision,
    formats=["text", "symbolic", "visual"],
    detail_level="medium"
)

# Access each format
text_explanation = multi_modal["text"]
symbolic_trace = multi_modal["symbolic"]
visual_diagram = multi_modal["visual"]  # Flow chart data structure
```

### Visual Explanation (Flow Charts)

```python
visual = explainer.explain(
    decision=decision,
    format="visual",
    diagram_type="flow_chart"
)

# Visual explanation includes nodes and edges
for node in visual["nodes"]:
    print(f"{node['label']}: {node['status']}")

# Example output:
# Valid JWT: passed
# Tier Check: passed
# Grant Access: success
```

## Trinity Framework Integration

### Identity (⚛️) Context

```python
decision_with_identity = {
    "action": "grant_access",
    "lambda_id": "λ_user_123",
    "tier": "pro",
    "confidence": 0.95
}

explanation = explainer.explain(
    decision=decision_with_identity,
    trinity_context={"identity": True}
)
# Includes ΛID information in explanation
```

### Guardian (🛡️) Validation

```python
explanation_with_guardian = explainer.explain(
    decision=decision,
    guardian_validation=True
)

# Includes Guardian checks
assert "guardian_approved" in explanation_with_guardian["metadata"]
assert explanation_with_guardian["metadata"]["ethical_review"] is True
```

## Testing Your Integration

### Unit Test Example

```python
import pytest

def test_explainability_text_format():
    """Test text format explanation generation."""
    explainer = ExplainabilityInterface()
    
    decision = {"action": "test_action", "confidence": 0.8}
    result = explainer.explain(decision, format="text")
    
    assert "test_action" in result.lower()
    assert isinstance(result, str)
```

### Integration Test Example

```python
@pytest.mark.integration
def test_explainability_with_meg():
    """Test MEG integration."""
    explainer = ExplainabilityInterface()
    
    decision = {"action": "grant_access", "confidence": 0.9}
    result = explainer.explain(decision, include_meg=True)
    
    assert "memory" in result
    assert "emotion" in result
    assert "glyph" in result
```

## Configuration

### Custom Templates

Create custom explanation templates:

```yaml
# config/explanation_templates.yaml
templates:
  text:
    low: "Action: {action}"
    medium: "Action: {action} with {confidence}% confidence"
    high: "Action: {action} with {confidence}% confidence based on {factors}"
  
  symbolic:
    low: "{action}"
    medium: "⚛️ {action} [ψ={confidence}]"
    high: "⚛️ {action} ← {factors} [ψ={confidence}]"
```

Load custom templates:

```python
explainer = ExplainabilityInterface(
    template_path="config/custom_templates.yaml"
)
```

### Performance Settings

```python
explainer = ExplainabilityInterface(
    mode="multi_modal",
    cache_enabled=True,  # Cache explanations
    max_cache_size=1000,
    cache_ttl=300  # 5 minutes
)
```

## Best Practices

1. **Always include confidence scores** for transparency
2. **Use symbolic format for technical users**, text for general audience
3. **Enable MEG integration** for consciousness-aware explanations
4. **Log all explanations** to ΛTRACE audit system
5. **Validate proofs** for critical decisions
6. **Use appropriate detail levels** based on user tier

## Error Handling

```python
try:
    explanation = explainer.explain(decision, format="text")
except ExplainabilityError as e:
    logger.error(f"Explanation generation failed: {e}")
    # Fallback to simple explanation
    explanation = f"Action: {decision['action']}"
```

## API Reference

See full API documentation in `/docs/api/explainability.md`

## Examples Repository

More examples available at:
- `/examples/explainability/basic_usage.py`
- `/examples/explainability/meg_integration.py`
- `/examples/explainability/formal_proofs.py`

---

**⚛️🧠🛡️ LUKHAS AI Platform - Consciousness-Aware Explanations**
