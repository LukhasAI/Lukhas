"""
LUKHAS AI Colony System - Reasoning Colony
Distributed reasoning and logic processing
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

from typing import Any, Dict, List, Optional

from .base import BaseColony, ColonyAgent, ColonyRole, ColonyTask


class ReasoningColony(BaseColony):
    """Colony for reasoning and logical inference"""

    def __init__(self, max_agents: int = 12):
        self.reasoning_cache = {}
        self.inference_rules = []
        super().__init__("reasoning", max_agents)

        # Add specialized reasoning agents
        self._add_reasoning_specialists()
        self._load_default_rules()

    def _add_reasoning_specialists(self):
        """Add specialized reasoning agents"""
        # Causal reasoning specialist
        causal_agent = ColonyAgent(
            role=ColonyRole.SPECIALIST,
            capabilities=[
                "causal_inference",
                "pattern_recognition",
                "temporal_reasoning",
            ],
            metadata={"specialization": "causal_reasoning"},
        )
        self.agents[causal_agent.id] = causal_agent

        # Logic specialist
        logic_agent = ColonyAgent(
            role=ColonyRole.SPECIALIST,
            capabilities=[
                "deductive_reasoning",
                "inductive_reasoning",
                "logical_validation",
            ],
            metadata={"specialization": "formal_logic"},
        )
        self.agents[logic_agent.id] = logic_agent

        # Abstract reasoning specialist
        abstract_agent = ColonyAgent(
            role=ColonyRole.SPECIALIST,
            capabilities=["abstract_reasoning", "concept_mapping", "analogy_detection"],
            metadata={"specialization": "abstract_reasoning"},
        )
        self.agents[abstract_agent.id] = abstract_agent

    def _load_default_rules(self):
        """Load default inference rules"""
        self.inference_rules = [
            {
                "name": "transitivity",
                "pattern": "if A->B and B->C then A->C",
                "type": "deductive",
            },
            {
                "name": "modus_ponens",
                "pattern": "if P->Q and P then Q",
                "type": "deductive",
            },
            {
                "name": "pattern_induction",
                "pattern": "if pattern P observed N times then likely P continues",
                "type": "inductive",
            },
        ]

    def get_default_capabilities(self) -> List[str]:
        """Default capabilities for reasoning agents"""
        return [
            "logical_inference",
            "pattern_analysis",
            "causal_reasoning",
            "hypothesis_testing",
            "argument_validation",
        ]

    def process_task(self, task: ColonyTask) -> Any:
        """Process reasoning task"""
        task_type = task.task_type
        payload = task.payload

        if task_type == "logical_inference":
            return self._perform_logical_inference(payload)
        elif task_type == "causal_analysis":
            return self._analyze_causality(payload)
        elif task_type == "pattern_recognition":
            return self._recognize_patterns(payload)
        elif task_type == "hypothesis_testing":
            return self._test_hypothesis(payload)
        elif task_type == "argument_validation":
            return self._validate_argument(payload)
        elif task_type == "concept_mapping":
            return self._map_concepts(payload)
        else:
            return {"status": "unknown_task_type", "task_type": task_type}

    def _perform_logical_inference(self, premises: Dict[str, Any]) -> Dict[str, Any]:
        """Perform logical inference from premises"""
        facts = premises.get("facts", [])
        rules = premises.get("rules", [])
        query = premises.get("query", "")

        result = {
            "query": query,
            "conclusion": None,
            "confidence": 0.0,
            "reasoning_steps": [],
            "rule_applications": [],
        }

        # Simple inference engine
        derived_facts = set(facts)
        reasoning_steps = []

        # Apply rules iteratively
        max_iterations = 10
        for iteration in range(max_iterations):
            new_facts = set()

            for rule in rules + self.inference_rules:
                rule_name = rule.get("name", "unnamed_rule")

                # Apply transitivity rule
                if rule_name == "transitivity":
                    for fact1 in derived_facts:
                        for fact2 in derived_facts:
                            if self._matches_transitivity(fact1, fact2):
                                new_fact = self._apply_transitivity(fact1, fact2)
                                if new_fact and new_fact not in derived_facts:
                                    new_facts.add(new_fact)
                                    reasoning_steps.append(
                                        f"Applied transitivity: {fact1} + {fact2} -> {new_fact}"
                                    )

                # Apply modus ponens
                elif rule_name == "modus_ponens":
                    for fact in derived_facts:
                        for implication in derived_facts:
                            if self._matches_modus_ponens(fact, implication):
                                new_fact = self._apply_modus_ponens(fact, implication)
                                if new_fact and new_fact not in derived_facts:
                                    new_facts.add(new_fact)
                                    reasoning_steps.append(
                                        f"Applied modus ponens: {fact} + {implication} -> {new_fact}"
                                    )

            if not new_facts:
                break

            derived_facts.update(new_facts)

        # Check if query can be answered
        if query in derived_facts:
            result["conclusion"] = True
            result["confidence"] = 0.9
        elif any(query in fact for fact in derived_facts):
            result["conclusion"] = "partially_derived"
            result["confidence"] = 0.6
        else:
            result["conclusion"] = False
            result["confidence"] = 0.1

        result["reasoning_steps"] = reasoning_steps
        result["derived_facts"] = list(derived_facts)

        return result

    def _matches_transitivity(self, fact1: str, fact2: str) -> bool:
        """Check if two facts match transitivity pattern"""
        # Simple pattern matching for A->B and B->C
        if "->" in fact1 and "->" in fact2:
            parts1 = fact1.split("->")
            parts2 = fact2.split("->")
            if len(parts1) == 2 and len(parts2) == 2:
                return parts1[1].strip() == parts2[0].strip()
        return False

    def _apply_transitivity(self, fact1: str, fact2: str) -> Optional[str]:
        """Apply transitivity rule"""
        if "->" in fact1 and "->" in fact2:
            parts1 = fact1.split("->")
            parts2 = fact2.split("->")
            if len(parts1) == 2 and len(parts2) == 2:
                return f"{parts1[0].strip()}->{parts2[1].strip()}"
        return None

    def _matches_modus_ponens(self, fact: str, implication: str) -> bool:
        """Check if fact and implication match modus ponens pattern"""
        if "->" in implication:
            antecedent = implication.split("->")[0].strip()
            return fact.strip() == antecedent
        return False

    def _apply_modus_ponens(self, fact: str, implication: str) -> Optional[str]:
        """Apply modus ponens rule"""
        if "->" in implication:
            consequent = implication.split("->")[1].strip()
            return consequent
        return None

    def _analyze_causality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze causal relationships"""
        events = data.get("events", [])

        result = {
            "causal_chains": [],
            "strength": {},
            "temporal_order": [],
            "confidence": 0.5,
        }

        # Simple temporal ordering
        sorted_events = sorted(events, key=lambda e: e.get("timestamp", 0))
        result["temporal_order"] = [e.get("name", "unknown") for e in sorted_events]

        # Identify potential causal chains
        for i, event1 in enumerate(sorted_events[:-1]):
            for event2 in sorted_events[i + 1 :]:
                # Simple causal strength based on temporal proximity
                time_diff = event2.get("timestamp", 0) - event1.get("timestamp", 0)
                if 0 < time_diff < 3600:  # Within 1 hour
                    strength = max(0, 1.0 - (time_diff / 3600))
                    chain = f"{event1.get('name', 'unknown')}->{event2.get('name', 'unknown')}"
                    result["causal_chains"].append(chain)
                    result["strength"][chain] = strength

        return result

    def _recognize_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recognize patterns in data"""
        sequence = data.get("sequence", [])

        result = {"patterns": [], "repetitions": {}, "anomalies": [], "confidence": 0.0}

        # Find repeating subsequences
        for length in range(2, min(len(sequence) // 2 + 1, 6)):
            for start in range(len(sequence) - length * 2 + 1):
                pattern = sequence[start : start + length]

                # Look for repetitions
                repetitions = 0
                for i in range(start + length, len(sequence) - length + 1, length):
                    if sequence[i : i + length] == pattern:
                        repetitions += 1

                if repetitions > 0:
                    pattern_str = str(pattern)
                    result["patterns"].append(pattern_str)
                    result["repetitions"][pattern_str] = repetitions + 1

        # Simple anomaly detection (items that appear infrequently)
        item_counts = {}
        for item in sequence:
            item_counts[item] = item_counts.get(item, 0) + 1

        avg_frequency = len(sequence) / len(item_counts) if item_counts else 0
        for item, count in item_counts.items():
            if count < avg_frequency * 0.3:  # Less than 30% of average
                result["anomalies"].append(item)

        result["confidence"] = min(len(result["patterns"]) * 0.2, 1.0)

        return result

    def _test_hypothesis(self, hypothesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a hypothesis against evidence"""
        hypothesis = hypothesis_data.get("hypothesis", "")
        evidence = hypothesis_data.get("evidence", [])

        result = {
            "hypothesis": hypothesis,
            "support_score": 0.0,
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "conclusion": "insufficient_evidence",
        }

        # Simple evidence evaluation
        supporting = 0
        contradicting = 0

        for item in evidence:
            relevance = item.get("relevance", 0.5)
            supports = item.get("supports_hypothesis", None)

            if supports is True:
                supporting += relevance
                result["supporting_evidence"].append(item)
            elif supports is False:
                contradicting += relevance
                result["contradicting_evidence"].append(item)

        total_evidence = supporting + contradicting
        if total_evidence > 0:
            result["support_score"] = supporting / total_evidence

            if result["support_score"] > 0.8:
                result["conclusion"] = "strongly_supported"
            elif result["support_score"] > 0.6:
                result["conclusion"] = "supported"
            elif result["support_score"] < 0.2:
                result["conclusion"] = "contradicted"
            else:
                result["conclusion"] = "inconclusive"

        return result

    def _validate_argument(self, argument: Dict[str, Any]) -> Dict[str, Any]:
        """Validate logical structure of argument"""
        premises = argument.get("premises", [])
        conclusion = argument.get("conclusion", "")

        result = {"valid": False, "sound": False, "fallacies": [], "strength": 0.0}

        # Basic validation checks
        if not premises:
            result["fallacies"].append("No premises provided")
            return result

        if not conclusion:
            result["fallacies"].append("No conclusion provided")
            return result

        # Check for common fallacies
        premise_text = " ".join(premises).lower()
        conclusion_text = conclusion.lower()

        # Ad hominem detection
        if any(word in premise_text for word in ["stupid", "idiot", "moron"]):
            result["fallacies"].append("Potential ad hominem attack")

        # Circular reasoning detection
        if conclusion_text in premise_text:
            result["fallacies"].append("Potential circular reasoning")

        # Simple validity check (premises support conclusion)
        support_words = ["therefore", "thus", "hence", "because"]
        if any(word in premise_text for word in support_words):
            result["strength"] += 0.3

        # Check if conclusion follows from premises (simplified)
        common_terms = set(premise_text.split()) & set(conclusion_text.split())
        if len(common_terms) > 2:
            result["strength"] += 0.4

        result["valid"] = len(result["fallacies"]) == 0 and result["strength"] > 0.5
        result["sound"] = result["valid"]  # Simplified: assume true premises

        return result

    def _map_concepts(self, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map relationships between concepts"""
        concepts = concept_data.get("concepts", [])

        result = {
            "concept_map": {},
            "relationships": [],
            "hierarchies": [],
            "similarity_scores": {},
        }

        # Create simple concept map
        for concept in concepts:
            name = concept.get("name", "")
            attributes = concept.get("attributes", [])

            result["concept_map"][name] = {
                "attributes": attributes,
                "related_concepts": [],
            }

        # Find relationships based on shared attributes
        concept_names = list(result["concept_map"].keys())
        for i, concept1 in enumerate(concept_names):
            for concept2 in concept_names[i + 1 :]:
                attrs1 = set(result["concept_map"][concept1]["attributes"])
                attrs2 = set(result["concept_map"][concept2]["attributes"])

                shared = attrs1 & attrs2
                if shared:
                    similarity = len(shared) / len(attrs1 | attrs2)
                    result["similarity_scores"][f"{concept1}-{concept2}"] = similarity

                    if similarity > 0.3:
                        result["relationships"].append(
                            {
                                "concept1": concept1,
                                "concept2": concept2,
                                "type": "similar",
                                "strength": similarity,
                                "shared_attributes": list(shared),
                            }
                        )

                        result["concept_map"][concept1]["related_concepts"].append(
                            concept2
                        )
                        result["concept_map"][concept2]["related_concepts"].append(
                            concept1
                        )

        return result


# Create singleton reasoning colony
_reasoning_colony = None


def get_reasoning_colony() -> ReasoningColony:
    """Get or create reasoning colony singleton"""
    global _reasoning_colony
    if _reasoning_colony is None:
        _reasoning_colony = ReasoningColony()

        # Register with global registry
        from .base import get_colony_registry

        registry = get_colony_registry()
        registry.register_colony(_reasoning_colony)

        # Set up task routing
        registry.add_task_route("logical_inference", "reasoning")
        registry.add_task_route("causal_analysis", "reasoning")
        registry.add_task_route("pattern_recognition", "reasoning")
        registry.add_task_route("hypothesis_testing", "reasoning")
        registry.add_task_route("argument_validation", "reasoning")
        registry.add_task_route("concept_mapping", "reasoning")

    return _reasoning_colony
