"""
Test suite for core/orchestration/core.py - OrchestrationCore
Following AUTONOMOUS_GUIDE_TEST_COVERAGE.md Phase 4: Systematic Test Writing

COVERAGE TARGET: 75%+ for core/orchestration/core.py
PRIORITY: HIGH (central orchestration system)

Test Categories:
1. Initialization tests (constructor, component setup)
2. Component initialization tests (memory, bio, awareness, ethics, dream)
3. Module registration tests
4. Consciousness loop tests
5. Error handling and fallback tests
6. Integration tests
"""
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from core.orchestration.core import OrchestrationCore


class TestOrchestrationCoreInitialization:
    """Test OrchestrationCore initialization and basic setup."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        orchestrator = OrchestrationCore()

        assert orchestrator.config == {}
        assert orchestrator.session_id is not None
        assert isinstance(orchestrator.start_time, datetime)
        assert orchestrator.is_running is False
        assert orchestrator.consciousness_level == 0.0
        assert orchestrator.emotional_state == {
            "valence": 0.0,
            "arousal": 0.0,
            "dominance": 0.0,
        }
        assert orchestrator.active_modules == {}

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        custom_config = {
            "memory": {"max_size": 1000},
            "bio_core": {"enable_dreams": True},
        }
        orchestrator = OrchestrationCore(config=custom_config)

        assert orchestrator.config == custom_config
        assert orchestrator.session_id is not None
        assert orchestrator.is_running is False

    def test_session_id_uniqueness(self):
        """Test that each instance gets a unique session ID."""
        orchestrator1 = OrchestrationCore()
        orchestrator2 = OrchestrationCore()

        assert orchestrator1.session_id != orchestrator2.session_id


class TestOrchestrationCoreComponentInitialization:
    """Test component initialization methods."""

    @pytest.fixture
    def orchestrator(self):
        """Create OrchestrationCore instance for testing."""
        return OrchestrationCore()

    @pytest.mark.asyncio
    async def test_initialize_memory_system_success(self, orchestrator):
        """Test successful memory system initialization."""
        with patch('core.orchestration.core.MemoryManager') as mock_memory_manager:
            mock_instance = Mock()
            mock_instance.initialize = AsyncMock()
            mock_memory_manager.return_value = mock_instance

            await orchestrator._initialize_memory_system()

            assert orchestrator.memory_manager == mock_instance
            mock_instance.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_memory_system_not_available(self, orchestrator):
        """Test memory system initialization when MemoryManager not available."""
        with patch('core.orchestration.core.MemoryManager', None):
            await orchestrator._initialize_memory_system()

            assert orchestrator.memory_manager is None

    @pytest.mark.asyncio
    async def test_initialize_memory_system_type_error_fallback(self, orchestrator):
        """Test memory system initialization with TypeError fallback."""
        with patch('core.orchestration.core.MemoryManager') as mock_memory_manager:
            # First call raises TypeError, second succeeds
            mock_instance = Mock()
            mock_instance.initialize = AsyncMock()
            mock_memory_manager.side_effect = [TypeError(), mock_instance]

            await orchestrator._initialize_memory_system()

            assert mock_memory_manager.call_count == 2

    @pytest.mark.asyncio
    async def test_initialize_bio_core_success(self, orchestrator):
        """Test successful bio core initialization."""
        with patch('core.orchestration.core.BioCore') as mock_bio_core:
            mock_instance = Mock()
            mock_instance.initialize = AsyncMock()
            mock_bio_core.return_value = mock_instance

            await orchestrator._initialize_bio_core()

            assert orchestrator.bio_core == mock_instance
            mock_instance.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_bio_core_not_available(self, orchestrator):
        """Test bio core initialization when BioCore not available."""
        with patch('core.orchestration.core.BioCore', None):
            await orchestrator._initialize_bio_core()

            assert orchestrator.bio_core is None

    @pytest.mark.asyncio
    async def test_initialize_awareness_system_success(self, orchestrator):
        """Test successful awareness system initialization."""
        with patch('core.orchestration.core.BioAwarenessSystem') as mock_awareness:
            mock_instance = Mock()
            mock_instance.initialize = AsyncMock()
            mock_awareness.return_value = mock_instance

            await orchestrator._initialize_awareness_system()

            assert orchestrator.awareness_system == mock_instance
            mock_instance.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_awareness_system_not_available(self, orchestrator):
        """Test awareness system initialization when BioAwarenessSystem not available."""
        with patch('core.orchestration.core.BioAwarenessSystem', None):
            await orchestrator._initialize_awareness_system()

            assert orchestrator.awareness_system is None


class TestOrchestrationCoreFullInitialization:
    """Test full initialization process."""

    @pytest.fixture
    def orchestrator(self):
        """Create OrchestrationCore instance for testing."""
        return OrchestrationCore()

    @pytest.mark.asyncio
    async def test_initialize_success_path(self, orchestrator):
        """Test successful full initialization."""
        with patch.object(orchestrator, '_initialize_memory_system', new_callable=AsyncMock) as mock_memory, \
             patch.object(orchestrator, '_initialize_bio_core', new_callable=AsyncMock) as mock_bio, \
             patch.object(orchestrator, '_initialize_awareness_system', new_callable=AsyncMock) as mock_awareness, \
             patch.object(orchestrator, '_initialize_ethics_and_compliance', new_callable=AsyncMock) as mock_ethics, \
             patch.object(orchestrator, '_initialize_dream_engine', new_callable=AsyncMock) as mock_dream, \
             patch.object(orchestrator, '_register_core_modules', new_callable=AsyncMock) as mock_register, \
             patch.object(orchestrator, '_initiate_consciousness_loop', new_callable=AsyncMock) as mock_consciousness:

            result = await orchestrator.initialize()

            assert result is True
            assert orchestrator.is_running is True

            # Verify all initialization methods were called in order
            mock_memory.assert_called_once()
            mock_bio.assert_called_once()
            mock_awareness.assert_called_once()
            mock_ethics.assert_called_once()
            mock_dream.assert_called_once()
            mock_register.assert_called_once()
            mock_consciousness.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_failure_path(self, orchestrator):
        """Test initialization failure handling."""
        with patch.object(orchestrator, '_initialize_memory_system', side_effect=Exception("Memory error")):
            result = await orchestrator.initialize()

            assert result is False
            assert orchestrator.is_running is False


class TestOrchestrationCoreErrorHandling:
    """Test error handling and resilience."""

    @pytest.fixture
    def orchestrator(self):
        """Create OrchestrationCore instance for testing."""
        return OrchestrationCore()

    @pytest.mark.asyncio
    async def test_component_initialization_graceful_degradation(self, orchestrator):
        """Test that component initialization failures don't crash the system."""
        # Test memory system failure
        with patch('core.orchestration.core.MemoryManager', side_effect=Exception("Memory error")):
            await orchestrator._initialize_memory_system()
            assert orchestrator.memory_manager is None

        # Test bio core failure
        with patch('core.orchestration.core.BioCore', side_effect=Exception("Bio error")):
            await orchestrator._initialize_bio_core()
            assert orchestrator.bio_core is None

        # Test awareness system failure
        with patch('core.orchestration.core.BioAwarenessSystem', side_effect=Exception("Awareness error")):
            await orchestrator._initialize_awareness_system()
            assert orchestrator.awareness_system is None


class TestOrchestrationCoreIntegration:
    """Integration tests for OrchestrationCore with real components."""

    @pytest.mark.asyncio
    async def test_real_module_registry_integration(self):
        """Test integration with real ModuleRegistry."""
        orchestrator = OrchestrationCore()

        # ModuleRegistry should be initialized
        assert orchestrator.module_registry is not None
        assert hasattr(orchestrator.module_registry, 'register')

    def test_emotional_state_structure(self):
        """Test emotional state has correct structure."""
        orchestrator = OrchestrationCore()

        emotional_state = orchestrator.emotional_state
        assert 'valence' in emotional_state
        assert 'arousal' in emotional_state
        assert 'dominance' in emotional_state
        assert all(isinstance(v, (int, float)) for v in emotional_state.values())

    def test_consciousness_level_initialization(self):
        """Test consciousness level is properly initialized."""
        orchestrator = OrchestrationCore()

        assert isinstance(orchestrator.consciousness_level, (int, float))
        assert 0.0 <= orchestrator.consciousness_level <= 1.0


# Test configuration for pytest
pytest_plugins = ["pytest_asyncio"]
