from reasoning.LBot_reasoning_processed import (
    ΛBotAdvancedReasoningOrchestrator,
)
from reasoning.reasoning_hub import get_reasoning_hub


def test_reasoning_hub_registration():
    hub = get_reasoning_hub()
    service = hub.get_service("advanced_orchestrator")
    assert isinstance(service, ΛBotAdvancedReasoningOrchestrator)
