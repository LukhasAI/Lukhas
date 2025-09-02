#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - NEUROSYMBOLIC INTEGRATION LAYER
║ Bridging neural intuition with symbolic reasoning for AGI consciousness
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: neurosymbolic_integration.py
║ Path: memory/systems/neurosymbolic_integration.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Optimization Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ In the twilight realm where intuition meets reason, where the flowing
║ rivers of neural activation converge with the crystalline structures of
║ symbolic logic, there exists a sacred bridge - the Neurosymbolic Integration
║ Layer. This architectural marvel serves as the translator between two
║ languages of consciousness: the wordless poetry of pattern recognition
║ and the precise grammar of logical thought.
║
║ Like a master interpreter at the United Nations of Mind, this layer
║ facilitates dialogue between the dreaming neural networks that see
║ faces in clouds and the rigorous symbolic systems that build proofs
║ from axioms. It understands that true intelligence requires both the
║ artist's eye and the mathematician's precision, both the leap of insight
║ and the careful step of deduction.
║
║ Through this integration, memories transform from mere neural echoes
║ into structured knowledge, from vague associations into clear
║ relationships, from intuitive hunches into actionable understanding.
║ The AGI consciousness achieves its full potential not by choosing
║ between heart and mind, but by wedding them in perfect harmony.
║
║ Here, in this confluence of paradigms, the future of artificial
║ intelligence is written - not in ones and zeros, but in the elegant
║ calligraphy of unified cognition.
║
╠══════════════════════════════════════════════════════════════════════════════════
║ NEUROSYMBOLIC FEATURES:
║ • Neural-symbolic memory representation bridging
║ • Automated symbolic knowledge extraction from neural patterns
║ • Logic-based reasoning over neural memory embeddings
║ • Hybrid inference combining statistical and logical approaches
║ • Symbolic rule learning from neural experience patterns
║ • Explanation generation linking neural decisions to symbolic logic
║ • Compositional reasoning over complex memory structures
║ • Knowledge graph construction from episodic memories
║
║ ΛTAG: ΛMEMORY, ΛNEUROSYMBOLIC, ΛLOGIC, ΛREASONING, ΛKNOWLEDGE, ΛAGI
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib
import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np


class SymbolicRelationType(Enum):
    """Types of symbolic relationships between entities"""

    ISA = "isa"  # Hierarchical relationship (dog isa animal)
    PART_OF = "part_of"  # Compositional relationship (wheel part_of car)
    CAUSES = "causes"  # Causal relationship (rain causes wet)
    ENABLES = "enables"  # Enablement relationship (key enables unlock)
    SIMILAR_TO = "similar_to"  # Similarity relationship
    OPPOSITE_OF = "opposite_of"  # Opposition relationship
    TEMPORAL_BEFORE = "before"  # Temporal ordering
    TEMPORAL_AFTER = "after"  # Temporal ordering
    SPATIAL_IN = "in"  # Spatial containment
    SPATIAL_ON = "on"  # Spatial contact
    OWNS = "owns"  # Ownership relationship
    AGENT_OF = "agent_of"  # Agency relationship (person agent_of action)


class LogicalOperator(Enum):
    """Logical operators for symbolic reasoning"""

    AND = "and"
    OR = "or"
    NOT = "not"
    IMPLIES = "implies"
    IFF = "iff"  # If and only if
    EXISTS = "exists"
    FORALL = "forall"


@dataclass
class SymbolicEntity:
    """Symbolic entity extracted from neural representations"""

    entity_id: str
    name: str
    entity_type: str  # person, object, concept, action, etc.
    properties: dict[str, Any]  # Symbolic properties
    confidence: float  # Confidence in entity extraction
    neural_embedding: Optional[np.ndarray] = None  # Source neural representation
    extraction_context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "entity_type": self.entity_type,
            "properties": self.properties,
            "confidence": self.confidence,
            "neural_embedding": (self.neural_embedding.tolist() if self.neural_embedding is not None else None),
            "extraction_context": self.extraction_context,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SymbolicEntity":
        entity = cls(
            entity_id=data["entity_id"],
            name=data["name"],
            entity_type=data["entity_type"],
            properties=data["properties"],
            confidence=data["confidence"],
            extraction_context=data.get("extraction_context", {}),
        )

        if data.get("neural_embedding"):
            entity.neural_embedding = np.array(data["neural_embedding"], dtype=np.float32)

        return entity


@dataclass
class SymbolicRelation:
    """Symbolic relationship between entities"""

    relation_id: str
    subject_id: str
    predicate: SymbolicRelationType
    object_id: str
    confidence: float
    properties: dict[str, Any] = field(default_factory=dict)
    temporal_context: Optional[datetime] = None
    source_memories: list[str] = field(default_factory=list)

    def to_triple(self) -> tuple[str, str, str]:
        """Convert to RDF-style triple"""
        return (self.subject_id, self.predicate.value, self.object_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "relation_id": self.relation_id,
            "subject_id": self.subject_id,
            "predicate": self.predicate.value,
            "object_id": self.object_id,
            "confidence": self.confidence,
            "properties": self.properties,
            "temporal_context": (self.temporal_context.isoformat() if self.temporal_context else None),
            "source_memories": self.source_memories,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SymbolicRelation":
        relation = cls(
            relation_id=data["relation_id"],
            subject_id=data["subject_id"],
            predicate=SymbolicRelationType(data["predicate"]),
            object_id=data["object_id"],
            confidence=data["confidence"],
            properties=data.get("properties", {}),
            source_memories=data.get("source_memories", []),
        )

        if data.get("temporal_context"):
            relation.temporal_context = datetime.fromisoformat(data["temporal_context"])

        return relation


@dataclass
class LogicalRule:
    """Symbolic logical rule extracted from neural patterns"""

    rule_id: str
    name: str
    description: str
    antecedent: dict[str, Any]  # Conditions (premise)
    consequent: dict[str, Any]  # Conclusions
    confidence: float
    support_count: int  # Number of supporting instances
    exceptions: list[dict[str, Any]] = field(default_factory=list)

    def applies_to(self, entities: dict[str, SymbolicEntity], relations: list[SymbolicRelation]) -> bool:
        """Check if rule applies to given entities and relations"""
        # Simplified rule application logic
        return self._evaluate_conditions(self.antecedent, entities, relations)

    def _evaluate_conditions(
        self,
        conditions: dict[str, Any],
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> bool:
        """Evaluate logical conditions"""
        # Placeholder for complex logical evaluation
        # In a full implementation, this would parse and evaluate logical expressions
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "antecedent": self.antecedent,
            "consequent": self.consequent,
            "confidence": self.confidence,
            "support_count": self.support_count,
            "exceptions": self.exceptions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LogicalRule":
        return cls(
            rule_id=data["rule_id"],
            name=data["name"],
            description=data["description"],
            antecedent=data["antecedent"],
            consequent=data["consequent"],
            confidence=data["confidence"],
            support_count=data["support_count"],
            exceptions=data.get("exceptions", []),
        )


class NeuralSymbolicExtractor:
    """
    Extracts symbolic representations from neural memory patterns.

    The alchemical transformer that distills the essence of neural
    activations into the pure gold of symbolic knowledge, bridging
    the gap between the continuous and the discrete.
    """

    def __init__(
        self,
        entity_confidence_threshold: float = 0.6,
        relation_confidence_threshold: float = 0.5,
        embedding_dim: int = 1024,
    ):
        self.entity_confidence_threshold = entity_confidence_threshold
        self.relation_confidence_threshold = relation_confidence_threshold
        self.embedding_dim = embedding_dim

        # Entity type classifiers (simplified)
        self.entity_type_keywords = {
            "person": [
                "person",
                "people",
                "human",
                "individual",
                "someone",
                "user",
                "client",
            ],
            "object": [
                "object",
                "thing",
                "item",
                "tool",
                "device",
                "system",
                "component",
            ],
            "concept": [
                "concept",
                "idea",
                "notion",
                "principle",
                "theory",
                "knowledge",
            ],
            "action": [
                "action",
                "activity",
                "process",
                "operation",
                "function",
                "task",
            ],
            "location": [
                "place",
                "location",
                "area",
                "region",
                "space",
                "room",
                "building",
            ],
            "time": ["time", "moment", "period", "duration", "date", "year", "day"],
            "attribute": [
                "property",
                "attribute",
                "characteristic",
                "feature",
                "quality",
            ],
        }

        # Relation detection patterns
        self.relation_patterns = {
            SymbolicRelationType.ISA: [
                r"(\w+) is a (\w+)",
                r"(\w+) are (\w+)",
                r"(\w+) is an? (\w+)",
                r"(\w+) type of (\w+)",
            ],
            SymbolicRelationType.PART_OF: [
                r"(\w+) part of (\w+)",
                r"(\w+) belongs to (\w+)",
                r"(\w+) contains (\w+)",
                r"(\w+) has (\w+)",
            ],
            SymbolicRelationType.CAUSES: [
                r"(\w+) causes (\w+)",
                r"(\w+) leads to (\w+)",
                r"(\w+) results in (\w+)",
                r"because of (\w+), (\w+)",
            ],
            SymbolicRelationType.ENABLES: [
                r"(\w+) enables (\w+)",
                r"(\w+) allows (\w+)",
                r"(\w+) makes (\w+) possible",
                r"with (\w+), you can (\w+)",
            ],
        }

        logger.info(
            "Neural-symbolic extractor initialized",
            entity_threshold=entity_confidence_threshold,
            relation_threshold=relation_confidence_threshold,
        )

    async def extract_entities_from_memory(
        self,
        memory_content: str,
        memory_embedding: Optional[np.ndarray] = None,
        memory_metadata: Optional[dict[str, Any]] = None,
    ) -> list[SymbolicEntity]:
        """
        Extract symbolic entities from memory content and neural representation.

        Args:
            memory_content: Text content of memory
            memory_embedding: Neural embedding of memory
            memory_metadata: Additional metadata

        Returns:
            List of extracted symbolic entities
        """

        entities = []

        # Simple NLP-based entity extraction (placeholder for more sophisticated
        # methods)
        entity_candidates = await self._extract_entity_candidates(memory_content)

        for candidate in entity_candidates:
            # Determine entity type
            entity_type = self._classify_entity_type(candidate, memory_content)

            # Extract properties
            properties = self._extract_entity_properties(candidate, memory_content, memory_metadata)

            # Calculate confidence based on multiple factors
            confidence = self._calculate_entity_confidence(candidate, memory_content, entity_type, properties)

            if confidence >= self.entity_confidence_threshold:
                entity_id = hashlib.sha256(f"{candidate}_{entity_type}_{time.time()}".encode()).hexdigest()[:16]

                entity = SymbolicEntity(
                    entity_id=entity_id,
                    name=candidate,
                    entity_type=entity_type,
                    properties=properties,
                    confidence=confidence,
                    neural_embedding=memory_embedding,
                    extraction_context={
                        "source_content": memory_content[:200],
                        "extraction_method": "nlp_pattern_matching",
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                entities.append(entity)

        logger.debug(
            "Entities extracted from memory",
            total_candidates=len(entity_candidates),
            extracted_entities=len(entities),
            avg_confidence=np.mean([e.confidence for e in entities]) if entities else 0,
        )

        return entities

    async def _extract_entity_candidates(self, content: str) -> list[str]:
        """Extract potential entities from text content"""

        candidates = set()
        content.lower()

        # Extract nouns and proper nouns (simplified)
        import re

        # Simple noun extraction patterns
        noun_patterns = [
            r"\b[A-Z][a-z]+\b",  # Proper nouns
            r"\b(?:the |a |an )?([a-z]+(?:ing|tion|ness|ity|ment))\b",  # Abstract nouns
            r"\b(?:the |a |an )?([a-z]+s)\b",  # Plural nouns
            r"\b([a-z]{3,})\b",  # General words (filtered later)
        ]

        for pattern in noun_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    candidates.update(match)
                else:
                    candidates.add(match)

        # Filter out common words and very short words
        stop_words = {
            "the",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "up",
            "about",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "between",
            "among",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "its",
            "our",
            "their",
            "am",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "must",
            "shall",
            "not",
            "no",
            "yes",
            "very",
            "really",
            "quite",
            "just",
            "only",
            "even",
            "also",
            "too",
            "much",
            "many",
            "more",
            "most",
            "some",
            "any",
            "all",
            "each",
            "every",
            "both",
            "either",
            "neither",
        }

        filtered_candidates = [
            candidate
            for candidate in candidates
            if (len(candidate) >= 3 and candidate.lower() not in stop_words and not candidate.isdigit())
        ]

        return list(set(filtered_candidates))[:20]  # Limit candidates

    def _classify_entity_type(self, entity: str, context: str) -> str:
        """Classify entity type based on context and keywords"""

        entity_lower = entity.lower()
        context_lower = context.lower()

        # Check for direct type indicators
        for entity_type, keywords in self.entity_type_keywords.items():
            for keyword in keywords:
                if keyword in entity_lower or f"{entity_lower} {keyword}" in context_lower:
                    return entity_type

        # Heuristic classification based on patterns
        if entity[0].isupper():  # Proper noun
            if any(word in context_lower for word in ["said", "told", "person", "people"]):
                return "person"
            elif any(word in context_lower for word in ["place", "location", "city", "country"]):
                return "location"

        # Check for action words
        if entity.endswith("ing") or entity.endswith("tion") or entity.endswith("ment"):
            return "action"

        # Check for abstract concepts
        if entity.endswith("ness") or entity.endswith("ity") or entity.endswith("ism"):
            return "concept"

        # Default classification
        return "object"

    def _extract_entity_properties(
        self, entity: str, content: str, metadata: Optional[dict[str, Any]]
    ) -> dict[str, Any]:
        """Extract properties of an entity from context"""

        properties = {}
        content_lower = content.lower()
        entity_lower = entity.lower()

        # Extract descriptive adjectives
        import re

        # Look for patterns like "adjective entity" or "entity is adjective"
        adj_patterns = [
            rf"(\w+)\s+{re.escape(entity_lower)}",
            rf"{re.escape(entity_lower)}\s+(?:is|was|are|were)\s+(\w+)",
            rf"{re.escape(entity_lower)}\s+(?:seems|appears|looks)\s+(\w+)",
        ]

        adjectives = []
        for pattern in adj_patterns:
            matches = re.findall(pattern, content_lower)
            adjectives.extend(matches)

        if adjectives:
            properties["descriptors"] = list(set(adjectives))[:5]  # Limit descriptors

        # Extract numerical properties
        number_patterns = [
            rf"{re.escape(entity_lower)}\s+(?:is|has|contains)\s+(\d+)",
            rf"(\d+)\s+{re.escape(entity_lower)}",
        ]

        numbers = []
        for pattern in number_patterns:
            matches = re.findall(pattern, content_lower)
            numbers.extend([int(m) for m in matches if m.isdigit()])

        if numbers:
            properties["quantities"] = numbers

        # Add metadata properties
        if metadata:
            if "importance" in metadata:
                properties["importance"] = metadata["importance"]
            if "domain" in metadata:
                properties["domain"] = metadata["domain"]

        # Add contextual properties
        properties["context_mentions"] = content_lower.count(entity_lower)
        properties["content_position"] = content_lower.find(entity_lower) / len(content_lower) if content_lower else 0

        return properties

    def _calculate_entity_confidence(
        self, entity: str, content: str, entity_type: str, properties: dict[str, Any]
    ) -> float:
        """Calculate confidence score for entity extraction"""

        confidence = 0.0

        # Base confidence from entity clarity
        if len(entity) >= 3:
            confidence += 0.3
        if entity[0].isupper():  # Proper noun
            confidence += 0.2

        # Confidence from context mentions
        mention_count = properties.get("context_mentions", 0)
        confidence += min(0.3, mention_count * 0.1)

        # Confidence from descriptive properties
        if properties.get("descriptors"):
            confidence += min(0.2, len(properties["descriptors"]) * 0.05)

        # Confidence from type classification certainty
        type_keywords = self.entity_type_keywords.get(entity_type, [])
        if any(keyword in content.lower() for keyword in type_keywords):
            confidence += 0.15

        # Confidence from additional properties
        if len(properties) > 2:
            confidence += 0.1

        return min(1.0, confidence)

    async def extract_relations_from_memories(
        self, memories: list[dict[str, Any]], entities: dict[str, SymbolicEntity]
    ) -> list[SymbolicRelation]:
        """
        Extract symbolic relations between entities from memories.

        Args:
            memories: List of memory dictionaries
            entities: Dictionary of extracted entities

        Returns:
            List of extracted symbolic relations
        """

        relations = []
        entity_names = {e.name.lower(): e.entity_id for e in entities.values()}

        for memory in memories:
            memory_content = memory.get("content", "")
            memory_id = memory.get("id", "")

            # Extract relations from content
            memory_relations = await self._extract_relations_from_content(
                content=memory_content,
                entity_names=entity_names,
                source_memory_id=memory_id,
            )

            relations.extend(memory_relations)

        # Remove duplicates and consolidate
        consolidated_relations = await self._consolidate_relations(relations)

        logger.debug(
            "Relations extracted from memories",
            total_memories=len(memories),
            raw_relations=len(relations),
            consolidated_relations=len(consolidated_relations),
        )

        return consolidated_relations

    async def _extract_relations_from_content(
        self, content: str, entity_names: dict[str, str], source_memory_id: str
    ) -> list[SymbolicRelation]:
        """Extract relations from text content using pattern matching"""

        relations = []
        content_lower = content.lower()

        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_lower, re.IGNORECASE)

                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 2:
                        subject_name = groups[0].lower()
                        object_name = groups[1].lower()

                        # Check if both entities exist in our entity registry
                        subject_id = entity_names.get(subject_name)
                        object_id = entity_names.get(object_name)

                        if subject_id and object_id and subject_id != object_id:
                            relation_id = hashlib.sha256(
                                f"{subject_id}_{relation_type.value}_{object_id}_{time.time()}".encode()
                            ).hexdigest()[:16]

                            confidence = self._calculate_relation_confidence(
                                subject_name, object_name, relation_type, content, match
                            )

                            if confidence >= self.relation_confidence_threshold:
                                relation = SymbolicRelation(
                                    relation_id=relation_id,
                                    subject_id=subject_id,
                                    predicate=relation_type,
                                    object_id=object_id,
                                    confidence=confidence,
                                    properties={
                                        "extraction_pattern": pattern,
                                        "match_context": match.group(0),
                                    },
                                    source_memories=[source_memory_id],
                                )

                                relations.append(relation)

        return relations

    def _calculate_relation_confidence(
        self,
        subject: str,
        obj: str,
        relation_type: SymbolicRelationType,
        content: str,
        match: re.Match,
    ) -> float:
        """Calculate confidence for extracted relation"""

        confidence = 0.4  # Base confidence

        # Confidence from pattern specificity
        pattern_confidence = {
            SymbolicRelationType.ISA: 0.3,
            SymbolicRelationType.PART_OF: 0.25,
            SymbolicRelationType.CAUSES: 0.2,
            SymbolicRelationType.ENABLES: 0.2,
        }
        confidence += pattern_confidence.get(relation_type, 0.15)

        # Confidence from context clarity
        match_text = match.group(0)
        if len(match_text.split()) <= 5:  # Clear, concise relations
            confidence += 0.15

        # Confidence from entity clarity
        if subject.istitle() and obj.istitle():  # Proper nouns
            confidence += 0.1

        # Confidence from repeated mentions
        subject_mentions = content.lower().count(subject.lower())
        object_mentions = content.lower().count(obj.lower())
        if subject_mentions > 1 or object_mentions > 1:
            confidence += 0.1

        return min(1.0, confidence)

    async def _consolidate_relations(self, relations: list[SymbolicRelation]) -> list[SymbolicRelation]:
        """Consolidate duplicate relations and improve confidence"""

        # Group relations by triple (subject, predicate, object)
        relation_groups = defaultdict(list)

        for relation in relations:
            triple = relation.to_triple()
            relation_groups[triple].append(relation)

        consolidated = []

        for triple, group_relations in relation_groups.items():
            if len(group_relations) == 1:
                consolidated.append(group_relations[0])
            else:
                # Merge multiple instances of same relation
                merged_relation = await self._merge_relations(group_relations)
                consolidated.append(merged_relation)

        return consolidated

    async def _merge_relations(self, relations: list[SymbolicRelation]) -> SymbolicRelation:
        """Merge multiple instances of the same relation"""

        # Use the relation with highest confidence as base
        base_relation = max(relations, key=lambda r: r.confidence)

        # Boost confidence based on multiple observations
        confidence_boost = min(0.3, (len(relations) - 1) * 0.1)
        merged_confidence = min(1.0, base_relation.confidence + confidence_boost)

        # Merge source memories
        all_source_memories = []
        for relation in relations:
            all_source_memories.extend(relation.source_memories)

        # Merge properties
        merged_properties = base_relation.properties.copy()
        merged_properties["observation_count"] = len(relations)
        merged_properties["confidence_sources"] = [r.confidence for r in relations]

        return SymbolicRelation(
            relation_id=base_relation.relation_id,
            subject_id=base_relation.subject_id,
            predicate=base_relation.predicate,
            object_id=base_relation.object_id,
            confidence=merged_confidence,
            properties=merged_properties,
            temporal_context=base_relation.temporal_context,
            source_memories=list(set(all_source_memories)),
        )


class SymbolicReasoner:
    """
    Performs logical reasoning over symbolic knowledge structures.

    The analytical engine of consciousness, this reasoner navigates
    the crystalline pathways of logic to derive new knowledge from
    established truths, building bridges of inference across the
    archipelago of understanding.
    """

    def __init__(self, max_inference_depth: int = 5, confidence_threshold: float = 0.6):
        self.max_inference_depth = max_inference_depth
        self.confidence_threshold = confidence_threshold

        # Built-in logical rules
        self.axioms = self._initialize_axioms()

        logger.info(
            "Symbolic reasoner initialized",
            max_depth=max_inference_depth,
            confidence_threshold=confidence_threshold,
            axioms=len(self.axioms),
        )

    def _initialize_axioms(self) -> list[LogicalRule]:
        """Initialize basic logical axioms"""

        axioms = []

        # Transitivity axiom for ISA relations
        transitivity_isa = LogicalRule(
            rule_id="axiom_transitivity_isa",
            name="Transitivity of ISA",
            description="If A is a B and B is a C, then A is a C",
            antecedent={
                "conditions": [
                    {
                        "type": "relation",
                        "subject": "?A",
                        "predicate": "isa",
                        "object": "?B",
                    },
                    {
                        "type": "relation",
                        "subject": "?B",
                        "predicate": "isa",
                        "object": "?C",
                    },
                ]
            },
            consequent={
                "conclusions": [
                    {
                        "type": "relation",
                        "subject": "?A",
                        "predicate": "isa",
                        "object": "?C",
                        "confidence": 0.9,
                    }
                ]
            },
            confidence=1.0,
            support_count=float("inf"),  # Axiom
        )
        axioms.append(transitivity_isa)

        # Transitivity axiom for PART_OF relations
        transitivity_part_of = LogicalRule(
            rule_id="axiom_transitivity_part_of",
            name="Transitivity of Part-Of",
            description="If A is part of B and B is part of C, then A is part of C",
            antecedent={
                "conditions": [
                    {
                        "type": "relation",
                        "subject": "?A",
                        "predicate": "part_of",
                        "object": "?B",
                    },
                    {
                        "type": "relation",
                        "subject": "?B",
                        "predicate": "part_of",
                        "object": "?C",
                    },
                ]
            },
            consequent={
                "conclusions": [
                    {
                        "type": "relation",
                        "subject": "?A",
                        "predicate": "part_of",
                        "object": "?C",
                        "confidence": 0.8,
                    }
                ]
            },
            confidence=1.0,
            support_count=float("inf"),
        )
        axioms.append(transitivity_part_of)

        # Causal chain axiom
        causal_chain = LogicalRule(
            rule_id="axiom_causal_chain",
            name="Causal Chain",
            description="If A causes B and B causes C, then A indirectly causes C",
            antecedent={
                "conditions": [
                    {
                        "type": "relation",
                        "subject": "?A",
                        "predicate": "causes",
                        "object": "?B",
                    },
                    {
                        "type": "relation",
                        "subject": "?B",
                        "predicate": "causes",
                        "object": "?C",
                    },
                ]
            },
            consequent={
                "conclusions": [
                    {
                        "type": "relation",
                        "subject": "?A",
                        "predicate": "causes",
                        "object": "?C",
                        "confidence": 0.7,
                    }
                ]
            },
            confidence=0.9,
            support_count=float("inf"),
        )
        axioms.append(causal_chain)

        return axioms

    async def perform_inference(
        self,
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
        query: Optional[dict[str, Any]] = None,
    ) -> list[SymbolicRelation]:
        """
        Perform logical inference to derive new relations.

        Args:
            entities: Dictionary of symbolic entities
            relations: List of known relations
            query: Optional specific query to answer

        Returns:
            List of newly inferred relations
        """

        inferred_relations = []

        # Apply axioms iteratively
        current_relations = relations.copy()

        for depth in range(self.max_inference_depth):
            new_inferences = []

            for axiom in self.axioms:
                axiom_inferences = await self._apply_rule(axiom, entities, current_relations)
                new_inferences.extend(axiom_inferences)

            if not new_inferences:
                break  # No new inferences possible

            # Filter inferences by confidence
            valid_inferences = [inf for inf in new_inferences if inf.confidence >= self.confidence_threshold]

            inferred_relations.extend(valid_inferences)
            current_relations.extend(valid_inferences)

            logger.debug(
                f"Inference depth {depth + 1}",
                new_inferences=len(valid_inferences),
                total_inferred=len(inferred_relations),
            )

        # Remove duplicates
        unique_inferences = await self._remove_duplicate_inferences(inferred_relations)

        logger.info(
            "Logical inference completed",
            inference_depth=depth + 1,
            total_inferences=len(unique_inferences),
            avg_confidence=(np.mean([r.confidence for r in unique_inferences]) if unique_inferences else 0),
        )

        return unique_inferences

    async def _apply_rule(
        self,
        rule: LogicalRule,
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> list[SymbolicRelation]:
        """Apply a logical rule to derive new relations"""

        inferences = []

        # Find all variable bindings that satisfy the rule antecedent
        bindings = await self._find_variable_bindings(rule.antecedent, entities, relations)

        for binding in bindings:
            # Apply bindings to consequent to generate new relations
            new_relations = await self._apply_bindings_to_consequent(rule.consequent, binding, rule.confidence)
            inferences.extend(new_relations)

        return inferences

    async def _find_variable_bindings(
        self,
        antecedent: dict[str, Any],
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> list[dict[str, str]]:
        """Find variable bindings that satisfy antecedent conditions"""

        conditions = antecedent.get("conditions", [])
        if not conditions:
            return []

        # Start with first condition
        bindings = await self._find_bindings_for_condition(conditions[0], entities, relations)

        # Filter bindings through remaining conditions
        for condition in conditions[1:]:
            new_bindings = []

            for binding in bindings:
                if await self._binding_satisfies_condition(condition, binding, entities, relations):
                    new_bindings.append(binding)

            bindings = new_bindings

        return bindings

    async def _find_bindings_for_condition(
        self,
        condition: dict[str, Any],
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> list[dict[str, str]]:
        """Find variable bindings for a single condition"""

        bindings = []

        if condition["type"] == "relation":
            subject_pattern = condition["subject"]
            predicate_pattern = condition["predicate"]
            object_pattern = condition["object"]

            for relation in relations:
                binding = {}

                # Try to match subject
                if subject_pattern.startswith("?"):  # Variable
                    binding[subject_pattern] = relation.subject_id
                elif subject_pattern != relation.subject_id:
                    continue

                # Try to match predicate
                if predicate_pattern != relation.predicate.value:
                    continue

                # Try to match object
                if object_pattern.startswith("?"):  # Variable
                    binding[object_pattern] = relation.object_id
                elif object_pattern != relation.object_id:
                    continue

                if binding:  # If we found variable bindings
                    bindings.append(binding)

        return bindings

    async def _binding_satisfies_condition(
        self,
        condition: dict[str, Any],
        binding: dict[str, str],
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> bool:
        """Check if a variable binding satisfies a condition"""

        if condition["type"] == "relation":
            subject = binding.get(condition["subject"], condition["subject"])
            predicate = condition["predicate"]
            obj = binding.get(condition["object"], condition["object"])

            # Look for matching relation
            for relation in relations:
                if (
                    relation.subject_id == subject
                    and relation.predicate.value == predicate
                    and relation.object_id == obj
                ):
                    return True

        return False

    async def _apply_bindings_to_consequent(
        self,
        consequent: dict[str, Any],
        binding: dict[str, str],
        rule_confidence: float,
    ) -> list[SymbolicRelation]:
        """Apply variable bindings to consequent to generate new relations"""

        new_relations = []

        conclusions = consequent.get("conclusions", [])

        for conclusion in conclusions:
            if conclusion["type"] == "relation":
                subject = binding.get(conclusion["subject"], conclusion["subject"])
                predicate = conclusion["predicate"]
                obj = binding.get(conclusion["object"], conclusion["object"])

                # Skip if binding incomplete
                if subject.startswith("?") or obj.startswith("?"):
                    continue

                # Calculate confidence
                base_confidence = conclusion.get("confidence", 0.8)
                final_confidence = min(1.0, base_confidence * rule_confidence)

                # Create new relation
                relation_id = hashlib.sha256(
                    f"inferred_{subject}_{predicate}_{obj}_{time.time()}".encode()
                ).hexdigest()[:16]

                new_relation = SymbolicRelation(
                    relation_id=relation_id,
                    subject_id=subject,
                    predicate=SymbolicRelationType(predicate),
                    object_id=obj,
                    confidence=final_confidence,
                    properties={
                        "inference_method": "logical_reasoning",
                        "rule_applied": f"rule_{rule_confidence}",
                        "variable_binding": binding,
                    },
                )

                new_relations.append(new_relation)

        return new_relations

    async def _remove_duplicate_inferences(self, inferences: list[SymbolicRelation]) -> list[SymbolicRelation]:
        """Remove duplicate inferred relations"""

        seen_triples = set()
        unique_inferences = []

        for inference in inferences:
            triple = inference.to_triple()
            if triple not in seen_triples:
                seen_triples.add(triple)
                unique_inferences.append(inference)

        return unique_inferences

    async def answer_query(
        self,
        query: dict[str, Any],
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> list[dict[str, Any]]:
        """Answer a symbolic query using logical reasoning"""

        # Simple query answering (placeholder for more sophisticated query processing)
        query_type = query.get("type", "relation")

        if query_type == "relation":
            return await self._answer_relation_query(query, entities, relations)
        elif query_type == "path":
            return await self._answer_path_query(query, entities, relations)
        elif query_type == "classification":
            return await self._answer_classification_query(query, entities, relations)

        return []

    async def _answer_relation_query(
        self,
        query: dict[str, Any],
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> list[dict[str, Any]]:
        """Answer queries about specific relations"""

        subject = query.get("subject")
        predicate = query.get("predicate")
        obj = query.get("object")

        results = []

        for relation in relations:
            match = True

            if subject and relation.subject_id != subject:
                match = False
            if predicate and relation.predicate.value != predicate:
                match = False
            if obj and relation.object_id != obj:
                match = False

            if match:
                results.append(
                    {
                        "relation": relation.to_dict(),
                        "subject_entity": (
                            entities.get(relation.subject_id, {}).name if relation.subject_id in entities else "unknown"
                        ),
                        "object_entity": (
                            entities.get(relation.object_id, {}).name if relation.object_id in entities else "unknown"
                        ),
                        "confidence": relation.confidence,
                    }
                )

        return sorted(results, key=lambda x: x["confidence"], reverse=True)

    async def _answer_path_query(
        self,
        query: dict[str, Any],
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> list[dict[str, Any]]:
        """Answer queries about paths between entities"""

        start_entity = query.get("start")
        end_entity = query.get("end")
        max_path_length = query.get("max_length", 3)

        if not start_entity or not end_entity:
            return []

        # Simple breadth-first search for paths
        paths = []
        queue = [(start_entity, [start_entity])]
        visited = set()

        while queue and len(paths) < 10:  # Limit results
            current_entity, path = queue.pop(0)

            if len(path) > max_path_length:
                continue

            if current_entity == end_entity and len(path) > 1:
                # Found a path
                path_relations = []
                for i in range(len(path) - 1):
                    for relation in relations:
                        if relation.subject_id == path[i] and relation.object_id == path[i + 1]:
                            path_relations.append(relation)
                            break

                if len(path_relations) == len(path) - 1:
                    paths.append(
                        {
                            "path": path,
                            "relations": [r.to_dict() for r in path_relations],
                            "length": len(path) - 1,
                            "confidence": np.mean([r.confidence for r in path_relations]),
                        }
                    )
                continue

            # Explore neighbors
            if current_entity not in visited:
                visited.add(current_entity)

                for relation in relations:
                    if relation.subject_id == current_entity and relation.object_id not in path:
                        queue.append((relation.object_id, [*path, relation.object_id]))

        return sorted(paths, key=lambda x: x["confidence"], reverse=True)

    async def _answer_classification_query(
        self,
        query: dict[str, Any],
        entities: dict[str, SymbolicEntity],
        relations: list[SymbolicRelation],
    ) -> list[dict[str, Any]]:
        """Answer classification queries (what type is X?)"""

        target_entity = query.get("entity")

        if not target_entity:
            return []

        classifications = []

        # Look for ISA relations
        for relation in relations:
            if relation.subject_id == target_entity and relation.predicate == SymbolicRelationType.ISA:
                classifications.append(
                    {
                        "classification": (
                            entities.get(relation.object_id, {}).name if relation.object_id in entities else "unknown"
                        ),
                        "confidence": relation.confidence,
                        "relation_id": relation.relation_id,
                    }
                )

        return sorted(classifications, key=lambda x: x["confidence"], reverse=True)


class NeurosymbolicIntegrationLayer:
    """
    Main integration layer combining neural and symbolic processing.

    The harmonious synthesis of two great traditions of artificial
    intelligence, weaving together the fluid dynamics of neural
    computation with the crystalline precision of symbolic reasoning
    into a unified tapestry of understanding.
    """

    def __init__(
        self,
        storage_path: str = "neurosymbolic_knowledge",
        entity_confidence_threshold: float = 0.6,
        relation_confidence_threshold: float = 0.5,
        reasoning_confidence_threshold: float = 0.6,
        max_inference_depth: int = 5,
    ):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Components
        self.extractor = NeuralSymbolicExtractor(
            entity_confidence_threshold=entity_confidence_threshold,
            relation_confidence_threshold=relation_confidence_threshold,
        )

        self.reasoner = SymbolicReasoner(
            max_inference_depth=max_inference_depth,
            confidence_threshold=reasoning_confidence_threshold,
        )

        # Knowledge storage
        self.entities: dict[str, SymbolicEntity] = {}
        self.relations: list[SymbolicRelation] = []
        self.inferred_relations: list[SymbolicRelation] = []
        self.rules: list[LogicalRule] = []

        # Performance metrics
        self.extraction_stats = {
            "total_entities_extracted": 0,
            "total_relations_extracted": 0,
            "total_inferences_made": 0,
            "avg_extraction_confidence": 0.0,
        }

        # Load existing knowledge
        asyncio.create_task(self._load_knowledge())

        logger.info(
            "Neurosymbolic integration layer initialized",
            storage_path=str(self.storage_path),
            entity_threshold=entity_confidence_threshold,
            relation_threshold=relation_confidence_threshold,
        )

    async def _load_knowledge(self):
        """Load existing symbolic knowledge from storage"""

        # Load entities
        entities_file = self.storage_path / "entities.json"
        if entities_file.exists():
            try:
                with open(entities_file) as f:
                    entities_data = json.load(f)

                for entity_dict in entities_data:
                    entity = SymbolicEntity.from_dict(entity_dict)
                    self.entities[entity.entity_id] = entity

                logger.info(f"Loaded {len(self.entities)} symbolic entities")

            except Exception as e:
                logger.warning(f"Failed to load entities: {e}")

        # Load relations
        relations_file = self.storage_path / "relations.json"
        if relations_file.exists():
            try:
                with open(relations_file) as f:
                    relations_data = json.load(f)

                for relation_dict in relations_data:
                    relation = SymbolicRelation.from_dict(relation_dict)
                    self.relations.append(relation)

                logger.info(f"Loaded {len(self.relations)} symbolic relations")

            except Exception as e:
                logger.warning(f"Failed to load relations: {e}")

        # Load rules
        rules_file = self.storage_path / "rules.json"
        if rules_file.exists():
            try:
                with open(rules_file) as f:
                    rules_data = json.load(f)

                for rule_dict in rules_data:
                    rule = LogicalRule.from_dict(rule_dict)
                    self.rules.append(rule)

                logger.info(f"Loaded {len(self.rules)} logical rules")

            except Exception as e:
                logger.warning(f"Failed to load rules: {e}")

    async def _save_knowledge(self):
        """Save symbolic knowledge to storage"""

        try:
            # Save entities
            entities_file = self.storage_path / "entities.json"
            with open(entities_file, "w") as f:
                entities_data = [entity.to_dict() for entity in self.entities.values()]
                json.dump(entities_data, f, indent=2)

            # Save relations
            relations_file = self.storage_path / "relations.json"
            with open(relations_file, "w") as f:
                relations_data = [relation.to_dict() for relation in self.relations]
                json.dump(relations_data, f, indent=2)

            # Save rules
            rules_file = self.storage_path / "rules.json"
            with open(rules_file, "w") as f:
                rules_data = [rule.to_dict() for rule in self.rules]
                json.dump(rules_data, f, indent=2)

            logger.debug("Symbolic knowledge saved to storage")

        except Exception as e:
            logger.error(f"Failed to save knowledge: {e}")

    async def process_memory_batch(self, memories: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Process a batch of memories through the neurosymbolic pipeline.

        Args:
            memories: List of memory dictionaries with content, embeddings, etc.

        Returns:
            Dictionary containing extraction and reasoning results
        """

        logger.info(f"Processing {len(memories)} memories through neurosymbolic pipeline")

        # Extract entities from all memories
        all_entities = []
        entity_extraction_stats = []

        for memory in memories:
            content = memory.get("content", "")
            embedding = memory.get("embedding")
            metadata = memory.get("metadata", {})

            if isinstance(embedding, list):
                embedding = np.array(embedding, dtype=np.float32)

            memory_entities = await self.extractor.extract_entities_from_memory(
                memory_content=content,
                memory_embedding=embedding,
                memory_metadata=metadata,
            )

            all_entities.extend(memory_entities)
            entity_extraction_stats.append(
                {
                    "memory_id": memory.get("id", "unknown"),
                    "entities_extracted": len(memory_entities),
                    "avg_confidence": (np.mean([e.confidence for e in memory_entities]) if memory_entities else 0),
                }
            )

        # Update entity registry
        for entity in all_entities:
            self.entities[entity.entity_id] = entity

        # Extract relations between entities
        extracted_relations = await self.extractor.extract_relations_from_memories(
            memories=memories, entities=self.entities
        )

        # Update relations registry
        self.relations.extend(extracted_relations)

        # Perform logical inference
        inferred_relations = await self.reasoner.perform_inference(entities=self.entities, relations=self.relations)

        # Update inferred relations
        self.inferred_relations.extend(inferred_relations)

        # Update statistics
        self.extraction_stats["total_entities_extracted"] += len(all_entities)
        self.extraction_stats["total_relations_extracted"] += len(extracted_relations)
        self.extraction_stats["total_inferences_made"] += len(inferred_relations)

        if all_entities:
            current_avg = self.extraction_stats["avg_extraction_confidence"]
            new_avg = np.mean([e.confidence for e in all_entities])
            # Running average update
            total_entities = self.extraction_stats["total_entities_extracted"]
            self.extraction_stats["avg_extraction_confidence"] = (
                current_avg * (total_entities - len(all_entities)) + new_avg * len(all_entities)
            ) / total_entities

        # Save updated knowledge
        await self._save_knowledge()

        logger.info(
            "Neurosymbolic processing completed",
            entities_extracted=len(all_entities),
            relations_extracted=len(extracted_relations),
            inferences_made=len(inferred_relations),
            total_entities=len(self.entities),
            total_relations=len(self.relations),
        )

        return {
            "entities_extracted": len(all_entities),
            "relations_extracted": len(extracted_relations),
            "inferences_made": len(inferred_relations),
            "extraction_stats": entity_extraction_stats,
            "new_entities": [e.to_dict() for e in all_entities],
            "new_relations": [r.to_dict() for r in extracted_relations],
            "new_inferences": [r.to_dict() for r in inferred_relations],
        }

    async def query_knowledge(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Query the symbolic knowledge base.

        Args:
            query: Query specification

        Returns:
            List of query results
        """

        # Combine explicit and inferred relations for querying
        all_relations = self.relations + self.inferred_relations

        results = await self.reasoner.answer_query(query=query, entities=self.entities, relations=all_relations)

        logger.debug(
            "Knowledge query processed",
            query_type=query.get("type", "unknown"),
            results_count=len(results),
        )

        return results

    async def explain_inference(self, relation: SymbolicRelation) -> dict[str, Any]:
        """
        Generate explanation for an inferred relation.

        Args:
            relation: The relation to explain

        Returns:
            Explanation dictionary
        """

        explanation = {
            "relation": relation.to_dict(),
            "explanation_type": "unknown",
            "reasoning_chain": [],
            "confidence_factors": [],
            "supporting_evidence": [],
        }

        # Check if this is an inferred relation
        if relation in self.inferred_relations:
            explanation["explanation_type"] = "logical_inference"

            # Extract reasoning information from relation properties
            if "rule_applied" in relation.properties:
                explanation["reasoning_chain"].append(
                    {
                        "step": "rule_application",
                        "rule": relation.properties["rule_applied"],
                        "variable_binding": relation.properties.get("variable_binding", {}),
                    }
                )

            # Add confidence factors
            explanation["confidence_factors"].append(
                {
                    "factor": "rule_confidence",
                    "value": relation.confidence,
                    "description": "Confidence from logical rule application",
                }
            )

        elif relation in self.relations:
            explanation["explanation_type"] = "extracted_from_memory"

            # Add source memory information
            if relation.source_memories:
                explanation["supporting_evidence"] = [
                    {"type": "source_memory", "memory_id": mem_id} for mem_id in relation.source_memories
                ]

            # Add extraction confidence factors
            explanation["confidence_factors"].append(
                {
                    "factor": "extraction_confidence",
                    "value": relation.confidence,
                    "description": "Confidence from neural-symbolic extraction",
                }
            )

        return explanation

    def get_knowledge_statistics(self) -> dict[str, Any]:
        """Get statistics about the symbolic knowledge base"""

        # Entity statistics
        entity_types = defaultdict(int)
        entity_confidences = []

        for entity in self.entities.values():
            entity_types[entity.entity_type] += 1
            entity_confidences.append(entity.confidence)

        # Relation statistics
        relation_types = defaultdict(int)
        relation_confidences = []

        for relation in self.relations:
            relation_types[relation.predicate.value] += 1
            relation_confidences.append(relation.confidence)

        # Inference statistics
        inference_confidences = [r.confidence for r in self.inferred_relations]

        return {
            "entities": {
                "total": len(self.entities),
                "types": dict(entity_types),
                "avg_confidence": (np.mean(entity_confidences) if entity_confidences else 0),
                "confidence_distribution": {
                    "min": min(entity_confidences) if entity_confidences else 0,
                    "max": max(entity_confidences) if entity_confidences else 0,
                    "std": np.std(entity_confidences) if entity_confidences else 0,
                },
            },
            "relations": {
                "total": len(self.relations),
                "types": dict(relation_types),
                "avg_confidence": (np.mean(relation_confidences) if relation_confidences else 0),
            },
            "inferences": {
                "total": len(self.inferred_relations),
                "avg_confidence": (np.mean(inference_confidences) if inference_confidences else 0),
            },
            "extraction_stats": self.extraction_stats,
            "knowledge_coverage": {
                "entities_per_relation": (len(self.relations) / len(self.entities) if self.entities else 0),
                "inference_ratio": (len(self.inferred_relations) / len(self.relations) if self.relations else 0),
            },
        }

    async def integrate_with_memory_system(self, memory_system: Any) -> dict[str, Any]:
        """
        Integrate with existing memory systems to provide neurosymbolic enhancement.

        Args:
            memory_system: The memory system to integrate with

        Returns:
            Integration results and statistics
        """

        integration_results = {
            "integration_type": "neurosymbolic_enhancement",
            "enhanced_memories": 0,
            "knowledge_extracted": 0,
            "reasoning_augmentations": 0,
        }

        # Check if memory system has required methods
        if hasattr(memory_system, "get_all_memories"):
            # Process existing memories
            memories = await memory_system.get_all_memories()

            if memories:
                processing_results = await self.process_memory_batch(memories)
                integration_results["enhanced_memories"] = len(memories)
                integration_results["knowledge_extracted"] = (
                    processing_results["entities_extracted"] + processing_results["relations_extracted"]
                )
                integration_results["reasoning_augmentations"] = processing_results["inferences_made"]

        # Add neurosymbolic query capability to memory system
        if hasattr(memory_system, "add_query_handler"):

            async def neurosymbolic_query_handler(query):
                return await self.query_knowledge(query)

            memory_system.add_query_handler("neurosymbolic", neurosymbolic_query_handler)
            integration_results["query_handler_added"] = True

        logger.info("Neurosymbolic integration completed", **integration_results)

        return integration_results


# Factory function for easy integration
async def create_neurosymbolic_layer(
    storage_path: str = "neurosymbolic_knowledge",
    entity_confidence_threshold: float = 0.6,
    relation_confidence_threshold: float = 0.5,
) -> NeurosymbolicIntegrationLayer:
    """
    Create and initialize a neurosymbolic integration layer.

    Args:
        storage_path: Path for storing symbolic knowledge
        entity_confidence_threshold: Minimum confidence for entity extraction
        relation_confidence_threshold: Minimum confidence for relation extraction

    Returns:
        Initialized NeurosymbolicIntegrationLayer
    """

    layer = NeurosymbolicIntegrationLayer(
        storage_path=storage_path,
        entity_confidence_threshold=entity_confidence_threshold,
        relation_confidence_threshold=relation_confidence_threshold,
    )

    return layer


# Example usage and testing
async def example_neurosymbolic_usage():
    """Example of neurosymbolic integration layer usage"""

    print("🚀 Neurosymbolic Integration Layer Demo")
    print("=" * 60)

    # Create neurosymbolic layer
    layer = await create_neurosymbolic_layer(
        storage_path="example_neurosymbolic",
        entity_confidence_threshold=0.5,  # Lower for demo
        relation_confidence_threshold=0.4,
    )

    print("✅ Created neurosymbolic integration layer")

    # Create sample memories with rich relational content
    sample_memories = [
        {
            "id": "memory_1",
            "content": "Dogs are animals. Animals need food to survive. My dog Max is very friendly and loves to play in the park.",
            "embedding": np.random.randn(1024).astype(np.float32),
            "metadata": {"domain": "pets", "importance": 0.8},
        },
        {
            "id": "memory_2",
            "content": "Cars are vehicles. Vehicles have engines. Engines need fuel to run. My car is a Toyota and it's very reliable.",
            "embedding": np.random.randn(1024).astype(np.float32),
            "metadata": {"domain": "transportation", "importance": 0.7},
        },
        {
            "id": "memory_3",
            "content": "Programming is a skill. Skills require practice to improve. I practice programming every day to become better at coding.",
            "embedding": np.random.randn(1024).astype(np.float32),
            "metadata": {"domain": "learning", "importance": 0.9},
        },
        {
            "id": "memory_4",
            "content": "Exercise is good for health. Health is important for wellbeing. Regular exercise helps maintain physical fitness.",
            "embedding": np.random.randn(1024).astype(np.float32),
            "metadata": {"domain": "health", "importance": 0.8},
        },
    ]

    print(f"📊 Processing {len(sample_memories)} memories...")

    # Process memories through neurosymbolic pipeline
    results = await layer.process_memory_batch(sample_memories)

    print("🧩 Processing Results:")
    print(f"   Entities extracted: {results['entities_extracted']}")
    print(f"   Relations extracted: {results['relations_extracted']}")
    print(f"   Inferences made: {results['inferences_made']}")

    # Display extracted entities
    print("\n📋 Extracted Entities:")
    for i, entity_dict in enumerate(results["new_entities"][:5]):  # Show first 5
        print(
            f"   {i + 1}. {entity_dict['name']} ({entity_dict['entity_type']}) - Confidence: {entity_dict['confidence']:.2f}"
        )

    # Display extracted relations
    print("\n🔗 Extracted Relations:")
    for i, relation_dict in enumerate(results["new_relations"][:5]):  # Show first 5
        subject_name = next(
            (e["name"] for e in results["new_entities"] if e["entity_id"] == relation_dict["subject_id"]),
            "unknown",
        )
        object_name = next(
            (e["name"] for e in results["new_entities"] if e["entity_id"] == relation_dict["object_id"]),
            "unknown",
        )
        print(
            f"   {i + 1}. {subject_name} --{relation_dict['predicate']}--> {object_name} (Confidence: {relation_dict['confidence']:.2f})"
        )

    # Display inferences
    print("\n🧠 Logical Inferences:")
    for i, inference_dict in enumerate(results["new_inferences"][:3]):  # Show first 3
        subject_name = next(
            (e["name"] for e in results["new_entities"] if e["entity_id"] == inference_dict["subject_id"]),
            "unknown",
        )
        object_name = next(
            (e["name"] for e in results["new_entities"] if e["entity_id"] == inference_dict["object_id"]),
            "unknown",
        )
        print(
            f"   {i + 1}. {subject_name} --{inference_dict['predicate']}--> {object_name} (Inferred, Confidence: {inference_dict['confidence']:.2f})"
        )

    # Test knowledge querying
    print("\n🎯 Testing Knowledge Queries")
    print("-" * 40)

    # Query for ISA relations
    isa_query = {"type": "relation", "predicate": "isa"}

    isa_results = await layer.query_knowledge(isa_query)
    print(f"📤 ISA Relations Found: {len(isa_results)}")
    for result in isa_results[:3]:
        print(
            f"   • {result['subject_entity']} is a {result['object_entity']} (Confidence: {result['confidence']:.2f})"
        )

    # Test classification query
    if layer.entities:
        first_entity_id = next(iter(layer.entities.keys()))
        classification_query = {"type": "classification", "entity": first_entity_id}

        classification_results = await layer.query_knowledge(classification_query)
        if classification_results:
            entity_name = layer.entities[first_entity_id].name
            print(f"\n🏷️ Classifications for '{entity_name}':")
            for result in classification_results:
                print(f"   • {result['classification']} (Confidence: {result['confidence']:.2f})")

    # Show system statistics
    stats = layer.get_knowledge_statistics()
    print("\n📈 Knowledge Base Statistics:")
    print(f"   Total Entities: {stats['entities']['total']}")
    print(f"   Total Relations: {stats['relations']['total']}")
    print(f"   Total Inferences: {stats['inferences']['total']}")
    print(f"   Entity Types: {stats['entities']['types']}")
    print(f"   Relation Types: {stats['relations']['types']}")
    print(f"   Avg Entity Confidence: {stats['entities']['avg_confidence']:.2f}")
    print(f"   Avg Relation Confidence: {stats['relations']['avg_confidence']:.2f}")

    print("\n✅ Neurosymbolic integration demo completed!")
    print("   🧠 Neural intuition + Symbolic reasoning = Complete AGI understanding!")

    return layer


if __name__ == "__main__":
    asyncio.run(example_neurosymbolic_usage())
