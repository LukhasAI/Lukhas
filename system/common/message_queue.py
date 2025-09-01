"""
Message Queue for Bottleneck Modules
====================================
Handles high-traffic communication with queuing and caching.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Message in the queue"""

    id: str
    source: str
    target: str
    payload: dict[str, Any]
    priority: int = 0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class MessageQueue:
    """Priority message queue for module communication"""

    def __init__(self, max_size: int = 10000):
        self._queues: dict[str, asyncio.PriorityQueue] = {}
        self._processors: dict[str, Callable] = {}
        self._max_size = max_size
        self._running = False
        self._metrics = {
            "messages_queued": 0,
            "messages_processed": 0,
            "messages_dropped": 0,
            "average_latency_ms": 0,
        }

    def register_processor(self, module: str, processor: Callable):
        """Register a message processor for a module"""
        self._processors[module] = processor
        if module not in self._queues:
            self._queues[module] = asyncio.PriorityQueue(maxsize=self._max_size)
        logger.info(f"Registered processor for module: {module}")

    async def enqueue(self, message: Message):
        """Add message to queue"""
        target_queue = self._queues.get(message.target)

        if not target_queue:
            logger.warning(f"No queue for target module: {message.target}")
            self._metrics["messages_dropped"] += 1
            return

        try:
            # Priority is negative because PriorityQueue is min-heap
            await target_queue.put((-message.priority, message))
            self._metrics["messages_queued"] += 1
        except asyncio.QueueFull:
            logger.error(f"Queue full for module: {message.target}")
            self._metrics["messages_dropped"] += 1

    async def process_module_queue(self, module: str):
        """Process messages for a specific module"""
        queue = self._queues.get(module)
        processor = self._processors.get(module)

        if not queue or not processor:
            return

        while self._running:
            try:
                # Get message with timeout
                priority, message = await asyncio.wait_for(queue.get(), timeout=1.0)

                # Calculate latency
                latency = (datetime.utcnow() - message.timestamp).total_seconds() * 1000
                self._update_latency(latency)

                # Process message
                if asyncio.iscoroutinefunction(processor):
                    await processor(message)
                else:
                    processor(message)

                self._metrics["messages_processed"] += 1

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message for {module}: {e}")

    async def start(self):
        """Start message queue processing"""
        self._running = True
        logger.info("Message queue started")

        # Start processors for each module
        tasks = []
        for module in self._queues:
            task = asyncio.create_task(self.process_module_queue(module))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop message queue processing"""
        self._running = False

        # Process remaining messages
        for module, queue in self._queues.items():
            while not queue.empty():
                try:
                    priority, message = queue.get_nowait()
                    processor = self._processors.get(module)
                    if processor:
                        await processor(message)
                except Exception as e:
                    logger.error(f"Error processing remaining messages: {e}")

        logger.info("Message queue stopped")

    def _update_latency(self, latency: float):
        """Update average latency metric"""
        if self._metrics["average_latency_ms"] == 0:
            self._metrics["average_latency_ms"] = latency
        else:
            # Exponential moving average
            alpha = 0.1
            self._metrics["average_latency_ms"] = alpha * latency + (1 - alpha) * self._metrics["average_latency_ms"]

    def get_metrics(self) -> dict[str, Any]:
        """Get queue metrics"""
        metrics = self._metrics.copy()
        metrics["queue_sizes"] = {module: queue.qsize() for module, queue in self._queues.items()}
        return metrics


# Global message queue instance
message_queue = MessageQueue()


# Cache layer for frequent requests
class CacheLayer:
    """Caching layer for reducing bottleneck load"""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: dict[str, Any] = {}
        self._timestamps: dict[str, datetime] = {}
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            timestamp = self._timestamps[key]
            if (datetime.utcnow() - timestamp).total_seconds() < self._ttl:
                self._hits += 1
                return self._cache[key]
            else:
                # Expired
                del self._cache[key]
                del self._timestamps[key]

        self._misses += 1
        return None

    def set(self, key: str, value: Any):
        """Set value in cache"""
        self._cache[key] = value
        self._timestamps[key] = datetime.utcnow()

    def clear(self):
        """Clear cache"""
        self._cache.clear()
        self._timestamps.clear()

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "size": len(self._cache),
        }


# Create cache instances for bottleneck modules
cache_layers = {"core": CacheLayer(), "orchestration": CacheLayer()}
