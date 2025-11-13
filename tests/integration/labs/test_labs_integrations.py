import pytest
from unittest.mock import MagicMock, AsyncMock
import sys

# Mock the core.common module to break the circular dependency
sys.modules['core.common'] = MagicMock()

from labs.identity import IdentitySystem, generate_lambda_id
from labs.memory.symbol_aware_tiered_memory import SymbolAwareTieredMemory
import uuid

# --- Governance + Explainability Integration ---

from labs.governance import PolicyGuard, PolicyResult
from labs.bridge.explainability_interface_layer import ExplainabilityInterface, ExplanationLevel

class SimplePolicyGuard(PolicyGuard):
    """A simple policy guard for testing purposes."""
    def check(self, data: dict) -> PolicyResult:
        is_allowed = data.get("value", 0) > 10
        result = PolicyResult()
        result.allowed = is_allowed
        result.reason = "Value must be greater than 10" if not is_allowed else "Value is acceptable"
        return result

@pytest.mark.asyncio
async def test_governance_explainability_integration():
    """
    Tests that the ExplainabilityInterface can generate explanations for governance decisions.
    """
    policy_guard = SimplePolicyGuard()
    decision_data = {"value": 5}
    policy_result = policy_guard.check(decision_data)

    decision = {
        "id": "decision_1",
        "result": "denied" if not policy_result.allowed else "approved",
        "premises": [f"Input value is {decision_data['value']}"],
        "conclusion": policy_result.reason,
        "factors": ["value > 10"],
    }

    explainer = ExplainabilityInterface()
    explanation = await explainer.explain(decision, level=ExplanationLevel.TECHNICAL)

    assert "Value must be greater than 10" in explanation.content

@pytest.mark.asyncio
async def test_governance_explainability_formal_proof():
    """
    Tests the generation of formal proofs for governance decisions.
    """
    policy_guard = SimplePolicyGuard()
    decision_data = {"value": 20}
    policy_result = policy_guard.check(decision_data)

    decision = {
        "id": "decision_2",
        "result": "approved",
        "premises": ["Input value is 20"],
        "conclusion": "Value is acceptable",
        "reasoning_steps": [{"statement": "20 > 10", "rule": "Arithmetic"}],
    }

    explainer = ExplainabilityInterface()
    explanation = await explainer.explain(decision, include_proof=True)

    assert explanation.formal_proof is not None
    assert explanation.formal_proof.valid
    assert "20 > 10" in explanation.formal_proof.steps[1]["statement"]


# --- Bridge + LLM Wrappers Integration ---

from labs.bridge.llm_wrappers.openai_modulated_service import (
    OpenAIModulatedService,
    CompletionRequest,
    ModelTier,
)

@pytest.mark.asyncio
async def test_bridge_llm_chat_completion():
    """
    Tests the basic data flow for chat completions.
    """
    mock_openai_client = AsyncMock()
    mock_openai_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="mocked_response"))]
    )
    service = OpenAIModulatedService(api_key="fake_key")
    service.async_client = mock_openai_client
    request = CompletionRequest(
        messages=[{"role": "user", "content": "Hello"}],
        model=ModelTier.GPT35_TURBO,
    )
    response = await service.chat_completion(request)
    mock_openai_client.chat.completions.create.assert_called_once()
    assert response.choices[0].message.content == "mocked_response"

@pytest.mark.asyncio
async def test_bridge_llm_error_propagation():
    """
    Tests that errors from the LLM are propagated correctly.
    """
    mock_openai_client = AsyncMock()
    mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
    service = OpenAIModulatedService(api_key="fake_key")
    service.async_client = mock_openai_client
    request = CompletionRequest(messages=[{"role": "user", "content": "Hello"}])
    with pytest.raises(Exception, match="API Error"):
        await service.chat_completion(request)

# --- Orchestration + Memory Integration ---

class SimpleWorkflow:
    """A simple workflow to demonstrate orchestration and memory interaction."""
    def __init__(self, memory_system: SymbolAwareTieredMemory):
        self.memory_system = memory_system
        self.workflow_id = f"wf_{uuid.uuid4()}"

    def run(self, data: str):
        """Runs the workflow and stores the result in memory."""
        result = f"processed_{data}"
        self.memory_system.store(memory_id=self.workflow_id, data=result)
        return self.workflow_id

def test_orchestration_memory_integration():
    memory_system = SymbolAwareTieredMemory()
    workflow = SimpleWorkflow(memory_system)
    input_data = "test_data"
    result_id = workflow.run(input_data)
    retrieved_result = memory_system.retrieve(memory_id=result_id)
    assert retrieved_result == f"processed_{input_data}"

def test_orchestration_memory_state_preservation():
    memory_system = SymbolAwareTieredMemory()
    workflow1 = SimpleWorkflow(memory_system)
    result_id1 = workflow1.run("data1")
    workflow2 = SimpleWorkflow(memory_system)
    result_id2 = workflow2.run("data2")
    retrieved1 = memory_system.retrieve(memory_id=result_id1)
    retrieved2 = memory_system.retrieve(memory_id=result_id2)
    assert retrieved1 == "processed_data1"
    assert retrieved2 == "processed_data2"

def test_orchestration_memory_error_handling():
    memory_system = SymbolAwareTieredMemory()
    non_existent_id = f"wf_{uuid.uuid4()}"
    retrieved_result = memory_system.retrieve(memory_id=non_existent_id)
    assert retrieved_result is None

# --- Identity + Memory Integration ---

def test_identity_memory_integration():
    lambda_id = generate_lambda_id(user_id="test_user_123")
    assert lambda_id is not None, "Failed to get lambda_id"
    memory_system = SymbolAwareTieredMemory()
    user_data = {"profile": "test_user_123", "settings": {"theme": "dark"}}
    memory_system.store(memory_id=lambda_id, data=user_data)
    retrieved_data = memory_system.retrieve(memory_id=lambda_id)
    assert retrieved_data is not None, "Failed to retrieve data from memory"
    assert retrieved_data == user_data, "Retrieved data does not match stored data"

def test_identity_memory_state_preservation():
    memory_system1 = SymbolAwareTieredMemory()
    memory_system2 = SymbolAwareTieredMemory()

    # User 1
    lambda_id1 = generate_lambda_id(user_id="user_alpha")
    user1_data = {"data": "user_A_data"}
    memory_system1.store(memory_id=lambda_id1, data=user1_data)

    # User 2
    lambda_id2 = generate_lambda_id(user_id="user_beta")
    user2_data = {"data": "user_B_data"}
    memory_system2.store(memory_id=lambda_id2, data=user2_data)

    retrieved1 = memory_system1.retrieve(memory_id=lambda_id1)
    retrieved2 = memory_system2.retrieve(memory_id=lambda_id2)

    assert retrieved1 == user1_data
    assert retrieved2 == user2_data
    assert retrieved1 != retrieved2

def test_identity_memory_error_handling():
    lambda_id = generate_lambda_id(user_id="test_user_404")
    memory_system = SymbolAwareTieredMemory()
    retrieved_data = memory_system.retrieve(memory_id=lambda_id)
    assert retrieved_data is None
