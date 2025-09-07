from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import streamlit as st


@dataclass
class PolicyEngine:
    """
    Minimal constitutional binding placeholder.
    Evaluates trigger pre/post and constitution labels.
    """

    constitution_rules: Sequence[str] | None = None

    def evaluate_trigger(self, trigger: Mapping[str, object]) -> bool:
        # TODO: Bind to real constitutional engine. For now, accept unless explicitly forbidden.
        labels = trigger.get("constitution") if isinstance(trigger, Mapping) else None
        return not (isinstance(labels, list) and any(lbl == "forbidden" for lbl in labels))
