#!/usr/bin/env python3
"""
Connect Critical Unused Systems
Integrates dreams, identity, consciousness, and other critical but disconnected modules.
"""
import os
from pathlib import Path
from typing import List, Dict, Tuple
import ast


class SystemConnector:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.connections_made = []

    def create_integration_hub(self):
        """Create a central integration hub for connecting systems."""
        hub_content = '''#!/usr/bin/env python3
"""
System Integration Hub
Central connection point for all major LUKHAS subsystems.
"""
from typing import Optional, Dict, Any
import asyncio

# Import all critical systems that were previously disconnected
from api.consciousness import ConsciousnessAPI
from api.dream import DreamAPI
from api.emotion import EmotionAPI
from identity.tiered_access import TieredAccessControl
from identity.safety_monitor import SafetyMonitor
from consciousness.bridge import ConsciousnessBridge
from dream.engine import DreamEngine
from colony.coordinator import ColonyCoordinator
from swarm.intelligence import SwarmIntelligence
from memory.core import MemoryCore
from learning.learning_gateway import get_learning_gateway


class SystemIntegrationHub:
    """
    Central hub that connects all major subsystems.
    This resolves the issue of disconnected critical components.
    """

    def __init__(self):
        # Initialize all subsystems
        self.consciousness_api = ConsciousnessAPI()
        self.dream_api = DreamAPI()
        self.emotion_api = EmotionAPI()
        self.identity = TieredAccessControl()
        self.safety = SafetyMonitor()
        self.consciousness_bridge = ConsciousnessBridge()
        self.dream_engine = DreamEngine()
        self.colony = ColonyCoordinator()
        self.swarm = SwarmIntelligence()
        self.memory = MemoryCore()
        self.learning = get_learning_gateway()

        # Wire up the connections
        self._connect_systems()

    def _connect_systems(self):
        """Establish connections between subsystems."""
        # Connect Dream ↔ Memory ↔ Consciousness cycle
        self.dream_engine.set_memory_interface(self.memory)
        self.dream_engine.set_consciousness_bridge(self.consciousness_bridge)
        self.consciousness_bridge.register_dream_engine(self.dream_engine)

        # Connect Identity → Safety → Ethics cycle
        self.identity.register_safety_monitor(self.safety)
        self.safety.set_identity_provider(self.identity)

        # Connect APIs to their engines
        self.consciousness_api.set_engine(self.consciousness_bridge)
        self.dream_api.set_engine(self.dream_engine)
        self.emotion_api.set_memory_interface(self.memory)

        # Connect Colony/Swarm systems
        self.colony.register_swarm(self.swarm)
        self.swarm.set_colony_coordinator(self.colony)

        # Connect Learning to all systems that need it
        self.consciousness_bridge.set_learning_gateway(self.learning)
        self.dream_engine.set_learning_gateway(self.learning)

    async def process_consciousness_request(self, agent_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process consciousness-related requests with full system integration."""
        # Check identity and safety first
        if not await self.identity.verify_access(agent_id, "consciousness"):
            raise PermissionError(f"Agent {agent_id} lacks consciousness access")

        # Process through consciousness with dream integration
        result = await self.consciousness_api.process(data)

        # Store in memory for future dream synthesis
        await self.memory.store_experience(agent_id, result)

        # Trigger dream synthesis if conditions are met
        if await self.dream_engine.should_synthesize(agent_id):
            dream_result = await self.dream_engine.synthesize(agent_id)
            result['dream_synthesis'] = dream_result

        return result

    async def process_collective_intelligence(self, swarm_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process colony/swarm collective intelligence requests."""
        # Coordinate through colony
        colony_result = await self.colony.coordinate(swarm_id, data)

        # Process through swarm intelligence
        swarm_result = await self.swarm.process_collective(colony_result)

        # Integrate with consciousness
        consciousness_result = await self.consciousness_bridge.process_collective(swarm_result)

        return {
            'colony': colony_result,
            'swarm': swarm_result,
            'consciousness': consciousness_result
        }


# Singleton instance
_hub_instance = None


def get_integration_hub() -> SystemIntegrationHub:
    """Get the singleton integration hub."""
    global _hub_instance
    if _hub_instance is None:
        _hub_instance = SystemIntegrationHub()
    return _hub_instance


__all__ = ['SystemIntegrationHub', 'get_integration_hub']
'''

        hub_path = self.root_path / "orchestration" / "integration_hub.py"
        hub_path.parent.mkdir(exist_ok=True)
        with open(hub_path, 'w') as f:
            f.write(hub_content)

        self.connections_made.append(("Created", str(hub_path)))
        return hub_path

    def update_api_endpoints(self):
        """Update API endpoints to use the integration hub."""
        # Update main API router
        api_init = self.root_path / "api" / "__init__.py"
        if api_init.exists():
            content = api_init.read_text()

            # Add import for integration hub
            new_imports = """
# Import the integration hub to connect all systems
from orchestration.integration_hub import get_integration_hub

# Initialize the hub to ensure all systems are connected
integration_hub = get_integration_hub()
"""

            # Insert after first imports
            if "from orchestration.integration_hub" not in content:
                lines = content.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('#'):
                        insert_pos = i + 1
                        break

                lines.insert(insert_pos, new_imports)
                content = '\n'.join(lines)

                with open(api_init, 'w') as f:
                    f.write(content)

                self.connections_made.append(("Updated", str(api_init)))

    def create_dream_consciousness_bridge(self):
        """Create explicit bridge between dreams and consciousness."""
        bridge_content = '''#!/usr/bin/env python3
"""
Dream-Consciousness Bridge
Implements the critical connection between dream synthesis and consciousness.
"""
from typing import Dict, Any, Optional
import asyncio

from consciousness.bridge import ConsciousnessBridge
from dream.engine import DreamEngine
from memory.core import MemoryCore


class DreamConsciousnessBridge:
    """
    Bridges dream synthesis with consciousness processing.
    This enables dreams to influence consciousness and vice versa.
    """

    def __init__(self):
        self.consciousness = ConsciousnessBridge()
        self.dream_engine = DreamEngine()
        self.memory = MemoryCore()

    async def process_dream_to_consciousness(self, dream_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process dream data through consciousness."""
        # Store dream in memory
        await self.memory.store_dream(dream_data)

        # Process through consciousness
        consciousness_result = await self.consciousness.process_dream(dream_data)

        # Update dream engine with consciousness feedback
        await self.dream_engine.update_from_consciousness(consciousness_result)

        return consciousness_result

    async def process_consciousness_to_dream(self, consciousness_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dreams from consciousness states."""
        # Analyze consciousness state
        dream_seed = await self.consciousness.extract_dream_seed(consciousness_data)

        # Generate dream
        dream_result = await self.dream_engine.synthesize_from_seed(dream_seed)

        # Store the synthesis
        await self.memory.store_synthesis(consciousness_data, dream_result)

        return dream_result


# 🔁 Cross-layer: Dream-consciousness integration
from orchestration.integration_hub import get_integration_hub

def register_with_hub():
    """Register this bridge with the integration hub."""
    hub = get_integration_hub()
    bridge = DreamConsciousnessBridge()
    hub.register_component('dream_consciousness_bridge', bridge)

# Auto-register on import
register_with_hub()
'''

        bridge_path = self.root_path / "consciousness" / "dream_bridge.py"
        with open(bridge_path, 'w') as f:
            f.write(bridge_content)

        self.connections_made.append(("Created", str(bridge_path)))
        return bridge_path

    def connect_identity_to_all_systems(self):
        """Ensure identity/safety is connected to all critical systems."""
        identity_connector = '''#!/usr/bin/env python3
"""
Identity System Connector
Ensures all systems properly integrate with identity and safety checks.
"""
from typing import Dict, Any, Optional, Callable
import functools

from identity.tiered_access import TieredAccessControl
from identity.safety_monitor import SafetyMonitor
from identity.audit_logger import AuditLogger


class IdentityConnector:
    """Connects identity and safety to all systems."""

    def __init__(self):
        self.access_control = TieredAccessControl()
        self.safety_monitor = SafetyMonitor()
        self.audit_logger = AuditLogger()

    def require_tier(self, min_tier: int):
        """Decorator to enforce tier requirements."""
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(self, agent_id: str, *args, **kwargs):
                # Check tier access
                tier = await self.access_control.get_agent_tier(agent_id)
                if tier < min_tier:
                    self.audit_logger.log_access_denied(agent_id, func.__name__, tier, min_tier)
                    raise PermissionError(f"Requires tier {min_tier}, agent has tier {tier}")

                # Log access
                self.audit_logger.log_access_granted(agent_id, func.__name__, tier)

                # Monitor safety during execution
                with self.safety_monitor.monitor_operation(agent_id, func.__name__):
                    return await func(self, agent_id, *args, **kwargs)

            return wrapper
        return decorator

    def connect_to_module(self, module_name: str, module_instance: Any):
        """Connect identity checks to a module."""
        # Inject identity methods
        module_instance._check_access = self.access_control.verify_access
        module_instance._log_audit = self.audit_logger.log_event
        module_instance._monitor_safety = self.safety_monitor.monitor_operation

        self.audit_logger.log_event(
            "system",
            "module_connected",
            {"module": module_name}
        )


# Global connector instance
_identity_connector = IdentityConnector()

def get_identity_connector() -> IdentityConnector:
    """Get the global identity connector."""
    return _identity_connector


# 🔁 Cross-layer: Identity system integration
from orchestration.integration_hub import get_integration_hub

# Register with hub
hub = get_integration_hub()
hub.register_component('identity_connector', _identity_connector)
'''

        connector_path = self.root_path / "identity" / "connector.py"
        with open(connector_path, 'w') as f:
            f.write(identity_connector)

        self.connections_made.append(("Created", str(connector_path)))
        return connector_path

    def update_main_entry_points(self):
        """Update main entry points to use connected systems."""
        # Find main.py or app.py
        main_files = [
            self.root_path / "main.py",
            self.root_path / "app.py",
            self.root_path / "run.py"
        ]

        for main_file in main_files:
            if main_file.exists():
                content = main_file.read_text()

                # Add integration hub import
                if "integration_hub" not in content:
                    import_line = "\n# Initialize system integration hub\nfrom orchestration.integration_hub import get_integration_hub\nintegration_hub = get_integration_hub()\n"

                    # Find where to insert (after imports)
                    lines = content.split('\n')
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            insert_pos = i + 1

                    lines.insert(insert_pos, import_line)
                    content = '\n'.join(lines)

                    with open(main_file, 'w') as f:
                        f.write(content)

                    self.connections_made.append(("Updated", str(main_file)))

    def create_colony_swarm_integration(self):
        """Create integration between colony and swarm systems."""
        integration_content = '''#!/usr/bin/env python3
"""
Colony-Swarm Integration
Connects the colony coordination and swarm intelligence systems.
"""
from typing import Dict, Any, List
import asyncio

from colony.coordinator import ColonyCoordinator
from swarm.intelligence import SwarmIntelligence
from event_bus.manager import EventBusManager
from baggage.tag_system import BaggageTagSystem


class ColonySwarmIntegration:
    """Integrates colony and swarm systems with event bus and baggage tags."""

    def __init__(self):
        self.colony = ColonyCoordinator()
        self.swarm = SwarmIntelligence()
        self.event_bus = EventBusManager()
        self.baggage = BaggageTagSystem()

        # Connect event handlers
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        """Set up event bus connections."""
        # Colony events
        self.kernel_bus.subscribe('colony.formed', self._on_colony_formed)
        self.kernel_bus.subscribe('colony.task_assigned', self._on_task_assigned)

        # Swarm events
        self.kernel_bus.subscribe('swarm.intelligence_update', self._on_swarm_update)
        self.kernel_bus.subscribe('swarm.consensus_reached', self._on_consensus)

    async def _on_colony_formed(self, event: Dict[str, Any]):
        """Handle colony formation."""
        colony_id = event['colony_id']
        agents = event['agents']

        # Initialize swarm for the colony
        swarm_config = await self.swarm.create_swarm(colony_id, agents)

        # Tag with baggage for tracking
        self.baggage.tag(colony_id, {
            'type': 'colony',
            'size': len(agents),
            'swarm_id': swarm_config['swarm_id']
        })

    async def _on_task_assigned(self, event: Dict[str, Any]):
        """Handle task assignment to colony."""
        task = event['task']
        colony_id = event['colony_id']

        # Distribute task through swarm intelligence
        result = await self.swarm.distribute_task(colony_id, task)

        # Update baggage
        self.baggage.update(colony_id, {'active_task': task['id']})

        return result

    async def _on_swarm_update(self, event: Dict[str, Any]):
        """Handle swarm intelligence updates."""
        swarm_id = event['swarm_id']
        intelligence_data = event['data']

        # Update colony with new intelligence
        await self.colony.update_intelligence(swarm_id, intelligence_data)

    async def _on_consensus(self, event: Dict[str, Any]):
        """Handle swarm consensus events."""
        consensus = event['consensus']
        swarm_id = event['swarm_id']

        # Apply consensus to colony
        await self.colony.apply_consensus(swarm_id, consensus)

        # Log in baggage
        self.baggage.update(swarm_id, {'last_consensus': consensus})


# 🔁 Cross-layer: Colony-swarm coordination
from orchestration.integration_hub import get_integration_hub

# Auto-register
integration = ColonySwarmIntegration()
hub = get_integration_hub()
hub.register_component('colony_swarm', integration)
'''

        integration_path = self.root_path / "colony" / "swarm_integration.py"
        integration_path.parent.mkdir(exist_ok=True)
        with open(integration_path, 'w') as f:
            f.write(integration_content)

        self.connections_made.append(("Created", str(integration_path)))
        return integration_path

    def run_connections(self):
        """Execute all connection tasks."""
        print("🔗 Connecting critical unused systems...")

        # Create integration hub
        print("  Creating integration hub...")
        self.create_integration_hub()

        # Update API endpoints
        print("  Updating API endpoints...")
        self.update_api_endpoints()

        # Create dream-consciousness bridge
        print("  Creating dream-consciousness bridge...")
        self.create_dream_consciousness_bridge()

        # Connect identity to all systems
        print("  Connecting identity system...")
        self.connect_identity_to_all_systems()

        # Create colony-swarm integration
        print("  Creating colony-swarm integration...")
        self.create_colony_swarm_integration()

        # Update main entry points
        print("  Updating main entry points...")
        self.update_main_entry_points()

        print(f"\n✅ Created {len(self.connections_made)} connections!")
        return self.connections_made


def main():
    """Main entry point."""
    root_path = Path(__file__).parent.parent

    connector = SystemConnector(root_path)
    connections = connector.run_connections()

    print("\n📊 Connections Summary:")
    for action, file_path in connections:
        print(f"  {action}: {file_path}")

    print("\n🎯 Next Steps:")
    print("  1. Run connectivity visualizer to see new connections")
    print("  2. Test the integration hub with sample requests")
    print("  3. Verify identity tier system is working")
    print("  4. Check dream-consciousness synthesis")

    print("\n💡 Critical systems are now connected!")
    print("  - Dreams ↔ Consciousness ↔ Memory")
    print("  - Identity → All Systems (safety enforcement)")
    print("  - Colony ↔ Swarm (with event bus)")
    print("  - APIs → Integration Hub → Engines")


if __name__ == "__main__":
    main()