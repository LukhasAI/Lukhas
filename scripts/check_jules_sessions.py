#!/usr/bin/env python3
"""
Check Jules Sessions Awaiting Feedback
======================================

Lists all sessions and shows details for those awaiting user feedback.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def check_sessions():
    """Check all sessions and show details for those awaiting feedback."""
    print("🔍 Checking Jules Sessions...")
    print("=" * 70)

    async with JulesClient() as jules:
        # Get all sessions
        sessions_response = await jules.list_sessions(page_size=20)
        sessions = sessions_response.get("sessions", [])

        if not sessions:
            print("ℹ️  No sessions found")
            return

        print(f"📋 Found {len(sessions)} total session(s)\n")

        # Filter sessions awaiting feedback
        awaiting_feedback = [
            s for s in sessions
            if s.get("state") == "AWAITING_USER_FEEDBACK"
        ]

        if not awaiting_feedback:
            print("✅ No sessions awaiting feedback")
            return

        print(f"⚠️  {len(awaiting_feedback)} session(s) awaiting feedback:\n")

        for i, session in enumerate(awaiting_feedback, 1):
            session_id = session.get("name")
            display_name = session.get("displayName", "Unnamed")
            created = session.get("createTime", "Unknown")

            print(f"{i}. {display_name}")
            print(f"   Session ID: {session_id}")
            print(f"   Created: {created}")
            print(f"   State: {session.get('state')}")
            print()

            # Get full session details
            print(f"   📄 Fetching activities for session {i}...")
            activities_response = await jules.list_activities(session_id)
            activities = activities_response.get("activities", [])

            if activities:
                print(f"   📊 Found {len(activities)} activities:\n")

                # Show last 5 activities
                for activity in activities[-5:]:
                    activity_type = activity.get("type", "UNKNOWN")
                    originator = activity.get("originator", "UNKNOWN")
                    message = activity.get("message", "")

                    print(f"      [{activity_type}] {originator}")
                    if message:
                        # Truncate long messages
                        msg_preview = message[:200] + "..." if len(message) > 200 else message
                        print(f"      {msg_preview}")
                    print()

                # Check if there's a plan awaiting approval
                plan_activities = [
                    a for a in activities
                    if a.get("type") == "PLAN"
                ]
                if plan_activities:
                    print(f"   ⚠️  This session has a plan awaiting approval!")
                    print(f"      Use: await jules.approve_plan('{session_id}')")
                    print()

            print("=" * 70)
            print()


def main():
    """Main entry point."""
    asyncio.run(check_sessions())


if __name__ == "__main__":
    main()
