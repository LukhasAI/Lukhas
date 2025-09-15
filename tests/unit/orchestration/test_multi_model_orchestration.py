import pytest
from candidate.orchestration.multi_model_orchestration import MultiModelOrchestrator, ModelProvider, ConsensusStrategy, OrchestrationPipeline, OrchestrationMode
import asyncio

class MockContextBus:
    """A mock context bus that has a no-op emit method."""
    async def emit(self, *args, **kwargs):
        await asyncio.sleep(0) # Simulate async behavior

class MockBridge:
    """A mock model bridge that simulates the behavior of a real bridge."""
    def __init__(self, model_name: str):
        self.model_name = model_name

    async def complete(self, prompt: str, **kwargs) -> dict:
        await asyncio.sleep(0.01)
        # Simulate a lower confidence for unsafe prompts to test consensus logic
        if "violence" in prompt or "harm" in prompt:
            return {"text": f"Mock unsafe response from {self.model_name}", "confidence": 0.2, "tokens": {"input": 10, "output": 10}}
        return {"text": f"Mock safe response from {self.model_name}", "confidence": 0.9, "tokens": {"input": 10, "output": 10}}

@pytest.fixture
def orchestrator():
    """Provides a fresh instance of the MultiModelOrchestrator with mock components."""
    # Mock the context bus
    mock_bus = MockContextBus()

    # Instantiate the orchestrator
    orch = MultiModelOrchestrator(context_bus=mock_bus)

    # Manually replace the model bridges with our functional mocks
    orch.model_bridges = {
        ModelProvider.OPENAI_GPT4: MockBridge("GPT-4"),
        ModelProvider.ANTHROPIC_CLAUDE: MockBridge("Claude"),
        ModelProvider.GOOGLE_GEMINI: MockBridge("Gemini"),
    }
    return orch

@pytest.mark.asyncio
async def test_parallel_orchestration_with_mock_bridges(orchestrator):
    """
    Tests that the orchestrator can run a simple parallel pipeline and get a consensus.
    """
    prompt = "This is a test prompt."
    pipeline = OrchestrationPipeline(
        pipeline_id="test_parallel",
        name="Test Parallel Pipeline",
        models=[ModelProvider.OPENAI_GPT4, ModelProvider.ANTHROPIC_CLAUDE],
        consensus_strategy=ConsensusStrategy.BEST_CONFIDENCE,
        orchestration_mode=OrchestrationMode.PARALLEL,
        requires_guardian_oversight=False, # Explicitly disable for this test
    )

    result = await orchestrator.orchestrate(prompt, pipeline)

    assert result is not None
    assert result.consensus_strategy == ConsensusStrategy.BEST_CONFIDENCE
    assert len(result.individual_responses) == 2
    # The mock bridge always returns a confidence of 0.9 for safe prompts
    assert result.confidence_score == pytest.approx(0.9)
    assert result.consensus_text.startswith("Mock safe response from")

@pytest.mark.asyncio
async def test_orchestration_blocked_by_guardian(orchestrator):
    """
    Tests that a pipeline with guardian oversight is blocked for unsafe prompts.
    """
    prompt = "This prompt contains instructions for violence and harm."
    pipeline = OrchestrationPipeline(
        pipeline_id="test_guardian_block",
        name="Test Guardian Block Pipeline",
        models=[ModelProvider.OPENAI_GPT4],
        consensus_strategy=ConsensusStrategy.BEST_CONFIDENCE,
        orchestration_mode=OrchestrationMode.PARALLEL,
        requires_guardian_oversight=True,
    )

    with pytest.raises(PermissionError, match="Guardian oversight blocked orchestration"):
        await orchestrator.orchestrate(prompt, pipeline)

@pytest.mark.asyncio
async def test_orchestration_allowed_by_guardian(orchestrator):
    """
    Tests that a pipeline with guardian oversight is allowed for safe prompts.
    """
    prompt = "This is a safe and helpful prompt about baking."
    pipeline = OrchestrationPipeline(
        pipeline_id="test_guardian_allow",
        name="Test Guardian Allow Pipeline",
        models=[ModelProvider.OPENAI_GPT4],
        consensus_strategy=ConsensusStrategy.BEST_CONFIDENCE,
        orchestration_mode=OrchestrationMode.PARALLEL,
        requires_guardian_oversight=True,
    )

    try:
        result = await orchestrator.orchestrate(prompt, pipeline)
        assert result is not None
        assert result.confidence_score > 0
    except PermissionError:
        pytest.fail("Guardian oversight unexpectedly blocked a safe prompt.")
