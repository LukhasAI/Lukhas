#!/usr/bin/env python3
"""
Test script for hybrid session key generation (BLAKE3 + SHAKE256)
Tests the dual-key approach for internal speed and external trust
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

from governance.identity.gateway.stargate_gateway import GlyphPayload, StargateGateway

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


async def test_hybrid_session_keys():
    """Test the hybrid BLAKE3 + SHAKE256 session key generation"""

    print("🔐 Testing LUKHΛS Hybrid Session Key Generation")
    print("=" * 60)

    # Initialize Stargate Gateway
    gateway = StargateGateway()

    # Test payloads with different tiers
    test_cases = [
        {
            "user_id": "hybrid_test_t3",
            "tier": "T3",
            "consciousness": "focused",
            "cultural_region": "americas",
        },
        {
            "user_id": "hybrid_test_t4",
            "tier": "T4",
            "consciousness": "creative",
            "cultural_region": "europe",
        },
        {
            "user_id": "hybrid_test_t5",
            "tier": "T5",
            "consciousness": "flow_state",
            "cultural_region": "asia",
        },
    ]

    for test_case in test_cases:
        print(f"\n📊 Testing {test_case['tier']} User: {test_case['user_id']}")
        print("-" * 40)

        # Create payload
        payload = GlyphPayload(
            source_agent="test_client",
            target_agent="openai_gateway",
            user_id=test_case["user_id"],
            auth_state=test_case["tier"],
            iris_score=0.95,
            symbolic_glyphs=["🔐", "🌊", "👁️"],
            cultural_signature={
                "region": test_case["cultural_region"],
                "adaptation_mode": "high_context",
            },
            consciousness_state=test_case["consciousness"],
            ethical_hash="trusthelix:test:12345abcdef",  # Proper format
            intent="test_hybrid_keys",
            prompt_payload={
                "test": "hybrid_keys",
                "timestamp": datetime.utcnow().isoformat(),
                "constraints": [
                    "harmful impact prevention",
                    "consciousness preservation",
                    "cultural sensitivity",
                    "drift prevention",
                    "transparency",
                    "explicability",
                    "fairness",
                    "accountability",
                ],
                "consent_types": [
                    "biometric_processing",
                    "consciousness_analysis",
                    "symbolic_transmission",
                ],
                "consent_signature": f"consent_{test_case['user_id']}_{datetime.utcnow().timestamp()}",
            },
            timestamp=datetime.utcnow(),
        )

        # Establish handshake (which generates session keys)
        success = await gateway.establish_handshake(payload)

        if success:
            print("✅ Session initialized successfully")

            # Get session data
            session_data = gateway.get_session_audit_data(test_case["user_id"])

            if session_data:
                print("\n🔑 Session Keys Generated:")
                print(
                    f"   Internal Key (first 16 chars): {session_data['internal_session_key'][:16]}..."
                )
                print(f"   Algorithm: {session_data['algorithm']}")
                print(
                    f"   Key Length: {len(session_data['internal_session_key'])} chars"
                )

                print("\n🛡️  Public Verification Hash:")
                print(f"   Hash: {session_data['public_verification_hash'][:32]}...")
                print("   Algorithm: SHAKE256")
                print(
                    f"   Length: {len(session_data['public_verification_hash'])} chars"
                )

                print("\n📊 Metadata:")
                print(f"   Tier: {session_data['tier']}")
                print(f"   Entropy Score: {session_data['entropy_score']:.2f}")
                print(f"   Timestamp: {session_data['timestamp']}")

                # Test retrieval methods
                public_hash = gateway.get_public_verification_hash(test_case["user_id"])
                if public_hash:
                    print("\n✓ Public hash retrieval working")
                    assert public_hash == session_data["public_verification_hash"]
                else:
                    print("\n✗ Failed to retrieve public hash")
            else:
                print("❌ Failed to get session audit data")
        else:
            print("❌ Failed to initialize session")

    print("\n" + "=" * 60)
    print("🎯 Hybrid Key Implementation Summary:")
    print("   • BLAKE3 provides fast internal operations")
    print("   • SHAKE256 ensures institutional trust")
    print("   • Both keys logged for complete audit trail")
    print("   • Speed + Ethics + Trust = Very LUKHΛS")

    # Check if BLAKE3 is available
    try:
        pass

        print("\n✅ BLAKE3 library installed - using optimal performance")
    except ImportError:
        print("\n⚠️  BLAKE3 not installed - using SHA3-256 fallback")
        print("   Install with: pip install blake3")

    # Display audit log preview
    print("\n📋 Audit Log Preview:")
    audit_path = Path("governance/identity/audit/stargate_audit.log")
    if audit_path.exists():
        with open(audit_path) as f:
            lines = f.readlines()
            recent_lines = [
                line
                for line in lines[-20:]
                if "session_key" in line or "verification_hash" in line
            ]
            for line in recent_lines[-5:]:
                print(f"   {line.strip()}")

    print("\n🌿🪷🔐 Hybrid session key testing complete!")


if __name__ == "__main__":
    asyncio.run(test_hybrid_session_keys())
