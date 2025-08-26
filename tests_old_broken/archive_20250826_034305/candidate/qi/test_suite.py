#!/usr/bin/env python3
"""
QI Component Test Suite
Designed by: Gonzalo Dominguez - Lukhas AI
"""
import sys
import json
import time
import os
import tempfile
from typing import Dict, List, Any

# Test results tracking
results = {"passed": [], "failed": [], "errors": []}

def test_component(name: str, test_func):
    """Run a component test and track results"""
    print(f"\n🧪 Testing: {name}")
    try:
        test_func()
        print(f"✅ {name}: PASSED")
        results["passed"].append(name)
        return True
    except Exception as e:
        print(f"❌ {name}: FAILED - {str(e)}")
        results["failed"].append(name)
        results["errors"].append({"component": name, "error": str(e)})
        return False

def test_calibration():
    """Test calibration engine"""
    import numpy as np
    from qi.metrics.calibration import auto_calibrate, ECE, MCE
    
    # Generate test data
    np.random.seed(42)
    n = 100
    conf = np.random.rand(n)
    y = (conf > 0.5).astype(int)
    
    # Test auto-calibration
    cal_conf, cal_func = auto_calibrate(conf, y)
    assert cal_conf.shape == conf.shape
    assert callable(cal_func)
    
    # Test ECE/MCE
    ece = ECE(conf, y)
    mce = MCE(conf, y)
    assert 0 <= ece <= 1
    assert 0 <= mce <= 1
    print(f"  ECE: {ece:.4f}, MCE: {mce:.4f}")

def test_pii_detection():
    """Test PII detection and masking"""
    from qi.safety.pii import detect_pii, mask_pii
    
    text = "Contact john@example.com or call 555-123-4567. SSN: 123-45-6789"
    
    # Test detection
    hits = detect_pii(text)
    assert len(hits) >= 3  # email, phone, SSN
    print(f"  Found {len(hits)} PII items")
    
    # Test masking
    masked = mask_pii(text, hits)
    assert "john@example.com" not in masked
    assert "123-45-6789" not in masked
    assert "[EMAIL_REDACTED]" in masked or "***" in masked

def test_budget_governor():
    """Test budget governor"""
    from qi.ops.budgeter import Budgeter
    
    b = Budgeter()
    
    # Test planning
    plan = b.plan(text="Test input text")
    assert "tokens_planned" in plan
    assert "cost_usd" in plan
    assert "energy_wh" in plan
    print(f"  Tokens: {plan['tokens_planned']}, Cost: ${plan['cost_usd']:.4f}")
    
    # Test usage tracking
    b.track("user1", "task1", tokens=100, latency_ms=50)
    usage = b.get_usage("user1")
    assert usage["tokens"] == 100

def test_teq_gate():
    """Test TEQ gate with policies"""
    from qi.safety.teq_gate import TEQCoupler
    
    gate = TEQCoupler(
        policy_dir="qi/safety/policy_packs",
        jurisdiction="global"
    )
    
    # Test with clean context
    ctx = {
        "provenance": {"inputs": ["test"], "sources": ["api"]},
        "pii_masked": True,
        "tokens_planned": 100
    }
    
    result = gate.run("generate_summary", ctx)
    print(f"  Allowed: {result.allowed}, Reasons: {len(result.reasons)}")
    
    # Test with PII
    ctx_pii = {
        "text": "My email is test@example.com",
        "provenance": {"inputs": ["test"], "sources": ["api"]}
    }
    result_pii = gate.run("generate_summary", ctx_pii)
    assert not result_pii.allowed  # Should block PII

def test_provenance():
    """Test Merkle chain provenance"""
    from qi.ops.provenance import merkle_chain
    
    steps = [
        {"phase": "input", "user": "alice"},
        {"phase": "processing", "tokens": 100},
        {"phase": "output", "success": True}
    ]
    
    chain = merkle_chain(steps)
    assert len(chain) == 3
    assert all("hash" in step for step in chain)
    assert chain[0]["prev"] is None
    assert chain[1]["prev"] == chain[0]["hash"]
    print(f"  Chain length: {len(chain)}, Root: {chain[-1]['hash'][:16]}...")

def test_risk_orchestrator():
    """Test risk orchestrator"""
    from qi.safety.risk_orchestrator import RiskOrchestrator
    
    ro = RiskOrchestrator()
    
    # Test low risk
    ctx_low = {
        "calibrated_confidence": 0.8,
        "pii": {},
        "content_flags": []
    }
    plan_low = ro.route(task="test", ctx=ctx_low)
    assert plan_low.tier == "low"
    
    # Test high risk
    ctx_high = {
        "calibrated_confidence": 0.2,
        "pii": {"_auto_hits": [{"kind": "email"}]},
        "content_flags": ["medical"]
    }
    plan_high = ro.route(task="test", ctx=ctx_high)
    assert plan_high.tier in ["high", "critical"]
    print(f"  Low tier: {plan_low.tier}, High tier: {plan_high.tier}")

def test_confidence_router():
    """Test confidence router"""
    from qi.router.confidence_router import confidence_router
    
    # Test different confidence levels
    low = confidence_router(calibrated_conf=0.3)
    assert low["path"] == "high_compute"
    
    med = confidence_router(calibrated_conf=0.6)
    assert med["path"] == "balanced"
    
    high = confidence_router(calibrated_conf=0.9)
    assert high["path"] == "fast_track"
    
    print(f"  Routes: low={low['path']}, med={med['path']}, high={high['path']}")

def test_consent_guard():
    """Test consent management"""
    from qi.memory.consent_guard import ConsentGuard
    
    # Use temp storage
    with tempfile.NamedTemporaryFile(suffix=".jsonl") as f:
        guard = ConsentGuard(storage_path=f.name)
        
        # Test grant
        consent = guard.grant("user1", "test_purpose", ttl_seconds=60)
        assert consent.granted
        
        # Test check
        has_consent, _ = guard.check("user1", "test_purpose")
        assert has_consent
        
        # Test revoke
        guard.revoke("user1", "test_purpose")
        has_consent, _ = guard.check("user1", "test_purpose")
        assert not has_consent
        
        print(f"  Grant/Check/Revoke: OK")

def test_provenance_uploader():
    """Test provenance uploader"""
    from qi.safety.provenance_uploader import record_artifact, verify_artifact
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        temp_path = f.name
    
    try:
        # Record artifact
        rec = record_artifact(
            artifact_path=temp_path,
            model_id="test-model",
            prompt="test prompt",
            metadata={"test": True}
        )
        
        assert rec.artifact_sha256
        assert rec.storage_url
        
        # Verify artifact
        verify_result = verify_artifact(temp_path, {
            "artifact_sha256": rec.artifact_sha256,
            "storage_url": rec.storage_url,
            "storage_backend": rec.storage_backend
        })
        
        assert verify_result["ok"]
        print(f"  SHA: {rec.artifact_sha256[:16]}..., Verified: {verify_result['ok']}")
    finally:
        os.unlink(temp_path)

def test_policy_components():
    """Test policy-related components"""
    import subprocess
    
    # Test policy report
    result = subprocess.run([
        sys.executable, "-m", "qi.safety.policy_report",
        "--policy-root", "qi/safety/policy_packs",
        "--jurisdiction", "global"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        assert "matrix" in data
        assert "gaps" in data
        print(f"  Policy Report: {len(data['matrix'])} tasks, {len(data['gaps'])} gaps")
    else:
        raise Exception(f"Policy report failed: {result.stderr}")

def main():
    """Run all component tests"""
    print("=" * 50)
    print("🧪 LUKHAS QI Component Test Suite")
    print("Designed by: Gonzalo Dominguez - Lukhas AI")
    print("=" * 50)
    
    # Run all tests
    tests = [
        ("Calibration Engine", test_calibration),
        ("PII Detection", test_pii_detection),
        ("Budget Governor", test_budget_governor),
        ("TEQ Gate", test_teq_gate),
        ("Provenance Chain", test_provenance),
        ("Risk Orchestrator", test_risk_orchestrator),
        ("Confidence Router", test_confidence_router),
        ("ConsentGuard", test_consent_guard),
        ("Provenance Uploader", test_provenance_uploader),
        ("Policy Components", test_policy_components),
    ]
    
    for name, test_func in tests:
        test_component(name, test_func)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    
    if results["passed"]:
        print("\n✅ Passed Components:")
        for name in results["passed"]:
            print(f"  • {name}")
    
    if results["failed"]:
        print("\n❌ Failed Components:")
        for name in results["failed"]:
            print(f"  • {name}")
    
    # Overall result
    print("\n" + "=" * 50)
    if not results["failed"]:
        print("🎉 All QI components tested successfully!")
        return 0
    else:
        print(f"⚠️  {len(results['failed'])} components failed testing")
        return 1

if __name__ == "__main__":
    sys.exit(main())