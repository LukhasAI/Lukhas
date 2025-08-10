#!/usr/bin/env python3

"""
LUKHAS (Logical Unified Knowledge Hyper-Adaptable System) - Symbolic Knowledge Loader

Copyright (c) 2025 LUKHAS AGI Development Team
All rights reserved.

This file is part of the LUKHAS AGI system, an enterprise artificial general
intelligence platform combining symbolic reasoning, emotional intelligence,
quantum integration, and bio-inspired architecture.

Mission: To illuminate complex reality through rigorous logic, adaptive
intelligence, and human-centred ethics—turning data into understanding,
understanding into foresight, and foresight into shared benefit for people
and planet.

Comprehensive knowledge base loader for LUKHAS AI foundational concepts.
Integrates symbolic ontologies, affect mappings, and glyph linkages for
enhanced memory, narrative, and ethics system functionality.

For more information, visit: https://lukhas.ai
"""

# ΛTRACE: Symbolic knowledge loader initialization
# ΛORIGIN_AGENT: Claude Code
# ΛTASK_ID: Task 17 - Foundational Knowledge Integration

__version__ = "1.0.0"
__author__ = "LUKHAS Development Team"
__email__ = "dev@lukhas.ai"
__status__ = "Production"

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Set up structured logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SymbolicConcept:
    """Represents a unified symbolic concept with LUKHAS integration."""

    concept: str
    definition: str
    affect_tag: Optional[str] = None
    glyph_links: List[str] = field(default_factory=list)
    importance: float = 5.0  # Scale 0.0-10.0
    related: List[str] = field(default_factory=list)
    symbolic_hash: Optional[str] = None
    temporal_stamp: Optional[str] = None

    def __post_init__(self):
        """Generate symbolic identifiers after initialization."""
        if self.temporal_stamp is None:
            self.temporal_stamp = datetime.now().isoformat()
        if self.symbolic_hash is None:
            # Generate a simple hash for symbolic identification
            self.symbolic_hash = f"concept_{hash(self.concept) % 10000:04d}"


class SymbolicKnowledgeLoader:
    """
    🧠 LUKHAS Symbolic Knowledge Base Loader

    Manages loading, normalization, and integration of foundational knowledge
    across the LUKHAS ecosystem with symbolic enrichment and affect mapping.
    """

    def __init__(self, base_path: Optional[str] = None):
        """Initialize the knowledge loader with optional base path."""
        self.base_path = (
            Path(base_path) if base_path else Path(__file__).parent.parent.parent
        )
        self.knowledge_cache: Dict[str, SymbolicConcept] = {}
        self.affect_mappings: Dict[str, str] = {}
        self.glyph_registry: Dict[str, List[str]] = {}

        # Default affect mappings for core concepts
        self._initialize_default_affect_mappings()

        logger.info(
            f"🔍 ΛTRACE: SymbolicKnowledgeLoader initialized with base path: {self.base_path}"
        )

    def _initialize_default_affect_mappings(self):
        """Initialize default affect tags for common concepts."""
        self.affect_mappings.update(
            {
                "consciousness": "wonder",
                "emotion": "resonance",
                "memory": "nostalgia",
                "fear": "anxiety",
                "collapse": "dread",
                "creativity": "inspiration",
                "learning": "curiosity",
                "empathy": "warmth",
                "problem": "tension",
                "solution": "relief",
                "understanding": "clarity",
                "confusion": "uncertainty",
                "success": "joy",
                "failure": "disappointment",
            }
        )

    def load_symbolic_ontology(
        self, path: Union[str, Path]
    ) -> Dict[str, SymbolicConcept]:
        """
        Load and normalize a symbolic ontology from JSON file.

        Args:
            path: Path to the knowledge base JSON file

        Returns:
            Dictionary of concept name to SymbolicConcept objects

        # ΛTRACE: Core knowledge loading operation
        """
        try:
            file_path = Path(path)
            logger.info(f"🔍 ΛTRACE: Loading symbolic ontology from {file_path}")

            if not file_path.exists():
                raise FileNotFoundError(f"Knowledge base file not found: {file_path}")

            with open(file_path, encoding="utf-8") as f:
                raw_data = json.load(f)

            concepts = {}
            for concept_name, concept_data in raw_data.items():
                # Handle both simple and complex concept structures
                if isinstance(concept_data, dict):
                    # Complex structure with definition and related terms
                    definition = concept_data.get(
                        "definition", f"Concept: {concept_name}"
                    )
                    related = concept_data.get("related", [])
                    affect_tag = concept_data.get(
                        "affect_tag", self._infer_affect_tag(concept_name)
                    )
                    importance = concept_data.get("importance", 5.0)
                    glyph_links = concept_data.get("glyph_links", [])
                else:
                    # Simple string definition
                    definition = str(concept_data)
                    related = []
                    affect_tag = self._infer_affect_tag(concept_name)
                    importance = 5.0
                    glyph_links = []

                concepts[concept_name] = SymbolicConcept(
                    concept=concept_name,
                    definition=definition,
                    affect_tag=affect_tag,
                    glyph_links=glyph_links,
                    importance=importance,
                    related=related,
                )

            # Update cache
            self.knowledge_cache.update(concepts)

            logger.info(f"🔍 ΛTRACE: Loaded {len(concepts)} concepts from {file_path}")
            return concepts

        except Exception as e:
            logger.error(
                f"🚨 ΛTRACE: Failed to load symbolic ontology from {path}: {e}"
            )
            raise

    def _infer_affect_tag(self, concept: str) -> str:
        """Infer appropriate affect tag for a concept."""
        concept_lower = concept.lower()

        # Check direct mappings first
        if concept_lower in self.affect_mappings:
            return self.affect_mappings[concept_lower]

        # Infer from keywords
        if any(word in concept_lower for word in ["fear", "anxiety", "worry"]):
            return "anxiety"
        elif any(word in concept_lower for word in ["joy", "happiness", "delight"]):
            return "joy"
        elif any(word in concept_lower for word in ["love", "affection", "care"]):
            return "warmth"
        elif any(word in concept_lower for word in ["anger", "rage", "fury"]):
            return "anger"
        elif any(word in concept_lower for word in ["sad", "grief", "sorrow"]):
            return "melancholy"
        elif any(word in concept_lower for word in ["creative", "innovation", "art"]):
            return "inspiration"
        elif any(word in concept_lower for word in ["learn", "study", "discover"]):
            return "curiosity"
        else:
            return "neutral"

    def normalize_knowledge_structure(
        self, concepts: Dict[str, SymbolicConcept]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Normalize concepts to unified LUKHAS structure.

        Args:
            concepts: Dictionary of SymbolicConcept objects

        Returns:
            Normalized structure for system integration

        # ΛTRACE: Knowledge normalization for cross-system compatibility
        """
        normalized = {}

        for concept_name, concept in concepts.items():
            normalized[concept_name] = {
                "concept": concept.concept,
                "definition": concept.definition,
                "affect_tag": concept.affect_tag,
                "glyph_links": concept.glyph_links,
                "importance": concept.importance,
                "related": concept.related,
                "symbolic_hash": concept.symbolic_hash,
                "temporal_stamp": concept.temporal_stamp,
                "system_integrations": {
                    "memory": True,  # Available for memory enrichment
                    "narrative": True,  # Available for story construction
                    "ethics": concept.importance
                    >= 7.0,  # High-importance concepts for ethics
                    "reasoning": len(concept.related)
                    > 2,  # Connected concepts for reasoning
                },
            }

        logger.info(
            f"🔍 ΛTRACE: Normalized {len(normalized)} concepts for system integration"
        )
        return normalized

    def merge_knowledge_bases(
        self, *knowledge_bases: Dict[str, SymbolicConcept]
    ) -> Dict[str, SymbolicConcept]:
        """
        Merge multiple knowledge bases with conflict resolution.

        Args:
            *knowledge_bases: Variable number of knowledge base dictionaries

        Returns:
            Merged knowledge base with resolved conflicts

        # ΛTRACE: Knowledge base consolidation operation
        """
        merged = {}
        conflict_log = []

        for kb_index, knowledge_base in enumerate(knowledge_bases):
            for concept_name, concept in knowledge_base.items():
                if concept_name in merged:
                    # Handle conflict - prioritize higher importance
                    existing = merged[concept_name]
                    if concept.importance > existing.importance:
                        conflict_log.append(
                            f"Replaced {concept_name}: {existing.importance} -> {concept.importance}"
                        )
                        merged[concept_name] = concept
                    else:
                        # Merge related terms and glyph links
                        existing.related = list(set(existing.related + concept.related))
                        existing.glyph_links = list(
                            set(existing.glyph_links + concept.glyph_links)
                        )
                        conflict_log.append(
                            f"Merged {concept_name}: Enhanced with additional relations"
                        )
                else:
                    merged[concept_name] = concept

        if conflict_log:
            logger.info(
                f"🔍 ΛTRACE: Knowledge merge conflicts resolved: {len(conflict_log)} items"
            )
            for log_entry in conflict_log[:5]:  # Log first 5 conflicts
                logger.info(f"  - {log_entry}")

        logger.info(
            f"🔍 ΛTRACE: Merged {len(knowledge_bases)} knowledge bases into {len(merged)} concepts"
        )
        return merged

    def get_concept(self, concept_name: str) -> Optional[SymbolicConcept]:
        """Retrieve a specific concept from the knowledge cache."""
        return self.knowledge_cache.get(concept_name)

    def search_concepts(self, query: str, limit: int = 10) -> List[SymbolicConcept]:
        """
        Search concepts by name, definition, or related terms.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching SymbolicConcept objects
        """
        query_lower = query.lower()
        matches = []

        for concept in self.knowledge_cache.values():
            # Check concept name
            if query_lower in concept.concept.lower():
                matches.append((concept, 3))  # High priority for name match
            # Check definition
            elif query_lower in concept.definition.lower():
                matches.append((concept, 2))  # Medium priority for definition match
            # Check related terms
            elif any(query_lower in term.lower() for term in concept.related):
                matches.append((concept, 1))  # Lower priority for related match

        # Sort by priority and importance
        matches.sort(key=lambda x: (x[1], x[0].importance), reverse=True)

        return [match[0] for match in matches[:limit]]

    def get_concepts_by_affect(self, affect_tag: str) -> List[SymbolicConcept]:
        """Get all concepts with a specific affect tag."""
        return [
            concept
            for concept in self.knowledge_cache.values()
            if concept.affect_tag == affect_tag
        ]

    def export_for_memory_system(self) -> Dict[str, Any]:
        """Export knowledge in format suitable for memory system integration."""
        return {
            "symbolic_enrichment": {
                concept.concept: {
                    "definition": concept.definition,
                    "affect_context": concept.affect_tag,
                    "symbolic_weight": concept.importance / 10.0,
                    "associative_links": concept.related,
                }
                for concept in self.knowledge_cache.values()
            },
            "metadata": {
                "total_concepts": len(self.knowledge_cache),
                "generation_timestamp": datetime.now().isoformat(),
                "integration_ready": True,
            },
        }

    def export_for_narrative_system(self) -> Dict[str, Any]:
        """Export knowledge in format suitable for narrative system integration."""
        return {
            "archetypal_concepts": {
                concept.concept: {
                    "symbolic_meaning": concept.definition,
                    "narrative_weight": concept.importance,
                    "emotional_resonance": concept.affect_tag,
                    "story_connections": concept.related,
                    "glyph_anchors": concept.glyph_links,
                }
                for concept in self.knowledge_cache.values()
                if concept.importance >= 6.0  # Higher threshold for narrative use
            },
            "concept_relationships": self._build_concept_graph(),
        }

    def export_for_ethics_system(self) -> Dict[str, Any]:
        """Export knowledge in format suitable for ethics system integration."""
        high_importance_concepts = {
            concept.concept: {
                "ethical_weight": concept.importance,
                "moral_implications": concept.definition,
                "associated_values": concept.related,
                "emotional_impact": concept.affect_tag,
            }
            for concept in self.knowledge_cache.values()
            if concept.importance >= 7.0  # High threshold for ethical considerations
        }

        return {
            "ethical_grounding": high_importance_concepts,
            "policy_concepts": self._extract_policy_relevant_concepts(),
            "compliance_keywords": list(high_importance_concepts.keys()),
        }

    def _build_concept_graph(self) -> Dict[str, List[str]]:
        """Build a graph of concept relationships."""
        graph = {}
        for concept in self.knowledge_cache.values():
            graph[concept.concept] = concept.related
        return graph

    def _extract_policy_relevant_concepts(self) -> List[str]:
        """Extract concepts relevant for policy and compliance."""
        policy_keywords = [
            "ethics",
            "responsibility",
            "privacy",
            "security",
            "safety",
            "trust",
            "transparency",
            "fairness",
            "justice",
            "harm",
            "benefit",
            "rights",
            "consent",
            "autonomy",
            "dignity",
        ]

        relevant = []
        for concept in self.knowledge_cache.values():
            if any(
                keyword in concept.concept.lower()
                or keyword in concept.definition.lower()
                for keyword in policy_keywords
            ):
                relevant.append(concept.concept)

        return relevant


# Convenience functions for direct usage
def load_symbolic_ontology(path: Union[str, Path]) -> Dict[str, SymbolicConcept]:
    """
    Convenience function to load a symbolic ontology.

    Args:
        path: Path to the knowledge base JSON file

    Returns:
        Dictionary of concept name to SymbolicConcept objects
    """
    loader = SymbolicKnowledgeLoader()
    return loader.load_symbolic_ontology(path)


def normalize_knowledge_structure(
    concepts: Dict[str, SymbolicConcept],
) -> Dict[str, Dict[str, Any]]:
    """
    Convenience function to normalize knowledge structure.

    Args:
        concepts: Dictionary of SymbolicConcept objects

    Returns:
        Normalized structure for system integration
    """
    loader = SymbolicKnowledgeLoader()
    return loader.normalize_knowledge_structure(concepts)


def merge_knowledge_bases(
    *knowledge_bases: Dict[str, SymbolicConcept]
) -> Dict[str, SymbolicConcept]:
    """
    Convenience function to merge multiple knowledge bases.

    Args:
        *knowledge_bases: Variable number of knowledge base dictionaries

    Returns:
        Merged knowledge base with resolved conflicts
    """
    loader = SymbolicKnowledgeLoader()
    return loader.merge_knowledge_bases(*knowledge_bases)


# CLAUDE CHANGELOG
# - Created comprehensive symbolic knowledge loader for Task 17 foundational knowledge integration # CLAUDE_EDIT_v1.0
# - Implemented unified knowledge structure with affect mapping and glyph linking # CLAUDE_EDIT_v1.1
# - Added cross-system export methods for memory, narrative, and ethics integration # CLAUDE_EDIT_v1.2

"""
═══════════════════════════════════════════════════════════════════════════════
║ COPYRIGHT & LICENSE:
║   Copyright (c) 2025 LUKHAS AI. All rights reserved.
║   Licensed under the LUKHAS AI Proprietary License.
╚═══════════════════════════════════════════════════════════════════════════════
"""
