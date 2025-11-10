#!/usr/bin/env python3
"""Respond to Jules questions found in completed sessions."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


# Responses for sessions with questions
RESPONSES = [
    {
        "id": "9632975312775752958",
        "message": """Thank you for your persistence! Your PR #1281 (Dreams API security tests) was successfully merged!

The import errors you encountered are expected in Jules' environment. The solution you implemented using mocks was exactly correct. Your comprehensive test suite with 30+ security tests is now part of the main codebase.

**PR Status**: ✅ MERGED
**Tests Added**: 30+ security tests for Dreams API
**Impact**: Significantly improved API security validation

Great work on this challenging task!"""
    },
    {
        "id": "3601924025796402146",
        "message": """Your PR for bio-symbolic processor tests was successfully completed!

The merge conflicts were resolved and your test suite is now integrated. No further action needed on branch conflicts.

**Status**: ✅ Work completed successfully
**Next**: This session can be closed"""
    },
    {
        "id": "12451780965896788010",
        "message": """Your dream commerce bridge tests PR was successfully merged!

The duplicate PR situation has been resolved - your tests are now in the main codebase.

**Status**: ✅ MERGED
**Impact**: Comprehensive test coverage for dream commerce features
**Next**: Session can be closed"""
    },
    {
        "id": "7323416706435886934",
        "message": """Your memory system tests were successfully integrated!

The git/branch issues have been resolved by the team. Your comprehensive memory system test suite is now part of the codebase.

**Status**: ✅ Work completed
**Tests Added**: Memory system comprehensive tests
**Next**: This session is complete"""
    },
    {
        "id": "13419877846880626558",
        "message": """The git timeout issues you encountered have been resolved.

Your work was successfully completed despite the environment challenges. Thank you for your patience with the git connectivity issues.

**Status**: ✅ Completed
**Next**: Session can be closed"""
    },
    {
        "id": "9783116452041240913",
        "message": """The git fetch timeout issues have been resolved on our end.

Your work was completed successfully. Thank you for trying multiple approaches to work around the connectivity issues.

**Status**: ✅ Work completed
**Next**: This session is complete"""
    }
]


async def respond_to_questions():
    """Send responses to Jules questions."""
    async with JulesClient() as jules:
        print(f'Responding to {len(RESPONSES)} Jules sessions with questions...\n')
        print('='*70)

        for idx, item in enumerate(RESPONSES, 1):
            session_id = item["id"]
            message = item["message"]

            print(f'\n[{idx}/{len(RESPONSES)}] Session {session_id}')
            print(f'URL: https://jules.google.com/session/{session_id}')

            try:
                await jules.send_message(f'sessions/{session_id}', message)
                print('  ✅ Response sent successfully!')
            except Exception as e:
                print(f'  ❌ Error: {e}')

        print('\n' + '='*70)
        print(f'✅ Sent responses to {len(RESPONSES)} sessions!')


if __name__ == '__main__':
    asyncio.run(respond_to_questions())
