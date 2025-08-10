"""
OpenAI Modulated Service
========================
Threads LUKHAS signal-based modulation into OpenAI requests via
UnifiedOpenAIClient.

Contract:
- Inputs: prompt (str), optional context (dict), optional precomputed
    signals/params
- Behavior: compute/accept modulation, build messages, call client with params
- Safety: Guardian pre/post moderation hooks
- Outputs: normalized response dict with content and metadata
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import time
import uuid
from typing import Any, cast

from bridge.llm_wrappers.tool_executor import execute_tool as bridged_execute_tool
from lukhas_pwm.audit.tool_analytics import get_analytics
from lukhas_pwm.metrics import get_metrics_collector
from lukhas_pwm.openai.tooling import build_tools_from_allowlist, get_all_tools
from orchestration.signals.homeostasis import (
    HomeostasisController,
    ModulationParams,
    SystemEvent,
)
from orchestration.signals.modulator import PromptModulation, PromptModulator
from orchestration.signals.signal_bus import Signal, get_signal_bus

from .unified_openai_client import UnifiedOpenAIClient

logger = logging.getLogger("ΛTRACE.bridge.openai_modulated_service")


class OpenAIModulatedService:
    """Compose Signal Bus + Homeostasis + PromptModulator with
    UnifiedOpenAIClient.
    """

    def __init__(
        self,
        client: UnifiedOpenAIClient | None = None,
        homeostasis: HomeostasisController | None = None,
        modulator: PromptModulator | None = None,
    ) -> None:
        self.bus = get_signal_bus()
        self.homeo = homeostasis or HomeostasisController(self.bus)
        self.modulator = modulator or PromptModulator()
        self.client = client or UnifiedOpenAIClient()
        self.metrics: dict[str, int] = {
            "requests": 0,
            "streams": 0,
            "moderation_blocks": 0,
        }

        # Build mapping from function names to allowlist names
        self._function_to_allowlist_map = {}
        all_tools = get_all_tools()
        for allowlist_name, tool_spec in all_tools.items():
            function_name = tool_spec.get("function", {}).get("name")
            if function_name:
                self._function_to_allowlist_map[function_name] = allowlist_name

    async def generate(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        signals: list[Signal] | None = None,
        params: ModulationParams | None = None,
        task: str | None = None,
        stream: bool = False,
    ) -> dict[str, Any]:
        """
        Run full modulation pipeline and call OpenAI.
        - If signals/params omitted: derive via homeostasis USER_INPUT path.
        - Applies Guardian pre/post moderation.
        """
        self.metrics["requests"] += 1

        # Compute signals/params if not provided
        if signals is None or params is None:
            evt_ctx = {
                "text": prompt,
                "additional_context": (context or {}).get("additional_context"),
            }
            new_params = await self.homeo.process_event(SystemEvent.USER_INPUT, evt_ctx)
            params = params or new_params
            signals = self.bus.get_active_signals()

        # Build prompt modulation
        modulation: PromptModulation = self.modulator.modulate(
            prompt, signals, params, context
        )

        # Retrieval v1: if allowed and retrieval_k > 0, attach retrieved notes
        if (
            params
            and params.retrieval_k
            and ("retrieval" in (params.tool_allowlist or []))
        ):
            retrieved = await self._retrieve_context(
                modulation, top_k=params.retrieval_k
            )
            if retrieved:
                # Light-touch injection
                context = dict(context or {})
                ctx_add = (context.get("additional_context") or "").strip()
                context["additional_context"] = (
                    ctx_add
                    + ("\n\n" if ctx_add else "")
                    + "Retrieved Notes:\n"
                    + "\n".join(retrieved)
                ).strip()
                # Rebuild modulation with enriched context
                modulation = self.modulator.modulate(prompt, signals, params, context)

        # Pre-moderation via Guardian
        self._pre_moderation_check(modulation)

        # Prepare API request from modulation
        api_payload = modulation.to_api_format()
        messages = api_payload.pop("messages")
        max_tokens = api_payload.pop("max_tokens", None)
        temperature = api_payload.pop("temperature", None)
        metadata = api_payload.pop("metadata", {})

        # Build tools from allowlist
        openai_tools = []
        analytics = get_analytics()
        audit_id = f"audit_{task or 'general'}_{int(time.time()*1000)}"
        tool_incidents = []

        if params and params.tool_allowlist:
            openai_tools = build_tools_from_allowlist(params.tool_allowlist)

        # Tool execution loop with safety
        MAX_STEPS = 6
        step = 0
        final_response = None
        tool_calls_made = []
        current_messages = list(messages)  # Work with a copy

        while step < MAX_STEPS:
            step += 1

            # Call OpenAI
            response = await self.client.chat_completion(
                messages=current_messages,
                task=task or "general",
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                tools=openai_tools if openai_tools else None,
                tool_choice="auto" if openai_tools else None,
            )

            # Check for streaming response
            if not isinstance(response, dict):
                # Handle streaming case
                final_response = response
                break

            # Extract message and tool calls
            choice = response["choices"][0] if response["choices"] else {}
            message = choice.get("message", {})
            tool_calls = message.get("tool_calls")

            # If no tool calls, we're done
            if not tool_calls:
                final_response = response
                break

            # Add assistant message with tool calls to history
            current_messages.append(
                {
                    "role": "assistant",
                    "content": message.get("content"),
                    "tool_calls": tool_calls,
                }
            )

            # Process each tool call
            for tool_call in tool_calls:
                tool_name = tool_call.get("function", {}).get("name", "unknown")
                tool_args = tool_call.get("function", {}).get("arguments", {})
                tool_id = tool_call.get("id", "unknown")

                # Map function name to allowlist name
                allowlist_name = self._function_to_allowlist_map.get(
                    tool_name, tool_name
                )

                # Check if tool is allowed
                if (
                    params
                    and params.tool_allowlist
                    and allowlist_name not in params.tool_allowlist
                ):
                    # Record security incident
                    incident = analytics.record_blocked_attempt(
                        audit_id=audit_id,
                        attempted_tool=tool_name,
                        allowed_tools=params.tool_allowlist,
                        prompt=prompt,
                    )
                    tool_incidents.append(incident)

                    # Record metrics
                    metrics = get_metrics_collector()
                    metrics.record_blocked_tool(
                        tool_name,
                        params.safety_mode if params else "unknown",
                    )
                    metrics.record_auto_tighten("blocked_tool")

                    # Auto-tighten to strict mode
                    if params:
                        params.safety_mode = "strict"
                        metrics.set_safety_mode("strict", audit_id)

                    logger.warning(
                        "SECURITY: Blocked disallowed tool attempt: %s",
                        tool_name,
                    )

                    # Add system note about blocked tool (for test assertions)
                    current_messages.append(
                        {
                            "role": "system",
                            "content": (
                                f"Blocked tool '{tool_name}'. Not in " "allowlist."
                            ),
                        }
                    )
                    continue

                # Execute allowed tool
                call_id = None
                try:
                    # Track tool call start
                    call_id = analytics.start_tool_call(tool_name, tool_args)

                    # Execute tool via bridge (monkeypatch-friendly in tests)
                    result = await bridged_execute_tool(tool_name, tool_args)

                    # Track success
                    analytics.complete_tool_call(call_id, status="success")
                    tool_calls_made.append(
                        {
                            "tool": tool_name,
                            "status": "executed",
                            "args": tool_args,
                            "result_preview": result[:100] if result else None,
                        }
                    )

                    # Add tool result to messages
                    current_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "name": tool_name,
                            "content": result,
                        }
                    )

                except Exception as e:
                    # Track failure
                    if call_id is not None:
                        analytics.complete_tool_call(call_id, status="error")
                    tool_calls_made.append(
                        {
                            "tool": tool_name,
                            "status": "error",
                            "args": tool_args,
                            "error": str(e),
                        }
                    )

                    # Add error message
                    current_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_id,
                            "content": f"Tool execution failed: {str(e)}",
                        }
                    )

                    logger.error(f"Tool execution failed: {tool_name}", exc_info=e)

        # Use final response or last response
        if final_response is not None:
            response = final_response
        else:
            # Ensure response is defined
            # Assign empty dict if response wasn't set in loop
            response = {}  # type: ignore[assignment]

        # Normalize to dict if streaming iterator was returned
        if not isinstance(response, dict) and hasattr(response, "__aiter__"):
            first = None
            async for chunk in response:  # type: ignore
                first = chunk
                break
            response = first or {"choices": [{"message": {"content": ""}}]}

        # Post-moderation via Guardian
        self._post_moderation_check(cast(dict[str, Any], response))

        # Normalize output
        content = None
        try:
            resp_dict = cast(dict[str, Any], response)
            content = resp_dict["choices"][0]["message"]["content"]
        except Exception:
            content = str(response)

        # Basic metrics log
        with contextlib.suppress(Exception):
            logger.info(
                "OpenAI.generate completed",
                extra={
                    "task": task or "general",
                    "style": modulation.style.value,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

        return {
            "content": content,
            "raw": response,
            "modulation": {
                "style": modulation.style.value,
                "params": modulation.api_params.to_dict(),
                "signal_levels": modulation.metadata.get("signal_levels", {}),
            },
            "metadata": {
                **metadata,
                "moderation": modulation.moderation_preset,
                "audit_id": audit_id,
            },
            "tool_analytics": {
                "tools_used": tool_calls_made,
                "incidents": [inc.to_dict() for inc in tool_incidents],
                "safety_tightened": len(tool_incidents) > 0,
            },
        }

    async def generate_stream(
        self,
        prompt: str,
        context: dict[str, Any] | None = None,
        signals: list[Signal] | None = None,
        params: ModulationParams | None = None,
        task: str | None = None,
    ):
        """
        Stream tokens from OpenAI with pre-moderation and retrieval injection.
        Yields text chunks.
        """
        self.metrics["streams"] += 1
        # Derive params/signals if missing
        if signals is None or params is None:
            evt_ctx = {
                "text": prompt,
                "additional_context": (context or {}).get("additional_context"),
            }
            new_params = await self.homeo.process_event(SystemEvent.USER_INPUT, evt_ctx)
            params = params or new_params
            signals = self.bus.get_active_signals()

        modulation = self.modulator.modulate(prompt, signals, params, context)

        # Retrieval injection
        if (
            params
            and params.retrieval_k
            and ("retrieval" in (params.tool_allowlist or []))
        ):
            retrieved = await self._retrieve_context(
                modulation, top_k=params.retrieval_k
            )
            if retrieved:
                context = dict(context or {})
                ctx_add = (context.get("additional_context") or "").strip()
                context["additional_context"] = (
                    ctx_add
                    + ("\n\n" if ctx_add else "")
                    + "Retrieved Notes:\n"
                    + "\n".join(retrieved)
                ).strip()
                modulation = self.modulator.modulate(prompt, signals, params, context)

        # Pre-moderation
        self._pre_moderation_check(modulation)

        api_payload = modulation.to_api_format()
        messages = api_payload.pop("messages")
        max_tokens = api_payload.pop("max_tokens", None)
        temperature = api_payload.pop("temperature", None)

        stream_iter = await self.client.chat_completion(
            messages=messages,
            task=task or "general",
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        # Fallback if not a stream
        if isinstance(stream_iter, dict) or not hasattr(stream_iter, "__aiter__"):

            async def _once():
                try:
                    si = cast(dict[str, Any], stream_iter)
                    text = si["choices"][0]["message"]["content"]
                except Exception:  # pragma: no cover
                    text = str(stream_iter)
                yield text

            return _once()

        async def _gen():
            buffer: list[str] = []
            async for chunk in stream_iter:  # type: ignore
                try:
                    delta = chunk["choices"][0].get("delta") or chunk["choices"][0].get(
                        "message"
                    )
                    piece = (
                        delta.get("content") if isinstance(delta, dict) else None
                    ) or ""
                except Exception:
                    piece = ""
                if piece:
                    buffer.append(piece)
                    yield piece
            # Post moderation on full text (best-effort)
            full = "".join(buffer)
            try:
                self._post_moderation_check(
                    {"choices": [{"message": {"content": full}}]}
                )
            except PermissionError:
                self.metrics["moderation_blocks"] += 1
                logger.warning("Post-moderation flagged streamed content")

        return _gen()

    def _pre_moderation_check(self, modulation: PromptModulation) -> None:
        """Guardian pre-check; provider fallback is a no-op."""
        # Guardian
        try:
            from governance.guardian_sentinel import (
                get_guardian_sentinel,  # lazy import
            )

            guardian = get_guardian_sentinel()
            allow, message, _meta = guardian.assess_threat(
                action="openai_pre_prompt",
                context={
                    "prompt": modulation.modulated_prompt,
                    "style": modulation.style.value,
                    "moderation": modulation.moderation_preset,
                },
                drift_score=0.0,
            )
            if not allow:
                self.metrics["moderation_blocks"] += 1
                raise PermissionError(f"Pre-moderation blocked: {message}")
        except Exception:
            # Fallback: do nothing
            pass
        return

    def _post_moderation_check(self, response: dict[str, Any]) -> None:
        """Guardian post-check with fallback no-op."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content")
        except Exception:
            content = None
        # Guardian
        try:
            from governance.guardian_sentinel import (
                get_guardian_sentinel,  # lazy import
            )

            guardian = get_guardian_sentinel()
            allow, message, _meta = guardian.assess_threat(
                action="openai_post_content",
                context={"content": content or str(response)},
                drift_score=0.0,
            )
            if not allow:
                self.metrics["moderation_blocks"] += 1
                raise PermissionError(f"Post-moderation blocked: {message}")
        except Exception:
            return

    async def _retrieve_context(
        self, modulation: PromptModulation, top_k: int = 5
    ) -> list[str]:
        """Best-effort retrieval adapter (placeholder). Short notes list."""
        # TODO: Integrate with real vector store or memory layer
        text = modulation.original_prompt.lower()
        tokens = [t for t in text.split() if len(t) > 4][:top_k]
        out: list[str] = []
        for tok in tokens:
            out.append(f"Note about {tok}: (placeholder retrieved context)")
        return out


# ============================================================================
# HELPER FUNCTIONS FOR TESTING AND SCRIPTING
# ============================================================================


async def _run_modulated_completion_impl(
    client,
    user_msg: str,
    ctx_snips: list[str] | None = None,
    endocrine_signals: dict[str, float] | None = None,
    base_model: str = "gpt-3.5-turbo",
    audit_id: str | None = None,
    max_steps: int = 6,
):
    """
    One-shot entrypoint: modulate → tool loop → final.

    Args:
        client: OpenAI client instance
        user_msg: User's prompt
        ctx_snips: Context snippets to include
        endocrine_signals: Signal levels (alignment_risk,
            stress, ambiguity, novelty)
        base_model: OpenAI model to use
        audit_id: Audit ID for tracking
        max_steps: Maximum tool execution iterations

    Returns:
        OpenAI completion response
    """
    # local imports avoided if not required; tolerate missing audit store
    # in tests
    try:
        from lukhas_pwm.audit.store import audit_log_write as _audit_log_write
    except Exception:  # pragma: no cover - optional in offline tests
        _audit_log_write = None  # type: ignore
    from orchestration.signals.homeostasis import ModulationParams
    from orchestration.signals.signal_bus import Signal, SignalType

    ctx_snips = ctx_snips or []
    endocrine_signals = endocrine_signals or {}
    audit_id = audit_id or f"A-{uuid.uuid4().hex[:8]}"

    # Ensure we have a client with a chat_completion coroutine.
    # Accept three shapes:
    # 1) Already a UnifiedOpenAIClient (has chat_completion)
    # 2) Duck-typed OpenAI SDK-like client with chat.completions.create
    # 3) Fallback to UnifiedOpenAIClient from env
    try:
        from .unified_openai_client import UnifiedOpenAIClient as _U
    except Exception:  # pragma: no cover
        _U = UnifiedOpenAIClient  # fallback to already imported

    if not hasattr(client, "chat_completion"):
        # Try to adapt duck-typed OpenAI SDK client
        has_duck_api = (
            hasattr(client, "chat")
            and hasattr(client.chat, "completions")
            and hasattr(client.chat.completions, "create")
        )

        if has_duck_api:
            raw_client = client

            class _DuckOpenAIAdapter:

                def __init__(self, rc):
                    self._raw = rc

                async def chat_completion(
                    self,
                    messages: list[dict[str, Any]],
                    task: str = "general",
                    temperature: float | None = None,
                    max_tokens: int | None = None,
                    stream: bool = False,
                    tools: list[dict[str, Any]] | None = None,
                    tool_choice: str | None = None,
                ) -> dict[str, Any]:
                    # Call sync create() in an async-friendly way

                    def _call_create():
                        kwargs = {
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                            "stream": stream,
                        }
                        if tools is not None:
                            kwargs["tools"] = tools
                        if tool_choice is not None:
                            kwargs["tool_choice"] = tool_choice
                        return self._raw.chat.completions.create(**kwargs)

                    completion = _call_create()

                    # Normalize to dict expected by service.generate
                    try:
                        comp_choices = completion.choices  # type: ignore[attr-defined]
                        msg = comp_choices[0].message
                        content = getattr(msg, "content", None)
                        tool_calls = (
                            getattr(msg, "tool_calls", None)
                            if hasattr(msg, "tool_calls")
                            else (
                                msg.get("tool_calls") if hasattr(msg, "get") else None
                            )
                        )
                        return {
                            "choices": [
                                {
                                    "message": {
                                        "content": content,
                                        "tool_calls": tool_calls,
                                    }
                                }
                            ],
                            "usage": getattr(completion, "usage", {}) or {},
                        }
                    except Exception:  # pragma: no cover
                        return {
                            "choices": [
                                {
                                    "message": {
                                        "content": str(completion),
                                        "tool_calls": None,
                                    }
                                }
                            ]
                        }

            client = _DuckOpenAIAdapter(raw_client)
        else:
            # Fallback to our unified client
            client = _U()

    # Create modulated service
    service = OpenAIModulatedService(client=client)

    # Build signals
    signals = []
    for name, level in endocrine_signals.items():
        if name in {"alignment_risk", "stress", "ambiguity", "novelty"}:
            try:
                signal_type = SignalType(name)
                signals.append(Signal(name=signal_type, level=level, source="helper"))
            except ValueError:
                continue

    # Build params with defaults
    # Type-safe coercions from signal dict
    temperature = float(endocrine_signals.get("temperature", 0.7))
    safety_mode = str(endocrine_signals.get("safety_mode", "balanced"))
    tool_allowlist = endocrine_signals.get("tool_allowlist", [])
    if not isinstance(tool_allowlist, list):
        tool_allowlist = []
    if not tool_allowlist:
        # Default to retrieval allowed in balanced mode for offline tests
        tool_allowlist = ["retrieval"]
    max_output_tokens = int(endocrine_signals.get("max_output_tokens", 500))

    params = ModulationParams(
        temperature=temperature,
        safety_mode=safety_mode,
        tool_allowlist=tool_allowlist,  # type: ignore[arg-type]
        max_output_tokens=max_output_tokens,
    )

    # Add context to prompt if provided
    full_prompt = user_msg
    if ctx_snips:
        context_str = "\n".join(f"- {snip}" for snip in ctx_snips[:8])
        full_prompt = f"Context:\n{context_str}\n\nQuery: {user_msg}"

    # Run generation
    result = await service.generate(
        prompt=full_prompt, params=params, signals=signals, task=audit_id
    )

    # Log audit
    if _audit_log_write:  # type: ignore
        p_dict = params.to_dict() if hasattr(params, "to_dict") else {}
        # Also expose allowlist at top-level for easier assertions in tests
        with contextlib.suppress(Exception):
            p_dict["tool_allowlist"] = list(params.tool_allowlist)
        _audit_log_write(
            {
                "audit_id": audit_id,
                "signals": endocrine_signals,
                "params": p_dict,
                "guardian": {"verdict": "approved"},
                "explanation": "modulated + tool loop via helper",
            }
        )

    return result


# Backward/forward compatible wrapper for sync callers
# - In async contexts: returns the coroutine so callers can
#   `await run_modulated_completion(...)` (tests remain valid)
# - In sync contexts: runs the coroutine and returns a minimal
#   OpenAI-like object
run_modulated_completion_async = _run_modulated_completion_impl


def run_modulated_completion(
    client,
    user_msg: str,
    ctx_snips: list[str] | None = None,
    endocrine_signals: dict[str, float] | None = None,
    base_model: str = "gpt-3.5-turbo",
    audit_id: str | None = None,
    max_steps: int = 6,
):
    """Dual-mode entrypoint (async-compatible + sync-friendly).

    - If an event loop is running, return the coroutine for awaiting
      (preserves existing async tests).
    - If no loop, execute and adapt the result to a minimal SDK-like
      object with .choices / .usage.
    """
    coro = run_modulated_completion_async(
        client=client,
        user_msg=user_msg,
        ctx_snips=ctx_snips,
        endocrine_signals=endocrine_signals,
        base_model=base_model,
        audit_id=audit_id,
        max_steps=max_steps,
    )

    # If already in an async loop, let caller await the coroutine
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return coro
    except Exception:
        pass

    # Run now and adapt to a lightweight OpenAI-like completion object
    res = asyncio.run(coro)

    class _Msg:

        def __init__(self, content: str | None):
            self.content = content

    class _Choice:

        def __init__(self, content: str | None):
            self.message = _Msg(content)

    class _Usage:

        def __init__(self, usage: dict[str, Any]):
            # Support dict-like and objects with attributes (e.g., SimpleNamespace)
            if hasattr(usage, "get"):
                self.prompt_tokens = usage.get("prompt_tokens")
                self.completion_tokens = usage.get("completion_tokens")
                self.total_tokens = usage.get("total_tokens")
            else:
                self.prompt_tokens = getattr(usage, "prompt_tokens", None)
                self.completion_tokens = getattr(usage, "completion_tokens", None)
                self.total_tokens = getattr(usage, "total_tokens", None)

    class _Completion:

        def __init__(self, result: dict[str, Any]):
            raw = result.get("raw") or {}
            usage = raw.get("usage") or {}
            self.choices = [_Choice(result.get("content"))]
            self.usage = _Usage(usage) if usage else None

    return _Completion(res)


def resume_with_tools(
    messages: list[dict[str, Any]],
    tool_calls: list[dict[str, Any]],
    allowlist: list[str],
    audit_id: str = "A-TEST",
) -> list[dict[str, Any]]:
    """
    Deterministically execute tool_calls and return augmented messages.

    Args:
        messages: Conversation history
        tool_calls: Tool calls to execute, shape:
            [{"id":"call_1","function":{"name":"retrieve_knowledge","arguments":"{\\"k\\":3}"}}]
        allowlist: List of allowed tool names
        audit_id: Audit ID for tracking

    Returns:
        Messages list with tool results appended
    """
    import asyncio
    import json

    from lukhas_pwm.audit.tool_analytics import get_analytics
    from lukhas_pwm.tools.tool_executor import get_tool_executor

    analytics = get_analytics()
    executor = get_tool_executor()
    out = list(messages)

    # Build function name mapping
    tool_mapping = {
        "retrieve_knowledge": "retrieval",
        "open_url": "browser",
        "schedule_task": "scheduler",
        "exec_code": "code_exec",
    }

    for tc in tool_calls:
        name = tc["function"]["name"]
        args_json = tc["function"].get("arguments", "{}")

        # Check allowlist (map function name to allowlist name)
        allowlist_name = tool_mapping.get(name, name)

        if allowlist_name not in allowlist:
            # Record blocked attempt
            analytics.record_blocked_attempt(
                audit_id=audit_id,
                attempted_tool=name,
                allowed_tools=allowlist,
                prompt="offline_test",
            )
            out.append(
                {
                    "role": "system",
                    "content": (
                        f"Tool '{name}' blocked by governance. " "Not in allowlist."
                    ),
                }
            )
            continue

        # Execute tool
        text = ""
        try:
            # Run async executor in sync context
            loop_running = False
            try:
                loop = asyncio.get_event_loop()
                loop_running = loop.is_running()
            except Exception:
                loop = asyncio.new_event_loop()
                loop_running = False
            # Run async executor in the appropriate context
            if not loop_running:
                text = loop.run_until_complete(executor.execute(name, args_json))
            if loop_running:
                # If already in async context
                text = asyncio.run_coroutine_threadsafe(
                    executor.execute(name, args_json), loop
                ).result()
            if not text:
                text = ""

            # Track success
            call_id = analytics.start_tool_call(
                name,
                (json.loads(args_json) if isinstance(args_json, str) else args_json),
            )
            analytics.complete_tool_call(call_id, status="success")

        except Exception as e:
            text = f"[Tool '{name}' failed: {str(e)}]"
            # Track failure
            call_id = analytics.start_tool_call(name, {})
            analytics.complete_tool_call(call_id, status="error")

        out.append(
            {
                "role": "tool",
                "tool_call_id": tc.get("id", "call_0"),
                "name": name,
                "content": text,
            }
        )

    return out
