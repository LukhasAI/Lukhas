import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Since oracle_colony uses importlib to load labs symbols, we need to do some setup
# before importing the module to ensure the symbols are available for patching.
import sys

# Mock the labs module and its classes before importing oracle_colony
mock_labs_openai_mod = MagicMock()
mock_labs_openai_mod.ModelType = MagicMock()
mock_labs_openai_mod.OpenAICoreService = MagicMock()
mock_labs_openai_mod.OpenAIRequest = MagicMock()

# We need to use a dictionary for sys.modules to be able to patch it
sys.modules['labs.consciousness.reflection.openai_core_service'] = mock_labs_openai_mod

# Now we can import the module to be tested
from core.colonies.oracle_colony import (  # noqa: E402 - test stubs must populate sys.modules before import
    OracleQuery,
    OracleResponse,
    OracleAgent,
    OracleColony,
    get_oracle_colony,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_openai_service():
    """Fixture to provide a mocked OpenAI service."""
    service = MagicMock()
    service.complete = AsyncMock(return_value=MagicMock(content="mocked response"))
    return service


def test_oracle_query_creation():
    """Test OracleQuery dataclass initialization."""
    query = OracleQuery(
        query_type="prediction",
        context={"data": "test"},
        time_horizon="near",
    )
    assert query.query_type == "prediction"
    assert query.context == {"data": "test"}


async def test_oracle_agent_prediction_fallback():
    """Test OracleAgent prediction fallback when OpenAI is not available."""
    agent = OracleAgent(agent_id="test_predictor", specialization="predictor")
    query = OracleQuery(query_type="prediction", context={}, openai_enhanced=False)
    response = await agent.process_query(query)
    assert response.response_type == "prediction"
    assert response.content["enhanced_by"] == "local_analysis"
    assert response.confidence == 0.65


async def test_oracle_agent_prediction_openai(mock_openai_service):
    """Test OracleAgent prediction with a mocked OpenAI service."""
    agent = OracleAgent(
        agent_id="test_predictor",
        specialization="predictor",
        openai_service=mock_openai_service,
    )
    query = OracleQuery(query_type="prediction", context={}, openai_enhanced=True)

    # We need to reload the symbols as they are loaded lazily
    from core.colonies import oracle_colony
    oracle_colony._load_labs_openai_symbols()

    response = await agent.process_query(query)
    assert response.response_type == "prediction"
    assert response.content["enhanced_by"] == "openai"
    assert "mocked response" in response.content["prediction"]
    mock_openai_service.complete.assert_called_once()


async def test_oracle_colony_initialization_no_openai():
    """Test OracleColony initialization without OpenAI."""
    with patch('core.colonies.oracle_colony._load_labs_openai_symbols'), \
         patch('core.colonies.oracle_colony.OpenAICoreService', None):
        colony = OracleColony()
        await colony.initialize()
        assert colony.openai_service is None
        assert "predictor" in colony.oracle_agents

# To avoid issues with the singleton pattern in get_oracle_colony,
# we reset it for tests that need a clean instance.
@pytest.fixture(autouse=True)
def reset_oracle_colony_singleton():
    from core.colonies import oracle_colony
    original_instance = oracle_colony.oracle_colony
    oracle_colony.oracle_colony = None
    yield
    oracle_colony.oracle_colony = original_instance


async def test_oracle_colony_query_routing():
    """Test that OracleColony routes queries to the correct agent."""
    colony = await get_oracle_colony()
    colony.emit_event = AsyncMock()
    # Mock the agent's process_query method to track calls
    colony.oracle_agents["predictor"].process_query = AsyncMock(
        return_value=OracleResponse(
            query_id="q1", response_type="prediction", content={}, confidence=0.5,
            temporal_scope="near", generated_at=None, metadata={}
        )
    )
    colony.oracle_agents["dreamer"].process_query = AsyncMock(
        return_value=OracleResponse(
            query_id="q2", response_type="dream", content={}, confidence=0.5,
            temporal_scope="near", generated_at=None, metadata={}
        )
    )

    # Test prediction query
    pred_query = OracleQuery(query_type="prediction", context={})
    await colony.query_oracle(pred_query)
    colony.oracle_agents["predictor"].process_query.assert_called_once()
    colony.oracle_agents["dreamer"].process_query.assert_not_called()

    # Test dream query
    dream_query = OracleQuery(query_type="dream", context={})
    await colony.query_oracle(dream_query)
    colony.oracle_agents["dreamer"].process_query.assert_called_once()
