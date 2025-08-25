"""
Colony System Canary Tests
Validates distributed colony functionality
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_colony_imports():
    """Test that colony modules can be imported"""
    from candidate.accepted import colonies
    assert colonies is not None
    assert hasattr(colonies, '__trinity__')

def test_colony_registry():
    """Test colony registry functionality"""
    from candidate.accepted.colonies.base import get_colony_registry

    registry = get_colony_registry()
    assert registry is not None

    # Should start empty
    initial_colonies = registry.get_all_colonies()

    # Test system status
    status = registry.get_system_status()
    assert "total_colonies" in status
    assert "active_colonies" in status

def test_governance_colony():
    """Test governance colony operations"""
    from candidate.accepted.colonies.governance import get_governance_colony

    colony = get_governance_colony()
    assert colony.name == "governance"
    assert colony.drift_threshold == 0.15

    # Test ethics check
    operation = {
        "id": "test_op",
        "involves_user_data": True,
        "user_consent": True,
        "involves_decision_making": False
    }

    task = colony.submit_task("ethics_check", operation)
    assert task is not None

    # Process the task
    results = colony.process_queue()
    assert results["processed"] > 0

    # Check if task completed
    assert task.id in colony.completed_tasks
    result = colony.completed_tasks[task.id].result
    assert "ethics_score" in result
    assert "approved" in result

def test_reasoning_colony():
    """Test reasoning colony operations"""
    from candidate.accepted.colonies.reasoning import get_reasoning_colony

    colony = get_reasoning_colony()
    assert colony.name == "reasoning"

    # Test logical inference
    premises = {
        "facts": ["A->B", "B->C", "A"],
        "rules": [],
        "query": "C"
    }

    task = colony.submit_task("logical_inference", premises)
    assert task is not None

    # Process the task
    colony.process_queue()

    # Check result
    if task.id in colony.completed_tasks:
        result = colony.completed_tasks[task.id].result
        assert "conclusion" in result
        assert "confidence" in result

def test_memory_colony():
    """Test memory colony operations"""
    from candidate.accepted.colonies.memory import get_memory_colony

    colony = get_memory_colony()
    assert colony.name == "memory"

    # Test memory storage
    task = colony.submit_task("store_memory", {"data": "test memory"})
    colony.process_queue()

    if task.id in colony.completed_tasks:
        result = colony.completed_tasks[task.id].result
        assert result["stored"] is True
        assert "memory_id" in result

def test_consciousness_colony():
    """Test consciousness colony operations"""
    from candidate.accepted.colonies.consciousness import get_consciousness_colony

    colony = get_consciousness_colony()
    assert colony.name == "consciousness"
    assert colony.awareness_level > 0

    # Test awareness check
    task = colony.submit_task("awareness_check", {})
    colony.process_queue()

    if task.id in colony.completed_tasks:
        result = colony.completed_tasks[task.id].result
        assert "awareness_level" in result
        assert "state" in result

def test_orchestrator_colony():
    """Test orchestrator colony coordination"""
    from candidate.accepted.colonies.orchestrator import get_orchestrator_colony

    orchestrator = get_orchestrator_colony()
    assert orchestrator.name == "orchestrator"

    # Test system status
    task = orchestrator.submit_task("system_status", {})
    orchestrator.process_queue()

    if task.id in orchestrator.completed_tasks:
        result = orchestrator.completed_tasks[task.id].result
        assert "total_colonies" in result
        assert "active_colonies" in result

def test_multi_colony_workflow():
    """Test workflow across multiple colonies"""
    from candidate.accepted.colonies.governance import get_governance_colony
    from candidate.accepted.colonies.memory import get_memory_colony
    from candidate.accepted.colonies.orchestrator import get_orchestrator_colony

    # Ensure colonies are initialized
    governance = get_governance_colony()
    memory = get_memory_colony()
    orchestrator = get_orchestrator_colony()

    # Define a multi-step workflow
    workflow = {
        "steps": [
            {
                "colony": "memory",
                "task_type": "store_memory",
                "payload": {"data": "workflow test data"}
            },
            {
                "colony": "governance",
                "task_type": "ethics_check",
                "payload": {"id": "workflow_op", "involves_user_data": False}
            }
        ]
    }

    # Execute workflow
    task = orchestrator.submit_task("execute_workflow", workflow)
    orchestrator.process_queue()

    if task.id in orchestrator.completed_tasks:
        result = orchestrator.completed_tasks[task.id].result
        assert "workflow_id" in result
        assert result["status"] in ["completed", "running"]

def test_trinity_integration():
    """Test Trinity Framework integration across colonies"""
    from candidate.accepted.colonies import trinity_sync

    sync_result = trinity_sync()
    assert sync_result['identity'] == '⚛️'
    assert sync_result['consciousness'] == '🧠'
    assert sync_result['guardian'] == '🛡️'
    assert 'colony_sync' in sync_result
    assert sync_result['total_colonies'] > 0

def test_task_routing():
    """Test task routing through registry"""
    from candidate.accepted.colonies.base import get_colony_registry

    registry = get_colony_registry()

    # Submit a task that should be routed to governance
    task = registry.submit_task("ethics_check", {"test": "data"})

    # Task should be created and routed
    assert task is not None
    assert task.task_type == "ethics_check"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
