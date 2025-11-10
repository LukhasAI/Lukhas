
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import copy
import asyncio

# Main API functions to test
from lukhas.glyphs import (
    bind_glyph,
    get_binding,
    is_enabled,
    get_glyph_engine,
    encode_concept,
    decode_symbol,
    validate_glyph,
    get_glyph_stats,
    verify_glyph_token,
)

# Implementation classes that will be mocked
from candidate.glyphs.glyph_verifier import GlyphVerifier
from candidate.glyphs.glyph_binder import GlyphBinder
from candidate.glyphs.glyph_retriever import GlyphRetriever

# --- Test Suite Setup ---

@pytest.fixture(autouse=True)
def clear_bindings():
    """Fixture to automatically clear the in-memory binding store after each test."""
    # Run before the test
    yield
    # Run after the test
    asyncio.run(GlyphRetriever._clear_bindings_for_testing())

# --- verify_glyph_token tests (async) ---

@pytest.mark.asyncio
async def test_verify_glyph_token_valid():
    """Test verify_glyph_token with a valid, freshly generated token."""
    token = GlyphVerifier._generate_test_token("user1")
    result = await verify_glyph_token(token, "user1")
    assert result is True

@pytest.mark.asyncio
async def test_verify_glyph_token_user_mismatch():
    """Test that a token for one user is invalid for another."""
    token = GlyphVerifier._generate_test_token("user1")
    result = await verify_glyph_token(token, "user2")
    assert result is False

@pytest.mark.asyncio
async def test_verify_glyph_token_expired():
    """Test that an expired token is invalid."""
    token = GlyphVerifier._generate_test_token("user1", expires_in_seconds=-1)
    result = await verify_glyph_token(token, "user1")
    assert result is False

@pytest.mark.asyncio
async def test_verify_glyph_token_invalid_format():
    """Test that a malformed token is invalid."""
    result = await verify_glyph_token("not-a-valid-token", "user1")
    assert result is False

# --- bind_glyph tests (synchronous public API) ---

def test_bind_glyph_success():
    """Test a successful glyph binding flow."""
    with patch('lukhas.glyphs.is_enabled', return_value=True):
        result = bind_glyph(
            glyph_data={"concept": "test"},
            memory_id="mem123",
            user_id="user1"
        )
        assert result["success"] is True
        assert "binding_id" in result

        # Verify it was actually stored
        binding = get_binding(result["binding_id"])
        assert binding is not None
        assert binding["glyph_id"] == "mem123"

def test_bind_glyph_with_valid_token():
    """Test binding succeeds when a valid token is provided."""
    token = GlyphVerifier._generate_test_token("user1")
    with patch('lukhas.glyphs.is_enabled', return_value=True):
        result = bind_glyph(
            glyph_data={"concept": "test"},
            memory_id="mem123",
            user_id="user1",
            token=token
        )
        assert result["success"] is True

def test_bind_glyph_with_invalid_token():
    """Test binding fails when an invalid token is provided."""
    token = GlyphVerifier._generate_test_token("user1", expires_in_seconds=-1)
    with patch('lukhas.glyphs.is_enabled', return_value=True):
        result = bind_glyph(
            glyph_data={"concept": "test"},
            memory_id="mem123",
            user_id="user1",
            token=token
        )
        assert result["success"] is False
        assert result["error"] == "Invalid or expired token"

def test_bind_glyph_input_validation():
    """Test input validation for bind_glyph."""
    with patch('lukhas.glyphs.is_enabled', return_value=True):
        assert "must be non-empty dictionary" in bind_glyph({}, "mem1", "u1")["error"]
        assert "must be non-empty string" in bind_glyph({"c": "t"}, "", "u1")["error"]
        assert "user_id is required" in bind_glyph({"c": "t"}, "mem1", None)["error"]

def test_bind_and_get_flow():
    """Test that a bound glyph can be retrieved."""
    with patch('lukhas.glyphs.is_enabled', return_value=True):
        # Bind
        bind_result = bind_glyph({"concept": "flow"}, "mem-flow", "user-flow")
        assert bind_result["success"] is True
        binding_id = bind_result["binding_id"]

        # Retrieve
        get_result = get_binding(binding_id)
        assert get_result is not None
        assert get_result["binding_id"] == binding_id
        assert get_result["user_id"] == "user-flow"
        assert get_result["context"]["original_memory_id"] == "mem-flow"

# --- get_binding tests (synchronous public API) ---

def test_get_binding_not_found():
    """Test retrieving a non-existent binding."""
    with patch('lukhas.glyphs.is_enabled', return_value=True):
        result = get_binding("non-existent-id")
        assert result is None

def test_get_binding_disabled():
    """Test get_binding when the feature is disabled."""
    with patch('lukhas.glyphs.is_enabled', return_value=False):
        result = get_binding("any-id")
        assert result is None

# --- Other Function Coverage ---

def test_is_enabled():
    with patch('lukhas.glyphs._GLYPHS_ENABLED', True), patch('lukhas.glyphs._GLYPHS_AVAILABLE', True):
        assert is_enabled() is True
    with patch('lukhas.glyphs._GLYPHS_ENABLED', False):
        assert is_enabled() is False

def test_get_glyph_engine():
    with patch('lukhas.glyphs.is_enabled', return_value=False):
        assert get_glyph_engine() is None
    with patch('lukhas.glyphs.is_enabled', return_value=True), patch('lukhas.glyphs._glyph_engine', "engine"):
        assert get_glyph_engine() == "engine"

def test_encode_concept_and_decode_symbol():
    with patch('lukhas.glyphs.is_enabled', return_value=False):
        assert encode_concept("test") is None
        assert decode_symbol({"c": "t"}) is None
    with patch('lukhas.glyphs.is_enabled', return_value=True):
        # Mock the engine for encode
        mock_engine = MagicMock()
        mock_engine.encode_concept.return_value = MagicMock(symbol_id="sym123")
        with patch('lukhas.glyphs._glyph_engine', mock_engine):
            result = encode_concept("test")
            assert result["symbol_id"] == "sym123"
        # Test decode
        assert decode_symbol({"concept": "test"}) == "test"

@pytest.mark.parametrize("data, is_valid, msg_part", [
    ({"concept": "test"}, True, None),
    ({}, False, "Missing required field"),
    ({"concept": ""}, False, "must be a non-empty string"),
    (None, False, "must be a dictionary"),
    ({"concept": "c" * 1001}, False, "exceeds maximum length"),
    ({"concept": "t", "emotion": {"joy": 1.1}}, False, "must be between 0.0 and 1.0"),
])
def test_validate_glyph(data, is_valid, msg_part):
    valid, message = validate_glyph(data)
    assert valid == is_valid
    if msg_part:
        assert msg_part in message

def test_get_glyph_stats():
    with patch('lukhas.glyphs.is_enabled', return_value=False):
        assert get_glyph_stats()["enabled"] is False

    mock_engine = MagicMock()
    mock_engine.stats = {"count": 5}
    with patch('lukhas.glyphs.is_enabled', return_value=True), \
         patch('lukhas.glyphs._glyph_engine', mock_engine):
        assert get_glyph_stats()["stats"]["count"] == 5
