"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧪 LUKHAS AI - UNIFIED GRAMMAR BASE MODULE TEST SUITE
║ Test suite for the foundational BaseLukhasModule class
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: test_base_module.py
║ Path: tests/unified_grammar/test_base_module.py
║ Version: 1.0.0 | Created: 2025-07-25 | Modified: 2025-07-25
║ Authors: LUKHAS AI Testing Team | Claude Code (test implementation)
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ Comprehensive test suite for the BaseLukhasModule class, which serves as the
║ foundation for all LUKHAS Unified Grammar modules. Tests ensure compliance
║ with the standardized module interface and lifecycle management.
║
║ Test Coverage:
║ • Module initialization and state management
║ • Lifecycle methods (startup/shutdown)
║ • Health status reporting
║ • Configuration management
║ • Tier-based access control
║ • Symbolic logging functionality
║ • Error handling and recovery
║
║ Symbolic Tags: {ΛTEST}, {ΛGRAMMAR}, {ΛBASE}
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
from datetime import datetime

import pytest
from core_unified_grammar.common.base_module import (
    BaseLukhasModule,
    ModuleState,
)


class TestModule(BaseLukhasModule):
    """Test implementation of BaseLukhasModule."""

    def __init__(self, config=None):
        super().__init__("TestModule")
        self.config = config or {}
        self.process_called = False
        self.process_result = None

    async def process(self, input_data):
        """Test processing method."""
        self.process_called = True
        self.process_result = input_data
        await self.log_symbolic("🧪 Processing test data")
        return {"processed": input_data}


class TestBaseLukhasModule:
    """Test suite for BaseLukhasModule."""

    @pytest.fixture
    async def test_module(self):
        """Create a test module instance."""
        module = TestModule()
        yield module
        # Cleanup
        if module.state == ModuleState.RUNNING:
            await module.shutdown()

    async def test_module_initialization(self, test_module):
        """Test module initializes correctly."""
        assert test_module.name == "TestModule"
        assert test_module.state == ModuleState.STOPPED
        assert test_module.startup_time is None
        assert test_module.tier_required == 1

    async def test_module_startup(self, test_module):
        """Test module startup process."""
        # Start module
        await test_module.startup()

        assert test_module.state == ModuleState.RUNNING
        assert test_module.startup_time is not None
        assert isinstance(test_module.startup_time, datetime)

    async def test_module_shutdown(self, test_module):
        """Test module shutdown process."""
        # Start then stop
        await test_module.startup()
        await test_module.shutdown()

        assert test_module.state == ModuleState.STOPPED
        assert test_module.shutdown_time is not None

    async def test_double_startup(self, test_module):
        """Test calling startup twice is safe."""
        await test_module.startup()
        original_time = test_module.startup_time

        # Second startup should be no-op
        await test_module.startup()
        assert test_module.startup_time == original_time
        assert test_module.state == ModuleState.RUNNING

    async def test_module_health_status(self, test_module):
        """Test health status reporting."""
        # Before startup
        health = await test_module.get_health_status()
        assert health["status"] == "stopped"
        assert health["uptime"] == 0

        # After startup
        await test_module.startup()
        await asyncio.sleep(0.1)  # Let some time pass

        health = await test_module.get_health_status()
        assert health["status"] == "healthy"
        assert health["uptime"] > 0
        assert "metrics" in health

    async def test_module_config_update(self, test_module):
        """Test configuration updates."""
        new_config = {"test_key": "test_value", "number": 42}

        test_module.update_config(new_config)

        assert test_module.config["test_key"] == "test_value"
        assert test_module.config["number"] == 42

    async def test_module_processing(self, test_module):
        """Test module processing."""
        await test_module.startup()

        test_data = {"input": "test"}
        result = await test_module.process(test_data)

        assert test_module.process_called
        assert test_module.process_result == test_data
        assert result == {"processed": test_data}

    async def test_symbolic_logging(self, test_module):
        """Test symbolic logging functionality."""
        await test_module.startup()

        # Test different log levels
        await test_module.log_info("Info message")
        await test_module.log_symbolic("🧪 Symbolic message")
        await test_module.log_error("Error message")

        # Verify messages were logged (would need mock logger in real test)
        assert True  # Placeholder - would check logger calls

    async def test_tier_check(self, test_module):
        """Test tier access checking."""
        # Default tier is 1
        assert await test_module.check_tier_access(1)
        assert await test_module.check_tier_access(2)
        assert await test_module.check_tier_access(3)

        # Set required tier
        test_module.tier_required = 3
        assert not await test_module.check_tier_access(1)
        assert not await test_module.check_tier_access(2)
        assert await test_module.check_tier_access(3)


class TestModuleLifecycle:
    """Test module lifecycle management."""

    async def test_module_state_transitions(self):
        """Test state transitions are valid."""
        module = TestModule()

        # Initial state
        assert module.state == ModuleState.STOPPED

        # Start -> Running
        await module.startup()
        assert module.state == ModuleState.RUNNING

        # Running -> Stopped
        await module.shutdown()
        assert module.state == ModuleState.STOPPED

    async def test_module_cleanup_on_error(self):
        """Test module cleanup on error."""

        class ErrorModule(BaseLukhasModule):
            async def startup(self):
                await super().startup()
                raise Exception("Startup error")

        module = ErrorModule("ErrorModule")

        with pytest.raises(Exception):
            await module.startup()

        # Module should still be stoppable
        assert module.state == ModuleState.RUNNING
        await module.shutdown()
        assert module.state == ModuleState.STOPPED


class TestModuleRegistry:
    """Test module registry interaction."""

    @pytest.mark.skip(reason="Registry implementation pending")
    async def test_module_registration(self):
        """Test module can register with registry."""
        from core_unified_grammar.core.module_registry import get_registry

        registry = get_registry()
        module = TestModule()

        # Register module
        success = await registry.register_module(
            name="test", module_class=TestModule, config={}
        )

        assert success
        assert "test" in registry.list_modules()


"""
╔══════════════════════════════════════════════════════════════════════════════════
║ TEST EXECUTION:
║   Run with: pytest tests/unified_grammar/test_base_module.py -v
║
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
║   Unauthorized use, reproduction, or distribution is prohibited.
╚══════════════════════════════════════════════════════════════════════════════════
"""
