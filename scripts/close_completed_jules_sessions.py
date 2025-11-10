#!/usr/bin/env python3
"""Close (delete) Jules sessions that are completed and have submitted PRs."""

import asyncio
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def close_completed_sessions(dry_run: bool = True):
    """
    Find and close completed Jules sessions.

    Args:
        dry_run: If True, only show what would be deleted without actually deleting
    """

    async with JulesClient() as jules:
        print("Fetching all Jules sessions...\n")

        # Get all sessions
        sessions_response = await jules.list_sessions(page_size=100)
        all_sessions = sessions_response.get("sessions", [])

        print(f"Total sessions: {len(all_sessions)}\n")

        # Filter for completed sessions
        completed_sessions = [
            s for s in all_sessions
            if s.get("state") == "COMPLETED"
        ]

        if not completed_sessions:
            print("✅ No completed sessions to close!")
            return

        print(f"Found {len(completed_sessions)} COMPLETED sessions\n")

        if dry_run:
            print("🔍 DRY RUN MODE - No sessions will be deleted\n")
        else:
            print("⚠️  DELETION MODE - Sessions will be permanently deleted\n")

        print("="*70)

        deleted_count = 0
        skipped_count = 0

        for idx, session in enumerate(completed_sessions, 1):
            session_id = session.get("id", "unknown")
            prompt = session.get("prompt", "")[:60] + "..." if len(session.get("prompt", "")) > 60 else session.get("prompt", "")
            created = session.get("createdAt", "unknown")[:19]

            print(f"\n[{idx}/{len(completed_sessions)}] Session {session_id}")
            print(f"  Created: {created}")
            print(f"  Prompt: {prompt}")

            # Get session details to check for PR
            try:
                details = await jules.get_session(f"sessions/{session_id}")

                # Check if session has PR information
                # Jules sessions may have PR info in different fields - check common ones
                has_pr = False
                pr_url = None

                # Check various possible PR indicators
                if "pullRequest" in str(details):
                    has_pr = True
                    # Try to extract PR URL
                    if isinstance(details, dict):
                        pr_info = details.get("pullRequest") or details.get("pr") or details.get("github_pr")
                        if pr_info:
                            pr_url = pr_info if isinstance(pr_info, str) else pr_info.get("url")

                if has_pr and pr_url:
                    print(f"  ✅ Has PR: {pr_url}")
                    print(f"  🔒 PRESERVING: Sessions with PRs should be kept for audit trail")
                    skipped_count += 1
                    continue
                elif has_pr:
                    print(f"  ✅ Has PR (URL not found)")
                    print(f"  🔒 PRESERVING: Sessions with PRs should be kept for audit trail")
                    skipped_count += 1
                    continue
                else:
                    print(f"  ℹ️  No PR found (may be a failed or manual session)")

                # Only delete sessions WITHOUT PRs
                if dry_run:
                    print(f"  🔍 Would delete: sessions/{session_id}")
                    deleted_count += 1
                else:
                    # Delete the session
                    await jules.delete_session(f"sessions/{session_id}")
                    print(f"  ✅ Deleted: sessions/{session_id}")
                    deleted_count += 1

            except Exception as e:
                print(f"  ❌ Error processing session: {e}")
                skipped_count += 1

        print("\n" + "="*70)

        if dry_run:
            print(f"\n🔍 DRY RUN Summary:")
            print(f"  Would delete: {deleted_count} sessions")
            print(f"  Would skip: {skipped_count} sessions (errors)")
            print(f"\nTo actually delete sessions, run:")
            print(f"  python3 scripts/close_completed_jules_sessions.py --delete")
        else:
            print(f"\n✅ Deletion Summary:")
            print(f"  Deleted: {deleted_count} sessions")
            print(f"  Skipped: {skipped_count} sessions (errors)")
            print(f"\nRemaining sessions: {len(all_sessions) - deleted_count}")


if __name__ == "__main__":
    # Check for --delete flag
    delete_mode = "--delete" in sys.argv or "--force" in sys.argv

    if delete_mode:
        print("⚠️  WARNING: This will permanently delete completed Jules sessions!")
        print("Press Ctrl+C within 3 seconds to cancel...\n")
        import time
        time.sleep(3)

    asyncio.run(close_completed_sessions(dry_run=not delete_mode))
