"""
Integration tests for MetaLearningEnhancement module

Tests the integration of the Meta-Learning Enhancement System
from labs/consciousness/reflection to matriz/consciousness/reflection
"""

import pytest


def test_import_meta_learning_enhancement():
    """Test that MetaLearningEnhancement can be imported from new location"""
    from matriz.consciousness.reflection.MetaLearningEnhancement import (
        EnhancementMode,
        MetaLearningEnhancementSystem,
        SystemIntegrationStatus,
    )

    assert MetaLearningEnhancementSystem is not None
    assert EnhancementMode is not None
    assert SystemIntegrationStatus is not None


def test_meta_learning_enhancement_instantiation():
    """Test that MetaLearningEnhancementSystem can be instantiated"""
    from matriz.consciousness.reflection.MetaLearningEnhancement import (
        EnhancementMode,
        MetaLearningEnhancementSystem,
    )

    # Test basic instantiation
    system = MetaLearningEnhancementSystem(
        node_id="test_node", enhancement_mode=EnhancementMode.MONITORING_ONLY
    )

    assert system.node_id == "test_node"
    assert system.enhancement_mode == EnhancementMode.MONITORING_ONLY
    assert system.monitor_dashboard is not None
    assert system.rate_modulator is not None
    assert system.symbolic_feedback is not None


def test_meta_learning_enhancement_with_federation():
    """Test MetaLearningEnhancementSystem with federation enabled"""
    from matriz.consciousness.reflection.MetaLearningEnhancement import (
        EnhancementMode,
        MetaLearningEnhancementSystem,
    )
    from labs.core.meta_learning.federated_integration import FederationStrategy

    # Test with federation enabled
    system = MetaLearningEnhancementSystem(
        node_id="test_federation_node",
        enhancement_mode=EnhancementMode.FEDERATED_COORDINATION,
        enable_federation=True,
        federation_strategy=FederationStrategy.BALANCED_HYBRID,
    )

    assert system.enable_federation is True
    assert system.federated_integration is not None
    assert system.federated_integration.initialized is True


@pytest.mark.asyncio
async def test_discover_and_enhance_systems():
    """Test the discover_and_enhance_meta_learning_systems method"""
    from matriz.consciousness.reflection.MetaLearningEnhancement import (
        EnhancementMode,
        MetaLearningEnhancementSystem,
    )

    system = MetaLearningEnhancementSystem(
        node_id="test_discovery", enhancement_mode=EnhancementMode.OPTIMIZATION_ACTIVE
    )

    # Test discovery method
    result = await system.discover_and_enhance_meta_learning_systems()

    assert "search_initiated" in result
    assert "systems_discovered" in result
    assert "enhancement_results" in result
    assert "integration_summary" in result
