from lukhas_website.lukhas.consciousness.registry import (
from typing import List, Optional
    ComponentType,
    ConsciousnessComponentRegistry,
)


def _register_component(
    registry: ConsciousnessComponentRegistry,
    component_id: str,
    *,
    dependencies: Optional[List[str]] = None,
    priority: int = 50,
) -> None:
    registry.register_component(
        component_id=component_id,
        component_type=ComponentType.CONSCIOUSNESS_REASONING,
        name=f"Component {component_id}",
        description="Test component",
        module_path="tests.unit.consciousness.stub_component",
        constellation_framework="🧠",
        dependencies=dependencies,
        activation_priority=priority,
    )


def test_activation_order_respects_dependencies():
    registry = ConsciousnessComponentRegistry()

    _register_component(registry, "base", dependencies=None, priority=30)
    _register_component(registry, "mid", dependencies=["base"], priority=20)
    _register_component(registry, "top", dependencies=["mid"], priority=10)

    assert registry._activation_order == ["base", "mid", "top"]


def test_activation_order_prioritizes_dependencies_over_priority():
    registry = ConsciousnessComponentRegistry()

    _register_component(registry, "fast", dependencies=None, priority=5)
    _register_component(registry, "slow", dependencies=None, priority=100)
    _register_component(registry, "dependent", dependencies=["slow"], priority=1)

    order = registry._activation_order
    assert order.index("slow") < order.index("dependent")


def test_activation_order_handles_cycles_and_missing_dependencies():
    registry = ConsciousnessComponentRegistry()

    _register_component(registry, "cycle_a", dependencies=["cycle_b"], priority=15)
    _register_component(registry, "cycle_b", dependencies=["cycle_a"], priority=10)
    _register_component(registry, "orphan", dependencies=["unknown"], priority=5)

    order = registry._activation_order
    assert set(order) == {"cycle_a", "cycle_b", "orphan"}
    assert len(order) == 3
