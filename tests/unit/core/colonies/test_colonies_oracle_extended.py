import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import sys

# Mock the labs module and its classes before importing oracle_colony
mock_labs_openai_mod = MagicMock()
mock_labs_openai_mod.ModelType = MagicMock()
mock_labs_openai_mod.OpenAICoreService = MagicMock()
mock_labs_openai_mod.OpenAIRequest = MagicMock()

# We need to use a dictionary for sys.modules to be able to patch it
sys.modules['labs.consciousness.reflection.openai_core_service'] = mock_labs_openai_mod

# Now we can import the module to be tested
from core.colonies.oracle_colony import (
    OracleQuery,
    OracleResponse,
    OracleAgent,
    OracleColony,
    get_oracle_colony,
)

pytestmark = pytest.mark.asyncio

@pytest.fixture(autouse=True)
def reset_oracle_colony_singleton():
    from core.colonies import oracle_colony
    original_instance = oracle_colony.oracle_colony
    oracle_colony.oracle_colony = None
    yield
    oracle_colony.oracle_colony = original_instance

async def test_oracle_agent_openai_api_error():
    """Test OracleAgent handling of OpenAI API errors."""
    mock_openai_service = MagicMock()
    mock_openai_service.complete = AsyncMock(side_effect=Exception("API Error"))
    agent = OracleAgent(
        agent_id="test_predictor",
        specialization="predictor",
        openai_service=mock_openai_service,
    )
    query = OracleQuery(query_type="prediction", context={}, openai_enhanced=True)
    response = await agent.process_query(query)
    assert response.response_type == "prediction"
    assert response.content["enhanced_by"] == "local_analysis"
    assert response.confidence < 0.7

async def test_oracle_colony_unknown_query_type():
    """Test OracleColony routing for an unknown query type defaults to prophet."""
    colony = await get_oracle_colony()
    colony.emit_event = AsyncMock()
    query = OracleQuery(query_type="unknown", context={})
    response = await colony.query_oracle(query)
    assert response is not None
    assert response.response_type == "prophecy"

async def test_oracle_agent_different_time_horizons():
    """Test OracleAgent with different time horizons."""
    agent = OracleAgent(agent_id="test_agent", specialization="predictor")
    query_near = OracleQuery(query_type="prediction", context={}, time_horizon="near")
    response_near = await agent.process_query(query_near)
    assert response_near.temporal_scope == "near"

    query_far = OracleQuery(query_type="prediction", context={}, time_horizon="far")
    response_far = await agent.process_query(query_far)
    assert response_far.temporal_scope == "far"
    # In the fallback implementation, confidence is the same regardless of horizon.
    assert response_near.confidence == response_far.confidence

async def test_get_oracle_colony_singleton_behavior():
    """Test the singleton behavior of get_oracle_colony."""
    colony1 = await get_oracle_colony()
    colony2 = await get_oracle_colony()
    assert colony1 is colony2

async def test_oracle_colony_initialization_with_openai():
    """Test OracleColony initialization with OpenAI service available."""
    with patch('core.colonies.oracle_colony._load_labs_openai_symbols') as mock_load, \
         patch('core.colonies.oracle_colony.OpenAICoreService') as mock_service:
        mock_service.return_value = "openai_service_instance"
        colony = OracleColony()
        await colony.initialize()
        assert colony.openai_service == "openai_service_instance"
        mock_load.assert_called_once()

async def test_oracle_agent_dream_generation_openai():
    """Test OracleAgent dream generation with a mocked OpenAI service."""
    mock_openai_service = MagicMock()
    mock_openai_service.complete = AsyncMock(return_value=MagicMock(content="a dream narrative"))
    agent = OracleAgent(
        agent_id="test_dreamer",
        specialization="dreamer",
        openai_service=mock_openai_service,
    )
    query = OracleQuery(query_type="dream", context={}, openai_enhanced=True)

    from core.colonies import oracle_colony
    oracle_colony._load_labs_openai_symbols()

    response = await agent.process_query(query)
    assert response.response_type == "dream"
    assert response.content["enhanced_by"] == "openai"
    assert "a dream narrative" in response.content["dream_narrative"]
    mock_openai_service.complete.assert_called_once()

async def test_oracle_agent_prophecy_openai():
    """Test OracleAgent prophecy generation with a mocked OpenAI service."""
    mock_openai_service = MagicMock()
    mock_openai_service.complete = AsyncMock(return_value=MagicMock(content="a prophecy"))
    agent = OracleAgent(
        agent_id="test_prophet",
        specialization="prophet",
        openai_service=mock_openai_service,
    )
    query = OracleQuery(query_type="prophecy", context={}, openai_enhanced=True)

    from core.colonies import oracle_colony
    oracle_colony._load_labs_openai_symbols()

    response = await agent.process_query(query)
    assert response.response_type == "prophecy"
    assert response.content["enhanced_by"] == "openai"
    assert "a prophecy" in response.content["prophecy"]
    mock_openai_service.complete.assert_called_once()


async def test_oracle_agent_analysis():
    """Test OracleAgent analysis."""
    agent = OracleAgent(agent_id="test_analyzer", specialization="analyzer")
    query = OracleQuery(query_type="analysis", context={})
    response = await agent.process_query(query)
    assert response.response_type == "analysis"
    assert "Deep system analysis" in response.content["analysis"]

async def test_oracle_colony_get_temporal_insights():
    """Test getting insights across multiple time horizons."""
    colony = await get_oracle_colony()
    insights = await colony.get_temporal_insights({}, horizons=["near", "far"])
    assert "near" in insights
    assert "far" in insights
    assert insights["near"].response_type == "prophecy"
    assert insights["far"].temporal_scope == "far"

async def test_oracle_colony_generate_contextual_dream():
    """Test generating a contextual dream."""
    colony = await get_oracle_colony()
    response = await colony.generate_contextual_dream("test_user", {})
    assert response.response_type == "dream"

async def test_oracle_colony_predict_system_drift():
    """Test predicting system drift."""
    colony = await get_oracle_colony()
    response = await colony.predict_system_drift({})
    assert response.response_type == "prediction"

async def test_convenience_functions():
    """Test the convenience functions predict, dream, and prophecy."""
    from core.colonies.oracle_colony import predict, dream, prophecy

    with patch('core.colonies.oracle_colony.get_oracle_colony') as mock_get_colony:
        mock_colony = AsyncMock()
        mock_get_colony.return_value = mock_colony

        query_pred = OracleQuery(query_type="prediction", context={}, time_horizon="near", openai_enhanced=True, priority='normal', user_id=None)
        await predict({}, time_horizon='near')
        called_query_pred = mock_colony.query_oracle.call_args[0][0]
        assert called_query_pred.query_type == query_pred.query_type

        query_dream = OracleQuery(query_type="dream", context={}, user_id=None, time_horizon='near', openai_enhanced=True, priority='normal')
        await dream({})
        called_query_dream = mock_colony.query_oracle.call_args[0][0]
        assert called_query_dream.query_type == query_dream.query_type

        query_prophecy = OracleQuery(query_type="prophecy", context={}, time_horizon="medium", openai_enhanced=True, priority='normal', user_id=None)
        await prophecy({})
        called_query_prophecy = mock_colony.query_oracle.call_args[0][0]
        assert called_query_prophecy.query_type == query_prophecy.query_type

async def test_oracle_agent_unknown_specialization_raises_error():
    """Test that an unknown specialization raises a ValueError."""
    agent = OracleAgent(agent_id="test_agent", specialization="unknown")
    query = OracleQuery(query_type="any", context={})
    with pytest.raises(ValueError, match="Unknown specialization: unknown"):
        await agent.process_query(query)
