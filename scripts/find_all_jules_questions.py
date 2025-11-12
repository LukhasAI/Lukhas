#!/usr/bin/env python3
"""Find ALL Jules questions across all sessions by checking agentMessaged field."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def find_all_questions():
    async with JulesClient() as jules:
        # Get all sessions
        response = await jules.list_sessions(page_size=100)
        sessions = response.get('sessions', [])

        print(f'Checking {len(sessions)} sessions for Jules questions...\n')
        print('='*70)

        sessions_with_questions = []

        for idx, session in enumerate(sessions, 1):
            session_id = session.get('name', '').split('/')[-1]
            state = session.get('state')
            title = session.get('displayName', 'No title')[:80]

            # Get ALL activities
            try:
                act_response = await jules.list_activities(f'sessions/{session_id}', page_size=200)
                activities = act_response.get('activities', [])

                # Look specifically for agentMessaged field
                questions = []
                for activity in activities:
                    if 'agentMessaged' in activity:
                        msg = activity['agentMessaged'].get('agentMessage', '')
                        if msg:  # Has actual message text
                            questions.append({
                                'time': activity.get('createTime', '')[:19],
                                'message': msg
                            })

                if questions:
                    sessions_with_questions.append({
                        'id': session_id,
                        'title': title,
                        'state': state,
                        'questions': questions
                    })

                    print(f'\n[{idx}/{len(sessions)}] ⚠️  Session {session_id}')
                    print(f'State: {state}')
                    print(f'Title: {title}')
                    print(f'URL: https://jules.google.com/session/{session_id}')
                    print(f'Questions: {len(questions)}')

                    # Show all questions
                    for q in questions:
                        print(f'\n  🤖 [{q["time"]}]:')
                        print(f'     {q["message"][:300]}')
                        if len(q["message"]) > 300:
                            print(f'     ...(truncated)')

            except Exception as e:
                print(f'Error checking session {session_id}: {e}')

        print('\n' + '='*70)
        if sessions_with_questions:
            print(f'\n❌ Found {len(sessions_with_questions)} sessions with Jules questions!\n')
            for s in sessions_with_questions:
                print(f'  - {s["id"]}: {s["title"][:60]} ({s["state"]}) - {len(s["questions"])} questions')
                print(f'    URL: https://jules.google.com/session/{s["id"]}')
        else:
            print('\n✅ No sessions with Jules questions found')


if __name__ == '__main__':
    asyncio.run(find_all_questions())
