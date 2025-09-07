#!/usr/bin/env python3
"""
LUKHAS  OpenAI Integration Demo ⚛️🧠🛡️
Demonstrates tool gating and audit logging with OpenAI completions.
"""

import time
from typing import Any


# Mock OpenAI client for demo purposes
class MockOpenAIClient:
    def __init__(self):
        self.chat = self
        self.completions = self

    def create(self, **kwargs):
        """Mock OpenAI completion call."""
        tools = kwargs.get("tools", [])
        tool_names = [t["function"]["name"] for t in tools] if tools else []

        return {
            "choices": [
                {
                    "message": {
                        "content": f"I can use these tools: {', '.join(tool_names)} if tool_names else 'none'}",
                        "tool_calls": None,
                    }
                }
            ],
            "usage": {"total_tokens": 50},
        }


def lukhas_completion_with_gating(
    messages: list[dict[str, str]], params: dict[str, Any], client: MockOpenAIClient
) -> dict[str, Any]:
    """
    Complete with LUKHAS tool gating and audit logging.

    Args:
        messages: OpenAI chat messages
        params: LUKHAS modulation params with tool_allowlist and safety_mode
        client: OpenAI client instance

    Returns:
        Completion response with audit bundle ID
    """
    from lukhas.audit.store import audit_log_write
    from lukhas.openai.tooling import build_tools_from_allowlist

    # Extract tool allowlist and build gated tools
    tool_allowlist = params.get("tool_allowlist", [])
    openai_tools = build_tools_from_allowlist(tool_allowlist)

    # Create audit bundle before completion
    audit_id = f"A-{int(time.time(} * 1000}"

    # Call OpenAI with gated tools
    completion = client.create(
        model=params.get("model", "gpt-4"),
        messages=messages,
        temperature=params.get("temperature", 0.7),
        top_p=params.get("top_p", 0.9),
        max_tokens=params.get("max_output_tokens", 1024),
        tools=openai_tools if openai_tools else None,
        tool_choice="auto" if openai_tools else None,
    )

    # Log audit bundle with tool governance info
    audit_bundle = {
        "audit_id": audit_id,
        "signals": params.get("signals", {}),
        "params": {
            **params,
            "tool_allowlist": tool_allowlist,
            "tools_provided": len(openai_tools),
        },
        "guardian": {
            "verdict": "approved",
            "rules_fired": [],
            "tool_governance": "enforced",
        },
        "explanation": f"Tool allowlist: {tool_allowlist}; Safety: {params.get('safety_mode', 'balanced')}",
    }

    audit_log_write(audit_bundle)

    return {
        "completion": completion,
        "audit_id": audit_id,
        "tools_used": len(openai_tools),
    }


def demo_scenarios():
    """Demo different tool gating scenarios."""
    client = MockOpenAIClient()

    print("🎭 LUKHAS Tool Gating Demo")
    print("=" * 50)

    scenarios = [
        {
            "name": "Strict Mode - No Tools",
            "params": {
                "safety_mode": "strict",
                "tool_allowlist": [],
                "temperature": 0.3,
                "top_p": 0.8,
            },
        },
        {
            "name": "Balanced Mode - Safe Tools",
            "params": {
                "safety_mode": "balanced",
                "tool_allowlist": ["retrieval", "scheduler"],
                "temperature": 0.6,
                "top_p": 0.9,
            },
        },
        {
            "name": "Creative Mode - All Tools",
            "params": {
                "safety_mode": "creative",
                "tool_allowlist": ["retrieval", "browser", "scheduler", "code_exec"],
                "temperature": 0.8,
                "top_p": 0.95,
            },
        },
    ]

    messages = [{"role": "user", "content": "Help me research a topic"}]

    for scenario in scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        print(f"   Safety Mode: {scenario['params']['safety_mode']}")
        print(f"   Tools: {scenario['params']['tool_allowlist']}")

        result = lukhas_completion_with_gating(messages, scenario["params"], client)

        print(f"   ✅ Audit ID: {result['audit_id']}")
        print(f"   🛠️  Tools Provided: {result['tools_used']}")
        print(f"   🎯 View: http://127.0.0.1:8000/audit/view/{result['audit_id']}")


if __name__ == "__main__":
    demo_scenarios()
