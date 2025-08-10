import asyncio
import sys
import types
import unittest

# Provide lightweight torch stub if torch is unavailable
for missing in ["torch", "torch.nn", "openai", "contracts"]:
    if missing not in sys.modules:
        stub = types.ModuleType(missing)
        if missing == "openai":
            stub.AsyncOpenAI = object  # minimal attribute used in imports
        if missing == "contracts":
            stub.IConsciousnessModule = object
            stub.IQuantumModule = object
            stub.ProcessingResult = object
            stub.AgentContext = object
        sys.modules[missing] = stub

for missing in ["structlog"]:
    if missing not in sys.modules:
        stub = types.ModuleType(missing)
        stub.get_logger = lambda *a, **k: types.SimpleNamespace(
            info=lambda *x, **y: None
        )
        sys.modules[missing] = stub

if "core.bridges.orchestration_core_bridge" not in sys.modules:
    ocb_stub = types.ModuleType("core.bridges.orchestration_core_bridge")
    ocb_stub.OrchestrationCoreBridge = object
    sys.modules["core.bridges.orchestration_core_bridge"] = ocb_stub

if "orchestration.brain.consciousness" not in sys.modules:
    oc_stub = types.ModuleType("orchestration.brain.consciousness")
    oc_stub.ConsciousnessCore = object
    sys.modules["orchestration.brain.consciousness"] = oc_stub

# Stub cognitive architecture controller to avoid heavy dependencies
if "consciousness.cognitive_architecture_controller" not in sys.modules:
    cac_stub = types.ModuleType("consciousness.cognitive_architecture_controller")

    class CognitiveResourceManager:
        def __init__(self, *a, **k):
            pass

    cac_stub.CognitiveResourceManager = CognitiveResourceManager
    sys.modules["consciousness.cognitive_architecture_controller"] = cac_stub

if "consciousness.reflection.lambda_mirror" not in sys.modules:
    lm_stub = types.ModuleType("consciousness.reflection.lambda_mirror")

    class AlignmentScore:
        def __init__(self, *a, **k):
            pass

    lm_stub.AlignmentScore = AlignmentScore
    sys.modules["consciousness.reflection.lambda_mirror"] = lm_stub
    sys.modules["consciousness.systems.lambda_mirror"] = lm_stub

# Provide dummy CoreComponent to satisfy hub initialization
import consciousness.cognitive.adapter_complete as adapter_complete


class DummyCoreComponent:
    def __init__(self, *a, **k):
        pass


adapter_complete.CoreComponent = DummyCoreComponent

from consciousness.cognitive.adapter_complete import CognitiveAdapter
from consciousness.consciousness_hub import get_consciousness_hub


class TestCognitiveAdapterCompleteIntegration(unittest.TestCase):
    """Integration tests for CognitiveAdapter within ConsciousnessHub."""

    def test_adapter_registered_in_hub(self):
        hub = get_consciousness_hub()
        asyncio.run(hub.initialize())
        service = hub.get_service("cognitive_adapter")
        self.assertIsNotNone(service)
        self.assertIsInstance(service, CognitiveAdapter)


if __name__ == "__main__":
    unittest.main()
