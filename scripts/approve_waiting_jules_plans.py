#!/usr/bin/env python3
"""Approve all Jules sessions in AWAITING_PLAN_APPROVAL state."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


SESSIONS_TO_APPROVE = [
    "8833127221412567236",   # Category 6: Dream/consciousness isolation
    "18029788532764900686",  # Category 5: Memory user isolation
]


async def approve_plans():
    """Approve plans for waiting sessions."""

    async with JulesClient() as jules:
        print(f"Approving {len(SESSIONS_TO_APPROVE)} Jules plans...\n")

        for idx, session_id in enumerate(SESSIONS_TO_APPROVE, 1):
            print(f"[{idx}/{len(SESSIONS_TO_APPROVE)}] Approving session {session_id}")

            try:
                result = await jules.approve_plan(f"sessions/{session_id}")

                print(f"  ✅ Plan approved!")
                print(f"  Result: {result}")
                print(f"  URL: https://jules.google.com/session/{session_id}\n")

            except Exception as e:
                print(f"  ❌ Failed to approve: {e}\n")

        print("="*70)
        print("✅ All plans approved! Jules will now start implementation.")
        print("="*70)


if __name__ == "__main__":
    asyncio.run(approve_plans())
