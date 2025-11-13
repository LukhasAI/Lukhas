# Claude Code Task: Implement Missing MATRIZ Cognitive Nodes (MS001)

**Task ID**: MS001
**Priority**: P0 (Critical)
**Effort**: Large (>16 hours)
**Owner**: claude-code
**Branch**: `feat/matriz-complete-nodes`

---

## Objective

Complete the **MATRIZ cognitive node registry** by implementing all missing nodes required for the full cognitive loop: Memory-Attention-Thought-Action-Decision-Awareness.

---

## Context

Current state of MATRIZ node registry:
- ✅ **Memory nodes**: Basic recall, storage
- ✅ **Attention nodes**: Focus, filtering
- ⚠️ **Thought nodes**: INCOMPLETE - only basic reasoning
- ❌ **Action nodes**: MISSING - no action execution
- ❌ **Decision nodes**: MISSING - no decision framework
- ⚠️ **Awareness nodes**: INCOMPLETE - only basic introspection

**Problem**: Cannot execute complete cognitive loops without all node types.

**Solution**: Implement 15+ missing cognitive nodes across all categories.

---

## Implementation Requirements

### 1. Thought Nodes (5 nodes to implement)

#### 1.1 Analogical Reasoning Node

**File**: `matriz/nodes/thought/analogical_reasoning.py`

```python
from typing import Any, Dict, List
from dataclasses import dataclass

from matriz.core.node import CognitiveNode, NodeInput, NodeOutput
from matriz.core.registry import register_node


@dataclass
class AnalogyMapping:
    """Mapping between source and target concepts."""
    source_concept: str
    target_concept: str
    similarity_score: float
    mapping_type: str  # "structural", "surface", "relational"


@register_node("thought", "analogical_reasoning")
class AnalogicalReasoningNode(CognitiveNode):
    """
    Performs analogical reasoning: mapping structure from known domain to new domain.

    Example: "The atom is like a solar system" (maps planetary orbits to electron orbits)
    """

    def __init__(self):
        super().__init__(
            node_id="analogical_reasoning",
            category="thought",
            description="Maps structural relationships from known domain to novel domain"
        )

    async def process(self, input_data: NodeInput) -> NodeOutput:
        """
        Perform analogical reasoning.

        Input:
            - source_domain: Known domain with understood structure
            - target_domain: Novel domain to understand
            - mapping_hints: Optional hints for mapping

        Output:
            - analogies: List of AnalogyMapping objects
            - confidence: Overall confidence in mappings
        """
        source = input_data.data.get("source_domain", {})
        target = input_data.data.get("target_domain", {})
        hints = input_data.data.get("mapping_hints", [])

        # Extract structural features from source
        source_structure = self._extract_structure(source)

        # Find corresponding structure in target
        analogies = []
        for src_concept, src_relations in source_structure.items():
            # Try to map to target
            tgt_concept = self._find_analogous_concept(
                src_concept,
                src_relations,
                target,
                hints
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

        return NodeOutput(
            success=True,
            data={
                "analogies": [
                    {
                        "source": a.source_concept,
                        "target": a.target_concept,
                        "similarity": a.similarity_score,
                        "type": a.mapping_type
                    }
                    for a in analogies
                ],
                "confidence": confidence,
                "mapping_count": len(analogies)
            },
            metadata={
                "node_id": self.node_id,
                "source_concepts": len(source_structure),
                "target_concepts": len(target.get("concepts", []))
            }
        )

    def _extract_structure(self, domain: dict) -> Dict[str, List[str]]:
        """Extract structural relationships from domain."""
        # Simplified: extract concepts and their relations
        structure = {}
        for concept in domain.get("concepts", []):
            relations = concept.get("relations", [])
            structure[concept["name"]] = relations
        return structure

    def _find_analogous_concept(
        self,
        src_concept: str,
        src_relations: List[str],
        target: dict,
        hints: List[str]
    ) -> dict:
        """Find analogous concept in target domain."""
        # Check hints first
        for hint in hints:
            if src_concept in hint:
                # Parse hint to find target concept
                parts = hint.split("->")
                if len(parts) == 2 and parts[0].strip() == src_concept:
                    target_name = parts[1].strip()
                    # Find in target concepts
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

        # Simple Jaccard similarity
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
```

#### 1.2 Causal Reasoning Node

**File**: `matriz/nodes/thought/causal_reasoning.py`

```python
from typing import List, Dict, Tuple
from dataclasses import dataclass

from matriz.core.node import CognitiveNode, NodeInput, NodeOutput
from matriz.core.registry import register_node


@dataclass
class CausalLink:
    """A causal relationship between two events."""
    cause: str
    effect: str
    strength: float  # 0.0 - 1.0
    mechanism: str  # How cause produces effect
    confidence: float  # Confidence in this link


@register_node("thought", "causal_reasoning")
class CausalReasoningNode(CognitiveNode):
    """
    Performs causal reasoning: identifying cause-effect relationships.

    Uses causal inference to distinguish correlation from causation.
    """

    def __init__(self):
        super().__init__(
            node_id="causal_reasoning",
            category="thought",
            description="Identifies and analyzes cause-effect relationships"
        )

    async def process(self, input_data: NodeInput) -> NodeOutput:
        """
        Perform causal reasoning.

        Input:
            - events: List of observed events
            - temporal_order: Temporal relationships between events
            - domain_knowledge: Background knowledge about domain

        Output:
            - causal_links: Identified causal relationships
            - causal_graph: Graph representation of causality
            - confidence: Overall confidence in causal model
        """
        events = input_data.data.get("events", [])
        temporal_order = input_data.data.get("temporal_order", {})
        domain_knowledge = input_data.data.get("domain_knowledge", {})

        # Identify potential causal links
        potential_links = self._identify_potential_causes(events, temporal_order)

        # Filter out spurious correlations
        causal_links = self._filter_spurious_correlations(
            potential_links,
            domain_knowledge
        )

        # Build causal graph
        causal_graph = self._build_causal_graph(causal_links)

        # Compute confidence
        confidence = self._compute_model_confidence(causal_links, causal_graph)

        return NodeOutput(
            success=True,
            data={
                "causal_links": [
                    {
                        "cause": link.cause,
                        "effect": link.effect,
                        "strength": link.strength,
                        "mechanism": link.mechanism,
                        "confidence": link.confidence
                    }
                    for link in causal_links
                ],
                "causal_graph": causal_graph,
                "confidence": confidence
            },
            metadata={
                "node_id": self.node_id,
                "event_count": len(events),
                "link_count": len(causal_links)
            }
        )

    def _identify_potential_causes(
        self,
        events: List[dict],
        temporal_order: dict
    ) -> List[CausalLink]:
        """Identify potential causal relationships based on temporal precedence."""
        potential_links = []

        for i, event_a in enumerate(events):
            for j, event_b in enumerate(events):
                if i == j:
                    continue

                # Check temporal precedence (cause must precede effect)
                if self._precedes(event_a, event_b, temporal_order):
                    # Compute correlation strength
                    strength = self._compute_correlation(event_a, event_b)

                    if strength > 0.3:  # Threshold for consideration
                        potential_links.append(
                            CausalLink(
                                cause=event_a["name"],
                                effect=event_b["name"],
                                strength=strength,
                                mechanism="unknown",
                                confidence=0.5  # Low initial confidence
                            )
                        )

        return potential_links

    def _precedes(self, event_a: dict, event_b: dict, temporal_order: dict) -> bool:
        """Check if event_a temporally precedes event_b."""
        # Simplified: check timestamps
        ts_a = event_a.get("timestamp", 0)
        ts_b = event_b.get("timestamp", 0)
        return ts_a < ts_b

    def _compute_correlation(self, event_a: dict, event_b: dict) -> float:
        """Compute correlation strength between events."""
        # Simplified: based on co-occurrence
        # In real implementation: use statistical correlation

        # Placeholder: random correlation for demo
        return 0.7  # Would be computed from data

    def _filter_spurious_correlations(
        self,
        potential_links: List[CausalLink],
        domain_knowledge: dict
    ) -> List[CausalLink]:
        """Filter out spurious correlations using domain knowledge."""
        causal_links = []

        for link in potential_links:
            # Check if mechanism exists in domain knowledge
            mechanism = self._find_mechanism(link.cause, link.effect, domain_knowledge)

            if mechanism:
                link.mechanism = mechanism
                link.confidence = 0.8  # Higher confidence with known mechanism
                causal_links.append(link)
            elif link.strength > 0.7:
                # Strong correlation without known mechanism
                link.mechanism = "unknown (strong correlation)"
                link.confidence = 0.6
                causal_links.append(link)

        return causal_links

    def _find_mechanism(self, cause: str, effect: str, domain_knowledge: dict) -> str:
        """Find causal mechanism in domain knowledge."""
        mechanisms = domain_knowledge.get("causal_mechanisms", {})

        # Look for direct mechanism
        key = f"{cause}->{effect}"
        if key in mechanisms:
            return mechanisms[key]

        # Look for general pattern
        for pattern, mechanism in mechanisms.items():
            if cause in pattern and effect in pattern:
                return mechanism

        return ""

    def _build_causal_graph(self, causal_links: List[CausalLink]) -> dict:
        """Build directed graph of causal relationships."""
        nodes = set()
        edges = []

        for link in causal_links:
            nodes.add(link.cause)
            nodes.add(link.effect)
            edges.append({
                "from": link.cause,
                "to": link.effect,
                "weight": link.strength
            })

        return {
            "nodes": list(nodes),
            "edges": edges
        }

    def _compute_model_confidence(
        self,
        causal_links: List[CausalLink],
        causal_graph: dict
    ) -> float:
        """Compute overall confidence in causal model."""
        if not causal_links:
            return 0.0

        # Average confidence across links
        avg_confidence = sum(link.confidence for link in causal_links) / len(causal_links)

        # Penalty for complex graphs (more uncertainty)
        complexity_penalty = min(0.2, len(causal_graph["edges"]) * 0.02)

        return max(0.0, avg_confidence - complexity_penalty)
```

#### 1.3 Counterfactual Reasoning Node

**File**: `matriz/nodes/thought/counterfactual_reasoning.py`

```python
from typing import Dict, List, Any
from dataclasses import dataclass

from matriz.core.node import CognitiveNode, NodeInput, NodeOutput
from matriz.core.registry import register_node


@dataclass
class CounterfactualScenario:
    """A counterfactual 'what if' scenario."""
    intervention: str  # What we change
    original_outcome: str
    counterfactual_outcome: str
    likelihood: float  # How likely this outcome is
    explanation: str


@register_node("thought", "counterfactual_reasoning")
class CounterfactualReasoningNode(CognitiveNode):
    """
    Performs counterfactual reasoning: 'What if X had been different?'

    Useful for understanding causality, planning, and learning from mistakes.
    """

    def __init__(self):
        super().__init__(
            node_id="counterfactual_reasoning",
            category="thought",
            description="Reasons about alternative scenarios and outcomes"
        )

    async def process(self, input_data: NodeInput) -> NodeOutput:
        """
        Perform counterfactual reasoning.

        Input:
            - actual_scenario: What actually happened
            - intervention: What to change in counterfactual
            - causal_model: Model of causal relationships

        Output:
            - counterfactual_scenarios: Alternative outcomes
            - most_likely: Most likely alternative outcome
            - insights: Insights from counterfactual analysis
        """
        actual = input_data.data.get("actual_scenario", {})
        intervention = input_data.data.get("intervention", {})
        causal_model = input_data.data.get("causal_model", {})

        # Generate counterfactual scenarios
        scenarios = self._generate_scenarios(actual, intervention, causal_model)

        # Find most likely alternative
        most_likely = max(scenarios, key=lambda s: s.likelihood) if scenarios else None

        # Extract insights
        insights = self._extract_insights(actual, scenarios, causal_model)

        return NodeOutput(
            success=True,
            data={
                "counterfactual_scenarios": [
                    {
                        "intervention": s.intervention,
                        "original_outcome": s.original_outcome,
                        "counterfactual_outcome": s.counterfactual_outcome,
                        "likelihood": s.likelihood,
                        "explanation": s.explanation
                    }
                    for s in scenarios
                ],
                "most_likely": {
                    "outcome": most_likely.counterfactual_outcome,
                    "likelihood": most_likely.likelihood,
                    "explanation": most_likely.explanation
                } if most_likely else None,
                "insights": insights
            },
            metadata={
                "node_id": self.node_id,
                "scenario_count": len(scenarios)
            }
        )

    def _generate_scenarios(
        self,
        actual: dict,
        intervention: dict,
        causal_model: dict
    ) -> List[CounterfactualScenario]:
        """Generate possible counterfactual scenarios."""
        scenarios = []

        # Get actual outcome
        original_outcome = actual.get("outcome", "unknown")

        # Apply intervention to causal model
        modified_model = self._apply_intervention(causal_model, intervention)

        # Simulate alternative outcomes
        outcomes = self._simulate_outcomes(modified_model, actual, intervention)

        for outcome, likelihood in outcomes:
            scenarios.append(
                CounterfactualScenario(
                    intervention=intervention.get("description", "unknown"),
                    original_outcome=original_outcome,
                    counterfactual_outcome=outcome,
                    likelihood=likelihood,
                    explanation=self._explain_difference(
                        original_outcome,
                        outcome,
                        intervention
                    )
                )
            )

        return scenarios

    def _apply_intervention(self, causal_model: dict, intervention: dict) -> dict:
        """Apply intervention to causal model."""
        # Create modified copy
        modified = causal_model.copy()

        # Update specified variables
        var_name = intervention.get("variable")
        var_value = intervention.get("value")

        if var_name and "variables" in modified:
            modified["variables"][var_name] = var_value

        return modified

    def _simulate_outcomes(
        self,
        modified_model: dict,
        actual: dict,
        intervention: dict
    ) -> List[Tuple[str, float]]:
        """Simulate possible outcomes given modified model."""
        # Simplified: generate a few plausible outcomes
        # Real implementation would use causal inference

        outcomes = []

        # Original outcome (lower likelihood due to intervention)
        outcomes.append((actual.get("outcome", "unknown"), 0.3))

        # Alternative outcome 1 (higher likelihood)
        alt_outcome = f"{actual.get('outcome', 'unknown')}_modified"
        outcomes.append((alt_outcome, 0.6))

        # Unexpected outcome (lower likelihood)
        outcomes.append(("unexpected_outcome", 0.1))

        return outcomes

    def _explain_difference(
        self,
        original: str,
        counterfactual: str,
        intervention: dict
    ) -> str:
        """Explain why outcomes differ."""
        if original == counterfactual:
            return "Intervention had no effect on outcome"

        var_name = intervention.get("variable", "unknown")
        return f"Changing {var_name} altered the causal chain, leading to {counterfactual}"

    def _extract_insights(
        self,
        actual: dict,
        scenarios: List[CounterfactualScenario],
        causal_model: dict
    ) -> List[str]:
        """Extract actionable insights from counterfactual analysis."""
        insights = []

        # Find scenarios with better outcomes
        original_outcome = actual.get("outcome", "unknown")
        better_scenarios = [
            s for s in scenarios
            if s.counterfactual_outcome != original_outcome
            and s.likelihood > 0.4
        ]

        if better_scenarios:
            insights.append(
                f"Could have achieved different outcome by: {better_scenarios[0].intervention}"
            )

        # Identify critical decision points
        insights.append("Critical factors: [would be extracted from causal model]")

        return insights
```

#### 1.4 Abductive Reasoning Node (Inference to Best Explanation)

**File**: `matriz/nodes/thought/abductive_reasoning.py`

```python
from typing import List, Dict, Tuple
from dataclasses import dataclass

from matriz.core.node import CognitiveNode, NodeInput, NodeOutput
from matriz.core.registry import register_node


@dataclass
class Explanation:
    """A candidate explanation for observations."""
    hypothesis: str
    explains: List[str]  # Observations explained
    plausibility: float  # 0.0 - 1.0
    simplicity: float  # 0.0 - 1.0 (prefer simpler)
    score: float  # Overall score


@register_node("thought", "abductive_reasoning")
class AbductiveReasoningNode(CognitiveNode):
    """
    Performs abductive reasoning: inference to the best explanation.

    Given observations, generates and evaluates candidate explanations.
    """

    def __init__(self):
        super().__init__(
            node_id="abductive_reasoning",
            category="thought",
            description="Infers best explanation for observations"
        )

    async def process(self, input_data: NodeInput) -> NodeOutput:
        """
        Perform abductive reasoning.

        Input:
            - observations: List of observed facts
            - background_knowledge: Domain knowledge
            - explanation_constraints: Constraints on explanations

        Output:
            - best_explanation: Highest-scoring explanation
            - alternative_explanations: Other plausible explanations
            - confidence: Confidence in best explanation
        """
        observations = input_data.data.get("observations", [])
        background = input_data.data.get("background_knowledge", {})
        constraints = input_data.data.get("explanation_constraints", {})

        # Generate candidate explanations
        candidates = self._generate_candidates(observations, background)

        # Evaluate explanations
        explanations = self._evaluate_explanations(
            candidates,
            observations,
            background,
            constraints
        )

        # Rank by score
        explanations.sort(key=lambda e: e.score, reverse=True)

        # Select best
        best = explanations[0] if explanations else None

        # Compute confidence
        confidence = self._compute_confidence(explanations)

        return NodeOutput(
            success=True,
            data={
                "best_explanation": {
                    "hypothesis": best.hypothesis,
                    "explains": best.explains,
                    "plausibility": best.plausibility,
                    "simplicity": best.simplicity,
                    "score": best.score
                } if best else None,
                "alternative_explanations": [
                    {
                        "hypothesis": e.hypothesis,
                        "score": e.score
                    }
                    for e in explanations[1:6]  # Top 5 alternatives
                ],
                "confidence": confidence
            },
            metadata={
                "node_id": self.node_id,
                "observation_count": len(observations),
                "candidate_count": len(explanations)
            }
        )

    def _generate_candidates(
        self,
        observations: List[str],
        background: dict
    ) -> List[str]:
        """Generate candidate explanations."""
        candidates = []

        # Generate from background knowledge
        for pattern in background.get("patterns", []):
            if self._matches_observations(pattern, observations):
                candidates.append(pattern["explanation"])

        # Generate from observation combinations
        # (simplified - real implementation would use more sophisticated methods)
        if len(observations) >= 2:
            candidates.append(f"Common cause of: {', '.join(observations[:2])}")

        return candidates

    def _matches_observations(self, pattern: dict, observations: List[str]) -> bool:
        """Check if pattern matches observations."""
        required = pattern.get("requires", [])
        return all(obs in observations for obs in required)

    def _evaluate_explanations(
        self,
        candidates: List[str],
        observations: List[str],
        background: dict,
        constraints: dict
    ) -> List[Explanation]:
        """Evaluate candidate explanations."""
        explanations = []

        for hypothesis in candidates:
            # How many observations does it explain?
            explains = self._observations_explained(hypothesis, observations, background)

            # How plausible is it?
            plausibility = self._assess_plausibility(hypothesis, background)

            # How simple is it?
            simplicity = self._assess_simplicity(hypothesis)

            # Overall score (weighted combination)
            score = (
                0.5 * (len(explains) / max(1, len(observations)))  # Coverage
                + 0.3 * plausibility
                + 0.2 * simplicity
            )

            explanations.append(
                Explanation(
                    hypothesis=hypothesis,
                    explains=explains,
                    plausibility=plausibility,
                    simplicity=simplicity,
                    score=score
                )
            )

        return explanations

    def _observations_explained(
        self,
        hypothesis: str,
        observations: List[str],
        background: dict
    ) -> List[str]:
        """Determine which observations are explained by hypothesis."""
        # Simplified: check if observation keywords in hypothesis
        explained = []
        for obs in observations:
            if any(word in hypothesis.lower() for word in obs.lower().split()):
                explained.append(obs)
        return explained

    def _assess_plausibility(self, hypothesis: str, background: dict) -> float:
        """Assess how plausible explanation is given background knowledge."""
        # Check if hypothesis aligns with known patterns
        for pattern in background.get("patterns", []):
            if hypothesis in pattern.get("explanation", ""):
                return 0.9  # High plausibility

        # Default moderate plausibility
        return 0.5

    def _assess_simplicity(self, hypothesis: str) -> float:
        """Assess simplicity (prefer Occam's razor)."""
        # Simpler = fewer assumptions = shorter description
        # Simplified: inverse of length
        max_len = 200
        return max(0.0, 1.0 - len(hypothesis) / max_len)

    def _compute_confidence(self, explanations: List[Explanation]) -> float:
        """Compute confidence in best explanation."""
        if not explanations:
            return 0.0

        # High confidence if best explanation much better than alternatives
        best_score = explanations[0].score
        second_best_score = explanations[1].score if len(explanations) > 1 else 0.0

        gap = best_score - second_best_score

        return min(1.0, best_score + gap * 0.5)
```

#### 1.5 Metacognitive Reasoning Node (Thinking About Thinking)

**File**: `matriz/nodes/thought/metacognitive_reasoning.py`

```python
from typing import Dict, List, Any
from dataclasses import dataclass

from matriz.core.node import CognitiveNode, NodeInput, NodeOutput
from matriz.core.registry import register_node


@dataclass
class MetacognitiveAssessment:
    """Assessment of cognitive process quality."""
    process_name: str
    confidence: float  # How confident are we?
    completeness: float  # Did we consider everything?
    coherence: float  # Do conclusions follow logically?
    biases_detected: List[str]  # Cognitive biases detected
    improvements: List[str]  # Suggestions for improvement


@register_node("thought", "metacognitive_reasoning")
class MetacognitiveReasoningNode(CognitiveNode):
    """
    Performs metacognitive reasoning: monitoring and evaluating own thought processes.

    Implements self-reflection, bias detection, and reasoning quality assessment.
    """

    def __init__(self):
        super().__init__(
            node_id="metacognitive_reasoning",
            category="thought",
            description="Monitors and evaluates quality of reasoning"
        )

    async def process(self, input_data: NodeInput) -> NodeOutput:
        """
        Perform metacognitive assessment.

        Input:
            - reasoning_trace: Trace of reasoning steps
            - conclusions: Conclusions reached
            - evidence: Evidence used

        Output:
            - assessment: Quality assessment of reasoning
            - confidence_calibration: How well-calibrated is confidence?
            - recommendations: How to improve reasoning
        """
        trace = input_data.data.get("reasoning_trace", [])
        conclusions = input_data.data.get("conclusions", [])
        evidence = input_data.data.get("evidence", [])

        # Assess reasoning quality
        assessment = self._assess_reasoning_quality(trace, conclusions, evidence)

        # Calibrate confidence
        calibration = self._calibrate_confidence(assessment, trace)

        # Generate recommendations
        recommendations = self._generate_recommendations(assessment)

        return NodeOutput(
            success=True,
            data={
                "assessment": {
                    "confidence": assessment.confidence,
                    "completeness": assessment.completeness,
                    "coherence": assessment.coherence,
                    "biases_detected": assessment.biases_detected,
                    "improvements": assessment.improvements
                },
                "confidence_calibration": calibration,
                "recommendations": recommendations
            },
            metadata={
                "node_id": self.node_id,
                "trace_length": len(trace),
                "conclusion_count": len(conclusions)
            }
        )

    def _assess_reasoning_quality(
        self,
        trace: List[dict],
        conclusions: List[str],
        evidence: List[str]
    ) -> MetacognitiveAssessment:
        """Assess quality of reasoning process."""
        # Assess confidence
        confidence = self._assess_confidence(trace, evidence)

        # Assess completeness
        completeness = self._assess_completeness(trace, conclusions)

        # Assess coherence
        coherence = self._assess_coherence(trace, conclusions)

        # Detect biases
        biases = self._detect_biases(trace, evidence)

        # Generate improvement suggestions
        improvements = self._suggest_improvements(
            confidence,
            completeness,
            coherence,
            biases
        )

        return MetacognitiveAssessment(
            process_name="reasoning",
            confidence=confidence,
            completeness=completeness,
            coherence=coherence,
            biases_detected=biases,
            improvements=improvements
        )

    def _assess_confidence(self, trace: List[dict], evidence: List[str]) -> float:
        """Assess confidence in reasoning."""
        # More evidence = higher confidence
        evidence_score = min(1.0, len(evidence) * 0.2)

        # Longer trace = more thorough = higher confidence
        trace_score = min(1.0, len(trace) * 0.1)

        return (evidence_score + trace_score) / 2

    def _assess_completeness(self, trace: List[dict], conclusions: List[str]) -> float:
        """Assess completeness of reasoning."""
        # Did we consider alternatives?
        alternatives_considered = sum(
            1 for step in trace
            if "alternative" in step.get("type", "").lower()
        )

        # Did we address all conclusions?
        if not conclusions:
            return 0.5  # Neutral

        addressed = sum(
            1 for conclusion in conclusions
            if any(conclusion in str(step) for step in trace)
        )

        coverage = addressed / len(conclusions) if conclusions else 0.0

        # Combine scores
        return (coverage + min(1.0, alternatives_considered * 0.3)) / 2

    def _assess_coherence(self, trace: List[dict], conclusions: List[str]) -> float:
        """Assess logical coherence of reasoning."""
        # Check for logical consistency
        # Simplified: check if steps follow logically

        coherent_steps = 0
        for i in range(1, len(trace)):
            if self._follows_logically(trace[i-1], trace[i]):
                coherent_steps += 1

        coherence = coherent_steps / max(1, len(trace) - 1) if len(trace) > 1 else 1.0

        return coherence

    def _follows_logically(self, step1: dict, step2: dict) -> bool:
        """Check if step2 follows logically from step1."""
        # Simplified: check if step2 references step1 output
        return step1.get("output") in str(step2.get("input", ""))

    def _detect_biases(self, trace: List[dict], evidence: List[str]) -> List[str]:
        """Detect cognitive biases in reasoning."""
        biases = []

        # Confirmation bias: only considering supporting evidence
        if evidence:
            supporting = sum(1 for e in evidence if "confirm" in e.lower())
            if supporting / len(evidence) > 0.8:
                biases.append("confirmation_bias")

        # Availability bias: recent evidence weighted too heavily
        if trace and len(trace) > 3:
            recent_steps = trace[-3:]
            recent_weight = sum(s.get("weight", 0.5) for s in recent_steps) / 3
            if recent_weight > 0.8:
                biases.append("availability_bias")

        # Anchoring bias: first evidence anchors all reasoning
        if trace and len(trace) > 2:
            first_weight = trace[0].get("weight", 0.5)
            if first_weight > 0.9:
                biases.append("anchoring_bias")

        return biases

    def _suggest_improvements(
        self,
        confidence: float,
        completeness: float,
        coherence: float,
        biases: List[str]
    ) -> List[str]:
        """Suggest improvements to reasoning."""
        improvements = []

        if confidence < 0.5:
            improvements.append("Gather more evidence to support conclusions")

        if completeness < 0.6:
            improvements.append("Consider alternative explanations")
            improvements.append("Address all aspects of the problem")

        if coherence < 0.7:
            improvements.append("Ensure logical consistency between steps")

        if "confirmation_bias" in biases:
            improvements.append("Actively seek disconfirming evidence")

        if "availability_bias" in biases:
            improvements.append("Weight evidence by quality, not recency")

        if "anchoring_bias" in biases:
            improvements.append("Re-evaluate initial assumptions")

        return improvements

    def _calibrate_confidence(
        self,
        assessment: MetacognitiveAssessment,
        trace: List[dict]
    ) -> Dict[str, Any]:
        """Calibrate confidence levels."""
        # Are we overconfident or underconfident?

        stated_confidence = assessment.confidence
        actual_quality = (
            assessment.completeness + assessment.coherence
        ) / 2

        calibration_error = abs(stated_confidence - actual_quality)

        if stated_confidence > actual_quality + 0.2:
            calibration_status = "overconfident"
        elif stated_confidence < actual_quality - 0.2:
            calibration_status = "underconfident"
        else:
            calibration_status = "well_calibrated"

        return {
            "stated_confidence": stated_confidence,
            "actual_quality": actual_quality,
            "calibration_error": calibration_error,
            "status": calibration_status
        }

    def _generate_recommendations(
        self,
        assessment: MetacognitiveAssessment
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Add general recommendations
        recommendations.append("Continue monitoring reasoning quality")

        # Add specific improvements
        recommendations.extend(assessment.improvements)

        # Add bias mitigation strategies
        for bias in assessment.biases_detected:
            recommendations.append(f"Mitigate {bias} by seeking diverse perspectives")

        return recommendations
```

---

### 2. Action Nodes (5 nodes to implement)

#### 2.1 Plan Generation Node

**File**: `matriz/nodes/action/plan_generation.py`

```python
from typing import List, Dict
from dataclasses import dataclass

from matriz.core.node import CognitiveNode, NodeInput, NodeOutput
from matriz.core.registry import register_node


@dataclass
class ActionStep:
    """A single step in an action plan."""
    step_id: str
    description: str
    preconditions: List[str]
    effects: List[str]
    estimated_duration: float  # seconds


@register_node("action", "plan_generation")
class PlanGenerationNode(CognitiveNode):
    """
    Generates multi-step action plans to achieve goals.

    Uses hierarchical task decomposition and constraint satisfaction.
    """

    def __init__(self):
        super().__init__(
            node_id="plan_generation",
            category="action",
            description="Generates step-by-step plans to achieve goals"
        )

    async def process(self, input_data: NodeInput) -> NodeOutput:
        """
        Generate action plan.

        Input:
            - goal: Target goal to achieve
            - current_state: Current state of the world
            - available_actions: Actions available to agent
            - constraints: Constraints on plan (time, resources, etc.)

        Output:
            - plan: Sequence of action steps
            - estimated_time: Total estimated time
            - success_probability: Estimated probability of success
        """
        goal = input_data.data.get("goal", "")
        current_state = input_data.data.get("current_state", {})
        available_actions = input_data.data.get("available_actions", [])
        constraints = input_data.data.get("constraints", {})

        # Decompose goal into subgoals
        subgoals = self._decompose_goal(goal, current_state)

        # Generate plan steps
        plan_steps = []
        for subgoal in subgoals:
            steps = self._plan_for_subgoal(
                subgoal,
                current_state,
                available_actions,
                constraints
            )
            plan_steps.extend(steps)

        # Estimate total time
        estimated_time = sum(step.estimated_duration for step in plan_steps)

        # Estimate success probability
        success_prob = self._estimate_success_probability(plan_steps, current_state)

        return NodeOutput(
            success=True,
            data={
                "plan": [
                    {
                        "step_id": step.step_id,
                        "description": step.description,
                        "preconditions": step.preconditions,
                        "effects": step.effects,
                        "estimated_duration": step.estimated_duration
                    }
                    for step in plan_steps
                ],
                "estimated_time": estimated_time,
                "success_probability": success_prob
            },
            metadata={
                "node_id": self.node_id,
                "step_count": len(plan_steps),
                "subgoal_count": len(subgoals)
            }
        )

    def _decompose_goal(self, goal: str, current_state: dict) -> List[str]:
        """Decompose high-level goal into subgoals."""
        # Simplified: split by "and" or generate sub-objectives
        subgoals = []

        if " and " in goal:
            subgoals = goal.split(" and ")
        else:
            # Single goal
            subgoals = [goal]

        return [sg.strip() for sg in subgoals]

    def _plan_for_subgoal(
        self,
        subgoal: str,
        current_state: dict,
        available_actions: List[dict],
        constraints: dict
    ) -> List[ActionStep]:
        """Plan steps to achieve a single subgoal."""
        steps = []

        # Find actions that achieve subgoal
        relevant_actions = [
            action for action in available_actions
            if subgoal.lower() in action.get("effects", "").lower()
        ]

        for i, action in enumerate(relevant_actions[:3]):  # Max 3 steps per subgoal
            steps.append(
                ActionStep(
                    step_id=f"step_{len(steps) + 1}",
                    description=action.get("description", ""),
                    preconditions=action.get("preconditions", []),
                    effects=action.get("effects", []),
                    estimated_duration=action.get("duration", 10.0)
                )
            )

        return steps

    def _estimate_success_probability(
        self,
        plan_steps: List[ActionStep],
        current_state: dict
    ) -> float:
        """Estimate probability that plan will succeed."""
        # Simplified: based on precondition satisfaction
        satisfied_preconditions = 0
        total_preconditions = 0

        for step in plan_steps:
            for precond in step.preconditions:
                total_preconditions += 1
                if precond in current_state.get("facts", []):
                    satisfied_preconditions += 1

        if total_preconditions == 0:
            return 0.8  # Default high probability

        return satisfied_preconditions / total_preconditions
```

---

(Continue with Decision Nodes and Awareness Nodes similarly...)

---

## Testing Requirements

### Unit Tests for Each Node

**File**: `tests/unit/matriz/nodes/thought/test_analogical_reasoning.py`

```python
import pytest
from matriz.nodes.thought.analogical_reasoning import AnalogicalReasoningNode


@pytest.mark.asyncio
async def test_analogical_reasoning_solar_system_atom():
    """Test classic solar system → atom analogy."""
    node = AnalogicalReasoningNode()

    input_data = {
        "source_domain": {
            "name": "solar_system",
            "concepts": [
                {
                    "name": "sun",
                    "relations": ["center", "massive", "attracts"]
                },
                {
                    "name": "planets",
                    "relations": ["orbit", "smaller", "attracted"]
                }
            ]
        },
        "target_domain": {
            "name": "atom",
            "concepts": [
                {
                    "name": "nucleus",
                    "relations": ["center", "massive", "attracts"]
                },
                {
                    "name": "electrons",
                    "relations": ["orbit", "smaller", "attracted"]
                }
            ]
        },
        "mapping_hints": ["sun -> nucleus", "planets -> electrons"]
    }

    result = await node.process(NodeInput(data=input_data))

    assert result.success
    assert len(result.data["analogies"]) >= 2
    assert result.data["confidence"] > 0.7

    # Check sun → nucleus mapping
    sun_mapping = next(
        (a for a in result.data["analogies"] if a["source"] == "sun"),
        None
    )
    assert sun_mapping is not None
    assert sun_mapping["target"] == "nucleus"
    assert sun_mapping["type"] == "structural"  # High structural similarity
```

---

## Acceptance Criteria

- [ ] **Thought nodes** (5): analogical, causal, counterfactual, abductive, metacognitive
- [ ] **Action nodes** (5): plan_generation, plan_execution, action_selection, goal_refinement, constraint_satisfaction
- [ ] **Decision nodes** (3): multi_criteria_decision, risk_assessment, utility_maximization
- [ ] **Awareness nodes** (2): self_monitoring, performance_evaluation
- [ ] All nodes registered in registry with proper categories
- [ ] Unit tests for each node (>90% coverage)
- [ ] Integration tests for multi-node pipelines
- [ ] Documentation for each node's algorithm
- [ ] Performance benchmarks (<200ms per node)

---

## Monitoring

```promql
# Node execution counts by category
sum by (category) (orchestrator_node_executions_total)

# Slowest nodes
topk(10, orchestrator_node_duration_ms)
```

---

**Estimated Completion**: 20-24 hours (Large effort)
**PR Target**: Ready for review within 1 week
**Critical Path**: Enables complete MATRIZ cognitive loops

