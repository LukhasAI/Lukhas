"""
Asynchronous priority queue for managing requests with backpressure and fairness.
"""

import asyncio
import time
from collections import deque
from enum import IntEnum
from typing import Any, Coroutine, Deque, Dict, NamedTuple, Tuple


class Priority(IntEnum):
    """Request priority levels."""
    LOW = 10
    NORMAL = 5
    HIGH = 1


class Request(NamedTuple):
    """Represents a request in the queue."""
    priority: Priority
    request_id: str
    submitted_at: float
    task: Coroutine[Any, Any, Any]


class RequestQueue:
    """
    An asynchronous priority queue with backpressure and fairness.
    """

    def __init__(self, max_size: int = 100, fairness_window: int = 10):
        self._max_size = max_size
        self._fairness_window = fairness_window
        self._queue: asyncio.PriorityQueue[Tuple[int, float, Request]] = asyncio.PriorityQueue()
        self._recent_requests: Dict[str, Deque[float]] = {}

    async def put(self, request_id: str, task: Coroutine[Any, Any, Any], priority: Priority) -> None:
        """
        Add a request to the queue.

        Args:
            request_id: A unique identifier for the request.
            task: The coroutine to execute for this request.
            priority: The priority of the request.

        Raises:
            asyncio.QueueFull: If the queue is full.
        """
        if self._queue.qsize() >= self._max_size:
            raise asyncio.QueueFull("Request queue is full")

        submitted_at = time.monotonic()
        request = Request(priority, request_id, submitted_at, task)
        await self._queue.put((priority.value, submitted_at, request))

    async def get(self) -> Request:
        """
        Get the next request from the queue, applying fairness rules.

        Returns:
            The next request to be processed.
        """
        while True:
            priority_val, submitted_at, request = await self._queue.get()

            if self._is_fair_to_process(request.request_id):
                self._record_request(request.request_id)
                return request
            else:
                # Re-queue with a slightly lower priority to prevent it from
                # being immediately picked again.
                await self._queue.put((priority_val + 1, submitted_at, request))
                await asyncio.sleep(0.01)  # Small delay to prevent busy-waiting

    def qsize(self) -> int:
        """Return the current size of the queue."""
        return self._queue.qsize()

    def full(self) -> bool:
        """Return True if the queue is full."""
        return self.qsize() >= self._max_size

    def _is_fair_to_process(self, request_id: str) -> bool:
        """
        Determine if it's fair to process a request from a given source.
        A request is considered unfair if the same request_id has been
        processed more than once in the fairness window.
        """
        if request_id not in self._recent_requests:
            return True

        now = time.monotonic()
        recent_times = self._recent_requests[request_id]

        # Clean up old timestamps
        while recent_times and now - recent_times[0] > self._fairness_window:
            recent_times.popleft()

        # Unfair if there are recent requests from the same ID
        return not recent_times

    def _record_request(self, request_id: str) -> None:
        """Record that a request has been processed."""
        if request_id not in self._recent_requests:
            self._recent_requests[request_id] = deque()
        self._recent_requests[request_id].append(time.monotonic())
