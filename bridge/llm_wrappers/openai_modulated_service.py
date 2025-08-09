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
import logging
from typing import Any, Dict, List, Optional, cast

from .unified_openai_client import UnifiedOpenAIClient
from orchestration.signals.signal_bus import get_signal_bus, Signal
from orchestration.signals.homeostasis import (
    HomeostasisController,
    ModulationParams,
    SystemEvent,
)
from orchestration.signals.modulator import PromptModulator, PromptModulation
from lukhas_pwm.openai.tooling import build_tools_from_allowlist

logger = logging.getLogger("ΛTRACE.bridge.openai_modulated_service")


class OpenAIModulatedService:
    """Compose Signal Bus + Homeostasis + PromptModulator with UnifiedOpenAIClient."""

    def __init__(
        self,
        client: Optional[UnifiedOpenAIClient] = None,
        homeostasis: Optional[HomeostasisController] = None,
        modulator: Optional[PromptModulator] = None,
    ) -> None:
        self.bus = get_signal_bus()
        self.homeo = homeostasis or HomeostasisController(self.bus)
        self.modulator = modulator or PromptModulator()
        self.client = client or UnifiedOpenAIClient()
        self.metrics: Dict[str, int] = {
            "requests": 0,
            "streams": 0,
            "moderation_blocks": 0,
        }

    async def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        signals: Optional[List[Signal]] = None,
        params: Optional[ModulationParams] = None,
        task: Optional[str] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
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
            new_params = await self.homeo.process_event(
                SystemEvent.USER_INPUT, evt_ctx
            )
            params = params or new_params
            signals = self.bus.get_active_signals()

        # Build prompt modulation
        modulation: PromptModulation = self.modulator.modulate(
            prompt, signals, params, context
        )

        # Retrieval v1: if allowed and retrieval_k > 0, attach retrieved notes
        if params and params.retrieval_k and (
            "retrieval" in (params.tool_allowlist or [])
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
                modulation = self.modulator.modulate(
                    prompt, signals, params, context
                )

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
        if params and params.tool_allowlist:
            openai_tools = build_tools_from_allowlist(params.tool_allowlist)

        # Call OpenAI with tools
        response = await self.client.chat_completion(
            messages=messages,
            task=task or "general",
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            tools=openai_tools if openai_tools else None,
            tool_choice="auto" if openai_tools else None,
        )

        # Normalize to dict if streaming iterator was returned
        if not isinstance(response, dict) and hasattr(response, "__aiter__"):
            first = None
            async for chunk in response:  # type: ignore
                first = chunk
                break
            response = first or {"choices": [{"message": {"content": ""}}]}

        # Post-moderation via Guardian
        self._post_moderation_check(cast(Dict[str, Any], response))

        # Normalize output
        content = None
        try:
            resp_dict = cast(Dict[str, Any], response)
            content = resp_dict["choices"][0]["message"]["content"]
        except Exception:
            content = str(response)

        # Basic metrics log
        try:
            logger.info(
                "OpenAI.generate completed",
                extra={
                    "task": task or "general",
                    "style": modulation.style.value,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
        except Exception:
            pass

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
            },
        }

    async def generate_stream(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        signals: Optional[List[Signal]] = None,
        params: Optional[ModulationParams] = None,
        task: Optional[str] = None,
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
            new_params = await self.homeo.process_event(
                SystemEvent.USER_INPUT, evt_ctx
            )
            params = params or new_params
            signals = self.bus.get_active_signals()

        modulation = self.modulator.modulate(prompt, signals, params, context)

        # Retrieval injection
        if params and params.retrieval_k and (
            "retrieval" in (params.tool_allowlist or [])
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
                modulation = self.modulator.modulate(
                    prompt, signals, params, context
                )

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
                    text = stream_iter["choices"][0]["message"]["content"]  # type: ignore
                except Exception:  # pragma: no cover
                    text = str(stream_iter)
                yield text
            return _once()

        async def _gen():
            buffer: List[str] = []
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
        """Run Guardian moderation if available; fall back to OpenAI moderation if configured."""
        # Guardian
        try:
            from governance.guardian_sentinel import get_guardian_sentinel  # lazy import
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
            return
        except Exception:
            pass
        # OpenAI moderation fallback (best-effort, sync path not available -> skip here)
        return

    def _post_moderation_check(self, response: Dict[str, Any]) -> None:
        """Guardian post-check with fallback no-op."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content")
        except Exception:
            content = None
        # Guardian
        try:
            from governance.guardian_sentinel import get_guardian_sentinel  # lazy import
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

    async def _retrieve_context(self, modulation: PromptModulation, top_k: int = 5) -> List[str]:
        """Best-effort retrieval adapter (placeholder). Returns list of short notes."""
        # TODO: Integrate with real vector store or memory layer
        text = modulation.original_prompt.lower()
        tokens = [t for t in text.split() if len(t) > 4][:top_k]
        return [f"Note about {tok}: (placeholder retrieved context)" for tok in tokens]
