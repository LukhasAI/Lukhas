---
title: lukhas_context
slug: guardian.lukhas_context
owner: T4
lane: L2
star: "🛡️ Watch Star"
stability: production
last_reviewed: 2025-10-24
constellation_stars: "🛡️ Watch · ⚛️ Anchor · ✦ Trail"
related_modules: "matriz, governance, identity, ethics"
manifests: "module.manifest.json"
links: "../matriz/node_contract.py, ../governance/lukhas_context.md"
contracts: "[GuardianValidation, GTΨ, MatrizNode]"
domain: security, governance, ethics
stars: "[Watch]"
status: active
tier: L2
updated: 2025-10-24
version: 3.0.0
schema_version: 3.0.0
---
# Guardian System - 🛡️ Watch Star
## Constitutional AI Validation & MATRIZ Integration

*Watch Star of Constellation Framework - Guardian validation for all MATRIZ cognitive operations*

---

## Guardian System Overview

**Guardian Module Location**: [guardian/](.)

The Guardian system is the **Constitutional AI validation and ethics enforcement layer** for the entire LUKHAS ecosystem. Every MATRIZ cognitive operation must pass Guardian validation, ensuring alignment with Constitutional AI principles and ethical constraints.

### **Watch Star Integration** 🛡️

- **Purpose**: Constitutional AI validation, ethics enforcement, and privileged operation approval
- **Architecture**: GTΨ (Guardian Tier Psi) step-up protocol with multi-tier validation
- **Integration**: MATRIZ Risk stage validation, runtime policy enforcement, Guardian token authentication
- **Contract**: Validates all MatrizNode operations per [node_contract.py](../matriz/node_contract.py:1)

### **System Scope**

- **Lane**: L2 (Integration) - Production-ready
- **Entrypoints**: 6 core Guardian functions
- **Schema**: 3.0.0
- **MATRIZ Integration**: Required for all cognitive operations
- **Constellation Role**: Watch Star 🛡️ - Security and ethics oversight

---

## Core Guardian Functions

### **1. emit_guardian_decision**

**Purpose**: Emit Guardian validation decision for MATRIZ operations

**Function Signature:**
```python
def emit_guardian_decision(
    operation: str,
    decision: str,  # "approved" | "rejected" | "escalated"
    reason: str,
    glyph_kind: str,
    msg_id: str,
    lane: str,
    metadata: Dict[str, Any]
) -> GuardianDecision
```

**MATRIZ Integration:**
```python
from guardian import emit_guardian_decision
from matriz.node_contract import MatrizMessage, MatrizResult

def handle(msg: MatrizMessage) -> MatrizResult:
    # Request Guardian validation
    decision = emit_guardian_decision(
        operation="cognitive_processing",
        decision="approved",
        reason="Operation within constitutional bounds",
        glyph_kind=msg.glyph.kind,
        msg_id=str(msg.msg_id),
        lane=msg.lane,
        metadata={"confidence": 0.95, "risk_level": "low"}
    )

    # Add to guardian_log in MatrizResult
    guardian_log = [
        f"Guardian validated {operation}",
        f"Decision: {decision.decision}",
        f"Reason: {decision.reason}"
    ]

    return MatrizResult(
        ok=decision.decision == "approved",
        reasons=[decision.reason],
        payload={"validated": True},
        trace={"guardian_decision_id": decision.id},
        guardian_log=guardian_log
    )
```

**Decision Types:**
- **approved**: Operation passes Constitutional AI validation
- **rejected**: Operation violates ethical constraints
- **escalated**: Requires GTΨ step-up or human oversight

### **2. validate_dual_approval**

**Purpose**: Enforce dual-approval requirement for privileged MATRIZ operations

**Function Signature:**
```python
def validate_dual_approval(
    operation: str,
    primary_approver: str,
    secondary_approver: str,
    operation_metadata: Dict[str, Any]
) -> bool
```

**MATRIZ GTΨ Integration:**
```python
from guardian import validate_dual_approval
from matriz.node_contract import MatrizMessage, GLYPH

# Privileged operations require dual approval
privileged_glyphs = ["INTENT", "DECISION"]

def handle(msg: MatrizMessage) -> MatrizResult:
    if msg.glyph.kind in privileged_glyphs:
        # Require GTΨ step-up with dual approval
        approved = validate_dual_approval(
            operation=f"{msg.glyph.kind}_processing",
            primary_approver="guardian_system",
            secondary_approver="human_supervisor",
            operation_metadata={
                "msg_id": str(msg.msg_id),
                "topic": msg.topic,
                "lane": msg.lane
            }
        )

        if not approved:
            return MatrizResult(
                ok=False,
                reasons=["Dual approval required but not granted"],
                payload={},
                trace={"gtpsi_required": True},
                guardian_log=["GTΨ step-up required", "Dual approval not granted"]
            )
```

**Use Cases:**
- INTENT GLYPH processing (ΛiD authentication)
- DECISION GLYPH with high-risk operations
- Production lane (prod) privileged operations
- Cross-system boundary operations

### **3. emit_guardian_action_with_exemplar**

**Purpose**: Emit Guardian action with exemplar pattern for learning

**Function Signature:**
```python
def emit_guardian_action_with_exemplar(
    action: str,
    exemplar: Dict[str, Any],
    outcome: str,
    metadata: Dict[str, Any]
) -> GuardianAction
```

**MATRIZ Learning Integration:**
```python
from guardian import emit_guardian_action_with_exemplar

# After successful MATRIZ operation, emit exemplar for learning
def handle(msg: MatrizMessage) -> MatrizResult:
    result = process_matriz_message(msg)

    if result.ok:
        # Emit positive exemplar for Guardian learning
        emit_guardian_action_with_exemplar(
            action="cognitive_processing_approved",
            exemplar={
                "glyph_kind": msg.glyph.kind,
                "topic": msg.topic,
                "lane": msg.lane,
                "operation_type": "reasoning",
                "risk_indicators": [],
                "success_pattern": "standard_cognitive_flow"
            },
            outcome="success",
            metadata={"processing_time_ms": 42, "confidence": 0.98}
        )

    return result
```

**Exemplar Types:**
- **Positive exemplars**: Successful operations for pattern learning
- **Negative exemplars**: Rejected operations for constraint learning
- **Edge cases**: Boundary conditions for robustness

### **4. emit_confidence_metrics**

**Purpose**: Emit confidence metrics for Guardian decision quality

**Function Signature:**
```python
def emit_confidence_metrics(
    decision_id: str,
    confidence_score: float,  # 0.0 to 1.0
    uncertainty_factors: List[str],
    metadata: Dict[str, Any]
) -> ConfidenceMetrics
```

**MATRIZ Trace Integration:**
```python
from guardian import emit_confidence_metrics, emit_guardian_decision

def handle(msg: MatrizMessage) -> MatrizResult:
    # Guardian makes decision
    decision = emit_guardian_decision(...)

    # Emit confidence metrics for trace
    confidence = emit_confidence_metrics(
        decision_id=decision.id,
        confidence_score=0.92,
        uncertainty_factors=[
            "novel_glyph_combination",
            "edge_case_topic"
        ],
        metadata={
            "training_data_coverage": 0.85,
            "similar_cases": 47
        }
    )

    return MatrizResult(
        ok=True,
        reasons=["Approved with high confidence"],
        payload={"result": "success"},
        trace={
            "guardian_confidence": confidence.confidence_score,
            "uncertainty_factors": confidence.uncertainty_factors
        },
        guardian_log=[f"Confidence: {confidence.confidence_score:.2f}"]
    )
```

### **5. emit_exemption**

**Purpose**: Emit exemption for exceptional Guardian override cases

**Function Signature:**
```python
def emit_exemption(
    operation: str,
    exemption_type: str,
    justification: str,
    approver: str,
    duration_seconds: Optional[int] = None
) -> GuardianExemption
```

**Emergency Override:**
```python
from guardian import emit_exemption

# Emergency exemption for critical operations
def emergency_override(msg: MatrizMessage) -> MatrizResult:
    exemption = emit_exemption(
        operation="emergency_cognitive_processing",
        exemption_type="time_critical",
        justification="Life-safety critical decision under time constraint",
        approver="senior_guardian_admin",
        duration_seconds=300  # 5-minute exemption
    )

    # Process with exemption logged
    result = process_without_full_validation(msg)
    result.guardian_log.append(f"Exemption granted: {exemption.id}")
    result.trace["exemption"] = exemption.to_dict()

    return result
```

**Exemption Types:**
- **time_critical**: Emergency time-sensitive operations
- **research**: Experimental lane research exemptions
- **maintenance**: System maintenance operations
- **audit_approved**: Pre-approved audit operations

### **6. redact_pii_for_exemplars**

**Purpose**: Redact personally identifiable information from Guardian exemplars

**Function Signature:**
```python
def redact_pii_for_exemplars(
    data: Dict[str, Any],
    pii_fields: List[str]
) -> Dict[str, Any]
```

**Privacy Protection:**
```python
from guardian import redact_pii_for_exemplars, emit_guardian_action_with_exemplar

def handle(msg: MatrizMessage) -> MatrizResult:
    result = process_matriz_message(msg)

    # Redact PII before emitting exemplar
    redacted_payload = redact_pii_for_exemplars(
        data=msg.payload,
        pii_fields=["user_email", "user_name", "phone_number", "ssn"]
    )

    # Safe to emit for learning
    emit_guardian_action_with_exemplar(
        action="cognitive_processing",
        exemplar={
            "payload": redacted_payload,  # PII removed
            "glyph_kind": msg.glyph.kind,
            "topic": msg.topic
        },
        outcome="success",
        metadata={"pii_redacted": True}
    )

    return result
```

---

## GTΨ (Guardian Tier Psi) Step-Up Protocol

### **Overview**

GTΨ is the **graduated validation protocol** for MATRIZ operations requiring enhanced Guardian oversight.

### **Validation Tiers**

#### **Tier 0: Monitor Only**
- **Lane**: experimental
- **Validation**: Passive monitoring, no blocking
- **Use Case**: Research and development
- **GLYPH kinds**: All allowed

#### **Tier 1: Standard Validation**
- **Lane**: candidate
- **Validation**: Basic Constitutional AI checks
- **Use Case**: Pre-production testing
- **GLYPH kinds**: MEMORY, CONTEXT, SENSORY_*

#### **Tier 2: Enhanced Validation**
- **Lane**: candidate, prod
- **Validation**: Full Constitutional AI validation
- **Use Case**: Standard production operations
- **GLYPH kinds**: THOUGHT, EMOTION, REFLECTION, AWARENESS

#### **Tier 3: GTΨ Step-Up (Privileged)**
- **Lane**: prod
- **Validation**: Enhanced validation + dual approval
- **Use Case**: Privileged operations
- **GLYPH kinds**: INTENT, DECISION
- **Requirements**:
  - Guardian approval
  - ΛiD authentication (Anchor Star ⚛️)
  - Dual approval for sensitive operations
  - Complete audit trail

### **GTΨ Implementation**

```python
from guardian import validate_dual_approval, emit_guardian_decision
from matriz.node_contract import MatrizMessage, MatrizResult, mk_guardian_token

def gtpsi_validation(msg: MatrizMessage) -> MatrizResult:
    """GTΨ step-up validation for privileged operations"""

    # Check if GTΨ required
    gtpsi_required = (
        msg.glyph.kind in ["INTENT", "DECISION"] and
        msg.lane == "prod" and
        msg.topic in ["BREAKTHROUGH", "CONTRADICTION"]
    )

    if not gtpsi_required:
        # Standard validation
        decision = emit_guardian_decision(
            operation="standard_validation",
            decision="approved",
            reason="Standard validation passed",
            glyph_kind=msg.glyph.kind,
            msg_id=str(msg.msg_id),
            lane=msg.lane,
            metadata={"tier": 2}
        )
        return MatrizResult(
            ok=True,
            reasons=[decision.reason],
            payload={},
            trace={"validation_tier": 2},
            guardian_log=[f"Tier 2 validation: {decision.decision}"]
        )

    # GTΨ Step-Up Required
    dual_approved = validate_dual_approval(
        operation="gtpsi_step_up",
        primary_approver="guardian_system",
        secondary_approver="human_supervisor",
        operation_metadata={"msg_id": str(msg.msg_id)}
    )

    if not dual_approved:
        return MatrizResult(
            ok=False,
            reasons=["GTΨ step-up required but dual approval not granted"],
            payload={},
            trace={"validation_tier": 3, "gtpsi_required": True},
            guardian_log=[
                "GTΨ step-up protocol activated",
                "Dual approval required",
                "Approval not granted - operation blocked"
            ]
        )

    # GTΨ approved
    decision = emit_guardian_decision(
        operation="gtpsi_step_up",
        decision="approved",
        reason="GTΨ step-up validation passed with dual approval",
        glyph_kind=msg.glyph.kind,
        msg_id=str(msg.msg_id),
        lane=msg.lane,
        metadata={"tier": 3, "dual_approval": True}
    )

    return MatrizResult(
        ok=True,
        reasons=[decision.reason],
        payload={"gtpsi_approved": True},
        trace={
            "validation_tier": 3,
            "gtpsi_protocol": "activated",
            "dual_approval": "granted"
        },
        guardian_log=[
            "GTΨ step-up protocol activated",
            "Dual approval granted",
            f"GTΨ validation: {decision.decision}"
        ]
    )
```

---

## MATRIZ Integration Patterns

### **Pattern 1: Standard MatrizNode Validation**

Every MatrizNode must integrate Guardian validation:

```python
from guardian import emit_guardian_decision
from matriz.node_contract import MatrizNode, MatrizMessage, MatrizResult

class MyMatrizNode(MatrizNode):
    name = "my-node"
    version = "1.0.0"

    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # 1. Request Guardian validation
        decision = emit_guardian_decision(
            operation=f"{self.name}_processing",
            decision="approved",  # Determine based on checks
            reason="Operation within constitutional bounds",
            glyph_kind=msg.glyph.kind,
            msg_id=str(msg.msg_id),
            lane=msg.lane,
            metadata={"node": self.name}
        )

        # 2. Check Guardian decision
        if decision.decision != "approved":
            return MatrizResult(
                ok=False,
                reasons=[f"Guardian rejected: {decision.reason}"],
                payload={},
                trace={"guardian_decision_id": decision.id},
                guardian_log=[f"Guardian decision: {decision.decision}"]
            )

        # 3. Process if approved
        result = self.process(msg)

        # 4. Add Guardian validation to result
        result.guardian_log.append(f"Guardian validated {self.name}")
        result.guardian_log.append(f"Decision: {decision.decision}")

        return result
```

### **Pattern 2: GTΨ Step-Up for Privileged Operations**

```python
from guardian import validate_dual_approval, emit_guardian_decision

class PrivilegedNode(MatrizNode):
    def handle(self, msg: MatrizMessage) -> MatrizResult:
        # Check if privileged operation
        if msg.glyph.kind in ["INTENT", "DECISION"]:
            # Require GTΨ step-up
            approved = validate_dual_approval(
                operation=f"{self.name}_privileged",
                primary_approver="guardian",
                secondary_approver="supervisor",
                operation_metadata={"msg_id": str(msg.msg_id)}
            )

            if not approved:
                return MatrizResult(
                    ok=False,
                    reasons=["GTΨ step-up required but not approved"],
                    payload={},
                    trace={"gtpsi_required": True},
                    guardian_log=["GTΨ step-up rejected"]
                )

        # Continue with standard processing
        return self.process(msg)
```

### **Pattern 3: Confidence Tracking**

```python
from guardian import emit_confidence_metrics, emit_guardian_decision

def handle(msg: MatrizMessage) -> MatrizResult:
    decision = emit_guardian_decision(...)

    # Track confidence
    confidence = emit_confidence_metrics(
        decision_id=decision.id,
        confidence_score=0.89,
        uncertainty_factors=["novel_pattern", "limited_training_data"],
        metadata={"node": self.name}
    )

    return MatrizResult(
        ok=True,
        reasons=["Approved with moderate confidence"],
        payload={"result": "success"},
        trace={"guardian_confidence": confidence.confidence_score},
        guardian_log=[f"Confidence: {confidence.confidence_score:.2f}"]
    )
```

---

## Constellation Framework Integration

### **Watch Star 🛡️ Coordination**

The Guardian system (Watch Star) coordinates with other Constellation stars:

```
Guardian Watch Star 🛡️
    │
    ├─→ Anchor Star ⚛️ (Identity)
    │   └─ ΛiD authentication for INTENT GLYPH
    │
    ├─→ Trail Star ✦ (Memory)
    │   └─ Guardian audit trail persistence
    │
    ├─→ MATRIZ Risk Stage
    │   └─ Ethics validation in cognitive pipeline
    │
    └─→ Runtime Policy (matriz/runtime)
        └─ Policy enforcement and resource limits
```

### **MATRIZ Risk Stage Integration**

```
Memory → Attention → Thought → RISK → Intent → Action
   M         A         T       R      I        A
                                │
                          Guardian 🛡️
                          Validation
                                │
                          ┌─────┴─────┐
                          │           │
                    Constitutional  GTΨ
                       AI Check    Step-Up
```

---

## Production Readiness

**Guardian Module Status**: 95% production ready

### ✅ Completed

- [x] 6 core Guardian functions implemented
- [x] GTΨ step-up protocol defined
- [x] MATRIZ contract integration
- [x] Dual approval mechanism
- [x] Confidence tracking and metrics
- [x] PII redaction for exemplars
- [x] Exemption system for emergencies
- [x] Complete audit trail logging
- [x] Constitutional AI validation framework

### 🔄 In Progress

- [ ] Machine learning for Guardian decision optimization
- [ ] Advanced pattern recognition for threat detection
- [ ] Real-time Guardian dashboard and monitoring

### 📋 Pending

- [ ] Comprehensive security audit
- [ ] Load testing for high-volume validation
- [ ] Enterprise Guardian policy templates

---

## Related Documentation

### **Guardian Contexts**
- [../matriz/lukhas_context.md](../matriz/lukhas_context.md:1) - MATRIZ cognitive engine
- [../matriz/runtime/lukhas_context.md](../matriz/runtime/lukhas_context.md:1) - Runtime policy enforcement
- [../governance/lukhas_context.md](../governance/lukhas_context.md:1) - Constitutional AI and policy
- [../identity/lukhas_context.md](../identity/lukhas_context.md:1) - ΛiD authentication

### **Technical Specifications**
- [../matriz/node_contract.py](../matriz/node_contract.py:1) - FROZEN v1.0.0 MatrizNode interface
- [../matriz/matriz_node_v1.json](../matriz/matriz_node_v1.json:1) - JSON Schema v1.1
- [../audit/MATRIZ_READINESS.md](../audit/MATRIZ_READINESS.md:1) - Production readiness

### **Governance Documentation**
- [../branding/MATRIZ_BRAND_GUIDE.md](../branding/MATRIZ_BRAND_GUIDE.md:1) - Official naming conventions
- [../docs/MATRIZ_TAIL_LATENCY_OPTIMIZATION.md](../docs/MATRIZ_TAIL_LATENCY_OPTIMIZATION.md:1) - Performance optimization

---

**Guardian Module**: Constitutional AI validation & GTΨ protocol | **Watch Star**: 🛡️ Security oversight
**Integration**: All MATRIZ operations | **Production**: 95% ready | **Schema**: 3.0.0
**Contract**: MatrizNode guardian_log required | **Tier**: L2 Integration
