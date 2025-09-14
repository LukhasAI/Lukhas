"""
LUKHΛS Entity Extractor
=======================

Extracts symbolic entities and metadata from natural language.
Works with Trinity Framework for deep understanding.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Types of entities that can be extracted."""

    USER = "user"
    MODULE = "module"
    GLYPH = "glyph"
    TIME = "time"
    METRIC = "metric"
    ACTION = "action"
    CONCEPT = "concept"
    TIER = "tier"


@dataclass
class Entity:
    """Extracted entity with metadata."""

    text: str
    type: EntityType
    value: Any
    confidence: float
    position: tuple[int, int]  # Start and end position in text
    metadata: dict[str, Any]


class EntityExtractor:
    """
    Extracts entities from natural language with symbolic understanding.
    """

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.glyph_registry = self._initialize_glyphs()
        self.module_registry = self._initialize_modules()
        self.concept_map = self._initialize_concepts()

    def _initialize_patterns(self) -> dict[EntityType, list[tuple[str, str]]]:
        """Initialize regex patterns for entity extraction."""
        return {
            EntityType.USER: [
                (r"@(\w+)", "username"),
                (r"user[:\s]+(\w+)", "username"),
                (r"(\w+@[\w.]+)", "email"),
            ],
            EntityType.MODULE: [
                (
                    r"\b(consciousness|memory|guardian|identity|quantum|emotion|dream|bio)\b",
                    "module_name",
                )
            ],
            EntityType.GLYPH: [(r"[⚛️🧠🛡️🔐🌍💭🔮✨🌟⚡🔍🔄🎭🌊⚠️]", "glyph_symbol")],
            EntityType.TIME: [
                (r"(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2})?)", "iso_date"),
                (r"(yesterday|today|tomorrow)", "relative_day"),
                (
                    r"(\d+)\s+(second|minute|hour|day|week|month)s?\s+ago",
                    "relative_past",
                ),
                (
                    r"last\s+(\d+)\s+(second|minute|hour|day|week|month)s?",
                    "relative_duration",
                ),
                (
                    r"in\s+(\d+)\s+(second|minute|hour|day|week|month)s?",
                    "relative_future",
                ),
            ],
            EntityType.METRIC: [
                (
                    r"(drift|constellation|entropy|coherence)\s*(?:score|level|value)?\s*[:\s]*([\d.]+)",
                    "metric_value",
                ),
                (r"(\d+(?:\.\d+)?)\s*%", "percentage"),
            ],
            EntityType.ACTION: [
                (
                    r"\b(query|search|explore|analyze|check|monitor|intervene|protect)\b",
                    "action_verb",
                )
            ],
            EntityType.TIER: [
                (r"\b[Tt](\d)\b", "tier_number"),
                (
                    r"\b(Observer|Participant|Contributor|Architect|Guardian)\b",
                    "tier_name",
                ),
            ],
        }

    def _initialize_glyphs(self) -> dict[str, dict[str, Any]]:
        """Initialize glyph registry with meanings."""
        return {
            "⚛️": {
                "name": "Identity",
                "type": "constellation",
                "meaning": "Core authentication and identity",
            },
            "🧠": {
                "name": "Consciousness",
                "type": "constellation",
                "meaning": "Awareness and cognition",
            },
            "🛡️": {
                "name": "Guardian",
                "type": "constellation",
                "meaning": "Protection and ethics",
            },
            "🔐": {
                "name": "Security",
                "type": "system",
                "meaning": "Access control layer",
            },
            "🌍": {
                "name": "Cultural",
                "type": "system",
                "meaning": "Global awareness",
            },
            "💭": {
                "name": "Memory",
                "type": "cognitive",
                "meaning": "Thought preservation",
            },
            "🔮": {
                "name": "Quantum",
                "type": "processing",
                "meaning": "Advanced computation",
            },
            "✨": {
                "name": "Dream",
                "type": "creative",
                "meaning": "Innovation state",
            },
            "🌟": {
                "name": "Ethics",
                "type": "alignment",
                "meaning": "Moral compass",
            },
            "⚡": {
                "name": "Intervention",
                "type": "action",
                "meaning": "Active correction",
            },
            "🔍": {
                "name": "Monitor",
                "type": "action",
                "meaning": "Observation mode",
            },
            "🔄": {
                "name": "Sync",
                "type": "action",
                "meaning": "Synchronization",
            },
            "🎭": {
                "name": "Persona",
                "type": "interface",
                "meaning": "Adaptive interaction",
            },
            "🌊": {
                "name": "Flow",
                "type": "state",
                "meaning": "Optimal performance",
            },
            "⚠️": {
                "name": "Warning",
                "type": "alert",
                "meaning": "Drift detection",
            },
        }

    def _initialize_modules(self) -> dict[str, dict[str, Any]]:
        """Initialize module registry."""
        return {
            "consciousness": {
                "glyphs": ["🧠", "👁️", "✨"],
                "tier_required": "T3",
            },
            "memory": {"glyphs": ["💭", "📚", "🔄"], "tier_required": "T2"},
            "guardian": {"glyphs": ["🛡️", "⚡", "⚖️"], "tier_required": "T5"},
            "identity": {"glyphs": ["⚛️", "🔐", "🎫"], "tier_required": "T1"},
            "quantum": {"glyphs": ["🔮", "⚛️", "∞"], "tier_required": "T4"},
            "emotion": {"glyphs": ["💗", "🎭", "🌊"], "tier_required": "T3"},
            "dream": {"glyphs": ["✨", "🌙", "💫"], "tier_required": "T3"},
            "bio": {"glyphs": ["🧬", "🌱", "♻️"], "tier_required": "T4"},
        }

    def _initialize_concepts(self) -> dict[str, list[str]]:
        """Initialize concept mappings."""
        return {
            "drift": ["deviation", "anomaly", "divergence", "misalignment"],
            "constellation": ["framework", "triad", "three-part", "triadic"],
            "intervention": [
                "correction",
                "adjustment",
                "remediation",
                "healing",
            ],
            "consciousness": ["awareness", "cognition", "sentience", "mind"],
            "memory": ["recollection", "remembrance", "fold", "trace"],
            "symbolic": ["glyph", "symbol", "token", "representation"],
        }

    def extract_entities(self, text: str) -> list[Entity]:
        """
        Extract all entities from text.

        Args:
            text: Input text to analyze

        Returns:
            List of extracted entities
        """
        entities = []

        # Extract each entity type
        for entity_type, patterns in self.patterns.items():
            for pattern, subtype in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = self._create_entity(match, entity_type, subtype, text)
                    if entity:
                        entities.append(entity)

        # Post-process and enrich entities
        entities = self._enrich_entities(entities, text)

        # Sort by position
        entities.sort(key=lambda e: e.position[0])

        return entities

    def _create_entity(
        self,
        match: re.Match,
        entity_type: EntityType,
        subtype: str,
        full_text: str,
    ) -> Optional[Entity]:
        """Create entity from regex match."""
        text = match.group(0)
        value = self._extract_value(match, entity_type, subtype)

        if value is None:
            return None

        metadata = self._extract_metadata(match, entity_type, subtype, full_text)

        return Entity(
            text=text,
            type=entity_type,
            value=value,
            confidence=self._calculate_confidence(match, entity_type, full_text),
            position=(match.start(), match.end()),
            metadata=metadata,
        )

    def _extract_value(self, match: re.Match, entity_type: EntityType, subtype: str) -> Any:
        """Extract the actual value from the match."""
        if entity_type == EntityType.TIME:
            return self._parse_time_value(match, subtype)
        elif entity_type == EntityType.METRIC:
            return self._parse_metric_value(match, subtype)
        elif entity_type == EntityType.TIER:
            return self._parse_tier_value(match, subtype)
        elif entity_type == EntityType.GLYPH:
            return match.group(0)
        else:
            # For most entities, use the first captured group or whole match
            return match.group(1) if match.groups() else match.group(0)

    def _parse_time_value(self, match: re.Match, subtype: str) -> Optional[datetime]:
        """Parse time-related values."""
        try:
            if subtype == "iso_date":
                date_str = match.group(1)
                if "T" in date_str:
                    return datetime.fromisoformat(date_str)
                else:
                    return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)

            elif subtype == "relative_day":
                day = match.group(0).lower()
                now = datetime.now(timezone.utc)
                if day == "yesterday":
                    return now - timedelta(days=1)
                elif day == "today":
                    return now
                elif day == "tomorrow":
                    return now + timedelta(days=1)

            elif subtype in ["relative_past", "relative_duration"]:
                amount = int(match.group(1))
                unit = match.group(2).lower()
                delta_kwargs = {f"{unit}s": amount}
                return datetime.now(timezone.utc) - timedelta(**delta_kwargs)

            elif subtype == "relative_future":
                amount = int(match.group(1))
                unit = match.group(2).lower()
                delta_kwargs = {f"{unit}s": amount}
                return datetime.now(timezone.utc) + timedelta(**delta_kwargs)

        except Exception as e:
            logger.warning(f"Failed to parse time value: {e}")
            return None

    def _parse_metric_value(self, match: re.Match, subtype: str) -> Optional[float]:
        """Parse metric values."""
        try:
            if subtype == "metric_value":
                return float(match.group(2))
            elif subtype == "percentage":
                return float(match.group(1)) / 100.0
        except Exception as e:
            logger.warning(f"Failed to parse metric value: {e}")
            return None

    def _parse_tier_value(self, match: re.Match, subtype: str) -> dict[str, Any]:
        """Parse tier values."""
        if subtype == "tier_number":
            tier_num = int(match.group(1))
            tier_names = {
                1: "Observer",
                2: "Participant",
                3: "Contributor",
                4: "Architect",
                5: "Guardian",
            }
            return {
                "number": tier_num,
                "name": tier_names.get(tier_num, "Unknown"),
                "code": f"T{tier_num}",
            }
        else:  # tier_name
            tier_name = match.group(0)
            tier_numbers = {
                "Observer": 1,
                "Participant": 2,
                "Contributor": 3,
                "Architect": 4,
                "Guardian": 5,
            }
            tier_num = tier_numbers.get(tier_name, 0)
            return {
                "number": tier_num,
                "name": tier_name,
                "code": f"T{tier_num}" if tier_num else "Unknown",
            }

    def _extract_metadata(
        self,
        match: re.Match,
        entity_type: EntityType,
        subtype: str,
        full_text: str,
    ) -> dict[str, Any]:
        """Extract additional metadata for the entity."""
        metadata = {"subtype": subtype}

        if entity_type == EntityType.GLYPH:
            glyph = match.group(0)
            if glyph in self.glyph_registry:
                metadata.update(self.glyph_registry[glyph])

        elif entity_type == EntityType.MODULE:
            module = match.group(0).lower()
            if module in self.module_registry:
                metadata.update(self.module_registry[module])

        # Add context
        context_start = max(0, match.start() - 20)
        context_end = min(len(full_text), match.end() + 20)
        metadata["context"] = full_text[context_start:context_end]

        return metadata

    def _calculate_confidence(self, match: re.Match, entity_type: EntityType, full_text: str) -> float:
        """Calculate confidence score for extracted entity."""
        base_confidence = 0.7

        # Exact matches get higher confidence
        if match.group(0) == match.group(0).strip():
            base_confidence += 0.1

        # Known entities get higher confidence
        if (entity_type == EntityType.GLYPH and match.group(0) in self.glyph_registry) or (
            entity_type == EntityType.MODULE and match.group(0).lower() in self.module_registry
        ):
            base_confidence += 0.2

        return min(1.0, base_confidence)

    def _enrich_entities(self, entities: list[Entity], text: str) -> list[Entity]:
        """Enrich entities with relationships and additional context."""
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            if entity.type not in entities_by_type:
                entities_by_type[entity.type] = []
            entities_by_type[entity.type].append(entity)

        # Link related concepts
        for entity in entities:
            if entity.type == EntityType.CONCEPT:
                concept = entity.value.lower()
                if concept in self.concept_map:
                    entity.metadata["related_concepts"] = self.concept_map[concept]

        return entities

    def extract_symbolic_context(self, text: str) -> dict[str, Any]:
        """
        Extract comprehensive symbolic context from text.

        Returns dictionary with categorized entities and relationships.
        """
        entities = self.extract_entities(text)

        context = {
            "glyphs": [],
            "modules": [],
            "users": [],
            "times": [],
            "metrics": [],
            "actions": [],
            "tiers": [],
            "concepts": [],
            "triad_components": set(),
        }

        # Categorize entities
        for entity in entities:
            if entity.type == EntityType.GLYPH:
                context["glyphs"].append(
                    {
                        "symbol": entity.value,
                        "meaning": entity.metadata.get("meaning", "Unknown"),
                        "type": entity.metadata.get("type", "Unknown"),
                    }
                )
                # Check for Trinity components
                if entity.value in ["⚛️", "🧠", "🛡️"]:
                    context["triad_components"].add(entity.metadata.get("name", ""))

            elif entity.type == EntityType.MODULE:
                context["modules"].append(
                    {
                        "name": entity.value,
                        "glyphs": entity.metadata.get("glyphs", []),
                        "tier_required": entity.metadata.get("tier_required", "T1"),
                    }
                )

            elif entity.type == EntityType.USER:
                context["users"].append(
                    {
                        "identifier": entity.value,
                        "type": entity.metadata.get("subtype", "unknown"),
                    }
                )

            elif entity.type == EntityType.TIME:
                context["times"].append(
                    {
                        "text": entity.text,
                        "datetime": (entity.value.isoformat() if entity.value else None),
                        "type": entity.metadata.get("subtype", "unknown"),
                    }
                )

            elif entity.type == EntityType.METRIC:
                metric_name = "unknown"
                if entity.metadata.get("subtype") == "metric_value" and entity.text:
                    # Extract metric name from text
                    metric_match = re.search(r"(\w+)\s*(?:score|level|value)?", entity.text)
                    if metric_match:
                        metric_name = metric_match.group(1)

                context["metrics"].append(
                    {
                        "name": metric_name,
                        "value": entity.value,
                        "text": entity.text,
                    }
                )

            elif entity.type == EntityType.ACTION:
                context["actions"].append(entity.value)

            elif entity.type == EntityType.TIER:
                context["tiers"].append(entity.value)

        # Convert constellation components set to list
        context["triad_components"] = list(context["triad_components"])

        # Add summary
        context["summary"] = {
            "has_triad_reference": len(context["triad_components"]) > 0,
            "glyph_count": len(context["glyphs"]),
            "module_count": len(context["modules"]),
            "has_time_reference": len(context["times"]) > 0,
            "has_metrics": len(context["metrics"]) > 0,
        }

        return context


# Global extractor instance
entity_extractor = EntityExtractor()
