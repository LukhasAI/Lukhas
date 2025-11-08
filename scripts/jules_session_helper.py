#!/usr/bin/env python3
"""
Jules Session Helper - Approve plans and send feedback

Usage:
    # Approve a plan
    python3 scripts/jules_session_helper.py approve SESSION_ID

    # Send feedback/message
    python3 scripts/jules_session_helper.py message SESSION_ID "Your message here"

    # List all sessions
    python3 scripts/jules_session_helper.py list

    # Show today's sessions
    python3 scripts/jules_session_helper.py today
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient

# Today's session IDs (update as needed)
TODAY_SESSIONS = {
    "Guardian Kill-Switch": "9950861015326926289",
    "Autofix Pass": "6061065372654877432",
    "Labs Import Codemod": "11824147330734113995",
    "SLSA CI": "919280777160162153",
    "API Documentation": "3809108493363703079",
    "OpenAI Integration": "9782303394486808860",
    "Archive Cleanup": "9165833065484293067",
    "Ethics Documentation": "7304854500083516301",
    "test_env_loader": "4345524498649388654",
    "test_anthropic_wrapper": "16574199843217941387",
}


async def list_sessions():
    """List all Jules sessions"""
    async with JulesClient() as jules:
        sessions_response = await jules.list_sessions()

        if isinstance(sessions_response, dict):
            sessions = sessions_response.get('sessions', [])
        else:
            sessions = sessions_response

        print(f"\n📋 All Jules Sessions ({len(sessions)} total)")
        print("=" * 70)

        for i, session in enumerate(sessions[:20], 1):  # Show first 20
            session_id = session['name'].split('/')[-1]
            state = session.get('state', 'UNKNOWN')
            title = session.get('displayName', 'Untitled')[:50]

            status_icon = {
                "IN_PROGRESS": "🟡",
                "AWAITING_PLAN_APPROVAL": "⏸️",
                "WAITING_FOR_USER": "⏸️",
                "COMPLETED": "✅",
                "FAILED": "❌"
            }.get(state, "❓")

            print(f"{i}. {status_icon} {title}")
            print(f"   State: {state} | ID: {session_id}")

            if state in ["AWAITING_PLAN_APPROVAL", "WAITING_FOR_USER"]:
                print(f"   ⚠️  URL: https://jules.google.com/session/{session_id}")

            print()


async def show_today_sessions():
    """Show today's session URLs"""
    print("\n📅 Today's Jules Sessions")
    print("=" * 70)

    for title, session_id in TODAY_SESSIONS.items():
        print(f"\n• {title}")
        print(f"  ID: {session_id}")
        print(f"  URL: https://jules.google.com/session/{session_id}")


async def approve_plan(session_id: str):
    """Approve a Jules session plan"""
    async with JulesClient() as jules:
        print(f"\n✅ Approving plan for session: {session_id}")

        try:
            result = await jules.approve_plan(session_id)
            print("✅ Plan approved successfully!")
            print(f"   URL: https://jules.google.com/session/{session_id}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def send_message(session_id: str, message: str):
    """Send a message to Jules session"""
    async with JulesClient() as jules:
        print(f"\n💬 Sending message to session: {session_id}")
        print(f"   Message: {message}")

        try:
            result = await jules.send_message(session_id, message)
            print("✅ Message sent successfully!")
            print(f"   URL: https://jules.google.com/session/{session_id}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def bulk_approve():
    """Approve all waiting plans (use with caution!)"""
    async with JulesClient() as jules:
        sessions_response = await jules.list_sessions()

        if isinstance(sessions_response, dict):
            sessions = sessions_response.get('sessions', [])
        else:
            sessions = sessions_response

        waiting = [
            s for s in sessions
            if s.get('state') == 'AWAITING_PLAN_APPROVAL'
        ]

        if not waiting:
            print("\n✅ No plans waiting for approval")
            return

        print(f"\n⚠️  Found {len(waiting)} plans waiting for approval")

        for session in waiting:
            session_id = session['name'].split('/')[-1]
            title = session.get('displayName', 'Untitled')[:50]
            print(f"\n• {title}")
            print(f"  ID: {session_id}")

        confirm = input("\n⚠️  Approve ALL these plans? (yes/no): ").strip().lower()

        if confirm != 'yes':
            print("❌ Cancelled")
            return

        print("\n🚀 Approving plans...")

        for session in waiting:
            session_id = session['name'].split('/')[-1]
            title = session.get('displayName', 'Untitled')[:50]

            try:
                await jules.approve_plan(session_id)
                print(f"✅ Approved: {title}")
            except Exception as e:
                print(f"❌ Failed {title}: {e}")

            await asyncio.sleep(1)

        print("\n✅ Bulk approval complete!")


def main():
    parser = argparse.ArgumentParser(description="Jules Session Helper")
    parser.add_argument(
        "action",
        choices=["list", "today", "approve", "message", "bulk-approve"],
        help="Action to perform"
    )
    parser.add_argument("session_id", nargs="?", help="Session ID (for approve/message)")
    parser.add_argument("message_text", nargs="?", help="Message text (for message action)")

    args = parser.parse_args()

    if args.action == "list":
        asyncio.run(list_sessions())

    elif args.action == "today":
        asyncio.run(show_today_sessions())

    elif args.action == "approve":
        if not args.session_id:
            print("❌ Error: Session ID required for approve action")
            print("Usage: python3 scripts/jules_session_helper.py approve SESSION_ID")
            sys.exit(1)
        asyncio.run(approve_plan(args.session_id))

    elif args.action == "message":
        if not args.session_id or not args.message_text:
            print("❌ Error: Session ID and message required")
            print('Usage: python3 scripts/jules_session_helper.py message SESSION_ID "Your message"')
            sys.exit(1)
        asyncio.run(send_message(args.session_id, args.message_text))

    elif args.action == "bulk-approve":
        asyncio.run(bulk_approve())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏸️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
