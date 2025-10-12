"""

#TAG:core
#TAG:symbolic
#TAG:neuroplastic
#TAG:colony

Enhanced Core TypeScript - Integrated from Advanced Systems
Original: semantic_reasoner.py
Advanced: semantic_reasoner.py
Integration Date: 2025-05-31T07:55:28.221604
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from .symbolic_core import SymbolicWorld  # Added import

logger = logging.getLogger(__name__)


class SymbolicReasoningEngine:
    """
    Implements pure symbolic reasoning to establish relationships between events and actions.
    This is a lightweight engine with minimized computational overhead, emphasizing
    explainability and ethical alignment.

    Inspired by Steve Jobs' focus on simplicity and Sam Altman's emphasis on
    ethical AI alignment.
    """

    def __init__(self, symbolic_world: Optional[SymbolicWorld] = None):  # Modified __init__
        self.reasoning_graph = {}
        self.confidence_threshold = 0.8  # Higher threshold for precision
        self.max_reasoning_depth = 3  # Limited depth for efficiency
        self.reasoning_history = []
        self.symbolic_rules = {
            "causation": [
                "because",
                "cause",
                "reason",
                "due to",
                "results in",
                "leads to",
                "produces",
            ],
            "correlation": [
                "associated with",
                "linked to",
                "related to",
                "connected with",
            ],
            "conditional": [
                "if",
                "when",
                "assuming",
                "provided that",
                "unless",
            ],
            "temporal": ["before", "after", "during", "while", "since"],
            "logical": [
                "and",
                "or",
                "not",
                "implies",
                "equivalent",
                "therefore",
            ],
        }
        self.symbolic_world = symbolic_world  # Store symbolic_world instance

    def _sanitize_for_symbol_name(self, text: str) -> str:  # Added helper method
        """Cleans and formats text to be a valid symbol name."""
        if not text:
            return ""
        # Replace common separators with underscore, remove problematic chars
        name = text.replace(" ", "_").replace(":", "").replace("→", "to").replace("-", "_")
        # Keep only alphanumeric characters and underscores
        name = "".join(e for e in name if e.isalnum() or e == "_")
        # Convert to lowercase and truncate
        return name.lower()[:80]  # Max length for symbol name, increased for clarity

    def reason(self, data: dict) -> dict:
        """
        Apply pure symbolic reasoning to input data and optionally populate SymbolicWorld.

        Args:
            data: Data that requires reasoning

        Returns:
            Dict containing reasoning results and logical chains
        """
        # Extract content from data with focus on symbolic patterns
        semantic_content = self._extract_semantic_content(data)
        symbolic_content = self._extract_symbolic_patterns(data)
        contextual_content = self._extract_contextual_content(data)

        # Identify logical elements with priority on symbolic patterns
        logical_elements = self._extract_logical_elements(semantic_content, symbolic_content, contextual_content)

        # Build logical chains using symbolic structures
        logical_chains = self._build_symbolic_logical_chains(logical_elements)

        # Apply symbolic logic for confidence calculation
        weighted_logic = self._calculate_symbolic_confidences(logical_chains)

        # Filter by confidence threshold
        valid_logic = {k: v for k, v in weighted_logic.items() if v["confidence"] >= self.confidence_threshold}

        # Update internal reasoning graph
        if valid_logic:
            self._update_reasoning_graph(valid_logic)

        # Prepare reasoning results with symbolic structure
        reasoning_results = {
            "logical_chains": valid_logic,
            "primary_conclusion": (self._identify_primary_conclusion(valid_logic) if valid_logic else None),
            "confidence": (max([v["confidence"] for v in valid_logic.values()]) if valid_logic else 0.0),
            "reasoning_path": self._extract_symbolic_reasoning_path(valid_logic),
            "symbolic_structure": self._extract_symbolic_structure(valid_logic),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Add to history
        self._update_history(reasoning_results)

        # Populate SymbolicWorld if an instance is provided and a conclusion is reached
        if self.symbolic_world and reasoning_results.get("primary_conclusion"):
            conclusion_data = reasoning_results["primary_conclusion"]
            if conclusion_data and conclusion_data.get("summary"):
                symbol_name = self._sanitize_for_symbol_name(conclusion_data["summary"])

                if symbol_name:  # Ensure a valid name was generated
                    props = {
                        "type": "derived_conclusion",
                        "source_engine": self.__class__.__name__,
                        "original_summary": conclusion_data["summary"],  # Store original summary
                        "confidence": conclusion_data["confidence"],
                        "relation_type_hint": conclusion_data.get("relation_type", "unknown"),
                        "last_derived_timestamp": reasoning_results["timestamp"],
                    }

                    if symbol_name not in self.symbolic_world.symbols:
                        self.symbolic_world.create_symbol(symbol_name, props)
                    else:
                        # Symbol exists, update its properties
                        existing_symbol = self.symbolic_world.symbols[symbol_name]
                        for key, value in props.items():
                            existing_symbol.update_property(key, value)

        return reasoning_results

    def _extract_semantic_content(self, data: dict) -> str:
        """Extract semantic content from input data"""
        if "text" in data:
            return data["text"]
        elif "content" in data:
            return data["content"].get("text", "")
        return ""

    def _extract_symbolic_patterns(self, data: dict) -> dict:
        """Extract symbolic patterns from input data"""
        patterns = {}

        # Extract from semantic content
        text = self._extract_semantic_content(data)

        # Detect logical operators
        patterns["logical_operators"] = any(
            op in text.lower() for op in ["if", "then", "and", "or", "not", "therefore"]
        )

        # Detect categorical structures
        patterns["categorical"] = any(
            cat in text.lower() for cat in ["is a", "type of", "category", "class", "belongs to"]
        )

        # Detect quantifiers
        patterns["quantifiers"] = any(
            q in text.lower() for op in ["all", "some", "none", "every", "any", "few", "many"]  # noqa: F821
        )

        # Check for formal logic structures
        patterns["formal_logic"] = self._detect_formal_logic(text)

        return patterns

    def _detect_formal_logic(self, text: str) -> dict:
        """Detect formal logic structures in text"""
        logic = {}

        # Check for conditional statements (if-then)
        if "if" in text.lower() and "then" in text.lower():
            logic["conditional"] = True

        # Check for universal/existential quantifiers
        if any(q in text.lower() for q in ["all", "every", "any", "for all"]):
            logic["universal"] = True
        if any(q in text.lower() for q in ["some", "exists", "there is", "at least one"]):
            logic["existential"] = True

        # Check for negation
        if any(
            n in text.lower()
            for n in [
                "not",
                "no",
                "never",
                "doesn't",
                "isn't",
                "aren't",
                "won't",
            ]
        ):
            logic["negation"] = True

        # Check for conjunction/disjunction
        if " and " in text.lower():
            logic["conjunction"] = True
        if " or " in text.lower():
            logic["disjunction"] = True

        return logic

    def _extract_contextual_content(self, data: dict) -> dict:
        """Extract contextual content from input data"""
        if "context" in data:
            return data["context"]
        return {}

    def _extract_logical_elements(
        self,
        semantic_content: str,
        symbolic_content: dict,
        contextual_content: dict,
    ) -> list[dict]:
        """Extract logical elements with priority on symbolic patterns"""
        logical_elements = []

        # First priority: Extract from symbolic patterns
        if symbolic_content:
            # Process logical operators
            if symbolic_content.get("logical_operators", False):
                logical_elements.append(
                    {
                        "type": "symbolic_logical",
                        "content": "Logical relation detected",
                        "base_confidence": 0.9,  # High confidence for symbolic relations
                        "relation_type": "logical",
                    }
                )

            # Process categorical structures
            if symbolic_content.get("categorical", False):
                logical_elements.append(
                    {
                        "type": "symbolic_categorical",
                        "content": "Categorical relation detected",
                        "base_confidence": 0.85,
                        "relation_type": "categorical",
                    }
                )

            # Process quantifiers
            if symbolic_content.get("quantifiers", False):
                logical_elements.append(
                    {
                        "type": "symbolic_quantifier",
                        "content": "Quantifier relation detected",
                        "base_confidence": 0.85,
                        "relation_type": "quantifier",
                    }
                )

            # Process formal logic
            formal_logic = symbolic_content.get("formal_logic", {})
            for logic_type, present in formal_logic.items():
                if present:
                    logical_elements.append(
                        {
                            "type": f"formal_logic_{logic_type}",
                            "content": f"{logic_type.capitalize()} logical structure detected",
                            "base_confidence": 0.95,  # Very high confidence for formal logic
                            "relation_type": "formal_logic",
                        }
                    )

        # Second priority: Extract from semantic content with symbolic patterns
        if semantic_content and isinstance(semantic_content, str):
            # Look for logical markers using symbolic rules
            for rule_type, markers in self.symbolic_rules.items():
                for marker in markers:
                    if marker in semantic_content.lower():
                        # Extract the sentence containing the marker
                        sentences = semantic_content.split(".")
                        for sentence in sentences:
                            if marker in sentence.lower():
                                logical_elements.append(
                                    {
                                        "type": f"semantic_{rule_type}",
                                        "content": sentence.strip(),
                                        "base_confidence": 0.8,
                                        "relation_type": rule_type,
                                    }
                                )

        # Extract from contextual content
        if contextual_content and isinstance(contextual_content, dict):
            # Process key contextual elements
            for key, value in contextual_content.items():
                if key in [
                    "goal",
                    "constraint",
                    "condition",
                    "requirement",
                    "rule",
                    "priority",
                ]:
                    logical_elements.append(
                        {
                            "type": "contextual",
                            "content": f"Context {key}: {value}",
                            "base_confidence": 0.75,
                            "relation_type": "contextual",
                        }
                    )

        return logical_elements

    def _build_symbolic_logical_chains(self, logical_elements: list[dict]) -> dict:
        """Build logical chains using symbolic structures"""
        logical_chains = {}

        # Group by relation type for symbolic processing
        relation_groups = {}
        for item in logical_elements:
            rel_type = item.get("relation_type", "unknown")
            if rel_type not in relation_groups:
                relation_groups[rel_type] = []
            relation_groups[rel_type].append(item)

        # Process each relation type to build chains
        chain_id_counter = 0
        for rel_type, items in relation_groups.items():
            # Create initial chain for this relation type
            chain_id = f"chain_{chain_id_counter}"
            chain_id_counter += 1

            if items:
                logical_chains[chain_id] = {
                    "elements": items.copy(),
                    "base_confidence": max(item["base_confidence"] for item in items),
                    "relation_type": rel_type,
                }

                # Look for cross-type relations that strengthen this chain
                for other_type, other_items in relation_groups.items():
                    if other_type != rel_type:
                        # Check for semantic overlap between first item in this chain
                        # and other items
                        for other_item in other_items:
                            if any(self._check_semantic_overlap(item, other_item) for item in items):
                                logical_chains[chain_id]["elements"].append(other_item)
                                # Strengthen confidence due to cross-domain evidence
                                logical_chains[chain_id]["base_confidence"] = min(
                                    0.95,
                                    logical_chains[chain_id]["base_confidence"] + 0.05,
                                )

        return logical_chains

    def _check_semantic_overlap(self, item1: dict, item2: dict) -> bool:
        """Check for semantic overlap between two items"""
        if not isinstance(item1.get("content"), str) or not isinstance(item2.get("content"), str):
            return False

        content1 = item1["content"].lower()
        content2 = item2["content"].lower()

        # Check for direct word overlap (simplified semantic matching)
        words1 = set(content1.split())
        words2 = set(content2.split())
        common_words = words1.intersection(words2)

        # Calculate overlap ratio
        if len(words1) > 0 and len(words2) > 0:
            overlap_ratio = len(common_words) / min(len(words1), len(words2))
            return overlap_ratio > 0.3  # 30% overlap threshold

        return False

    def _calculate_symbolic_confidences(self, logical_chains: dict) -> dict:
        """Calculate confidence levels using symbolic logic"""
        weighted_logic = {}

        for chain_id, chain in logical_chains.items():
            # Base confidence from the chain
            base_confidence = chain["base_confidence"]

            # Apply symbolic confidence rules

            # Rule 1: Multiple elements of the same type strengthen confidence
            elements_by_type = {}
            for elem in chain["elements"]:
                elem_type = elem["type"]
                if elem_type not in elements_by_type:
                    elements_by_type[elem_type] = []
                elements_by_type[elem_type].append(elem)

            # Calculate type diversity score
            type_count = len(elements_by_type)
            type_diversity_bonus = min(0.1, 0.03 * type_count)

            # Rule 2: Symbolic types have higher weight
            symbolic_types = sum(1 for t in elements_by_type if "symbolic" in t or "formal_logic" in t)
            symbolic_bonus = min(0.15, 0.05 * symbolic_types)

            # Rule 3: More elements in high-confidence types increase confidence
            evidence_strength = 0
            for elem_type, elems in elements_by_type.items():
                if ("symbolic" in elem_type or "formal_logic" in elem_type) and len(elems) > 1:
                    evidence_strength += 0.05 * min(3, len(elems))

            # Calculate final confidence with caps
            final_confidence = min(
                0.99,
                base_confidence + type_diversity_bonus + symbolic_bonus + evidence_strength,
            )

            weighted_logic[chain_id] = {
                "elements": chain["elements"][:3],  # Limit elements stored for efficiency
                "confidence": final_confidence,
                "relation_type": chain.get("relation_type", "unknown"),
                "summary": self._create_symbolic_summary(chain["elements"], chain.get("relation_type", "unknown")),
            }

        return weighted_logic

    def _create_symbolic_summary(self, elements: list[dict], relation_type: str) -> str:
        """Create a symbolic summary of a logical chain"""
        if not elements:
            return ""

        # Different summary formats based on relation type
        if relation_type == "logical":
            # Format like a logical statement
            return "Logical relationship: " + " AND ".join([e["content"] for e in elements[:2]])
        elif relation_type == "formal_logic":
            # Format with formal logic notation
            contents = [e["content"] for e in elements[:2]]
            return f"Formal logic: {' ∧ '.join(contents)}"
        elif relation_type == "conditional":
            # Format as if-then
            if len(elements) >= 2:
                return f"IF {elements[0]['content']} THEN {elements[1]['content']}"
            else:
                return elements[0]["content"]
        elif relation_type == "causation":
            # Format as cause -> effect
            if len(elements) >= 2:
                return f"Cause: {elements[0]['content']} → Effect: {elements[1]['content']}"
            else:
                return elements[0]["content"]
        else:
            # Generic format for other types
            return " • ".join([e["content"] for e in elements[:3]])

    def _update_reasoning_graph(self, valid_logic: dict) -> None:
        """Update the internal reasoning graph"""
        timestamp = datetime.now(timezone.utc).isoformat()

        for chain_id, chain_data in valid_logic.items():
            relation_type = chain_data.get("relation_type", "unknown")
            confidence = chain_data["confidence"]

            # Create a memory-efficient representation
            entry_key = f"{relation_type}_{chain_id[-5:]}"

            if entry_key not in self.reasoning_graph:
                self.reasoning_graph[entry_key] = {
                    "first_seen": timestamp,
                    "last_seen": timestamp,
                    "frequency": 1,
                    "avg_confidence": confidence,
                    "relation_type": relation_type,
                }
            else:
                # Update existing entry
                entry = self.reasoning_graph[entry_key]
                entry["frequency"] += 1
                entry["last_seen"] = timestamp
                # Running average of confidence
                entry["avg_confidence"] = (entry["avg_confidence"] * (entry["frequency"] - 1) + confidence) / entry[
                    "frequency"
                ]

        # Limit reasoning graph size by pruning oldest and least frequent entries
        if len(self.reasoning_graph) > 30:  # Reduced size limit for efficiency
            # Sort by frequency and recency
            sorted_entries = sorted(
                self.reasoning_graph.items(),
                key=lambda x: (x[1]["frequency"], x[1]["last_seen"]),
                reverse=True,
            )
            # Keep only top entries
            self.reasoning_graph = dict(sorted_entries[:30])

    def _identify_primary_conclusion(self, valid_logic: dict) -> dict:
        """Identify the most likely primary conclusion"""
        if not valid_logic:
            return None

        # Prioritize by relation type and confidence
        priority_order = {
            "formal_logic": 5,
            "logical": 4,
            "conditional": 3,
            "causation": 2,
            "correlation": 1,
            "temporal": 0,
        }

        # Score each logical chain
        scored_logic = {}
        for logic_id, logic_data in valid_logic.items():
            relation_type = logic_data.get("relation_type", "unknown")
            relation_priority = priority_order.get(relation_type, 0)
            confidence = logic_data["confidence"]

            # Combined score
            score = (relation_priority * 0.2) + confidence
            scored_logic[logic_id] = score

        # Get highest score
        primary_logic_id = max(scored_logic.keys(), key=lambda k: scored_logic[k])
        logic_data = valid_logic[primary_logic_id]

        return {
            "id": primary_logic_id,
            "summary": logic_data["summary"],
            "confidence": logic_data["confidence"],
            "relation_type": logic_data.get("relation_type", "unknown"),
        }

    def _extract_symbolic_reasoning_path(self, valid_logic: dict) -> list[dict]:
        """Extract a symbolic reasoning path that shows logical structure"""
        reasoning_steps = []

        # Group by relation type
        grouped_logic = {}
        for logic_id, logic_data in valid_logic.items():
            rel_type = logic_data.get("relation_type", "unknown")
            if rel_type not in grouped_logic:
                grouped_logic[rel_type] = []
            grouped_logic[rel_type].append((logic_id, logic_data))

        # Add steps in order of relation type importance
        priority_order = [
            "formal_logic",
            "logical",
            "conditional",
            "causation",
            "correlation",
            "temporal",
            "unknown",
        ]
        step_counter = 1

        for rel_type in priority_order:
            if rel_type in grouped_logic:
                for logic_id, logic_data in grouped_logic[rel_type]:
                    reasoning_steps.append(
                        {
                            "step": step_counter,
                            "type": rel_type,
                            "content": logic_data["summary"],
                            "confidence": logic_data["confidence"],
                        }
                    )
                    step_counter += 1

        # Limit to most relevant steps
        return reasoning_steps[:3]

    def _extract_symbolic_structure(self, valid_logic: dict) -> dict:
        """Extract symbolic structure from reasoning results"""
        if not valid_logic:
            return {"type": "unknown", "structure": None}

        # Count relation types
        relation_counts = {}
        for logic_data in valid_logic.values():
            rel_type = logic_data.get("relation_type", "unknown")
            relation_counts[rel_type] = relation_counts.get(rel_type, 0) + 1

        # Determine dominant structure type
        if relation_counts:
            dominant_type = max(relation_counts.items(), key=lambda x: x[1])[0]

            # Create appropriate structure
            if dominant_type == "logical" or dominant_type == "formal_logic":
                return {
                    "type": dominant_type,
                    "structure": "logical_structure",
                    "elements": len(relation_counts),
                }
            elif dominant_type == "conditional":
                return {
                    "type": "conditional",
                    "structure": "if_then_structure",
                    "elements": len(relation_counts),
                }
            elif dominant_type == "causation":
                return {
                    "type": "causal",
                    "structure": "causal_chain",
                    "elements": len(relation_counts),
                }
            else:
                return {
                    "type": dominant_type,
                    "structure": "generic",
                    "elements": len(relation_counts),
                }

        return {"type": "unknown", "structure": None}

    def _update_history(self, reasoning_results: dict) -> None:
        """Update reasoning history with minimal footprint"""
        # Only store essential information
        self.reasoning_history.append(
            {
                "timestamp": reasoning_results["timestamp"],
                "primary_conclusion_type": reasoning_results.get("primary_conclusion", {}).get(
                    "relation_type", "unknown"
                ),
                "confidence": reasoning_results.get("confidence", 0),
            }
        )

        # Limit history size
        self.reasoning_history = self.reasoning_history[-30:]  # Limited to last 30 for efficiency
