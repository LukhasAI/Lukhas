"""
LUKHAS Audit & Observability Demo - Complete Integration

Demonstrates:
- OpenTelemetry tracing with MATRIZ stages
- Audit trail submission with signed permalinks
- Consent-aware evidence redaction
- Feedback collection and follow-ups
"""

import sys
import time
import uuid
import hashlib
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from observability.tracing import spanify, matriz_stage, set_trace_metadata
from observability.audit.models import DecisionTrace, TraceSpan, EvidenceLink, GovernanceEvent
from observability.audit.storage import write_json
from observability.audit.links import mint_signed_query, verify_signed_query
from observability.audit.redaction import mask_pii, viewer_allows_scope
from governance.metrics.confidence_calibration import AdaptiveConfidenceCalibrator
from consciousness.symphony.integration import MultiBrainSymphony


async def simulate_matriz_pipeline(user_input: str, trace_id: str) -> dict:
    """
    Simulate a complete MATRIZ pipeline with OTel tracing.

    Args:
        user_input: User query
        trace_id: Trace identifier

    Returns:
        Pipeline result with metadata
    """
    start_time = time.time()
    result = {"text": "", "confidence": 0.0, "spans": []}

    # Memory stage
    with matriz_stage("Memory", trace_id=trace_id, user_input_hash=hashlib.sha256(user_input.encode()).hexdigest()):
        time.sleep(0.01)  # Simulate work
        memory_result = "Retrieved 3 relevant memories"

        # Record span
        span = TraceSpan(
            span_id=f"span-{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            module="Memory",
            operation="retrieve",
            ts_start=start_time,
            ts_end=time.time(),
            status="OK"
        )
        await write_json("trace_span", {"id": span.span_id, **span.model_dump()})
        result["spans"].append(span)

        # Record evidence
        evidence = EvidenceLink(
            span_id=span.span_id,
            source_type="memory",
            uri_or_key="memory://fold-850",
            sha256=hashlib.sha256(b"memory-content").hexdigest(),
            excerpt="User previously asked about consciousness systems...",
            consent_scope="default"
        )
        await write_json("evidence_link", {"id": f"{evidence.span_id}:{evidence.uri_or_key}", **evidence.model_dump()})

    # Attention stage
    with matriz_stage("Attention", trace_id=trace_id):
        time.sleep(0.005)
        attention_result = "Focused on consciousness-related context"

        span = TraceSpan(
            span_id=f"span-{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            module="Attention",
            operation="focus",
            ts_start=time.time(),
            ts_end=time.time() + 0.005,
            status="OK"
        )
        await write_json("trace_span", {"id": span.span_id, **span.model_dump()})
        result["spans"].append(span)

    # Thought stage (reasoning)
    with matriz_stage("Thought", trace_id=trace_id):
        time.sleep(0.015)
        thought_result = "Applied causal reasoning to generate answer"

        span = TraceSpan(
            span_id=f"span-{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            module="Thought",
            operation="reason",
            ts_start=time.time(),
            ts_end=time.time() + 0.015,
            status="OK"
        )
        await write_json("trace_span", {"id": span.span_id, **span.model_dump()})
        result["spans"].append(span)

    # Risk stage (guardian)
    with matriz_stage("Risk", trace_id=trace_id):
        time.sleep(0.003)

        span = TraceSpan(
            span_id=f"span-{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            module="Risk",
            operation="validate",
            ts_start=time.time(),
            ts_end=time.time() + 0.003,
            status="OK"
        )
        await write_json("trace_span", {"id": span.span_id, **span.model_dump()})
        result["spans"].append(span)

        # Record governance event
        gov_event = GovernanceEvent(
            event_id=f"gov-{uuid.uuid4().hex[:8]}",
            trace_id=trace_id,
            rule_id="guardian.safety_check",
            decision="ALLOW",
            justification="No safety violations detected",
            feature_flags_snapshot={"guardian_v2": True}
        )
        await write_json("governance_event", {"id": gov_event.event_id, **gov_event.model_dump()})

    # Action stage
    with matriz_stage("Action", trace_id=trace_id):
        result["text"] = "LUKHAS consciousness systems integrate memory, reasoning, and safety..."
        result["confidence"] = 0.85

    return result


async def demo_complete_observability():
    """Demonstrate complete observability integration."""
    print("=" * 80)
    print("LUKHAS Audit & Observability Demo")
    print("=" * 80)
    print()

    # 1. Initialize components
    print("📋 Step 1: Initializing Observability Stack")
    print("-" * 80)

    trace_id = f"trace-{uuid.uuid4().hex}"
    user_input = "How do LUKHAS consciousness systems work?"
    calibrator = AdaptiveConfidenceCalibrator()

    print(f"✅ Trace ID: {trace_id}")
    print(f"✅ User Input: {user_input}")
    print()

    # 2. Execute MATRIZ pipeline with tracing
    print("📋 Step 2: Executing MATRIZ Pipeline with OTel Tracing")
    print("-" * 80)

    start_time = time.time()
    pipeline_result = await simulate_matriz_pipeline(user_input, trace_id)
    end_time = time.time()

    print(f"✅ Pipeline executed in {(end_time - start_time) * 1000:.2f}ms")
    print(f"✅ Generated {len(pipeline_result['spans'])} spans")
    print(f"✅ Raw confidence: {pipeline_result['confidence']:.3f}")
    print()

    # 3. Calibrate confidence
    print("📋 Step 3: Calibrating Confidence")
    print("-" * 80)

    # Train calibrator with some history
    for i in range(50):
        calibrator.record_prediction(0.7 + (i % 10) * 0.03, 1.0 if i % 3 == 0 else 0.0)

    calibrated = calibrator.calibrate(pipeline_result['confidence'])
    metrics = calibrator.get_metrics()

    print(f"✅ Calibrated confidence: {calibrated:.3f}")
    print(f"   ECE: {metrics.expected_calibration_error:.4f}")
    print(f"   Brier Score: {metrics.brier_score:.4f}")
    print()

    # 4. Store decision trace
    print("📋 Step 4: Storing Decision Trace")
    print("-" * 80)

    decision_trace = DecisionTrace(
        trace_id=trace_id,
        user_id="user_demo",
        session_id="session_123",
        input_hash=hashlib.sha256(user_input.encode()).hexdigest(),
        started_at=start_time,
        finished_at=end_time,
        latency_ms=int((end_time - start_time) * 1000),
        final_outcome={"text": pipeline_result["text"], "confidence": calibrated},
        confidence=calibrated,
        policy_version="v1",
        git_sha="demo"
    )

    await write_json("decision_trace", {"id": trace_id, **decision_trace.model_dump()})
    print(f"✅ Decision trace stored: {trace_id}")
    print()

    # 5. Generate signed permalink
    print("📋 Step 5: Generating Signed Permalink")
    print("-" * 80)

    viewer_id = "viewer@example.com"
    signed_query = mint_signed_query(trace_id, viewer_id, ttl_seconds=300)

    print(f"✅ Generated signed link (5min TTL)")
    print(f"   Viewer: {viewer_id}")
    print(f"   URL: /audit/trace/{trace_id}?{signed_query[:50]}...")
    print()

    # Verify it works
    params = dict([p.split("=") for p in signed_query.split("&")])
    valid, reason = verify_signed_query(trace_id, params)
    print(f"✅ Link verification: {'PASS' if valid else 'FAIL'} ({reason})")
    print()

    # 6. Demonstrate consent-aware redaction
    print("📋 Step 6: Consent-Aware Evidence Redaction")
    print("-" * 80)

    pii_text = "User email: user@example.com, phone: 555-1234"
    redacted = mask_pii(pii_text)

    print(f"Original: {pii_text}")
    print(f"Redacted: {redacted}")
    print()

    # Check scope permissions
    viewer_scopes_low = ["default"]
    viewer_scopes_high = ["default", "pii", "allow"]

    evidence_scope = "pii"
    print(f"Evidence scope: {evidence_scope}")
    print(f"  Viewer with {viewer_scopes_low}: {viewer_allows_scope(viewer_scopes_low, evidence_scope)}")
    print(f"  Viewer with {viewer_scopes_high}: {viewer_allows_scope(viewer_scopes_high, evidence_scope)}")
    print()

    # 7. Simulate feedback submission
    print("📋 Step 7: Collecting User Feedback")
    print("-" * 80)

    feedback_payload = {
        "id": f"fb:{trace_id}",
        "feedback_id": f"fb:{trace_id}",
        "trace_id": trace_id,
        "rating_0_10": 8,
        "text": "Great answer! Maybe add more examples.",
        "labels": {"helpful": 1.0, "needs-examples": 0.5}
    }

    await write_json("feedback_event", feedback_payload)
    print(f"✅ Feedback stored: {feedback_payload['feedback_id']}")
    print(f"   Rating: {feedback_payload['rating_0_10']}/10")
    print(f"   Comment: {feedback_payload['text']}")
    print()

    # 8. Summary
    print("=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Traced {len(pipeline_result['spans'])} MATRIZ stages with OpenTelemetry")
    print(f"  - Stored decision trace with calibrated confidence")
    print(f"  - Generated signed permalink (HMAC-SHA256)")
    print(f"  - Demonstrated PII redaction and scope-based access")
    print(f"  - Collected user feedback linked to trace")
    print()
    print("Files Created:")
    print(f"  - audit_logs/decision_trace.jsonl")
    print(f"  - audit_logs/trace_span.jsonl")
    print(f"  - audit_logs/evidence_link.jsonl")
    print(f"  - audit_logs/governance_event.jsonl")
    print(f"  - audit_logs/feedback_event.jsonl")
    print()
    print("Next Steps:")
    print("  1. Run: make audit-validate-ledger")
    print("  2. Run: make feedback-validate")
    print("  3. View trace: GET /audit/trace/{trace_id}")
    print("  4. Submit feedback: POST /feedback/")
    print()


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_complete_observability())
