"""Moderation wrapper applying symbolic compliance rules."""

from __future__ import annotations

import logging
from typing import Callable, List

log = logging.getLogger(__name__)


class SymbolicComplianceRules:
    """Simple symbolic compliance rule set."""

    def __init__(
        self,
        banned_phrases: List[str] | None = None,
        intensity_keywords: List[str] | None = None,
    ):
        self.banned_phrases = [p.lower() for p in (banned_phrases or [])]
        self.intensity_keywords = [
            k.lower()
            for k in (
                intensity_keywords
                or [
                    "angry",
                    "furious",
                    "rage",
                    "crying",
                    "screaming",
                ]
            )
        ]

    def is_emotionally_intense(self, prompt: str) -> bool:
        prompt_l = prompt.lower()
        return any(word in prompt_l for word in self.intensity_keywords)

    def is_compliant(self, prompt: str) -> bool:
        prompt_l = prompt.lower()
        return not any(phrase in prompt_l for phrase in self.banned_phrases)


class ModerationWrapper:
    """Wraps a responder to enforce symbolic alignment."""

    def __init__(self, rules: SymbolicComplianceRules):
        self.rules = rules

    def respond(self, prompt: str, responder: Callable[[str], str]) -> str:
        if self.rules.is_emotionally_intense(prompt):
            log.info("Emotionally intense prompt detected; running alignment check")
            if not self.rules.is_compliant(prompt):
                return "\u26a0\ufe0f Response withheld due to policy non-compliance."
        return responder(prompt)
