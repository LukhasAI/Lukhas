import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest

# Module to be tested
MODULE_NAME = "cognitive_core.reasoning.deep_inference_engine"


@pytest.fixture
def clean_module():
    """Fixture to ensure the module is reloaded for each test."""
    if MODULE_NAME in sys.modules:
        del sys.modules[MODULE_NAME]
    yield
    if MODULE_NAME in sys.modules:
        del sys.modules[MODULE_NAME]


def test_fallback_mechanism_first_candidate(clean_module):
    """Test that the first candidate is loaded if available."""
    mock_candidate_one = MagicMock()
    mock_candidate_one.some_function = MagicMock()

    with patch.dict(sys.modules, {
        "lukhas_website.lukhas.cognitive_core.reasoning.deep_inference_engine": mock_candidate_one,
        "candidate.cognitive_core.reasoning.deep_inference_engine": None,
        "labs.cognitive_core.reasoning.deep_inference_engine": None,
    }):
        engine = importlib.import_module(MODULE_NAME)
        assert engine.some_function is mock_candidate_one.some_function
        assert "some_function" in engine.__all__


def test_fallback_mechanism_second_candidate(clean_module):
    """Test that the second candidate is loaded if the first fails."""
    mock_candidate_two = MagicMock()
    mock_candidate_two.another_function = MagicMock()

    with patch.dict(sys.modules, {
        "lukhas_website.lukhas.cognitive_core.reasoning.deep_inference_engine": None,
        "candidate.cognitive_core.reasoning.deep_inference_engine": mock_candidate_two,
        "labs.cognitive_core.reasoning.deep_inference_engine": None,
    }):
        # Mocking import_module to simulate import failure for the first candidate
        original_import = importlib.import_module
        def mock_import(name):
            if name == "lukhas_website.lukhas.cognitive_core.reasoning.deep_inference_engine":
                raise ImportError
            return original_import(name)

        with patch("importlib.import_module", side_effect=mock_import):
            engine = importlib.import_module(MODULE_NAME)
            assert engine.another_function is mock_candidate_two.another_function
            assert "another_function" in engine.__all__


def test_no_candidates_available(clean_module):
    """Test that the module is empty if no candidates are available."""
    original_import = importlib.import_module
    def mock_import(name):
        if any(name.startswith(p) for p in ["lukhas_website", "candidate", "labs"]):
            raise ImportError
        return original_import(name)

    with patch("importlib.import_module", side_effect=mock_import):
        engine = importlib.import_module(MODULE_NAME)
        assert len(engine.__all__) == 0
        with pytest.raises(AttributeError):
            _ = engine.some_random_attribute


def test_getattr_for_late_added_attribute(clean_module):
    """Test __getattr__ for attributes added to the backend after import."""
    # 1. Set up a simple backend mock
    class MockBackend:
        def public_function(self):
            return True

    mock_candidate = MockBackend()

    with patch.dict(sys.modules, {
        "lukhas_website.lukhas.cognitive_core.reasoning.deep_inference_engine": mock_candidate,
    }):
        # 2. Import the bridge module. This populates __all__
        engine = importlib.import_module(MODULE_NAME)

        # At this point, 'dynamic_attribute' does not exist
        assert "public_function" in engine.__all__
        assert "dynamic_attribute" not in engine.__all__
        with pytest.raises(AttributeError):
            _ = engine.dynamic_attribute

        # 3. Now, add the attribute to the original backend mock
        mock_candidate.dynamic_attribute = "hello"

        # 4. Access it through the bridge. This should now work via __getattr__
        assert engine.dynamic_attribute == "hello"


def test_getattr_attribute_error(clean_module):
    """Test that __getattr__ raises AttributeError for missing attributes."""
    mock_candidate = MagicMock()
    # Remove a potential attribute to ensure it's not found
    del mock_candidate.non_existent_attribute

    with patch.dict(sys.modules, {
        "lukhas_website.lukhas.cognitive_core.reasoning.deep_inference_engine": mock_candidate,
    }):
        engine = importlib.import_module(MODULE_NAME)
        with pytest.raises(AttributeError, match="module 'cognitive_core.reasoning.deep_inference_engine' has no attribute 'non_existent_attribute'"):
            _ = engine.non_existent_attribute
