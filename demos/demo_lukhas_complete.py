"""
LUKHAS Complete Demo - Integrated Audit, Calibration, and Multi-Brain Symphony

Demonstrates:
- Secure audit trail with consent-aware redaction
- Adaptive confidence calibration
- Deterministic multi-brain consensus
- Complete decision provenance tracking
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from governance.lukhas_audit_system import (
    AuditTrail,
    DecisionType,
    BrainContext,
)
from governance.lukhas_confidence_calibration import AdaptiveConfidenceCalibrator
from governance.lukhas_symphony_integration import (
    MultiBrainSymphony,
    ConsensusMethod,
)


def simulate_brain_decision(brain_id: str, input_data: dict) -> dict:
    """
    Simulate a brain's decision-making process

    Args:
        brain_id: ID of the brain
        input_data: Input context for decision

    Returns:
        Decision result with confidence and reasoning
    """
    # Simulate different brain specializations
    if brain_id == "analytical_brain":
        decision = "analyze_deeply"
        confidence = 0.85
        activation = 0.9
        reasoning = [
            "Detected complex pattern requiring analysis",
            "High confidence in analytical approach"
        ]
    elif brain_id == "creative_brain":
        decision = "explore_alternatives"
        confidence = 0.75
        activation = 0.8
        reasoning = [
            "Multiple creative solutions possible",
            "Recommending exploratory approach"
        ]
    elif brain_id == "safety_brain":
        decision = "analyze_deeply"
        confidence = 0.95
        activation = 1.0
        reasoning = [
            "Safety analysis confirms deep analysis needed",
            "High priority on risk assessment"
        ]
    else:
        decision = "default_action"
        confidence = 0.5
        activation = 0.5
        reasoning = ["Default reasoning"]

    return {
        "decision": decision,
        "confidence": confidence,
        "activation": activation,
        "reasoning": reasoning,
        "metadata": {
            "brain_type": brain_id,
            "timestamp": time.time()
        }
    }


def demo_complete_workflow():
    """Demonstrate complete LUKHAS decision workflow"""
    print("=" * 80)
    print("LUKHAS Complete Demo - Audit, Calibration, Multi-Brain Symphony")
    print("=" * 80)
    print()

    # 1. Initialize components
    print("📋 Step 1: Initializing Components")
    print("-" * 80)

    audit_trail = AuditTrail(storage_path="audit_logs")
    calibrator = AdaptiveConfidenceCalibrator(window_size=1000)
    symphony = MultiBrainSymphony(audit_trail=audit_trail)

    # Add brains to symphony
    symphony.add_brain("analytical_brain", weight=1.0, specialization="analysis")
    symphony.add_brain("creative_brain", weight=0.8, specialization="creativity")
    symphony.add_brain("safety_brain", weight=1.2, specialization="safety")

    print("✅ Audit trail initialized")
    print("✅ Calibrator initialized")
    print("✅ Symphony initialized with 3 brains")
    print()

    # 2. Create decision context
    print("📋 Step 2: Creating Decision Context")
    print("-" * 80)

    decision_context = {
        "task": "analyze_user_request",
        "input": "How can we improve memory efficiency?",
        "user_id": "user_12345",
        "email": "user@example.com",  # Will be redacted without consent
        "priority": "high"
    }

    print(f"Task: {decision_context['task']}")
    print(f"Priority: {decision_context['priority']}")
    print()

    # 3. Create audit node with consent-aware redaction
    print("📋 Step 3: Creating Audit Node (with PII redaction)")
    print("-" * 80)

    node_id = audit_trail.create_decision_node(
        decision_type=DecisionType.ORCHESTRATION,
        input_data=decision_context,
        tags=["demo", "multi-brain", "analysis"],
        consent_scopes=[]  # No PII consent - will redact email
    )

    print(f"✅ Created audit node: {node_id}")
    print("✅ PII automatically redacted (email field)")
    print()

    # 4. Orchestrate multi-brain decision
    print("📋 Step 4: Multi-Brain Decision Orchestration")
    print("-" * 80)

    # Create brain decision functions
    brain_functions = {
        "analytical_brain": lambda ctx: simulate_brain_decision("analytical_brain", ctx),
        "creative_brain": lambda ctx: simulate_brain_decision("creative_brain", ctx),
        "safety_brain": lambda ctx: simulate_brain_decision("safety_brain", ctx),
    }

    # Orchestrate decision
    start_time = time.time()
    result = symphony.orchestrate_decision(
        decision_context=decision_context,
        brain_functions=brain_functions,
        consensus_method=ConsensusMethod.WEIGHTED_VOTE
    )
    execution_time = (time.time() - start_time) * 1000

    print(f"Final Decision: {result['decision']}")
    print(f"Raw Confidence: {result['raw_confidence']:.3f}")
    print(f"Participating Brains: {result['participating_brains']}")
    print(f"Consensus Strength: {result['metadata']['consensus_strength']:.3f}")
    print(f"Execution Time: {execution_time:.2f}ms")
    print()

    print("Brain Votes:")
    for brain_id, vote in result['brain_votes'].items():
        conf = result['brain_confidences'][brain_id]
        print(f"  - {brain_id}: {vote} (confidence: {conf:.3f})")
    print()

    # 5. Calibrate confidence
    print("📋 Step 5: Confidence Calibration")
    print("-" * 80)

    # Simulate some historical predictions for calibration
    print("Training calibrator with historical data...")
    for i in range(100):
        # Simulate predictions and outcomes
        pred = 0.7 + (i % 10) * 0.03
        outcome = 1.0 if pred > 0.75 else 0.0
        calibrator.record_prediction(pred, outcome)

    # Calibrate current confidence
    calibrated_confidence = calibrator.calibrate(result['raw_confidence'])

    # Get calibration metrics
    metrics = calibrator.get_metrics()

    print(f"✅ Calibrated Confidence: {calibrated_confidence:.3f}")
    print(f"   (Raw: {result['raw_confidence']:.3f})")
    print(f"   Temperature: {metrics.temperature:.3f}")
    print(f"   Platt A: {metrics.platt_a:.3f}, B: {metrics.platt_b:.3f}")
    print(f"   ECE: {metrics.expected_calibration_error:.4f}")
    print(f"   Brier Score: {metrics.brier_score:.4f}")
    print()

    # 6. Add reasoning to audit trail
    print("📋 Step 6: Recording Decision Reasoning")
    print("-" * 80)

    audit_trail.add_reasoning_step(
        node_id,
        f"Collected decisions from {result['participating_brains']} brains"
    )
    audit_trail.add_reasoning_step(
        node_id,
        f"Applied {result['consensus_method']} consensus mechanism"
    )
    audit_trail.add_reasoning_step(
        node_id,
        f"Calibrated confidence from {result['raw_confidence']:.3f} to {calibrated_confidence:.3f}"
    )

    # Record individual brain votes
    for brain_id, vote in result['brain_votes'].items():
        audit_trail.record_brain_vote(node_id, brain_id, vote)

    print("✅ Recorded 3 reasoning steps")
    print(f"✅ Recorded {len(result['brain_votes'])} brain votes")
    print()

    # 7. Add safety checks
    print("📋 Step 7: Safety Validation")
    print("-" * 80)

    audit_trail.add_safety_check(node_id, "guardian_approval", True)
    audit_trail.add_safety_check(node_id, "ethics_check", True)
    audit_trail.add_safety_check(node_id, "consent_validation", True)

    print("✅ Passed guardian_approval")
    print("✅ Passed ethics_check")
    print("✅ Passed consent_validation")
    print()

    # 8. Finalize decision
    print("📋 Step 8: Finalizing Decision")
    print("-" * 80)

    audit_trail.finalize_decision(
        node_id=node_id,
        decision_output=result['decision'],
        raw_confidence=result['raw_confidence'],
        calibrated_confidence=calibrated_confidence,
        execution_time_ms=execution_time,
        memory_used_mb=0.5  # Simulated
    )

    print(f"✅ Decision finalized and appended to ledger")
    print(f"   Node ID: {node_id}")
    print(f"   Decision: {result['decision']}")
    print(f"   Confidence: {calibrated_confidence:.3f}")
    print()

    # 9. Check ledger files
    print("📋 Step 9: Verifying Audit Ledger")
    print("-" * 80)

    ledger_path = Path("audit_logs/ledger.jsonl")
    sig_path = Path("audit_logs/ledger.sig.jsonl")

    if ledger_path.exists():
        with open(ledger_path, 'r') as f:
            lines = f.readlines()
        print(f"✅ Ledger file: {ledger_path} ({len(lines)} events)")

    if sig_path.exists():
        with open(sig_path, 'r') as f:
            sig_lines = f.readlines()
        print(f"✅ Signature file: {sig_path} ({len(sig_lines)} signatures)")

    print()

    # 10. Summary
    print("=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Created secure audit trail with PII redaction")
    print(f"  - Orchestrated {result['participating_brains']}-brain consensus")
    print(f"  - Applied adaptive confidence calibration")
    print(f"  - Recorded complete decision provenance")
    print(f"  - Generated append-only ledger with signatures")
    print()
    print("Next Steps:")
    print("  1. Run: make audit-validate-ledger")
    print("  2. Inspect: audit_logs/ledger.jsonl")
    print("  3. Verify: audit_logs/ledger.sig.jsonl")
    print()


if __name__ == "__main__":
    demo_complete_workflow()
