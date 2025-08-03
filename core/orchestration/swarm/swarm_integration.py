#!/usr/bin/env python3
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
        self.event_bus.subscribe('colony.formed', self._on_colony_formed)
        self.event_bus.subscribe('colony.task_assigned', self._on_task_assigned)

        # Swarm events
        self.event_bus.subscribe('swarm.intelligence_update', self._on_swarm_update)
        self.event_bus.subscribe('swarm.consensus_reached', self._on_consensus)

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
