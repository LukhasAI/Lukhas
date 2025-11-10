import asyncio

class DreamEngine:
    async def stream_generate(self, user_id: str):
        """Generates a stream of dream events."""
        for i in range(10):
            progress = (i + 1) * 10
            yield {
                "type": "dream_progress",
                "data": {"step": i, "content": f"Dream content for user {user_id}"},
                "progress": progress,
            }
            await asyncio.sleep(0.1)
