"""
Comprehensive tests for the Enhanced Mailbox System
Tests sequential guarantees, priority processing, back-pressure, and persistence
"""

import asyncio
import tempfile
from pathlib import Path

import pytest

from core.actor_system import ActorMessage, get_global_actor_system
from core.mailbox import (
    BackPressureStrategy,
    BoundedMailbox,
    DeadLetterQueue,
    MailboxActor,
    MailboxFactory,
    MailboxType,
    MessagePriority,
    PersistentMailbox,
    PriorityMailbox,
    UnboundedMailbox,
)


class TestMailboxBasics:
    """Test basic mailbox functionality"""

    @pytest.mark.asyncio
    async def test_unbounded_mailbox(self):
        """Test unbounded mailbox can accept many messages"""
        mailbox = UnboundedMailbox()

        # Add 1000 messages
        for i in range(1000):
            msg = ActorMessage(
                message_id=str(i),
                sender="test",
                recipient="test",
                message_type="test",
                payload={"id": i},
                timestamp=0,
            )
            result = await mailbox.put(msg)
            assert result is True

        assert mailbox.qsize() == 1000

        # Retrieve messages in FIFO order
        for i in range(1000):
            msg = await mailbox.get()
            assert msg.payload["id"] == i

    @pytest.mark.asyncio
    async def test_bounded_mailbox_blocking(self):
        """Test bounded mailbox with blocking strategy"""
        mailbox = BoundedMailbox(
            max_size=5, back_pressure_strategy=BackPressureStrategy.BLOCK
        )

        # Fill mailbox
        for i in range(5):
            msg = ActorMessage(
                message_id=str(i),
                sender="test",
                recipient="test",
                message_type="test",
                payload={"id": i},
                timestamp=0,
            )
            await mailbox.put(msg)

        assert mailbox.is_full()

        # Try to add one more - should block
        blocked = False

        async def try_put():
            nonlocal blocked
            blocked = True
            msg = ActorMessage(
                message_id="blocked",
                sender="test",
                recipient="test",
                message_type="test",
                payload={},
                timestamp=0,
            )
            await mailbox.put(msg)  # This should block
            blocked = False

        # Start put task
        put_task = asyncio.create_task(try_put())
        await asyncio.sleep(0.1)
        assert blocked  # Should be blocked

        # Remove one message
        await mailbox.get()
        await asyncio.sleep(0.1)
        assert not blocked  # Should unblock

        put_task.cancel()

    @pytest.mark.asyncio
    async def test_bounded_mailbox_drop_newest(self):
        """Test bounded mailbox with drop newest strategy"""
        dlq = DeadLetterQueue()
        mailbox = BoundedMailbox(
            max_size=3,
            back_pressure_strategy=BackPressureStrategy.DROP_NEWEST,
            dead_letter_queue=dlq,
        )

        # Fill mailbox
        for i in range(3):
            msg = ActorMessage(
                message_id=str(i),
                sender="test",
                recipient="test",
                message_type="test",
                payload={"id": i},
                timestamp=0,
            )
            result = await mailbox.put(msg)
            assert result is True

        # Try to add more - should be dropped
        msg = ActorMessage(
            message_id="dropped",
            sender="test",
            recipient="test",
            message_type="test",
            payload={"id": "dropped"},
            timestamp=0,
        )
        result = await mailbox.put(msg)
        assert result is False

        # Check DLQ
        dlq_messages = await dlq.get_all()
        assert len(dlq_messages) == 1
        assert dlq_messages[0]["message"].message_id == "dropped"

        # Check stats
        stats = mailbox.get_stats()
        assert stats["messages_dropped"] == 1


class TestPriorityMailbox:
    """Test priority-based message processing"""

    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        """Test messages are processed by priority"""
        mailbox = PriorityMailbox(
            max_size=10, starvation_prevention=False  # Disable for this test
        )

        # Add messages in reverse priority order
        priorities = [
            (MessagePriority.BULK, "bulk"),
            (MessagePriority.LOW, "low"),
            (MessagePriority.NORMAL, "normal"),
            (MessagePriority.HIGH, "high"),
            (MessagePriority.SYSTEM, "system"),
        ]

        for priority, name in priorities:
            msg = ActorMessage(
                message_id=name,
                sender="test",
                recipient="test",
                message_type="test",
                payload={"name": name},
                timestamp=0,
            )
            await mailbox.put(msg, priority)

        # Should get messages in priority order (SYSTEM first)
        expected_order = ["system", "high", "normal", "low", "bulk"]
        for expected in expected_order:
            msg = await mailbox.get()
            assert msg.payload["name"] == expected

    @pytest.mark.asyncio
    async def test_starvation_prevention(self):
        """Test that low priority messages eventually get processed"""
        mailbox = PriorityMailbox(max_size=20, starvation_prevention=True)

        # Set low starvation threshold for testing
        mailbox._starvation_threshold = 0.5  # 500ms

        # Add low priority message first
        low_msg = ActorMessage(
            message_id="low",
            sender="test",
            recipient="test",
            message_type="test",
            payload={"priority": "low"},
            timestamp=0,
        )
        await mailbox.put(low_msg, MessagePriority.LOW)

        # Wait to trigger starvation
        await asyncio.sleep(0.6)

        # Add high priority messages
        for i in range(5):
            high_msg = ActorMessage(
                message_id=f"high-{i}",
                sender="test",
                recipient="test",
                message_type="test",
                payload={"priority": "high"},
                timestamp=0,
            )
            await mailbox.put(high_msg, MessagePriority.HIGH)

        # Low priority should be served first due to starvation
        msg = await mailbox.get()
        assert msg.payload["priority"] == "low"


class TestPersistentMailbox:
    """Test mailbox persistence features"""

    @pytest.mark.asyncio
    async def test_persistence_and_recovery(self):
        """Test mailbox can persist and recover messages"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            persistence_path = tmp.name

        try:
            # Create mailbox and add messages
            mailbox1 = PersistentMailbox(
                max_size=10, persistence_path=persistence_path, persistence_interval=0.1
            )

            for i in range(5):
                msg = ActorMessage(
                    message_id=str(i),
                    sender="test",
                    recipient="test",
                    message_type="test",
                    payload={"id": i},
                    timestamp=0,
                )
                await mailbox1.put(msg)

            # Wait for persistence
            await asyncio.sleep(0.2)

            # Create new mailbox and restore
            mailbox2 = PersistentMailbox(max_size=10, persistence_path=persistence_path)

            restored = await mailbox2.restore_from_disk()
            assert restored == 5

            # Verify messages
            for i in range(5):
                msg = await mailbox2.get()
                assert msg.payload["id"] == i

        finally:
            # Cleanup
            Path(persistence_path).unlink(missing_ok=True)


class TestSequentialProcessing:
    """Test sequential processing guarantees"""

    @pytest.mark.asyncio
    async def test_no_race_conditions(self):
        """Test that sequential processing prevents race conditions"""

        class CounterActor(MailboxActor):
            def __init__(self, actor_id: str):
                super().__init__(actor_id, mailbox_type=MailboxType.BOUNDED)
                self.counter = 0
                self.register_handler("increment", self._increment)
                self.register_handler("get_count", self._get_count)

            async def _increment(self, msg):
                # Simulate some async work
                current = self.counter
                await asyncio.sleep(0.001)  # Would cause race condition if parallel
                self.counter = current + 1
                return {"count": self.counter}

            async def _get_count(self, msg):
                return {"count": self.counter}

        system = await get_global_actor_system()
        actor_ref = await system.create_actor(CounterActor, "counter-test")

        # Send 100 concurrent increment messages
        tasks = []
        for _ in range(100):
            tasks.append(actor_ref.tell("increment", {}))

        await asyncio.gather(*tasks)

        # Wait for processing
        await asyncio.sleep(0.5)

        # Check final count
        result = await actor_ref.ask("get_count", {})
        assert result["count"] == 100  # No race conditions!

        await system.stop_actor("counter-test")


class TestMailboxFactory:
    """Test mailbox factory functionality"""

    def test_create_unbounded(self):
        """Test creating unbounded mailbox"""
        mailbox = MailboxFactory.create_mailbox(MailboxType.UNBOUNDED)
        assert isinstance(mailbox, UnboundedMailbox)

    def test_create_bounded(self):
        """Test creating bounded mailbox"""
        mailbox = MailboxFactory.create_mailbox(
            MailboxType.BOUNDED,
            max_size=50,
            back_pressure_strategy=BackPressureStrategy.DROP_OLDEST,
        )
        assert isinstance(mailbox, BoundedMailbox)
        assert mailbox.max_size == 50
        assert mailbox.back_pressure_strategy == BackPressureStrategy.DROP_OLDEST

    def test_create_priority(self):
        """Test creating priority mailbox"""
        mailbox = MailboxFactory.create_mailbox(
            MailboxType.PRIORITY, max_size=100, starvation_prevention=True
        )
        assert isinstance(mailbox, PriorityMailbox)
        assert mailbox.starvation_prevention is True

    def test_create_persistent(self):
        """Test creating persistent mailbox"""
        mailbox = MailboxFactory.create_mailbox(
            MailboxType.PERSISTENT, persistence_path="/tmp/test.json"
        )
        assert isinstance(mailbox, PersistentMailbox)
        assert mailbox.persistence_path == "/tmp/test.json"


class TestMailboxActor:
    """Test MailboxActor functionality"""

    @pytest.mark.asyncio
    async def test_message_filtering(self):
        """Test message filtering capability"""

        class FilteredActor(MailboxActor):
            def __init__(self, actor_id: str):
                super().__init__(actor_id, mailbox_type=MailboxType.BOUNDED)
                self.received = []
                self.register_handler("process", self._process)

                # Add filter to only accept even IDs
                self.add_message_filter(lambda msg: msg.payload.get("id", 0) % 2 == 0)

            async def _process(self, msg):
                self.received.append(msg.payload["id"])
                return {"processed": msg.payload["id"]}

        system = await get_global_actor_system()
        actor_ref = await system.create_actor(FilteredActor, "filtered-test")

        # Send 10 messages
        for i in range(10):
            await actor_ref.tell("process", {"id": i})

        await asyncio.sleep(0.5)

        # Check only even IDs were processed
        actor = system.get_actor("filtered-test")
        assert sorted(actor.received) == [0, 2, 4, 6, 8]

        await system.stop_actor("filtered-test")

    @pytest.mark.asyncio
    async def test_batch_processing(self):
        """Test batch message processing"""

        class BatchActor(MailboxActor):
            def __init__(self, actor_id: str):
                super().__init__(
                    actor_id,
                    mailbox_type=MailboxType.BOUNDED,
                    mailbox_config={"batch_size": 5, "batch_timeout": 0.1},
                )
                self.batches_processed = []

            async def _process_message_batch(self, messages):
                """Override to handle batches"""
                batch_ids = [msg.payload["id"] for msg in messages]
                self.batches_processed.append(batch_ids)
                self._stats["messages_processed"] += len(messages)

        system = await get_global_actor_system()
        actor_ref = await system.create_actor(BatchActor, "batch-test")

        # Send 12 messages
        for i in range(12):
            await actor_ref.tell("process", {"id": i})

        await asyncio.sleep(1)

        # Check batches
        actor = system.get_actor("batch-test")
        # Should have processed 2 full batches of 5 and 1 partial batch of 2
        assert len(actor.batches_processed) == 3
        assert len(actor.batches_processed[0]) == 5
        assert len(actor.batches_processed[1]) == 5
        assert len(actor.batches_processed[2]) == 2

        await system.stop_actor("batch-test")


@pytest.mark.asyncio
async def test_integration_with_supervision():
    """Test mailbox integration with supervision system"""
    from core.supervision import SupervisionStrategy, SupervisorActor

    class WorkerWithPriorityMailbox(MailboxActor):
        def __init__(self, actor_id: str):
            super().__init__(
                actor_id,
                mailbox_type=MailboxType.PRIORITY,
                mailbox_config={"max_size": 50},
            )
            self.register_handler("work", self._work)
            self.register_handler("fail", self._fail)

        async def _work(self, msg):
            return {"result": "done"}

        async def _fail(self, msg):
            raise Exception("Simulated failure")

    system = await get_global_actor_system()

    # Create supervisor
    supervisor = await system.create_actor(
        SupervisorActor,
        "mailbox-supervisor",
        supervision_strategy=SupervisionStrategy(max_failures=3),
    )

    # Create worker and supervise it
    worker_ref = await system.create_actor(WorkerWithPriorityMailbox, "priority-worker")

    # Tell supervisor to supervise the worker
    await supervisor.tell("supervise_child", {"child_ref": worker_ref})

    # Test that it works
    result = await worker_ref.ask("work", {})
    assert result["result"] == "done"

    # Test failure handling
    await worker_ref.tell("fail", {})
    await asyncio.sleep(0.5)

    # Worker should be restarted and still functional
    result = await worker_ref.ask("work", {})
    assert result["result"] == "done"

    await system.stop()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
