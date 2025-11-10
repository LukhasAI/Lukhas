#!/usr/bin/env python3
"""Check all active (non-completed) Jules sessions."""

import asyncio
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def check_active_sessions():
    """Check all active sessions grouped by state."""

    async with JulesClient() as jules:
        print("Fetching all Jules sessions (up to 100)...\n")

        # Get sessions
        sessions_response = await jules.list_sessions(page_size=100)
        all_sessions = sessions_response.get("sessions", [])

        print(f"Total sessions fetched: {len(all_sessions)}\n")

        # Group by state
        by_state = defaultdict(list)
        for session in all_sessions:
            state = session.get("state", "UNKNOWN")
            by_state[state].append(session)

        # Show summary
        print("="*70)
        print("SESSIONS BY STATE:")
        print("="*70)
        for state, sessions in sorted(by_state.items()):
            print(f"{state}: {len(sessions)} sessions")

        print("\n" + "="*70)

        # Show details for non-completed sessions
        active_states = [s for s in by_state.keys() if s != "COMPLETED"]

        if not active_states:
            print("\n✅ All sessions are COMPLETED!")
            return

        print("\n📋 ACTIVE (NON-COMPLETED) SESSIONS:")
        print("="*70)

        for state in sorted(active_states):
            sessions = by_state[state]
            print(f"\n{state} ({len(sessions)} sessions):")
            print("-"*70)

            for idx, session in enumerate(sessions[:10], 1):  # Show up to 10 per state
                session_id = session.get("id", "unknown")
                prompt = session.get("prompt", "")[:70] + "..." if len(session.get("prompt", "")) > 70 else session.get("prompt", "")
                created = session.get("createdAt", "unknown")[:19]  # Truncate timestamp
                url = f"https://jules.google.com/session/{session_id}"

                print(f"\n  [{idx}] {session_id}")
                print(f"      Created: {created}")
                print(f"      Prompt: {prompt}")
                print(f"      URL: {url}")

                # Suggest actions based on state
                if state == "WAITING_FOR_USER":
                    print(f"      ⏳ ACTION: Approve plan or send message")
                    print(f"      Code: jules.approve_plan('sessions/{session_id}')")
                elif state == "PLANNING":
                    print(f"      🔄 STATUS: Jules is creating implementation plan")
                elif state == "IN_PROGRESS":
                    print(f"      ⚙️ STATUS: Jules is implementing")
                elif state == "BLOCKED":
                    print(f"      🚫 ACTION: Check error and provide guidance")

            if len(sessions) > 10:
                print(f"\n  ... and {len(sessions) - 10} more {state} sessions")

        print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(check_active_sessions())
