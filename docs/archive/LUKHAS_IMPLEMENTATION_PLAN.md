# LUKHAS PWM Implementation Plan

## Executive Summary
This document consolidates all key recommendations from the GPT5 architectural consultation for the LUKHAS PWM (Personal Workspace Manager) system. It provides a structured, actionable implementation roadmap with specific code examples and best practices.

## System Architecture Overview

### Core Concept: Colony + Endocrine + Personal Symbols
The system operates as a non-hierarchical "colony" of specialized modules that communicate via endocrine-like signals, creating adaptive behavior without tight coupling.

### Trinity Framework (⚛️🧠🛡️)
- **⚛️ Identity**: Authenticity, consciousness, symbolic self
- **🧠 Consciousness**: Memory, learning, dream states, neural processing  
- **🛡️ Guardian**: Ethics, drift detection, repair

## Phase 1: Foundation Components (Weeks 1-2)

### 1.1 Signal-to-Prompt Modulation System

#### Configuration (modulation_policy.yaml)
```yaml
signals:
  - name: alignment_risk
    weight: 1.0
    cooldown_ms: 0
  - name: stress
    weight: 0.9
    cooldown_ms: 800
  - name: ambiguity
    weight: 0.7
    cooldown_ms: 700
  - name: novelty
    weight: 0.6
    cooldown_ms: 500
  - name: trust
    weight: 0.4
    cooldown_ms: 500
  - name: urgency
    weight: 0.5
    cooldown_ms: 300

bounds:
  temperature:        [0.0, 1.0]
  top_p:              [0.1, 1.0]
  max_output_tokens:  [256, 2048]
  reasoning_effort:   [0.0, 1.0]
  retrieval_k:        [2, 10]
  planner_beam:       [1, 6]
  memory_write:       [0.1, 1.0]
  safety_mode:        ["strict","balanced","creative"]

maps:
  alignment_risk:
    temperature:      "1 - 0.85*x"
    top_p:            "max(0.2, 1 - 0.8*x)"
    reasoning_effort: "min(1.0, 0.4 + 0.6*x)"
    planner_beam:     "max(1, round(6 - 4*x))"
    safety_mode:      "strict if x>0.3 else balanced"
  stress:
    temperature:      "max(0.1, 0.7 - 0.6*x)"
    top_p:            "max(0.3, 0.9 - 0.5*x)"
    max_output_tokens:"round(1400 - 600*x)"
    retrieval_k:      "min(10, 4 + round(4*x))"
```

#### Dispatcher Module (lukhas_pwm/modulation/dispatcher.py)
```python
from dataclasses import dataclass
from typing import Dict, Any, List
import time, yaml

@dataclass
class Signal:
    name: str
    level: float    # 0..1
    ttl_ms: int
    source: str
    audit_id: str
    ts: float = time.time()

class Modulator:
    def __init__(self, policy_path: str = "modulation_policy.yaml"):
        with open(policy_path, "r") as f:
            self.policy = yaml.safe_load(f)
        self.last_emit_ts = {s["name"]: 0 for s in self.policy["signals"]}

    def combine(self, incoming: List[Signal]) -> Dict[str, Any]:
        # Implementation details from conversation
        pass
```

### 1.2 Tool Governance System

#### Tool Registry (lukhas_pwm/openai/tooling.py)
```python
def build_tools_from_allowlist(allowlist: List[str]) -> List[Dict[str, Any]]:
    """Return tool schemas restricted to the provided allowlist."""
    tools = []
    if "retrieval" in allowlist:
        tools.append({
          "name":"retrieve_knowledge",
          "description":"Fetch top-K relevant notes.",
          "parameters":{"type":"object","properties":{"k":{"type":"integer"}}}
        })
    if "browser" in allowlist and Flags.get("BROWSER_TOOL", True):
        tools.append({
          "name":"open_url",
          "description":"Open a URL in a sandboxed browser.",
          "parameters":{"type":"object","properties":{"url":{"type":"string"}}}
        })
    return tools
```

### 1.3 Audit System

#### Audit Store (lukhas_pwm/audit/store.py)
```python
import json, os, threading
from pathlib import Path
from typing import Optional, Dict, Any

_AUDIT_LOCK = threading.Lock()
_AUDIT_DIR = Path(os.getenv("LUKHAS_AUDIT_DIR", ".lukhas_audit"))
_AUDIT_FILE = _AUDIT_DIR / "audit.jsonl"

def audit_log_write(bundle: Dict[str, Any]) -> None:
    """Append audit bundle as JSON line."""
    if "audit_id" not in bundle:
        raise ValueError("audit bundle missing 'audit_id'")
    bundle = _redact(bundle)
    line = json.dumps(bundle, ensure_ascii=False)
    with _AUDIT_LOCK:
        with _AUDIT_FILE.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
```

## Phase 2: Enhancement Components (Weeks 3-4)

### 2.1 Feedback System

#### Bounded LUT Implementation
```python
def record_feedback(card: FeedbackCard) -> dict:
    """Process feedback with exponential decay and bounded adjustments."""
    recent = get_recent_cards(window_hours=24)
    weights = compute_exponential_weights(recent)
    
    # Bounded style adjustments only
    deltas = {
        "temperature_delta": clamp(-0.1, 0.1, weighted_avg),
        "top_p_delta": clamp(-0.1, 0.1, weighted_avg),
        "memory_write_boost": clamp(0, 0.2, positive_only),
    }
    
    # Never adjust safety_mode or safety caps
    return {"version": version, "style": deltas, "updated_ms": now}
```

### 2.2 Feature Flags

#### Flag System (lukhas_pwm/flags/ff.py)
```python
class Flags:
    """Env-backed feature flags with 5s cache."""
    _cache = {}
    _ts = 0.0
    
    @classmethod
    def get(cls, name: str, default: bool = False) -> bool:
        now = time.time()
        if now - cls._ts > 5:
            cls._refresh()
        return cls._cache.get(name, default)
```

## Phase 3: Production Readiness (Weeks 5-6)

### 3.1 CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install -r requirements.txt
      - run: pytest --cov=lukhas_pwm --cov-report=xml
      - run: python scripts/smoke_check.py --json out/smoke.json
      - name: Enforce thresholds
        run: |
          [ "$IMPORT_MS" -le 1500 ] || exit 1
          [ "$INCIDENTS" -eq 1 ] || exit 1
```

### 3.2 Performance Testing

#### k6 Script (perf/k6_smoke.js)
```javascript
export const options = {
  scenarios: {
    smoke: { vus: 10, duration: '45s' }
  },
  thresholds: {
    'http_req_duration{endpoint:health}': ['p(95)<120'],
    'http_req_failed': ['rate<0.01']
  }
};
```

### 3.3 Colony ↔ DNA Integration

#### Integration Adapter
```python
def persist_consensus_to_dna(dna: HelixMemory, c: ConsensusResult) -> DNAWriteReceipt:
    """Maps consensus decision into DNA write with bounded strength."""
    quorum_ratio = c.votes_for / max(1, c.votes_total)
    raw_strength = 0.4 + 0.5 * (0.5 * c.confidence + 0.5 * quorum_ratio)
    strength = max(0.1, min(1.0, raw_strength))
    
    if Flags.get("DNA_ENCRYPT_PERSONAL", False) and value.get("_personal"):
        value = {"_enc": True, "blob": "[ENCRYPTED]"}
    
    return dna.write(c.key, value, version=c.version, strength=strength)
```

## Safety Invariants (CRITICAL)

1. **Alignment Risk**: Can only tighten safety, never relax
2. **Feedback Cards**: Update style weights only, cannot change safety_mode boundaries
3. **Moderation**: Always run on user input, tool outputs, and final assistant output
4. **Tool Governance**: 100% enforcement of allowlist
5. **Auto-Tightening**: Immediate escalation to strict mode on violations

## Implementation Order

### Week 1-2: Core Foundation
- [ ] modulation_policy.yaml configuration
- [ ] Dispatcher module with signal processing
- [ ] Tool registry and allowlist system
- [ ] Basic audit logging

### Week 3-4: Enhancements
- [ ] Feedback card system with LUT
- [ ] Feature flags infrastructure
- [ ] API documentation (OpenAPI)
- [ ] Admin dashboard

### Week 5-6: Production
- [ ] CI/CD pipeline with thresholds
- [ ] k6 performance tests
- [ ] Colony ↔ DNA integration
- [ ] Migration scaffolding

## Testing Strategy

### Unit Tests
- Signal modulation with various inputs
- Tool allowlist enforcement
- Feedback LUT bounds
- Feature flag toggles

### Integration Tests
- End-to-end OpenAI flow with tools
- Colony consensus to DNA persistence
- Audit trail completeness

### Performance Tests
- p95 latency < 800ms
- Error rate < 1%
- Tool execution < 200ms

## Deployment Strategy

### Phase 1: Shadow Mode
- Enable dual-write (FLAG_DNA_DUAL_WRITE)
- Monitor drift with read-shadow
- Collect metrics without affecting production

### Phase 2: Gradual Rollout
- Feature flags for each capability
- Start with internal users
- Monitor safety metrics closely

### Phase 3: Full Production
- Cutover reads to DNA
- Decommission legacy systems
- Full audit trail and governance

## Success Metrics

### Technical
- p95 API latency < 800ms
- 99.9% uptime
- <1% error rate
- 100% audit coverage

### Safety
- Zero safety boundary violations
- 100% tool governance enforcement
- All incidents logged and reviewed
- Auto-tightening response < 50ms

### Business
- Reduced manual intervention by 80%
- Improved user satisfaction scores
- Complete compliance audit trail
- Seamless migration with zero data loss

## Next Steps

1. Review and approve this implementation plan
2. Set up development environment
3. Begin Phase 1 implementation
4. Establish weekly review cadence
5. Deploy to staging environment for testing

---

*This plan is derived from comprehensive architectural consultation and represents production-ready patterns for building the LUKHAS PWM system with OpenAI/GPT-5 integration.*