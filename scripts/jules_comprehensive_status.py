#!/usr/bin/env python3
"""Get comprehensive Jules session and PR status."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def get_comprehensive_status():
    """Get comprehensive Jules status report."""
    async with JulesClient() as jules:
        response = await jules.list_sessions(page_size=100)
        sessions = response.get('sessions', [])

        print('📊 COMPREHENSIVE JULES STATUS REPORT')
        print('='*70)
        print()

        # Count by state
        by_state = {}
        for s in sessions:
            state = s.get('state', 'UNKNOWN')
            by_state[state] = by_state.get(state, 0) + 1

        print(f'Total Sessions: {len(sessions)}')
        for state, count in sorted(by_state.items()):
            print(f'  {state}: {count}')

        # Check for sessions with PRs
        print('\n🔍 Checking PR associations...')
        pr_sessions = []
        no_pr_sessions = []

        for s in sessions:
            session_id = s.get('name', '').split('/')[-1]
            state = s.get('state', 'UNKNOWN')
            title = s.get('title', 'Untitled')

            # Only check COMPLETED sessions for PRs
            if state == 'COMPLETED':
                try:
                    session_detail = await jules.get_session(f'sessions/{session_id}')
                    pr_info = session_detail.get('pullRequest', {})
                    if pr_info.get('url'):
                        pr_sessions.append({
                            'id': session_id,
                            'title': title,
                            'pr_url': pr_info.get('url', '')
                        })
                    else:
                        no_pr_sessions.append({
                            'id': session_id,
                            'title': title
                        })
                except Exception as e:
                    no_pr_sessions.append({
                        'id': session_id,
                        'title': title
                    })

        print(f'\n📝 PR Generation (COMPLETED sessions only):')
        print(f'  Sessions with PRs: {len(pr_sessions)}')
        print(f'  Sessions without PRs: {len(no_pr_sessions)}')

        if no_pr_sessions:
            print(f'\n⚠️  COMPLETED sessions without PRs (candidates for cleanup):')
            for s in no_pr_sessions[:10]:
                print(f'  - {s["title"][:60]}... (ID: {s["id"]})')
            if len(no_pr_sessions) > 10:
                print(f'  ... and {len(no_pr_sessions) - 10} more')

        # Check recently created sessions (today)
        recent = [s for s in sessions if '2025-11-10T1' in s.get('createTime', '')]
        if recent:
            print(f'\n🆕 Recent Sessions (created today afternoon):')
            for s in sorted(recent, key=lambda x: x.get('createTime', ''), reverse=True)[:15]:
                title = s.get('title', 'Untitled')[:50]
                state = s.get('state', 'UNKNOWN')
                created = s.get('createTime', '')[:19]
                session_id = s.get('name', '').split('/')[-1]
                print(f'  - {title}... ({state})')
                print(f'    Created: {created}, ID: {session_id}')


if __name__ == '__main__':
    asyncio.run(get_comprehensive_status())
