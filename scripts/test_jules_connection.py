#!/usr/bin/env python3
"""
Test Jules API Connection
=========================

Verifies Jules API key is configured and working.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def test_jules_connection():
    """Test Jules API connection and list repositories."""
    print("🔍 Testing Jules API Connection...")
    print("=" * 70)

    try:
        async with JulesClient() as jules:
            print("✅ Jules API client initialized")
            print("   (API key retrieved from macOS Keychain)")
            print()

            # List connected sources
            print("📋 Fetching connected repositories...")
            sources = await jules.list_sources()

            if not sources:
                print("⚠️  No repositories connected to Jules yet")
                print()
                print("To connect repositories:")
                print("  1. Visit https://jules.ai")
                print("  2. Go to Sources section")
                print("  3. Connect your GitHub repositories")
                print()
                return False

            print(f"✅ Found {len(sources)} connected repository/repositories:")
            print()

            for i, source in enumerate(sources, 1):
                print(f"  {i}. {source.display_name or source.name}")
                if source.repository_url:
                    print(f"     URL: {source.repository_url}")
                print(f"     ID: {source.name}")
                if source.create_time:
                    print(f"     Created: {source.create_time.strftime('%Y-%m-%d %H:%M')}")
                print()

            # List recent sessions
            print("📊 Fetching recent Jules sessions...")
            sessions_response = await jules.list_sessions(page_size=5)
            sessions = sessions_response.get("sessions", [])

            if sessions:
                print(f"✅ Found {len(sessions)} recent session(s):")
                print()
                for session in sessions:
                    print(f"  - {session.get('displayName', 'Unnamed')}")
                    print(f"    State: {session.get('state', 'Unknown')}")
                    print(f"    Created: {session.get('createTime', 'Unknown')}")
                    print()
            else:
                print("ℹ️  No previous sessions (this is normal for first use)")
                print()

            print("=" * 70)
            print("✅ Jules API is working correctly!")
            print()
            print("Ready to delegate coding tasks to Jules. Try:")
            print("  python3 scripts/delegate_to_jules.py")
            print()

            return True

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print()
        print("💡 Run this to configure your API key:")
        print("   python3 scripts/setup_api_keys.py")
        return False

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print()
        print("Possible issues:")
        print("  - API key may be invalid")
        print("  - Network connection problem")
        print("  - Jules API service unavailable")
        return False


def main():
    """Main entry point."""
    success = asyncio.run(test_jules_connection())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
