#!/usr/bin/env python3
"""
Inspect a Specific Jules Session
================================

Shows full details of a session including all activities.
"""
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def inspect_session(session_id: str):
    """Inspect a specific session in detail."""
    print(f"🔍 Inspecting Jules Session: {session_id}")
    print("=" * 70)

    async with JulesClient() as jules:
        # Get session details
        session = await jules.get_session(session_id)
        print("\n📄 Session Details:")
        print(json.dumps(session, indent=2, default=str))
        print()

        # Get activities
        activities_response = await jules.list_activities(session_id)
        activities = activities_response.get("activities", [])

        print(f"\n📊 Activities ({len(activities)} total):")
        print("=" * 70)

        # Show last 10 activities
        for i, activity in enumerate(activities[-10:], 1):
            print(f"\nActivity {len(activities) - 10 + i}:")
            print(json.dumps(activity, indent=2, default=str))
            print("-" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/inspect_jules_session.py <session_id>")
        print("\nExample:")
        print("  python3 scripts/inspect_jules_session.py sessions/8638636043477486067")
        sys.exit(1)

    session_id = sys.argv[1]
    asyncio.run(inspect_session(session_id))


if __name__ == "__main__":
    main()
