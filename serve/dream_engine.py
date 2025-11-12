import asyncio

class DreamEngine:
    async def stream_generate(self, user_id: str):
        """
        Generates a stream of dream events.

        Args:
            user_id (str): User identifier for personalized dream generation.

        Yields:
            dict: Dictionary with keys:
                - type (str): Type of the event, e.g., "dream_progress".
                - data (dict): Event data, including step and content.
                - progress (int): Progress percentage (0-100).
        """
        for i in range(10):
            progress = (i + 1) * 10
            yield {
                "type": "dream_progress",
                "data": {"step": i, "content": f"Dream content for user {user_id}"},
                "progress": progress,
            }
            await asyncio.sleep(0.1)
