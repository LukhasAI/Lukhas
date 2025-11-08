import asyncio
import threading
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from core.utils.orchestration_energy_aware_execution_planner import (
    DistributedEnergyTask,
    EnergyAwareExecutionPlanner,
    EnergyBudget,
    EnergyProfile,
    EnergyTask,
    Priority,
    create_eaxp_instance,
)


@pytest.fixture
def planner():
    """Provides a default EnergyAwareExecutionPlanner instance for tests."""
    config = {
        "total_energy_capacity": 1000.0,
        "initial_energy": 800.0,
        "critical_reserve": 100.0,
        "maintenance_reserve": 50.0,
        "peak_consumption_rate": 50.0,
        "regeneration_rate": 10.0,
        "max_concurrent_tasks": 2,
        "energy_monitoring_interval": 0.1,
        "optimization_interval": 60.0,
        "efficiency_target": 0.8,
        "adaptive_learning": True,
        "bio_integration": False,
        "energy_profiles": {
            EnergyProfile.MINIMAL: {"multiplier": 0.5, "max_duration": 3600},
            EnergyProfile.STANDARD: {"multiplier": 1.0, "max_duration": 1800},
            EnergyProfile.INTENSIVE: {"multiplier": 2.0, "max_duration": 600},
            EnergyProfile.BURST: {"multiplier": 3.0, "max_duration": 60},
            EnergyProfile.CONSERVATION: {"multiplier": 0.3, "max_duration": 7200},
            EnergyProfile.ADAPTIVE: {"multiplier": 1.0, "max_duration": 1800},
        },
    }
    planner_instance = EnergyAwareExecutionPlanner(config)
    yield planner_instance
    # Ensure executor is shut down even if tests fail
    if not planner_instance.executor._shutdown:
        planner_instance.executor.shutdown(wait=True)


def test_planner_initialization(planner):
    """Tests that the planner initializes with the correct configuration."""
    assert planner.is_running is False
    assert planner.energy_budget.total_capacity == 1000.0
    assert planner.energy_budget.current_available == 800.0


def test_submit_valid_task(planner):
    """Tests that a valid task can be submitted and is added to the queue."""
    task = EnergyTask(
        task_id="test_task_1",
        name="Test Task",
        priority=Priority.NORMAL,
        estimated_energy=50.0,
        max_energy=75.0,
        estimated_duration=10.0,
    )
    task_id = planner.submit_task(task)
    assert task_id == "test_task_1"
    assert len(planner.task_queue) == 1
    assert planner.task_queue[0].task_id == "test_task_1"


def test_submit_invalid_task_raises_error(planner):
    """Tests that submitting a task with invalid parameters raises a ValueError."""
    with pytest.raises(ValueError, match="Estimated energy must be positive"):
        EnergyTask(
            task_id="invalid_task",
            name="Invalid Task",
            priority=Priority.NORMAL,
            estimated_energy=0,
            max_energy=50.0,
            estimated_duration=5.0,
        )


def test_cancel_queued_task(planner):
    """Tests that a queued task can be successfully canceled."""
    task = EnergyTask(
        task_id="cancel_task_1",
        name="Task to be Canceled",
        priority=Priority.LOW,
        estimated_energy=20.0,
        max_energy=30.0,
        estimated_duration=5.0,
    )
    planner.submit_task(task)
    assert len(planner.task_queue) == 1
    assert planner.cancel_task("cancel_task_1") is True
    assert len(planner.task_queue) == 0


def test_get_task_status_queued(planner):
    """Tests retrieving the status of a queued task."""
    task = EnergyTask(
        task_id="status_task_1",
        name="Status Task",
        priority=Priority.NORMAL,
        estimated_energy=50.0,
        max_energy=75.0,
        estimated_duration=10.0,
    )
    planner.submit_task(task)
    status = planner.get_task_status("status_task_1")
    assert status["status"] == "queued"
    assert status["queue_position"] == 0


@pytest.mark.asyncio
async def test_task_execution_and_stop(planner):
    """Tests the full lifecycle of a task and graceful shutdown."""
    callback = MagicMock(return_value={"data": "result"})
    task = EnergyTask(
        task_id="exec_task_1",
        name="Execution Task",
        priority=Priority.NORMAL,
        estimated_energy=100.0,
        max_energy=150.0,
        estimated_duration=0.1,
        callback=callback,
    )
    planner.submit_task(task)

    planner.is_running = True
    execution_task = asyncio.create_task(planner._execution_loop())

    # Allow time for the task to be processed
    await asyncio.sleep(0.5)

    assert len(planner.completed_tasks) == 1
    assert planner.completed_tasks[0]["task_id"] == "exec_task_1"
    callback.assert_called_once()

    # Now stop the planner
    await planner.stop()

    # The loop should terminate because is_running is now False
    await asyncio.sleep(0.2)
    assert execution_task.done()


def test_energy_budget_allocation(planner):
    """Tests that energy is correctly allocated and tracked."""
    initial_energy = planner.energy_budget.current_available
    task = EnergyTask(
        task_id="energy_task",
        name="Energy Task",
        priority=Priority.NORMAL,
        estimated_energy=100.0,
        max_energy=150.0,
        estimated_duration=1.0,
    )
    planner._allocate_energy(task)
    assert planner.energy_budget.current_available == initial_energy - 100.0


def test_priority_scheduling(planner):
    """Tests that tasks are inserted into the queue based on priority."""
    low_task = EnergyTask("low", "Low", Priority.LOW, 10, 15, 1)
    high_task = EnergyTask("high", "High", Priority.HIGH, 10, 15, 1)
    normal_task = EnergyTask("normal", "Normal", Priority.NORMAL, 10, 15, 1)

    planner.submit_task(low_task)
    planner.submit_task(high_task)
    planner.submit_task(normal_task)

    assert len(planner.task_queue) == 3
    assert planner.task_queue[0].task_id == "high"
    assert planner.task_queue[1].task_id == "normal"
    assert planner.task_queue[2].task_id == "low"


def test_get_energy_metrics(planner):
    """Tests that energy metrics are calculated correctly."""
    planner.energy_metrics.tasks_completed = 10
    planner.energy_metrics.tasks_failed = 2
    planner.energy_metrics.total_consumed = 500
    metrics = planner.get_energy_metrics()

    assert metrics["task_metrics"]["tasks_completed"] == 10
    assert metrics["task_metrics"]["tasks_failed"] == 2
    assert metrics["task_metrics"]["success_rate"] == 10 / 12
    assert metrics["consumption_metrics"]["total_consumed"] == 500


def test_analyze_task_queue(planner):
    """Tests analysis of the task queue."""
    now = datetime.now(timezone.utc)
    task1 = EnergyTask("1", "1", Priority.NORMAL, 10, 15, 1, created_at=now - timedelta(seconds=10))
    task2 = EnergyTask("2", "2", Priority.LOW, 10, 15, 1, created_at=now - timedelta(seconds=20))
    planner.task_queue.append(task1)
    planner.task_queue.append(task2)

    analysis = planner._analyze_task_queue()
    assert analysis["queue_length"] == 2
    assert analysis["average_wait_time"] == pytest.approx(15.0, rel=1e-3)


def test_calculate_efficiency_metrics(planner):
    """Tests the calculation of efficiency metrics."""
    planner.completed_tasks = [
        {"energy_consumed": 100},
        {"energy_consumed": 120},
    ]
    metrics = planner._calculate_efficiency_metrics()
    assert "efficiency_score" in metrics


def test_optimize_energy_allocation_high_energy(planner):
    """Tests for performance_boost recommendation with high energy."""
    planner.energy_budget.current_available = 900  # Results in < 30% utilization
    optimization = planner.optimize_energy_allocation()
    assert any(rec["type"] == "performance_boost" for rec in optimization["recommendations"])


def test_optimize_energy_allocation_long_wait(planner):
    """Tests for queue_optimization recommendation with long wait times."""
    with patch.object(planner, "_analyze_task_queue", return_value={"average_wait_time": 400}):
        optimization = planner.optimize_energy_allocation()
        assert any(rec["type"] == "queue_optimization" for rec in optimization["recommendations"])


def test_optimize_energy_allocation_low_efficiency(planner):
    """Tests for efficiency_improvement recommendation with low efficiency."""
    with patch.object(planner, "_calculate_efficiency_metrics", return_value={"efficiency_score": 0.5}):
        optimization = planner.optimize_energy_allocation()
        assert any(rec["type"] == "efficiency_improvement" for rec in optimization["recommendations"])


@pytest.mark.asyncio
async def test_energy_regeneration_with_monitor_thread(planner):
    """Tests energy regeneration via the monitor thread."""
    initial_energy = planner.energy_budget.current_available

    planner.is_running = True
    monitor_thread = threading.Thread(target=planner._energy_monitor_loop, daemon=True)
    monitor_thread.start()

    await asyncio.sleep(0.5)  # Let the monitor thread run

    planner.is_running = False
    monitor_thread.join(timeout=1.0)

    assert planner.energy_budget.current_available > initial_energy


def test_task_deadline_passed(planner):
    """Tests that a task with a passed deadline is not started."""
    task = EnergyTask(
        "deadline_task", "Deadline Task", Priority.NORMAL, 10, 20, 1,
        deadline=datetime.now(timezone.utc) - timedelta(seconds=1)
    )
    assert not planner._can_start_task(task)


def test_task_dependency_not_satisfied(planner):
    """Tests that a task with an unsatisfied dependency is not started."""
    task = EnergyTask(
        "dep_task", "Dependency Task", Priority.NORMAL, 10, 20, 1,
        dependencies=["unmet_dep"]
    )
    assert not planner._can_start_task(task)


def test_task_dependency_satisfied(planner):
    """Tests that a task with a satisfied dependency can be started."""
    planner.completed_tasks.append({"task_id": "met_dep"})
    task = EnergyTask(
        "dep_task", "Dependency Task", Priority.NORMAL, 10, 20, 1,
        dependencies=["met_dep"]
    )
    assert planner._can_start_task(task)


def test_get_task_status_not_found(planner):
    """Tests getting status for a non-existent task."""
    status = planner.get_task_status("non_existent_task")
    assert status["status"] == "not_found"


@pytest.mark.asyncio
async def test_task_failure(planner):
    """Tests that a failing task is handled correctly."""
    callback = MagicMock(side_effect=Exception("Task failed"))
    task = EnergyTask("fail_task", "Failing Task", Priority.NORMAL, 50, 75, 0.1, callback=callback)

    planner.submit_task(task)

    planner.is_running = True
    execution_task = asyncio.create_task(planner._execution_loop())
    await asyncio.sleep(0.5)

    assert len(planner.failed_tasks) == 1
    assert planner.failed_tasks[0]["task_id"] == "fail_task"
    assert "Task failed" in planner.failed_tasks[0]["error"]

    await planner.stop()
    await asyncio.sleep(0.2)
    assert execution_task.done()


def test_adaptive_optimizations(planner):
    """Tests adaptive optimizations for task concurrency."""
    # Low efficiency case
    planner._apply_adaptive_optimizations({"efficiency_score": 0.5})
    assert planner.config["max_concurrent_tasks"] == 1

    # High efficiency case
    planner.config["max_concurrent_tasks"] = 2 # Reset
    planner.energy_budget.current_available = 800
    planner._apply_adaptive_optimizations({"efficiency_score": 0.95})
    assert planner.config["max_concurrent_tasks"] == 3


def test_create_eaxp_instance():
    """Tests the factory function for creating a planner instance."""
    planner = create_eaxp_instance()
    assert isinstance(planner, EnergyAwareExecutionPlanner)


def test_get_task_status_running_and_failed(planner):
    """Tests getting the status of running and failed tasks."""
    # Mock a running task
    future = MagicMock()
    future.done.return_value = False
    future.cancelled.return_value = False
    planner.running_tasks["running_task"] = future

    status_running = planner.get_task_status("running_task")
    assert status_running["status"] == "running"

    # Add a failed task
    planner.failed_tasks.append({"task_id": "failed_task", "error": "it broke"})
    status_failed = planner.get_task_status("failed_task")
    assert status_failed["status"] == "failed"
    assert status_failed["error"] == "it broke"


def test_insufficient_energy_prevents_start(planner):
    """Tests that a task is not started if there is not enough energy."""
    planner.energy_budget.current_available = 50
    task = EnergyTask("energy_hog", "Energy Hog", Priority.NORMAL, 100, 150, 1)
    assert not planner._can_start_task(task)


def test_apply_energy_profile(planner):
    """Tests that energy profiles are applied correctly."""
    task = EnergyTask("profile_task", "Profile Task", Priority.NORMAL, 100, 150, 1,
                      energy_profile=EnergyProfile.INTENSIVE)

    profiled_task = planner._apply_energy_profile(task)

    assert profiled_task.estimated_energy == 200 # Intensive multiplier is 2.0
    assert profiled_task.max_energy == 300


def test_default_config():
    """Tests that a planner can be initialized with a default config."""
    planner = EnergyAwareExecutionPlanner()
    assert planner.config["total_energy_capacity"] == 1000.0


def test_get_priority_distribution(planner):
    """Tests the priority distribution calculation."""
    planner.task_queue.append(EnergyTask("1", "1", Priority.NORMAL, 10, 15, 1))
    planner.task_queue.append(EnergyTask("2", "2", Priority.HIGH, 10, 15, 1))
    planner.task_queue.append(EnergyTask("3", "3", Priority.NORMAL, 10, 15, 1))
    dist = planner._get_priority_distribution()
    assert dist == {"NORMAL": 2, "HIGH": 1}


def test_update_energy_metrics(planner):
    """Tests the energy metrics update."""
    planner.energy_history.append({"utilization": 0.5})
    planner.energy_history.append({"utilization": 0.7})
    planner._update_energy_metrics()
    assert planner.energy_metrics.average_utilization == 0.6
    assert planner.energy_metrics.peak_utilization == 0.7


def test_estimate_completion_and_start_time(planner):
    """Tests time estimation functions."""
    assert planner._estimate_completion_time("any_task") is not None
    assert planner._estimate_start_time(1) is not None


def test_submit_task_no_id_raises_error(planner):
    """Tests that submitting a task with no ID raises a ValueError."""
    with pytest.raises(ValueError, match="Task ID is required"):
        task = EnergyTask(
            task_id="", name="No ID", priority=Priority.NORMAL,
            estimated_energy=10, max_energy=15, estimated_duration=1
        )
        planner.submit_task(task)

def test_energy_task_post_init():
    """Tests the __post_init__ method of the EnergyTask dataclass."""
    # Test that max_energy is adjusted if it's less than estimated_energy
    task = EnergyTask("task1", "Test Task", Priority.NORMAL, 100, 80, 10)
    assert task.max_energy == 150.0

def test_energy_budget_can_allocate():
    """Tests the can_allocate method of the EnergyBudget dataclass."""
    budget = EnergyBudget(1000, 800, 100, 50, 50, 10)
    assert budget.can_allocate(50, Priority.NORMAL) is True
    assert budget.can_allocate(700, Priority.NORMAL) is False
    assert budget.can_allocate(700, Priority.CRITICAL) is True
    assert budget.can_allocate(900, Priority.CRITICAL) is False

def test_distributed_energy_task_dataclass():
    """Tests the DistributedEnergyTask dataclass methods."""
    # Test __post_init__
    dist_task = DistributedEnergyTask("dist_task", "Distributed Task", Priority.NORMAL, 200, 20)
    assert dist_task.total_energy_budget == 200

    # Test estimate_total_energy
    dist_task.node_requirements = {"node1": 100, "node2": 150}
    assert dist_task.estimate_total_energy() == 250

    # Test get_node_allocation
    allocation = dist_task.get_node_allocation(["node1", "node3"])
    assert allocation == {"node1": 100}

    dist_task.node_requirements = {}
    allocation = dist_task.get_node_allocation(["node1", "node2", "node3"])
    assert len(allocation) == 3
    assert all(val == 200/3 for val in allocation.values())

    # Test can_execute_on_nodes
    dist_task.minimum_nodes = 2
    dist_task.maximum_nodes = 4
    assert dist_task.can_execute_on_nodes(1) is False
    assert dist_task.can_execute_on_nodes(3) is True
    assert dist_task.can_execute_on_nodes(5) is False
