"""Symbolic delivery loop integration for NIAS candidate interface."""

from __future__ import annotations

import logging
from typing import Any, Iterable, List

try:
    from .nias_core import push_symbolic_message
except Exception as exc:  # pragma: no cover - fallback for missing backend
    push_symbolic_message = None  # type: ignore[assignment]
    logging.getLogger(__name__).warning(
        "nias_push_unavailable", error=str(exc)
    )

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


# ΛTAG: symbolic_delivery

def run_delivery_queue(
    queue: Iterable[dict[str, Any]],
    user_context: dict[str, Any],
) -> List[dict[str, Any]]:
    """Process symbolic messages through NIAS push pipeline.

    Args:
        queue: Iterable of symbolic message payloads.
        user_context: Context dict describing consent and emotional state.

    Returns:
        A list of decision dictionaries returned by ``push_symbolic_message``.
    """
    results: List[dict[str, Any]] = []

    if push_symbolic_message is None:
        logger.error("push_handler_missing")
        return results

    for message in queue:
        message_id = message.get("message_id", "unknown")
        try:
            decision = push_symbolic_message(message, user_context)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception(
                "delivery_push_failed",
                extra={"message_id": message_id, "error": str(exc)},
            )
            results.append({
                "status": "error",
                "reason": "push_exception",
                "error": str(exc),
                "message_id": message_id,
            })
            continue

        logger.info(
            "delivery_decision",
            extra={
                "message_id": message_id,
                "status": decision.get("status"),
                "reason": decision.get("reason"),
            },
        )
        results.append(decision)

    return results
