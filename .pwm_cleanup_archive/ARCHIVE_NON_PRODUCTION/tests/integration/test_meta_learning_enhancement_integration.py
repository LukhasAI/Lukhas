"""
Integration tests for Meta-Learning Enhancement System
Tests for Agent 1 Task 4: core/meta_learning/enhancement_system.py integration
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.meta_learning.enhancement_system import (
    EnhancementMode,
    MetaLearningEnhancementSystem,
    SystemIntegrationStatus,
)


class TestMetaLearningEnhancementIntegration:
    """Test suite for meta-learning enhancement system integration"""

    def test_enhancement_mode_enum(self):
        """Test enhancement mode enumeration completeness"""
        assert hasattr(EnhancementMode, "MONITORING_ONLY")
        assert hasattr(EnhancementMode, "OPTIMIZATION_ACTIVE")
        assert hasattr(EnhancementMode, "FEDERATED_COORDINATION")
        assert hasattr(EnhancementMode, "RESEARCH_MODE")

        # Test enum values
        assert EnhancementMode.MONITORING_ONLY.value == "monitoring_only"
        assert EnhancementMode.OPTIMIZATION_ACTIVE.value == "optimization_active"
        assert EnhancementMode.FEDERATED_COORDINATION.value == "federated_coord"
        assert EnhancementMode.RESEARCH_MODE.value == "research_mode"

    def test_system_integration_status(self):
        """Test system integration status data structure"""
        # Test creating a basic status
        from datetime import datetime

        status = SystemIntegrationStatus(
            meta_learning_systems_found=5,
            systems_enhanced=3,
            monitoring_active=True,
            rate_optimization_active=True,
            symbolic_feedback_active=False,
            federation_enabled=False,
            last_health_check=datetime.now(),
            integration_errors=[],
        )

        assert status.meta_learning_systems_found == 5
        assert status.systems_enhanced == 3
        assert status.monitoring_active is True
        assert status.rate_optimization_active is True
        assert status.symbolic_feedback_active is False
        assert status.federation_enabled is False
        assert isinstance(status.integration_errors, list)

    def test_enhancement_system_initialization(self):
        """Test enhancement system initialization"""
        # Test with default parameters
        enhancement = MetaLearningEnhancementSystem()

        assert enhancement.node_id == "lukhas_primary"
        assert enhancement.enhancement_mode == EnhancementMode.OPTIMIZATION_ACTIVE
        assert enhancement.enable_federation is False
        assert hasattr(enhancement, "monitor_dashboard")
        assert hasattr(enhancement, "rate_modulator")
        assert hasattr(enhancement, "symbolic_feedback")
        assert hasattr(enhancement, "integration_status")

        # Test with custom parameters
        custom_enhancement = MetaLearningEnhancementSystem(
            node_id="test_node",
            enhancement_mode=EnhancementMode.MONITORING_ONLY,
            enable_federation=False,
        )

        assert custom_enhancement.node_id == "test_node"
        assert custom_enhancement.enhancement_mode == EnhancementMode.MONITORING_ONLY
        assert custom_enhancement.enable_federation is False

    def test_enhancement_system_components(self):
        """Test enhancement system component availability"""
        enhancement = MetaLearningEnhancementSystem()

        # Test monitor dashboard component
        assert hasattr(enhancement, "monitor_dashboard")
        assert enhancement.monitor_dashboard is not None

        # Test rate modulator component
        assert hasattr(enhancement, "rate_modulator")
        assert enhancement.rate_modulator is not None

        # Test symbolic feedback component
        assert hasattr(enhancement, "symbolic_feedback")
        assert enhancement.symbolic_feedback is not None

        # Test federated integration (should be None when disabled)
        assert hasattr(enhancement, "federated_integration")
        assert enhancement.federated_integration is None

    def test_enhancement_system_state_tracking(self):
        """Test enhancement system state and tracking capabilities"""
        enhancement = MetaLearningEnhancementSystem()

        # Test state tracking attributes
        assert hasattr(enhancement, "enhanced_systems")
        assert isinstance(enhancement.enhanced_systems, list)

        assert hasattr(enhancement, "enhancement_history")
        assert isinstance(enhancement.enhancement_history, list)

        assert hasattr(enhancement, "coordination_events")
        assert isinstance(enhancement.coordination_events, list)

        assert hasattr(enhancement, "ethical_audit_trail")
        assert isinstance(enhancement.ethical_audit_trail, list)

    def test_integration_status_initial_state(self):
        """Test integration status initial state"""
        enhancement = MetaLearningEnhancementSystem()
        status = enhancement.integration_status

        assert status.meta_learning_systems_found == 0
        assert status.systems_enhanced == 0
        assert status.monitoring_active is False
        assert status.rate_optimization_active is False
        assert status.symbolic_feedback_active is False
        assert status.federation_enabled is False
        assert isinstance(status.integration_errors, list)
        assert len(status.integration_errors) == 0

    @pytest.mark.asyncio
    async def test_core_methods_existence(self):
        """Test that all core methods exist and are callable"""
        enhancement = MetaLearningEnhancementSystem()

        # Test discover_and_enhance_meta_learning_systems method
        assert hasattr(enhancement, "discover_and_enhance_meta_learning_systems")
        assert callable(enhancement.discover_and_enhance_meta_learning_systems)

        # Test start_enhancement_operations method
        assert hasattr(enhancement, "start_enhancement_operations")
        assert callable(enhancement.start_enhancement_operations)

        # Test run_enhancement_cycle method
        assert hasattr(enhancement, "run_enhancement_cycle")
        assert callable(enhancement.run_enhancement_cycle)

    def test_federated_integration_disabled(self):
        """Test federated integration when disabled"""
        enhancement = MetaLearningEnhancementSystem(enable_federation=False)

        assert enhancement.federated_integration is None
        assert enhancement.integration_status.federation_enabled is False

    def test_enhancement_mode_configurations(self):
        """Test different enhancement mode configurations"""
        # Test monitoring only mode
        monitoring_enhancement = MetaLearningEnhancementSystem(
            enhancement_mode=EnhancementMode.MONITORING_ONLY
        )
        assert (
            monitoring_enhancement.enhancement_mode == EnhancementMode.MONITORING_ONLY
        )

        # Test optimization active mode
        optimization_enhancement = MetaLearningEnhancementSystem(
            enhancement_mode=EnhancementMode.OPTIMIZATION_ACTIVE
        )
        assert (
            optimization_enhancement.enhancement_mode
            == EnhancementMode.OPTIMIZATION_ACTIVE
        )

        # Test research mode
        research_enhancement = MetaLearningEnhancementSystem(
            enhancement_mode=EnhancementMode.RESEARCH_MODE
        )
        assert research_enhancement.enhancement_mode == EnhancementMode.RESEARCH_MODE

    def test_integration_completeness(self):
        """Test that all required integration points are satisfied"""
        # Verify all required classes are importable
        from core.meta_learning.enhancement_system import (
            MetaLearningEnhancementSystem,
        )

        # Verify key functions exist
        enhancement = MetaLearningEnhancementSystem()
        required_methods = [
            "discover_and_enhance_meta_learning_systems",
            "start_enhancement_operations",
            "run_enhancement_cycle",
        ]

        for method in required_methods:
            assert hasattr(enhancement, method)
            assert callable(getattr(enhancement, method))

    def test_enhancement_system_architecture(self):
        """Test that the enhancement system follows the correct architecture"""
        enhancement = MetaLearningEnhancementSystem()

        # Test that it's designed as an enhancement layer, not replacement
        assert hasattr(enhancement, "enhanced_systems")  # Tracks enhanced systems
        assert hasattr(enhancement, "integration_status")  # Integration tracking

        # Test that it maintains audit trails
        assert hasattr(enhancement, "enhancement_history")
        assert hasattr(enhancement, "coordination_events")
        assert hasattr(enhancement, "ethical_audit_trail")

    def test_component_integration(self):
        """Test integration between enhancement system components"""
        enhancement = MetaLearningEnhancementSystem()

        # Test that all core components are properly initialized
        assert enhancement.monitor_dashboard is not None
        assert enhancement.rate_modulator is not None
        assert enhancement.symbolic_feedback is not None

        # Test that components are from the correct modules
        from core.meta_learning.monitor_dashboard import (
            MetaLearningMonitorDashboard,
        )
        from core.meta_learning.rate_modulator import (
            DynamicLearningRateModulator,
        )
        from core.meta_learning.symbolic_feedback import SymbolicFeedbackSystem

        assert isinstance(enhancement.monitor_dashboard, MetaLearningMonitorDashboard)
        assert isinstance(enhancement.rate_modulator, DynamicLearningRateModulator)
        assert isinstance(enhancement.symbolic_feedback, SymbolicFeedbackSystem)

    def test_node_identification(self):
        """Test node identification and configuration"""
        # Test default node ID
        default_enhancement = MetaLearningEnhancementSystem()
        assert default_enhancement.node_id == "lukhas_primary"

        # Test custom node ID
        custom_enhancement = MetaLearningEnhancementSystem(node_id="custom_node_123")
        assert custom_enhancement.node_id == "custom_node_123"


if __name__ == "__main__":
    # Run basic integration test
    pytest.main([__file__, "-v"])
