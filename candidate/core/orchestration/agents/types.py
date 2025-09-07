"""Type definitions for orchestration agents.

ΛTAG: orchestration_agent_types
"""
import streamlit as st

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class AgentCapability(Enum):
    """Capabilities that an orchestration agent can provide."""

    SYMBOLIC_REASONING = "symbolic_reasoning"
    DREAM_SYNTHESIS = "dream_synthesis"
    ETHICAL_EVALUATION = "ethical_evaluation"
    MEMORY_MANAGEMENT = "memory_management"
    ORCHESTRATION = "orchestration"


@dataclass
class AgentContext:
    """Context passed to orchestration agents."""

    task_id: str
    symbolic_state: dict[str, Any]
    memory_context: Optional[dict[str, Any]] = None
    glyphs: Optional[list[str]] = None


@dataclass
class AgentResponse:
    """Standard response from an orchestration agent."""

    success: bool
    result: Any
    metadata: dict[str, Any]
    drift_delta: float = 0.0
