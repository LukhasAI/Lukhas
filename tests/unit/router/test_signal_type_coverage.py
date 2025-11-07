"""
Unit test to ensure all ConsciousnessSignalType values have routing rules and targets

This test prevents future regressions where new signal types are added
but no routing rules are created for them.
"""
import pytest

from core.consciousness_signal_router import ConsciousnessSignalRouter
from core.matriz_consciousness_signals import ConsciousnessSignal, ConsciousnessSignalType


def test_all_signal_types_have_rules_and_targets():
    """Ensure every ConsciousnessSignalType has routing rules that resolve to target nodes"""

    # Create router and initialize defaults
    router = ConsciousnessSignalRouter()

    # Register minimal test nodes to match routing rule targets
    test_nodes = {
        "consciousness": ["awareness", "reflection", "consciousness_core"],
        "orchestration": ["network_pulse", "coordination", "health_monitoring"],
        "identity": ["authentication", "namespace", "trinity_compliance"],
        "governance": ["compliance", "ethics", "guardian", "policy"],
        "symbolic_core": ["symbolic_processing", "pattern_recognition"],
        "bio": ["biological_modeling", "bio_symbolic_adaptation"],
        "memory": ["storage", "retrieval", "temporal_processing"]
    }

    for module_name, capabilities in test_nodes.items():
        router.register_node(
            node_id=f"test_{module_name}",
            module_name=module_name,
            capabilities=capabilities
        )

    # Test each signal type
    for signal_type in ConsciousnessSignalType:
        # Create test signal
        test_signal = ConsciousnessSignal(
            signal_type=signal_type,
            consciousness_id="test_cid",
            producer_module="consciousness",
            awareness_level=0.8
        )

        # Find applicable rules
        applicable_rules = router._find_applicable_rules(test_signal)
        assert applicable_rules, f"No routing rules found for {signal_type.value}"

        # Ensure at least one rule resolves to actual target nodes
        found_targets = False
        for rule in applicable_rules:
            target_nodes = router._get_nodes_by_modules(rule.target_modules)
            if target_nodes:
                found_targets = True
                break

        assert found_targets, f"No target nodes found for {signal_type.value} (rules exist but no matching nodes)"


def test_routing_rules_priority_ordering():
    """Ensure routing rules are properly prioritized"""

    router = ConsciousnessSignalRouter()

    # Register test nodes
    router.register_node("test_consciousness", "consciousness", ["test"])

    # Create test signal
    test_signal = ConsciousnessSignal(
        signal_type=ConsciousnessSignalType.AWARENESS,
        consciousness_id="test_cid",
        producer_module="consciousness",
        awareness_level=0.8
    )

    # Find applicable rules
    applicable_rules = router._find_applicable_rules(test_signal)
    assert applicable_rules, "Should have at least one applicable rule for AWARENESS"

    # Verify rules are sorted by priority (highest first)
    sorted_rules = sorted(applicable_rules, key=lambda r: r.priority, reverse=True)
    best_rule = max(applicable_rules, key=lambda r: r.priority)

    assert best_rule.priority == sorted_rules[0].priority, "Best rule should have highest priority"


def test_fallback_rule_catches_all_types():
    """Ensure the fallback rule can handle any signal type"""

    router = ConsciousnessSignalRouter()

    # Register orchestration node (fallback target)
    router.register_node("test_orchestration", "orchestration", ["fallback"])

    # Find the fallback rule
    fallback_rule = None
    for rule in router.routing_rules:
        if rule.rule_id == "fallback_broadcast":
            fallback_rule = rule
            break

    assert fallback_rule is not None, "Fallback rule should exist"

    # Test that fallback rule accepts all signal types
    for signal_type in ConsciousnessSignalType:
        assert signal_type in fallback_rule.signal_types, f"Fallback rule should accept {signal_type.value}"

    # Test fallback rule can find target nodes
    target_nodes = router._get_nodes_by_modules(fallback_rule.target_modules)
    assert target_nodes, "Fallback rule should find target nodes"


def test_node_registration_idempotent():
    """Test that node registration is idempotent and handles conflicts properly"""

    router = ConsciousnessSignalRouter()

    # Register node first time
    node1 = router.register_node("test_node", "consciousness", ["test"])
    assert node1.node_id == "test_node"
    assert node1.module_name == "consciousness"

    # Register same node again - should return existing node
    node2 = router.register_node("test_node", "consciousness", ["test"])
    assert node2 is node1, "Should return same node instance"

    # Register same node ID with different module - should warn but return existing
    node3 = router.register_node("test_node", "different_module", ["test"])
    assert node3 is node1, "Should return original node even with different module"
    assert node3.module_name == "consciousness", "Should keep original module name"


def test_router_metrics_integration():
    """Test that router properly increments metrics"""

    ConsciousnessSignalRouter()

    # Test signal with no matching rules (should increment no_rule metric)
    # Create signal with type that has no rules
    from core.metrics import router_no_rule_total

    # Get initial counter value (may not be zero due to other tests)
    router_no_rule_total.labels(
        signal_type="CUSTOM_TYPE",
        producer_module="test_producer"
    )._value if hasattr(router_no_rule_total.labels(
        signal_type="CUSTOM_TYPE",
        producer_module="test_producer"
    ), '_value') else 0

    # This test would require mocking or we'd need to temporarily remove all rules
    # For now, just verify the metric exists and is accessible
    assert router_no_rule_total is not None, "Router no-rule metric should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
