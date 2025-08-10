from core.bridges.core_consciousness_bridge import CoreConsciousnessBridge
from core.bridges.core_safety_bridge import CoreSafetyBridge
from core.core_hub import get_core_hub


def test_core_hub_bridge_registration():
    hub = get_core_hub()
    conc_bridge = hub.get_service("consciousness_bridge")
    safe_bridge = hub.get_service("safety_bridge")
    assert isinstance(conc_bridge, CoreConsciousnessBridge)
    assert isinstance(safe_bridge, CoreSafetyBridge)
