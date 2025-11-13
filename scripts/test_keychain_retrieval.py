#!/usr/bin/env python3
"""
Test keychain API key retrieval

Quick test to verify that API keys can be retrieved from macOS Keychain.

Usage:
    python3 scripts/test_keychain_retrieval.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.env_loader import get_api_key, get_from_keychain


def test_keychain_retrieval():
    """Test retrieving API key from keychain"""
    print("🔐 Testing Keychain API Key Retrieval\n")
    print("=" * 60)

    # Test direct keychain retrieval
    print("\n1. Direct Keychain Retrieval")
    print("-" * 60)

    service_name = "LUKHASAI.ANTHROPIC_API_KEY"
    print(f"Service: {service_name}")

    key = get_from_keychain(service_name)

    if key:
        print(f"✅ Found key: {key[:20]}...")
        print(f"   Length: {len(key)} characters")
        print(f"   Format: {'Valid' if key.startswith('sk-ant-') else 'Invalid'}")
    else:
        print("❌ No key found in keychain")
        return False

    # Test get_api_key with fallback
    print("\n2. get_api_key() with Keychain Fallback")
    print("-" * 60)

    api_key = get_api_key("anthropic")

    if api_key:
        print(f"✅ Retrieved key: {api_key[:20]}...")
        print(f"   Source: {'Keychain' if api_key == key else 'Environment'}")
    else:
        print("❌ get_api_key() returned None")
        return False

    # Verify format
    print("\n3. Key Validation")
    print("-" * 60)

    if api_key.startswith('sk-ant-'):
        print("✅ Key format is valid (starts with 'sk-ant-')")
    else:
        print(f"❌ Invalid key format: {api_key[:10]}...")
        return False

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

    print("\nNext steps:")
    print("  - The API key is automatically retrieved from keychain")
    print("  - No .env configuration needed")
    print("  - To test with actual API call, install anthropic:")
    print("    pip install anthropic")

    return True


if __name__ == "__main__":
    try:
        success = test_keychain_retrieval()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
