"""
LLM Guardrail Tests

Smoke tests for the LLM guardrail module to ensure schema validation
and error handling work correctly.
"""

import os
import pytest
import sys
from unittest.mock import patch

# Import bypassing compat layer to avoid recursion in tests
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from lukhas.core.bridge.llm_guardrail import call_llm, guardrail_health


def fake_llm_good(prompt):
    """Mock LLM that returns valid response."""
    return {"title": "Analysis Complete", "score": 0.85}


def fake_llm_bad(prompt):
    """Mock LLM that returns invalid response (missing required field)."""
    return {"title": 123}  # Wrong type for title


def fake_llm_missing(prompt):
    """Mock LLM that returns response missing required field."""
    return {"title": "Analysis"}  # Missing score


class TestLLMGuardrail:
    """Test suite for LLM guardrail functionality."""

    def test_guardrail_pass(self, monkeypatch):
        """Test guardrail allows valid schema responses."""
        monkeypatch.setenv("ENABLE_LLM_GUARDRAIL", "1")

        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "score": {"type": "number"}
            },
            "required": ["title", "score"]
        }

        result = call_llm(prompt="Analyze this", schema=schema, llm=fake_llm_good)
        assert result["score"] == 0.85
        assert result["title"] == "Analysis Complete"

    def test_guardrail_fail_bad_type(self, monkeypatch):
        """Test guardrail rejects response with wrong type."""
        monkeypatch.setenv("ENABLE_LLM_GUARDRAIL", "1")

        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "score": {"type": "number"}
            },
            "required": ["title", "score"]
        }

        with pytest.raises(ValueError) as exc_info:
            call_llm(prompt="Analyze this", schema=schema, llm=fake_llm_bad)

        assert "schema validation" in str(exc_info.value).lower()

    def test_guardrail_fail_missing_field(self, monkeypatch):
        """Test guardrail rejects response missing required field."""
        monkeypatch.setenv("ENABLE_LLM_GUARDRAIL", "1")

        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "score": {"type": "number"}
            },
            "required": ["title", "score"]
        }

        with pytest.raises(ValueError) as exc_info:
            call_llm(prompt="Analyze this", schema=schema, llm=fake_llm_missing)

        assert "schema validation" in str(exc_info.value).lower()

    def test_guardrail_disabled(self, monkeypatch):
        """Test guardrail fails when disabled."""
        monkeypatch.setenv("ENABLE_LLM_GUARDRAIL", "0")

        schema = {"type": "object", "properties": {"score": {"type": "number"}}}

        with pytest.raises(RuntimeError) as exc_info:
            call_llm(prompt="test", schema=schema, llm=fake_llm_good)

        assert "not enabled" in str(exc_info.value)

    def test_guardrail_health(self, monkeypatch):
        """Test guardrail health check function."""
        monkeypatch.setenv("ENABLE_LLM_GUARDRAIL", "1")
        monkeypatch.setenv("LUKHAS_LANE", "candidate")

        health = guardrail_health()
        assert health["enabled"] is True
        assert health["lane"] == "candidate"
        assert "version" in health

    def test_stub_response_when_no_llm(self, monkeypatch):
        """Test guardrail returns stub when no LLM provided."""
        monkeypatch.setenv("ENABLE_LLM_GUARDRAIL", "1")

        schema = {
            "type": "object",
            "properties": {
                "_stub": {"type": "boolean"},
                "message": {"type": "string"}
            },
            "required": ["_stub", "message"]
        }

        result = call_llm(prompt="test", schema=schema)  # No llm parameter
        assert result["_stub"] is True
        assert "guardrail active" in result["message"]