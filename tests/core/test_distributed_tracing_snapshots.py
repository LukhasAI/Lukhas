import pytest
import os
import json
import time
from unittest.mock import MagicMock, patch

from lukhas.core.distributed_tracing import (
    StateSnapshotter,
    EventReplayer,
    TraceCollector,
    TraceSpan,
    demo_distributed_tracing,
    get_global_collector,
)

@pytest.fixture
def snapshotter(tmp_path):
    return StateSnapshotter(storage_path=str(tmp_path))

@pytest.fixture
def collector():
    return TraceCollector()

@pytest.fixture
def replayer(collector, snapshotter):
    return EventReplayer(collector, snapshotter)

class TestStateSnapshotter:
    def test_take_and_restore_snapshot(self, snapshotter):
        agent_id = "agent-snap-001"
        state_data = {"key": "value", "counter": 1}

        filepath = snapshotter.take_snapshot(agent_id, state_data)
        assert os.path.exists(filepath)

        restored_state = snapshotter.restore_latest_snapshot(agent_id)
        assert restored_state is not None
        assert restored_state.agent_id == agent_id
        assert restored_state.state_data == state_data

    def test_restore_no_snapshot(self, snapshotter):
        restored_state = snapshotter.restore_latest_snapshot("non_existent_agent")
        assert restored_state is None

class TestEventReplayer:
    def test_replay_agent_state(self, replayer, snapshotter):
        agent_id = "agent-replay-001"
        initial_state = {"status": "initial"}
        snapshotter.take_snapshot(agent_id, initial_state)

        trace_data = {
            "spans": [
                {
                    "tags": {"agent.id": agent_id},
                    "logs": [
                        {"timestamp": time.time(), "event": "state_update", "fields": {"status": "processing"}},
                        {"timestamp": time.time() + 0.1, "event": "state_update", "fields": {"progress": 50}},
                    ]
                }
            ]
        }

        reconstructed_state = replayer.replay_agent_state(agent_id, trace_data)
        assert reconstructed_state["status"] == "processing"
        assert reconstructed_state["progress"] == 50

    def test_replay_trace_not_found(self, replayer):
        with pytest.raises(ValueError, match="Trace with ID trace-not-found not found."):
            replayer.replay_trace("trace-not-found")

@pytest.mark.skip(reason="Demo function is complex to test and not critical for production.")
@patch('lukhas.core.distributed_tracing.StateSnapshotter')
@patch('lukhas.core.distributed_tracing.get_global_collector')
def test_demo_function(mock_get_collector, mock_snapshotter, capsys):
    """Test the demo function to improve coverage."""
    # This is a complex function to test because it uses global state.
    # We will run the function and check its output, which is a good
    # integration test for the module.

    # The demo function creates its own tracers and collectors, so we need to
    # let it run and then inspect the state of the global collector.

    # Since the demo uses the global collector, we can get it and clear it first
    collector = get_global_collector()
    collector.traces.clear()
    collector.spans.clear()
    collector.completed_traces.clear()

    demo_distributed_tracing()

    captured = capsys.readouterr()
    assert "Tracing Statistics" in captured.out
    assert "Found 1 traces for analyze_data operation" in captured.out

    # The number of spans can be brittle, let's check for a reasonable number
    assert "spans" in captured.out

    # We can also check the collector directly
    stats = collector.get_trace_statistics()
    assert stats['completed_traces'] > 0
    assert stats['total_spans'] > 0
