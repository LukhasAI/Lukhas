#!/usr/bin/env python3
"""Deep check for Jules messages across all sessions."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.jules_wrapper import JulesClient


async def check_all():
    async with JulesClient() as jules:
        # Get all sessions
        response = await jules.list_sessions(page_size=100)
        sessions = response.get('sessions', [])

        print(f'Checking all {len(sessions)} sessions for Jules messages...\n')

        sessions_with_messages = []

        for idx, session in enumerate(sessions, 1):
            session_id = session.get('name', '').split('/')[-1]
            state = session.get('state')
            title = session.get('displayName', 'No title')[:80]

            # Get activities
            try:
                act_response = await jules.list_activities(f'sessions/{session_id}', page_size=50)
                activities = act_response.get('activities', [])

                # Look for agent messages
                agent_messages = []
                for a in activities:
                    if a.get('originator') == 'AGENT':
                        if 'agentMessaged' in a:
                            agent_messages.append(a)

                if agent_messages:
                    sessions_with_messages.append({
                        'id': session_id,
                        'title': title,
                        'state': state,
                        'messages': agent_messages
                    })
                    print(f'[{idx}/{len(sessions)}] ⚠️  Session {session_id}: {len(agent_messages)} messages')
                    print(f'  State: {state}')
                    print(f'  Title: {title}')
                    print(f'  URL: https://jules.google.com/session/{session_id}')
                    for msg in agent_messages[-2:]:  # Show last 2 messages
                        text = msg['agentMessaged'].get('agentMessage', '')[:300]
                        create_time = msg.get('createTime', '')[:19]
                        print(f'  🤖 [{create_time}]: {text}...')
                    print()
            except Exception:
                pass

        print('\n' + '='*70)
        if sessions_with_messages:
            print(f'❌ Found {len(sessions_with_messages)} sessions with Jules messages!')
            print('\nSessions needing attention:')
            for s in sessions_with_messages:
                print(f'  - {s["id"]}: {s["title"]} ({s["state"]}) - {len(s["messages"])} messages')
        else:
            print('✅ No sessions with Jules messages found')


if __name__ == '__main__':
    asyncio.run(check_all())
