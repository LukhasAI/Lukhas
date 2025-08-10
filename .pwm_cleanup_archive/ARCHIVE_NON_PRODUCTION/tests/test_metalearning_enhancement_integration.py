#!/usr/bin/env python3
"""
Test Meta-Learning Enhancement System Integration
Tests for meta-learning enhancement system integration
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestMetaLearningEnhancementIntegration:
    """Test meta-learning enhancement system integration"""

    def test_enhancement_wrapper_import(self):
        """Test that enhancement wrapper can be imported"""
        from learning.metalearningenhancementsystem_wrapper import (
            get_meta_learning_enhancement,
        )

        assert get_meta_learning_enhancement is not None

    def test_learning_hub_with_enhancement(self):
        """Test learning hub integration with enhancement system"""
        from learning.learning_hub import get_learning_hub

        hub = get_learning_hub()
        assert hub is not None

        # Check if enhancement system is available
        if hasattr(hub, "meta_enhancement"):
            print(
                f"Meta-learning enhancement found in learning hub: {hub.meta_enhancement is not None}"
            )
            if hub.meta_enhancement:
                print("Meta-learning enhancement is initialized")

    @pytest.mark.asyncio
    async def test_enhancement_system_functionality(self):
        """Test enhancement system functionality"""
        from learning.metalearningenhancementsystem_wrapper import (
            get_meta_learning_enhancement,
        )

        enhancement = get_meta_learning_enhancement()
        if enhancement:
            # Initialize
            success = await enhancement.initialize()
            assert isinstance(success, bool)

            if success:
                # Test enhancement process
                learning_context = {
                    "task_type": "classification",
                    "data_size": 1000,
                    "complexity": "medium",
                }

                result = await enhancement.enhance_learning_process(learning_context)

                assert isinstance(result, dict)
                assert "success" in result

                if result["success"]:
                    assert "enhanced_config" in result
                    assert "monitoring_active" in result
                    print(f"Enhancement successful: {result['enhanced_config']}")

    @pytest.mark.asyncio
    async def test_learning_metrics_retrieval(self):
        """Test learning metrics retrieval"""
        from learning.metalearningenhancementsystem_wrapper import (
            get_meta_learning_enhancement,
        )

        enhancement = get_meta_learning_enhancement()
        if enhancement:
            await enhancement.initialize()

            # Get metrics
            metrics = await enhancement.get_learning_metrics()
            assert isinstance(metrics, dict)
            print(f"Learning metrics: {metrics}")

    @pytest.mark.asyncio
    async def test_symbolic_feedback(self):
        """Test symbolic feedback application"""
        from learning.metalearningenhancementsystem_wrapper import (
            get_meta_learning_enhancement,
        )

        enhancement = get_meta_learning_enhancement()
        if enhancement:
            await enhancement.initialize()

            # Apply symbolic feedback
            feedback_data = {
                "feedback_type": "performance",
                "score": 0.85,
                "context": "learning_improvement",
            }

            result = await enhancement.apply_symbolic_feedback(feedback_data)
            assert isinstance(result, dict)

            if "error" not in result:
                assert "feedback_id" in result or "processed" in result
                print(f"Symbolic feedback result: {result}")

    def test_integration_status(self):
        """Test integration status reporting"""
        from learning.metalearningenhancementsystem_wrapper import (
            get_meta_learning_enhancement,
        )

        enhancement = get_meta_learning_enhancement()
        if enhancement:
            status = enhancement.get_integration_status()

            assert isinstance(status, dict)
            assert "node_id" in status
            assert "enhancement_mode" in status
            assert "integration_stats" in status

            print(f"Integration status: {status}")

    def test_mock_implementation(self):
        """Test that mock implementation works"""
        try:
            from learning.metalearningenhancementsystem_mock import (
                Enhancementmode,
                MetaLearningEnhancementsystem,
                get_meta_learning_enhancement,
            )

            enhancement = get_meta_learning_enhancement()
            assert enhancement is not None

            # Test enhancement modes
            assert Enhancementmode.MONITORING_ONLY.value == "monitoring_only"
            assert Enhancementmode.OPTIMIZATION_ACTIVE.value == "optimization_active"

        except ImportError:
            pytest.skip("Mock implementation not available")

    @pytest.mark.asyncio
    async def test_enhancement_system_discovery(self):
        """Test meta-learning system discovery"""
        from learning.metalearningenhancementsystem_wrapper import (
            get_meta_learning_enhancement,
        )

        enhancement = get_meta_learning_enhancement()
        if enhancement:
            await enhancement.initialize()

            # Get system status which includes discovery results
            status = enhancement.get_integration_status()

            if "system_status" in status:
                system_status = status["system_status"]
                print(f"Systems found: {system_status.get('systems_found', 0)}")
                print(f"Systems enhanced: {system_status.get('systems_enhanced', 0)}")
                print(
                    f"Monitoring active: {system_status.get('monitoring_active', False)}"
                )
                print(
                    f"Optimization active: {system_status.get('optimization_active', False)}"
                )

    @pytest.mark.asyncio
    async def test_enhancement_through_learning_hub(self):
        """Test enhancement through learning hub"""
        from learning.learning_hub import get_learning_hub

        hub = get_learning_hub()

        # Initialize hub
        await hub.initialize()

        # Test enhancement if available
        if hasattr(hub, "enhance_learning_process"):
            learning_context = {
                "algorithm": "neural_network",
                "dataset": "test_data",
                "goal": "accuracy_improvement",
            }

            result = await hub.enhance_learning_process(learning_context)

            assert isinstance(result, dict)
            print(f"Hub enhancement result: {result}")
        else:
            print("Enhancement methods not available in hub")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
