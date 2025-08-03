"""Type definitions for orchestration agents.

ΛTAG: orchestration_agent_types
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


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
    symbolic_state: Dict[str, Any]
    memory_context: Optional[Dict[str, Any]] = None
    glyphs: Optional[List[str]] = None


@dataclass
class AgentResponse:
    """Standard response from an orchestration agent."""

    success: bool
    result: Any
    metadata: Dict[str, Any]
    drift_delta: float = 0.0
