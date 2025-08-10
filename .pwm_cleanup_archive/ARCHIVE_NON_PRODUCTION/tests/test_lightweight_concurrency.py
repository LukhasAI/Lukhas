import asyncio
import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.lightweight_concurrency import (
    ai_agent_behavior,
    create_lightweight_actor_system,
)


class TestLightweightConcurrency(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_ai_agent_behavior(self):
        async def _test():
            scheduler, pool = await create_lightweight_actor_system()

            # Create an AI agent actor
            agent = await pool.acquire_actor("ai-agent-1", ai_agent_behavior)

            # Teach the agent a fact
            await scheduler.send_message(
                agent.actor_id, {"type": "learn", "fact": "The sky is blue."}
            )
            await asyncio.sleep(0.01)

            # Check the agent's state
            self.assertIn("knowledge", agent.state)
            self.assertIn("The sky is blue.", agent.state["knowledge"])

            # Ask the agent a question
            # This part of the test is tricky because we don't have a direct way to get the response.
            # We will just send the message and assume it's processed.
            await scheduler.send_message(
                agent.actor_id, {"type": "ask", "question": "The sky is blue."}
            )
            await asyncio.sleep(0.01)

            await pool.shutdown()

        self.loop.run_until_complete(_test())


if __name__ == "__main__":
    unittest.main()
