#!/usr/bin/env python3
"""
MATRIZ Factual Knowledge Retrieval Node

A production-ready cognitive node for factual knowledge retrieval that provides:
- Built-in knowledge base with common facts
- Fuzzy matching for flexible queries
- Confidence scoring based on certainty and match quality
- Complete MATRIZ format node emission
- Graceful "I don't know" handling
- Full traceability and audit support

This node handles factual questions about geography, history, science, and general knowledge.
All responses include confidence scoring and complete provenance tracking.
"""
from typing import List
from typing import Dict
import streamlit as st

import difflib
import re
import time
from typing import Any, Optional

from ..core.node_interface import (
    CognitiveNode,
    NodeState,
    NodeTrigger,
)


class FactNode(CognitiveNode):
    """
    Production-ready factual knowledge retrieval node for MATRIZ-AGI system.

    Features:
    - Comprehensive built-in knowledge base
    - Fuzzy string matching for flexible queries
    - Confidence scoring based on match quality and fact certainty
    - Graceful handling of unknown questions
    - Complete MATRIZ format node emission
    - Full audit trail and traceability

    Knowledge Categories:
    - World capitals and geography
    - Historical dates and events
    - Scientific facts and constants
    - Mathematical constants and definitions
    - Common general knowledge
    """

    def __init__(self, tenant: str = "default"):
        """
        Initialize the factual knowledge node.

        Args:
            tenant: Tenant identifier for multi-tenancy
        """
        super().__init__(
            node_name="matriz_fact_node",
            capabilities=[
                "factual_knowledge_retrieval",
                "geographic_information",
                "historical_facts",
                "scientific_knowledge",
                "general_knowledge_qa",
                "confidence_assessment",
            ],
            tenant=tenant,
        )

        # Initialize knowledge base
        self.knowledge_base = self._build_knowledge_base()

        # Fuzzy matching threshold (0.0-1.0)
        self.match_threshold = 0.4

        # Confidence scoring weights
        self.confidence_weights = {
            "exact_match": 1.0,
            "high_similarity": 0.9,
            "medium_similarity": 0.7,
            "low_similarity": 0.5,
            "fact_certainty": 0.95,  # How certain we are about stored facts
            "fuzzy_penalty": 0.1,  # Penalty for fuzzy matches
        }

    def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process factual knowledge queries.

        Args:
            input_data: Dict containing:
                - 'question': Question to answer
                - 'trace_id': Optional execution trace ID
                - 'context': Optional additional context

        Returns:
            Dict containing:
                - 'answer': The factual answer or "I don't know" response
                - 'confidence': Confidence score (0.0-1.0)
                - 'matriz_node': Complete MATRIZ format node
                - 'processing_time': Processing duration in seconds
        """
        start_time = time.time()

        # Extract and validate input
        question = input_data.get("question", "").strip()
        trace_id = input_data.get("trace_id", self.get_deterministic_hash(input_data))
        context = input_data.get("context", {})

        # Create initial trigger
        trigger = NodeTrigger(
            event_type="factual_knowledge_request",
            timestamp=int(time.time() * 1000),
            effect="knowledge_retrieval",
        )

        if not question:
            return self._create_error_response("No question provided", input_data, trace_id, start_time, [trigger])

        # Clean and normalize the question
        normalized_question = self._normalize_question(question)

        # Search for answers in knowledge base
        search_results = self._search_knowledge_base(normalized_question)

        if search_results:
            # Found matches - return best match
            best_match = search_results[0]
            answer = best_match["answer"]
            confidence = best_match["confidence"]
            match_info = best_match["match_info"]

            # Create success state
            state = NodeState(
                confidence=confidence,
                salience=min(0.9, 0.4 + confidence * 0.5),  # Higher confidence = higher salience
                valence=0.7,  # Positive - found answer
                utility=0.8,  # High utility for factual information
                novelty=max(0.1, 1.0 - confidence),  # Lower confidence = higher novelty
                arousal=0.4,  # Moderate arousal for knowledge retrieval
            )

            # Create affirmation reflection
            reflection = self.create_reflection(
                reflection_type="affirmation",
                cause=f"Successfully retrieved factual knowledge: {match_info['match_type']} match",
                new_state={
                    "question": question,
                    "answer": answer,
                    "confidence": confidence,
                    "match_type": match_info["match_type"],
                    "similarity_score": match_info["similarity_score"],
                },
            )

            # Create MATRIZ node for successful knowledge retrieval
            matriz_node = self.create_matriz_node(
                node_type="MEMORY",
                state=state,
                trace_id=trace_id,
                triggers=[trigger],
                reflections=[reflection],
                additional_data={
                    "question": question,
                    "normalized_question": normalized_question,
                    "answer": answer,
                    "knowledge_category": match_info.get("category", "general"),
                    "match_type": match_info["match_type"],
                    "similarity_score": match_info["similarity_score"],
                    "fact_source": match_info.get("source", "built_in_knowledge"),
                    "retrieval_method": "fuzzy_search",
                    "context": context,
                    "deterministic_hash": self.get_deterministic_hash({"question": normalized_question}),
                },
            )

        else:
            # No matches found - return "I don't know" response
            answer = "I don't know the answer to that question."
            confidence = 0.1  # Low confidence for unknown answers

            # Create uncertainty state
            state = NodeState(
                confidence=confidence,
                salience=0.3,  # Moderate salience for unknown answers
                valence=-0.2,  # Slightly negative - couldn't help
                utility=0.2,  # Low utility - no answer provided
                novelty=0.8,  # High novelty - unknown question
                arousal=0.2,  # Low arousal for simple "don't know"
            )

            # Create regret reflection
            reflection = self.create_reflection(
                reflection_type="regret",
                cause="Could not find answer in knowledge base",
                new_state={
                    "question": question,
                    "answer": answer,
                    "confidence": confidence,
                    "search_attempted": True,
                },
            )

            # Create MATRIZ node for unknown answer
            matriz_node = self.create_matriz_node(
                node_type="MEMORY",
                state=state,
                trace_id=trace_id,
                triggers=[trigger],
                reflections=[reflection],
                additional_data={
                    "question": question,
                    "normalized_question": normalized_question,
                    "answer": answer,
                    "knowledge_category": "unknown",
                    "match_type": "no_match",
                    "similarity_score": 0.0,
                    "fact_source": "none",
                    "retrieval_method": "fuzzy_search",
                    "context": context,
                    "deterministic_hash": self.get_deterministic_hash({"question": normalized_question}),
                },
            )

        processing_time = time.time() - start_time

        return {
            "answer": answer,
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }

    def validate_output(self, output: dict[str, Any]) -> bool:
        """
        Validate the factual knowledge output.

        Validates:
        1. Required fields presence and types
        2. MATRIZ node schema compliance
        3. Knowledge retrieval result validity
        4. Confidence-answer consistency
        5. Processing metadata completeness

        Args:
            output: Output from process() method

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level fields
            required_fields = ["answer", "confidence", "matriz_node", "processing_time"]
            for field in required_fields:
                if field not in output:
                    return False

            # Validate field types
            if not isinstance(output["answer"], str):
                return False
            if not isinstance(output["confidence"], (int, float)):
                return False
            if not isinstance(output["processing_time"], (int, float)):
                return False

            # Validate confidence range
            confidence = output["confidence"]
            if not (0 <= confidence <= 1):
                return False

            # Validate MATRIZ node
            matriz_node = output["matriz_node"]
            if not self.validate_matriz_node(matriz_node):
                return False

            # Check node type is MEMORY
            if matriz_node.get("type") != "MEMORY":
                return False

            # Validate knowledge retrieval specific fields
            state = matriz_node.get("state", {})

            # Check for question in state
            if "question" not in state:
                return False

            # Validate answer consistency
            answer = output["answer"]
            if not answer or len(answer.strip()) == 0:
                return False

            # Check match type if present
            match_type = state.get("match_type")
            if match_type is not None:
                valid_match_types = [
                    "exact_match",
                    "high_similarity",
                    "medium_similarity",
                    "low_similarity",
                    "no_match",
                    "error",
                ]
                if match_type not in valid_match_types:
                    return False

            # Check similarity score if present
            similarity_score = state.get("similarity_score")
            if similarity_score is not None:
                if not isinstance(similarity_score, (int, float)):
                    return False
                if not (0 <= similarity_score <= 1):
                    return False

            # Validate confidence-answer consistency
            if answer == "I don't know the answer to that question.":
                # For "don't know" answers, confidence should be low
                if confidence > 0.3:
                    return False
            elif answer.startswith("Error:"):
                # For error answers, confidence should be very low
                if confidence > 0.2:
                    return False
            else:
                # For factual answers, confidence should be reasonable
                if confidence < 0.3:
                    return False

            # Validate provenance
            provenance = matriz_node.get("provenance", {})
            return not (
                "producer" not in provenance or "factual_knowledge_retrieval" not in provenance.get("capabilities", [])
            )

        except Exception:
            return False

    def _build_knowledge_base(self) -> dict[str, dict]:
        """
        Build the comprehensive factual knowledge base.

        Returns:
            Dict mapping questions/topics to factual answers with metadata
        """
        knowledge = {}

        # World Capitals
        capitals = {
            "what is the capital of france": {
                "answer": "The capital of France is Paris.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["france", "capital", "paris"],
            },
            "what is the capital of japan": {
                "answer": "The capital of Japan is Tokyo.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["japan", "capital", "tokyo"],
            },
            "what is the capital of italy": {
                "answer": "The capital of Italy is Rome.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["italy", "capital", "rome"],
            },
            "what is the capital of germany": {
                "answer": "The capital of Germany is Berlin.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["germany", "capital", "berlin"],
            },
            "what is the capital of spain": {
                "answer": "The capital of Spain is Madrid.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["spain", "capital", "madrid"],
            },
            "what is the capital of united kingdom": {
                "answer": "The capital of the United Kingdom is London.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["united kingdom", "uk", "britain", "capital", "london"],
            },
            "what is the capital of canada": {
                "answer": "The capital of Canada is Ottawa.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["canada", "capital", "ottawa"],
            },
            "what is the capital of australia": {
                "answer": "The capital of Australia is Canberra.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["australia", "capital", "canberra"],
            },
        }
        knowledge.update(capitals)

        # Historical Facts
        history = {
            "when did world war 2 end": {
                "answer": "World War 2 ended in 1945.",
                "category": "history",
                "certainty": 1.0,
                "keywords": ["world war 2", "ww2", "wwii", "end", "1945"],
            },
            "when did the berlin wall fall": {
                "answer": "The Berlin Wall fell on November 9, 1989.",
                "category": "history",
                "certainty": 1.0,
                "keywords": ["berlin wall", "fall", "1989", "november"],
            },
            "when was the declaration of independence signed": {
                "answer": "The Declaration of Independence was signed on July 4, 1776.",
                "category": "history",
                "certainty": 1.0,
                "keywords": ["declaration of independence", "signed", "1776", "july"],
            },
            "when did the titanic sink": {
                "answer": "The Titanic sank on April 15, 1912.",
                "category": "history",
                "certainty": 1.0,
                "keywords": ["titanic", "sink", "sank", "1912", "april"],
            },
        }
        knowledge.update(history)

        # Scientific Facts
        science = {
            "what is the speed of light": {
                "answer": "The speed of light in a vacuum is approximately 299,792,458 meters per second.",
                "category": "science",
                "certainty": 1.0,
                "keywords": [
                    "speed of light",
                    "light speed",
                    "meters per second",
                    "vacuum",
                ],
            },
            "how many planets are in our solar system": {
                "answer": "There are 8 planets in our solar system.",
                "category": "science",
                "certainty": 1.0,
                "keywords": ["planets", "solar system", "eight", "8"],
            },
            "what is the largest planet": {
                "answer": "Jupiter is the largest planet in our solar system.",
                "category": "science",
                "certainty": 1.0,
                "keywords": ["largest planet", "jupiter", "biggest planet"],
            },
            "what is the chemical symbol for gold": {
                "answer": "The chemical symbol for gold is Au.",
                "category": "science",
                "certainty": 1.0,
                "keywords": ["chemical symbol", "gold", "au", "element"],
            },
            "what is the chemical symbol for water": {
                "answer": "The chemical formula for water is H2O.",
                "category": "science",
                "certainty": 1.0,
                "keywords": ["chemical formula", "water", "h2o", "molecule"],
            },
        }
        knowledge.update(science)

        # Mathematical Facts
        math_facts = {
            "what is pi": {
                "answer": "Pi (π) is approximately 3.14159, representing the ratio of a circle's circumference to its diameter.",
                "category": "mathematics",
                "certainty": 1.0,
                "keywords": [
                    "pi",
                    "π",
                    "3.14159",
                    "circle",
                    "circumference",
                    "diameter",
                ],
            },
            "what is the square root of 144": {
                "answer": "The square root of 144 is 12.",
                "category": "mathematics",
                "certainty": 1.0,
                "keywords": ["square root", "144", "12", "sqrt"],
            },
        }
        knowledge.update(math_facts)

        # General Knowledge
        general = {
            "how many days are in a year": {
                "answer": "There are 365 days in a regular year and 366 days in a leap year.",
                "category": "general",
                "certainty": 1.0,
                "keywords": ["days", "year", "365", "366", "leap year"],
            },
            "how many continents are there": {
                "answer": "There are 7 continents: Asia, Africa, North America, South America, Antarctica, Europe, and Australia.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": [
                    "continents",
                    "seven",
                    "7",
                    "asia",
                    "africa",
                    "america",
                    "antarctica",
                    "europe",
                    "australia",
                ],
            },
            "what is the largest ocean": {
                "answer": "The Pacific Ocean is the largest ocean on Earth.",
                "category": "geography",
                "certainty": 1.0,
                "keywords": ["largest ocean", "pacific ocean", "biggest ocean"],
            },
        }
        knowledge.update(general)

        return knowledge

    def _normalize_question(self, question: str) -> str:
        """
        Normalize question for better matching.

        Args:
            question: Raw question string

        Returns:
            Normalized question string
        """
        # Convert to lowercase
        normalized = question.lower().strip()

        # Remove punctuation
        normalized = re.sub(r"[^\w\s]", "", normalized)

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized)

        # Only remove minimal stop words to preserve meaning
        minimal_stop_words = ["the", "a", "an"]
        words = normalized.split()
        filtered_words = [word for word in words if word not in minimal_stop_words]

        # If we filtered out too much, keep original
        if len(filtered_words) < 2 and len(words) > 2:
            return normalized

        return " ".join(filtered_words)

    def _search_knowledge_base(self, question: str) -> list[dict[str, Any]]:
        """
        Search knowledge base for answers using fuzzy matching.

        Args:
            question: Normalized question to search for

        Returns:
            List of matching results sorted by confidence
        """
        results = []

        for kb_question, kb_data in self.knowledge_base.items():
            # Calculate similarity scores
            exact_match = question == kb_question
            similarity_score = difflib.SequenceMatcher(None, question, kb_question).ratio()

            # Check keyword matches
            question_words = set(question.split())
            keyword_matches = sum(
                1
                for keyword in kb_data["keywords"]
                if any(keyword in word or word in keyword for word in question_words)
            )
            keyword_ratio = keyword_matches / len(kb_data["keywords"]) if kb_data["keywords"] else 0

            # Combine similarity scores with better weighting
            # Only use keyword matching if there's some baseline similarity
            if similarity_score >= 0.3 and keyword_ratio > 0:
                combined_score = max(similarity_score, keyword_ratio * 0.8)
            else:
                combined_score = similarity_score

            # Determine match type and confidence
            if exact_match:
                match_type = "exact_match"
                confidence = self.confidence_weights["exact_match"] * kb_data["certainty"]
            elif combined_score >= 0.7:
                match_type = "high_similarity"
                confidence = self.confidence_weights["high_similarity"] * kb_data["certainty"]
            elif combined_score >= 0.5:
                match_type = "medium_similarity"
                confidence = self.confidence_weights["medium_similarity"] * kb_data["certainty"]
            elif combined_score >= self.match_threshold:
                match_type = "low_similarity"
                confidence = self.confidence_weights["low_similarity"] * kb_data["certainty"]
            else:
                continue  # Below threshold, skip

            # Apply fuzzy penalty if not exact match (but less aggressive)
            if not exact_match:
                confidence -= self.confidence_weights["fuzzy_penalty"] * (1 - combined_score) * 0.5

            # Ensure confidence is in valid range
            confidence = max(0.1, min(1.0, confidence))

            results.append(
                {
                    "answer": kb_data["answer"],
                    "confidence": confidence,
                    "match_info": {
                        "match_type": match_type,
                        "similarity_score": combined_score,
                        "category": kb_data["category"],
                        "source": "built_in_knowledge",
                    },
                }
            )

        # Sort by confidence (highest first)
        results.sort(key=lambda x: x["confidence"], reverse=True)

        return results

    def _create_error_response(
        self,
        error_message: str,
        input_data: dict[str, Any],
        trace_id: str,
        start_time: float,
        triggers: list[NodeTrigger],
        question: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create standardized error response with MATRIZ node.

        Args:
            error_message: Error description
            input_data: Original input data
            trace_id: Execution trace ID
            start_time: Processing start time
            triggers: List of triggers that led to this error
            question: Question if available

        Returns:
            Standardized error response dict
        """
        confidence = 0.1

        state = NodeState(
            confidence=confidence,
            salience=0.3,
            valence=-0.6,  # Negative - failed to process
            risk=0.7,  # Moderate risk due to error
            utility=0.1,  # Low utility - no answer provided
        )

        # Create regret reflection
        reflection = self.create_reflection(
            reflection_type="regret",
            cause=f"Knowledge retrieval failed: {error_message}",
            old_state={"question": question} if question else None,
            new_state={"error": error_message},
        )

        matriz_node = self.create_matriz_node(
            node_type="MEMORY",
            state=state,
            trace_id=trace_id,
            triggers=triggers,
            reflections=[reflection],
            additional_data={
                "question": question,
                "error": error_message,
                "answer": None,
                "knowledge_category": "error",
                "match_type": "error",
                "similarity_score": 0.0,
                "retrieval_method": "failed",
                "context": input_data.get("context", {}),
            },
        )

        processing_time = time.time() - start_time

        return {
            "answer": f"Error: {error_message}",
            "confidence": confidence,
            "matriz_node": matriz_node,
            "processing_time": processing_time,
        }


# Example usage and testing
if __name__ == "__main__":
    # Create the fact node
    fact_node = FactNode()

    # Comprehensive test cases
    test_cases = [
        # Exact matches
        {
            "question": "What is the capital of France?",
            "expected_type": "high_confidence",
        },
        {
            "question": "What is the capital of Japan?",
            "expected_type": "high_confidence",
        },
        {"question": "When did World War 2 end?", "expected_type": "high_confidence"},
        # Similar questions (fuzzy matching)
        {
            "question": "What's the capital of France?",
            "expected_type": "high_confidence",
        },
        {"question": "Capital of France?", "expected_type": "medium_confidence"},
        {"question": "France capital", "expected_type": "medium_confidence"},
        {
            "question": "What city is the capital of France",
            "expected_type": "high_confidence",
        },
        # Scientific facts
        {"question": "What is the speed of light?", "expected_type": "high_confidence"},
        {
            "question": "How many planets are in our solar system?",
            "expected_type": "high_confidence",
        },
        {"question": "What is the largest planet?", "expected_type": "high_confidence"},
        # Mathematical facts
        {"question": "What is pi?", "expected_type": "high_confidence"},
        {"question": "What is the value of pi?", "expected_type": "medium_confidence"},
        # General knowledge
        {
            "question": "How many days are in a year?",
            "expected_type": "high_confidence",
        },
        {
            "question": "How many continents are there?",
            "expected_type": "high_confidence",
        },
        # Unknown questions (should return "I don't know")
        {"question": "What is the meaning of life?", "expected_type": "unknown"},
        {"question": "Who will win the next election?", "expected_type": "unknown"},
        {"question": "What is my favorite color?", "expected_type": "unknown"},
        # Edge cases
        {"question": "", "expected_type": "error"},
        {"question": "   ", "expected_type": "error"},
        {"question": "askdjfh askdjfh askdjfh", "expected_type": "unknown"},
    ]

    print("MATRIZ Factual Knowledge Retrieval Node Test")
    print("=" * 55)

    success_count = 0
    total_tests = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        expected_type = test_case["expected_type"]

        print(f"\nTest {i:2d}: {question}")
        print("-" * 40)

        try:
            # Process the question
            result = fact_node.process({"question": question, "context": {"test_case": i}})

            # Validate output
            is_valid = fact_node.validate_output(result)

            print(f"Answer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Processing time: {result['processing_time']:.6f}s")
            print(f"Output valid: {is_valid}")

            # Determine actual result type
            confidence = result["confidence"]
            answer = result["answer"]

            if answer.startswith("Error:"):
                actual_type = "error"
            elif answer == "I don't know the answer to that question.":
                actual_type = "unknown"
            elif confidence >= 0.7:
                actual_type = "high_confidence"
            elif confidence >= 0.4:
                actual_type = "medium_confidence"
            else:
                actual_type = "low_confidence"

            type_matches = actual_type == expected_type
            print(f"Expected: {expected_type}, Got: {actual_type}, Match: {type_matches}")

            # Show MATRIZ node details
            matriz_node = result["matriz_node"]
            print(f"MATRIZ Node ID: {matriz_node['id'][:8]}...")
            print(f"Node Type: {matriz_node['type']}")

            state = matriz_node["state"]
            print(f"State: conf={state['confidence']:.3f}, sal={state['salience']:.3f}")

            if "knowledge_category" in state:
                print(f"Category: {state['knowledge_category']}")

            if "match_type" in state:
                print(f"Match Type: {state['match_type']}")

            if "similarity_score" in state:
                print(f"Similarity: {state['similarity_score']:.3f}")

            # Check reflections
            if matriz_node["reflections"]:
                reflection = matriz_node["reflections"][0]
                print(f"Reflection: {reflection['reflection_type']} - {reflection['cause'][:50]}...")

            if is_valid and type_matches:
                success_count += 1
                print("✓ PASS")
            else:
                print("✗ FAIL")

        except Exception as e:
            print(f"✗ EXCEPTION: {e!s}")

    print("\n" + "=" * 55)
    print(f"Test Results: {success_count}/{total_tests} passed ({success_count / total_tests * 100:.1f}%)")
    print(f"Processing History: {len(fact_node.get_trace())} MATRIZ nodes created")
    print(f"Knowledge Base Size: {len(fact_node.knowledge_base)} facts")

    # Show deterministic behavior
    print("\nDeterministic Test:")
    test_question = "What is the capital of France?"
    hash1 = fact_node.get_deterministic_hash({"question": test_question})
    hash2 = fact_node.get_deterministic_hash({"question": test_question})
    print(f"Same input produces same hash: {hash1 == hash2}")
    print(f"Hash: {hash1[:16]}...")

    # Show knowledge categories
    categories = {}
    for kb_data in fact_node.knowledge_base.values():
        category = kb_data["category"]
        categories[category] = categories.get(category, 0) + 1

    print("\nKnowledge Categories:")
    for category, count in sorted(categories.items()):
        print(f"  {category}: {count} facts")
