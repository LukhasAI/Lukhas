"""
Test suite for LUKHAS Unified Grammar Module Integration.

Tests inter-module communication, registry, and lifecycle management.
"""

import asyncio

import pytest
from core_unified_grammar.bio.core import LucasBioModule
from core_unified_grammar.common.base_module import (
    BaseLukhasModule,
    ModuleState,
)
from core_unified_grammar.dream.core import LucasDreamModule
from core_unified_grammar.vision.core import LucasVisionModule
from core_unified_grammar.voice.core import LucasVoiceModule


class TestModuleIntegration:
    """Test integration between different modules."""

    @pytest.fixture
    async def dream_module(self):
        """Create dream module instance."""
        module = LucasDreamModule()
        yield module
        if module.state == ModuleState.RUNNING:
            await module.shutdown()

    @pytest.fixture
    async def bio_module(self):
        """Create bio module instance."""
        module = LucasBioModule()
        yield module
        if module.state == ModuleState.RUNNING:
            await module.shutdown()

    async def test_module_startup_sequence(self, dream_module, bio_module):
        """Test multiple modules can start up correctly."""
        # Start both modules
        await dream_module.startup()
        await bio_module.startup()

        assert dream_module.state == ModuleState.RUNNING
        assert bio_module.state == ModuleState.RUNNING

        # Both should report healthy
        dream_health = await dream_module.get_health_status()
        bio_health = await bio_module.get_health_status()

        assert dream_health["status"] == "healthy"
        assert bio_health["status"] == "healthy"

    async def test_module_communication(self, dream_module, bio_module):
        """Test modules can communicate (simulated)."""
        await dream_module.startup()
        await bio_module.startup()

        # Simulate bio module providing data to dream module
        bio_data = {"heart_rate": 72, "stress_level": 0.3, "emotional_state": "calm"}

        # Process in dream module
        dream_result = await dream_module.process(
            {"type": "bio_integration", "bio_data": bio_data}
        )

        assert dream_result is not None
        # Dream module should acknowledge bio data
        assert "processed" in dream_result or "dream" in str(dream_result).lower()

    async def test_module_shutdown_order(self, dream_module, bio_module):
        """Test modules shut down in correct order."""
        # Start modules
        await dream_module.startup()
        await bio_module.startup()

        # Shutdown in reverse order
        await bio_module.shutdown()
        await dream_module.shutdown()

        assert dream_module.state == ModuleState.STOPPED
        assert bio_module.state == ModuleState.STOPPED


class TestModuleRegistry:
    """Test module registry functionality."""

    @pytest.mark.asyncio
    async def test_registry_operations(self):
        """Test basic registry operations."""
        # This would test actual registry when implemented
        # For now, test the pattern

        modules = {
            "dream": LucasDreamModule,
            "bio": LucasBioModule,
            "voice": LucasVoiceModule,
            "vision": LucasVisionModule,
        }

        # All module classes should exist
        for name, module_class in modules.items():
            assert issubclass(module_class, BaseLukhasModule)

            # Can instantiate
            instance = module_class()
            assert instance.name.lower() == name or name in instance.name.lower()

    async def test_module_discovery_pattern(self):
        """Test module discovery pattern."""
        # Simulate module discovery
        discovered_modules = []

        module_types = [
            LucasDreamModule,
            LucasBioModule,
            LucasVoiceModule,
            LucasVisionModule,
        ]

        for module_class in module_types:
            instance = module_class()
            discovered_modules.append(
                {
                    "name": instance.name,
                    "class": module_class,
                    "tier": instance.tier_required,
                }
            )

        assert len(discovered_modules) == 4
        assert all(m["tier"] >= 1 for m in discovered_modules)


class TestModuleConfiguration:
    """Test module configuration management."""

    async def test_config_propagation(self):
        """Test configuration propagates to modules."""
        config = {"dream_interval": 60, "max_insights": 10, "symbolic_logging": True}

        module = LucasDreamModule(config)
        await module.startup()

        # Config should be accessible
        assert module.config["dream_interval"] == 60
        assert module.config["max_insights"] == 10

        # Update config
        module.update_config({"dream_interval": 30})
        assert module.config["dream_interval"] == 30

        await module.shutdown()

    async def test_module_specific_configs(self):
        """Test each module type has appropriate config."""
        # Dream module config
        dream = LucasDreamModule(
            {"dream_cycle_interval": 30, "emotional_weighting": True}
        )
        assert "dream_cycle_interval" in dream.config

        # Bio module config
        bio = LucasBioModule({"health_monitoring": True, "biometric_encryption": True})
        assert "health_monitoring" in bio.config

        # Voice module config
        voice = LucasVoiceModule(
            {"voice_provider": "mock", "emotional_adaptation": True}
        )
        assert "voice_provider" in voice.config


class TestModuleErrorHandling:
    """Test error handling across modules."""

    async def test_module_error_recovery(self):
        """Test modules can recover from errors."""
        module = LucasDreamModule()
        await module.startup()

        # Process invalid data
        result = await module.process(None)

        # Should handle gracefully
        assert module.state == ModuleState.RUNNING

        # Can still process valid data
        valid_result = await module.process({"type": "test"})
        assert valid_result is not None

        await module.shutdown()

    async def test_module_timeout_handling(self):
        """Test modules handle timeouts."""

        class SlowModule(BaseLukhasModule):
            async def process(self, data):
                await asyncio.sleep(10)  # Simulate slow operation
                return {"done": True}

        module = SlowModule("SlowModule")
        await module.startup()

        # Process with timeout
        try:
            result = await asyncio.wait_for(module.process({"test": True}), timeout=0.1)
        except asyncio.TimeoutError:
            # Module should still be healthy
            assert module.state == ModuleState.RUNNING

        await module.shutdown()


class TestModuleMetrics:
    """Test module metrics and monitoring."""

    async def test_module_metrics_collection(self):
        """Test modules collect metrics."""
        module = LucasDreamModule()
        await module.startup()

        # Process some data
        for i in range(5):
            await module.process({"iteration": i})
            await asyncio.sleep(0.01)

        # Get health with metrics
        health = await module.get_health_status()

        assert "metrics" in health
        # Could include: process_count, last_process_time, etc.

        await module.shutdown()

    async def test_module_performance_tracking(self):
        """Test performance tracking across modules."""
        modules = [
            LucasDreamModule(),
            LucasBioModule(),
            LucasVoiceModule(),
            LucasVisionModule(),
        ]

        startup_times = {}

        for module in modules:
            start = asyncio.get_event_loop().time()
            await module.startup()
            startup_times[module.name] = asyncio.get_event_loop().time() - start

        # All modules should start quickly
        for name, duration in startup_times.items():
            assert duration < 1.0, f"{name} took too long to start: {duration}s"

        # Cleanup
        for module in modules:
            await module.shutdown()


class TestModuleSecurity:
    """Test module security and access control."""

    async def test_tier_based_access(self):
        """Test tier-based access control."""
        # Create module requiring tier 3
        module = LucasDreamModule()
        module.tier_required = 3

        # Test access checks
        assert not await module.check_tier_access(1)
        assert not await module.check_tier_access(2)
        assert await module.check_tier_access(3)
        assert await module.check_tier_access(4)
        assert await module.check_tier_access(5)

    async def test_module_isolation(self):
        """Test modules are properly isolated."""
        dream1 = LucasDreamModule()
        dream2 = LucasDreamModule()

        await dream1.startup()
        await dream2.startup()

        # Modules should have separate state
        dream1.config["test_value"] = "dream1"
        dream2.config["test_value"] = "dream2"

        assert dream1.config["test_value"] == "dream1"
        assert dream2.config["test_value"] == "dream2"

        await dream1.shutdown()
        await dream2.shutdown()
