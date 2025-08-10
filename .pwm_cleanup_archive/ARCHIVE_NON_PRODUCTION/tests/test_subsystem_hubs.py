import pytest

try:
    from core.bridges.identity_core_bridge import IdentityCoreBridge
    from identity.identity_hub import get_identity_hub

    _IDENTITY_AVAILABLE = True
except Exception:
    _IDENTITY_AVAILABLE = False
try:
    from core.bridges.memory_consciousness_bridge import (
        MemoryConsciousnessBridge,
    )
    from core.bridges.memory_learning_bridge import MemoryLearningBridge
    from memory.memory_hub import get_memory_hub

    _MEMORY_AVAILABLE = True
except Exception:
    _MEMORY_AVAILABLE = False

try:
    from core.bridges.orchestration_core_bridge import OrchestrationCoreBridge
    from orchestration.orchestration_hub import get_orchestration_hub

    _ORCH_AVAILABLE = True
except Exception:
    _ORCH_AVAILABLE = False

try:
    from core.bridges.quantum_memory_bridge import QuantumMemoryBridge
    from quantum.quantum_hub import get_quantum_hub

    _QUANTUM_AVAILABLE = True
except Exception:
    _QUANTUM_AVAILABLE = False

try:
    from consciousness.consciousness_hub import get_consciousness_hub
    from core.bridges.consciousness_quantum_bridge import (
        ConsciousnessQuantumBridge,
    )
    from core.bridges.memory_consciousness_bridge import (
        MemoryConsciousnessBridge,
    )

    _CONSC_AVAILABLE = True
except Exception:
    _CONSC_AVAILABLE = False


@pytest.mark.skipif(not _IDENTITY_AVAILABLE, reason="identity hub not available")
def test_identity_hub_bridge_registration():
    hub = get_identity_hub()
    bridge = hub.get_service("core_bridge")
    assert isinstance(bridge, IdentityCoreBridge)


@pytest.mark.skipif(not _MEMORY_AVAILABLE, reason="memory hub not available")
def test_memory_hub_bridge_registration():
    hub = get_memory_hub()
    bridge = hub.get_service("learning_bridge")
    assert isinstance(bridge, MemoryLearningBridge)
    bridge2 = hub.get_service("consciousness_bridge")
    assert isinstance(bridge2, MemoryConsciousnessBridge)


@pytest.mark.skipif(not _ORCH_AVAILABLE, reason="orchestration hub not available")
def test_orchestration_hub_bridge_registration():
    hub = get_orchestration_hub()
    bridge = hub.get_service("core_bridge")
    assert isinstance(bridge, OrchestrationCoreBridge)


@pytest.mark.skipif(not _QUANTUM_AVAILABLE, reason="quantum hub not available")
def test_quantum_hub_bridge_registration():
    hub = get_quantum_hub()
    bridge = hub.get_service("memory_bridge")
    assert isinstance(bridge, QuantumMemoryBridge)


@pytest.mark.skipif(not _CONSC_AVAILABLE, reason="consciousness hub not available")
def test_consciousness_hub_bridge_registration():
    hub = get_consciousness_hub()
    bridge = hub.get_service("quantum_bridge")
    assert isinstance(bridge, ConsciousnessQuantumBridge)
    bridge2 = hub.get_service("memory_bridge")
    assert isinstance(bridge2, MemoryConsciousnessBridge)
