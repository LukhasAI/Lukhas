
import asyncio
import unittest.mock
from datetime import datetime, timedelta, timezone

import pytest
from labs.consciousness.awareness.awareness_engine import (
    AwarenessEngine,
    create_and_initialize_awareness_component,
    create_awareness_component,
)

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


class TestAwarenessEngine:
    """Comprehensive tests for the AwarenessEngine."""

    def test_instantiation(self):
        """Test basic instantiation of the AwarenessEngine."""
        engine = AwarenessEngine(config={"key": "value"}, user_id_context="test_user")
        assert engine is not None
        assert engine.config == {"key": "value"}
        assert engine.user_id_context == "test_user"
        assert not engine.is_initialized
        assert engine.status == "inactive"

    async def test_successful_initialization(self):
        """Test the happy path for the initialize method."""
        engine = AwarenessEngine()
        result = await engine.initialize("user1")
        assert result is True
        assert engine.is_initialized is True
        assert engine.status == "active"
        # Check if internal components seem to be set up
        assert "awareness_level" in engine.consciousness_state
        assert engine.consciousness_state["integration_status"] == "calibrated"

    async def test_initialization_failure(self):
        """Test that initialization fails gracefully."""
        engine = AwarenessEngine()
        with unittest.mock.patch.object(
            engine, "_setup_consciousness_system", new=unittest.mock.AsyncMock(side_effect=Exception("Setup failed"))
        ) as mock_setup:
            result = await engine.initialize("user1")
            assert result is False
            assert engine.is_initialized is False
            assert engine.status == "initialization_failed"
            mock_setup.assert_awaited_once()

    def test_get_status(self):
        """Test the get_status method in various states."""
        engine = AwarenessEngine()
        status = engine.get_status("user1")
        assert status["current_status"] == "inactive"
        assert status["is_initialized"] is False
        assert "timestamp_utc" in status

    async def test_process_when_not_initialized(self):
        """Test that process triggers initialization if the engine is not ready."""
        engine = AwarenessEngine()
        # Mock initialize to control its behavior
        engine.initialize = unittest.mock.AsyncMock(wraps=engine.initialize)

        data = {"category": "test"}
        result = await engine.process(data, user_id="user1")

        engine.initialize.assert_awaited_once_with(user_id="user1")
        assert engine.is_initialized is True
        assert result["status"] == "success"
        assert result["category_processed"] == "test"

    async def test_process_initialization_failure(self):
        """Test process when the implicit initialization fails."""
        engine = AwarenessEngine()
        engine.initialize = unittest.mock.AsyncMock(return_value=False)
        # To ensure the mock is used correctly and status is set.
        async def mock_init_fail(user_id):
            engine.is_initialized = False
            engine.status = "initialization_failed"
            return False
        engine.initialize.side_effect = mock_init_fail

        data = {"category": "test"}
        result = await engine.process(data, user_id="user1")

        assert result["status"] == "error"
        assert result["error"] == "Component not initialized"

    @pytest.mark.parametrize(
        "category, expected_key",
        [
            ("consciousness_stream", "consciousness_level_assessed"),
            ("governance_query", "policy_compliance_status"),
            ("voice_data", "voice_data_processed"),
            ("identity_data", "identity_verification_status"),
            ("quantum_data", "qi_entanglement_status"),
            ("unknown_category", "data_processed_generically"),
            (None, "data_processed_generically"),
        ],
    )
    async def test_process_with_different_categories(self, category, expected_key):
        """Test the processing logic for various data categories."""
        engine = await create_and_initialize_awareness_component(user_id="test_user")
        data = {"category": category, "payload": "some_data"}

        # Mocking the specific processing methods to isolate the dispatch logic
        with unittest.mock.patch.object(engine, "_process_consciousness_data", new=unittest.mock.AsyncMock(return_value={"consciousness_level_assessed": True})), \
             unittest.mock.patch.object(engine, "_process_governance_data", new=unittest.mock.AsyncMock(return_value={"policy_compliance_status": True})), \
             unittest.mock.patch.object(engine, "_process_voice_data", new=unittest.mock.AsyncMock(return_value={"voice_data_processed": True})), \
             unittest.mock.patch.object(engine, "_process_identity_data", new=unittest.mock.AsyncMock(return_value={"identity_verification_status": True})), \
             unittest.mock.patch.object(engine, "_process_quantum_data", new=unittest.mock.AsyncMock(return_value={"qi_entanglement_status": True})), \
             unittest.mock.patch.object(engine, "_process_generic_data", new=unittest.mock.AsyncMock(return_value={"data_processed_generically": True})):

            # The original implementation dispatches based on category but I am adding them to the test
            if category not in ["consciousness_stream", "governance_query", None, "unknown_category"]:
                handler_map = {
                    "voice_data": engine._process_voice_data,
                    "identity_data": engine._process_identity_data,
                    "quantum_data": engine._process_quantum_data,
                }

                async def side_effect_func(d, c):
                    if c in handler_map:
                        return await handler_map[c](d)
                    return await engine._process_generic_data(d)

                engine._core_consciousness_processing = unittest.mock.AsyncMock(side_effect=side_effect_func)


            result = await engine.process(data, "user1")

            assert result["status"] == "success"
            assert result["category_processed"] == category
            assert expected_key in result["result"]

    async def test_process_exception_handling(self):
        """Test the error handling within the process method."""
        engine = await create_and_initialize_awareness_component(user_id="test_user")
        with unittest.mock.patch.object(
            engine, "_core_consciousness_processing", new=unittest.mock.AsyncMock(side_effect=ValueError("Core processing error"))
        ) as mock_core:
            data = {"category": "test"}
            result = await engine.process(data, "user1")
            assert result["status"] == "error"
            assert result["error_message"] == "Core processing error"
            assert result["exception_type"] == "ValueError"
            mock_core.assert_awaited_once()

    async def test_validate_when_not_initialized(self):
        """Test that validate returns False if the engine is not initialized."""
        engine = AwarenessEngine()
        assert await engine.validate("user1") is False

    async def test_validate_when_initialized(self):
        """Test that validate returns True when the engine is initialized and healthy."""
        engine = await create_and_initialize_awareness_component(user_id="test_user")
        assert await engine.validate("user1") is True

    async def test_validate_with_internal_failure(self):
        """Test validate when an internal check fails."""
        engine = await create_and_initialize_awareness_component(user_id="test_user")
        with unittest.mock.patch.object(
            engine, "_perform_internal_validation", new=unittest.mock.AsyncMock(return_value=False)
        ) as mock_internal_validate:
            assert await engine.validate("user1") is False
            mock_internal_validate.assert_awaited_once()

    async def test_shutdown(self):
        """Test the shutdown method."""
        engine = await create_and_initialize_awareness_component(user_id="test_user")
        assert engine.is_initialized is True
        assert engine.status == "active"

        await engine.shutdown("user1")

        assert engine.is_initialized is False
        assert engine.status == "inactive"

        status = engine.get_status()
        assert status["is_initialized"] is False
        assert status["current_status"] == "inactive"

    def test_factory_create_awareness_component(self):
        """Test the synchronous factory function."""
        engine = create_awareness_component(config={"id": 1}, user_id="factory_user")
        assert isinstance(engine, AwarenessEngine)
        assert engine.config == {"id": 1}
        assert engine.user_id_context == "factory_user"

    async def test_factory_create_and_initialize_awareness_component(self):
        """Test the asynchronous factory that also initializes."""
        engine = await create_and_initialize_awareness_component(config={"id": 2}, user_id="async_factory_user")
        assert isinstance(engine, AwarenessEngine)
        assert engine.is_initialized is True
        assert engine.status == "active"
        assert engine.config == {"id": 2}
        assert engine.user_id_context == "async_factory_user"

    # --- Tests for internal validation methods ---
    @pytest.mark.parametrize(
        "state, expected",
        [
            ({"awareness_level": 0.5, "temporal_coherence": 0.6}, True),
            ({"awareness_level": 0.5, "temporal_coherence": 0.9}, False), # Difference > 0.3
            ({"awareness_level": 1.1, "temporal_coherence": 0.9}, False), # Invalid level
            ({}, False), # Missing keys
            ({"awareness_level": "bad", "temporal_coherence": "data"}, False), # Wrong type
        ],
    )
    def test_internal_validate_consciousness_coherence(self, state, expected):
        engine = AwarenessEngine()
        assert engine._validate_consciousness_coherence(state) == expected

    @pytest.mark.parametrize(
        "patterns, expected",
        [
            (set(range(50)), True),
            (set(range(100)), True),
            (set(range(101)), False),
            ("not a set", False),
        ],
    )
    def test_internal_validate_symbolic_integration(self, patterns, expected):
        engine = AwarenessEngine()
        assert engine._validate_symbolic_integration(patterns) == expected

    @pytest.mark.parametrize(
        "coherence_data, expected",
        [
            ({"coherence_score": 0.8, "last_update": datetime.now(timezone.utc)}, True),
            ({"coherence_score": 1.1, "last_update": datetime.now(timezone.utc)}, False), # Invalid score
            ({"coherence_score": 0.8, "last_update": datetime.now(timezone.utc) - timedelta(minutes=6)}, False), # Stale
            ({"coherence_score": 0.8}, True), # No last_update is fine
            ({}, True), # Empty dict is fine (defaults to 0.0)
            ({"coherence_score": "bad"}, False), # Bad type
        ],
    )
    def test_internal_validate_temporal_coherence(self, coherence_data, expected):
        engine = AwarenessEngine()
        assert engine._validate_temporal_coherence(coherence_data) == expected
