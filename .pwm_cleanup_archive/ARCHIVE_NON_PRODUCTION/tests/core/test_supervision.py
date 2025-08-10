"""
Comprehensive tests for the Actor Supervision System.

This suite tests:
- Supervision strategies and deciders
- Supervisor actor behavior (creation, failure handling)
- Circuit breaker functionality
- Root supervisor and system-wide policies
"""

import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from core.actor_system import (
    Actor,
)
from core.supervision import (
    AllForOneStrategy,
    CircuitBreaker,
    DefaultSupervisionDecider,
    FailureInfo,
    OneForOneStrategy,
    RestartPolicy,
    RestForOneStrategy,
    RootSupervisor,
    SupervisionDirective,
    SupervisionStrategy,
    SupervisorActor,
)


# A simple worker actor for testing
class WorkerActor(Actor):
    def __init__(self, actor_id, *args, **kwargs):
        super().__init__(actor_id)
        self.state = "initial"
        self.register_handler("work", self.work)
        self.register_handler("fail", self.fail)
        self.register_handler("get_state", self.get_state)

    async def work(self, message):
        self.state = message.payload.get("new_state", "working")
        return {"status": "done"}

    async def fail(self, message):
        raise ValueError("I was told to fail")

    async def get_state(self, message):
        return {"state": self.state}


@pytest.fixture
def event_loop():
    """Create a new event loop for each test."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def actor_system(event_loop):
    """A fresh actor system for each test function."""
    system = ActorSystem()
    await system.start()
    return system


class TestSupervisionStrategy:
    def test_calculate_restart_delay(self):
        strategy = SupervisionStrategy(
            restart_delay=0.1, backoff_multiplier=2.0, max_restart_delay=1.0
        )
        assert strategy.calculate_restart_delay(1) == 0.1
        assert strategy.calculate_restart_delay(2) == 0.2
        assert strategy.calculate_restart_delay(3) == 0.4
        assert strategy.calculate_restart_delay(4) == 0.8
        assert strategy.calculate_restart_delay(5) == 1.0  # Capped at max
        assert strategy.calculate_restart_delay(6) == 1.0  # Stays at max

    def test_rest_for_one_strategy(self):
        strategy = RestForOneStrategy(SupervisionStrategy())
        strategy.register_child("child-1")
        strategy.register_child("child-2")
        strategy.register_child("child-3")

        affected = strategy.get_affected_children("child-2")
        assert affected == ["child-2", "child-3"]

        affected_first = strategy.get_affected_children("child-1")
        assert affected_first == ["child-1", "child-2", "child-3"]

        affected_last = strategy.get_affected_children("child-3")
        assert affected_last == ["child-3"]

        affected_unknown = strategy.get_affected_children("unknown")
        assert affected_unknown == ["unknown"]


@pytest.mark.asyncio
class TestDefaultSupervisionDecider:
    async def test_restart_on_failure(self):
        strategy = SupervisionStrategy(restart_policy=RestartPolicy.ON_FAILURE)
        decider = DefaultSupervisionDecider(strategy)
        failure = FailureInfo("test-actor", Exception("test"), time.time(), 1)

        directive = await decider.decide(failure)
        assert directive == SupervisionDirective.RESTART

    async def test_stop_on_max_failures(self):
        strategy = SupervisionStrategy(max_failures=2, within_time_window=10)
        decider = DefaultSupervisionDecider(strategy)

        failure1 = FailureInfo("test-actor", Exception("fail1"), time.time(), 1)
        await decider.decide(failure1)

        failure2 = FailureInfo("test-actor", Exception("fail2"), time.time(), 2)
        await decider.decide(failure2)

        failure3 = FailureInfo("test-actor", Exception("fail3"), time.time(), 3)
        directive = await decider.decide(failure3)

        assert directive == SupervisionDirective.STOP

    async def test_failure_window_resets(self):
        strategy = SupervisionStrategy(max_failures=2, within_time_window=0.1)
        decider = DefaultSupervisionDecider(strategy)

        failure1 = FailureInfo("test-actor", Exception("fail1"), time.time(), 1)
        await decider.decide(failure1)

        await asyncio.sleep(0.15)

        failure2 = FailureInfo("test-actor", Exception("fail2"), time.time(), 2)
        directive = await decider.decide(failure2)

        assert directive == SupervisionDirective.RESTART  # Should not stop


class TestCircuitBreaker:
    def test_initial_state_is_closed(self):
        cb = CircuitBreaker()
        assert cb.state == "closed"
        assert cb.can_proceed() is True

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "closed"
        cb.record_failure()
        assert cb.state == "open"
        assert cb.can_proceed() is False

    @pytest.mark.asyncio
    async def test_half_open_state(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=0.1)
        for _ in range(3):
            cb.record_failure()

        assert cb.state == "open"
        await asyncio.sleep(0.15)  # Wait for reset timeout

        assert cb.can_proceed() is True
        assert cb.state == "half_open"

    @pytest.mark.asyncio
    async def test_closes_from_half_open_after_success(self):
        cb = CircuitBreaker(
            failure_threshold=3, reset_timeout=0.1, half_open_requests=2
        )
        for _ in range(3):
            cb.record_failure()

        await asyncio.sleep(0.15)

        assert cb.can_proceed() is True
        assert cb.state == "half_open"
        cb.record_success()
        assert cb.state == "half_open"
        cb.record_success()
        assert cb.state == "closed"

    @pytest.mark.asyncio
    async def test_opens_from_half_open_after_failure(self):
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=0.1)
        for _ in range(3):
            cb.record_failure()

        await asyncio.sleep(0.15)

        assert cb.can_proceed() is True
        assert cb.state == "half_open"
        cb.record_failure()
        assert cb.state == "open"


@pytest.mark.asyncio
class TestSupervisorActor:
    async def test_create_child(self, actor_system):
        supervisor = await actor_system.create_actor(SupervisorActor, "supervisor-1")
        child_ref = await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-1"}
        )

        assert child_ref is not None
        assert "worker-1" in supervisor.children

        worker_actor = actor_system.get_actor("worker-1")
        assert worker_actor is not None
        assert worker_actor.supervisor.actor_id == "supervisor-1"

    async def test_one_for_one_restart(self, actor_system):
        strategy = SupervisionStrategy(max_failures=3, restart_delay=0.01)
        supervisor = await actor_system.create_actor(
            SupervisorActor,
            "supervisor-1",
            supervision_strategy=strategy,
            supervision_decider=OneForOneStrategy(strategy),
        )

        child_ref = await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-1"}
        )

        # Change state
        await child_ref.tell("work", {"new_state": "dirty"})
        state_before_fail = await child_ref.ask("get_state", {})
        assert state_before_fail["state"] == "dirty"

        # Tell it to fail
        await child_ref.tell("fail", {})
        await asyncio.sleep(0.1)  # Give time for restart

        # Check it was restarted
        state_after_fail = await child_ref.ask("get_state", {})
        assert state_after_fail["state"] == "initial"  # State is reset

        supervisor_actor = actor_system.get_actor("supervisor-1")
        child_meta = supervisor_actor.child_metadata["worker-1"]
        assert child_meta["restart_count"] == 1

    async def test_all_for_one_stop(self, actor_system):
        strategy = SupervisionStrategy(restart_policy=RestartPolicy.NEVER)
        supervisor = await actor_system.create_actor(
            SupervisorActor,
            "supervisor-1",
            supervision_strategy=strategy,
            supervision_decider=AllForOneStrategy(),
        )

        child1_ref = await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-1"}
        )
        child2_ref = await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-2"}
        )

        # Fail one child
        await child1_ref.tell("fail", {})
        await asyncio.sleep(0.1)

        # Both children should be stopped
        assert actor_system.get_actor("worker-1") is None
        assert actor_system.get_actor("worker-2") is None
        assert not supervisor.children

    async def test_rest_for_one_strategy_integration(self, actor_system):
        strategy = SupervisionStrategy(restart_policy=RestartPolicy.NEVER)
        decider = RestForOneStrategy(strategy)
        supervisor = await actor_system.create_actor(
            SupervisorActor,
            "supervisor-1",
            supervision_strategy=strategy,
            supervision_decider=decider,
        )

        # Important: decider needs to know about children as they are created.
        # The supervisor actor does this automatically.
        child1_ref = await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-1"}
        )
        child2_ref = await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-2"}
        )
        child3_ref = await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-3"}
        )

        # Fail the middle child
        await child2_ref.tell("fail", {})
        await asyncio.sleep(0.1)

        # worker-1 should still be running
        assert actor_system.get_actor("worker-1") is not None
        # worker-2 and worker-3 should be stopped
        assert actor_system.get_actor("worker-2") is None
        assert actor_system.get_actor("worker-3") is None

        assert "worker-1" in supervisor.children
        assert "worker-2" not in supervisor.children
        assert "worker-3" not in supervisor.children

    async def test_stop_on_max_failures(self, actor_system):
        strategy = SupervisionStrategy(max_failures=2, restart_delay=0.01)
        supervisor = await actor_system.create_actor(
            SupervisorActor, "supervisor-1", supervision_strategy=strategy
        )

        child_ref = await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-1"}
        )

        # Fail twice (should restart)
        await child_ref.tell("fail", {})
        await asyncio.sleep(0.1)
        await child_ref.tell("fail", {})
        await asyncio.sleep(0.1)

        # Fail a third time (should stop)
        await child_ref.tell("fail", {})
        await asyncio.sleep(0.1)

        assert actor_system.get_actor("worker-1") is None
        assert "worker-1" not in supervisor.children

    async def test_escalate_failure(self, actor_system):
        # Mock decider to always escalate
        class EscalatingDecider(DefaultSupervisionDecider):
            async def decide(self, failure: FailureInfo) -> SupervisionDirective:
                return SupervisionDirective.ESCALATE

        # Create a grand-parent supervisor
        grand_supervisor = await actor_system.create_actor(
            SupervisorActor, "grand-supervisor-1"
        )

        # Create parent supervisor under grand-parent
        parent_ref = await grand_supervisor.ask(
            "create_child",
            {
                "child_class": SupervisorActor,
                "child_id": "parent-supervisor-1",
                "supervision_decider": EscalatingDecider(SupervisionStrategy()),
            },
        )

        # Create child under parent
        child_ref = await parent_ref.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-1"}
        )

        # Mock the grand-supervisor's failure handling
        grand_supervisor_actor = actor_system.get_actor("grand-supervisor-1")
        grand_supervisor_actor._handle_child_failure = AsyncMock()

        # Fail the child, which should escalate to the parent, then to the grand-parent
        await child_ref.tell("fail", {})
        await asyncio.sleep(0.1)

        # Check that the grand-parent's failure handler was called
        grand_supervisor_actor._handle_child_failure.assert_called_once()
        call_args = grand_supervisor_actor._handle_child_failure.call_args[0][0]
        assert call_args.payload["child_id"] == "parent-supervisor-1"
        assert "Escalated from child worker-1" in call_args.payload["error"]

    async def test_supervision_stats(self, actor_system):
        supervisor = await actor_system.create_actor(SupervisorActor, "supervisor-1")
        await supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-1"}
        )

        stats = await supervisor.ask("get_supervision_stats", {})

        assert stats["supervisor_id"] == "supervisor-1"
        assert stats["children_count"] == 1
        assert "worker-1" in stats["children"]


@pytest.mark.asyncio
class TestRootSupervisor:
    async def test_root_supervisor_creation(self, actor_system):
        root_supervisor = await actor_system.create_actor(
            RootSupervisor, "root-supervisor"
        )
        assert root_supervisor is not None
        assert root_supervisor.actor_id == "root-supervisor"

        # Check default strategy
        supervisor_actor = actor_system.get_actor("root-supervisor")
        assert supervisor_actor.supervision_strategy.max_failures == 10
        assert (
            supervisor_actor.supervision_strategy.restart_policy == RestartPolicy.ALWAYS
        )

    async def test_graceful_shutdown(self, actor_system):
        root_supervisor = await actor_system.create_actor(
            RootSupervisor, "root-supervisor"
        )

        # Create some children
        await root_supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-1"}
        )
        await root_supervisor.ask(
            "create_child", {"child_class": WorkerActor, "child_id": "worker-2"}
        )

        assert actor_system.get_actor("worker-1") is not None
        assert actor_system.get_actor("worker-2") is not None

        # Trigger shutdown
        await root_supervisor.tell("system_shutdown", {})
        await asyncio.sleep(0.1)

        # All children should be stopped
        assert actor_system.get_actor("worker-1") is None
        assert actor_system.get_actor("worker-2") is None
        assert not root_supervisor.children


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
