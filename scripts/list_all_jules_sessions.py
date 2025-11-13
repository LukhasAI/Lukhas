#!/usr/bin/env python3
"""
List All Jules Sessions with States
===================================
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def list_all_sessions():
    """List all sessions with their states."""
    print("📋 All Jules Sessions")
    print("=" * 70)

    async with JulesClient() as jules:
        sessions_response = await jules.list_sessions(page_size=50)
        sessions = sessions_response.get("sessions", [])

        print(f"\nTotal: {len(sessions)} sessions\n")

        # Group by state
        by_state = {}
        for session in sessions:
            state = session.get("state", "UNKNOWN")
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(session)

        # Print by state
        for state in ["COMPLETED", "AWAITING_USER_FEEDBACK", "ACTIVE", "FAILED", "CANCELLED"]:
            if state in by_state:
                print(f"\n{'=' * 70}")
                print(f"{state}: {len(by_state[state])} sessions")
                print(f"{'=' * 70}\n")

                for session in by_state[state]:
                    title = session.get("title", "Unnamed")
                    session_id = session.get("name", "").split("/")[-1]
                    created = session.get("createTime", "")[:19]

                    # Truncate title
                    title_short = title.split('\n')[0][:80]

                    print(f"  {title_short}")
                    print(f"  ID: {session_id}")
                    print(f"  Created: {created}")
                    print(f"  URL: https://jules.google.com/session/{session_id}")
                    print()


def main():
    asyncio.run(list_all_sessions())


if __name__ == "__main__":
    main()
