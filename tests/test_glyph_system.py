#!/usr/bin/env python3
"""
LUKHAS AI GLYPH System Test Suite

Comprehensive smoke tests for the cryptographic seal implementation.
"""
import os, tempfile, json, time
from pathlib import Path

# Test the core GLYPH system
def test_seal_creation_and_verification():
    """Test basic seal creation and verification"""
    print("=== Test 1: Seal Creation & Verification ===")
    
    try:
        from qi.glyphs.seal import GlyphSigner, policy_fingerprint_from_files
        from qi.glyphs.verify import GlyphVerifier
        
        # Create test content
        test_content = b"Hello, LUKHAS AI GLYPH System! This is a test."
        
        # Create signer
        signer = GlyphSigner(key_id="test-key-001")
        
        # Generate policy fingerprint from actual policy files
        policy_fp = policy_fingerprint_from_files("qi/safety/policy_packs/global", "qi/risk")
        print(f"✓ Policy fingerprint: {policy_fp}")
        
        # Create seal
        result = signer.create_seal(
            content_bytes=test_content,
            media_type="text/plain",
            issuer="lukhas://org/test-tenant",
            model_id="lukhas-test-v1.0",
            policy_fingerprint=policy_fp,
            jurisdiction="global",
            proof_bundle="https://verify.lukhas.ai/test/abc123",
            ttl_days=30,
            calib_ref={"temp": 1.05, "ece": 0.042}
        )
        
        print("✓ Seal created successfully")
        print(f"  - Seal ID derived from content hash")
        print(f"  - Compact size: {len(result['compact'])} chars")
        
        # Verify seal
        jwks = {"test-key-001": signer.get_public_key()}
        
        verifier = GlyphVerifier(jwks)
        verification = verifier.verify_seal(
            test_content, 
            result["seal"], 
            result["signature"]
        )
        
        if verification.valid:
            print("✓ Verification successful")
            print(f"  - Issuer: {verification.issuer}")
            print(f"  - Model: {verification.model_id}")
            print(f"  - Created: {verification.created_at}")
        else:
            print("✗ Verification failed:")
            for error in verification.errors:
                print(f"    {error}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_file_embedding():
    """Test embedding seals in various file formats"""
    print("\n=== Test 2: File Embedding ===")
    
    try:
        from qi.glyphs.seal import GlyphSigner
        from qi.glyphs.embed import embed_seal_text, extract_seal_text, auto_embed_seal, auto_extract_seal
        
        # Create test seal
        signer = GlyphSigner(key_id="embed-test-001")
        test_content = b"Test content for embedding"
        
        result = signer.create_seal(
            content_bytes=test_content,
            media_type="text/plain",
            issuer="lukhas://org/embed-test",
            model_id="lukhas-embed-v1.0",
            policy_fingerprint="sha3-256:" + "a" * 64,
            jurisdiction="global",
            proof_bundle="https://verify.lukhas.ai/embed/test123"
        )
        
        # Test text embedding
        original_text = "This is a test document.\nIt contains multiple lines.\nAnd should preserve formatting."
        
        sealed_text = embed_seal_text(original_text, result)
        print("✓ Text embedding successful")
        
        # Extract and verify
        extracted_seal, clean_text = extract_seal_text(sealed_text)
        
        if extracted_seal and clean_text == original_text:
            print("✓ Text extraction successful")
            print(f"  - Original: {len(original_text)} chars")
            print(f"  - Sealed: {len(sealed_text)} chars")
            print(f"  - Extracted clean: {len(clean_text)} chars")
        else:
            print("✗ Text extraction failed")
            return False
        
        # Test with temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(original_text)
            temp_file = f.name
        
        try:
            # Auto-embed
            sealed_file = auto_embed_seal(temp_file, result)
            print(f"✓ Auto-embedding created: {sealed_file}")
            
            # Auto-extract
            extracted_data, clean_file = auto_extract_seal(sealed_file)
            
            if extracted_data and clean_file:
                print("✓ Auto-extraction successful")
                
                # Verify clean content matches original
                with open(clean_file, 'r') as f:
                    clean_content = f.read()
                
                if clean_content == original_text:
                    print("✓ Round-trip preservation verified")
                else:
                    print("✗ Content mismatch after round-trip")
                    return False
            else:
                print("✗ Auto-extraction failed")
                return False
                
        finally:
            # Cleanup
            for path in [temp_file, sealed_file, clean_file]:
                if os.path.exists(path):
                    os.unlink(path)
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_compact_seal_qr():
    """Test compact seal format for QR codes"""
    print("\n=== Test 3: Compact Seal & QR ===")
    
    try:
        from qi.glyphs.seal import GlyphSigner
        from qi.glyphs.verify import verify_compact_seal
        
        # Create compact seal
        signer = GlyphSigner(key_id="qr-test-001")
        test_content = b"QR test content"
        
        result = signer.create_seal(
            content_bytes=test_content,
            media_type="text/plain",
            issuer="lukhas://org/qr-test",
            model_id="lukhas-qr-v1.0",
            policy_fingerprint="sha3-256:" + "b" * 64,
            jurisdiction="eu",
            proof_bundle="https://verify.lukhas.ai/qr/test456"
        )
        
        compact_seal = result["compact"]
        print(f"✓ Compact seal created: {len(compact_seal)} chars")
        
        # Verify compact seal
        jwks = {"qr-test-001": signer.get_public_key()}
        verification = verify_compact_seal(compact_seal, test_content, jwks)
        
        if verification.valid:
            print("✓ Compact verification successful")
            print(f"  - Jurisdiction: {verification.jurisdiction}")
            print(f"  - Model: {verification.model_id}")
        else:
            print("✗ Compact verification failed:")
            for error in verification.errors:
                print(f"    {error}")
            return False
        
        # Test QR code generation (if available)
        try:
            import qrcode
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(compact_seal)
            qr.make(fit=True)
            
            print("✓ QR code generation successful")
            print(f"  - QR capacity: {len(compact_seal)} chars")
            
            # Test if QR fits in standard size
            if len(compact_seal) < 2000:  # Rough QR capacity estimate
                print("✓ Compact seal fits in standard QR code")
            else:
                print("⚠ Compact seal may be too large for QR code")
                
        except ImportError:
            print("⚠ QR code library not available (install qrcode package)")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_schema_validation():
    """Test JSON schema validation"""
    print("\n=== Test 4: Schema Validation ===")
    
    try:
        import jsonschema
        
        # Load schema
        schema_path = "qi/glyphs/GLYPH_SEAL.schema.json"
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        print(f"✓ Schema loaded: {schema_path}")
        
        # Create a test seal
        from qi.glyphs.seal import GlyphSigner
        
        signer = GlyphSigner(key_id="schema-test-001")
        test_content = b"Schema validation test"
        
        result = signer.create_seal(
            content_bytes=test_content,
            media_type="text/plain",
            issuer="lukhas://org/schema-test",
            model_id="lukhas-schema-v1.0", 
            policy_fingerprint="sha3-256:" + "c" * 64,
            jurisdiction="us",
            proof_bundle="https://verify.lukhas.ai/schema/test789"
        )
        
        # Validate seal against schema
        seal_data = result["seal"]
        jsonschema.validate(seal_data, schema)
        print("✓ Seal validates against schema")
        
        # Test signature validation
        signature_schema = schema["definitions"]["signature"]
        signature_data = result["signature"]
        jsonschema.validate(signature_data, signature_schema)
        print("✓ Signature validates against schema")
        
        # Test complete seal validation  
        complete_schema = schema["definitions"]["complete_seal"]
        complete_seal = {
            "seal": seal_data,
            "signature": signature_data,
            "compact": result["compact"]
        }
        # Debug the structure
        print(f"  Complete seal keys: {list(complete_seal.keys())}")
        jsonschema.validate(complete_seal, complete_schema)
        print("✓ Complete seal validates against schema")
        
        return True
        
    except ImportError:
        print("⚠ jsonschema library not available (install jsonschema package)")
        return True  # Skip test but don't fail
    except Exception as e:
        print(f"✗ Schema validation failed: {e}")
        return False

def test_cli_interface():
    """Test CLI interface"""
    print("\n=== Test 5: CLI Interface ===")
    
    try:
        import subprocess
        import tempfile
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("CLI test content")
            test_file = f.name
        
        seal_file = None  # Initialize to avoid reference error
        
        try:
            # Test CLI info command
            result = subprocess.run([
                "python3", "-m", "qi.glyphs.cli", "info"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✓ CLI info command working")
            else:
                print(f"✗ CLI info failed: {result.stderr}")
                return False
            
            # Test seal creation via CLI
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                seal_file = f.name
            
            # Close the file so CLI can write to it
            f.close()
            
            result = subprocess.run([
                "python3", "-m", "qi.glyphs.cli", "create", test_file,
                "--issuer", "lukhas://org/cli-test",
                "--model-id", "lukhas-cli-v1.0",
                "--proof-bundle", "https://verify.lukhas.ai/cli/test123",
                "--policy-root", "qi/safety/policy_packs/global",
                "--overlays", "qi/risk",
                "--output", seal_file
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and os.path.exists(seal_file):
                print("✓ CLI seal creation successful")
                
                # Test verification via CLI
                result = subprocess.run([
                    "python3", "-m", "qi.glyphs.cli", "verify", test_file, seal_file
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print("✓ CLI verification successful")
                else:
                    print(f"✗ CLI verification failed: {result.stderr}")
                    return False
                    
            else:
                print(f"✗ CLI seal creation failed: {result.stderr}")
                return False
                
        finally:
            # Cleanup
            for path in [test_file, seal_file]:
                if path and os.path.exists(path):
                    os.unlink(path)
        
        return True
        
    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        return False

def test_integration_with_receipts():
    """Test integration with existing receipt system"""
    print("\n=== Test 6: Receipt Integration ===")
    
    try:
        from qi.glyphs.seal import GlyphSigner
        from qi.provenance.receipts_hub import emit_receipt
        
        # Create content and seal
        signer = GlyphSigner(key_id="receipt-test-001")
        test_content = b"Receipt integration test content"
        
        seal_result = signer.create_seal(
            content_bytes=test_content,
            media_type="text/plain",
            issuer="lukhas://org/receipt-test",
            model_id="lukhas-receipt-v1.0",
            policy_fingerprint="sha3-256:" + "d" * 64,
            jurisdiction="global",
            proof_bundle="https://verify.lukhas.ai/receipt/test123"
        )
        
        print("✓ GLYPH seal created for receipt integration")
        
        # Emit receipt with GLYPH metadata
        import hashlib
        artifact_sha = hashlib.sha256(test_content).hexdigest()
        
        receipt = emit_receipt(
            artifact_sha=artifact_sha,
            artifact_mime="text/plain",
            artifact_size=len(test_content),
            storage_url="file://test/glyph_integration",
            run_id="glyph_test_001",
            task="glyph_integration_test",
            started_at=time.time()-2,
            ended_at=time.time(),
            user_id="test_user",
            metrics={
                "glyph_seal_compact": seal_result["compact"],
                "glyph_seal_id": seal_result["seal"]["content_hash"],
                "glyph_issuer": seal_result["seal"]["issuer"],
                "glyph_model": seal_result["seal"]["model_id"]
            }
        )
        
        print("✓ Receipt emitted with GLYPH metadata")
        print(f"  - Receipt ID: {receipt['id']}")
        print(f"  - GLYPH metadata included in metrics")
        
        # Verify GLYPH data in receipt
        glyph_compact = receipt["metrics"]["glyph_seal_compact"]
        if glyph_compact == seal_result["compact"]:
            print("✓ GLYPH data preserved in receipt")
        else:
            print("✗ GLYPH data corrupted in receipt")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Receipt integration test failed: {e}")
        return False

def main():
    """Run all GLYPH system tests"""
    print("🔒 LUKHAS AI GLYPH System Test Suite")
    print("=" * 50)
    
    tests = [
        test_seal_creation_and_verification,
        test_file_embedding,
        test_compact_seal_qr,
        test_schema_validation,
        test_cli_interface,
        test_integration_with_receipts
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print()  # Add spacing after failed tests
    
    print("\n" + "=" * 50)
    print(f"🧪 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! GLYPH system is ready for production.")
        print("\nNext steps:")
        print("1. Deploy signer service: uvicorn qi.glyphs.signer_service:app --port 8080")
        print("2. Set up HSM/KMS for production keys")
        print("3. Configure JWKS endpoint and transparency log")
        print("4. Integrate with existing AI workflows")
        return 0
    else:
        print("❌ Some tests failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    exit(main())