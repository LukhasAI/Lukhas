#!/usr/bin/env python3
import logging
from core.core_hub import get_core_hub
from memory.memory_hub import get_memory_hub
from consciousness.consciousness_hub import get_consciousness_hub
from orchestration.orchestration_hub import get_orchestration_hub
from dast.dast_integration_hub import get_dast_hub
# from abas.abas_integration_hub import get_abas_hub
from nias.integration.nias_integration_hub import get_nias_hub

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_all_hubs():
    hubs = {
        "core": get_core_hub(),
        "memory": get_memory_hub(),
        "consciousness": get_consciousness_hub(),
        "orchestration": get_orchestration_hub(),
        "dast": get_dast_hub(),
        "abas": get_abas_hub(),
        "nias": get_nias_hub()
    }

    for hub_name, hub_instance in hubs.items():
        for other_name, other_instance in hubs.items():
            if hub_name != other_name:
                hub_instance.connect_to_hub(other_name, other_instance)
                logger.info(f"Connected {hub_name} -> {other_name}")

    test_message = {"id": "test_001", "type": "system_check", "content": "Hub connectivity test"}
    responses = hubs["core"].broadcast_to_all_hubs(test_message)

    for hub_name, response in responses.items():
        if "error" not in response:
            logger.info(f"✅ {hub_name}: Connected successfully")
        else:
            logger.error(f"❌ {hub_name}: Connection failed - {response['error']}")

    logger.info(f"\n🎉 System integration complete! All {len(hubs)} hubs connected.")
    return hubs

if __name__ == "__main__":
    connect_all_hubs()
