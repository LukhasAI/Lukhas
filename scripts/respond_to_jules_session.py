#!/usr/bin/env python3
"""
Respond to Jules Session
========================

Send a message to a Jules session.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def send_message(session_id: str, message: str):
    """Send a message to a Jules session."""
    print(f"📤 Sending message to session: {session_id}")
    print("=" * 70)
    print(f"\nMessage:\n{message}\n")
    print("=" * 70)

    async with JulesClient() as jules:
        response = await jules.send_message(session_id, message)
        print("\n✅ Message sent successfully!")
        print(f"Activity ID: {response.get('name')}")


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/respond_to_jules_session.py <session_id> <message>")
        print("\nExample:")
        print('  python3 scripts/respond_to_jules_session.py sessions/123 "Please continue"')
        sys.exit(1)

    session_id = sys.argv[1]
    message = sys.argv[2]
    asyncio.run(send_message(session_id, message))


if __name__ == "__main__":
    main()
