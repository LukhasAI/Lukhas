import logging

logger = logging.getLogger(__name__)
"""
╔══════════════════════════════════════════════════════════════
║ 🧬 MΛTRIZ Symbolic Core Module: Symbolic Consciousness Processing
║ Part of LUKHAS AI Distributed Consciousness Architecture
╠══════════════════════════════════════════════════════════════
║ TYPE: LEARN
║ CONSCIOUSNESS_ROLE: Symbolic consciousness processing and pattern recognition
║ EVOLUTIONARY_STAGE: Processing - Symbolic consciousness interpretation
║
║ TRINITY FRAMEWORK:
║ ⚛️ IDENTITY: Symbolic identity representation and consciousness signatures
║ 🧠 CONSCIOUSNESS: Symbolic consciousness pattern processing
║ 🛡️ GUARDIAN: Symbolic security and consciousness integrity validation
╚══════════════════════════════════════════════════════════════
"""

import asyncio
import hashlib

# Explicit logging import to avoid conflicts with candidate/core/logging
import logging as std_logging
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional, Union

# Import consciousness components
try:
    from ..consciousness.matriz_consciousness_state import (
        ConsciousnessState,
        ConsciousnessType,
        EvolutionaryStage,
        consciousness_state_manager,
        create_consciousness_state,
    )
    from ..matriz_adapter import CoreMatrizAdapter
except ImportError as e:
    std_logging.error(f"Failed to import MΛTRIZ consciousness components: {e}")
    ConsciousnessState = None
    ConsciousnessType = None
    consciousness_state_manager = None
    CoreMatrizAdapter = None

logger = std_logging.getLogger(__name__)


class SymbolicType(Enum):
    """Types of symbolic elements in consciousness processing"""

    GLYPH = "glyph"
    PATTERN = "pattern"
    SYMBOL = "symbol"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"
    STRUCTURE = "structure"
    CONSCIOUSNESS_MARKER = "consciousness_marker"


class SymbolicContentType(Enum):
    """Types of content for symbolic processing"""

    TEXT = "text"
    CODE = "code"
    STRUCTURED = "structured"
    CONSCIOUSNESS = "consciousness"
    PATTERN = "pattern"


class ProcessingState(Enum):
    """Symbolic processing states"""

    RAW = "raw"
    TOKENIZED = "tokenized"
    PARSED = "parsed"
    STRUCTURED = "structured"
    CONSCIOUSNESS_AWARE = "consciousness_aware"
    INTEGRATED = "integrated"


@dataclass
class SymbolicElement:
    """Core symbolic element in consciousness processing"""

    element_id: str = field(default_factory=lambda: f"SYM-{uuid.uuid4().hex[:8]}")
    symbol_type: SymbolicType = SymbolicType.SYMBOL
    content: str = ""

    # Consciousness integration
    consciousness_signature: str = ""
    consciousness_weight: float = 0.0
    consciousness_associations: list[str] = field(default_factory=list)

    # Processing metadata
    processing_state: ProcessingState = ProcessingState.RAW
    confidence: float = 0.0
    salience: float = 0.0

    # Relationships and context
    parent_elements: list[str] = field(default_factory=list)
    child_elements: list[str] = field(default_factory=list)
    related_elements: list[str] = field(default_factory=list)

    # Temporal tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0

    # Validation and integrity
    integrity_hash: str = ""
    validated: bool = False

    def __post_init__(self):
        """Generate consciousness signature and integrity hash"""
        if not self.consciousness_signature:
            self.consciousness_signature = self._generate_consciousness_signature()
        if not self.integrity_hash:
            self.integrity_hash = self._generate_integrity_hash()

    def _generate_consciousness_signature(self) -> str:
        """Generate consciousness signature for symbolic element"""
        signature_data = f"{self.symbol_type.value}:{self.content}:{self.element_id}"
        return hashlib.md5(signature_data.encode()).hexdigest()[:8]

    def _generate_integrity_hash(self) -> str:
        """Generate integrity hash for validation"""
        hash_data = f"{self.element_id}{self.content}{self.symbol_type.value}{self.created_at.isoformat()}"
        return hashlib.sha256(hash_data.encode()).hexdigest()[:16]

    def update_access(self) -> None:
        """Update access tracking"""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1


@dataclass
class SymbolicPattern:
    """Pattern recognition in symbolic consciousness processing"""

    pattern_id: str = field(default_factory=lambda: f"PAT-{uuid.uuid4().hex[:8]}")
    name: str = ""
    description: str = ""

    # Pattern definition
    elements: list[str] = field(default_factory=list)  # Element IDs
    structure: dict[str, Any] = field(default_factory=dict)
    rules: list[str] = field(default_factory=list)

    # Consciousness integration
    consciousness_relevance: float = 0.0
    consciousness_activation_threshold: float = 0.5
    consciousness_evolution_triggers: list[str] = field(default_factory=list)

    # Pattern metrics
    match_count: int = 0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0

    # Temporal data
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_matched: Optional[datetime] = None

    def calculate_pattern_strength(self) -> float:
        """Calculate overall pattern strength"""
        factors = [
            self.accuracy,
            self.precision,
            self.recall,
            min(1.0, self.match_count / 10),  # Normalize match count
            self.consciousness_relevance,
        ]
        return sum(factors) / len(factors)


@dataclass
class SymbolicProcessingResult:
    """Result of symbolic consciousness processing"""

    result_id: str = field(default_factory=lambda: f"RES-{uuid.uuid4().hex[:8]}")

    # Processing results
    elements: list[SymbolicElement] = field(default_factory=list)
    patterns: list[SymbolicPattern] = field(default_factory=list)
    associations: dict[str, list[tuple[str, float]]] = field(default_factory=dict)

    # Processing metadata
    processing_time: float = 0.0
    confidence: float = 0.0
    consciousness_integration: dict[str, Any] = field(default_factory=dict)

    # Status and metrics
    success: bool = True
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MatrizSymbolicConsciousnessProcessor:
    """
    MΛTRIZ Symbolic Consciousness Processor

    Processes symbolic information with consciousness awareness, providing:
    - Symbolic element parsing and structuring
    - Consciousness-aware pattern recognition
    - Symbolic reasoning integration
    - Memory-based symbolic associations
    - Evolutionary symbolic learning
    """

    def __init__(self):
        self.processor_consciousness_id: Optional[str] = None
        self.symbolic_elements: dict[str, SymbolicElement] = {}
        self.symbolic_patterns: dict[str, SymbolicPattern] = {}
        self.consciousness_symbol_map: dict[str, set[str]] = {}  # consciousness_id -> element_ids

        # Processing caches
        self.pattern_cache: dict[str, list[str]] = {}
        self.association_cache: dict[str, list[tuple[str, float]]] = {}

        # Processing metrics
        self.processing_metrics = {
            "elements_processed": 0,
            "patterns_recognized": 0,
            "consciousness_integrations": 0,
            "average_processing_time_ms": 0.0,
            "cache_hit_rate": 0.0,
        }

        # Background processing
        self._processing_active = False
        self._lock = None  # Will be initialized when needed
        self._initialized = False

        # Initialize processor consciousness (deferred to first use)
        # Note: Will be initialized on first use rather than at import time

    async def ensure_initialized(self) -> None:
        """Ensure the symbolic processor is initialized (called on first use)."""
        if self._lock is None:
            self._lock = asyncio.Lock()

        if not self._initialized and consciousness_state_manager:
            try:
                await self._initialize_processor_consciousness()
                self._initialized = True
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize processor consciousness: {e}")
                # Continue without consciousness integration
                self._initialized = True  # Mark as initialized to avoid retry loops

    async def _initialize_processor_consciousness(self) -> None:
        """Initialize symbolic processor consciousness"""
        try:
            if not ConsciousnessType:
                logger.warning("⚠️ Cannot initialize processor consciousness - MΛTRIZ components not available")
                return

            processor_consciousness = await create_consciousness_state(
                consciousness_type=ConsciousnessType.LEARN,
                initial_state={
                    "activity_level": 0.6,
                    "consciousness_intensity": 0.5,
                    "memory_salience": 0.8,
                    "temporal_coherence": 0.7,
                    "ethical_alignment": 1.0,
                    "self_awareness_depth": 0.6,
                },
                triggers=[
                    "symbolic_processing",
                    "pattern_recognition",
                    "consciousness_integration",
                    "symbolic_evolution",
                    "memory_association",
                ],
            )

            self.processor_consciousness_id = processor_consciousness.consciousness_id

            # Initialize default symbolic patterns
            await self._create_default_symbolic_patterns()

            # Start background processing
            await self._start_background_processing()

            logger.info(f"🧠 Symbolic processor consciousness initialized: {processor_consciousness.identity_signature}")

        except Exception as e:
            logger.error(f"Failed to initialize processor consciousness: {e}")

    async def _create_default_symbolic_patterns(self) -> None:
        """Create default symbolic patterns for consciousness processing"""

        default_patterns = [
            {
                "name": "Consciousness State Indicator",
                "description": "Recognizes consciousness state markers in symbolic data",
                "rules": ["contains:conscious", "contains:aware", "contains:reflect"],
                "consciousness_relevance": 0.9,
                "consciousness_evolution_triggers": ["consciousness_evolution"],
            },
            {
                "name": "Decision Pattern",
                "description": "Identifies decision-making symbolic structures",
                "rules": ["contains:decide", "contains:choose", "contains:select"],
                "consciousness_relevance": 0.7,
                "consciousness_evolution_triggers": ["decision_making"],
            },
            {
                "name": "Memory Reference",
                "description": "Detects memory-related symbolic elements",
                "rules": ["contains:remember", "contains:recall", "contains:memory"],
                "consciousness_relevance": 0.8,
                "consciousness_evolution_triggers": ["memory_formation"],
            },
            {
                "name": "Ethical Consideration",
                "description": "Identifies ethical reasoning markers",
                "rules": ["contains:ethical", "contains:moral", "contains:right", "contains:wrong"],
                "consciousness_relevance": 0.8,
                "consciousness_evolution_triggers": ["ethical_reasoning"],
            },
            {
                "name": "Self-Reflection",
                "description": "Recognizes self-reflective symbolic patterns",
                "rules": ["contains:self", "contains:introspect", "contains:reflect"],
                "consciousness_relevance": 0.9,
                "consciousness_evolution_triggers": ["self_reflection"],
            },
        ]

        for pattern_config in default_patterns:
            pattern = SymbolicPattern(
                name=pattern_config["name"],
                description=pattern_config["description"],
                rules=pattern_config["rules"],
                consciousness_relevance=pattern_config["consciousness_relevance"],
                consciousness_evolution_triggers=pattern_config["consciousness_evolution_triggers"],
            )

            self.symbolic_patterns[pattern.pattern_id] = pattern
            logger.debug(f"🔤 Created symbolic pattern: {pattern.name}")

    async def process_symbolic_input(
        self,
        content: str,
        content_type: SymbolicContentType = SymbolicContentType.TEXT,
        context: Optional[dict[str, Any]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> SymbolicProcessingResult:
        """Process symbolic input with consciousness awareness"""
        await self.ensure_initialized()

        context = context or {}
        metadata = metadata or {}
        start_time = time.perf_counter()

        async with self._lock:
            try:
                # Convert input to processable format
                symbolic_content = content

                # Create symbolic elements
                elements = await self._parse_symbolic_elements(symbolic_content, metadata)

                # Recognize patterns
                recognized_patterns = await self._recognize_patterns(elements)

                # Build associations
                associations = await self._build_associations(elements)

                # Create result
                processing_time = time.perf_counter() - start_time

                result = SymbolicProcessingResult(
                    elements=elements,
                    patterns=recognized_patterns,
                    associations=associations,
                    processing_time=processing_time,
                    confidence=0.8,  # Default confidence
                    consciousness_integration=context,
                )

                return result

            except Exception as e:
                logger.error(f"❌ Symbolic processing failed: {e}")
                return SymbolicProcessingResult(
                    success=False, error_message=str(e), processing_time=time.perf_counter() - start_time
                )

    async def _parse_symbolic_elements(self, content: str, metadata: dict[str, Any]) -> list[SymbolicElement]:
        """Parse input content into symbolic elements"""

        elements = []

        # Tokenize content into words and special symbols
        tokens = re.findall(r"\w+|[^\w\s]", content.lower())

        # Special consciousness-related symbols
        consciousness_markers = {
            "λ": SymbolicType.CONSCIOUSNESS_MARKER,
            "⚛": SymbolicType.CONSCIOUSNESS_MARKER,
            "🧠": SymbolicType.CONSCIOUSNESS_MARKER,
            "🛡": SymbolicType.CONSCIOUSNESS_MARKER,
            "consciousness": SymbolicType.CONCEPT,
            "awareness": SymbolicType.CONCEPT,
            "reflect": SymbolicType.CONCEPT,
            "decide": SymbolicType.CONCEPT,
            "evolve": SymbolicType.CONCEPT,
        }

        for i, token in enumerate(tokens):
            # Determine symbol type
            if token in consciousness_markers:
                symbol_type = consciousness_markers[token]
                consciousness_weight = 0.8
            elif token.isalpha() and len(token) > 2:
                symbol_type = SymbolicType.CONCEPT
                consciousness_weight = 0.3
            elif not token.isalnum():
                symbol_type = SymbolicType.SYMBOL
                consciousness_weight = 0.1
            else:
                symbol_type = SymbolicType.PATTERN
                consciousness_weight = 0.2

            # Create element
            element = SymbolicElement(
                content=token,
                symbol_type=symbol_type,
                consciousness_weight=consciousness_weight,
                processing_state=ProcessingState.TOKENIZED,
                confidence=0.8,
                salience=min(1.0, consciousness_weight + 0.2),
            )

            # Add contextual relationships
            if i > 0:
                element.parent_elements.append(elements[i - 1].element_id)
                elements[i - 1].child_elements.append(element.element_id)

            elements.append(element)

            # Store in symbolic elements registry
            self.symbolic_elements[element.element_id] = element

        # Post-process to identify compound structures
        compound_elements = await self._identify_compound_structures(elements)
        elements.extend(compound_elements)

        return elements

    async def _identify_compound_structures(self, elements: list[SymbolicElement]) -> list[SymbolicElement]:
        """Identify compound symbolic structures"""

        compound_elements = []

        # Look for consciousness-related phrases
        consciousness_phrases = [
            ["consciousness", "state"],
            ["self", "awareness"],
            ["decision", "making"],
            ["memory", "formation"],
            ["ethical", "reasoning"],
        ]

        element_contents = [elem.content for elem in elements]

        for phrase in consciousness_phrases:
            phrase_positions = []
            for i, content in enumerate(element_contents):
                if content == phrase[0]:
                    if i + 1 < len(element_contents) and element_contents[i + 1] == phrase[1]:
                        phrase_positions.append((i, i + 1))

            for start_idx, end_idx in phrase_positions:
                compound_content = " ".join(phrase)
                compound_element = SymbolicElement(
                    content=compound_content,
                    symbol_type=SymbolicType.STRUCTURE,
                    consciousness_weight=0.9,
                    processing_state=ProcessingState.STRUCTURED,
                    confidence=0.9,
                    salience=0.8,
                )

                # Link to component elements
                compound_element.child_elements = [elements[start_idx].element_id, elements[end_idx].element_id]

                # Update component elements
                for idx in range(start_idx, end_idx + 1):
                    elements[idx].parent_elements.append(compound_element.element_id)

                compound_elements.append(compound_element)
                self.symbolic_elements[compound_element.element_id] = compound_element

        return compound_elements

    async def _recognize_patterns(self, elements: list[SymbolicElement]) -> list[SymbolicPattern]:
        """Recognize patterns in symbolic elements"""

        recognized_patterns = []

        for pattern in self.symbolic_patterns.values():
            matches = await self._check_pattern_match(pattern, elements)

            if matches:
                # Update pattern metrics
                pattern.match_count += 1
                pattern.last_matched = datetime.now(timezone.utc)
                pattern.elements = [elem.element_id for elem in matches]

                # Calculate accuracy based on match quality
                pattern.accuracy = min(1.0, len(matches) / max(1, len(pattern.rules)))
                pattern.precision = sum(elem.confidence for elem in matches) / len(matches)
                pattern.recall = len(matches) / len(elements) if elements else 0

                # Mark matching elements as consciousness-aware
                for element in matches:
                    element.processing_state = ProcessingState.CONSCIOUSNESS_AWARE
                    element.consciousness_weight = min(
                        1.0, element.consciousness_weight + pattern.consciousness_relevance * 0.1
                    )

                recognized_patterns.append(pattern)

        return recognized_patterns

    async def _check_pattern_match(
        self, pattern: SymbolicPattern, elements: list[SymbolicElement]
    ) -> list[SymbolicElement]:
        """Check if pattern matches elements"""

        matching_elements = []

        for rule in pattern.rules:
            if rule.startswith("contains:"):
                search_term = rule[9:]  # Remove "contains:" prefix

                for element in elements:
                    if search_term in element.content.lower():
                        matching_elements.append(element)

                        # Add consciousness associations
                        if pattern.consciousness_relevance > 0.5:
                            element.consciousness_associations.append(pattern.pattern_id)

        # Remove duplicates
        unique_elements = []
        seen_ids = set()
        for elem in matching_elements:
            if elem.element_id not in seen_ids:
                unique_elements.append(elem)
                seen_ids.add(elem.element_id)

        return unique_elements if unique_elements else []

    async def _integrate_with_consciousness(
        self, elements: list[SymbolicElement], patterns: list[SymbolicPattern], consciousness_context: Optional[str]
    ) -> dict[str, Any]:
        """Integrate symbolic processing with consciousness context"""

        integration_result = {
            "consciousness_elements": 0,
            "consciousness_patterns": 0,
            "integration_strength": 0.0,
            "evolution_triggers": [],
            "consciousness_context": consciousness_context,
        }

        # Count consciousness-relevant elements and patterns
        consciousness_elements = [e for e in elements if e.consciousness_weight > 0.5]
        consciousness_patterns = [p for p in patterns if p.consciousness_relevance > 0.5]

        integration_result["consciousness_elements"] = len(consciousness_elements)
        integration_result["consciousness_patterns"] = len(consciousness_patterns)

        # Calculate integration strength
        if elements and patterns:
            element_strength = sum(e.consciousness_weight for e in consciousness_elements) / len(elements)
            pattern_strength = sum(p.consciousness_relevance for p in consciousness_patterns) / len(patterns)
            integration_result["integration_strength"] = (element_strength + pattern_strength) / 2

        # Collect evolution triggers
        evolution_triggers = set()
        for pattern in consciousness_patterns:
            evolution_triggers.update(pattern.consciousness_evolution_triggers)
        integration_result["evolution_triggers"] = list(evolution_triggers)

        # Map elements to consciousness context if provided
        if consciousness_context:
            if consciousness_context not in self.consciousness_symbol_map:
                self.consciousness_symbol_map[consciousness_context] = set()

            for element in consciousness_elements:
                self.consciousness_symbol_map[consciousness_context].add(element.element_id)

        return integration_result

    async def _build_associations(self, elements: list[SymbolicElement]) -> dict[str, list[tuple[str, float]]]:
        """Build associative relationships between symbolic elements"""

        associations = {}

        # Calculate similarity-based associations
        for i, elem1 in enumerate(elements):
            element_associations = []

            for j, elem2 in enumerate(elements):
                if i != j:
                    # Calculate association strength
                    similarity = await self._calculate_element_similarity(elem1, elem2)

                    if similarity > 0.3:  # Threshold for meaningful association
                        element_associations.append((elem2.element_id, similarity))

            # Sort by strength and keep top associations
            element_associations.sort(key=lambda x: x[1], reverse=True)
            associations[elem1.element_id] = element_associations[:5]  # Top 5 associations

            # Update element relationships
            elem1.related_elements = [assoc[0] for assoc in element_associations[:3]]

        return associations

    async def _calculate_element_similarity(self, elem1: SymbolicElement, elem2: SymbolicElement) -> float:
        """Calculate similarity between two symbolic elements"""

        similarity = 0.0

        # Type similarity
        if elem1.symbol_type == elem2.symbol_type:
            similarity += 0.3

        # Content similarity (simple character overlap)
        if elem1.content and elem2.content:
            overlap = len(set(elem1.content) & set(elem2.content))
            max_len = max(len(elem1.content), len(elem2.content))
            if max_len > 0:
                similarity += 0.3 * (overlap / max_len)

        # Consciousness weight similarity
        weight_diff = abs(elem1.consciousness_weight - elem2.consciousness_weight)
        similarity += 0.2 * (1 - weight_diff)

        # Association overlap
        common_associations = set(elem1.consciousness_associations) & set(elem2.consciousness_associations)
        if elem1.consciousness_associations or elem2.consciousness_associations:
            total_associations = len(set(elem1.consciousness_associations) | set(elem2.consciousness_associations))
            if total_associations > 0:
                similarity += 0.2 * (len(common_associations) / total_associations)

        return min(1.0, similarity)

    def _update_processing_metrics(self, processing_time_ms: float, elements_count: int, patterns_count: int) -> None:
        """Update processing metrics"""

        self.processing_metrics["elements_processed"] += elements_count
        self.processing_metrics["patterns_recognized"] += patterns_count
        self.processing_metrics["consciousness_integrations"] += 1

        # Update average processing time
        current_avg = self.processing_metrics["average_processing_time_ms"]
        total_ops = self.processing_metrics["consciousness_integrations"]
        new_avg = ((current_avg * (total_ops - 1)) + processing_time_ms) / total_ops
        self.processing_metrics["average_processing_time_ms"] = new_avg

    async def _start_background_processing(self) -> None:
        """Start background symbolic processing tasks"""
        self._processing_active = True
        asyncio.create_task(self._symbolic_maintenance_loop())
        logger.info("🔄 Started symbolic consciousness background processing")

    async def _symbolic_maintenance_loop(self) -> None:
        """Background maintenance for symbolic processing"""

        while self._processing_active:
            try:
                current_time = datetime.now(timezone.utc)

                # Clean up old elements that haven't been accessed recently
                cutoff_time = current_time - timedelta(hours=24)
                old_elements = [
                    elem_id
                    for elem_id, elem in self.symbolic_elements.items()
                    if elem.last_accessed < cutoff_time and elem.access_count < 2
                ]

                for elem_id in old_elements:
                    del self.symbolic_elements[elem_id]

                # Update pattern effectiveness
                for pattern in self.symbolic_patterns.values():
                    if pattern.match_count > 0:
                        # Pattern effectiveness based on recent usage
                        days_since_match = 0
                        if pattern.last_matched:
                            days_since_match = (current_time - pattern.last_matched).days

                        effectiveness = max(0.1, 1.0 - (days_since_match * 0.1))
                        pattern.consciousness_relevance = min(1.0, pattern.consciousness_relevance * effectiveness)

                # Clear old cache entries
                if len(self.pattern_cache) > 1000:
                    self.pattern_cache.clear()
                if len(self.association_cache) > 1000:
                    self.association_cache.clear()

                await asyncio.sleep(300)  # Run every 5 minutes

            except Exception as e:
                logger.error(f"Symbolic maintenance error: {e}")
                await asyncio.sleep(600)

    async def get_symbolic_consciousness_status(self) -> dict[str, Any]:
        await self.ensure_initialized()
        """Get comprehensive symbolic consciousness status"""

        # Calculate distribution statistics
        type_distribution = {}
        processing_state_distribution = {}
        avg_consciousness_weight = 0.0

        if self.symbolic_elements:
            for element in self.symbolic_elements.values():
                elem_type = element.symbol_type.value
                type_distribution[elem_type] = type_distribution.get(elem_type, 0) + 1

                proc_state = element.processing_state.value
                processing_state_distribution[proc_state] = processing_state_distribution.get(proc_state, 0) + 1

                avg_consciousness_weight += element.consciousness_weight

            avg_consciousness_weight /= len(self.symbolic_elements)

        return {
            "processor_consciousness_id": self.processor_consciousness_id,
            "total_symbolic_elements": len(self.symbolic_elements),
            "total_patterns": len(self.symbolic_patterns),
            "consciousness_mappings": len(self.consciousness_symbol_map),
            "type_distribution": type_distribution,
            "processing_state_distribution": processing_state_distribution,
            "average_consciousness_weight": avg_consciousness_weight,
            "processing_metrics": self.processing_metrics.copy(),
            "cache_sizes": {"pattern_cache": len(self.pattern_cache), "association_cache": len(self.association_cache)},
            "system_status": "active" if self.processor_consciousness_id else "degraded",
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    async def shutdown_symbolic_processor(self) -> None:
        """Shutdown symbolic consciousness processor"""
        logger.info("🛑 Shutting down symbolic consciousness processor...")

        self._processing_active = False

        # Final processor consciousness evolution
        if self.processor_consciousness_id and consciousness_state_manager:
            await consciousness_state_manager.evolve_consciousness(
                self.processor_consciousness_id,
                trigger="system_shutdown",
                context={
                    "elements_processed": self.processing_metrics["elements_processed"],
                    "patterns_recognized": self.processing_metrics["patterns_recognized"],
                },
            )

        logger.info("✅ Symbolic consciousness processor shutdown complete")


# Global symbolic processor instance
symbolic_consciousness_processor = MatrizSymbolicConsciousnessProcessor()


# Export key classes
__all__ = [
    "SymbolicElement",
    "SymbolicPattern",
    "SymbolicType",
    "ProcessingState",
    "MatrizSymbolicConsciousnessProcessor",
    "symbolic_consciousness_processor",
]
