"""
Symbolic Kernel Bus Integration Examples
========================================

Common patterns for using the new kernel bus in LUKHΛS components.
"""


from lukhas.orchestration.symbolic_kernel_bus import (
    EventPriority,
    SymbolicEffect,
    kernel_bus,
)


# Example 1: Memory fold event
def create_memory_fold(fold_id: str, content: dict):
    """Create a memory fold with proper symbolic effects"""
    kernel_bus.emit(
        "lukhas.memory.fold.init",
        {"fold_id": fold_id, "content": content},
        source="lukhas.memory.manager",
        effects=[SymbolicEffect.MEMORY_FOLD, SymbolicEffect.LOG_TRACE],
        priority=EventPriority.HIGH,
    )


# Example 2: Agent drift detection


def detect_agent_drift(agent_id: str, drift_score: float):
    """Report agent drift to Guardian system"""
    kernel_bus.emit(
        "agent.drift.detected",
        {"agent_id": agent_id, "drift_score": drift_score},
        source="swarm.monitor",
        effects=[SymbolicEffect.DRIFT_DETECT, SymbolicEffect.ETHICS_CHECK],
        priority=EventPriority.HIGH if drift_score > 0.7 else EventPriority.NORMAL,
    )


# Example 3: Plugin loading


def load_plugin(plugin_name: str, config: dict):
    """Load a plugin with registry update"""
    kernel_bus.emit(
        "plugin.loaded",
        {"name": plugin_name, "config": config},
        source="plugin.loader",
        effects=[SymbolicEffect.PLUGIN_LOAD, SymbolicEffect.PLUGIN_UPDATE],
    )


# Example 4: Subscribe to memory events


def handle_memory_event(event):
    """Handle memory-related events"""
    print(f"Memory event: {event.event_type}",
        source="dream.engine",
        effects=[SymbolicEffect.DREAM_TRIGGER, SymbolicEffect.MEMORY_FOLD],
        correlation_id=dream_id,
    )

    # Correlated consciousness update
    kernel_bus.emit(
        "consciousness.state.changed",
        {"state": "dreaming", "dream_id": dream_id},
        source="consciousness.core",
        effects=[SymbolicEffect.AWARENESS_UPDATE],
        correlation_id=dream_id,
    )

    return event_id


# Example 6: Critical safety event


def safety_violation(boundary: str, severity: str = "high"):
    """Report safety boundary violation"""
    kernel_bus.emit(
        "safety.boundary.violated",
        {"boundary": boundary, "severity": severity},
        source="safety.monitor",
        effects=[SymbolicEffect.SAFETY_GATE, SymbolicEffect.ETHICS_CHECK],
        priority=EventPriority.CRITICAL,
    )


# Example 7: Swarm consensus


async def request_swarm_consensus(topic: str, agents: list):
    """Request consensus from agent swarm"""
    kernel_bus.emit(
        "swarm.consensus.required",
        {"topic": topic, "agents": agents, "quorum": len(agents) * 0.6},
        source="swarm.coordinator",
        effects=[SymbolicEffect.SWARM_CONSENSUS, SymbolicEffect.AGENT_SYNC],
        priority=EventPriority.HIGH,
    )


# Example 8: Effect-based subscription


def handle_memory_effects(event):
    """Handle any event with memory effects"""
    if SymbolicEffect.MEMORY_PERSIST in event.effects:
        # Persist to storage
        print(f"Persisting memory from {event.source}")


kernel_bus.subscribe_effect(SymbolicEffect.MEMORY_PERSIST, handle_memory_effects)
