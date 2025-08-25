import pytest
import json
from datetime import datetime

import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from candidate.core.common.glyph import (
    GLYPHToken,
    GLYPHSymbol,
    GLYPHContext,
    create_glyph,
    parse_glyph,
    validate_glyph,
    create_response_glyph,
    create_error_glyph,
)

def test_glyph_token_creation():
    """Tests the creation of a GLYPHToken."""
    glyph = create_glyph(
        symbol=GLYPHSymbol.CONNECT,
        source="test_source",
        target="test_target",
        payload={"data": "test_payload"},
    )
    assert isinstance(glyph, GLYPHToken)
    assert glyph.symbol == GLYPHSymbol.CONNECT
    assert glyph.source == "test_source"
    assert glyph.target == "test_target"
    assert glyph.payload == {"data": "test_payload"}

def test_glyph_token_serialization():
    """Tests the serialization and deserialization of a GLYPHToken."""
    glyph = create_glyph(
        symbol=GLYPHSymbol.DREAM,
        source="dream_engine",
        target="consciousness",
        payload={"dream_id": "dream_123"},
    )

    # Test to_dict and from_dict
    glyph_dict = glyph.to_dict()
    parsed_glyph_from_dict = GLYPHToken.from_dict(glyph_dict)
    assert glyph.to_dict() == parsed_glyph_from_dict.to_dict()

    # Test to_json and from_json
    glyph_json = glyph.to_json()
    parsed_glyph_from_json = GLYPHToken.from_json(glyph_json)
    assert glyph.to_dict() == parsed_glyph_from_json.to_dict()

    # Test parse_glyph function
    parsed_glyph = parse_glyph(glyph_json)
    assert glyph.to_dict() == parsed_glyph.to_dict()

def test_glyph_token_metadata():
    """Tests the metadata functionality of a GLYPHToken."""
    glyph = create_glyph(symbol=GLYPHSymbol.ADAPT, source="learning", target="all")

    glyph.add_to_trace("module_a")
    glyph.add_to_trace("module_b")
    assert glyph.context.module_trace == ["module_a", "module_b"]

    glyph.set_metadata("test_key", "test_value")
    assert glyph.get_metadata("test_key") == "test_value"
    assert glyph.get_metadata("nonexistent_key") is None

def test_glyph_response_creation():
    """Tests the creation of response and error glyphs."""
    request_glyph = create_glyph(
        symbol=GLYPHSymbol.QUERY,
        source="user",
        target="memory",
        payload={"query": "What is LUKHAS?"},
    )

    # Test response glyph
    response_glyph = create_response_glyph(
        request=request_glyph,
        symbol=GLYPHSymbol.SUCCESS,
        payload={"answer": "LUKHAS is an AI."},
    )
    assert response_glyph.target == request_glyph.source
    assert response_glyph.source == request_glyph.target
    assert response_glyph.get_metadata("request_id") == request_glyph.glyph_id

    # Test error glyph
    error_glyph = create_error_glyph(
        request=request_glyph,
        error_message="Memory module not available.",
        error_code="MEMORY_ERROR",
    )
    assert error_glyph.symbol == GLYPHSymbol.ERROR
    assert error_glyph.payload["error"] == "MEMORY_ERROR"
    assert "Memory module not available" in error_glyph.payload["message"]

def test_glyph_validation():
    """Tests the validation of a GLYPHToken."""
    valid_glyph = create_glyph(symbol=GLYPHSymbol.SYNC, source="a", target="b")
    assert validate_glyph(valid_glyph)

    invalid_glyph = GLYPHToken(glyph_id="", symbol=GLYPHSymbol.SYNC, source="a", target="b")
    with pytest.raises(Exception):
        validate_glyph(invalid_glyph)
