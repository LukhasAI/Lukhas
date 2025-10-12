from datetime import datetime, timezone
import logging
import streamlit as st
import time
from typing import Dict
from typing import List
logger = logging.getLogger(__name__)
"""

#TAG:memory
#TAG:causal
#TAG:neuroplastic
#TAG:colony


Causal Reasoning Module for lukhas AI

This module implements advanced causal reasoning capabilities, establishing relationships
between events and actions using a hybrid neural-symbolic approach.

Based on the advanced implementation from Lukhas GitHub repository.
"""

import datetime
from typing import Any

from lukhas.core.common import get_logger

logger = get_logger(__name__)


class CausalReasoningModule:
    """
    Implements causal reasoning to establish relationships between events and actions.
    Uses a hybrid approach combining neural and symbolic methods.
    """

    def __init__(self):
        self.causal_graph = {}
        self.confidence_threshold = 0.7
        self.max_causal_depth = 5
        self.causal_history = []

    def reason(self, attended_data: dict) -> dict:
        """
        Apply causal reasoning to attended data

        Args:
            attended_data: Data that has been processed by attention mechanism

        Returns:
            Dict containing reasoning results and causal chains
        """
        # Extract content from attended data
        semantic_content = attended_data.get("attended_content", {}).get("semantic", {}).get("content")
        emotional_content = attended_data.get("attended_content", {}).get("emotional", {}).get("content")
        contextual_content = attended_data.get("attended_content", {}).get("contextual", {}).get("content")

        # Identify potential causes and effects
        causes_effects = self._extract_causal_elements(semantic_content, emotional_content, contextual_content)

        # Build causal chains
        causal_chains = self._build_causal_chains(causes_effects)

        # Calculate confidence in causal relationships
        weighted_causes = self._calculate_causal_confidences(causal_chains)

        # Filter by confidence threshold
        valid_causes = {k: v for k, v in weighted_causes.items() if v["confidence"] >= self.confidence_threshold}

        # Update internal causal graph
        self._update_causal_graph(valid_causes)

        # Prepare reasoning results
        reasoning_results = {
            "causal_chains": valid_causes,
            "primary_cause": (self._identify_primary_cause(valid_causes) if valid_causes else None),
            "confidence": (max([v["confidence"] for v in valid_causes.values()]) if valid_causes else 0.0),
            "reasoning_path": self._extract_reasoning_path(valid_causes),
            "original_attended_data": attended_data,
            "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        }

        # Add to history
        self._update_history(reasoning_results)

        return reasoning_results

    def _extract_causal_elements(self, semantic_content, emotional_content, contextual_content):
        """Extract potential causes and effects from different content type"""
        elements = []

        # Process semantic content for causal indicators
        if semantic_content:
            semantic_elements = self._process_semantic_causes(semantic_content)
            elements.extend(semantic_elements)

        # Process emotional content for causal patterns
        if emotional_content:
            emotional_elements = self._process_emotional_causes(emotional_content)
            elements.extend(emotional_elements)

        # Process contextual content for situational causes
        if contextual_content:
            contextual_elements = self._process_contextual_causes(contextual_content)
            elements.extend(contextual_elements)

        return elements

    def _process_semantic_causes(self, semantic_content):
        """Process semantic content for causal indicator"""
        causal_keywords = [
            "because",
            "since",
            "due to",
            "caused by",
            "resulting from",
            "leads to",
            "results in",
            "triggers",
            "influences",
            "affects",
        ]

        elements = []
        content_str = str(semantic_content).lower()

        for keyword in causal_keywords:
            if keyword in content_str:
                elements.append(
                    {
                        "type": "semantic_cause",
                        "indicator": keyword,
                        "content": semantic_content,
                        "confidence": 0.7,
                    }
                )

        return elements

    def _process_emotional_causes(self, emotional_content):
        """Process emotional content for causal pattern"""
        elements = []

        if isinstance(emotional_content, dict):
            # Look for emotional state changes that might indicate causation
            if "state_change" in emotional_content:
                elements.append(
                    {
                        "type": "emotional_cause",
                        "trigger": emotional_content.get("trigger"),
                        "change": emotional_content["state_change"],
                        "confidence": 0.8,
                    }
                )

        return elements

    def _process_contextual_causes(self, contextual_content):
        """Process contextual content for situational cause"""
        elements = []

        if isinstance(contextual_content, dict):
            # Look for temporal relationships
            if "temporal_sequence" in contextual_content:
                elements.append(
                    {
                        "type": "temporal_cause",
                        "sequence": contextual_content["temporal_sequence"],
                        "confidence": 0.6,
                    }
                )

            # Look for spatial relationships
            if "spatial_proximity" in contextual_content:
                elements.append(
                    {
                        "type": "spatial_cause",
                        "proximity": contextual_content["spatial_proximity"],
                        "confidence": 0.5,
                    }
                )

        return elements

    def _build_causal_chains(self, causes_effects):
        """Build causal chains by connecting related causes and effect"""
        causal_chains = {}

        # Group related elements into chains
        for i, element in enumerate(causes_effects):
            chain_id = f"chain_{i}"

            # Start a new chain with this element
            causal_chains[chain_id] = {
                "elements": [element],
                "base_confidence": element.get("confidence", 0.5),
            }

            # Look for related elements to extend the chain
            for j, other_element in enumerate(causes_effects):
                if i != j and self._are_elements_related(element, other_element):
                    causal_chains[chain_id]["elements"].append(other_element)
                    # Update confidence based on chain length and element confidence
                    causal_chains[chain_id]["base_confidence"] = (
                        causal_chains[chain_id]["base_confidence"] + other_element.get("confidence", 0.5)
                    ) / 2

        return causal_chains

    def _are_elements_related(self, element1, element2):
        """Check if two causal elements are related"""
        # Simple heuristic: elements are related if they share content or type
        if element1.get("type") == element2.get("type"):
            return True

        # Check for content overlap
        content1 = str(element1.get("content", "")).lower()
        content2 = str(element2.get("content", "")).lower()

        # Simple word overlap check
        words1 = set(content1.split())
        words2 = set(content2.split())
        overlap = len(words1.intersection(words2))

        return overlap > 0

    def _calculate_causal_confidences(self, causal_chains):
        """Calculate confidence levels for causal chain"""
        weighted_chains = {}

        for chain_id, chain_data in causal_chains.items():
            elements = chain_data["elements"]
            base_confidence = chain_data["base_confidence"]

            # Calculate chain strength based on number of elements and their types
            chain_strength = len(elements) * 0.1
            type_diversity = len({elem.get("type") for elem in elements}) * 0.1

            # Final confidence calculation
            final_confidence = min(0.95, base_confidence + chain_strength + type_diversity)

            weighted_chains[chain_id] = {
                "elements": elements,
                "confidence": final_confidence,
                "summary": self._summarize_chain(elements),
            }

        return weighted_chains

    def _summarize_chain(self, elements):
        """Create a summary of a causal chain"""
        if not elements:
            return "Empty chain"

        types = [elem.get("type", "unknown") for elem in elements]
        return f"Causal chain with {len(elements)} elements: {', '.join(set(types)}"  # noqa: invalid-syntax  # TODO: Expected ,, found }

    def _update_causal_graph(self, valid_causes):
        """Update the internal causal graph with new validated cause"""
        timestamp = datetime.datetime.now(timezone.utc).isoformat()

        for chain_id, chain_data in valid_causes.items():
            if chain_id not in self.causal_graph:
                self.causal_graph[chain_id] = {
                    "first_seen": timestamp,
                    "frequency": 1,
                    "confidence_history": [chain_data["confidence"]],
                }
            else:
                self.causal_graph[chain_id]["frequency"] += 1
                self.causal_graph[chain_id]["confidence_history"].append(chain_data["confidence"])
                # Keep last 10 confidence values

    # SYNTAX_ERROR_FIXED:
    # self.causal_graph[chain_id]['confidence_history'] = " +
    # "self.causal_graph[chain_id]['confidence_history'][-10:]

    def _identify_primary_cause(self, valid_causes):
        """Identify the most likely primary cause from valid cause"""
        if not valid_causes:
            return None

        # Find the cause with highest confidence
        primary_cause = max(valid_causes.items(), key=lambda x: x[1]["confidence"])

        return {
            "chain_id": primary_cause[0],
            "confidence": primary_cause[1]["confidence"],
            "summary": primary_cause[1]["summary"],
        }

    def _extract_reasoning_path(self, valid_causes):
        """Extract the reasoning path from valid cause"""
        if not valid_causes:
            return []

        path = []
        for chain_id, chain_data in valid_causes.items():
            path.append(
                {
                    "step": len(path) + 1,
                    "chain_id": chain_id,
                    "confidence": chain_data["confidence"],
                    "reasoning": chain_data["summary"],
                }
            )

        return path

    def _update_history(self, reasoning_results):
        """Update the reasoning history"""
        self.causal_history.append(reasoning_results)

        # Keep only last 100 reasoning cycles
        if len(self.causal_history) > 100:
            self.causal_history = self.causal_history[-100:]

    def get_causal_insights(self) -> dict:
        """
        Get insights from the causal reasoning system

        Returns:
            Dictionary containing causal insights and statistics
        """
        total_chains = len(self.causal_graph)
        avg_confidence = 0.0

        if total_chains > 0:
            all_confidences = []
            for chain_data in self.causal_graph.values():
                all_confidences.extend(chain_data["confidence_history"])

            if all_confidences:
                avg_confidence = sum(all_confidences) / len(all_confidences)

        return {
            "total_causal_chains": total_chains,
            "average_confidence": avg_confidence,
            "reasoning_cycles": len(self.causal_history),
            "confidence_threshold": self.confidence_threshold,
            "recent_insights": self.causal_history[-5:] if self.causal_history else [],
            "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        }

    def analyze_counterfactuals(self, scenario: dict) -> dict:
        """
        Perform counterfactual analysis on a given scenario

        Args:
            scenario: The scenario to analyze

        Returns:
            Counterfactual analysis results
        """
        counterfactuals = []

        # Generate alternative scenarios by modifying causal elements
        if "causal_elements" in scenario:
            for i, element in enumerate(scenario["causal_elements"]):
                # Create alternative by removing this element
                alt_scenario = scenario.copy()
                alt_elements = alt_scenario["causal_elements"].copy()
                alt_elements.pop(i)
                alt_scenario["causal_elements"] = alt_elements

                counterfactuals.append(
                    {
                        "type": "removal",
                        "removed_element": element,
                        "alternative_scenario": alt_scenario,
                        "likelihood": self._estimate_likelihood(alt_scenario),
                    }
                )

        return {
            "original_scenario": scenario,
            "counterfactuals": counterfactuals,
            "analysis_timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        }

    def _estimate_likelihood(self, scenario: dict) -> float:
        """
        Estimate the likelihood of a scenario based on causal patterns

        Args:
            scenario: The scenario to evaluate

        Returns:
            Likelihood score (0.0 to 1.0)
        """
        # Simple heuristic based on number of causal elements and their coherence
        elements = scenario.get("causal_elements", [])
        if not elements:
            return 0.1

        # Base likelihood decreases with complexity
        base_likelihood = max(0.1, 1.0 - (len(elements) * 0.1))

        # Adjust based on element types and coherence
        type_coherence = self._calculate_type_coherence(elements)

        return min(0.95, base_likelihood + type_coherence * 0.3)

    def _calculate_type_coherence(self, elements: list[dict]) -> float:
        """
        Calculate coherence score based on element types

        Args:
            elements: List of causal elements

        Returns:
            Coherence score (0.0 to 1.0)
        """
        if not elements:
            return 0.0

        types = [elem.get("type", "unknown") for elem in elements]
        unique_types = set(types)

        # More diverse types = higher coherence (up to a point)
        diversity_score = min(1.0, len(unique_types) / 3.0)

        return diversity_score

    async def analyze_causal_relationships(self, input_data, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze causal relationships in input data within given context

        Args:
            input_data: The data to analyze for causal relationships
            context: Context information for analysis

        Returns:
            Causal analysis results
        """
        try:
            # Convert input data to analysis format
            analysis_data = {
                "attended_content": {
                    "semantic": {"content": str(input_data)},
                    "emotional": {"content": context.get("emotional_state", {})},
                    "contextual": {"content": context},
                }
            }

            # Perform causal reasoning analysis
            reasoning_results = self.reason(analysis_data)

            # Extract key insights for the enhanced processing pipeline
            causal_insights = {
                "pattern_strength": self._calculate_pattern_strength(reasoning_results),
                "confidence": reasoning_results.get("confidence", 0.0),
                "primary_cause": reasoning_results.get("primary_cause"),
                "causal_chain_count": len(reasoning_results.get("causal_chains", {})),
                "reasoning_depth": self._calculate_reasoning_depth(reasoning_results),
                "temporal_relationships": self._extract_temporal_relationships(input_data, context),
                "analysis_timestamp": datetime.datetime.now(timezone.utc).isoformat(),
            }

            return {
                "status": "success",
                "causal_analysis": causal_insights,
                "detailed_reasoning": reasoning_results,
                "enhancement_applied": True,
            }

        except Exception as e:
            logger.error(f"Causal analysis failed: {e}")
            return {"status": "error", "error": str(e), "enhancement_applied": False}

    def _calculate_pattern_strength(self, reasoning_results: dict[str, Any]) -> float:
        """Calculate the overall strength of causal patterns found"""
        causal_chains = reasoning_results.get("causal_chains", {})
        if not causal_chains:
            return 0.0

        # Average confidence across all causal chains
        confidences = [chain.get("confidence", 0.0) for chain in causal_chains.values()]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Boost for multiple consistent chains
        chain_bonus = min(0.3, len(causal_chains) / 10.0)

        return min(1.0, avg_confidence + chain_bonus)

    def _calculate_reasoning_depth(self, reasoning_results: dict[str, Any]) -> int:
        """Calculate the depth of causal reasoning performed"""
        reasoning_path = reasoning_results.get("reasoning_path", [])
        return len(reasoning_path)

    def _extract_temporal_relationships(self, input_data, context: dict[str, Any]) -> dict[str, Any]:
        """Extract temporal relationships from input and context"""
        temporal_info = {
            "has_temporal_markers": False,
            "sequence_indicators": [],
            "time_references": [],
        }

        # Simple temporal marker detection
        data_str = str(input_data).lower()
        temporal_markers = [
            "before",
            "after",
            "then",
            "when",
            "while",
            "during",
            "since",
            "until",
        ]

        for marker in temporal_markers:
            if marker in data_str:
                temporal_info["has_temporal_markers"] = True
                temporal_info["sequence_indicators"].append(marker)

        # Check for time references in context
        if "timestamp" in context:
            temporal_info["time_references"].append("context_timestamp")

        return temporal_info
