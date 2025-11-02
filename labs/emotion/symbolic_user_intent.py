"""Symbolic representation utilities for user intents.

This module defines a ``UserIntent`` dataclass and an ``IntentEncoder`` class
that provides simple text-based intent inference.

# ΛTAG: codex, intent
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field


@dataclass
class UserIntent:
    """Represents a parsed user intent."""

    intent_type: str
    confidence: float = 0.0
    entities: dict[str, str] = field(default_factory=dict)
    raw_input: str | None = None
    sid: str = field(default_factory=lambda: uuid.uuid4().hex)
    drift_score: float = 0.0
    affect_delta: float = 0.0


class IntentEncoder:
    """Simple rule-based intent encoder."""

    QUESTION_RE = re.compile(r"\b(what|who|when|where|why|how)\b", re.I)
    COMMAND_RE = re.compile(r"\b(do|create|make|build|execute)\b", re.I)

    def encode(self, text: str) -> UserIntent:
        """Infer intent from ``text`` and return a :class:`UserIntent`."""
        text_lower = text.lower()
        if self.QUESTION_RE.search(text_lower):
            intent = "query"
            confidence = 0.8
        elif self.COMMAND_RE.search(text_lower):
            intent = "task"
            confidence = 0.8
        else:
            intent = "dialogue"
            confidence = 0.6
        return UserIntent(intent_type=intent, confidence=confidence, raw_input=text)
