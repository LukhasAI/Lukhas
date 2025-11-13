#!/usr/bin/env python3
"""
Summarize Jules Sessions Awaiting Feedback
==========================================

Provides a quick summary of what each session is waiting for.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def summarize_sessions():
    """Summarize all sessions awaiting feedback."""
    print("📊 Jules Sessions Awaiting Feedback - Summary")
    print("=" * 70)

    async with JulesClient() as jules:
        # Get all sessions
        sessions_response = await jules.list_sessions(page_size=20)
        sessions = sessions_response.get("sessions", [])

        # Filter sessions awaiting feedback
        awaiting_feedback = [
            s for s in sessions
            if s.get("state") == "AWAITING_USER_FEEDBACK"
        ]

        if not awaiting_feedback:
            print("\n✅ No sessions awaiting feedback!")
            return

        print(f"\n⚠️  Found {len(awaiting_feedback)} session(s) awaiting feedback:\n")

        for i, session in enumerate(awaiting_feedback, 1):
            session_id = session.get("name")
            title = session.get("title", "Unnamed")
            created = session.get("createTime", "Unknown")

            # Truncate title to first line
            title_first_line = title.split('\n')[0][:80]

            print(f"{i}. {title_first_line}")
            print(f"   ID: {session_id}")
            print(f"   Created: {created[:19]}")
            print(f"   URL: https://jules.google.com/session/{session_id.split('/')[-1]}")
            print()


def main():
    """Main entry point."""
    asyncio.run(summarize_sessions())


if __name__ == "__main__":
    main()
