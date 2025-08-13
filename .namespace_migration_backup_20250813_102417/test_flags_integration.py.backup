#!/usr/bin/env python3
"""
Integration tests for feature flags in core code paths
========================================================
Verifies that FLAG_* environment variables properly control:
- Browser tool availability (FLAG_BROWSER_TOOL)
- Strict safety mode default (FLAG_STRICT_DEFAULT)
- Tool analytics logging (FLAG_TOOL_ANALYTICS)
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_browser_tool_flag():
    """Test FLAG_BROWSER_TOOL gates browser tool availability"""
    from lukhas.flags.ff import Flags
    from lukhas.openai.tooling import build_tools_from_allowlist

    # Test with flag disabled (default)
    with patch.dict(os.environ, {}, clear=False):
        # Remove flag if it exists
        os.environ.pop("FLAG_BROWSER_TOOL", None)
        # Force cache refresh
        Flags._ts = 0

        tools = build_tools_from_allowlist(["retrieval", "browser", "scheduler"])
        tool_names = [t["function"]["name"] for t in tools]

        # Browser should be excluded
        assert "retrieve_knowledge" in tool_names
        assert "open_url" not in tool_names  # Browser tool blocked
        assert "schedule_task" in tool_names

    # Test with flag enabled
    with patch.dict(os.environ, {"FLAG_BROWSER_TOOL": "true"}):
        # Force cache refresh
        Flags._ts = 0

        tools = build_tools_from_allowlist(["retrieval", "browser", "scheduler"])
        tool_names = [t["function"]["name"] for t in tools]

        # All tools should be present
        assert "retrieve_knowledge" in tool_names
        assert "open_url" in tool_names  # Browser tool allowed
        assert "schedule_task" in tool_names

    print("✅ Browser tool flag works correctly")


def test_strict_default_flag():
    """Test FLAG_STRICT_DEFAULT forces strict safety mode"""
    from lukhas.flags.ff import Flags
    from lukhas.modulation.dispatcher import Modulator

    # Mock policy file
    policy = {
        "signals": [
            {"name": "stress", "cooldown_ms": 100},
            {"name": "alignment_risk", "cooldown_ms": 100},
        ],
        "maps": {},
        "bounds": {
            "temperature": [0.1, 1.0],
            "top_p": [0.1, 1.0],
            "max_output_tokens": [100, 4000],
            "retrieval_k": [1, 20],
            "planner_beam": [1, 5],
            "memory_write": [0.0, 1.0],
        },
        "prompt_styles": {
            "strict": {"system": "Be extremely cautious"},
            "balanced": {"system": "Be helpful and safe"},
        },
    }

    # Test without flag (default balanced)
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("FLAG_STRICT_DEFAULT", None)
        # Force cache refresh
        Flags._ts = 0

        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = str(
                policy
            )
            with patch("yaml.safe_load", return_value=policy):
                modulator = Modulator("dummy_path")
                params = modulator.combine([])
                assert params["safety_mode"] == "balanced"

    # Test with flag enabled (strict mode)
    with patch.dict(os.environ, {"FLAG_STRICT_DEFAULT": "1"}):
        # Force cache refresh
        Flags._ts = 0

        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = str(
                policy
            )
            with patch("yaml.safe_load", return_value=policy):
                modulator = Modulator("dummy_path")
                params = modulator.combine([])
                assert params["safety_mode"] == "strict"

    print("✅ Strict default flag works correctly")


def test_tool_analytics_flag():
    """Test FLAG_TOOL_ANALYTICS controls analytics logging"""
    from lukhas.audit.tool_analytics import ToolAnalytics
    from lukhas.flags.ff import Flags

    # Test with analytics enabled (default)
    with patch.dict(os.environ, {"FLAG_TOOL_ANALYTICS": "true"}):
        # Force cache refresh
        Flags._ts = 0
        analytics = ToolAnalytics()

        # Start and complete a tool call
        call_id = analytics.start_tool_call("test_tool", {"arg": "value"})
        analytics.complete_tool_call(call_id, status="success")

        # Should have recorded the call
        assert len(analytics.completed_calls) == 1
        assert analytics.completed_calls[0].tool_name == "test_tool"

    # Test with analytics disabled
    with patch.dict(os.environ, {"FLAG_TOOL_ANALYTICS": "false"}):
        # Force cache refresh
        Flags._ts = 0
        analytics = ToolAnalytics()

        # Start and complete a tool call
        call_id = analytics.start_tool_call("test_tool", {"arg": "value"})
        analytics.complete_tool_call(call_id, status="success")

        # Should NOT have recorded the call (no-op mode)
        assert len(analytics.completed_calls) == 0
        assert len(analytics.active_calls) == 0

    print("✅ Tool analytics flag works correctly")


def test_analytics_incident_logging():
    """Test that incident logging respects FLAG_TOOL_ANALYTICS"""
    from lukhas.audit.tool_analytics import ToolAnalytics
    from lukhas.flags.ff import Flags

    # Test with analytics enabled
    with patch.dict(os.environ, {"FLAG_TOOL_ANALYTICS": "true"}):
        # Force cache refresh
        Flags._ts = 0
        analytics = ToolAnalytics()

        # Mock the write_incident function to track calls
        with patch("lukhas.audit.tool_analytics.write_incident") as mock_write:
            incident = analytics.record_blocked_attempt(
                audit_id="test_audit",
                attempted_tool="dangerous_tool",
                allowed_tools=["safe_tool"],
                prompt="test prompt",
            )

            # Should have written incident to file
            mock_write.assert_called_once()
            assert incident.attempted_tool == "dangerous_tool"

    # Test with analytics disabled
    with patch.dict(os.environ, {"FLAG_TOOL_ANALYTICS": "false"}):
        # Force cache refresh
        Flags._ts = 0
        analytics = ToolAnalytics()

        with patch("lukhas.audit.tool_analytics.write_incident") as mock_write:
            incident = analytics.record_blocked_attempt(
                audit_id="test_audit",
                attempted_tool="dangerous_tool",
                allowed_tools=["safe_tool"],
                prompt="test prompt",
            )

            # Should NOT have written to file
            mock_write.assert_not_called()
            # But incident should still be in memory for current session
            assert len(analytics.incidents) == 1

    print("✅ Analytics incident logging respects flag")


def test_flag_combinations():
    """Test various flag combinations work together"""
    from lukhas.flags.ff import Flags
    from lukhas.modulation.dispatcher import Modulator
    from lukhas.openai.tooling import build_tools_from_allowlist

    # Test: strict mode + no browser + no analytics
    with patch.dict(
        os.environ,
        {
            "FLAG_STRICT_DEFAULT": "on",
            "FLAG_BROWSER_TOOL": "false",
            "FLAG_TOOL_ANALYTICS": "0",
        },
    ):
        # Force cache refresh
        Flags._ts = 0
        # Check browser exclusion
        tools = build_tools_from_allowlist(["browser", "retrieval"])
        tool_names = [t["function"]["name"] for t in tools]
        assert "open_url" not in tool_names
        assert "retrieve_knowledge" in tool_names

        # Check strict mode (with mocked policy)
        policy = {
            "signals": [],
            "maps": {},
            "bounds": {
                "temperature": [0.1, 1.0],
                "top_p": [0.1, 1.0],
                "max_output_tokens": [100, 4000],
                "retrieval_k": [1, 20],
                "planner_beam": [1, 5],
                "memory_write": [0.0, 1.0],
            },
            "prompt_styles": {
                "strict": {"system": "strict"},
                "balanced": {"system": "balanced"},
            },
        }

        with patch("builtins.open", create=True):
            with patch("yaml.safe_load", return_value=policy):
                modulator = Modulator("dummy")
                params = modulator.combine([])
                assert params["safety_mode"] == "strict"

    print("✅ Flag combinations work correctly")


def main():
    """Run all feature flag integration tests"""
    print("🧪 Testing Feature Flags in Core Code Paths...")
    print("=" * 50)

    try:
        test_browser_tool_flag()
        test_strict_default_flag()
        test_tool_analytics_flag()
        test_analytics_incident_logging()
        test_flag_combinations()

        print("\n" + "=" * 50)
        print("🎉 All feature flag tests passed!")
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
