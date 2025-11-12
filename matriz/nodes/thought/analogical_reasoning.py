#!/usr/bin/env python3
"""
MATRIZ Analogical Reasoning Node

Performs analogical reasoning by mapping structural relationships from
a known domain to a novel domain. Supports structural, relational, and
surface-level analogies.

Example: "The atom is like a solar system" maps planetary orbits to electron orbits.
"""

import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState, NodeTrigger


@dataclass
class AnalogyMapping:
    """Mapping between source and target concepts."""
    source_concept: str
    target_concept: str
    similarity_score: float
    mapping_type: str  # "structural", "surface", "relational"


class AnalogicalReasoningNode(CognitiveNode):
    """
    Performs analogical reasoning: mapping structure from known domain to new domain.

    Capabilities:
    - Structural relationship extraction
    - Analogical concept mapping
    - Similarity scoring
    - Confidence calibration
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="matriz_analogical_reasoning",
            capabilities=[
                "analogical_mapping",
                "structural_similarity",
                "concept_transfer",
                "governed_trace"
            ],
            tenant=tenant
        )

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform analogical reasoning.

        Args:
            input_data: Dict containing:
                - source_domain: Known domain with understood structure
                - target_domain: Novel domain to understand
                - mapping_hints: Optional hints for mapping

        Returns:
            Dict with analogies, confidence, and MATRIZ node
        """
        start_time = time.time()

        source = input_data.get("source_domain", {})
        target = input_data.get("target_domain", {})
        hints = input_data.get("mapping_hints", [])

        # Extract structural features from source
        source_structure = self._extract_structure(source)

        # Find corresponding structure in target
        analogies = []
        for src_concept, src_relations in source_structure.items():
            tgt_concept = self._find_analogous_concept(
                src_concept, src_relations, target, hints
            )

            if tgt_concept:
                similarity = self._compute_similarity(src_relations, tgt_concept)
                analogies.append(
                    AnalogyMapping(
                        source_concept=src_concept,
                        target_concept=tgt_concept["name"],
                        similarity_score=similarity,
                        mapping_type=self._classify_mapping(src_relations, tgt_concept)
                    )
                )

        # Compute overall confidence
        confidence = self._compute_confidence(analogies)

        # Create NodeState
        state = NodeState(
            confidence=confidence,
            salience=min(1.0, 0.5 + 0.1 * len(analogies)),
            novelty=max(0.1, 1.0 - confidence),
            utility=min(1.0, 0.6 + confidence / 2)
        )

        # Create trigger
        trigger = NodeTrigger(
            event_type="analogical_reasoning_request",
            timestamp=int(time.time() * 1000)
        )

        # Build MATRIZ node
        matriz_node = {
            "id": str(uuid.uuid4()),
            "type": "ANALOGICAL_REASONING",
            "state": {
                "confidence": state.confidence,
                "salience": state.salience,
                "novelty": state.novelty,
                "utility": state.utility
            },
            "triggers": [{
                "event_type": trigger.event_type,
                "timestamp": trigger.timestamp
            }],
            "metadata": {
                "node_name": self.node_name,
                "tenant": self.tenant,
                "capabilities": self.capabilities,
                "processing_time": time.time() - start_time,
                "source_concepts": len(source_structure),
                "mapping_count": len(analogies)
            },
            "analogies": [
                {
                    "source": a.source_concept,
                    "target": a.target_concept,
                    "similarity": a.similarity_score,
                    "type": a.mapping_type
                }
                for a in analogies
            ]
        }

        return {
            "answer": {
                "analogies": matriz_node["analogies"],
                "mapping_count": len(analogies)
            },
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": time.time() - start_time
        }

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Validate output structure."""
        required = ["answer", "confidence", "matriz_node", "processing_time"]
        if not all(k in output for k in required):
            return False

        if not 0.0 <= output["confidence"] <= 1.0:
            return False

        if "analogies" not in output["answer"]:
            return False

        return True

    def _extract_structure(self, domain: dict) -> Dict[str, List[str]]:
        """Extract structural relationships from domain."""
        structure = {}
        for concept in domain.get("concepts", []):
            relations = concept.get("relations", [])
            structure[concept["name"]] = relations
        return structure

    def _find_analogous_concept(
        self, src_concept: str, src_relations: List[str],
        target: dict, hints: List[str]
    ) -> dict:
        """Find analogous concept in target domain."""
        # Check hints first
        for hint in hints:
            if " -> " in hint:
                parts = hint.split(" -> ")
                if len(parts) == 2 and parts[0].strip() == src_concept:
                    target_name = parts[1].strip()
                    for concept in target.get("concepts", []):
                        if concept["name"] == target_name:
                            return concept

        # No hint: find by structural similarity
        best_match = None
        best_score = 0.0

        for concept in target.get("concepts", []):
            score = self._structural_similarity(src_relations, concept.get("relations", []))
            if score > best_score:
                best_score = score
                best_match = concept

        return best_match if best_score > 0.5 else None

    def _structural_similarity(self, rels1: List[str], rels2: List[str]) -> float:
        """Compute structural similarity between relation sets."""
        if not rels1 or not rels2:
            return 0.0

        # Jaccard similarity
        set1 = set(rels1)
        set2 = set(rels2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _compute_similarity(self, src_relations: List[str], tgt_concept: dict) -> float:
        """Compute overall similarity score."""
        return self._structural_similarity(src_relations, tgt_concept.get("relations", []))

    def _classify_mapping(self, src_relations: List[str], tgt_concept: dict) -> str:
        """Classify type of analogy mapping."""
        similarity = self._compute_similarity(src_relations, tgt_concept)

        if similarity > 0.8:
            return "structural"  # Deep structural similarity
        elif similarity > 0.5:
            return "relational"  # Some shared relations
        else:
            return "surface"  # Surface-level similarity only

    def _compute_confidence(self, analogies: List[AnalogyMapping]) -> float:
        """Compute overall confidence in analogical mapping."""
        if not analogies:
            return 0.0

        # Average similarity score
        avg_similarity = sum(a.similarity_score for a in analogies) / len(analogies)

        # Boost if many structural mappings
        structural_count = sum(1 for a in analogies if a.mapping_type == "structural")
        structural_boost = min(0.2, structural_count * 0.05)

        return min(1.0, avg_similarity + structural_boost)
