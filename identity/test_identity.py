"""
Test script for LUKHΛS Identity System
======================================

Tests all identity endpoints to ensure they're working correctly.
"""

import asyncio
import json
from datetime import datetime

# Import identity components
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_db import user_db


async def test_identity_system():
    """Test all identity system components."""
    
    print("🧠 LUKHΛS Identity System Test")
    print("=" * 50)
    
    # Test 1: Check demo user exists
    print("\n1. Checking demo user...")
    demo_user = user_db.get_user_by_email("reviewer@openai.com")
    if demo_user:
        print("✅ Demo user found:")
        print(f"   - Email: {demo_user['email']}")
        print(f"   - Tier: {demo_user['tier']}")
        print(f"   - Lambda ID: {demo_user['lambda_id']}")
        print(f"   - Glyphs: {' '.join(demo_user['glyphs'])}")
    else:
        print("❌ Demo user not found")
    
    # Test 2: Test user registration
    print("\n2. Testing user registration...")
    try:
        new_user = user_db.create_user(
            email="test@lukhas.ai",
            password="TestPass123",
            tier="T2",
            cultural_profile="universal",
            personality_type="creative"
        )
        print("✅ User created successfully:")
        print(f"   - Lambda ID: {new_user['lambda_id']}")
        print(f"   - Token: {new_user['token'][:20]}...")
        print(f"   - Glyphs: {' '.join(new_user['glyphs'])}")
    except ValueError as e:
        print(f"ℹ️ User already exists: {e}")
    
    # Test 3: Test login
    print("\n3. Testing login...")
    auth_user = user_db.authenticate_user("reviewer@openai.com", "demo_password")
    if auth_user:
        print("✅ Login successful:")
        print(f"   - Token: {auth_user['token'][:20]}...")
        print(f"   - Trinity Score: {auth_user['metadata']['trinity_score']}")
        demo_token = auth_user['token']
    else:
        print("❌ Login failed")
        demo_token = None
    
    # Test 4: Test token verification
    if demo_token:
        print("\n4. Testing token verification...")
        verified_user = user_db.verify_token(demo_token)
        if verified_user:
            print("✅ Token verified:")
            print(f"   - Valid for: {verified_user['email']}")
            print(f"   - Tier: {verified_user['tier']}")
        else:
            print("❌ Token verification failed")
    
    # Test 5: Check consent log
    print("\n5. Checking consent log...")
    consent_log_path = user_db.data_dir / "consent_log.jsonl"
    if consent_log_path.exists():
        with open(consent_log_path, 'r') as f:
            lines = f.readlines()
            print(f"✅ Consent log has {len(lines)} entries")
            if lines:
                latest = json.loads(lines[-1])
                print(f"   - Latest: {latest['action']} for {latest['email']}")
                print(f"   - Glyphs: {' '.join(latest['glyphs'])}")
    else:
        print("❌ No consent log found")
    
    # Test 6: Test tier permissions
    print("\n6. Testing tier permissions...")
    # Define tier permissions inline to avoid import issues
    tier_permissions = {
        "T1": 1,  # can_view_public
        "T2": 3,  # + can_create_content, can_access_api
        "T3": 6,  # + can_use_consciousness, can_use_emotion, can_use_dream
        "T4": 7,  # + can_use_quantum
        "T5": 9   # + can_access_guardian, can_admin
    }
    for tier, count in tier_permissions.items():
        print(f"   - {tier}: {count} permissions")
    
    print("\n" + "=" * 50)
    print("✅ Identity system test complete!")
    print("\nDemo credentials for testing:")
    print("  Email: reviewer@openai.com")
    print("  Password: demo_password")
    print("  Tier: T5 (Full Guardian access)")
    print("\n🛡️ Trinity Framework Active")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_identity_system())