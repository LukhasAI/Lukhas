import json
import types
import uuid

import pytest

# SUT
from bridge.llm_wrappers.openai_modulated_service import run_modulated_completion

# Optional: read audit bundle for assertions (if available)
try:
    from lukhas.audit.store import audit_log_read
except Exception:
    audit_log_read = None


# ----------------------------
# Helpers: fake OpenAI client
# ----------------------------
def _completion(message_dict):
    """Return an object that mimics openai.ChatCompletion with .choices[0].message."""

    class Msg:
        def __init__(self, d):
            self._d = d

        def __getattr__(self, k):  # allow attribute-style access (message.tool_calls)
            if k == "tool_calls":
                return self._d.get("tool_calls")
            raise AttributeError

        def __getitem__(self, k):
            return self._d[k]

        @property
        def content(self):  # convenience
            return self._d.get("content")

        def get(self, k, default=None):
            return self._d.get(k, default)

    class Choice:
        def __init__(self, msg):
            self.message = msg

    class Completion:
        def __init__(self, msg):
            self.choices = [Choice(msg)]
            self.usage = types.SimpleNamespace()

    return Completion(Msg(message_dict))


class FakeChatCompletions:
    def __init__(self, scripted_responses):
        """
        scripted_responses: list of dicts; each is the message payload that the SDK would have returned.
        We also record inputs for inspection.
        """
        self.scripted = list(scripted_responses)
        self.calls = []  # each item is kwargs passed to create()

    def create(self, **kwargs):
        self.calls.append(kwargs)
        assert self.scripted, "No more scripted responses left for FakeChatCompletions"
        return _completion(self.scripted.pop(0))


class FakeOpenAIClient:
    def __init__(self, scripted_responses):
        self.chat = types.SimpleNamespace(
            completions=FakeChatCompletions(scripted_responses)
        )


# ----------------------------
# Monkeypatch executor
# ----------------------------
@pytest.fixture(autouse=True)
def patch_tool_executor(monkeypatch):
    # Return deterministic text for retrieval; other tools shouldn't run in tests below.
    def fake_execute_tool(tool_name, args_json):
        args = json.loads(args_json or "{}")
        if tool_name == "retrieve_knowledge":
            txt = f"[retrieval ok] k={args.get('k')} query={args.get('query')}"
            return txt
        raise RuntimeError(f"Unexpected tool execution: {tool_name}")

    class FakeToolExecutionError(Exception):
        def __init__(self, safe_message, duration_ms=None, args_summary=None):
            super().__init__(safe_message)
            self.safe_message = safe_message
            self.duration_ms = duration_ms
            self.args_summary = args_summary

    monkeypatch.setenv("PYTHONHASHSEED", "0")
    monkeypatch.setenv("NO_NETWORK", "1")

    monkeypatch.setattr(
        "bridge.llm_wrappers.tool_executor.execute_tool",
        lambda name, args: fake_execute_tool(name, args),
        raising=True,
    )
    monkeypatch.setattr(
        "bridge.llm_wrappers.tool_executor.ToolExecutionError",
        FakeToolExecutionError,
        raising=True,
    )
    return None


# ----------------------------
# Tests
# ----------------------------
def test_run_modulated_completion_no_tools():
    """
    Verifies the simple path: no tool_calls → final text returned.
    """
    # Script one completion that returns a plain assistant message (no tools)
    scripted = [{"content": "Final answer without tools."}]
    client = FakeOpenAIClient(scripted)

    out = run_modulated_completion(
        client=client,
        user_msg="Say hello without using any tools.",
        ctx_snips=[],
        endocrine_signals={},  # likely BALANCED, allowlist may include retrieval but model doesn't ask
        base_model="gpt-4o-mini",
        audit_id=f"A-UNIT-{uuid.uuid4()}",
        max_steps=3,
    )

    assert out.choices[0].message.content == "Final answer without tools."
    # Ensure we only called OpenAI once
    assert len(client.chat.completions.calls) == 1
    # Ensure tools param is present but may be empty/None (both acceptable)
    kwargs = client.chat.completions.calls[0]
    assert "tools" in kwargs


def test_run_modulated_completion_allowed_and_blocked_tools():
    """
    First response includes two tool calls:
    - allowed: retrieve_knowledge (should execute)
    - blocked: open_url (should be blocked and add a system note)
    Second response returns final content.
    """
    # Step 1 (from model): asks for two tools
    tool_calls_msg = {
        "tool_calls": [
            {
                "id": "call_1",
                "function": {
                    "name": "retrieve_knowledge",
                    "arguments": json.dumps({"k": 2, "query": "modulation policy"}),
                },
            },
            {
                "id": "call_2",
                "function": {
                    "name": "open_url",
                    "arguments": json.dumps({"url": "https://openai.com"}),
                },
            },
        ]
    }
    # Step 2 (after our executor runs): model replies with a normal message
    final_msg = {"content": "Answer after tools."}

    client = FakeOpenAIClient(scripted_responses=[tool_calls_msg, final_msg])

    audit_id = f"A-UNIT-{uuid.uuid4()}"
    out = run_modulated_completion(
        client=client,
        user_msg="Use retrieval and browsing if needed.",
        ctx_snips=[],
        endocrine_signals={"ambiguity": 0.6, "alignment_risk": 0.2},
        base_model="gpt-4o-mini",
        audit_id=audit_id,
        max_steps=4,
    )

    # Final answer should be from the second scripted response
    assert out.choices[0].message.content == "Answer after tools."

    # We should have invoked OpenAI twice (before and after tool execution)
    assert len(client.chat.completions.calls) == 2

    # Inspect the messages for the second call: it should contain
    # - a 'tool' role message with the retrieval result
    # - a 'system' note about the blocked 'open_url'
    second_call_msgs = client.chat.completions.calls[1]["messages"]
    tool_msgs = [m for m in second_call_msgs if m.get("role") == "tool"]
    sys_msgs = [
        m
        for m in second_call_msgs
        if m.get("role") == "system" and "blocked" in m.get("content", "").lower()
    ]

    assert any(
        tm.get("name") == "retrieve_knowledge" for tm in tool_msgs
    ), "Expected retrieval tool result appended"
    assert any(
        "blocked" in sm.get("content", "").lower() for sm in sys_msgs
    ), "Expected system note about blocked tool"

    # Optional: confirm audit bundle exists (if the store is available)
    if audit_log_read:
        bundle = audit_log_read(audit_id)
        assert bundle is not None
        assert "params" in bundle
        # The allowlist is logged; by default, browser should not be allowed under
        # stricter modes
        assert "tool_allowlist" in bundle["params"]
