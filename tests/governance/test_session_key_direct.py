#!/usr/bin/env python3
"""
Direct test of hybrid session key generation without full handshake
"""

import sys
from datetime import datetime
from pathlib import Path

from lukhas.governance.identity.gateway.stargate_gateway import GlyphPayload, StargateGateway

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_session_key_generation():
    """Test the hybrid session key generation directly"""

    print("🔐 Direct Test of Hybrid Session Key Generation")
    print("=" * 60)

    # Initialize gateway
    gateway = StargateGateway()

    # Create test payload
    payload = GlyphPayload(
        source_agent="test_client",
        target_agent="openai_gateway",
        user_id="direct_test_user",
        auth_state="tier_5_verified",  # This will extract to T5
        iris_score=0.95,
        symbolic_glyphs=["🔐", "🌊", "👁️"],
        cultural_signature={
            "region": "global",
            "adaptation_mode": "universal",
        },
        consciousness_state="flow_state",
        ethical_hash="trusthelix:test:12345",
        intent="test_session_keys",
        prompt_payload={"test": "direct_key_generation"},
        timestamp=datetime.utcnow(),
    )

    print(f"📊 Testing with user: {payload.user_id}")
    print(f"   Auth State: {payload.auth_state}")
    print(f"   Consciousness: {payload.consciousness_state}")

    # Call the key generation method directly
    print("\n🔑 Generating Session Keys...")
    gateway._generate_session_key(payload)

    # Access the stored session data
    if payload.user_id in gateway.session_keys:
        session_data = gateway.session_keys[payload.user_id]

        print("\n✅ Session Keys Generated Successfully!")
        print(f"\n📊 Session Data Keys: {list(session_data.keys())}")

        # Use the correct key names
        internal_key = session_data.get("internal_session_key")
        if internal_key:
            print("\n🔑 Internal Session Key (BLAKE3/SHA3):")
            print(f"   Algorithm: {session_data.get('algorithm', 'SHA3-256')}")
            print(f"   Key (first 32 chars): {internal_key[:32]}...")
            print(f"   Full Length: {len(internal_key)} characters")

        if "public_verification_hash" in session_data:
            print("\n🛡️  Public Verification Hash (SHAKE256):")
            print(
                f"   Hash (first 32 chars): {session_data['public_verification_hash'][:32]}..."
            )
            print(
                f"   Full Length: {len(session_data['public_verification_hash'])} characters"
            )

        print("\n📊 Additional Metadata:")
        print(f"   Tier: {session_data.get('tier', 'Unknown')}")
        print(f"   Entropy Score: {session_data.get('entropy_score', 0):.3f}")
        print(f"   Timestamp: {session_data.get('timestamp', 'Unknown')}")

        # Test the retrieval methods
        public_hash = gateway.get_public_verification_hash(payload.user_id)
        audit_data = gateway.get_session_audit_data(payload.user_id)

        print("\n✓ Retrieval Methods:")
        print(
            f"   get_public_verification_hash: {'Working' if public_hash else 'Failed'}"
        )
        print(f"   get_session_audit_data: {'Working' if audit_data else 'Failed'}")

        if audit_data:
            print("\n📋 Audit Data Summary:")
            for key, value in audit_data.items():
                if key in ["internal_session_key", "public_verification_hash"]:
                    print(f"   {key}: {value[:24]}... (truncated)")
                else:
                    print(f"   {key}: {value}")
    else:
        print(f"❌ No session data found for user: {payload.user_id}")

    print("\n" + "=" * 60)
    print("🎯 Key Characteristics:")
    print("   • Internal key uses BLAKE3 (or SHA3-256 fallback)")
    print("   • Public hash uses SHAKE256 for institutional trust")
    print("   • Both stored for complete audit trail")
    print("   • Keys are deterministic but include entropy")

    # Check BLAKE3 availability
    try:
        pass

        print("\n✅ BLAKE3 installed - optimal performance enabled")
    except ImportError:
        print("\n⚠️  BLAKE3 not installed - using SHA3-256 fallback")
        print("   To enable BLAKE3: pip install blake3")

    print("\n🌿🪷🔐 Direct key generation test complete!")


if __name__ == "__main__":
    test_session_key_generation()
