#!/usr/bin/env python3
"""Find and display all Jules sessions waiting for user feedback."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def check_waiting_sessions():
    """Check for sessions in WAITING_FOR_USER state."""

    async with JulesClient() as jules:
        print("Fetching all Jules sessions...\n")

        # Get all sessions
        sessions_response = await jules.list_sessions(page_size=100)

        all_sessions = sessions_response.get("sessions", [])
        print(f"Total sessions: {len(all_sessions)}\n")

        # Filter for waiting sessions
        waiting_sessions = [
            s for s in all_sessions
            if s.get("state") == "WAITING_FOR_USER"
        ]

        if not waiting_sessions:
            print("✅ No sessions waiting for user feedback!")
            return

        print(f"⏳ Found {len(waiting_sessions)} sessions WAITING FOR USER:\n")
        print("="*70)

        for idx, session in enumerate(waiting_sessions, 1):
            session_id = session.get("id", "unknown")
            prompt = session.get("prompt", "")[:80] + "..." if len(session.get("prompt", "")) > 80 else session.get("prompt", "")
            created = session.get("createdAt", "unknown")
            url = f"https://jules.google.com/session/{session_id}"

            print(f"\n[{idx}/{len(waiting_sessions)}] Session {session_id}")
            print(f"Created: {created}")
            print(f"Prompt: {prompt}")
            print(f"URL: {url}")

            # Try to get more details
            try:
                details = await jules.get_session(f"sessions/{session_id}")

                # Check if there's a plan waiting for approval
                if "plan" in str(details).lower():
                    print(f"⏳ Status: Plan waiting for approval")
                    print(f"   Action: Approve with: jules.approve_plan('sessions/{session_id}')")
                else:
                    print(f"⏳ Status: Waiting for user message")
                    print(f"   Action: Send message with: jules.send_message('sessions/{session_id}', 'your message')")

            except Exception as e:
                print(f"   (Could not fetch details: {e})")

        print("\n" + "="*70)
        print(f"\nTotal waiting: {len(waiting_sessions)} sessions")


if __name__ == "__main__":
    asyncio.run(check_waiting_sessions())
