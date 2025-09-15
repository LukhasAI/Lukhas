import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.consciousness_wordsmith_fixed import fix_later, register_fix_later
from src.attribution.fallback_ladder import BehavioralAnalyzer


@pytest.mark.asyncio
async def test_behavioral_analyzer_uses_context_opportunity():
    analyzer = BehavioralAnalyzer({"enabled": True, "confidence_threshold": 0.2})
    result = await analyzer.infer_attribution(
        "user-123",
        {"amount": 100},
        {"affiliate_params": {"opportunity_id": "opp_42", "source": "nias"}},
    )
    assert result["signals"]["likely_opportunity_id"] == "opp_42"
    assert result["attribution_likely"] is True


@pytest.mark.asyncio
async def test_behavioral_analyzer_disabled_returns_default():
    analyzer = BehavioralAnalyzer({"enabled": False})
    result = await analyzer.infer_attribution("user", {}, {})
    assert result["pattern"] == "behavioral_disabled"
    assert result["attribution_likely"] is False


def test_fix_later_registry_allows_resolution():
    register_fix_later("symbol", lambda value: f"resolved:{value}")
    assert fix_later("symbol", "ok") == "resolved:ok"
    assert fix_later("missing", default="fallback") == "fallback"
