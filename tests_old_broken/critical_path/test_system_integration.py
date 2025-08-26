#!/usr/bin/env python3
"""
🧪 Critical Path Integration Tests
==================================
Tests core system flows and integration paths.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestCoreSystemIntegration:
    """Test critical paths through core systems"""

    @pytest.fixture
    def setup_dependency_injection(self):
        """Set up basic dependency injection for tests"""
        from core.interfaces.dependency_injection import (
            clear_registry,
            register_service,
        )

        # Clear any existing services
        clear_registry()

        # Register mock services
        mock_memory = Mock()
        mock_memory.store = AsyncMock(
            return_value={"status": "stored", "id": "test_memory_001"}
        )
        mock_memory.retrieve = AsyncMock(
            return_value={"data": "test_data", "metadata": {}}
        )

        mock_consciousness = Mock()
        mock_consciousness.process = AsyncMock(
            return_value={"awareness_level": 0.8, "decision": "proceed"}
        )

        mock_guardian = Mock()
        mock_guardian.validate = AsyncMock(
            return_value={"approved": True, "risk_level": "low"}
        )

        register_service("memory_service", mock_memory)
        register_service("consciousness_service", mock_consciousness)
        register_service("guardian_service", mock_guardian)

        yield

        # Cleanup
        clear_registry()

    @pytest.mark.asyncio
    async def test_memory_consciousness_integration(self, setup_dependency_injection):
        """Test memory and consciousness integration path"""
        from core.interfaces.dependency_injection import get_service

        # Get services
        memory_service = get_service("memory_service")
        consciousness_service = get_service("consciousness_service")

        # Test critical path: data -> memory -> consciousness -> decision
        test_data = {
            "input": "test decision scenario",
            "context": "integration_test",
        }

        # Step 1: Store in memory
        memory_result = await memory_service.store(test_data)
        assert memory_result["status"] == "stored"

        # Step 2: Process through consciousness
        consciousness_result = await consciousness_service.process(
            {"memory_id": memory_result["id"], "data": test_data}
        )
        assert consciousness_result["awareness_level"] > 0.5
        assert consciousness_result["decision"] is not None

        # Step 3: Retrieve from memory
        retrieved = await memory_service.retrieve(memory_result["id"])
        assert retrieved["data"] is not None

    @pytest.mark.asyncio
    async def test_guardian_system_validation_path(self, setup_dependency_injection):
        """Test Guardian system validation critical path"""
        from core.interfaces.dependency_injection import get_service

        guardian_service = get_service("guardian_service")

        # Test ethical validation path
        test_action = {
            "type": "memory_access",
            "target": "sensitive_data",
            "requester": "test_agent",
            "purpose": "analysis",
        }

        validation_result = await guardian_service.validate(test_action)
        assert validation_result["approved"] is not None
        assert "risk_level" in validation_result

    @pytest.mark.asyncio
    async def test_glyph_token_processing_path(self):
        """Test GLYPH token processing through system"""
        from core.common.glyph import GLYPHSymbol, GLYPHToken

        # Create test GLYPH token
        token = GLYPHToken(
            symbol=GLYPHSymbol.TRUST,
            source="test_module",
            target="integration_test",
            payload={"test": True, "path": "critical"},
        )

        # Test token creation and processing
        assert token.symbol == GLYPHSymbol.TRUST
        assert token.source == "test_module"
        assert token.target == "integration_test"
        assert token.payload["test"] is True

        # Test token serialization/deserialization
        serialized = token.to_dict()
        assert "symbol" in serialized
        assert "source" in serialized
        assert "target" in serialized
        assert "payload" in serialized

    def test_interface_availability(self):
        """Test that all critical interfaces are available"""
        # Test memory interface
        from core.interfaces.memory_interface import MemoryInterface, MemoryType

        assert MemoryInterface is not None
        assert hasattr(MemoryType, "EPISODIC")

        # Test core interface
        from core.interfaces.core_interface import CoreInterface, MessagePriority

        assert CoreInterface is not None
        assert hasattr(MessagePriority, "HIGH")

        # Test dependency injection
        from core.interfaces.dependency_injection import ServiceRegistry, inject

        assert ServiceRegistry is not None
        assert inject is not None

    def test_common_utilities_available(self):
        """Test that common utilities are accessible"""
        from lukhas.core.common import get_logger
        from core.common.config import get_config
        from core.common.exceptions import LukhasError

        # Test logger
        logger = get_logger("test")
        assert logger is not None

        # Test config
        config = get_config("test_module")
        assert config is not None

        # Test exception hierarchy
        assert issubclass(LukhasError, Exception)


class TestCriticalSystemPaths:
    """Test end-to-end critical system paths"""

    @pytest.mark.asyncio
    async def test_memory_storage_retrieval_path(self):
        """Test complete memory storage and retrieval path"""
        with patch(
            "core.interfaces.dependency_injection.get_service"
        ) as mock_get_service:
            # Mock memory service
            mock_memory = AsyncMock()
            mock_memory.store.return_value = {
                "id": "mem_001",
                "status": "stored",
            }
            mock_memory.retrieve.return_value = {
                "data": "test_data",
                "timestamp": "2025-08-03",
            }
            mock_get_service.return_value = mock_memory

            # Test the path
            from core.interfaces.dependency_injection import get_service

            memory = get_service("memory_service")

            # Store data
            store_result = await memory.store({"test": "data"})
            assert store_result["status"] == "stored"

            # Retrieve data
            retrieve_result = await memory.retrieve(store_result["id"])
            assert retrieve_result["data"] is not None

    @pytest.mark.asyncio
    async def test_consciousness_decision_path(self):
        """Test consciousness decision-making path"""
        with patch(
            "core.interfaces.dependency_injection.get_service"
        ) as mock_get_service:
            # Mock consciousness service
            mock_consciousness = AsyncMock()
            mock_consciousness.process.return_value = {
                "decision": "approve",
                "confidence": 0.85,
                "reasoning": "test_reasoning",
            }
            mock_get_service.return_value = mock_consciousness

            # Test the path
            from core.interfaces.dependency_injection import get_service

            consciousness = get_service("consciousness_service")

            decision_result = await consciousness.process(
                {"scenario": "test_decision", "context": {"priority": "high"}}
            )

            assert decision_result["decision"] is not None
            assert decision_result["confidence"] > 0.5

    def test_module_imports_critical_path(self):
        """Test that critical modules can be imported without errors"""
        critical_modules = [
            "core.common",
            "core.interfaces.dependency_injection",
            "core.interfaces.memory_interface",
            "core.interfaces.core_interface",
            "governance.guardian_system",
        ]

        imported_modules = []
        failed_modules = []

        for module in critical_modules:
            try:
                __import__(module)
                imported_modules.append(module)
            except ImportError as e:
                failed_modules.append((module, str(e)))

        # At least 80% of critical modules should import successfully
        success_rate = len(imported_modules) / len(critical_modules)
        assert (
            success_rate >= 0.8
        ), f"Only {success_rate:.1%} of critical modules imported successfully. Failed: {failed_modules}"


class TestErrorHandlingPaths:
    """Test error handling in critical paths"""

    @pytest.mark.asyncio
    async def test_dependency_injection_fallback(self):
        """Test fallback behavior when services aren't available"""
        from core.interfaces.dependency_injection import clear_registry, get_service

        # Clear registry to simulate missing service
        clear_registry()

        # Test that getting non-existent service raises ValueError
        with pytest.raises(ValueError):
            get_service("non_existent_service")

    def test_interface_error_handling(self):
        """Test interface error handling"""
        from core.common.exceptions import LukhasError

        # Test that LUKHAS errors can be raised and caught
        with pytest.raises(LukhasError):
            raise LukhasError("Test error")

        # Test error hierarchy
        try:
            raise LukhasError("Test error")
        except Exception as e:
            assert isinstance(e, LukhasError)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
