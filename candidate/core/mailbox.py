"""
Enhanced Mailbox System for Actor Model
Addresses TODO 35: Sequential Processing with Advanced Features

This module implements sophisticated mailbox functionality including:
- Priority queues for message ordering
- Back-pressure mechanisms
- Dead letter queues
- Message persistence options
- Bounded and unbounded variants
"""
import asyncio
import heapq
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

import streamlit as st

from .actor_system import Actor, ActorMessage

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels"""

    SYSTEM = 0  # Highest priority - system messages
    HIGH = 1  # High priority user messages
    NORMAL = 2  # Default priority
    LOW = 3  # Low priority background tasks
    BULK = 4  # Lowest priority bulk operations


class MailboxType(Enum):
    """Types of mailboxes available"""

    UNBOUNDED = "unbounded"
    BOUNDED = "bounded"
    PRIORITY = "priority"
    PERSISTENT = "persistent"


@dataclass
class PrioritizedMessage:
    """Message wrapper with priority and ordering"""

    priority: int
    sequence: int  # For FIFO within same priority
    message: ActorMessage
    enqueued_at: float = field(default_factory=time.time)

    def __lt__(self, other):
        # Lower priority value = higher priority
        if self.priority != other.priority:
            return self.priority < other.priority
        # Same priority: FIFO based on sequence
        return self.sequence < other.sequence


class DeadLetterQueue:
    """Storage for messages that couldn't be processed"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.messages: deque = deque(maxlen=max_size)
        self._lock = asyncio.Lock()

    async def add(self, message: ActorMessage, reason: str):
        """Add a message to dead letter queue"""
        async with self._lock:
            self.messages.append(
                {
                    "message": message,
                    "reason": reason,
                    "timestamp": time.time(),
                }
            )
            logger.warning(f"Message {message.message_id} moved to DLQ: {reason}")

    async def get_all(self) -> list[dict[str, Any]]:
        """Get all messages in DLQ"""
        async with self._lock:
            return list(self.messages)

    async def clear(self):
        """Clear the DLQ"""
        async with self._lock:
            self.messages.clear()


class BackPressureStrategy(Enum):
    """Strategies for handling back-pressure"""

    DROP_NEWEST = "drop_newest"  # Drop incoming message
    DROP_OLDEST = "drop_oldest"  # Drop oldest in queue
    BLOCK = "block"  # Block until space available
    REDIRECT = "redirect"  # Redirect to overflow handler


class Mailbox:
    """Base mailbox implementation with sequential processing guarantees"""

    def __init__(
        self,
        max_size: Optional[int] = None,
        back_pressure_strategy: BackPressureStrategy = BackPressureStrategy.BLOCK,
    ):
        self.max_size = max_size
        self.back_pressure_strategy = back_pressure_strategy
        self._sequence_counter = 0
        self._stats = {
            "messages_received": 0,
            "messages_processed": 0,
            "messages_dropped": 0,
            "messages_dlq": 0,
            "current_size": 0,
            "max_size_reached": 0,
            "total_wait_time": 0.0,
        }

    async def put(self, message: ActorMessage) -> bool:
        """Add message to mailbox"""
        raise NotImplementedError

    async def get(self) -> ActorMessage:
        """Get next message from mailbox"""
        raise NotImplementedError

    def qsize(self) -> int:
        """Get current mailbox size"""
        raise NotImplementedError

    def is_full(self) -> bool:
        """Check if mailbox is full"""
        if self.max_size is None:
            return False
        return self.qsize() >= self.max_size

    def get_stats(self) -> dict[str, Any]:
        """Get mailbox statistics"""
        return {
            **self._stats,
            "current_size": self.qsize(),
            "utilization": (self.qsize() / self.max_size if self.max_size else 0),
        }


class UnboundedMailbox(Mailbox):
    """Simple unbounded FIFO mailbox"""

    def __init__(self):
        super().__init__(max_size=None)
        self._queue = asyncio.Queue()

    async def put(self, message: ActorMessage) -> bool:
        """Add message to mailbox"""
        await self._queue.put(message)
        self._stats["messages_received"] += 1
        return True

    async def get(self) -> ActorMessage:
        """Get next message from mailbox"""
        start_time = time.time()
        message = await self._queue.get()
        wait_time = time.time() - start_time

        self._stats["messages_processed"] += 1
        self._stats["total_wait_time"] += wait_time

        return message

    def qsize(self) -> int:
        """Get current mailbox size"""
        return self._queue.qsize()


class BoundedMailbox(Mailbox):
    """Bounded mailbox with back-pressure handling"""

    def __init__(
        self,
        max_size: int = 1000,
        back_pressure_strategy: BackPressureStrategy = BackPressureStrategy.BLOCK,
        dead_letter_queue: Optional[DeadLetterQueue] = None,
    ):
        super().__init__(max_size, back_pressure_strategy)
        self._queue = asyncio.Queue(maxsize=max_size)
        self.dead_letter_queue = dead_letter_queue or DeadLetterQueue()

    async def put(self, message: ActorMessage) -> bool:
        """Add message to mailbox with back-pressure handling"""
        self._stats["messages_received"] += 1

        if self.back_pressure_strategy == BackPressureStrategy.BLOCK:
            # Block until space available
            await self._queue.put(message)
            return True

        elif self.back_pressure_strategy == BackPressureStrategy.DROP_NEWEST:
            # Try to put, drop if full
            try:
                self._queue.put_nowait(message)
                return True
            except asyncio.QueueFull:
                self._stats["messages_dropped"] += 1
                self._stats["max_size_reached"] += 1
                await self.dead_letter_queue.add(message, "mailbox_full")
                return False

        elif self.back_pressure_strategy == BackPressureStrategy.DROP_OLDEST:
            # Drop oldest if full
            if self._queue.full():
                try:
                    # Remove oldest
                    old_message = self._queue.get_nowait()
                    self._stats["messages_dropped"] += 1
                    await self.dead_letter_queue.add(old_message, "dropped_for_newer")
                except asyncio.QueueEmpty:
                    pass

            await self._queue.put(message)
            return True

        return False

    async def get(self) -> ActorMessage:
        """Get next message from mailbox"""
        start_time = time.time()
        message = await self._queue.get()
        wait_time = time.time() - start_time

        self._stats["messages_processed"] += 1
        self._stats["total_wait_time"] += wait_time

        return message

    def qsize(self) -> int:
        """Get current mailbox size"""
        return self._queue.qsize()


class PriorityMailbox(Mailbox):
    """Priority-based mailbox with multiple queues"""

    def __init__(
        self,
        max_size: int = 1000,
        back_pressure_strategy: BackPressureStrategy = BackPressureStrategy.BLOCK,
        starvation_prevention: bool = True,
    ):
        super().__init__(max_size, back_pressure_strategy)
        self._heap: list[PrioritizedMessage] = []
        self._lock = asyncio.Lock()
        self._not_empty = asyncio.Condition(self._lock)
        self._not_full = asyncio.Condition(self._lock)
        self.starvation_prevention = starvation_prevention
        self._priority_counters = dict.fromkeys(MessagePriority, 0)

        # Starvation prevention: track when first message of each priority was added
        self._first_message_time = dict.fromkeys(MessagePriority)
        self._last_service_time = {p: time.time() for p in MessagePriority}
        self._starvation_threshold = 10.0  # seconds

    async def put(
        self,
        message: ActorMessage,
        priority: MessagePriority = MessagePriority.NORMAL,
    ) -> bool:
        """Add message to mailbox with priority"""
        async with self._not_full:
            # Wait if full and blocking strategy
            while self.is_full() and self.back_pressure_strategy == BackPressureStrategy.BLOCK:
                await self._not_full.wait()

            # Handle back-pressure for non-blocking strategies
            if self.is_full():
                if self.back_pressure_strategy == BackPressureStrategy.DROP_NEWEST:
                    self._stats["messages_dropped"] += 1
                    return False
                elif self.back_pressure_strategy == BackPressureStrategy.DROP_OLDEST:
                    # Find and remove lowest priority oldest message
                    if self._heap:
                        # Since heap is min-heap by priority, last elements have lowest
                        # priority
                        removed = heapq.heappop(self._heap)
                        self._stats["messages_dropped"] += 1
                        self._priority_counters[MessagePriority(removed.priority)] -= 1

            # Add message
            prioritized_msg = PrioritizedMessage(
                priority=priority.value,
                sequence=self._sequence_counter,
                message=message,
            )
            self._sequence_counter += 1

            heapq.heappush(self._heap, prioritized_msg)
            self._stats["messages_received"] += 1
            self._priority_counters[priority] += 1

            # Track first message time for starvation prevention
            if self._first_message_time[priority] is None:
                self._first_message_time[priority] = time.time()

            self._not_empty.notify()
            return True

    async def get(self) -> ActorMessage:
        """Get highest priority message with starvation prevention"""
        async with self._not_empty:
            while not self._heap:
                await self._not_empty.wait()

            start_time = time.time()

            # Check for starvation if enabled
            if self.starvation_prevention:
                selected_msg = await self._select_with_starvation_prevention()
            else:
                selected_msg = heapq.heappop(self._heap)

            wait_time = time.time() - start_time

            # Update stats
            self._stats["messages_processed"] += 1
            self._stats["total_wait_time"] += wait_time
            priority = MessagePriority(selected_msg.priority)
            self._priority_counters[priority] -= 1
            self._last_service_time[priority] = time.time()

            # Reset first message time if no more messages of this priority
            if self._priority_counters[priority] == 0:
                self._first_message_time[priority] = None

            self._not_full.notify()
            return selected_msg.message

    async def _select_with_starvation_prevention(self) -> PrioritizedMessage:
        """Select message considering starvation"""
        current_time = time.time()

        # Check each priority level for starvation
        for priority in MessagePriority:
            if self._priority_counters[priority] > 0 and self._first_message_time[priority] is not None:
                # Check how long the oldest message of this priority has been waiting
                time_waiting = current_time - self._first_message_time[priority]

                # If this priority is starving, find and return its oldest message
                if time_waiting > self._starvation_threshold:
                    # Find oldest message of this priority
                    for i, msg in enumerate(self._heap):
                        if msg.priority == priority.value:
                            # Remove and return this message
                            selected = self._heap.pop(i)
                            # Restore heap property after removal
                            heapq.heapify(self._heap)
                            return selected

        # No starvation detected, return highest priority
        return heapq.heappop(self._heap)

    def qsize(self) -> int:
        """Get current mailbox size"""
        return len(self._heap)

    def get_priority_stats(self) -> dict[str, int]:
        """Get message count by priority"""
        return {p.name: count for p, count in self._priority_counters.items()}


class PersistentMailbox(BoundedMailbox):
    """Mailbox with optional persistence to disk"""

    def __init__(
        self,
        max_size: int = 1000,
        persistence_path: Optional[str] = None,
        persistence_interval: float = 5.0,
    ):
        super().__init__(max_size)
        self.persistence_path = persistence_path
        self.persistence_interval = persistence_interval
        self._last_persist_time = time.time()
        self._persist_lock = asyncio.Lock()

        # Start persistence task if path provided
        self._persistence_task = None
        if persistence_path:
            # Task will be created when first message is added
            self._needs_persistence_task = True
        else:
            self._needs_persistence_task = False

    async def put(self, message: ActorMessage) -> bool:
        """Add message and trigger persistence if needed"""
        result = await super().put(message)

        # Start persistence task on first message if needed
        if self._needs_persistence_task and self._persistence_task is None:
            try:
                self._persistence_task = asyncio.create_task(self._persistence_loop())
                self._needs_persistence_task = False
            except RuntimeError:
                # No event loop yet, will retry later
                pass

        # Check if we should persist
        if self.persistence_path and time.time() - self._last_persist_time > self.persistence_interval:
            asyncio.create_task(self._persist_messages())

        return result

    async def _persist_messages(self):
        """Persist current mailbox state to disk"""
        async with self._persist_lock:
            if not self.persistence_path:
                return

            try:
                # Get current messages
                messages = []
                temp_storage = []

                # Temporarily drain queue
                while not self._queue.empty():
                    try:
                        msg = self._queue.get_nowait()
                        messages.append(msg.to_dict())
                        temp_storage.append(msg)
                    except asyncio.QueueEmpty:
                        break

                # Restore messages
                for msg in temp_storage:
                    await self._queue.put(msg)

                # Write to disk
                with open(self.persistence_path, "w") as f:
                    json.dump(
                        {
                            "messages": messages,
                            "stats": self._stats,
                            "timestamp": time.time(),
                        },
                        f,
                    )

                self._last_persist_time = time.time()
                logger.debug(f"Persisted {len(messages)} messages to {self.persistence_path}")

            except Exception as e:
                logger.error(f"Failed to persist mailbox: {e}")

    async def _persistence_loop(self):
        """Background task for periodic persistence"""
        while True:
            await asyncio.sleep(self.persistence_interval)
            await self._persist_messages()

    async def restore_from_disk(self) -> int:
        """Restore messages from disk"""
        if not self.persistence_path:
            return 0

        try:
            with open(self.persistence_path) as f:
                data = json.load(f)

            messages = data.get("messages", [])
            for msg_dict in messages:
                # Reconstruct ActorMessage
                message = ActorMessage(**msg_dict)
                await self.put(message)

            logger.info(f"Restored {len(messages)} messages from {self.persistence_path}")
            return len(messages)

        except FileNotFoundError:
            logger.debug(f"No persistence file found at {self.persistence_path}")
            return 0
        except Exception as e:
            logger.error(f"Failed to restore mailbox: {e}")
            return 0


class MailboxFactory:
    """Factory for creating different mailbox types"""

    @staticmethod
    def create_mailbox(mailbox_type: MailboxType = MailboxType.BOUNDED, **kwargs) -> Mailbox:
        """Create a mailbox of specified type"""

        if mailbox_type == MailboxType.UNBOUNDED:
            return UnboundedMailbox()

        elif mailbox_type == MailboxType.BOUNDED:
            return BoundedMailbox(
                max_size=kwargs.get("max_size", 1000),
                back_pressure_strategy=kwargs.get("back_pressure_strategy", BackPressureStrategy.BLOCK),
            )

        elif mailbox_type == MailboxType.PRIORITY:
            return PriorityMailbox(
                max_size=kwargs.get("max_size", 1000),
                back_pressure_strategy=kwargs.get("back_pressure_strategy", BackPressureStrategy.BLOCK),
                starvation_prevention=kwargs.get("starvation_prevention", True),
            )

        elif mailbox_type == MailboxType.PERSISTENT:
            return PersistentMailbox(
                max_size=kwargs.get("max_size", 1000),
                persistence_path=kwargs.get("persistence_path"),
                persistence_interval=kwargs.get("persistence_interval", 5.0),
            )

        else:
            raise ValueError(f"Unknown mailbox type: {mailbox_type}")


# Enhanced Actor with configurable mailbox


class MailboxActor(Actor):
    """Actor with enhanced mailbox capabilities"""

    def __init__(
        self,
        actor_id: str,
        mailbox_type: MailboxType = MailboxType.BOUNDED,
        mailbox_config: Optional[dict[str, Any]] = None,
    ):
        super().__init__(actor_id)

        # Replace default mailbox with enhanced version
        mailbox_config = mailbox_config or {}
        self.mailbox = MailboxFactory.create_mailbox(mailbox_type, **mailbox_config)

        # Message filtering
        self._message_filters: list[Callable[[ActorMessage], bool]] = []

        # Batch processing support
        self._batch_size = mailbox_config.get("batch_size", 1)
        self._batch_timeout = mailbox_config.get("batch_timeout", 0.1)

    def add_message_filter(self, filter_func: Callable[[ActorMessage], bool]):
        """Add a message filter"""
        self._message_filters.append(filter_func)

    async def send_message(self, message: ActorMessage) -> bool:
        """Override to support filtering"""
        # Apply filters
        for filter_func in self._message_filters:
            if not filter_func(message):
                logger.debug(f"Message {message.message_id} filtered out")
                return False

        # Determine priority if using priority mailbox
        if isinstance(self.mailbox, PriorityMailbox):
            priority = self._determine_priority(message)
            return await self.mailbox.put(message, priority)

        return await self.mailbox.put(message)

    def _determine_priority(self, message: ActorMessage) -> MessagePriority:
        """Determine message priority based on type and content"""
        # System messages get highest priority
        if message.message_type.startswith("system_"):
            return MessagePriority.SYSTEM

        # Check for priority hint in payload
        if "priority" in message.payload:
            priority_value = message.payload["priority"]
            if isinstance(priority_value, str):
                return MessagePriority[priority_value.upper()]
            elif isinstance(priority_value, int):
                return MessagePriority(priority_value)

        # Default priority based on message type
        priority_map = {
            "health_check": MessagePriority.HIGH,
            "shutdown": MessagePriority.SYSTEM,
            "query": MessagePriority.NORMAL,
            "batch": MessagePriority.BULK,
        }

        return priority_map.get(message.message_type, MessagePriority.NORMAL)

    async def _message_loop(self):
        """Enhanced message loop with batch processing"""
        while self._running:
            try:
                if self._batch_size > 1:
                    # Batch processing mode
                    messages = await self._get_message_batch()
                    if messages:
                        await self._process_message_batch(messages)
                else:
                    # Single message processing
                    message = await asyncio.wait_for(self.mailbox.get(), timeout=1.0)
                    await self._process_message(message)
                    self._stats["messages_processed"] += 1
                    self._stats["last_activity"] = time.time()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._stats["messages_failed"] += 1
                logger.error(f"Actor {self.actor_id} message processing error: {e}")

                if self.supervisor:
                    await self.supervisor.tell(
                        "child_failed",
                        {"child_id": self.actor_id, "error": str(e)},
                    )

    async def _get_message_batch(self) -> list[ActorMessage]:
        """Get a batch of messages"""
        messages = []
        deadline = time.time() + self._batch_timeout

        while len(messages) < self._batch_size and time.time() < deadline:
            try:
                timeout = deadline - time.time()
                if timeout > 0:
                    message = await asyncio.wait_for(self.mailbox.get(), timeout=timeout)
                    messages.append(message)
                else:
                    break
            except asyncio.TimeoutError:
                break

        return messages

    async def _process_message_batch(self, messages: list[ActorMessage]):
        """Process a batch of messages"""
        # Default implementation processes sequentially
        for message in messages:
            await self._process_message(message)
            self._stats["messages_processed"] += 1

        self._stats["last_activity"] = time.time()

    def get_mailbox_stats(self) -> dict[str, Any]:
        """Get detailed mailbox statistics"""
        stats = {
            "actor_stats": self.get_stats(),
            "mailbox_stats": self.mailbox.get_stats(),
            "mailbox_type": type(self.mailbox).__name__,
        }

        if isinstance(self.mailbox, PriorityMailbox):
            stats["priority_distribution"] = self.mailbox.get_priority_stats()

        return stats


# Example usage


async def demo_enhanced_mailbox():
    """Demonstrate enhanced mailbox features"""
    from .actor_system import get_global_actor_system

    system = await get_global_actor_system()

    # Create actor with priority mailbox

    class PriorityActor(MailboxActor):
        def __init__(self, actor_id: str):
            super().__init__(
                actor_id,
                mailbox_type=MailboxType.PRIORITY,
                mailbox_config={
                    "max_size": 100,
                    "starvation_prevention": True,
                },
            )
            self.register_handler("process", self._handle_process)

        async def _handle_process(self, message: ActorMessage):
            print(f"Processing {message.message_type} with priority {message.payload.get('priority', 'NORMAL')}")
            await asyncio.sleep(0.1)  # Simulate work
            return {"processed": True}

    # Create actor
    actor_ref = await system.create_actor(PriorityActor, "priority-actor-001")

    # Send messages with different priorities
    tasks = []

    # Send low priority messages
    for i in range(5):
        tasks.append(actor_ref.tell("process", {"data": f"low-priority-{i}", "priority": "LOW"}))

    # Send high priority message
    tasks.append(actor_ref.tell("process", {"data": "urgent-task", "priority": "HIGH"}))

    # Send system message
    tasks.append(actor_ref.tell("system_health_check", {"check_type": "full"}))

    await asyncio.gather(*tasks)

    # Wait for processing
    await asyncio.sleep(2)

    # Get stats
    actor = system.get_actor("priority-actor-001")
    stats = actor.get_mailbox_stats()
    print("Mailbox stats:", json.dumps(stats, indent=2))


if __name__ == "__main__":
    asyncio.run(demo_enhanced_mailbox())
