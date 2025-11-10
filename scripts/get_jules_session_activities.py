#!/usr/bin/env python3
"""Get activities (conversation/messages) from Jules sessions."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def get_session_activities(session_ids: list[str]):
    """
    Get activities for specific sessions to see Jules' messages.

    Args:
        session_ids: List of session IDs to check
    """
    async with JulesClient() as jules:
        for idx, session_id in enumerate(session_ids, 1):
            print(f"\n{'='*70}")
            print(f"[{idx}/{len(session_ids)}] Session: {session_id}")
            print(f"URL: https://jules.google.com/session/{session_id}")
            print('='*70)

            try:
                # Get session details
                session = await jules.get_session(f"sessions/{session_id}")
                state = session.get("state", "UNKNOWN")
                title = session.get("title", "")[:100]

                print(f"State: {state}")
                print(f"Title: {title}")

                # Get activities (messages, plans, etc.)
                activities_response = await jules.list_activities(
                    f"sessions/{session_id}",
                    page_size=100
                )

                activities = activities_response.get("activities", [])
                print(f"\nActivities: {len(activities)} total\n")

                if not activities:
                    print("  No activities found")
                    continue

                # Show last 5 activities (most recent conversation)
                recent_activities = activities[-5:]

                for activity in recent_activities:
                    activity_type = activity.get("type", "UNKNOWN")
                    originator = activity.get("originator", "UNKNOWN")
                    created = activity.get("createTime", "")[:19]
                    message = activity.get("message", "")

                    # Highlight AGENT messages (Jules asking questions)
                    if originator == "AGENT":
                        print(f"  🤖 JULES [{activity_type}] ({created}):")
                        if message:
                            # Truncate long messages
                            if len(message) > 300:
                                print(f"     {message[:300]}...")
                            else:
                                print(f"     {message}")
                        else:
                            print(f"     (No message text)")
                    else:
                        print(f"  👤 USER [{activity_type}] ({created}):")
                        if message:
                            if len(message) > 200:
                                print(f"     {message[:200]}...")
                            else:
                                print(f"     {message}")

                    print()

                # Check if Jules is waiting for response
                if state in ["WAITING_FOR_USER", "AWAITING_PLAN_APPROVAL"]:
                    print(f"  ⚠️  SESSION NEEDS ACTION: {state}")

            except Exception as e:
                print(f"  ❌ Error: {e}")


async def check_all_non_completed_sessions():
    """Check all non-completed sessions for Jules messages."""
    async with JulesClient() as jules:
        print("Fetching all sessions...\n")

        sessions_response = await jules.list_sessions(page_size=100)
        all_sessions = sessions_response.get("sessions", [])

        # Filter non-completed sessions
        active_sessions = [
            s for s in all_sessions
            if s.get("state") != "COMPLETED"
        ]

        if not active_sessions:
            print("✅ All sessions are COMPLETED. Checking last 10 completed for recent activity...")
            # Check last 10 completed sessions for any recent messages
            completed_sessions = [s for s in all_sessions if s.get("state") == "COMPLETED"]
            session_ids = [s.get("id") for s in completed_sessions[-10:]]
        else:
            print(f"Found {len(active_sessions)} non-completed sessions\n")
            session_ids = [s.get("id") for s in active_sessions]

        await get_session_activities(session_ids)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check specific sessions
        session_ids = sys.argv[1:]
        asyncio.run(get_session_activities(session_ids))
    else:
        # Check all active sessions
        asyncio.run(check_all_non_completed_sessions())
