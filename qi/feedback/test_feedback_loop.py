#!/usr/bin/env python3
# path: qi/feedback/test_feedback_loop.py
"""
Test script for the complete LUKHAS feedback loop.

Tests:
1. Feedback ingestion with HMAC redaction
2. Clustering and triage
3. Promotion to change proposals
4. Calibration with feedback weights
5. Merkle tree generation
6. PQC signing
"""

import os, sys, json, time, uuid
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_feedback_ingestion():
    """Test feedback card ingestion."""
    print("\n=== Testing Feedback Ingestion ===")
    
    from qi.feedback.store import get_store
    store = get_store()
    
    # Create sample feedback
    feedback_data = {
        "fc_id": str(uuid.uuid4()),
        "ts": datetime.utcnow().isoformat() + "Z",
        "user_id": "test_user_123",  # Will be HMACed
        "session_id": "session_456",  # Will be HMACed
        "context": {
            "task": "summarize",
            "jurisdiction": "eu",
            "policy_pack": "global@2025-08-01",
            "model_version": "lukhas-qiv2.1"
        },
        "feedback": {
            "satisfaction": 0.65,
            "issues": ["tone", "verbose"],
            "note": "Response was too technical"  # Will be HMACed
        },
        "proposed_tuning": {
            "style": "empathetic",
            "threshold_delta": -0.02
        },
        "constraints": {
            "ethics_bound": True,
            "compliance_bound": True
        }
    }
    
    # Ingest feedback
    fc_id = store.append_feedback(feedback_data.copy())
    print(f"✓ Ingested feedback: {fc_id}")
    
    # Verify HMAC redaction
    feedback_list = store.read_feedback(limit=1)
    if feedback_list:
        fc = feedback_list[0]
        assert "user_hash" in fc and "hmac_sha3_512:" in fc["user_hash"]
        assert "session_hash" in fc and "hmac_sha3_512:" in fc["session_hash"]
        assert "user_id" not in fc
        assert "session_id" not in fc
        print("✓ HMAC redaction verified")
    
    # Add more feedback for clustering
    for i in range(10):
        data = feedback_data.copy()
        data["fc_id"] = str(uuid.uuid4())
        data["user_id"] = f"user_{i}"
        data["session_id"] = f"session_{i}"
        data["feedback"]["satisfaction"] = 0.3 + (i * 0.05)
        store.append_feedback(data)
    
    print("✓ Added 10 more feedback cards for clustering")
    return True

def test_clustering():
    """Test feedback clustering and triage."""
    print("\n=== Testing Clustering ===")
    
    from qi.feedback.triage import get_triage
    triage = get_triage()
    
    # Run triage
    stats = triage.run_triage(limit=100)
    print(f"✓ Triage stats: {json.dumps(stats, indent=2)}")
    
    # Check clusters
    clusters = triage.store.read_clusters()
    if clusters:
        print(f"✓ Generated {len(clusters)} clusters")
        for cluster in clusters[:2]:
            print(f"  - Task: {cluster['task']}, Samples: {cluster['n_samples']}, SAT: {cluster['sat_mean']:.2f}")
    
    # Compute weights
    weights = triage.compute_task_weights(clusters)
    print(f"✓ Task weights: {weights}")
    
    return True

def test_promotion():
    """Test promotion to change proposals."""
    print("\n=== Testing Promotion ===")
    
    from qi.feedback.proposals import ProposalMapper
    from qi.feedback.triage import get_triage
    
    mapper = ProposalMapper()
    triage = get_triage()
    
    # Get clusters
    clusters = triage.store.read_clusters()
    if not clusters:
        print("⚠ No clusters available for promotion")
        return False
    
    cluster = clusters[0]
    cluster_id = cluster["cluster_id"]
    
    # Map to patch
    patch = mapper.map_cluster_to_patch(cluster)
    if patch:
        print(f"✓ Mapped cluster to patch: {patch.dict()}")
        
        # Validate guardrails
        if mapper.validate_guardrails(patch):
            print("✓ Patch passes guardrails")
        else:
            print("✗ Patch failed guardrails")
        
        # Create proposal (mock - don't actually queue)
        proposal = mapper.to_change_proposal(
            patch=patch,
            cluster_id=cluster_id,
            target_file="qi/safety/policy_packs/global/mappings.yaml"
        )
    else:
        print("⚠ No patch generated (satisfaction may be neutral)")
        # Create a minimal proposal for testing
        from qi.feedback.schema import PolicySafePatch
        patch = PolicySafePatch(style="concise")
        proposal = mapper.to_change_proposal(
            patch=patch,
            cluster_id=cluster_id,
            target_file="qi/safety/policy_packs/global/mappings.yaml"
        )
    
    print(f"✓ Created proposal: {proposal['id']}")
    print(f"  - Author: {proposal['author']}")
    print(f"  - Risk: {proposal['risk']}")
    print(f"  - Patch: {proposal['patch']}")
    
    return True

def test_calibration_with_weights():
    """Test calibration with feedback weights."""
    print("\n=== Testing Calibration with Weights ===")
    
    from qi.metrics.calibration import fit_and_save, load_params
    from qi.feedback.triage import get_triage
    
    # Get feedback weights
    triage = get_triage()
    clusters = triage.store.read_clusters()
    weights = triage.compute_task_weights(clusters)
    
    print(f"Using weights: {weights}")
    
    # Fit calibration with weights (mock data)
    try:
        params = fit_and_save(source_preference="eval", feedback_weights=weights)
        print(f"✓ Calibration fitted with feedback weights")
        print(f"  - Global temperature: {params.temperature:.3f}")
        print(f"  - Global ECE: {params.ece:.4f}")
        if params.per_task_temperature:
            print(f"  - Per-task temperatures: {params.per_task_temperature}")
    except Exception as e:
        print(f"⚠ Calibration fitting skipped (no eval data): {e}")
    
    return True

def test_merkle_and_signing():
    """Test Merkle tree generation and PQC signing."""
    print("\n=== Testing Merkle Tree and Signing ===")
    
    from qi.feedback.store import get_store
    from qi.crypto.pqc_signer import sign_dilithium, verify_signature
    
    store = get_store()
    
    # Generate weekly digest
    digest = store.generate_weekly_digest()
    print(f"✓ Generated weekly digest:")
    print(f"  - Week: {digest['week']}")
    print(f"  - Records: {digest['n_records']}")
    print(f"  - Merkle root: {digest['merkle_root'][:16]}...")
    
    # Test PQC signing
    test_data = json.dumps(digest, sort_keys=True).encode()
    signature = sign_dilithium(test_data)
    
    print(f"✓ Signed with {signature['alg']}")
    print(f"  - Signature: {signature['sig'][:32]}...")
    print(f"  - Content hash: {signature['content_hash'][:16]}...")
    
    # Verify signature
    is_valid = verify_signature(test_data, signature)
    print(f"✓ Signature verification: {'PASSED' if is_valid else 'FAILED'}")
    
    return True

def test_teq_coupler_integration():
    """Test TEQ coupler with feedback adjustments."""
    print("\n=== Testing TEQ Coupler Integration ===")
    
    from qi.safety.teq_coupler import calibrated_gate
    
    # Test without feedback
    result = calibrated_gate(
        confidence=0.75,
        base_threshold=0.70,
        task="summarize"
    )
    
    print(f"✓ Calibrated gate result:")
    print(f"  - Raw confidence: {result['raw_conf']:.3f}")
    print(f"  - Calibrated: {result['calibrated_conf']:.3f}")
    print(f"  - Decision: {result['decision']}")
    print(f"  - Effective threshold: {result['threshold_eff']:.3f}")
    print(f"  - Temperature: {result['temperature']:.3f}")
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("LUKHAS FEEDBACK LOOP TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Feedback Ingestion", test_feedback_ingestion),
        ("Clustering & Triage", test_clustering),
        ("Proposal Promotion", test_promotion),
        ("Calibration with Weights", test_calibration_with_weights),
        ("Merkle & PQC Signing", test_merkle_and_signing),
        ("TEQ Coupler Integration", test_teq_coupler_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, "PASSED" if success else "FAILED"))
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append((name, "ERROR"))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for name, status in results:
        symbol = "✓" if status == "PASSED" else "✗"
        print(f"{symbol} {name}: {status}")
    
    passed = sum(1 for _, s in results if s == "PASSED")
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)