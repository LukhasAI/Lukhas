from dataclasses import dataclass
from typing import Any, Optional
import streamlit as st


@dataclass(frozen=True)
class AgentOpinion:
    agent_id: str
    value: Any
    confidence: float  # 0..1
    rationale: Optional[str] = None


@dataclass(frozen=True)
class ConsensusResult:
    key: str
    decided_value: Any
    votes_for: int
    votes_total: int
    confidence: float  # 0..1
    metadata: dict[str, Any]
    version: int = 1


class ColonyConsensus:
    """Thin interface for colony consensus (implemented elsewhere)."""

    def compute(self, key: str, opinions: list[AgentOpinion]) -> ConsensusResult:
        raise NotImplementedError
