import time
from typing import Any, Dict, List

from matriz.core.node_interface import CognitiveNode, NodeState


class AnalogicalReasoningNode(CognitiveNode):
    """
    Performs analogical reasoning by mapping structure from a known source domain
    to a new target domain. This node conforms to the modern MATRIZ CognitiveNode interface.
    """

    def __init__(self, tenant: str = "default"):
        super().__init__(
            node_name="analogical_reasoning",
            capabilities=["analogical_reasoning", "structure_mapping", "domain_comparison"],
            tenant=tenant,
        )

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Performs analogical reasoning based on the provided source and target domains.

        Args:
            input_data: A dictionary containing:
                - 'source_domain': The known domain with an understood structure.
                - 'target_domain': The novel domain to understand.
                - 'mapping_hints': Optional hints to guide the mapping process.

        Returns:
            A dictionary containing the answer, confidence, a MATRIZ node, and processing time.
        """
        start_time = time.time()

        source = input_data.get("source_domain", {})
        target = input_data.get("target_domain", {})
        hints = input_data.get("mapping_hints", [])
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))

        if not source or not target:
            confidence = 0.1
            answer = "Analogical reasoning requires both a source and a target domain."
            state = NodeState(confidence=confidence, salience=0.3)
            matriz_node = self.create_matriz_node(
                node_type="DECISION",
                state=state,
                trace_id=trace_id,
                additional_data={"error": "Missing source or target domain."}
            )
        else:
            source_structure = self._extract_structure(source)
            analogies = []
            for src_concept, src_relations in source_structure.items():
                tgt_concept = self._find_analogous_concept(src_concept, src_relations, target, hints)
                if tgt_concept:
                    similarity = self._compute_similarity(src_relations, tgt_concept)
                    mapping_type = self._classify_mapping(src_relations, tgt_concept)
                    analogies.append({
                        "source_concept": src_concept,
                        "target_concept": tgt_concept["name"],
                        "similarity_score": similarity,
                        "mapping_type": mapping_type,
                    })

            confidence = self._compute_confidence(analogies)
            answer = f"Found {len(analogies)} potential analogies between the source and target domains."
            state = NodeState(confidence=confidence, salience=0.8, utility=0.7)
            matriz_node = self.create_matriz_node(
                node_type="HYPOTHESIS",
                state=state,
                trace_id=trace_id,
                additional_data={
                    "analogies": analogies,
                    "source_concepts": len(source_structure),
                    "target_concepts": len(target.get("concepts", []))
                }
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        """Validates the output of the analogical reasoning node."""
        if not all(k in output for k in ["answer", "confidence", "matriz_node", "processing_time"]):
            return False
        if not (0 <= output["confidence"] <= 1):
            return False
        if not self.validate_matriz_node(output["matriz_node"]):
            return False
        return True

    def _extract_structure(self, domain: dict) -> Dict[str, List[str]]:
        """Extracts structural relationships from a domain."""
        structure = {}
        for concept in domain.get("concepts", []):
            relations = concept.get("relations", [])
            structure[concept["name"]] = relations
        return structure

    def _find_analogous_concept(self, src_concept: str, src_relations: List[str], target: dict, hints: List[str]) -> dict:
        """Finds an analogous concept in the target domain."""
        for hint in hints:
            if src_concept in hint:
                parts = hint.split("->")
                if len(parts) == 2 and parts[0].strip() == src_concept:
                    target_name = parts[1].strip()
                    for concept in target.get("concepts", []):
                        if concept["name"] == target_name:
                            return concept

        best_match, best_score = None, 0.0
        for concept in target.get("concepts", []):
            score = self._structural_similarity(src_relations, concept.get("relations", []))
            if score > best_score:
                best_score, best_match = score, concept

        return best_match if best_score > 0.5 else None

    def _structural_similarity(self, rels1: List[str], rels2: List[str]) -> float:
        """Computes structural similarity between two sets of relations."""
        if not rels1 or not rels2:
            return 0.0
        set1, set2 = set(rels1), set(rels2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def _compute_similarity(self, src_relations: List[str], tgt_concept: dict) -> float:
        """Computes the overall similarity score."""
        return self._structural_similarity(src_relations, tgt_concept.get("relations", []))

    def _classify_mapping(self, src_relations: List[str], tgt_concept: dict) -> str:
        """Classifies the type of analogy mapping."""
        similarity = self._compute_similarity(src_relations, tgt_concept)
        if similarity > 0.8:
            return "structural"
        elif similarity > 0.5:
            return "relational"
        else:
            return "surface"

    def _compute_confidence(self, analogies: List[dict]) -> float:
        """Computes the overall confidence in the analogical mapping."""
        if not analogies:
            return 0.0
        avg_similarity = sum(a["similarity_score"] for a in analogies) / len(analogies)
        structural_count = sum(1 for a in analogies if a["mapping_type"] == "structural")
        structural_boost = min(0.2, structural_count * 0.05)
        return min(1.0, avg_similarity + structural_boost)
