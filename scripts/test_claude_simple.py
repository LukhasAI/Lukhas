#!/usr/bin/env python3
"""
Simple Claude API test without branding dependencies

Tests actual API call using keychain-retrieved key.

Usage:
    python3 scripts/test_claude_simple.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.env_loader import get_api_key


async def test_claude_api():
    """Test Claude API with keychain key"""
    print("🤖 Testing Claude API with Keychain Key\n")
    print("=" * 60)

    # Get API key (will use keychain)
    print("\n1. Retrieving API Key from Keychain")
    print("-" * 60)

    api_key = get_api_key("anthropic")

    if not api_key:
        print("❌ No API key found")
        print("\nTroubleshooting:")
        print("  - Check keychain for: LUKHASAI.ANTHROPIC_API_KEY")
        print("  - Or add to .env: ANTHROPIC_API_KEY=sk-ant-...")
        return False

    print(f"✅ API key retrieved: {api_key[:20]}...")
    print("   Source: macOS Keychain")

    # Check if anthropic package is installed
    print("\n2. Checking Anthropic Package")
    print("-" * 60)

    try:
        import anthropic
        print(f"✅ Anthropic package installed (v{anthropic.__version__})")
    except ImportError:
        print("❌ Anthropic package not installed")
        print("\nInstall with:")
        print("  pip install anthropic")
        return False

    # Test API call
    print("\n3. Testing API Call")
    print("-" * 60)

    try:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        print("Sending test query to Claude...")

        response = await client.messages.create(
            model="claude-3-5-haiku-20241022",  # Fastest, cheapest
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'Hello from LUKHAS!' in exactly 5 words."}
            ]
        )

        if response.content:
            text = response.content[0].text
            print("✅ API call successful!")
            print(f"   Model: {response.model}")
            print(f"   Response: {text}")
            print(f"   Input tokens: {response.usage.input_tokens}")
            print(f"   Output tokens: {response.usage.output_tokens}")

            return True
        else:
            print("❌ Empty response from API")
            return False

    except anthropic.APIError as e:
        print(f"❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    print("\n🔐 LUKHAS Claude API Test (Keychain Integration)")
    print("=" * 60)

    success = await test_claude_api()

    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nYour Claude API integration is working!")
        print("\nAPI key is automatically retrieved from macOS Keychain:")
        print("  Service: LUKHASAI.ANTHROPIC_API_KEY")
        print("\nNo .env configuration needed!")
    else:
        print("❌ TESTS FAILED")
        print("=" * 60)

    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
