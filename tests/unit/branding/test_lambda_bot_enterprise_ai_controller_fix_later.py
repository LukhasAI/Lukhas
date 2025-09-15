"""Unit tests for the deferred implementation helper."""

from datetime import datetime, timezone
from pathlib import Path
import importlib.util
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = (
    PROJECT_ROOT
    / "branding"
    / "engines"
    / "lukhas_content_platform"
    / "bots"
    / "lambda_bot_enterprise_ai_controller_lambda_bot.py"
)

spec = importlib.util.spec_from_file_location("lambda_bot_ai_controller", MODULE_PATH)
assert spec and spec.loader, "Unable to load lambda bot module for testing"
lambda_bot_module = importlib.util.module_from_spec(spec)
sys.modules.setdefault("lambda_bot_ai_controller_test_module", lambda_bot_module)
spec.loader.exec_module(lambda_bot_module)

DEFAULT_FIX_LATER_MESSAGE = lambda_bot_module.DEFAULT_FIX_LATER_MESSAGE
DeferredImplementationSignal = lambda_bot_module.DeferredImplementationSignal
fix_later = lambda_bot_module.fix_later


def test_fix_later_defaults():
    """Ensure the default signal contains baseline metadata."""

    signal = fix_later()

    assert isinstance(signal, DeferredImplementationSignal)
    assert signal.message == DEFAULT_FIX_LATER_MESSAGE
    assert signal.args == ()
    assert signal.metadata == {}
    assert signal.drift_score == 0.0
    assert signal.affect_delta == 0.0

    payload = signal.to_payload()
    assert payload["message"] == DEFAULT_FIX_LATER_MESSAGE
    created_at = datetime.fromisoformat(payload["created_at"])
    assert created_at.tzinfo == timezone.utc
    assert payload["args"] == []
    assert payload["metadata"] == {}


def test_fix_later_custom_metadata_preserved():
    """Custom messages, args, and metadata should be respected."""

    source_metadata = {"source": "unit", "drift_score": 0.25}

    signal = fix_later(
        "custom message",
        "module-x",
        metadata=source_metadata,
        stage="alpha",
        drift_score=0.5,
        affect_delta=0.125,
    )

    # The original metadata dict should remain unchanged.
    assert source_metadata == {"source": "unit", "drift_score": 0.25}

    assert signal.message == "custom message"
    assert signal.args == ("module-x",)
    assert signal.metadata == {"source": "unit", "stage": "alpha"}
    assert signal.drift_score == pytest.approx(0.5)
    assert signal.affect_delta == pytest.approx(0.125)

    payload = signal.to_payload()
    assert payload["metadata"] == {"source": "unit", "stage": "alpha"}
    assert payload["args"] == ["module-x"]


def test_fix_later_handles_non_numeric_scores():
    """Invalid numeric inputs fall back to a safe default."""

    signal = fix_later(drift_score="invalid", affect_delta=None)

    assert signal.drift_score == 0.0
    assert signal.affect_delta == 0.0
