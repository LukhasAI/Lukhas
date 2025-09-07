"""

#TAG:memory
#TAG:causal
#TAG:neuroplastic
#TAG:colony


Causal Reasoning Module

This module provides advanced causal reasoning capabilities for understanding
cause-effect relationships in input data and context.
"""
import streamlit as st
from datetime import timezone

import re
from datetime import datetime
from typing import Optional


class CausalReasoningModule:
    """
    Advanced causal reasoning for understanding cause-effect relationships
    """

    def __init__(self, timezone):
        self.causal_graph = {}
        self.causal_history = []
        self.confidence_threshold = 0.7

    def reason(self, attended_data: dict) -> dict:
        """Apply causal reasoning to attended data"""
        causal_elements = self._identify_causal_elements(attended_data)
        causal_chains = self._build_causal_chains(causal_elements)
        weighted_causes = self._calculate_causal_confidences(causal_chains)

        valid_causes = {k: v for k, v in weighted_causes.items() if v.get("confidence", 0) >= self.confidence_threshold}

        if valid_causes:
            self._update_causal_graph(valid_causes)
            primary_cause = self._identify_primary_cause(valid_causes)
            reasoning_path = self._extract_reasoning_path(valid_causes)
        else:
            primary_cause = None
            reasoning_path = []

        reasoning_results = {
            "primary_cause": primary_cause,
            "valid_causes": valid_causes,
            "reasoning_path": reasoning_path,
            "confidence": primary_cause["confidence"] if primary_cause else 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._update_history(reasoning_results)
        return reasoning_results

    def _identify_causal_elements(self, attended_data: dict) -> list[dict]:
        """Identify elements that might have causal relationships"""
        causal_elements = []
        content = attended_data.get("text", "")

        # Extract causal indicators
        causal_patterns = [
            r"because\\s+(.+?)(?=\\.|,|$)",
            r"due to\\s+(.+?)(?=\\.|,|$)",
            r"results in\\s+(.+?)(?=\\.|,|$)",
            r"leads to\\s+(.+?)(?=\\.|,|$)",
            r"causes?\\s+(.+?)(?=\\.|,|$)",
        ]

        for i, pattern in enumerate(causal_patterns):
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                causal_elements.append(
                    {
                        "type": "causal_relation",
                        "content": match.strip(),
                        "pattern_id": i,
                        "base_confidence": 0.8 - (i * 0.1),
                    }
                )

        # Add contextual elements
        if "context" in attended_data:
            context = attended_data["context"]
            for key, value in context.items():
                causal_elements.append(
                    {
                        "type": "contextual",
                        "content": f"{key}: {value}",
                        "base_confidence": 0.6,
                    }
                )

        return causal_elements

    def _build_causal_chains(self, causal_elements: list[dict]) -> dict:
        """Build chains of causal relationships"""
        causal_chains = {}

        for i, item in enumerate(causal_elements):
            chain_id = f"chain_{i}"
            causal_chains[chain_id] = {
                "elements": [item],
                "base_confidence": item["base_confidence"],
            }

            # Look for related elements
            for other_item in causal_elements:
                if other_item != item and (
                    item["content"].lower() in other_item["content"].lower()
                    or other_item["content"].lower() in item["content"].lower()
                ):
                    causal_chains[chain_id]["elements"].append(other_item)
                    causal_chains[chain_id]["base_confidence"] = (
                        causal_chains[chain_id]["base_confidence"] + other_item["base_confidence"]
                    ) / 2

        return causal_chains

    def _calculate_causal_confidences(self, causal_chains: dict) -> dict:
        """Calculate confidence levels for causal chains"""
        weighted_causes = {}

        for chain_id, chain in causal_chains.items():
            base_confidence = chain["base_confidence"]
            length_adjustment = min(0.2, 0.05 * len(chain["elements"]))
            element_types = {elem["type"] for elem in chain["elements"]}
            diversity_adjustment = min(0.15, 0.05 * len(element_types))
            final_confidence = min(0.99, base_confidence + length_adjustment + diversity_adjustment)

            weighted_causes[chain_id] = {
                "elements": chain["elements"],
                "confidence": final_confidence,
                "summary": self._summarize_chain(chain["elements"]),
            }

        return weighted_causes

    def _summarize_chain(self, elements: list[dict]) -> str:
        """Create summary of causal chain"""
        if not elements:
            return ""
        contents = [elem["content"] for elem in elements]
        return " -> ".join(contents) if len(contents) > 1 else contents[0]

    def _update_causal_graph(self, valid_causes: dict):
        """Update persistent causal graph"""
        timestamp = datetime.now(timezone.utc).isoformat()
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
                self.causal_graph[chain_id]["confidence_history"] = self.causal_graph[chain_id]["confidence_history"][
                    -10:
                ]

    def _identify_primary_cause(self, valid_causes: dict) -> Optional[dict]:
        """Identify most likely primary cause"""
        if not valid_causes:
            return None
        primary_cause_id = max(valid_causes.keys(), key=lambda k: valid_causes[k]["confidence"])
        return {
            "id": primary_cause_id,
            "summary": valid_causes[primary_cause_id]["summary"],
            "confidence": valid_causes[primary_cause_id]["confidence"],
        }

    def _extract_reasoning_path(self, valid_causes: dict) -> list[dict]:
        """Extract reasoning path from valid causes"""
        reasoning_steps = []
        for chain_data in valid_causes.values():
            for _i, element in enumerate(chain_data["elements"]):
                reasoning_steps.append(
                    {
                        "step": len(reasoning_steps) + 1,
                        "type": element["type"],
                        "content": element["content"],
                        "confidence": chain_data["confidence"],
                    }
                )
        reasoning_steps.sort(key=lambda x: x["confidence"], reverse=True)
        return reasoning_steps[:5]

    def _update_history(self, reasoning_results: dict):
        """Update reasoning history"""
        self.causal_history.append(
            {
                "timestamp": reasoning_results["timestamp"],
                "primary_cause": reasoning_results.get("primary_cause"),
                "confidence": reasoning_results.get("confidence"),
            }
        )
        self.causal_history = self.causal_history[-100:]

    def get_causal_insights(self) -> dict:
        """Get insights about causal reasoning patterns"""
        if not self.causal_history:
            return {"insights": "No causal reasoning history available"}

        recent_confidence = [entry["confidence"] for entry in self.causal_history[-10:]]
        avg_confidence = sum(recent_confidence) / len(recent_confidence) if recent_confidence else 0

        return {
            "average_confidence": avg_confidence,
            "total_reasoning_sessions": len(self.causal_history),
            "causal_graph_size": len(self.causal_graph),
            "confidence_trend": (
                "improving" if len(recent_confidence) > 1 and recent_confidence[-1] > recent_confidence[0] else "stable"
            ),
        }


__all__ = ["CausalReasoningModule"]
