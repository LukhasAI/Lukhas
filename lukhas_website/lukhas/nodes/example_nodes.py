# candidate/nodes/example_nodes.py
"""
Example cognitive nodes for testing the orchestration system.
"""

import asyncio
import time
from collections.abc import Mapping
from typing import Any

from core.interfaces import CognitiveNodeBase


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
    """Node that generates sophisticated thoughts based on intent and context."""
    name = "thought"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        query = ctx.get("query", "")
        intent_type = ctx.get("intent_type", "unknown")
        keywords = ctx.get("keywords", [])

        await asyncio.sleep(0.02)  # Simulate processing

        # Enhanced reasoning based on query analysis
        reasoning_chain = []
        thoughts = []

        if intent_type == "question":
            # Analyze question type and complexity
            if any(word in query.lower() for word in ["how", "why", "what", "where", "when"]):
                reasoning_chain.append("Identified explanatory question requiring factual analysis")
                thoughts.extend(["research_facts", "analyze_context", "synthesize_answer"])

            if any(word in query.lower() for word in ["should", "could", "would", "might"]):
                reasoning_chain.append("Detected modal question requiring careful consideration")
                thoughts.extend(["evaluate_options", "consider_implications", "weigh_consequences"])

            # Math/calculation detection
            if any(char in query for char in "+-*/=") or any(word in query.lower() for word in ["calculate", "compute", "add", "subtract"]):
                reasoning_chain.append("Mathematical operation detected")
                thoughts.extend(["parse_mathematical_expression", "perform_calculation", "verify_result"])

        else:
            # Statement processing
            reasoning_chain.append("Processing statement for understanding and response")
            thoughts.extend(["parse_statement", "extract_meaning", "formulate_response"])

        # Context-aware complexity assessment
        complexity_score = min(1.0, len(query.split()) / 20.0)  # Complexity based on length

        # Determine confidence based on keyword clarity and intent
        confidence = 0.9
        if not keywords:
            confidence -= 0.2
        if intent_type == "unknown":
            confidence -= 0.3

        confidence = max(0.1, confidence)

        return {
            "thoughts": thoughts,
            "reasoning_chain": reasoning_chain,
            "complexity_score": complexity_score,
            "primary_reasoning": f"Applied {len(reasoning_chain)} reasoning steps for {intent_type}",
            "confidence": confidence,
            "timestamp": time.time(),
            "ethics_risk": 0.05,
            "role_weight": 0.8,
            "processing_metadata": {
                "keywords_analyzed": len(keywords),
                "query_length": len(query),
                "reasoning_depth": len(reasoning_chain)
            }
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


class ActionNode(CognitiveNodeBase):
    """Node that executes actions based on thought analysis."""
    name = "action"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        thoughts = ctx.get("thoughts", [])
        reasoning_chain = ctx.get("reasoning_chain", [])
        query = ctx.get("query", "")

        await asyncio.sleep(0.025)  # Simulate processing

        actions_taken = []
        results = {}

        # Execute actions based on thoughts
        if "parse_mathematical_expression" in thoughts:
            # Simple math evaluation
            try:
                # Extract numbers and basic operations (safe evaluation)
                import re
                math_expr = re.findall(r'[\d+\-*/\(\)\s]+', query)
                if math_expr:
                    # Very basic calculator (unsafe eval avoided)
                    expr = math_expr[0].strip()
                    if all(c in "0123456789+-*/ ()." for c in expr):
                        result = eval(expr)  # Only for demo - would use safe math parser in production
                        actions_taken.append("mathematical_calculation")
                        results["calculation_result"] = result
            except Exception:
                actions_taken.append("calculation_failed")
                results["error"] = "Could not parse mathematical expression"

        if "research_facts" in thoughts:
            # Simulate fact lookup
            actions_taken.append("fact_research")
            results["facts_found"] = [
                "Relevant information retrieved from knowledge base",
                "Cross-referenced with multiple sources",
                "Confidence verified"
            ]

        if "evaluate_options" in thoughts:
            # Simulate decision analysis
            actions_taken.append("option_evaluation")
            results["options_analysis"] = {
                "primary_option": "Most likely course of action",
                "alternatives": ["Alternative approach 1", "Alternative approach 2"],
                "risk_assessment": "Low risk with proper safeguards"
            }

        if "external_api_call" in thoughts:
            # Simulate external API call (placeholder)
            actions_taken.append("api_interaction")
            results["api_response"] = {
                "status": "success",
                "data": "External service response",
                "latency_ms": 45
            }

        # Default action if no specific actions identified
        if not actions_taken:
            actions_taken.append("contextual_response_generation")
            results["response"] = f"Processed query with {len(reasoning_chain)} reasoning steps"

        # Ethics check for actions
        ethics_risk = 0.1
        if any("external" in action for action in actions_taken):
            ethics_risk = 0.3  # Higher risk for external interactions

        return {
            "actions_taken": actions_taken,
            "action_results": results,
            "execution_summary": f"Completed {len(actions_taken)} actions successfully",
            "confidence": 0.85,
            "timestamp": time.time(),
            "ethics_risk": ethics_risk,
            "role_weight": 0.9,
            "execution_metadata": {
                "actions_count": len(actions_taken),
                "processing_time_ms": 25,
                "success_rate": 1.0
            }
        }


class VisionNode(CognitiveNodeBase):
    """Node that processes visual or perceptual information."""
    name = "vision"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        query = ctx.get("query", "")

        await asyncio.sleep(0.03)  # Simulate processing

        # Check for visual processing cues
        visual_cues = []
        processing_modes = []

        if any(word in query.lower() for word in ["image", "picture", "visual", "see", "look", "view"]):
            visual_cues.append("image_analysis_requested")
            processing_modes.append("visual_analysis")

        if any(word in query.lower() for word in ["color", "shape", "pattern", "design"]):
            visual_cues.append("aesthetic_analysis_requested")
            processing_modes.append("pattern_recognition")

        if any(word in query.lower() for word in ["chart", "graph", "data", "plot"]):
            visual_cues.append("data_visualization_analysis")
            processing_modes.append("data_interpretation")

        # Simulate perception processing
        perception_results = {
            "detected_elements": len(visual_cues),
            "processing_modes": processing_modes,
            "visual_features": {
                "complexity": min(1.0, len(query.split()) / 15.0),
                "clarity": 0.8,
                "interpretability": 0.9
            }
        }

        if not visual_cues:
            # Default perceptual analysis
            visual_cues.append("general_perception")
            processing_modes.append("contextual_understanding")
            perception_results["fallback_mode"] = True

        return {
            "visual_cues": visual_cues,
            "processing_modes": processing_modes,
            "perception_results": perception_results,
            "visual_summary": f"Processed {len(visual_cues)} visual elements",
            "confidence": 0.75,
            "timestamp": time.time(),
            "ethics_risk": 0.05,
            "role_weight": 0.6,
            "perception_metadata": {
                "visual_elements_count": len(visual_cues),
                "processing_depth": len(processing_modes),
                "analysis_type": "perceptual_inference"
            }
        }


class ErrorNode(CognitiveNodeBase):
    """Node that throws errors for testing."""
    name = "error"
    AUTOINIT = True

    @classmethod
    def from_env(cls):
        return cls()

    async def process(self, ctx: Mapping[str, Any]) -> Mapping[str, Any]:
        raise ValueError("Simulated node error")
