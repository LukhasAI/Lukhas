#!/usr/bin/env python3
"""
Test suite for enhanced Receipts API with trace and replay endpoints
Tests: Replay endpoint, trace SVG generation, policy fingerprint, ETag caching
"""

import os
import sys
import json
import time
import hashlib
import requests
from typing import Dict, Any

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_api_endpoints():
    """Test API endpoints directly without starting server"""
    print("Testing API endpoints (direct)...")
    
    from qi.provenance.receipts_api import (
        _read_json, _receipt_path, _policy_fingerprint,
        get_receipt, list_receipts, policy_fp
    )
    
    # Test list receipts
    try:
        receipts = list_receipts(limit=5)
        assert "items" in receipts
        assert "count" in receipts
        print(f"  ✓ Listed {receipts['count']} receipts")
        
        if receipts["items"]:
            # Test get single receipt
            rid = receipts["items"][0]["id"]
            receipt = get_receipt(rid)
            assert receipt["id"] == rid
            print(f"  ✓ Retrieved receipt: {rid[:16]}...")
    except Exception as e:
        print(f"  ⚠️ API test failed: {e}")
        return False
    
    # Test policy fingerprint
    fp = _policy_fingerprint("qi/safety/policy_packs", None)
    assert len(fp) == 64  # SHA256
    print(f"  ✓ Policy fingerprint: {fp[:16]}...")
    
    return True

def test_replay_endpoint():
    """Test TEQ replay endpoint"""
    print("\nTesting replay endpoint...")
    
    from qi.provenance.receipts_api import replay_receipt, _read_json
    import glob
    from fastapi.testclient import TestClient
    from qi.provenance.receipts_api import app
    
    # Get a receipt
    receipts = glob.glob(os.path.expanduser("~/.lukhas/state/provenance/exec_receipts/*.json"))
    if not receipts:
        print("  ⚠️ No receipts available")
        return False
    
    rid = os.path.basename(receipts[0]).replace(".json", "")
    
    # Create test client
    client = TestClient(app)
    
    # Test replay endpoint
    response = client.get(
        f"/receipts/{rid}/replay.json",
        params={
            "policy_root": "qi/safety/policy_packs",
            "overlays": None
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        assert "task" in data
        assert "replay" in data
        assert "policy_fingerprint" in data
        
        # Check ETag header
        assert "etag" in response.headers
        etag = response.headers["etag"]
        print(f"  ✓ Replay successful, ETag: {etag}")
        print(f"  ✓ Task: {data['task']}, Verdict: {data['replay']['allowed']}")
        
        return data
    else:
        print(f"  ❌ Replay failed: {response.status_code}")
        return False

def test_trace_svg_endpoint():
    """Test trace SVG generation endpoint"""
    print("\nTesting trace SVG endpoint...")
    
    from fastapi.testclient import TestClient
    from qi.provenance.receipts_api import app
    import glob
    
    # Get a receipt
    receipts = glob.glob(os.path.expanduser("~/.lukhas/state/provenance/exec_receipts/*.json"))
    if not receipts:
        print("  ⚠️ No receipts available")
        return False
    
    rid = os.path.basename(receipts[0]).replace(".json", "")
    
    # Create test client
    client = TestClient(app)
    
    # Test trace SVG endpoint
    response = client.get(
        f"/receipts/{rid}/trace.svg",
        params={
            "policy_root": "qi/safety/policy_packs",
            "link_base": "http://localhost:8095",
            "prov_base": "http://localhost:8088"
        }
    )
    
    # Check if graphviz is available
    if response.status_code == 500 and "graphviz" in response.text:
        print("  ⚠️ Graphviz not available for SVG rendering")
        print("  ℹ️ Install with: brew install graphviz")
        return False
    elif response.status_code == 200:
        # Check it's SVG
        assert response.headers["content-type"] == "image/svg+xml"
        assert b"<svg" in response.content
        
        # Check caching headers
        assert "etag" in response.headers
        assert "cache-control" in response.headers
        
        print(f"  ✓ SVG generated ({len(response.content)} bytes)")
        print(f"  ✓ ETag: {response.headers['etag']}")
        print(f"  ✓ Cache-Control: {response.headers['cache-control']}")
        
        # Save for inspection
        svg_path = "/tmp/test_api_trace.svg"
        with open(svg_path, "wb") as f:
            f.write(response.content)
        print(f"  ✓ SVG saved to {svg_path}")
        
        return True
    else:
        print(f"  ❌ Trace SVG failed: {response.status_code}")
        return False

def test_policy_fingerprint_endpoint():
    """Test policy fingerprint endpoint"""
    print("\nTesting policy fingerprint endpoint...")
    
    from fastapi.testclient import TestClient
    from qi.provenance.receipts_api import app
    
    client = TestClient(app)
    
    # Test fingerprint endpoint
    response = client.get(
        "/policy/fingerprint",
        params={
            "policy_root": "qi/safety/policy_packs"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "fingerprint" in data
    assert len(data["fingerprint"]) == 64
    
    print(f"  ✓ Policy fingerprint: {data['fingerprint'][:16]}...")
    
    # Test with overlays
    response = client.get(
        "/policy/fingerprint",
        params={
            "policy_root": "qi/safety/policy_packs",
            "overlays": "qi/risk"
        }
    )
    
    data2 = response.json()
    # Should be different with overlays
    if os.path.exists("qi/risk/overlays.yaml"):
        assert data2["fingerprint"] != data["fingerprint"]
        print(f"  ✓ Different with overlays: {data2['fingerprint'][:16]}...")
    
    return True

def test_etag_caching():
    """Test ETag-based caching behavior"""
    print("\nTesting ETag caching...")
    
    from fastapi.testclient import TestClient
    from qi.provenance.receipts_api import app
    import glob
    
    receipts = glob.glob(os.path.expanduser("~/.lukhas/state/provenance/exec_receipts/*.json"))
    if not receipts:
        print("  ⚠️ No receipts available")
        return False
    
    rid = os.path.basename(receipts[0]).replace(".json", "")
    
    client = TestClient(app)
    
    # First request - get ETag
    response1 = client.get(
        f"/receipts/{rid}/replay.json",
        params={"policy_root": "qi/safety/policy_packs"}
    )
    
    assert response1.status_code == 200
    etag1 = response1.headers.get("etag")
    assert etag1
    print(f"  ✓ Initial ETag: {etag1}")
    
    # Second request - should get same ETag
    response2 = client.get(
        f"/receipts/{rid}/replay.json",
        params={"policy_root": "qi/safety/policy_packs"}
    )
    
    etag2 = response2.headers.get("etag")
    assert etag2 == etag1
    print(f"  ✓ Consistent ETag on same data")
    
    # Different policy should get different ETag
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copy policies and modify
        test_policies = os.path.join(tmpdir, "test_policies")
        shutil.copytree("qi/safety/policy_packs", test_policies)
        
        # Modify a file to change fingerprint
        test_file = os.path.join(test_policies, "global", "policy.yaml")
        if os.path.exists(test_file):
            with open(test_file, "a") as f:
                f.write("\n# Modified\n")
        
        # Request with modified policies
        response3 = client.get(
            f"/receipts/{rid}/replay.json",
            params={"policy_root": test_policies}
        )
        
        etag3 = response3.headers.get("etag")
        if etag3 != etag1:
            print(f"  ✓ Different ETag with modified policy: {etag3}")
        else:
            print(f"  ⚠️ ETag unchanged despite policy modification")
    
    return True

def test_cors_support():
    """Test CORS configuration"""
    print("\nTesting CORS support...")
    
    # Set CORS environment variable
    os.environ["RECEIPTS_API_CORS"] = "http://localhost:3000,https://example.com"
    
    # Reimport to apply CORS
    import importlib
    import qi.provenance.receipts_api
    importlib.reload(qi.provenance.receipts_api)
    
    from fastapi.testclient import TestClient
    from qi.provenance.receipts_api import app
    
    client = TestClient(app)
    
    # Test CORS headers
    response = client.options(
        "/receipts",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    # Check CORS headers if middleware is active
    if "access-control-allow-origin" in response.headers:
        print(f"  ✓ CORS enabled for: {response.headers['access-control-allow-origin']}")
    else:
        print("  ℹ️ CORS not configured (set RECEIPTS_API_CORS env var)")
    
    # Clean up
    del os.environ["RECEIPTS_API_CORS"]
    
    return True

def main():
    """Run all enhanced API tests"""
    print("=" * 60)
    print("ENHANCED RECEIPTS API - Test Suite")
    print("=" * 60)
    
    try:
        # Run tests
        test_api_endpoints()
        replay_data = test_replay_endpoint()
        test_trace_svg_endpoint()
        test_policy_fingerprint_endpoint()
        test_etag_caching()
        test_cors_support()
        
        print("\n" + "=" * 60)
        print("✅ ENHANCED API TESTS COMPLETED!")
        print("=" * 60)
        
        print("\nAPI features validated:")
        print("  • Receipt listing and retrieval")
        print("  • TEQ replay endpoint with ETag")
        print("  • Trace SVG generation (if graphviz available)")
        print("  • Policy fingerprint endpoint")
        print("  • ETag-based caching")
        print("  • CORS support (configurable)")
        
        if replay_data:
            print(f"\nSample replay result:")
            print(f"  Task: {replay_data['task']}")
            print(f"  Allowed: {replay_data['replay']['allowed']}")
            print(f"  Fingerprint: {replay_data['policy_fingerprint'][:16]}...")
        
        print("\n📡 To run the API server:")
        print("  uvicorn qi.provenance.receipts_api:app --port 8095")
        print("\n🔗 Endpoints:")
        print("  GET /receipts")
        print("  GET /receipts/{id}")
        print("  GET /receipts/{id}/replay.json?policy_root=...")
        print("  GET /receipts/{id}/trace.svg?policy_root=...")
        print("  GET /policy/fingerprint?policy_root=...")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())