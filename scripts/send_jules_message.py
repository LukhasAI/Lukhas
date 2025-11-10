#!/usr/bin/env python3
"""Send a message to a specific Jules session."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def send_message(session_id: str, message: str):
    """
    Send a message/feedback to a Jules session.

    Args:
        session_id: Jules session ID
        message: Message to send to Jules
    """
    async with JulesClient() as jules:
        print(f"Sending message to session {session_id}...")
        print(f"Message: {message}\n")

        try:
            result = await jules.send_message(f"sessions/{session_id}", message)
            print(f"✅ Message sent successfully!")
            print(f"Result: {result}")
            print(f"\nURL: https://jules.google.com/session/{session_id}")
        except Exception as e:
            print(f"❌ Error sending message: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/send_jules_message.py <session_id> <message>")
        print("\nExample:")
        print('  python3 scripts/send_jules_message.py 12640991174544438084 "Use lukhas.* imports"')
        sys.exit(1)

    session_id = sys.argv[1]
    message = sys.argv[2]

    asyncio.run(send_message(session_id, message))
