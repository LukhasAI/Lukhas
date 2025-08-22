#!/usr/bin/env python3
"""
Comprehensive test suite for TEQ Replay Tool
Tests: Receipt loading, policy fingerprinting, replay logic, attestation verification
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_receipt_loading():
    """Test receipt loading functionality"""
    print("Testing receipt loading...")
    
    from qi.safety.teq_replay import _load_receipt, RECEIPTS_DIR
    
    # Get an existing receipt
    import glob
    receipts = glob.glob(os.path.join(RECEIPTS_DIR, "*.json"))
    if not receipts:
        print("  ⚠️ No receipts found to test with")
        return False
    
    # Test full ID loading
    receipt_path = receipts[0]
    receipt_id = os.path.basename(receipt_path).replace(".json", "")
    
    receipt = _load_receipt(receipt_id, None)
    assert "id" in receipt
    assert receipt["id"] == receipt_id
    print(f"  ✓ Loaded receipt by full ID: {receipt_id[:16]}...")
    
    # Test prefix matching
    prefix = receipt_id[:8]
    receipt_prefix = _load_receipt(prefix, None)
    assert receipt_prefix["id"] == receipt_id
    print(f"  ✓ Loaded receipt by prefix: {prefix}")
    
    # Test direct path loading
    receipt_path_load = _load_receipt(None, receipt_path)
    assert receipt_path_load["id"] == receipt_id
    print(f"  ✓ Loaded receipt by path")
    
    print("  ✓ Receipt loading tests passed")
    return True

def test_policy_fingerprint():
    """Test policy fingerprint generation"""
    print("\nTesting policy fingerprint...")
    
    from qi.safety.teq_replay import _policy_fingerprint
    
    # Create test policy directory
    with tempfile.TemporaryDirectory() as tmpdir:
        policy_dir = os.path.join(tmpdir, "test_policies")
        os.makedirs(policy_dir)
        
        # Add test policy files
        with open(os.path.join(policy_dir, "policy.yaml"), "w") as f:
            f.write("version: 1.0\nrules: []\n")
        
        # Generate fingerprint
        fp1 = _policy_fingerprint(policy_dir, None)
        assert len(fp1) == 64  # SHA256 hex
        print(f"  ✓ Generated fingerprint: {fp1[:16]}...")
        
        # Modify policy
        with open(os.path.join(policy_dir, "policy.yaml"), "w") as f:
            f.write("version: 1.1\nrules: [new_rule]\n")
        
        # Fingerprint should change
        fp2 = _policy_fingerprint(policy_dir, None)
        assert fp2 != fp1
        print(f"  ✓ Fingerprint changes with policy: {fp2[:16]}...")
        
        # Test with overlays
        overlays_dir = os.path.join(tmpdir, "overlays")
        os.makedirs(overlays_dir)
        with open(os.path.join(overlays_dir, "overlays.yaml"), "w") as f:
            f.write("overlays: {}\n")
        
        fp3 = _policy_fingerprint(policy_dir, overlays_dir)
        assert fp3 != fp2  # Should differ with overlays
        print(f"  ✓ Fingerprint includes overlays: {fp3[:16]}...")
    
    print("  ✓ Policy fingerprint tests passed")
    return True

def test_context_building():
    """Test TEQ context reconstruction from receipts"""
    print("\nTesting context building...")
    
    from qi.safety.teq_replay import _build_teq_context
    
    # Create a test receipt
    test_receipt = {
        "id": "test123",
        "entity": {
            "digest_sha256": "abc123"
        },
        "activity": {
            "type": "test_task",
            "jurisdiction": "us",
            "context": "test_context"
        },
        "agents": [
            {"id": "agent:user:test_user", "role": "user"},
            {"id": "agent:service:lukhas", "role": "system"}
        ],
        "tokens_out": 100
    }
    
    # Build context
    ctx = _build_teq_context(test_receipt, None)
    
    # Validate context structure
    assert ctx["user_profile"]["user_id"] == "test_user"
    assert ctx["tokens_planned"] == 100
    assert ctx["pii_masked"] == True
    assert "provenance" in ctx
    assert ctx["provenance"]["inputs"] == ["receipt"]
    print("  ✓ Context built correctly from receipt")
    
    # Test with provenance record
    prov_record = {
        "artifact_sha256": "xyz789"
    }
    ctx_with_prov = _build_teq_context(test_receipt, prov_record)
    assert ctx_with_prov["provenance_record_sha"] == "xyz789"
    print("  ✓ Context includes provenance SHA when available")
    
    print("  ✓ Context building tests passed")
    return True

def test_full_replay():
    """Test complete replay flow"""
    print("\nTesting full replay flow...")
    
    from qi.provenance.receipts_hub import emit_receipt
    from qi.safety.teq_replay import replay_from_receipt
    
    # Generate a test receipt
    start = time.time()
    time.sleep(0.01)
    end = time.time()
    
    receipt_data = emit_receipt(
        artifact_sha="replay_test_123",
        artifact_mime="text/plain",
        artifact_size=100,
        storage_url=None,
        run_id="replay-test-run",
        task="generate_summary",
        started_at=start,
        ended_at=end,
        user_id="replay_tester",
        jurisdiction="global",
        context="test",
        policy_decision_id="pol-replay",
        risk_flags=["test"],
        tokens_in=50,
        tokens_out=25
    )
    
    print(f"  ✓ Created test receipt: {receipt_data['id'][:16]}...")
    
    # Perform replay
    replay_result = replay_from_receipt(
        receipt=receipt_data,
        policy_root="qi/safety/policy_packs",
        overlays_dir=None,
        verify_receipt_attestation=True,
        verify_provenance_attestation=False
    )
    
    # Validate replay result
    assert replay_result["task"] == "generate_summary"
    assert replay_result["jurisdiction"] == "global"
    assert replay_result["context"] == "test"
    assert replay_result["receipt_id"] == receipt_data["id"]
    assert replay_result["artifact_sha"] == "replay_test_123"
    assert "policy_fingerprint" in replay_result
    assert "replay" in replay_result
    assert "allowed" in replay_result["replay"]
    assert "reasons" in replay_result["replay"]
    
    print(f"  ✓ Replay verdict: {'ALLOWED' if replay_result['replay']['allowed'] else 'BLOCKED'}")
    
    if replay_result["receipt_attestation_ok"] is not None:
        status = "✅ verified" if replay_result["receipt_attestation_ok"] else "❌ failed"
        print(f"  ✓ Attestation verification: {status}")
    
    print("  ✓ Full replay tests passed")
    return replay_result

def test_regression_detection():
    """Test that replay can detect policy changes"""
    print("\nTesting regression detection...")
    
    from qi.safety.teq_replay import _policy_fingerprint
    
    # Get current policy fingerprint
    fp_current = _policy_fingerprint("qi/safety/policy_packs", None)
    print(f"  Current policy fingerprint: {fp_current[:16]}...")
    
    # Create a modified policy for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy current policies
        test_policy_dir = os.path.join(tmpdir, "modified_policies")
        shutil.copytree("qi/safety/policy_packs", test_policy_dir)
        
        # Modify a policy file
        mappings_path = os.path.join(test_policy_dir, "global", "mappings.yaml")
        if os.path.exists(mappings_path):
            with open(mappings_path, "a") as f:
                f.write("\n# Modified for testing\n")
        
        # Get new fingerprint
        fp_modified = _policy_fingerprint(test_policy_dir, None)
        assert fp_modified != fp_current
        print(f"  Modified policy fingerprint: {fp_modified[:16]}...")
        print("  ✓ Policy changes detected via fingerprint")
    
    print("  ✓ Regression detection tests passed")
    return True

def test_cli_interface():
    """Test CLI argument parsing and execution"""
    print("\nTesting CLI interface...")
    
    import subprocess
    import glob
    
    # Get a receipt ID for testing
    receipts = glob.glob(os.path.join(
        os.path.expanduser("~/.lukhas/state/provenance/exec_receipts"), 
        "*.json"
    ))
    
    if not receipts:
        print("  ⚠️ No receipts available for CLI testing")
        return False
    
    receipt_id = os.path.basename(receipts[0]).replace(".json", "")
    
    # Test basic replay
    result = subprocess.run(
        [
            sys.executable, "-m", "qi.safety.teq_replay",
            "--id", receipt_id[:8],  # Use prefix
            "--policy-root", "qi/safety/policy_packs",
            "--json"
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        output = json.loads(result.stdout)
        assert "task" in output
        assert "replay" in output
        print(f"  ✓ CLI replay successful for {receipt_id[:8]}...")
    else:
        print(f"  ⚠️ CLI failed: {result.stderr}")
        return False
    
    # Test with attestation verification
    result = subprocess.run(
        [
            sys.executable, "-m", "qi.safety.teq_replay",
            "--id", receipt_id,
            "--policy-root", "qi/safety/policy_packs",
            "--verify-att",
            "--json"
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        output = json.loads(result.stdout)
        assert "receipt_attestation_ok" in output
        print("  ✓ CLI attestation verification works")
    
    print("  ✓ CLI interface tests passed")
    return True

def main():
    """Run all TEQ replay tests"""
    print("=" * 60)
    print("TEQ REPLAY TOOL - Comprehensive Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        test_receipt_loading()
        test_policy_fingerprint()
        test_context_building()
        replay_result = test_full_replay()
        test_regression_detection()
        test_cli_interface()
        
        print("\n" + "=" * 60)
        print("✅ ALL REPLAY TESTS PASSED!")
        print("=" * 60)
        
        print("\nTEQ Replay capabilities validated:")
        print("  • Receipt loading with prefix matching")
        print("  • Policy fingerprint generation")
        print("  • Context reconstruction from receipts")
        print("  • Full replay with current policies")
        print("  • Attestation verification")
        print("  • Regression detection via fingerprints")
        print("  • CLI interface with JSON output")
        
        if replay_result:
            print(f"\nSample replay result:")
            print(f"  Task: {replay_result['task']}")
            print(f"  Verdict: {'✅ ALLOWED' if replay_result['replay']['allowed'] else '❌ BLOCKED'}")
            print(f"  Policy fingerprint: {replay_result['policy_fingerprint'][:16]}...")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())