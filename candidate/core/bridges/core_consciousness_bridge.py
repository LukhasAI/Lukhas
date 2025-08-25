"""Core-Consciousness Bridge

Bidirectional communication between the core and consciousness systems.
"""

from typing import Any, Optional


class MockSystem:
    """A mock system to simulate core or consciousness for bridging."""

    def __init__(self, name: str):
        self.name = name
        self.state = {"status": "initialized"}

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        print(f"[{self.name}] Received data: {data}")
        self.state.update(data)
        return {"status": "processed", "source": self.name}

    def get_state(self) -> dict[str, Any]:
        return self.state

    def set_state(self, new_state: dict[str, Any]):
        self.state = new_state
        print(f"[{self.name}] State updated: {self.state}")

    async def handle_event(self, event: dict[str, Any]):
        print(f"[{self.name}] Event handled: {event.get('type')}")


class CoreConsciousnessBridge:
    """Bridge connecting core and consciousness modules."""

    def __init__(
        self,
        core_system: Optional[Any] = None,
        consciousness_system: Optional[Any] = None,
    ) -> None:
        # If no systems are provided, create mock ones for simulation.
        self.core_system = core_system if core_system else MockSystem("Core")
        self.consciousness_system = (
            consciousness_system
            if consciousness_system
            else MockSystem("Consciousness")
        )

    async def core_to_consciousness(self, data: dict[str, Any]) -> dict[str, Any]:
        """Send data from core to the consciousness system."""
        if not hasattr(self.consciousness_system, "process"):
            return {
                "status": "error",
                "message": "Consciousness system cannot process data.",
            }
        return await self.consciousness_system.process(data)

    async def consciousness_to_core(self, data: dict[str, Any]) -> dict[str, Any]:
        """Send data from consciousness to the core system."""
        if not hasattr(self.core_system, "process"):
            return {"status": "error", "message": "Core system cannot process data."}
        return await self.core_system.process(data)

    async def sync_state(self, from_core_to_consciousness: bool = True) -> None:
        """
        Synchronize state between systems.
        By default, syncs from core to consciousness.
        """
        if from_core_to_consciousness:
            source, dest = self.core_system, self.consciousness_system
        else:
            source, dest = self.consciousness_system, self.core_system

        if hasattr(source, "get_state") and hasattr(dest, "set_state"):
            state_to_sync = source.get_state()
            dest.set_state(state_to_sync)
            print(f"State synced from {source.name} to {dest.name}")

    async def handle_event(self, event: dict[str, Any]) -> None:
        """
        Handle cross-system events by forwarding them.
        Assumes event has a 'destination' key ('core' or 'consciousness').
        """
        destination = event.get("destination")
        if destination == "consciousness" and hasattr(
            self.consciousness_system, "handle_event"
        ):
            await self.consciousness_system.handle_event(event)
        elif destination == "core" and hasattr(self.core_system, "handle_event"):
            await self.core_system.handle_event(event)
        else:
            print(f"Could not route event: unknown destination '{destination}'")
