from trace.drift_metrics import compute_drift_score
from unittest.mock import MagicMock, patch

import pytest
from dream.hyperspace_dream_simulator import (
    MAX_RECURSION_DEPTH,
    HyperspaceDreamSimulator,
)

from memory.core_memory.fold_lineage_tracker import (
    MAX_DRIFT_RATE,
    CausationType,
    FoldLineageTracker,
)


@pytest.fixture
def mock_logger():
    with (
        patch("lukhas.dream.hyperspace_dream_simulator.logger") as mock_hds_logger,
        patch(
            "lukhas.memory.core_memory.fold_lineage_tracker.logger"
        ) as mock_flt_logger,
    ):
        yield {"hds": mock_hds_logger, "flt": mock_flt_logger}


@pytest.mark.asyncio
async def test_hds_recursion_depth_guard(mock_logger):
    """
    Tests that the HyperspaceDreamSimulator stops recursion when
    MAX_RECURSION_DEPTH is exceeded.
    """
    hds = HyperspaceDreamSimulator(integration_mode=False)
    scenario_id = await hds.create_scenario("test", "test")
    timeline_id = hds.active_scenarios[scenario_id].root_timeline

    # Manually set recursion depth to be over the limit
    high_recursion_depth = MAX_RECURSION_DEPTH + 1

    result = await hds.simulate_decision(
        scenario_id, timeline_id, {"type": "test"}, recursion_depth=high_recursion_depth
    )

    assert result == []
    mock_logger["hds"].warning.assert_called_with(
        "ÎHDS: Max recursion depth exceeded, breaking loop",
        scenario_id=scenario_id,
        timeline_id=timeline_id,
        recursion_depth=high_recursion_depth,
    )


@pytest.mark.asyncio
async def test_hds_token_budget_guard(mock_logger):
    """
    Tests that the HyperspaceDreamSimulator stops when the token budget is exceeded.
    """
    hds = HyperspaceDreamSimulator(integration_mode=False, max_tokens=100)
    scenario_id = await hds.create_scenario("test", "test")
    timeline_id = hds.active_scenarios[scenario_id].root_timeline

    # Simulate a decision that will exceed the token budget
    large_decision = {"type": "test", "data": "a" * 1000}
    result = await hds.simulate_decision(scenario_id, timeline_id, large_decision)

    assert result == []
    mock_logger["hds"].warning.assert_called_with(
        "ÎHDS: Token budget exceeded, halting simulation",
        scenario_id=scenario_id,
        timeline_id=timeline_id,
        tokens_used=hds.tokens_used,
    )


def test_flt_recursion_depth_guard(mock_logger):
    """
    Tests that the FoldLineageTracker stops recursion when
    MAX_RECURSION_DEPTH is exceeded.
    """
    flt = FoldLineageTracker()
    high_recursion_depth = MAX_RECURSION_DEPTH + 1

    result = flt.track_causation(
        "source",
        "target",
        CausationType.ASSOCIATION,
        recursion_depth=high_recursion_depth,
    )

    assert result == ""
    mock_logger["flt"].warning.assert_called_with(
        "FoldCausation: Max recursion depth exceeded, breaking loop",
        source="source",
        target="target",
        recursion_depth=high_recursion_depth,
    )


def test_flt_drift_rate_guard(mock_logger):
    """
    Tests that the FoldLineageTracker stops when the drift rate is exceeded.
    """
    flt = FoldLineageTracker()

    # Mock a fold node with high drift score
    flt.fold_nodes["source"] = MagicMock(drift_score=MAX_DRIFT_RATE + 0.1)

    result = flt.track_causation("source", "target", CausationType.ASSOCIATION)

    assert result == ""
    mock_logger["flt"].warning.assert_called_with(
        "FoldCausation: Drift rate exceeded, halting tracking",
        source="source",
        drift_score=flt.fold_nodes["source"].drift_score,
    )


def test_drift_metrics_token_budget():
    """
    Tests that the compute_drift_score function respects the token budget.
    """
    state1 = {"a": 1, "b": [1, 2, 3]}
    state2 = {"a": 2, "b": [4, 5, 6], "c": "a" * 1000}

    # With a small budget, the score should be incomplete
    score_low_budget = compute_drift_score(state1, state2, max_tokens=10)

    # With a large budget, the score should be complete
    score_high_budget = compute_drift_score(state1, state2, max_tokens=10000)

    assert score_low_budget < score_high_budget
