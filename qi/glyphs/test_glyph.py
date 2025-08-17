#!/usr/bin/env python3
# path: qi/glyphs/test_glyph.py
"""
Test script for GLYPH seal system.
"""
import os, sys, json, tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_seal_creation():
    """Test creating a GLYPH seal."""
    print("\n=== Testing Seal Creation ===")
    
    from qi.glyphs.seal import make_seal
    
    # Test content
    content = b"This is test content for LUKHAS GLYPH seal."
    policy = b'{"version": "1.0", "rules": ["test"]}'
    
    # Create seal
    result = make_seal(
        content_bytes=content,
        media_type="text/plain",
        issuer="lukhas://org/test",
        model_id="lukhas-test-v1",
        policy_bytes=policy,
        jurisdiction="global",
        proof_bundle="https://example.com/proof/123",
        ttl_days=30,
        calib_ref={"temp": 1.2, "ece": 0.05}
    )
    
    seal = result["seal"]
    sig = result["sig"]
    
    print(f"✓ Created seal v{seal['v']}")
    print(f"  Content hash: {seal['content_hash'][:50]}...")
    print(f"  Issuer: {seal['issuer']}")
    print(f"  Model: {seal['model_id']}")
    print(f"  Nonce: {seal['nonce']}")
    # Decode protected header
    import base64
    protected_b64 = sig['protected']
    protected_json = base64.urlsafe_b64decode(protected_b64 + '=' * (4 - len(protected_b64) % 4))
    protected = json.loads(protected_json)
    print(f"  Signature alg: {protected['alg']}")
    
    return result

def test_text_embedding(seal_result):
    """Test embedding seal in text."""
    print("\n=== Testing Text Embedding ===")
    
    from qi.glyphs.embed import embed_in_text, extract_from_text
    
    # Original text
    text = b"This is a test document.\nIt contains important information."
    
    # Embed seal
    sealed_text = embed_in_text(text, seal_result["seal"], seal_result["sig"])
    
    print(f"✓ Embedded seal in text ({len(sealed_text)} bytes)")
    
    # Extract seal
    extracted = extract_from_text(sealed_text)
    
    if extracted:
        print("✓ Successfully extracted seal from text")
        assert extracted["seal"]["v"] == seal_result["seal"]["v"]
        assert extracted["seal"]["nonce"] == seal_result["seal"]["nonce"]
    else:
        print("✗ Failed to extract seal")
        return False
    
    return True

def test_png_embedding(seal_result):
    """Test embedding seal in PNG."""
    print("\n=== Testing PNG Embedding ===")
    
    from qi.glyphs.embed import embed_in_png, extract_from_png
    
    # Create a minimal valid PNG (1x1 red pixel)
    png_data = bytes.fromhex(
        '89504e470d0a1a0a'  # PNG signature
        '0000000d49484452'  # IHDR chunk start
        '00000001000000010802000000907753de'  # 1x1, RGB
        '0000000c494441540889620000000200013912b434'  # IDAT chunk
        '0000000049454e44ae426082'  # IEND chunk
    )
    
    # Embed seal
    sealed_png = embed_in_png(png_data, seal_result["seal"], seal_result["sig"])
    
    print(f"✓ Embedded seal in PNG ({len(sealed_png)} bytes)")
    
    # Extract seal
    extracted = extract_from_png(sealed_png)
    
    if extracted:
        print("✓ Successfully extracted seal from PNG")
        assert extracted["seal"]["v"] == seal_result["seal"]["v"]
        assert extracted["seal"]["nonce"] == seal_result["seal"]["nonce"]
    else:
        print("✗ Failed to extract seal")
        return False
    
    # Save for manual verification
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(sealed_png)
        print(f"  Saved test PNG to: {f.name}")
    
    return True

def test_qr_encoding(seal_result):
    """Test QR code data encoding."""
    print("\n=== Testing QR Encoding ===")
    
    from qi.glyphs.embed import embed_qr_data, parse_qr_data
    
    # Create QR data
    qr_data = embed_qr_data(seal_result["seal"], seal_result["sig"])
    
    print(f"✓ Created QR data: {qr_data[:50]}...")
    print(f"  Length: {len(qr_data)} chars")
    
    # Parse back
    parsed = parse_qr_data(qr_data)
    
    if parsed:
        print("✓ Successfully parsed QR data")
        print(f"  Issuer: {parsed['issuer']}")
        print(f"  Model: {parsed['model_id']}")
    else:
        print("✗ Failed to parse QR data")
        return False
    
    return True

def test_verification(seal_result):
    """Test seal verification."""
    print("\n=== Testing Verification ===")
    
    from qi.glyphs.seal import verify_seal, canonicalize
    
    seal = seal_result["seal"]
    sig = seal_result["sig"]
    
    # Canonicalize for verification
    seal_bytes = canonicalize(seal)
    
    # Verify
    is_valid = verify_seal(seal_bytes, sig)
    
    if is_valid:
        print("✓ Seal signature verified")
    else:
        print("✗ Seal signature verification failed")
    
    return is_valid

def main():
    """Run all tests."""
    print("=" * 60)
    print("LUKHAS GLYPH SEAL TEST SUITE")
    print("=" * 60)
    
    tests = []
    
    # Create a seal
    seal_result = test_seal_creation()
    tests.append(("Seal Creation", seal_result is not None))
    
    if seal_result:
        # Test embedding
        tests.append(("Text Embedding", test_text_embedding(seal_result)))
        tests.append(("PNG Embedding", test_png_embedding(seal_result)))
        tests.append(("QR Encoding", test_qr_encoding(seal_result)))
        tests.append(("Verification", test_verification(seal_result)))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    for name, passed in tests:
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {'PASSED' if passed else 'FAILED'}")
    
    passed_count = sum(1 for _, p in tests if p)
    total_count = len(tests)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)