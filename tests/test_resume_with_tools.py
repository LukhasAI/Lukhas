#!/usr/bin/env python3
"""
Unit tests for resume_with_tools helper
========================================
Tests deterministic tool execution without calling OpenAI.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge.llm_wrappers.openai_modulated_service import resume_with_tools


def test_resume_with_tools_allows_and_blocks():
    """Test that allowed tools execute and blocked tools generate system messages"""
    
    # Initial messages
    messages = [
        {"role": "user", "content": "Fetch notes then open a url."}
    ]
    
    # Tool calls to test
    tool_calls = [
        {
            "id": "t1",
            "function": {
                "name": "retrieve_knowledge",
                "arguments": json.dumps({"k": 2, "query": "modulation policy"})
            }
        },
        {
            "id": "t2",
            "function": {
                "name": "open_url",
                "arguments": json.dumps({"url": "https://openai.com"})
            }
        },
    ]
    
    # Only retrieval allowed, browser blocked
    allowlist = ["retrieval"]
    
    # Execute
    out = resume_with_tools(messages, tool_calls, allowlist, audit_id="A-UNIT-1")
    
    # Verify results
    tool_msgs = [m for m in out if m["role"] == "tool"]
    sys_msgs = [m for m in out if m["role"] == "system" and "blocked" in m["content"].lower()]
    
    # Should have one tool execution (retrieval)
    assert len(tool_msgs) == 1, f"Expected 1 tool message, got {len(tool_msgs)}"
    assert tool_msgs[0]["name"] == "retrieve_knowledge"
    assert "knowledge" in tool_msgs[0]["content"].lower() or "context" in tool_msgs[0]["content"].lower()
    
    # Should have one system message about blocked browser
    assert len(sys_msgs) == 1, f"Expected 1 system message about blocking, got {len(sys_msgs)}"
    assert "open_url" in sys_msgs[0]["content"] or "blocked" in sys_msgs[0]["content"].lower()
    
    print("✅ Test passed: Tools correctly allowed and blocked")


def test_resume_with_scheduler():
    """Test scheduler tool execution"""
    
    messages = [
        {"role": "user", "content": "Schedule a meeting for tomorrow"}
    ]
    
    tool_calls = [
        {
            "id": "sched1",
            "function": {
                "name": "schedule_task",
                "arguments": json.dumps({"when": "tomorrow 2pm", "note": "Team meeting"})
            }
        }
    ]
    
    allowlist = ["scheduler"]
    
    out = resume_with_tools(messages, tool_calls, allowlist, audit_id="A-SCHED-1")
    
    # Check for successful scheduling
    tool_msgs = [m for m in out if m["role"] == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0]["name"] == "schedule_task"
    assert "scheduled" in tool_msgs[0]["content"].lower() or "task" in tool_msgs[0]["content"].lower()
    
    print("✅ Test passed: Scheduler works correctly")


def test_all_tools_blocked():
    """Test when no tools are allowed"""
    
    messages = [{"role": "user", "content": "Do everything"}]
    
    tool_calls = [
        {"id": "tc1", "function": {"name": "retrieve_knowledge", "arguments": "{}"}},
        {"id": "tc2", "function": {"name": "open_url", "arguments": "{}"}},
        {"id": "tc3", "function": {"name": "schedule_task", "arguments": "{}"}},
    ]
    
    allowlist = []  # Empty allowlist
    
    out = resume_with_tools(messages, tool_calls, allowlist, audit_id="A-BLOCK-ALL")
    
    # All should be blocked
    tool_msgs = [m for m in out if m["role"] == "tool"]
    sys_msgs = [m for m in out if m["role"] == "system" and "blocked" in m["content"].lower()]
    
    assert len(tool_msgs) == 0, "No tools should execute with empty allowlist"
    assert len(sys_msgs) == 3, f"Expected 3 block messages, got {len(sys_msgs)}"
    
    print("✅ Test passed: Empty allowlist blocks all tools")


def test_tool_execution_error():
    """Test handling of tool execution errors"""
    
    messages = [{"role": "user", "content": "Execute code"}]
    
    # Invalid JSON arguments to trigger error
    tool_calls = [
        {
            "id": "err1",
            "function": {
                "name": "retrieve_knowledge",
                "arguments": "not-valid-json"  # This should cause a parsing error
            }
        }
    ]
    
    allowlist = ["retrieval"]
    
    # This should handle the error gracefully
    out = resume_with_tools(messages, tool_calls, allowlist, audit_id="A-ERROR-1")
    
    tool_msgs = [m for m in out if m["role"] == "tool"]
    assert len(tool_msgs) == 1
    # Even with invalid JSON, executor should handle it
    assert tool_msgs[0]["content"] is not None
    
    print("✅ Test passed: Tool errors handled gracefully")


def main():
    """Run all tests"""
    print("🧪 Testing resume_with_tools helper...")
    print("=" * 50)
    
    try:
        test_resume_with_tools_allows_and_blocks()
        test_resume_with_scheduler()
        test_all_tools_blocked()
        test_tool_execution_error()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed!")
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