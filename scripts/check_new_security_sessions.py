#!/usr/bin/env python3
"""Check status of newly created security hardening sessions."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


NEW_SESSION_IDS = [
    "9341665105078240778",  # Category 1: StrictAuthMiddleware
    "4881210246989891433",  # Category 2: serve/routes.py security
    "12640991174544438084",  # Category 3: openai_routes.py security
    "9632975312775752958",  # Category 4: Skipped tests
    "18029788532764900686",  # Category 5: Memory user isolation
    "8833127221412567236",  # Category 6: Dream/consciousness isolation
]


async def check_sessions():
    """Check status of new security sessions."""

    async with JulesClient() as jules:
        print("Checking status of 6 new security hardening sessions...\n")

        for idx, session_id in enumerate(NEW_SESSION_IDS, 1):
            try:
                session = await jules.get_session(f"sessions/{session_id}")

                state = session.get("state", "UNKNOWN")
                title = session.get("prompt", "")[:60] + "..."
                url = f"https://jules.google.com/session/{session_id}"

                print(f"[{idx}/6] {session_id}")
                print(f"  State: {state}")
                print(f"  Title: {title}")
                print(f"  URL: {url}")

                # If waiting for approval, print that
                if state == "WAITING_FOR_USER":
                    print(f"  ⏳ WAITING FOR APPROVAL - Ready to approve plan")
                elif state == "PLANNING":
                    print(f"  🔄 PLANNING - Jules is working on the plan")
                elif state == "IN_PROGRESS":
                    print(f"  ⚙️ IN_PROGRESS - Jules is implementing")
                elif state == "COMPLETED":
                    print(f"  ✅ COMPLETED")

                print()

            except Exception as e:
                print(f"  ❌ Error: {e}\n")

        print("="*70)
        print("Summary:")
        print("- To approve a plan: await jules.approve_plan('sessions/SESSION_ID')")
        print("- To send message: await jules.send_message('sessions/SESSION_ID', 'message')")


if __name__ == "__main__":
    asyncio.run(check_sessions())
