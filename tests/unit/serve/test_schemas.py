"""
Comprehensive unit tests for serve/schemas.py

Tests Pydantic schema models including:
- DreamRequest/Response
- GlyphFeedbackRequest/Response
- TierAuthRequest/Response
- PluginLoadRequest/Response
- MemoryDumpResponse
- ModulatedChatRequest/Response
- Field validation (valid and invalid data)
"""

import pytest
from pydantic import ValidationError

from serve.schemas import (
    DreamRequest,
    DreamResponse,
    GlyphFeedbackRequest,
    GlyphFeedbackResponse,
    MemoryDumpResponse,
    ModulatedChatRequest,
    ModulatedChatResponse,
    PluginLoadRequest,
    PluginLoadResponse,
    TierAuthRequest,
    TierAuthResponse,
)


class TestDreamRequest:
    """Test DreamRequest schema validation."""

    def test_valid_dream_request(self):
        """Test creating valid DreamRequest."""
        request = DreamRequest(symbols=["star", "moon", "tree"])
        assert request.symbols == ["star", "moon", "tree"]

    def test_empty_symbols_list(self):
        """Test DreamRequest with empty symbols list."""
        request = DreamRequest(symbols=[])
        assert request.symbols == []

    def test_single_symbol(self):
        """Test DreamRequest with single symbol."""
        request = DreamRequest(symbols=["star"])
        assert len(request.symbols) == 1

    def test_missing_symbols_field_raises_validation_error(self):
        """Test that missing symbols field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DreamRequest()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("symbols",) for e in errors)

    def test_invalid_symbols_type_raises_validation_error(self):
        """Test that invalid symbols type raises ValidationError."""
        with pytest.raises(ValidationError):
            DreamRequest(symbols="not-a-list")

    def test_symbols_with_non_string_items(self):
        """Test that non-string items in symbols are coerced or raise error."""
        # Pydantic may coerce or raise depending on strict mode
        with pytest.raises(ValidationError):
            DreamRequest(symbols=[123, 456])


class TestDreamResponse:
    """Test DreamResponse schema validation."""

    def test_valid_dream_response(self):
        """Test creating valid DreamResponse."""
        response = DreamResponse(dream="A mystical journey through the stars")
        assert response.dream == "A mystical journey through the stars"

    def test_empty_dream_string(self):
        """Test DreamResponse with empty dream string."""
        response = DreamResponse(dream="")
        assert response.dream == ""

    def test_missing_dream_field_raises_validation_error(self):
        """Test that missing dream field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DreamResponse()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("dream",) for e in errors)

    def test_invalid_dream_type_raises_validation_error(self):
        """Test that invalid dream type raises ValidationError."""
        with pytest.raises(ValidationError):
            DreamResponse(dream=123)


class TestGlyphFeedbackRequest:
    """Test GlyphFeedbackRequest schema validation."""

    def test_valid_glyph_feedback_request(self):
        """Test creating valid GlyphFeedbackRequest."""
        request = GlyphFeedbackRequest(driftScore=0.75)
        assert request.driftScore == 0.75

    def test_zero_drift_score(self):
        """Test GlyphFeedbackRequest with zero drift score."""
        request = GlyphFeedbackRequest(driftScore=0.0)
        assert request.driftScore == 0.0

    def test_negative_drift_score(self):
        """Test GlyphFeedbackRequest with negative drift score."""
        request = GlyphFeedbackRequest(driftScore=-0.5)
        assert request.driftScore == -0.5

    def test_large_drift_score(self):
        """Test GlyphFeedbackRequest with large drift score."""
        request = GlyphFeedbackRequest(driftScore=1000.0)
        assert request.driftScore == 1000.0

    def test_missing_drift_score_raises_validation_error(self):
        """Test that missing driftScore raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GlyphFeedbackRequest()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("driftScore",) for e in errors)

    def test_invalid_drift_score_type_raises_validation_error(self):
        """Test that invalid driftScore type raises ValidationError."""
        with pytest.raises(ValidationError):
            GlyphFeedbackRequest(driftScore="not-a-number")


class TestGlyphFeedbackResponse:
    """Test GlyphFeedbackResponse schema validation."""

    def test_valid_glyph_feedback_response(self):
        """Test creating valid GlyphFeedbackResponse."""
        response = GlyphFeedbackResponse(suggestions=["adjust", "recalibrate", "stabilize"])
        assert len(response.suggestions) == 3

    def test_empty_suggestions_list(self):
        """Test GlyphFeedbackResponse with empty suggestions."""
        response = GlyphFeedbackResponse(suggestions=[])
        assert response.suggestions == []

    def test_single_suggestion(self):
        """Test GlyphFeedbackResponse with single suggestion."""
        response = GlyphFeedbackResponse(suggestions=["recalibrate"])
        assert response.suggestions == ["recalibrate"]

    def test_missing_suggestions_raises_validation_error(self):
        """Test that missing suggestions raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GlyphFeedbackResponse()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("suggestions",) for e in errors)


class TestTierAuthRequest:
    """Test TierAuthRequest schema validation."""

    def test_valid_tier_auth_request(self):
        """Test creating valid TierAuthRequest."""
        request = TierAuthRequest(token="secret-token-123")
        assert request.token == "secret-token-123"

    def test_empty_token(self):
        """Test TierAuthRequest with empty token."""
        request = TierAuthRequest(token="")
        assert request.token == ""

    def test_missing_token_raises_validation_error(self):
        """Test that missing token raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            TierAuthRequest()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("token",) for e in errors)

    def test_token_with_special_characters(self):
        """Test TierAuthRequest with special characters in token."""
        token = "token!@#$%^&*()_+-={}[]|:;<>?,./"
        request = TierAuthRequest(token=token)
        assert request.token == token


class TestTierAuthResponse:
    """Test TierAuthResponse schema validation."""

    def test_valid_tier_auth_response(self):
        """Test creating valid TierAuthResponse."""
        response = TierAuthResponse(access_rights=["read", "write", "execute"])
        assert response.access_rights == ["read", "write", "execute"]

    def test_empty_access_rights(self):
        """Test TierAuthResponse with empty access rights."""
        response = TierAuthResponse(access_rights=[])
        assert response.access_rights == []

    def test_single_access_right(self):
        """Test TierAuthResponse with single access right."""
        response = TierAuthResponse(access_rights=["read"])
        assert response.access_rights == ["read"]

    def test_missing_access_rights_raises_validation_error(self):
        """Test that missing access_rights raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            TierAuthResponse()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("access_rights",) for e in errors)


class TestPluginLoadRequest:
    """Test PluginLoadRequest schema validation."""

    def test_valid_plugin_load_request(self):
        """Test creating valid PluginLoadRequest."""
        request = PluginLoadRequest(symbols=["plugin_a", "plugin_b"])
        assert request.symbols == ["plugin_a", "plugin_b"]

    def test_empty_symbols_list(self):
        """Test PluginLoadRequest with empty symbols list."""
        request = PluginLoadRequest(symbols=[])
        assert request.symbols == []

    def test_single_symbol(self):
        """Test PluginLoadRequest with single symbol."""
        request = PluginLoadRequest(symbols=["plugin_a"])
        assert len(request.symbols) == 1

    def test_missing_symbols_raises_validation_error(self):
        """Test that missing symbols raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PluginLoadRequest()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("symbols",) for e in errors)


class TestPluginLoadResponse:
    """Test PluginLoadResponse schema validation."""

    def test_valid_plugin_load_response_success(self):
        """Test creating valid PluginLoadResponse with success status."""
        response = PluginLoadResponse(status="success")
        assert response.status == "success"

    def test_valid_plugin_load_response_failure(self):
        """Test creating valid PluginLoadResponse with failure status."""
        response = PluginLoadResponse(status="failure")
        assert response.status == "failure"

    def test_empty_status(self):
        """Test PluginLoadResponse with empty status."""
        response = PluginLoadResponse(status="")
        assert response.status == ""

    def test_missing_status_raises_validation_error(self):
        """Test that missing status raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PluginLoadResponse()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("status",) for e in errors)


class TestMemoryDumpResponse:
    """Test MemoryDumpResponse schema validation."""

    def test_valid_memory_dump_response(self):
        """Test creating valid MemoryDumpResponse."""
        folds = [
            {"id": "fold1", "data": "content1"},
            {"id": "fold2", "data": "content2"},
        ]
        response = MemoryDumpResponse(folds=folds)
        assert len(response.folds) == 2
        assert response.folds[0]["id"] == "fold1"

    def test_empty_folds_list(self):
        """Test MemoryDumpResponse with empty folds list."""
        response = MemoryDumpResponse(folds=[])
        assert response.folds == []

    def test_single_fold(self):
        """Test MemoryDumpResponse with single fold."""
        response = MemoryDumpResponse(folds=[{"id": "fold1"}])
        assert len(response.folds) == 1

    def test_fold_with_nested_data(self):
        """Test MemoryDumpResponse with nested fold data."""
        folds = [
            {
                "id": "fold1",
                "nested": {"key": "value", "list": [1, 2, 3]},
            }
        ]
        response = MemoryDumpResponse(folds=folds)
        assert response.folds[0]["nested"]["key"] == "value"

    def test_missing_folds_raises_validation_error(self):
        """Test that missing folds raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            MemoryDumpResponse()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("folds",) for e in errors)

    def test_invalid_folds_type_raises_validation_error(self):
        """Test that invalid folds type raises ValidationError."""
        with pytest.raises(ValidationError):
            MemoryDumpResponse(folds="not-a-list")


class TestModulatedChatRequest:
    """Test ModulatedChatRequest schema validation."""

    def test_valid_modulated_chat_request_minimal(self):
        """Test creating valid ModulatedChatRequest with only prompt."""
        request = ModulatedChatRequest(prompt="Hello, world!")
        assert request.prompt == "Hello, world!"

    def test_valid_modulated_chat_request_full(self):
        """Test creating valid ModulatedChatRequest with all fields."""
        request = ModulatedChatRequest(
            prompt="Hello, world!",
            # Note: context and task are module-level variables in schemas.py,
            # not part of ModulatedChatRequest model
        )
        assert request.prompt == "Hello, world!"

    def test_empty_prompt(self):
        """Test ModulatedChatRequest with empty prompt."""
        request = ModulatedChatRequest(prompt="")
        assert request.prompt == ""

    def test_long_prompt(self):
        """Test ModulatedChatRequest with very long prompt."""
        long_prompt = "A" * 10000
        request = ModulatedChatRequest(prompt=long_prompt)
        assert len(request.prompt) == 10000

    def test_missing_prompt_raises_validation_error(self):
        """Test that missing prompt raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ModulatedChatRequest()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("prompt",) for e in errors)

    def test_invalid_prompt_type_raises_validation_error(self):
        """Test that invalid prompt type raises ValidationError."""
        with pytest.raises(ValidationError):
            ModulatedChatRequest(prompt=123)


class TestModulatedChatResponse:
    """Test ModulatedChatResponse schema validation."""

    def test_valid_modulated_chat_response_minimal(self):
        """Test creating valid ModulatedChatResponse with only content."""
        response = ModulatedChatResponse(content="Response text")
        assert response.content == "Response text"

    def test_valid_modulated_chat_response_full(self):
        """Test creating valid ModulatedChatResponse with all fields."""
        response = ModulatedChatResponse(
            content="Response text",
            # Note: raw, modulation, metadata are module-level variables,
            # not part of ModulatedChatResponse model
        )
        assert response.content == "Response text"

    def test_empty_content(self):
        """Test ModulatedChatResponse with empty content."""
        response = ModulatedChatResponse(content="")
        assert response.content == ""

    def test_missing_content_raises_validation_error(self):
        """Test that missing content raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ModulatedChatResponse()

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("content",) for e in errors)

    def test_invalid_content_type_raises_validation_error(self):
        """Test that invalid content type raises ValidationError."""
        with pytest.raises(ValidationError):
            ModulatedChatResponse(content={"not": "a string"})


class TestSchemaInteroperability:
    """Test schema interoperability and edge cases."""

    def test_dream_request_response_flow(self):
        """Test typical flow from request to response."""
        request = DreamRequest(symbols=["star", "moon"])
        # Simulate processing
        response = DreamResponse(dream="A dream about stars and moons")
        assert request.symbols == ["star", "moon"]
        assert "stars" in response.dream.lower()

    def test_tier_auth_request_response_flow(self):
        """Test typical auth flow."""
        request = TierAuthRequest(token="secret-token")
        # Simulate auth
        response = TierAuthResponse(access_rights=["read", "write"])
        assert request.token == "secret-token"
        assert "read" in response.access_rights

    def test_plugin_load_request_response_flow(self):
        """Test typical plugin load flow."""
        request = PluginLoadRequest(symbols=["plugin_a", "plugin_b"])
        response = PluginLoadResponse(status="success")
        assert len(request.symbols) == 2
        assert response.status == "success"

    def test_modulated_chat_request_response_flow(self):
        """Test typical chat flow."""
        request = ModulatedChatRequest(prompt="What is the meaning of life?")
        response = ModulatedChatResponse(content="42")
        assert "meaning" in request.prompt.lower()
        assert response.content == "42"


class TestSchemaSerializationDeserialization:
    """Test schema serialization and deserialization."""

    def test_dream_request_dict_roundtrip(self):
        """Test DreamRequest dict serialization roundtrip."""
        original = DreamRequest(symbols=["star", "moon"])
        data = original.model_dump()
        restored = DreamRequest(**data)
        assert original.symbols == restored.symbols

    def test_memory_dump_response_dict_roundtrip(self):
        """Test MemoryDumpResponse dict serialization roundtrip."""
        original = MemoryDumpResponse(
            folds=[{"id": "f1", "data": "d1"}, {"id": "f2", "data": "d2"}]
        )
        data = original.model_dump()
        restored = MemoryDumpResponse(**data)
        assert original.folds == restored.folds

    def test_tier_auth_response_json_roundtrip(self):
        """Test TierAuthResponse JSON serialization roundtrip."""
        original = TierAuthResponse(access_rights=["read", "write", "execute"])
        json_str = original.model_dump_json()
        restored = TierAuthResponse.model_validate_json(json_str)
        assert original.access_rights == restored.access_rights


class TestValidationErrorMessages:
    """Test that validation errors have helpful messages."""

    def test_missing_field_error_message(self):
        """Test that missing field errors are clear."""
        with pytest.raises(ValidationError) as exc_info:
            DreamRequest()

        errors = exc_info.value.errors()
        # Should indicate field is missing/required
        assert any("required" in str(e["type"]).lower() for e in errors)

    def test_wrong_type_error_message(self):
        """Test that type errors are clear."""
        with pytest.raises(ValidationError) as exc_info:
            DreamRequest(symbols="not-a-list")

        errors = exc_info.value.errors()
        # Should indicate type issue
        assert len(errors) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_in_string_fields(self):
        """Test Unicode characters in string fields."""
        request = DreamRequest(symbols=["🌟", "🌙", "🌳"])
        assert "🌟" in request.symbols

    def test_very_large_lists(self):
        """Test handling of very large lists."""
        large_list = [f"symbol_{i}" for i in range(1000)]
        request = DreamRequest(symbols=large_list)
        assert len(request.symbols) == 1000

    def test_deeply_nested_dict_in_memory_dump(self):
        """Test deeply nested structures in MemoryDumpResponse."""
        nested = {"level1": {"level2": {"level3": {"level4": "value"}}}}
        response = MemoryDumpResponse(folds=[nested])
        assert response.folds[0]["level1"]["level2"]["level3"]["level4"] == "value"

    def test_special_characters_in_strings(self):
        """Test special characters in string fields."""
        special = 'Test with "quotes" and \\backslashes\\ and \nnewlines'
        request = ModulatedChatRequest(prompt=special)
        assert request.prompt == special

    def test_null_values_rejected(self):
        """Test that null values are rejected for required fields."""
        with pytest.raises(ValidationError):
            DreamRequest(symbols=None)
