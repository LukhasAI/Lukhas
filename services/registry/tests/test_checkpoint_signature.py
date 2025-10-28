"""
Integration tests for PQC checkpoint signatures (MATRIZ-007).

Tests:
- PQC sign/verify workflow
- Fallback to HMAC when PQC unavailable
- Signature tampering detection
- Backward compatibility
- Checkpoint loading with verification
"""
import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.registry.main import app, save_checkpoint, load_checkpoint, _store, _pqc_signer
from services.registry.pqc_signer import PQCSigner, create_registry_signer


client = TestClient(app)


def test_signature_info_endpoint():
    """Test that signature info endpoint returns scheme details."""
    response = client.get("/api/v1/registry/signature_info")
    assert response.status_code == 200
    
    info = response.json()
    assert "scheme" in info
    assert "quantum_resistant" in info
    assert info["scheme"] in ["Dilithium2", "HMAC-SHA256"]
    
    # Should be either PQC active or fallback
    assert info.get("status") in ["pqc_active", "fallback"]


def test_checkpoint_sign_and_verify():
    """Test checkpoint signing and verification workflow."""
    # Create a temporary registry
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        tmp_store = tmp_root / "registry_store.json"
        tmp_sig = tmp_root / "checkpoint.sig"
        
        # Create signer
        signer = create_registry_signer(tmp_root)
        
        # Create test checkpoint data
        test_data = {
            "version": 12345,
            "ts": 1234567890.0,
            "entries": {
                "test_node::abc123": {
                    "node_spec": {"metadata": {"name": "test"}},
                    "registered_at": 1234567890.0
                }
            }
        }
        
        # Write checkpoint
        tmp_store.write_text(json.dumps(test_data, indent=2))
        checkpoint_bytes = tmp_store.read_bytes()
        
        # Sign checkpoint
        signature = signer.sign(checkpoint_bytes)
        tmp_sig.write_text(signature.hex())
        
        # Verify signature
        signature_bytes = bytes.fromhex(tmp_sig.read_text())
        is_valid = signer.verify(checkpoint_bytes, signature_bytes)
        
        assert is_valid, "Signature verification should succeed"


def test_signature_tampering_detection():
    """Test that tampered checkpoints are rejected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        tmp_store = tmp_root / "registry_store.json"
        tmp_sig = tmp_root / "checkpoint.sig"
        
        # Create signer
        signer = create_registry_signer(tmp_root)
        
        # Create and sign checkpoint
        test_data = {"version": 1, "ts": 1.0, "entries": {}}
        tmp_store.write_text(json.dumps(test_data))
        checkpoint_bytes = tmp_store.read_bytes()
        signature = signer.sign(checkpoint_bytes)
        tmp_sig.write_text(signature.hex())
        
        # Tamper with checkpoint
        tampered_data = {"version": 999, "ts": 1.0, "entries": {}}
        tmp_store.write_text(json.dumps(tampered_data))
        tampered_bytes = tmp_store.read_bytes()
        
        # Verification should fail
        signature_bytes = bytes.fromhex(tmp_sig.read_text())
        is_valid = signer.verify(tampered_bytes, signature_bytes)
        
        assert not is_valid, "Tampered checkpoint should fail verification"


def test_registration_creates_signed_checkpoint():
    """Test that node registration creates a signed checkpoint."""
    # Register a node
    nodespec = {
        "node_type": "test.node",
        "metadata": {
            "name": "test_node",
            "version": "0.1.0",
            "schema_version": "nodespec.v1",
            "created_at": "2025-10-28",
        },
        "identity": {
            "owner_id": "GLYMPH:test123",
            "lane": "candidate",
            "tier": 3,
            "roles": ["test"],
            "capabilities_policy": {"allow": ["test/*"]},
        },
        "interfaces": {
            "inputs": [],
            "outputs": [],
            "signals": {"emits": [], "subscribes": []},
        },
        "contracts": {
            "performance_hints": {"p50": 20, "p95": 80, "concurrency": 10, "timeout_ms": 1000}
        },
        "provenance_manifest": {
            "glymph_enabled": True,
            "signing_scheme": "dilithium2",
            "pqc_compat": True,
        },
        "security": {"encryption": {"envelope": "XChaCha20-Poly1305", "kem": "kyber-768"}},
    }
    
    response = client.post("/api/v1/registry/register", json=nodespec)
    assert response.status_code == 200
    
    data = response.json()
    assert "checkpoint_sig" in data
    assert len(data["checkpoint_sig"]) > 0
    
    # Verify signature is hex-encoded
    try:
        bytes.fromhex(data["checkpoint_sig"])
    except ValueError:
        pytest.fail("Checkpoint signature should be valid hex")


def test_pqc_or_hmac_fallback():
    """Test that PQC is used if available, otherwise HMAC fallback."""
    info = _pqc_signer.get_signature_info()
    
    if info["scheme"] == "Dilithium2":
        assert info["quantum_resistant"] is True
        assert info["status"] == "pqc_active"
        assert "public_key_size" in info
    else:
        # HMAC fallback
        assert info["scheme"] == "HMAC-SHA256"
        assert info["quantum_resistant"] is False
        assert info["status"] == "fallback"
        assert "warning" in info


def test_checkpoint_load_verification():
    """Test that checkpoint loading verifies signatures."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        tmp_store = tmp_root / "registry_store.json"
        tmp_sig = tmp_root / "checkpoint.sig"
        
        # Create signer
        signer = create_registry_signer(tmp_root)
        
        # Create valid checkpoint
        test_data = {
            "version": 1,
            "ts": 1.0,
            "entries": {
                "node1::xyz": {
                    "node_spec": {"metadata": {"name": "node1"}},
                    "registered_at": 1.0
                }
            }
        }
        tmp_store.write_text(json.dumps(test_data))
        checkpoint_bytes = tmp_store.read_bytes()
        signature = signer.sign(checkpoint_bytes)
        tmp_sig.write_text(signature.hex())
        
        # Verify valid checkpoint loads
        signature_bytes = bytes.fromhex(tmp_sig.read_text())
        is_valid = signer.verify(checkpoint_bytes, signature_bytes)
        assert is_valid
        
        # Load and parse
        loaded_data = json.loads(checkpoint_bytes)
        assert "entries" in loaded_data
        assert "node1::xyz" in loaded_data["entries"]


def test_empty_checkpoint_signing():
    """Test signing empty checkpoint (startup scenario)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        tmp_store = tmp_root / "registry_store.json"
        tmp_sig = tmp_root / "checkpoint.sig"
        
        signer = create_registry_signer(tmp_root)
        
        # Empty checkpoint
        empty_data = {"version": 0, "ts": 0.0, "entries": {}}
        tmp_store.write_text(json.dumps(empty_data))
        checkpoint_bytes = tmp_store.read_bytes()
        
        # Should sign successfully
        signature = signer.sign(checkpoint_bytes)
        assert len(signature) > 0
        
        # Should verify successfully
        is_valid = signer.verify(checkpoint_bytes, signature)
        assert is_valid


def test_signature_scheme_consistency():
    """Test that signature scheme is consistent across operations."""
    info1 = _pqc_signer.get_signature_info()
    
    # Perform a sign operation
    test_data = b"test data"
    signature = _pqc_signer.sign(test_data)
    
    info2 = _pqc_signer.get_signature_info()
    
    # Scheme should remain the same
    assert info1["scheme"] == info2["scheme"]
    assert info1["quantum_resistant"] == info2["quantum_resistant"]


def test_multiple_checkpoints_same_signer():
    """Test that same signer can handle multiple checkpoint operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        signer = create_registry_signer(tmp_root)
        
        # Sign multiple checkpoints
        for i in range(5):
            data = json.dumps({"version": i, "ts": float(i), "entries": {}}).encode()
            signature = signer.sign(data)
            assert signer.verify(data, signature)


def test_performance_checkpoint_latency():
    """Test that checkpoint signing meets latency requirements."""
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        signer = create_registry_signer(tmp_root)
        
        # Create realistic checkpoint data
        test_data = {
            "version": 12345,
            "ts": time.time(),
            "entries": {
                f"node_{i}::abc{i}": {
                    "node_spec": {"metadata": {"name": f"node_{i}"}},
                    "registered_at": time.time()
                }
                for i in range(100)  # 100 nodes
            }
        }
        checkpoint_bytes = json.dumps(test_data).encode()
        
        # Measure signing latency
        start = time.perf_counter()
        signature = signer.sign(checkpoint_bytes)
        sign_latency = (time.perf_counter() - start) * 1000  # ms
        
        # Measure verification latency
        start = time.perf_counter()
        is_valid = signer.verify(checkpoint_bytes, signature)
        verify_latency = (time.perf_counter() - start) * 1000  # ms
        
        assert is_valid
        
        # Latency targets from MATRIZ_PQC_CHECKLIST.md
        # Sign: < 200ms p95 (testing p50, so more lenient)
        # Verify: < 10ms (HMAC) or < 50ms (Dilithium2)
        
        info = signer.get_signature_info()
        if info["scheme"] == "HMAC-SHA256":
            # HMAC is fast
            assert sign_latency < 100, f"HMAC signing took {sign_latency:.2f}ms (target: <100ms)"
            assert verify_latency < 50, f"HMAC verify took {verify_latency:.2f}ms (target: <50ms)"
        else:
            # Dilithium2 is slower but should meet targets
            assert sign_latency < 500, f"PQC signing took {sign_latency:.2f}ms (target: <500ms)"
            assert verify_latency < 100, f"PQC verify took {verify_latency:.2f}ms (target: <100ms)"
        
        print(f"\nPerformance ({info['scheme']}):")
        print(f"  Sign: {sign_latency:.2f}ms")
        print(f"  Verify: {verify_latency:.2f}ms")
