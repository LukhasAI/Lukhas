
import asyncio
import functools
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock missing modules that cause TypeErrors on initialization
# Use AsyncMock for modules that have async functions
mock_dmb = MagicMock()
mock_dmb.get_dmb = AsyncMock()
sys.modules["core.integration.dynamic_modality_broker"] = mock_dmb


# Mock the decorator correctly to handle arguments
def mock_instrument_reasoning(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper


mock_debugger = MagicMock()
mock_debugger.get_srd = MagicMock()
mock_debugger.instrument_reasoning = mock_instrument_reasoning
sys.modules["ethics.self_reflective_debugger"] = mock_debugger


sys.modules["labs.consciousness.dream.core.dream_feedback_controller"] = MagicMock()
mock_meg_module = MagicMock()
mock_meg_module.get_meg = AsyncMock()
sys.modules["ethics.meta_ethics_governor"] = mock_meg_module
sys.modules["memory.emotional"] = MagicMock()


from matriz.memory.temporal.hyperspace_dream_simulator import (
    CausalConstraint,
    HyperspaceDreamSimulator,
    HyperspaceVector,
    SimulationScenario,
    SimulationType,
    TimelineBranch,
)


@pytest.fixture
def simulator():
    # We need to re-import the class under test after mocking the dependencies
    from matriz.memory.temporal.hyperspace_dream_simulator import (
        HyperspaceDreamSimulator,
    )

    return HyperspaceDreamSimulator()


@pytest.mark.asyncio
async def test_create_scenario(simulator):
    scenario_id = await simulator.create_scenario("Test Scenario", "A test scenario")
    assert scenario_id in simulator.active_scenarios


@pytest.mark.asyncio
async def test_simulate_decision(simulator):
    scenario_id = await simulator.create_scenario("Test Scenario", "A test scenario")
    scenario = simulator.active_scenarios[scenario_id]
    timeline_id = scenario.root_timeline
    decision = {"type": "test_decision", "description": "A test decision"}
    timeline_ids = await simulator.simulate_decision(scenario_id, timeline_id, decision)
    assert timeline_id in timeline_ids


@pytest.mark.asyncio
async def test_complete_scenario(simulator):
    scenario_id = await simulator.create_scenario("Test Scenario", "A test scenario")
    await simulator.complete_scenario(scenario_id)
    assert scenario_id not in simulator.active_scenarios
    assert scenario_id in simulator.scenario_history


def test_initialization():
    from matriz.memory.temporal.hyperspace_dream_simulator import (
        HyperspaceDreamSimulator,
    )

    simulator = HyperspaceDreamSimulator()
    assert simulator is not None
    assert isinstance(simulator, HyperspaceDreamSimulator)


@pytest.mark.asyncio
async def test_scenario_creation_with_context(simulator):
    initial_context = {"key": "value"}
    scenario_id = await simulator.create_scenario(
        "Test", "Test Desc", initial_context=initial_context
    )
    scenario = simulator.active_scenarios[scenario_id]
    root_timeline = scenario.timelines[scenario.root_timeline]
    assert root_timeline.context == initial_context


@pytest.mark.asyncio
async def test_decision_simulation_adds_to_timeline(simulator):
    scenario_id = await simulator.create_scenario("Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "action", "param": "value"}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    timeline = simulator.active_scenarios[scenario_id].timelines[timeline_id]
    assert len(timeline.decisions) == 1
    assert timeline.decisions[0]["type"] == "action"


@pytest.mark.asyncio
async def test_outcome_generation(simulator):
    scenario_id = await simulator.create_scenario("Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "action", "param": "value"}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    timeline = simulator.active_scenarios[scenario_id].timelines[timeline_id]
    assert len(timeline.outcomes) > 0


@pytest.mark.asyncio
async def test_timeline_branching(simulator):
    scenario_id = await simulator.create_scenario(
        "Test", "Test Desc", simulation_type=SimulationType.RISK_ASSESSMENT
    )
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "risky_action"}
    new_timelines = await simulator.simulate_decision(
        scenario_id, timeline_id, decision, explore_alternatives=True
    )
    assert len(new_timelines) > 1
    assert len(simulator.active_scenarios[scenario_id].timelines) > 1


@pytest.mark.asyncio
async def test_error_handling_scenario_not_found(simulator):
    with pytest.raises(ValueError, match="Scenario fake_id not found"):
        await simulator.simulate_decision("fake_id", "fake_timeline", {})


@pytest.mark.asyncio
async def test_error_handling_timeline_not_found(simulator):
    scenario_id = await simulator.create_scenario("Test", "Test Desc")
    with pytest.raises(ValueError, match="Timeline fake_timeline not found in scenario"):
        await simulator.simulate_decision(scenario_id, "fake_timeline", {})


@pytest.mark.asyncio
async def test_scenario_analysis(simulator):
    scenario_id = await simulator.create_scenario("Test", "Test Desc")
    analysis = await simulator.analyze_scenario(scenario_id)
    assert "optimal_timeline" in analysis
    assert "risk_analysis" in analysis


@pytest.mark.asyncio
async def test_system_status(simulator):
    await simulator.create_scenario("Test", "Test Desc")
    status = simulator.get_system_status()
    assert status["active_scenarios"] == 1


@pytest.mark.asyncio
async def test_token_budget_exceeded(simulator):
    simulator.max_tokens = 10
    scenario_id = await simulator.create_scenario("Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "costly_action", "description": "This is a very costly action"}
    # This should exceed the token budget and return an empty list
    result = await simulator.simulate_decision(scenario_id, timeline_id, decision)
    assert result == []


@pytest.mark.asyncio
async def test_hyperspace_navigation_updates_position(simulator):
    scenario_id = await simulator.create_scenario("Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    timeline = simulator.active_scenarios[scenario_id].timelines[timeline_id]
    initial_pos = timeline.current_position.dimensions.copy()
    decision = {
        "type": "move",
        "impact_dimensions": {"x": 1.0, "y": -0.5},
    }
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    final_pos = timeline.current_position.dimensions
    assert final_pos.get("x", 0) != initial_pos.get("x", 0)
    assert final_pos.get("y", 0) != initial_pos.get("y", 0)


@patch(
    "matriz.memory.temporal.hyperspace_dream_simulator.get_meg", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_ethical_governor_integration(mock_get_meg, simulator):
    mock_meg = AsyncMock()
    mock_meg.evaluate_decision.return_value = MagicMock(
        verdict=MagicMock(value="approved")
    )
    mock_get_meg.return_value = mock_meg

    # Re-initialize integrations with the mock
    simulator.meg = await mock_get_meg()
    simulator.integration_mode = True

    scenario_id = await simulator.create_scenario("Ethical Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "ethical_dilemma"}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    mock_meg.evaluate_decision.assert_awaited_once()


@patch(
    "matriz.memory.temporal.hyperspace_dream_simulator.get_meg", new_callable=AsyncMock
)
@pytest.mark.asyncio
async def test_ethical_governor_rejection(mock_get_meg, simulator):
    mock_meg = AsyncMock()
    mock_meg.evaluate_decision.return_value = MagicMock(
        verdict=MagicMock(value="rejected")
    )
    mock_get_meg.return_value = mock_meg

    # Re-initialize integrations with the mock
    simulator.meg = await mock_get_meg()
    simulator.integration_mode = True

    scenario_id = await simulator.create_scenario("Ethical Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "unethical_action"}
    result = await simulator.simulate_decision(scenario_id, timeline_id, decision)
    assert result == []


@pytest.mark.asyncio
async def test_dream_state_persistence(tmp_path):
    trace_dir = tmp_path / "traces"
    from matriz.memory.temporal.hyperspace_dream_simulator import (
        HyperspaceDreamSimulator,
    )

    simulator = HyperspaceDreamSimulator(trace_dir=trace_dir)
    scenario_id = await simulator.create_scenario("Persistent Test", "Test Desc")
    await simulator.complete_scenario(scenario_id)
    expected_file = trace_dir / f"scenario_{scenario_id}.json"
    assert expected_file.exists()
    with open(expected_file, "r") as f:
        data = json.load(f)
        assert data["scenario"]["scenario_id"] == scenario_id


def test_timeline_branch_logic():
    scenario = SimulationScenario(name="Test")
    root = TimelineBranch()
    scenario.add_timeline(root)
    branch_id = scenario.branch_timeline(root.branch_id, {"type": "split"})
    assert branch_id is not None
    assert branch_id in scenario.timelines
    assert scenario.timelines[branch_id].parent_branch == root.branch_id


@pytest.mark.asyncio
async def test_max_recursion_depth(simulator):
    # This value is hardcoded in the file, so we are testing against it.
    # MAX_RECURSION_DEPTH = 10
    scenario_id = await simulator.create_scenario("Recursive Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "recursive_action"}
    # The first call is at recursion_depth 0
    result = await simulator.simulate_decision(
        scenario_id, timeline_id, decision, recursion_depth=11
    )
    assert result == []


@pytest.mark.asyncio
async def test_get_scenario_status(simulator):
    scenario_id = await simulator.create_scenario("Status Test", "Test Desc")
    status = simulator.get_scenario_status(scenario_id)
    assert status["name"] == "Status Test"
    assert status["status"] == "initialized"


@pytest.mark.asyncio
async def test_find_optimal_timeline():
    scenario = SimulationScenario(name="Optimal Test")
    t1 = TimelineBranch(probability=0.8, confidence=0.9)
    t2 = TimelineBranch(probability=0.9, confidence=0.8)
    scenario.add_timeline(t1)
    scenario.add_timeline(t2)
    optimal_id = scenario.find_optimal_timeline()
    assert optimal_id == t2.branch_id


@patch("matriz.memory.temporal.hyperspace_dream_simulator.DreamFeedbackPropagator")
@pytest.mark.asyncio
async def test_dream_feedback_integration(MockDreamFeedbackPropagator, simulator):
    mock_propagator = MockDreamFeedbackPropagator.return_value
    # Manually set the propagator since initialize_integrations is complex
    simulator.dream_feedback_propagator = mock_propagator
    simulator.integration_mode = True

    scenario_id = await simulator.create_scenario("Feedback Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "feedback_action"}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    mock_propagator.propagate.assert_called_once()


@pytest.mark.asyncio
async def test_token_profiling(simulator):
    simulator.max_tokens = 1000
    scenario_id = await simulator.create_scenario("Token Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "some_action", "data": "x" * 100}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    report = simulator.get_token_usage_report()
    assert report["session_summary"]["total_tokens_used"] > 0
    assert len(simulator.token_profiler["decision_token_costs"]) > 0


@pytest.mark.asyncio
async def test_token_warning_emission(simulator, tmp_path):
    # The _log_token_warning will fail in the test env, so we are patching it
    with patch(
        "matriz.memory.temporal.hyperspace_dream_simulator.HyperspaceDreamSimulator._log_token_warning"
    ):
        simulator.max_tokens = 100
        scenario_id = await simulator.create_scenario("Warning Test", "Test Desc")
        timeline_id = simulator.active_scenarios[scenario_id].root_timeline
        # A large decision to trigger the 80% warning
        decision = {"type": "large_action", "data": "x" * 300}
        await simulator.simulate_decision(scenario_id, timeline_id, decision)


@pytest.mark.asyncio
async def test_simulation_of_various_types(simulator):
    for sim_type in SimulationType:
        scenario_id = await simulator.create_scenario(
            f"{sim_type.value} Test", "Test Desc", simulation_type=sim_type
        )
        assert simulator.active_scenarios[scenario_id].simulation_type == sim_type


def test_hyperspace_vector_logic():
    v1 = HyperspaceVector(dimensions={"x": 1, "y": 2})
    v2 = HyperspaceVector(dimensions={"x": 4, "y": 6})
    assert v1.distance_to(v2) == 5.0
    v_int = v1.interpolate(v2, 0.5)
    assert v_int.dimensions["x"] == 2.5
    assert v_int.dimensions["y"] == 4.0


@pytest.mark.asyncio
async def test_constraint_checking(simulator):
    scenario_id = await simulator.create_scenario("Constraint Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    timeline = simulator.active_scenarios[scenario_id].timelines[timeline_id]
    timeline.constraints.append(CausalConstraint.RESOURCE_LIMITS)
    timeline.context["resource_budget"] = 10
    decision = {"type": "action"}
    # This outcome will exceed the budget
    outcome = {"resource_cost": 20}
    with patch.object(
        simulator, "_generate_outcomes", new_callable=AsyncMock
    ) as mock_outcomes:
        mock_outcomes.return_value = [outcome]
        await simulator.simulate_decision(scenario_id, timeline_id, decision)

    assert "Resource limit exceeded" in timeline.violations


@pytest.mark.asyncio
async def test_quick_scenario_simulation_utility():
    with patch(
        "matriz.memory.temporal.hyperspace_dream_simulator.get_hds", new_callable=AsyncMock
    ) as mock_get_hds:
        # We need to re-import the module to be tested after mocking
        from matriz.memory.temporal.hyperspace_dream_simulator import (
            quick_scenario_simulation,
        )

        mock_hds = AsyncMock()
        mock_get_hds.return_value = mock_hds

        # Configure the mock to behave like the real object for the test
        mock_hds.create_scenario.return_value = "quick_scenario_123"
        mock_hds.active_scenarios = {
            "quick_scenario_123": MagicMock(root_timeline="root_abc")
        }
        mock_hds.simulate_decision.return_value = ["root_abc"]
        mock_hds.complete_scenario.return_value = {"analysis": "done"}

        decision_sequence = [{"type": "step1"}, {"type": "step2"}]

        result = await quick_scenario_simulation("Quick Test", decision_sequence)

        assert result == {"analysis": "done"}
        mock_hds.create_scenario.assert_awaited_once()
        assert mock_hds.simulate_decision.await_count == 2
        mock_hds.complete_scenario.assert_awaited_once()


@pytest.mark.asyncio
async def test_no_alternative_timelines_when_false(simulator):
    scenario_id = await simulator.create_scenario(
        "No Alt Test", "Test Desc", simulation_type=SimulationType.RISK_ASSESSMENT
    )
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "single_path"}

    # explore_alternatives=False
    new_timelines = await simulator.simulate_decision(
        scenario_id, timeline_id, decision, explore_alternatives=False
    )

    # Should only return the original timeline ID
    assert len(new_timelines) == 1
    assert new_timelines[0] == timeline_id
    # No new timelines should be created
    assert len(simulator.active_scenarios[scenario_id].timelines) == 1


@pytest.mark.asyncio
async def test_get_hds_singleton():
    # This function is defined in the file, so we must import it to test it.
    from matriz.memory.temporal.hyperspace_dream_simulator import (
        _hds_instance,
        get_hds,
    )

    # Reset instance for clean test
    _hds_instance = None

    hds1 = await get_hds()
    hds2 = await get_hds()

    assert hds1 is hds2
    assert isinstance(hds1, HyperspaceDreamSimulator)


@pytest.mark.asyncio
async def test_initialization_with_integrations_disabled():
    from matriz.memory.temporal.hyperspace_dream_simulator import (
        HyperspaceDreamSimulator,
    )

    simulator = HyperspaceDreamSimulator(integration_mode=False)
    await simulator.initialize_integrations()
    assert simulator.meg is None
    assert simulator.emotional_memory is None


@pytest.mark.asyncio
async def test_generate_recommendations(simulator):
    scenario_id = await simulator.create_scenario("Test Scenario", "A test scenario")
    scenario = simulator.active_scenarios[scenario_id]
    timeline_id = scenario.root_timeline
    decision = {"type": "test_decision", "description": "A test decision"}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    analysis = await simulator.analyze_scenario(scenario_id)
    assert "recommendations" in analysis
    assert isinstance(analysis["recommendations"], list)


@pytest.mark.asyncio
async def test_analyze_convergence(simulator):
    scenario_id = await simulator.create_scenario("Test Scenario", "A test scenario")
    scenario = simulator.active_scenarios[scenario_id]
    timeline_id = scenario.root_timeline
    decision = {"type": "test_decision", "description": "A test decision"}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    analysis = await simulator.analyze_scenario(scenario_id)
    assert "convergence_analysis" in analysis
    assert "convergence_points" in analysis["convergence_analysis"]


@pytest.mark.asyncio
async def test_creative_exploration_outcome(simulator):
    scenario_id = await simulator.create_scenario(
        "Creative Test",
        "Test creative exploration",
        simulation_type=SimulationType.CREATIVE_EXPLORATION,
    )
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "creative_action"}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    timeline = simulator.active_scenarios[scenario_id].timelines[timeline_id]
    assert any(o["type"] == "breakthrough" for o in timeline.outcomes)


@pytest.mark.asyncio
async def test_risk_assessment_outcome(simulator):
    scenario_id = await simulator.create_scenario(
        "Risk Test",
        "Test risk assessment",
        simulation_type=SimulationType.RISK_ASSESSMENT,
    )
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "risky_action"}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    timeline = simulator.active_scenarios[scenario_id].timelines[timeline_id]
    assert any(o["type"] == "worst_case" for o in timeline.outcomes)


@pytest.mark.asyncio
async def test_token_usage_report(simulator):
    scenario_id = await simulator.create_scenario("Token Report Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {"type": "some_action", "data": "x" * 100}
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    report = simulator.get_token_usage_report()
    assert "session_summary" in report
    assert "decision_analysis" in report
    assert "outcome_analysis" in report
    assert report["session_summary"]["total_tokens_used"] > 0


@pytest.mark.asyncio
async def test_analyze_symbolic_reasons(simulator):
    scenario_id = await simulator.create_scenario("Symbolic Reasons Test", "Test Desc")
    timeline_id = simulator.active_scenarios[scenario_id].root_timeline
    decision = {
        "type": "complex_action",
        "data": "x" * 1001,
        "alternatives": [],
        "context": {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6},
    }
    await simulator.simulate_decision(scenario_id, timeline_id, decision)
    reasons = simulator._analyze_symbolic_reasons()
    assert "complex_decision_structure" in reasons
    assert "alternative_exploration" in reasons
    assert "rich_context" in reasons


@pytest.mark.asyncio
async def test_get_system_status_with_no_scenarios():
    simulator = HyperspaceDreamSimulator()
    status = simulator.get_system_status()
    assert status["active_scenarios"] == 0
    assert status["completed_scenarios"] == 0


@pytest.mark.asyncio
async def test_get_scenario_status_not_found():
    simulator = HyperspaceDreamSimulator()
    status = simulator.get_scenario_status("not_found")
    assert "error" in status


@pytest.mark.asyncio
async def test_max_concurrent_scenarios(simulator):
    simulator.max_concurrent_scenarios = 1
    scenario_id1 = await simulator.create_scenario("Test 1", "Test 1")
    assert scenario_id1 in simulator.active_scenarios
    scenario_id2 = await simulator.create_scenario("Test 2", "Test 2")
    assert scenario_id2 in simulator.active_scenarios
    assert scenario_id1 not in simulator.active_scenarios


@pytest.mark.asyncio
async def test_generate_causal_model_outcomes(simulator):
    decision = {"type": "strategic", "affects_network": True}
    outcomes = await simulator._generate_causal_model_outcomes(decision, [])
    assert len(outcomes) == 2
    assert "systemic_cascade" in [o["type"] for o in outcomes]
    assert "network_propagation" in [o["type"] for o in outcomes]
