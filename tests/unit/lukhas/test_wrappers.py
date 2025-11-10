"""
Tests for LUKHAS Core Wrappers
===============================

Validates that consciousness, dream, and glyph wrappers:
- Respect feature flags (default OFF)
- Handle imports safely
- Provide consistent APIs
- Gracefully degrade when subsystems unavailable
"""
import os
import pytest
from unittest.mock import patch, MagicMock


class TestConsciousnessWrapper:
    """Tests for lukhas.consciousness wrapper module"""

    def test_import_succeeds(self):
        """Wrapper module can be imported"""
        import lukhas.consciousness
        assert lukhas.consciousness is not None

    def test_disabled_by_default(self):
        """Consciousness is disabled by default"""
        # Clear any env vars
        with patch.dict(os.environ, {}, clear=False):
            if 'LUKHAS_CONSCIOUSNESS_ENABLED' in os.environ:
                del os.environ['LUKHAS_CONSCIOUSNESS_ENABLED']

            # Reimport to get clean state
            import importlib
            import lukhas.consciousness
            importlib.reload(lukhas.consciousness)

            assert not lukhas.consciousness.is_enabled()

    def test_is_enabled_function(self):
        """is_enabled() returns boolean"""
        from lukhas.consciousness import is_enabled
        result = is_enabled()
        assert isinstance(result, bool)

    def test_get_consciousness_state_when_disabled(self):
        """get_consciousness_state returns None when disabled"""
        from lukhas.consciousness import get_consciousness_state

        with patch('lukhas.consciousness.is_enabled', return_value=False):
            result = get_consciousness_state("test_agent")
            assert result is None

    def test_create_state_when_disabled(self):
        """create_state returns None when disabled"""
        from lukhas.consciousness import create_state

        with patch('lukhas.consciousness.is_enabled', return_value=False):
            result = create_state("test_agent", "agent")
            assert result is None

    def test_get_orchestrator_when_disabled(self):
        """get_orchestrator returns None when disabled"""
        from lukhas.consciousness import get_orchestrator

        with patch('lukhas.consciousness.is_enabled', return_value=False):
            result = get_orchestrator()
            assert result is None

    def test_get_network_metrics_when_disabled(self):
        """get_network_metrics returns disabled status"""
        from lukhas.consciousness import get_network_metrics

        with patch('lukhas.consciousness.is_enabled', return_value=False):
            result = get_network_metrics()
            assert isinstance(result, dict)
            assert result.get("enabled") is False

    def test_public_api(self):
        """All expected functions are in __all__"""
        from lukhas.consciousness import __all__

        expected = [
            "is_enabled",
            "get_consciousness_state",
            "create_state",
            "get_orchestrator",
            "get_network_metrics",
        ]
        for func in expected:
            assert func in __all__


class TestDreamWrapper:
    """Tests for lukhas.dream wrapper module"""

    def test_import_succeeds(self):
        """Wrapper module can be imported"""
        import lukhas.dream
        assert lukhas.dream is not None

    def test_disabled_by_default(self):
        """Dreams is disabled by default"""
        with patch.dict(os.environ, {}, clear=False):
            if 'LUKHAS_DREAMS_ENABLED' in os.environ:
                del os.environ['LUKHAS_DREAMS_ENABLED']

            import importlib
            import lukhas.dream
            importlib.reload(lukhas.dream)

            assert not lukhas.dream.is_enabled()

    def test_is_enabled_function(self):
        """is_enabled() returns boolean"""
        from lukhas.dream import is_enabled
        result = is_enabled()
        assert isinstance(result, bool)

    def test_is_parallel_enabled_function(self):
        """is_parallel_enabled() returns boolean"""
        from lukhas.dream import is_parallel_enabled
        result = is_parallel_enabled()
        assert isinstance(result, bool)

    def test_get_dream_engine_when_disabled(self):
        """get_dream_engine returns None when disabled"""
        from lukhas.dream import get_dream_engine

        with patch('lukhas.dream.is_enabled', return_value=False):
            result = get_dream_engine()
            assert result is None

    def test_simulate_dream_when_disabled(self):
        """simulate_dream returns error when disabled"""
        from lukhas.dream import simulate_dream

        with patch('lukhas.dream.is_enabled', return_value=False):
            result = simulate_dream("test_seed")
            assert isinstance(result, dict)
            assert result["success"] is False
            assert "error" in result

    def test_simulate_dream_structure(self):
        """simulate_dream returns proper structure when enabled"""
        from lukhas.dream import simulate_dream

        with patch('lukhas.dream.is_enabled', return_value=True):
            result = simulate_dream("test_seed", context={"foo": "bar"})
            assert isinstance(result, dict)
            assert "success" in result
            assert "dream_id" in result
            assert "seed" in result
            assert result["seed"] == "test_seed"

    def test_parallel_dream_mesh_when_disabled(self):
        """parallel_dream_mesh returns error when parallel disabled"""
        from lukhas.dream import parallel_dream_mesh

        with patch('lukhas.dream.is_parallel_enabled', return_value=False):
            result = parallel_dream_mesh(["seed1", "seed2"])
            assert isinstance(result, dict)
            assert result["success"] is False
            assert "parallel" in result.get("error", "").lower()

    def test_get_dream_by_id_when_disabled(self):
        """get_dream_by_id returns None when disabled"""
        from lukhas.dream import get_dream_by_id

        with patch('lukhas.dream.is_enabled', return_value=False):
            result = get_dream_by_id("test_id")
            assert result is None

    def test_public_api(self):
        """All expected functions are in __all__"""
        from lukhas.dream import __all__

        expected = [
            "is_enabled",
            "is_parallel_enabled",
            "get_dream_engine",
            "simulate_dream",
            "get_dream_by_id",
            "parallel_dream_mesh",
        ]
        for func in expected:
            assert func in __all__


class TestGlyphsWrapper:
    """Tests for lukhas.glyphs wrapper module"""

    def test_import_succeeds(self):
        """Wrapper module can be imported"""
        import lukhas.glyphs
        assert lukhas.glyphs is not None

    def test_disabled_by_default(self):
        """GLYPHs is disabled by default"""
        with patch.dict(os.environ, {}, clear=False):
            if 'LUKHAS_GLYPHS_ENABLED' in os.environ:
                del os.environ['LUKHAS_GLYPHS_ENABLED']

            import importlib
            import lukhas.glyphs
            importlib.reload(lukhas.glyphs)

            assert not lukhas.glyphs.is_enabled()

    def test_is_enabled_function(self):
        """is_enabled() returns boolean"""
        from lukhas.glyphs import is_enabled
        result = is_enabled()
        assert isinstance(result, bool)

    def test_get_glyph_engine_when_disabled(self):
        """get_glyph_engine returns None when disabled"""
        from lukhas.glyphs import get_glyph_engine

        with patch('lukhas.glyphs.is_enabled', return_value=False):
            result = get_glyph_engine()
            assert result is None

    def test_encode_concept_when_disabled(self):
        """encode_concept returns None when disabled"""
        from lukhas.glyphs import encode_concept

        with patch('lukhas.glyphs.is_enabled', return_value=False):
            result = encode_concept("test_concept")
            assert result is None

    def test_encode_concept_structure(self):
        """encode_concept returns proper structure when enabled"""
        from lukhas.glyphs import encode_concept

        with patch('lukhas.glyphs.is_enabled', return_value=True):
            with patch('lukhas.glyphs._glyph_engine') as mock_engine:
                mock_symbol = MagicMock()
                mock_symbol.symbol_id = "test_id"
                mock_engine.encode_concept.return_value = mock_symbol

                result = encode_concept(
                    "test_concept",
                    emotion={"joy": 0.8},
                    source_module="test"
                )

                assert isinstance(result, dict)
                assert result["concept"] == "test_concept"
                assert result["emotion"] == {"joy": 0.8}
                assert result["source_module"] == "test"

    def test_bind_glyph_when_disabled(self):
        """bind_glyph returns error when disabled"""
        from lukhas.glyphs import bind_glyph

        with patch('lukhas.glyphs.is_enabled', return_value=False):
            result = bind_glyph({"concept": "test"}, "memory_123")
            assert isinstance(result, dict)
            assert result["success"] is False
            assert "error" in result

    def test_bind_glyph_validates_inputs(self):
        """bind_glyph validates glyph_data and memory_id"""
        from lukhas.glyphs import bind_glyph

        with patch('lukhas.glyphs.is_enabled', return_value=True):
            # Invalid glyph_data
            result = bind_glyph(None, "memory_123")
            assert result["success"] is False
            assert "glyph_data" in result["error"]

            # Invalid memory_id
            result = bind_glyph({"concept": "test"}, "")
            assert result["success"] is False
            assert "memory_id" in result["error"]

    def test_bind_glyph_success(self):
        """bind_glyph returns success structure"""
        from lukhas.glyphs import bind_glyph

        with patch('lukhas.glyphs.is_enabled', return_value=True):
            result = bind_glyph(
                {"concept": "test"},
                "memory_123",
                user_id="user_1"
            )
            assert isinstance(result, dict)
            assert result["success"] is True
            assert "binding_id" in result

    def test_validate_glyph_function(self):
        """validate_glyph checks structure and content"""
        from lukhas.glyphs import validate_glyph

        # Invalid: not a dict
        is_valid, error = validate_glyph("not a dict")
        assert not is_valid
        assert "dictionary" in error

        # Invalid: missing concept
        is_valid, error = validate_glyph({})
        assert not is_valid
        assert "concept" in error

        # Invalid: empty concept
        is_valid, error = validate_glyph({"concept": ""})
        assert not is_valid

        # Invalid: concept too long
        is_valid, error = validate_glyph({"concept": "x" * 1001})
        assert not is_valid
        assert "length" in error

        # Invalid: emotion not dict
        is_valid, error = validate_glyph({"concept": "test", "emotion": "happy"})
        assert not is_valid

        # Invalid: emotion value out of range
        is_valid, error = validate_glyph({"concept": "test", "emotion": {"joy": 1.5}})
        assert not is_valid

        # Valid
        is_valid, error = validate_glyph({"concept": "test"})
        assert is_valid
        assert error is None

        # Valid with emotion
        is_valid, error = validate_glyph({
            "concept": "test",
            "emotion": {"joy": 0.8, "calm": 0.6}
        })
        assert is_valid
        assert error is None

    def test_get_glyph_stats_when_disabled(self):
        """get_glyph_stats returns disabled status"""
        from lukhas.glyphs import get_glyph_stats

        with patch('lukhas.glyphs.is_enabled', return_value=False):
            result = get_glyph_stats()
            assert isinstance(result, dict)
            assert result.get("enabled") is False

    def test_public_api(self):
        """All expected functions are in __all__"""
        from lukhas.glyphs import __all__

        expected = [
            "is_enabled",
            "get_glyph_engine",
            "encode_concept",
            "decode_symbol",
            "bind_glyph",
            "get_binding",
            "validate_glyph",
            "get_glyph_stats",
        ]
        for func in expected:
            assert func in __all__


class TestFeatureFlags:
    """Tests for feature flag behavior across wrappers"""

    def test_all_disabled_by_default(self):
        """All subsystems disabled by default (safety)"""
        with patch.dict(os.environ, {}, clear=False):
            # Clear all feature flags
            for key in ['LUKHAS_CONSCIOUSNESS_ENABLED', 'LUKHAS_DREAMS_ENABLED',
                       'LUKHAS_GLYPHS_ENABLED', 'LUKHAS_PARALLEL_DREAMS']:
                if key in os.environ:
                    del os.environ[key]

            # Reload all modules
            import importlib
            import lukhas.consciousness
            import lukhas.dream
            import lukhas.glyphs

            importlib.reload(lukhas.consciousness)
            importlib.reload(lukhas.dream)
            importlib.reload(lukhas.glyphs)

            assert not lukhas.consciousness.is_enabled()
            assert not lukhas.dream.is_enabled()
            assert not lukhas.glyphs.is_enabled()

    def test_flags_require_explicit_enable(self):
        """Flags require explicit '1' to enable"""
        test_cases = ['0', 'false', 'False', 'no', 'disabled', '']

        for value in test_cases:
            with patch.dict(os.environ, {'LUKHAS_DREAMS_ENABLED': value}):
                import importlib
                import lukhas.dream
                importlib.reload(lukhas.dream)

                assert not lukhas.dream.is_enabled(), f"Failed for value: {value}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
