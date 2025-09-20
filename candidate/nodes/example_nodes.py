# candidate/nodes/example_nodes.py
"""
Example cognitive nodes for testing the orchestration system.
"""

import asyncio
import time
from typing import Any, Mapping

from lukhas.core.interfaces import CognitiveNodeBase


class IntentNode(CognitiveNodeBase):
    """Node that processes user intent."""
    name = "intent"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        query = ctx.get("query", "")
        await asyncio.sleep(0.01)  # Simulate processing

        return {
            "intent_type": "question" if "?" in query else "statement",
            "keywords": query.split()[:3],
            "confidence": 0.8,
            "timestamp": time.time(),
            "ethics_risk": 0.1,
            "role_weight": 0.7
        }


class ThoughtNode(CognitiveNodeBase):
    """Node that generates thoughts based on intent."""
    name = "thought"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        intent_type = ctx.get("intent_type", "unknown")
        await asyncio.sleep(0.02)  # Simulate processing

        if intent_type == "question":
            thoughts = ["analyze", "research", "reason"]
        else:
            thoughts = ["acknowledge", "process", "respond"]

        return {
            "thoughts": thoughts,
            "reasoning": f"Generated thoughts for {intent_type}",
            "confidence": 0.9,
            "timestamp": time.time(),
            "ethics_risk": 0.05,
            "role_weight": 0.8
        }


class DecisionNode(CognitiveNodeBase):
    """Node that makes final decisions with ethics checking."""
    name = "decision"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        thoughts = ctx.get("thoughts", [])
        await asyncio.sleep(0.015)  # Simulate processing

        # Simple ethics check
        has_risky_content = any(word in str(ctx).lower() for word in ["hack", "attack", "harm"])
        ethics_risk = 0.9 if has_risky_content else 0.1

        return {
            "decision": "execute" if ethics_risk < 0.8 else "require_human",
            "action_plan": thoughts,
            "final_answer": f"Processed {len(thoughts)} thoughts",
            "confidence": 0.85,
            "timestamp": time.time(),
            "ethics_risk": ethics_risk,
            "role_weight": 0.9
        }


class SlowNode(CognitiveNodeBase):
    """Node that intentionally times out for testing."""
    name = "slow"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        await asyncio.sleep(1.0)  # Will timeout with 200ms default
        return {"status": "should_not_reach_here"}


class ErrorNode(CognitiveNodeBase):
    """Node that throws errors for testing."""
    name = "error"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        raise ValueError("Simulated node error")