#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - UNIFIED MEMORY ORCHESTRATOR
║ Bio-inspired memory system with Hippocampal-Neocortical consolidation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: unified_memory_orchestrator.py
║ Path: memory/core/unified_memory_orchestrator.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Memory Consolidation Team
╠══════════════════════════════════════════════════════════════════════════════════
║ ΛTAG: ΛMEMORY, ΛORCHESTRATOR, ΛHIPPOCAMPAL, ΛNEOCORTICAL, ΛCONSOLIDATION
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import contextlib
import hashlib
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Union

import numpy as np

# Import logging
from candidate.core.common import get_logger

logger = get_logger(__name__)

# Import LUKHAS components
try:
    from ..integrity.collapse_hash import CollapseHash
    from ..protection.symbolic_quarantine_sanctum import SymbolicQuarantineSanctum
    from ..scaffold.atomic_memory_scaffold import AtomicMemoryScaffold
    from ..symbol_aware_tiered_memory import SymbolAwareTieredMemory
    from ..systems.colony_swarm_integration import SwarmConsensusManager
    from ..systems.distributed_memory_fold import DistributedMemoryFold

    LUKHAS_COMPONENTS_AVAILABLE = True
except ImportError:
    LUKHAS_COMPONENTS_AVAILABLE = False
    # Fallback imports for development
    SymbolAwareTieredMemory = object
    AtomicMemoryScaffold = object
    CollapseHash = object
    SymbolicQuarantineSanctum = object
    SwarmConsensusManager = object
    DistributedMemoryFold = object

# Import memory system components
try:
    # Import through interface to break circular dependency
    from candidate.core.interfaces.memory_interface import get_test_module

    from ..consolidation.consolidation_orchestrator import (
        ConsolidationOrchestrator,
        SleepStage,
    )
    from ..hippocampal.hippocampal_buffer import HippocampalBuffer
    from ..neocortical.neocortical_network import NeocorticalNetwork
    from .colony_memory_validator import ColonyMemoryValidator, ValidationMode
    from .interfaces import (
        EpisodicMemoryInterface,
        MemoryOperation,
        MemoryType,
        SemanticMemoryInterface,
        memory_registry,
    )

    MEMORY_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Memory components not available: {e}")
    MEMORY_COMPONENTS_AVAILABLE = False
    # Stubs for development
    HippocampalBuffer = object
    NeocorticalNetwork = object
    ConsolidationOrchestrator = object
    EpisodicMemoryInterface = object
    SemanticMemoryInterface = object
    ColonyMemoryValidator = object

    # Add test function stubs
    def test_memory_lifecycle(orchestrator):
        return {"status": "error", "message": "Memory components not available"}

    def test_error_conditions(orchestrator):
        return {"status": "error", "message": "Memory components not available"}


class MemoryType(Enum):
    """Types of memory in the unified system"""

    EPISODIC = "episodic"  # Specific events and experiences
    SEMANTIC = "semantic"  # General knowledge and concepts
    EMOTIONAL = "emotional"  # Affective states and associations
    PROCEDURAL = "procedural"  # Skills and how-to knowledge
    WORKING = "working"  # Active short-term memory
    DECLARATIVE = "declarative"  # Facts and information
    SENSORY = "sensory"  # Raw sensory impressions
    META = "meta"  # Memory about memories


class ConsolidationState(Enum):
    """States of memory consolidation"""

    ENCODING = "encoding"  # Initial capture in hippocampus
    CONSOLIDATING = "consolidating"  # Transfer to neocortex
    CONSOLIDATED = "consolidated"  # Stable in neocortex
    RECONSOLIDATING = "reconsolidating"  # Updating existing memory
    FORGETTING = "forgetting"  # Gradual decay


class SleepStage(Enum):
    """Sleep stages for memory consolidation"""

    AWAKE = "awake"
    NREM1 = "nrem1"  # Light sleep
    NREM2 = "nrem2"  # Sleep spindles
    NREM3 = "nrem3"  # Slow-wave sleep (SWS)
    REM = "rem"  # Rapid eye movement


@dataclass
class MemoryTrace:
    """Represents a memory trace in the system"""

    memory_id: str
    content: Any
    memory_type: MemoryType
    encoding_strength: float = 1.0
    consolidation_state: ConsolidationState = ConsolidationState.ENCODING
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    hippocampal_index: Optional[int] = None
    neocortical_indices: list[int] = field(default_factory=list)
    emotional_valence: float = 0.0  # -1 to 1
    semantic_links: set[str] = field(default_factory=set)
    colony_validations: dict[str, float] = field(default_factory=dict)
    replay_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "encoding_strength": self.encoding_strength,
            "consolidation_state": self.consolidation_state.value,
            "timestamp": self.timestamp.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "hippocampal_index": self.hippocampal_index,
            "neocortical_indices": self.neocortical_indices,
            "emotional_valence": self.emotional_valence,
            "semantic_links": list(self.semantic_links),
            "colony_validations": self.colony_validations,
            "replay_count": self.replay_count,
        }


@dataclass
class OscillationPattern:
    """Neural oscillation patterns for memory encoding"""

    theta_phase: float = 0.0  # 4-8 Hz (hippocampal)
    gamma_phase: float = 0.0  # 30-100 Hz (binding)
    ripple_amplitude: float = 0.0  # Sharp-wave ripples
    spindle_density: float = 0.0  # Sleep spindles
    slow_wave_power: float = 0.0  # Delta waves


class UnifiedMemoryOrchestrator:
    """
    Unified memory orchestrator implementing Hippocampal-Neocortical model
    with bio-inspired patterns and colony/swarm integration.

    This system coordinates:
    - Rapid episodic encoding (hippocampus)
    - Slow semantic consolidation (neocortex)
    - Sleep-cycle memory transfer
    - Colony-based validation
    - Distributed consensus
    - Emergent memory patterns
    """

    def __init__(
        self,
        hippocampal_capacity: int = 10000,
        neocortical_capacity: int = 1000000,
        consolidation_rate: float = 0.1,
        enable_colony_validation: bool = True,
        enable_distributed: bool = True,
        node_id: Optional[str] = None,
    ):
        self.hippocampal_capacity = hippocampal_capacity
        self.neocortical_capacity = neocortical_capacity
        self.consolidation_rate = consolidation_rate
        self.enable_colony_validation = enable_colony_validation
        self.enable_distributed = enable_distributed

        # Core memory systems with memory limits
        self.hippocampal_buffer: deque[MemoryTrace] = deque(maxlen=min(hippocampal_capacity, 1000))  # Limit to 1000
        self.neocortical_network: dict[str, MemoryTrace] = {}
        self.working_memory: dict[str, MemoryTrace] = {}

        # Memory limits for leak prevention
        self.max_neocortical_size = min(neocortical_capacity, 10000)  # Limit to 10K
        self.max_working_memory_size = 50  # Strict limit for working memory
        self.max_replay_buffer_size = 100
        self.max_consolidation_queue_size = 200

        # Indexing structures with size limits
        self.semantic_index: dict[str, set[str]] = defaultdict(set)
        self.temporal_index: dict[datetime, set[str]] = defaultdict(set)
        self.emotional_index: dict[float, set[str]] = defaultdict(set)
        self.max_index_entries = 1000  # Limit index size

        # Bio-inspired components
        self.oscillations = OscillationPattern()
        self.sleep_stage = SleepStage.AWAKE
        self.consolidation_queue: deque[str] = deque(maxlen=self.max_consolidation_queue_size)
        self.replay_buffer: list[MemoryTrace] = []

        # Background task management
        self.background_tasks: list = []

        # Initialize subsystems if available
        if LUKHAS_COMPONENTS_AVAILABLE:
            self._initialize_lukhas_subsystems(node_id)
        else:
            self.symbol_memory = None
            self.atomic_scaffold = None
            self.collapse_hash = None
            self.quarantine = None
            self.swarm_consensus = None
            self.distributed_memory = None

        # Initialize memory components
        if MEMORY_COMPONENTS_AVAILABLE:
            self._initialize_memory_subsystems()
        else:
            self.hippocampus = None
            self.neocortex = None
            self.consolidation_orchestrator = None
            self.episodic_interface = None
            self.semantic_interface = None
            self.colony_validator = None

        # Colony integration
        self.memory_colonies: dict[MemoryType, str] = {
            MemoryType.EPISODIC: "episodic_memory_colony",
            MemoryType.SEMANTIC: "semantic_memory_colony",
            MemoryType.EMOTIONAL: "emotional_memory_colony",
            MemoryType.WORKING: "working_memory_colony",
        }

        # Metrics
        self.encoding_count = 0
        self.consolidation_count = 0
        self.retrieval_count = 0
        self.forgetting_count = 0

        # Start background processes (if event loop is available)
        self._start_background_tasks()

        # Memory cleanup timer
        self.last_cleanup = datetime.now(timezone.utc)
        self.cleanup_interval = 300  # 5 minutes

        # Initialize comprehensive memory testing system through dependency injection
        try:
            test_module = get_test_module("memory_comprehensive")
            if test_module:
                self.comprehensive_memory_tester = {
                    "test_memory_lifecycle": lambda orch: test_module.test_memory_lifecycle(),
                    "test_error_conditions": lambda orch: test_module.test_error_conditions(),
                    "initialized": True,
                }
                logger.info("Comprehensive memory tester initialized via dependency injection")
            else:
                # Fallback to local test functions
                self.comprehensive_memory_tester = {
                    "test_memory_lifecycle": test_memory_lifecycle,
                    "test_error_conditions": test_error_conditions,
                    "initialized": True,
                }
                logger.info("Comprehensive memory tester initialized with local functions")
        except Exception as e:
            logger.warning(f"Failed to initialize comprehensive tester: {e}")
            self.comprehensive_memory_tester = {
                "test_memory_lifecycle": None,
                "test_error_conditions": None,
                "initialized": False,
            }

        logger.info(
            f"Unified Memory Orchestrator initialized: "
            f"hippocampal_capacity={hippocampal_capacity}, "
            f"neocortical_capacity={neocortical_capacity}, "
            f"colony_validation={enable_colony_validation}, "
            f"distributed={enable_distributed}"
        )

    def _initialize_lukhas_subsystems(self, node_id: Optional[str]):
        """Initialize LUKHAS subsystems"""
        try:
            # Symbol-aware memory
            self.symbol_memory = SymbolAwareTieredMemory(embedding_dim=768, enable_compression=True)

            # Atomic scaffold for stable storage
            self.atomic_scaffold = AtomicMemoryScaffold(dimensions=4, max_memories_per_coil=100)

            # Integrity verification
            self.collapse_hash = CollapseHash()

            # Memory protection
            self.quarantine = SymbolicQuarantineSanctum()

            # Colony consensus
            if self.enable_colony_validation:
                from ..systems.integration_adapters import MemorySafetyIntegration
                from ..systems.memory_safety_features import MemorySafetySystem

                safety = MemorySafetySystem()
                integration = MemorySafetyIntegration(safety, self.symbol_memory)
                self.swarm_consensus = SwarmConsensusManager(integration)

                # Register memory colonies
                self._register_memory_colonies()

            # Distributed memory
            if self.enable_distributed and node_id:
                self.distributed_memory = DistributedMemoryFold(
                    node_id=node_id,
                    port=8000 + hash(node_id) % 1000,
                    consciousness_level=0.8,
                )

        except Exception as e:
            logger.error(f"Failed to initialize subsystems: {e}")
            # Set to None so system can still function
            self.symbol_memory = None
            self.atomic_scaffold = None
            self.collapse_hash = None
            self.quarantine = None
            self.swarm_consensus = None
            self.distributed_memory = None

    def _register_memory_colonies(self):
        """Register specialized memory colonies for validation"""
        if not self.swarm_consensus:
            return

        from ..systems.colony_swarm_integration import ColonyRole

        # Register episodic memory colony
        self.swarm_consensus.register_colony(
            "episodic_memory_colony",
            ColonyRole.SPECIALIST,
            ["episodic", "temporal", "autobiographical"],
        )

        # Register semantic memory colony
        self.swarm_consensus.register_colony(
            "semantic_memory_colony",
            ColonyRole.SPECIALIST,
            ["semantic", "conceptual", "knowledge"],
        )

        # Register emotional memory colony
        self.swarm_consensus.register_colony(
            "emotional_memory_colony",
            ColonyRole.SPECIALIST,
            ["emotional", "affective", "valence"],
        )

        # Register working memory colony
        self.swarm_consensus.register_colony(
            "working_memory_colony",
            ColonyRole.VALIDATOR,
            ["working", "active", "attention"],
        )

        # Register arbiters for conflict resolution
        self.swarm_consensus.register_colony("memory_arbiter_alpha", ColonyRole.ARBITER)
        self.swarm_consensus.register_colony("memory_arbiter_beta", ColonyRole.ARBITER)

        logger.info("Memory colonies registered for consensus validation")

    def _initialize_memory_subsystems(self):
        """Initialize bio-inspired memory subsystems and colony validation"""
        try:
            # Initialize hippocampal buffer
            self.hippocampus = HippocampalBuffer(
                capacity=self.hippocampal_capacity,
                theta_frequency=6.0,
                enable_place_cells=True,
                enable_grid_cells=True,
            )

            # Initialize neocortical network
            self.neocortex = NeocorticalNetwork(
                columns_x=10,
                columns_y=10,
                neurons_per_layer=100,
                learning_rate_base=0.01,
            )

            # Initialize consolidation orchestrator
            self.consolidation_orchestrator = ConsolidationOrchestrator(
                hippocampus=self.hippocampus,
                neocortex=self.neocortex,
                enable_sleep_cycles=True,
                enable_creative_consolidation=True,
                enable_distributed=self.enable_distributed,
            )

            # Initialize memory interfaces
            self.episodic_interface = EpisodicMemoryInterface(
                colony_id="episodic_memory_colony",
                enable_distributed=self.enable_distributed,
            )

            self.semantic_interface = SemanticMemoryInterface(
                colony_id="semantic_memory_colony",
                enable_distributed=self.enable_distributed,
            )

            # Register interfaces with registry
            memory_registry.register_interface(MemoryType.EPISODIC, self.episodic_interface)
            memory_registry.register_interface(MemoryType.SEMANTIC, self.semantic_interface)

            # Initialize colony validator if enabled
            if self.enable_colony_validation:
                self.colony_validator = ColonyMemoryValidator(
                    default_validation_mode=ValidationMode.QUORUM, default_timeout=30.0
                )

                # Register colonies for validation
                self._register_colonies_with_validator()

            logger.info("Memory subsystems initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize memory subsystems: {e}")
            # Set to None so system can still function
            self.hippocampus = None
            self.neocortex = None
            self.consolidation_orchestrator = None
            self.episodic_interface = None
            self.semantic_interface = None
            self.colony_validator = None

    def _register_colonies_with_validator(self):
        """Register colonies with the colony validator"""
        if not self.colony_validator:
            return

        # Register memory colonies for validation
        for memory_type, colony_id in self.memory_colonies.items():
            self.colony_validator.register_colony(
                colony_id=colony_id,
                colony_info={
                    "memory_type": memory_type.value,
                    "specialization": memory_type.value + "_processing",
                    "capabilities": ["validate", "store", "retrieve"],
                },
                initial_trust_score=1.0,
            )

        # Register arbiter colonies
        self.colony_validator.register_colony(
            colony_id="memory_arbiter_alpha",
            colony_info={
                "role": "arbiter",
                "capabilities": ["arbitrate", "resolve_conflicts"],
            },
            initial_trust_score=1.0,
        )

        self.colony_validator.register_colony(
            colony_id="memory_arbiter_beta",
            colony_info={
                "role": "arbiter",
                "capabilities": ["arbitrate", "resolve_conflicts"],
            },
            initial_trust_score=1.0,
        )

        logger.info("Colonies registered with validator")

    def _start_background_tasks(self):
        """Start background processes for consolidation and maintenance"""
        try:
            # Only start tasks if we have an event loop
            loop = asyncio.get_running_loop()

            # Create and track tasks to prevent memory leaks
            self.background_tasks = [
                loop.create_task(self._consolidation_loop()),
                loop.create_task(self._oscillation_generator()),
                loop.create_task(self._memory_replay_loop()),
                loop.create_task(self._health_maintenance_loop()),
            ]

            logger.info(f"Background tasks started: {len(self.background_tasks)} tasks")
        except RuntimeError:
            # No event loop running, tasks will be started manually when needed
            self.background_tasks = []
            logger.info("No event loop available, background tasks deferred")

    async def encode_memory(
        self,
        content: Any,
        memory_type: MemoryType,
        tags: Optional[list[str]] = None,
        emotional_valence: float = 0.0,
        importance: float = 0.5,
        semantic_links: Optional[list[str]] = None,
    ) -> str:
        """
        Encode a new memory into the hippocampal buffer.

        This implements rapid encoding characteristic of hippocampal function,
        with pattern separation to prevent interference.

        Args:
            content: The memory content to encode
            memory_type: Type of memory (episodic, semantic, etc.)
            tags: Associated tags for indexing
            emotional_valence: Emotional charge (-1 to 1)
            importance: Memory importance (0 to 1)
            semantic_links: Links to related memories

        Returns:
            Memory ID for future retrieval
        """
        # Generate unique memory ID
        memory_id = self._generate_memory_id(content, memory_type)

        # Create memory trace
        memory_trace = MemoryTrace(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            encoding_strength=self._calculate_encoding_strength(importance, emotional_valence),
            emotional_valence=emotional_valence,
            semantic_links=set(semantic_links or []),
        )

        # Apply pattern separation (hippocampal function)
        memory_trace = await self._pattern_separation(memory_trace)

        # Colony validation if enabled
        if self.enable_colony_validation:
            validation_passed = await self._validate_memory_with_colonies(memory_trace, tags)
            if not validation_passed:
                logger.warning(f"Memory {memory_id} failed colony validation")
                return ""

        # Add to hippocampal buffer (rapid encoding)
        self.hippocampal_buffer.append(memory_trace)
        memory_trace.hippocampal_index = len(self.hippocampal_buffer) - 1

        # Update indices
        self._update_indices(memory_trace, tags)

        # Add to working memory if high importance (with size limit)
        if importance > 0.7:
            self._add_to_working_memory(memory_id, memory_trace)

        # Store in symbol-aware memory if available
        if self.symbol_memory:
            try:
                await self.symbol_memory.store(
                    data={"content": content, "trace": memory_trace.to_dict()},
                    tags=tags or [],
                    metadata={"memory_type": memory_type.value},
                )
            except Exception as e:
                logger.error(f"Failed to store in symbol memory: {e}")

        # Queue for consolidation based on importance
        if importance > 0.5 or abs(emotional_valence) > 0.7:
            self.consolidation_queue.append(memory_id)

        self.encoding_count += 1

        logger.debug(
            f"Memory encoded: memory_id={memory_id}, "
            f"memory_type={memory_type.value}, "
            f"encoding_strength={memory_trace.encoding_strength}"
        )

        return memory_id

    def _generate_memory_id(self, content: Any, memory_type: MemoryType) -> str:
        """Generate unique memory ID"""
        content_str = json.dumps(content, sort_keys=True) if isinstance(content, dict) else str(content)
        timestamp = datetime.now(timezone.utc).isoformat()
        hash_input = f"{memory_type.value}:{content_str}:{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _calculate_encoding_strength(self, importance: float, emotional_valence: float) -> float:
        """Calculate initial encoding strength based on importance and emotion"""
        # Emotional memories are encoded more strongly
        emotion_boost = abs(emotional_valence) * 0.5
        base_strength = importance

        # Apply current oscillation phase (theta enhances encoding)
        theta_boost = np.sin(self.oscillations.theta_phase) * 0.2

        return min(1.0, base_strength + emotion_boost + theta_boost)

    async def _pattern_separation(self, memory_trace: MemoryTrace) -> MemoryTrace:
        """
        Apply pattern separation to reduce interference between similar memories.
        This is a key hippocampal function.
        """
        # Check for similar memories in hippocampal buffer
        similar_memories = self._find_similar_memories(memory_trace)

        if similar_memories:
            # Orthogonalize the representation
            # In a real implementation, this would modify the neural representation
            # Here we simulate by adjusting semantic links
            existing_links = set()
            for similar in similar_memories:
                existing_links.update(similar.semantic_links)

            # Add unique differentiating links
            unique_id = f"unique_{memory_trace.memory_id[:8]}"
            memory_trace.semantic_links.add(unique_id)

            # Slightly reduce encoding strength if very similar
            if len(similar_memories) > 3:
                memory_trace.encoding_strength *= 0.9

        return memory_trace

    def _find_similar_memories(self, memory_trace: MemoryTrace, threshold: float = 0.7) -> list[MemoryTrace]:
        """Find memories similar to the given trace"""
        similar = []

        # Check recent memories in hippocampal buffer
        for existing_trace in list(self.hippocampal_buffer)[-100:]:  # Check last 100
            if existing_trace.memory_type == memory_trace.memory_type:
                # Simple similarity based on semantic links overlap
                if existing_trace.semantic_links:
                    overlap = len(memory_trace.semantic_links & existing_trace.semantic_links)
                    similarity = overlap / max(
                        len(memory_trace.semantic_links),
                        len(existing_trace.semantic_links),
                        1,
                    )
                    if similarity > threshold:
                        similar.append(existing_trace)

        return similar

    async def _validate_with_colonies(self, memory_trace: MemoryTrace, tags: list[str]) -> bool:
        """
        Validate memory with specialized colonies
        """
        if not self.swarm_consensus:
            return True

        # Prepare memory data for validation
        memory_data = {
            "content": memory_trace.content,
            "type": memory_trace.memory_type.value,
            "timestamp": memory_trace.timestamp,
            "emotion": memory_trace.emotional_valence,
            "tags": tags or [],
        }

        # Get appropriate colony for this memory type
        proposing_colony = self.memory_colonies.get(memory_trace.memory_type, "general_memory_colony")

        # Request distributed validation
        validation_id = await self.swarm_consensus.distributed_memory_storage(
            memory_data=memory_data,
            tags=tags or [memory_trace.memory_type.value],
            proposing_colony=proposing_colony,
        )

        return validation_id is not None

    async def _validate_memory_with_colonies(self, memory_trace: MemoryTrace, tags: list[str]) -> bool:
        """
        Validate memory using the new colony validator system with Byzantine fault tolerance
        """
        # Use legacy validation if new system not available
        if not self.colony_validator and self.swarm_consensus:
            return await self._validate_with_colonies(memory_trace, tags)

        # Skip validation if no validator available
        if not self.colony_validator:
            return True

        # Create memory operation for validation
        operation = MemoryOperation(
            operation_type="create",
            content=memory_trace.content,
            metadata=self._create_memory_metadata(memory_trace, tags),
            target_colonies=self._select_validation_colonies(memory_trace.memory_type),
            require_consensus=True,
            consensus_threshold=0.67,  # 2/3 majority
        )

        # Perform validation with Byzantine fault tolerance
        try:
            outcome = await self.colony_validator.validate_memory_operation(
                operation=operation,
                validation_mode=ValidationMode.BYZANTINE,
                timeout_seconds=30.0,
            )

            # Record validation results in memory trace
            for colony_id, response in outcome.colony_responses.items():
                if response.success:
                    memory_trace.colony_validations[colony_id] = response.colony_trust_score

            validation_success = outcome.consensus_achieved and outcome.result.name == "SUCCESS"

            logger.debug(
                f"Colony validation completed: memory_id={memory_trace.memory_id}, "
                f"success={validation_success}, "
                f"consensus_confidence={outcome.consensus_confidence}, "
                f"participating_colonies={len(outcome.colony_responses)}"
            )

            return validation_success

        except Exception as e:
            logger.error(f"Colony validation failed: {e}")
            return False

    def _create_memory_metadata(self, memory_trace: MemoryTrace, tags: list[str]):
        """Create metadata for memory validation"""
        if not MEMORY_COMPONENTS_AVAILABLE:
            return None

        from .interfaces.memory_interface import MemoryMetadata

        return MemoryMetadata(
            memory_id=memory_trace.memory_id,
            memory_type=memory_trace.memory_type,
            importance=memory_trace.encoding_strength,
            tags=set(tags or []),
            source="unified_orchestrator",
            context={
                "emotional_valence": memory_trace.emotional_valence,
                "timestamp": memory_trace.timestamp.isoformat(),
                "semantic_links": list(memory_trace.semantic_links),
            },
        )

    def _select_validation_colonies(self, memory_type: MemoryType) -> list[str]:
        """Select appropriate colonies for validation based on memory type"""
        # Primary colony for this memory type
        colonies = []

        if memory_type in self.memory_colonies:
            colonies.append(self.memory_colonies[memory_type])

        # Add arbiters for important decisions
        colonies.extend(["memory_arbiter_alpha", "memory_arbiter_beta"])

        # Add cross-validation from other specialized colonies
        if memory_type == MemoryType.EPISODIC:
            # Episodic memories often have emotional components
            colonies.append(self.memory_colonies.get(MemoryType.EMOTIONAL, "emotional_memory_colony"))
        elif memory_type == MemoryType.SEMANTIC:
            # Semantic memories might relate to procedural knowledge
            colonies.append(self.memory_colonies.get(MemoryType.PROCEDURAL, "procedural_memory_colony"))

        return colonies

    def _update_indices(self, memory_trace: MemoryTrace, tags: list[str]):
        """Update various indices for efficient retrieval"""
        memory_id = memory_trace.memory_id

        # Semantic index
        for link in memory_trace.semantic_links:
            self.semantic_index[link].add(memory_id)

        # Tag index
        if tags:
            for tag in tags:
                self.semantic_index[tag].add(memory_id)

        # Temporal index (bucket by hour)
        time_bucket = memory_trace.timestamp.replace(minute=0, second=0, microsecond=0)
        self.temporal_index[time_bucket].add(memory_id)

        # Emotional index (bucket by valence)
        emotion_bucket = round(memory_trace.emotional_valence, 1)
        self.emotional_index[emotion_bucket].add(memory_id)

    async def retrieve_memory(
        self,
        query: Union[str, dict[str, Any]],
        memory_types: Optional[list[MemoryType]] = None,
        use_pattern_completion: bool = True,
        max_results: int = 10,
    ) -> list[tuple[MemoryTrace, float]]:
        """
        Retrieve memories using hippocampal pattern completion.

        Args:
            query: Search query (string or structured)
            memory_types: Filter by memory types
            use_pattern_completion: Enable hippocampal pattern completion
            max_results: Maximum results to return

        Returns:
            List of (memory_trace, relevance_score) tuples
        """
        results = []

        # Search in working memory first (fastest)
        working_results = self._search_working_memory(query, memory_types)
        results.extend(working_results)

        # Search hippocampal buffer
        hippocampal_results = await self._search_hippocampal(query, memory_types, use_pattern_completion)
        results.extend(hippocampal_results)

        # Search neocortical network for consolidated memories
        neocortical_results = await self._search_neocortical(query, memory_types)
        results.extend(neocortical_results)

        # Remove duplicates and sort by relevance
        seen_ids = set()
        unique_results = []
        for trace, score in sorted(results, key=lambda x: x[1], reverse=True):
            if trace.memory_id not in seen_ids:
                seen_ids.add(trace.memory_id)
                unique_results.append((trace, score))

                # Update access metadata
                trace.access_count += 1
                trace.last_accessed = datetime.now(timezone.utc)

                if len(unique_results) >= max_results:
                    break

        self.retrieval_count += 1

        return unique_results

    def _search_working_memory(
        self,
        query: Union[str, dict[str, Any]],
        memory_types: Optional[list[MemoryType]] = None,
    ) -> list[tuple[MemoryTrace, float]]:
        """Fast search in working memory"""
        results = []
        query_str = str(query).lower()

        for trace in self.working_memory.values():
            if memory_types and trace.memory_type not in memory_types:
                continue

            # Simple relevance scoring
            content_str = str(trace.content).lower()
            if query_str in content_str:
                score = 1.0  # Working memory has high relevance
                results.append((trace, score))

        return results

    async def _search_hippocampal(
        self,
        query: Union[str, dict[str, Any]],
        memory_types: Optional[list[MemoryType]] = None,
        use_pattern_completion: bool = True,
    ) -> list[tuple[MemoryTrace, float]]:
        """Search in hippocampal buffer with pattern completion"""
        results = []

        # Extract query features
        if isinstance(query, dict):
            query_tags = query.get("tags", [])
            query_emotion = query.get("emotion", 0.0)
            query_text = query.get("text", "")
        else:
            query_tags = []
            query_emotion = 0.0
            query_text = str(query)

        for trace in self.hippocampal_buffer:
            if memory_types and trace.memory_type not in memory_types:
                continue

            # Calculate relevance score
            score = 0.0

            # Text similarity
            if query_text:
                content_str = str(trace.content).lower()
                if query_text.lower() in content_str:
                    score += 0.5

            # Semantic link similarity
            if query_tags:
                tag_overlap = len(set(query_tags) & trace.semantic_links)
                score += tag_overlap * 0.2

            # Emotional similarity
            emotion_diff = abs(trace.emotional_valence - query_emotion)
            score += (1.0 - emotion_diff) * 0.3

            # Pattern completion boost
            if use_pattern_completion and score > 0.3:
                # Simulate pattern completion by boosting partial matches
                score = await self._apply_pattern_completion(trace, query, score)

            if score > 0.1:
                results.append((trace, score))

        return results

    async def _apply_pattern_completion(self, trace: MemoryTrace, query: Any, base_score: float) -> float:
        """
        Apply hippocampal pattern completion to boost partial matches.
        This simulates the hippocampus's ability to recall full memories from partial cues.
        """
        # Boost recent memories (recency effect)
        time_diff = (datetime.now(timezone.utc) - trace.timestamp).total_seconds()
        recency_boost = np.exp(-time_diff / (24 * 3600))  # Decay over 24 hours

        # Boost frequently accessed memories
        access_boost = min(trace.access_count * 0.05, 0.3)

        # Boost based on encoding strength
        strength_boost = trace.encoding_strength * 0.2

        # Apply gamma oscillation for binding
        gamma_boost = abs(np.sin(self.oscillations.gamma_phase)) * 0.1

        return min(
            1.0,
            base_score + recency_boost * 0.2 + access_boost + strength_boost + gamma_boost,
        )

    async def _search_neocortical(
        self,
        query: Union[str, dict[str, Any]],
        memory_types: Optional[list[MemoryType]] = None,
    ) -> list[tuple[MemoryTrace, float]]:
        """Search in consolidated neocortical memories"""
        results = []

        # Use semantic index for efficient search
        relevant_ids = set()

        if isinstance(query, str):
            # Find memories linked to query terms
            for term in query.lower().split():
                if term in self.semantic_index:
                    relevant_ids.update(self.semantic_index[term])

        # Search in identified memories
        for memory_id in relevant_ids:
            if memory_id in self.neocortical_network:
                trace = self.neocortical_network[memory_id]

                if memory_types and trace.memory_type not in memory_types:
                    continue

                # Neocortical memories have stable representations
                score = 0.7  # Base score for consolidated memories

                # Boost based on semantic richness
                score += len(trace.semantic_links) * 0.01

                results.append((trace, score))

        return results

    async def consolidate_memory(self, memory_id: str, force: bool = False) -> bool:
        """
        Consolidate a memory from hippocampus to neocortex.
        This implements the gradual transfer process during sleep cycles.

        Args:
            memory_id: ID of memory to consolidate
            force: Force consolidation regardless of sleep stage

        Returns:
            True if successfully consolidated
        """
        # Check sleep stage (consolidation happens mainly during NREM3)
        if not force and self.sleep_stage not in [SleepStage.NREM3, SleepStage.NREM2]:
            return False

        # Find memory in hippocampal buffer
        memory_trace = None
        for trace in self.hippocampal_buffer:
            if trace.memory_id == memory_id:
                memory_trace = trace
                break

        if not memory_trace:
            return False

        # Check if already consolidating
        if memory_trace.consolidation_state == ConsolidationState.CONSOLIDATING:
            return False

        # Begin consolidation
        memory_trace.consolidation_state = ConsolidationState.CONSOLIDATING

        try:
            # Extract semantic features (neocortical representation)
            semantic_features = await self._extract_semantic_features(memory_trace)

            # Create distributed representation
            neocortical_representation = await self._create_neocortical_representation(memory_trace, semantic_features)

            # Store in neocortex with gradually increasing strength
            consolidation_strength = min(
                1.0,
                memory_trace.encoding_strength * self.consolidation_rate * memory_trace.replay_count,
            )

            if consolidation_strength > 0.5:  # Threshold for stable storage
                # Add to neocortical network
                self.neocortical_network[memory_id] = memory_trace
                memory_trace.consolidation_state = ConsolidationState.CONSOLIDATED
                memory_trace.neocortical_indices = neocortical_representation

                # Store in atomic scaffold if available
                if self.atomic_scaffold:
                    try:
                        coil_index = await self.atomic_scaffold.fold_memory(
                            memory_trace.to_dict(), dimension=hash(memory_id) % 4
                        )
                        memory_trace.neocortical_indices.append(coil_index)
                    except Exception as e:
                        logger.error(f"Failed to store in atomic scaffold: {e}")

                # Update semantic index with enriched links (with size limit)
                for feature in semantic_features:
                    if len(self.semantic_index) < self.max_index_entries:
                        self.semantic_index[feature].add(memory_id)
                        memory_trace.semantic_links.add(feature)

                self.consolidation_count += 1

                logger.info(
                    f"Memory consolidated to neocortex: memory_id={memory_id}, "
                    f"strength={consolidation_strength}, "
                    f"semantic_features={len(semantic_features)}"
                )

                return True
            else:
                # Not ready for consolidation, keep in hippocampus
                memory_trace.consolidation_state = ConsolidationState.ENCODING
                memory_trace.replay_count += 1
                return False

        except Exception as e:
            logger.error(f"Consolidation failed for {memory_id}: {e}")
            memory_trace.consolidation_state = ConsolidationState.ENCODING
            return False

    async def _extract_semantic_features(self, memory_trace: MemoryTrace) -> list[str]:
        """
        Extract semantic features for neocortical representation.
        This simulates the abstraction process during consolidation.
        """
        features = list(memory_trace.semantic_links)

        # Extract features from content
        if isinstance(memory_trace.content, dict):
            # Extract keys as features
            features.extend(memory_trace.content.keys())
        elif isinstance(memory_trace.content, str):
            # Extract significant words (simplified)
            words = memory_trace.content.lower().split()
            significant_words = [w for w in words if len(w) > 4]  # Simple heuristic
            features.extend(significant_words[:5])  # Limit features

        # Add memory type as feature
        features.append(f"type:{memory_trace.memory_type.value}")

        # Add emotional category if significant
        if abs(memory_trace.emotional_valence) > 0.5:
            emotion_category = "positive" if memory_trace.emotional_valence > 0 else "negative"
            features.append(f"emotion:{emotion_category}")

        # Colony-based feature extraction if available
        if self.swarm_consensus:
            # This would involve colonies analyzing and adding features
            # For now, we simulate this
            features.append(f"colony_validated:{memory_trace.memory_type.value}")

        return list(set(features))  # Remove duplicates

    async def _create_neocortical_representation(
        self, memory_trace: MemoryTrace, semantic_features: list[str]
    ) -> list[int]:
        """
        Create distributed neocortical representation.
        This simulates how memories are stored across cortical regions.
        """
        # Generate distributed indices based on features
        indices = []

        for feature in semantic_features:
            # Hash feature to get neocortical index
            feature_hash = hash(feature)
            # Distribute across virtual "cortical columns"
            column_index = abs(feature_hash) % 1000
            indices.append(column_index)

        # Add some redundancy (multiple representations)
        redundancy_factor = 3
        redundant_indices = []
        for idx in indices:
            for i in range(redundancy_factor):
                redundant_indices.append((idx + i * 1000) % self.neocortical_capacity)

        return redundant_indices

    async def replay_memories(
        self,
        replay_count: int = 10,
        prioritize_emotional: bool = True,
        prioritize_recent: bool = True,
    ):
        """
        Replay memories for consolidation (hippocampal replay).
        This simulates sharp-wave ripples during sleep.
        """
        if self.sleep_stage == SleepStage.AWAKE:
            return  # Replay mainly occurs during sleep

        # Select memories for replay
        replay_candidates = []

        for trace in self.hippocampal_buffer:
            if trace.consolidation_state == ConsolidationState.ENCODING:
                # Calculate replay priority
                priority = trace.encoding_strength

                if prioritize_emotional:
                    priority += abs(trace.emotional_valence) * 0.5

                if prioritize_recent:
                    time_diff = (datetime.now(timezone.utc) - trace.timestamp).total_seconds()
                    recency_factor = np.exp(-time_diff / (12 * 3600))  # 12-hour decay
                    priority += recency_factor * 0.3

                replay_candidates.append((trace, priority))

        # Sort by priority and select top memories
        replay_candidates.sort(key=lambda x: x[1], reverse=True)
        selected_memories = replay_candidates[:replay_count]

        # Replay selected memories
        for trace, priority in selected_memories:
            # Simulate ripple event
            self.oscillations.ripple_amplitude = np.random.gamma(2, 2)  # Gamma distribution

            # Strengthen memory through replay
            trace.encoding_strength = min(1.0, trace.encoding_strength + 0.1)
            trace.replay_count += 1

            # Add to replay buffer for pattern analysis (with strict size limit)
            self.replay_buffer.append(trace)
            if len(self.replay_buffer) > self.max_replay_buffer_size:
                # Remove oldest 20% when at capacity
                num_to_remove = max(1, len(self.replay_buffer) // 5)
                self.replay_buffer = self.replay_buffer[num_to_remove:]

            # Attempt consolidation if replayed enough
            if trace.replay_count >= 3:
                await self.consolidate_memory(trace.memory_id)

            # Brief pause between replays
            await asyncio.sleep(0.1)

        logger.debug(f"Replayed {len(selected_memories)} memories during {self.sleep_stage.value}")

    async def enter_sleep_stage(self, stage: SleepStage):
        """
        Transition to a new sleep stage.
        Different stages have different consolidation patterns.
        """
        self.sleep_stage = stage

        logger.info(f"Entering sleep stage: {stage.value}")

        # Adjust oscillation patterns based on stage
        if stage == SleepStage.NREM2:
            # Sleep spindles (12-14 Hz)
            self.oscillations.spindle_density = 0.8
            self.oscillations.theta_phase = 0.2
        elif stage == SleepStage.NREM3:
            # Slow-wave sleep
            self.oscillations.slow_wave_power = 0.9
            self.oscillations.spindle_density = 0.3
            # Best time for consolidation
            await self._batch_consolidation()
        elif stage == SleepStage.REM:
            # REM sleep - creative consolidation
            self.oscillations.theta_phase = 0.9
            self.oscillations.gamma_phase = 0.7
            await self._creative_consolidation()
        elif stage == SleepStage.AWAKE:
            # Reset oscillations
            self.oscillations = OscillationPattern()

    async def _batch_consolidation(self):
        """
        Perform batch consolidation during slow-wave sleep
        """
        # Process consolidation queue
        consolidated_count = 0
        max_consolidations = 20

        while self.consolidation_queue and consolidated_count < max_consolidations:
            memory_id = self.consolidation_queue.popleft()
            success = await self.consolidate_memory(memory_id, force=True)
            if success:
                consolidated_count += 1
            else:
                # Re-queue if failed
                self.consolidation_queue.append(memory_id)

            await asyncio.sleep(0.05)  # Prevent blocking

        logger.info(f"Batch consolidated {consolidated_count} memories during SWS")

    async def _creative_consolidation(self):
        """
        Creative memory consolidation during REM sleep.
        This creates new associations between memories.
        """
        if len(self.replay_buffer) < 2:
            return

        # Select random pairs of memories for creative linking
        num_links = min(10, len(self.replay_buffer) // 2)

        for _ in range(num_links):
            # Select two random memories
            idx1, idx2 = np.random.choice(len(self.replay_buffer), 2, replace=False)
            memory1 = self.replay_buffer[idx1]
            memory2 = self.replay_buffer[idx2]

            # Create bidirectional semantic link
            link_id = f"rem_link_{memory1.memory_id[:8]}_{memory2.memory_id[:8]}"
            memory1.semantic_links.add(link_id)
            memory2.semantic_links.add(link_id)

            # Update semantic index
            self.semantic_index[link_id].add(memory1.memory_id)
            self.semantic_index[link_id].add(memory2.memory_id)

            # If memories have opposite emotional valence, create emotional regulation
            # link
            if memory1.emotional_valence * memory2.emotional_valence < -0.5:
                regulation_link = f"emotion_regulation_{link_id}"
                memory1.semantic_links.add(regulation_link)
                memory2.semantic_links.add(regulation_link)

        logger.debug(f"Created {num_links} creative associations during REM sleep")

    async def forget_memory(self, memory_id: str, gradual: bool = True) -> bool:
        """
        Implement forgetting (memory decay).
        Can be gradual (natural decay) or immediate (active forgetting).
        """
        # Check in working memory
        if memory_id in self.working_memory:
            del self.working_memory[memory_id]

        # Check in neocortex
        if memory_id in self.neocortical_network:
            memory_trace = self.neocortical_network[memory_id]

            if gradual:
                # Gradual forgetting by reducing strength
                memory_trace.encoding_strength *= 0.5
                if memory_trace.encoding_strength < 0.1:
                    del self.neocortical_network[memory_id]
                    memory_trace.consolidation_state = ConsolidationState.FORGETTING
                    self.forgetting_count += 1
                    return True
                return False
            else:
                # Immediate forgetting
                del self.neocortical_network[memory_id]
                memory_trace.consolidation_state = ConsolidationState.FORGETTING
                self.forgetting_count += 1
                return True

        # Check in hippocampus (remove from buffer)
        for _i, trace in enumerate(self.hippocampal_buffer):
            if trace.memory_id == memory_id:
                # Can't directly remove from deque by index
                # Mark for forgetting instead
                trace.consolidation_state = ConsolidationState.FORGETTING
                trace.encoding_strength = 0.0
                self.forgetting_count += 1
                return True

        return False

    async def _consolidation_loop(self):
        """
        Background consolidation process
        """
        while True:
            try:
                # Consolidation rate varies by sleep stage
                if self.sleep_stage == SleepStage.NREM3:
                    wait_time = 5  # Fast consolidation during SWS
                elif self.sleep_stage == SleepStage.NREM2:
                    wait_time = 10
                elif self.sleep_stage == SleepStage.REM:
                    wait_time = 15
                else:  # Awake
                    wait_time = 60  # Slow consolidation when awake

                await asyncio.sleep(wait_time)

                # Process consolidation queue
                if self.consolidation_queue:
                    memory_id = self.consolidation_queue[0]  # Peek
                    success = await self.consolidate_memory(memory_id)
                    if success:
                        self.consolidation_queue.popleft()

                # Replay memories periodically
                if self.sleep_stage != SleepStage.AWAKE:
                    await self.replay_memories()

            except Exception as e:
                logger.error(f"Consolidation loop error: {e}")
                await asyncio.sleep(60)

    async def _oscillation_generator(self):
        """
        Generate neural oscillations for memory processing
        """
        while True:
            try:
                # Update oscillation phases
                dt = 0.01  # 10ms time step

                # Theta oscillation (4-8 Hz, use 6 Hz)
                self.oscillations.theta_phase += 2 * np.pi * 6 * dt
                self.oscillations.theta_phase %= 2 * np.pi

                # Gamma oscillation (30-100 Hz, use 40 Hz)
                self.oscillations.gamma_phase += 2 * np.pi * 40 * dt
                self.oscillations.gamma_phase %= 2 * np.pi

                # Ripple events (stochastic)
                if self.sleep_stage in [SleepStage.NREM2, SleepStage.NREM3]:
                    if np.random.random() < 0.001:  # Rare events
                        self.oscillations.ripple_amplitude = np.random.gamma(2, 2)
                else:
                    self.oscillations.ripple_amplitude *= 0.9  # Decay

                await asyncio.sleep(dt)

            except Exception as e:
                logger.error(f"Oscillation generator error: {e}")
                await asyncio.sleep(1)

    async def _memory_replay_loop(self):
        """
        Periodic memory replay for consolidation
        """
        while True:
            try:
                # Wait for appropriate sleep stage
                if self.sleep_stage in [
                    SleepStage.NREM2,
                    SleepStage.NREM3,
                    SleepStage.REM,
                ]:
                    await self.replay_memories(
                        replay_count=5,
                        prioritize_emotional=(self.sleep_stage == SleepStage.REM),
                        prioritize_recent=(self.sleep_stage == SleepStage.NREM3),
                    )

                # Replay interval depends on sleep stage
                if self.sleep_stage == SleepStage.NREM3:
                    await asyncio.sleep(30)  # Frequent replay during SWS
                else:
                    await asyncio.sleep(120)  # Less frequent otherwise

            except Exception as e:
                logger.error(f"Memory replay loop error: {e}")
                await asyncio.sleep(300)

    async def _health_maintenance_loop(self):
        """
        Maintain memory system health
        """
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                # Clean up forgotten memories
                forgotten_ids = []
                for trace in list(self.hippocampal_buffer):
                    if trace.consolidation_state == ConsolidationState.FORGETTING:
                        forgotten_ids.append(trace.memory_id)

                # Remove from indices
                for memory_id in forgotten_ids:
                    for index_dict in [
                        self.semantic_index,
                        self.temporal_index,
                        self.emotional_index,
                    ]:
                        for key in list(index_dict.keys()):
                            if isinstance(index_dict[key], set):
                                index_dict[key].discard(memory_id)

                # Manage working memory size aggressively
                if len(self.working_memory) > self.max_working_memory_size:
                    # Remove least recently accessed (keep only 60% of limit)
                    target_size = int(self.max_working_memory_size * 0.6)
                    sorted_working = sorted(self.working_memory.items(), key=lambda x: x[1].last_accessed)
                    for memory_id, _ in sorted_working[:-target_size]:
                        del self.working_memory[memory_id]

                # Periodic memory cleanup
                current_time = datetime.now(timezone.utc)
                if (current_time - self.last_cleanup).total_seconds() > self.cleanup_interval:
                    await self._aggressive_memory_cleanup()
                    self.last_cleanup = current_time

                # Colony health check
                if self.swarm_consensus:
                    swarm_status = self.swarm_consensus.get_swarm_status()
                    if swarm_status["average_accuracy"] < 0.5:
                        logger.warning("Colony consensus accuracy below threshold")

                # Log health metrics
                logger.info(
                    f"Memory system health check: "
                    f"hippocampal_size={len(self.hippocampal_buffer)}, "
                    f"neocortical_size={len(self.neocortical_network)}, "
                    f"working_memory_size={len(self.working_memory)}, "
                    f"encoding_count={self.encoding_count}, "
                    f"consolidation_count={self.consolidation_count}, "
                    f"retrieval_count={self.retrieval_count}, "
                    f"forgetting_count={self.forgetting_count}"
                )

            except Exception as e:
                logger.error(f"Health maintenance error: {e}")
                await asyncio.sleep(600)

    def _add_to_working_memory(self, memory_id: str, memory_trace: MemoryTrace):
        """Add memory to working memory with size management"""
        if len(self.working_memory) >= self.max_working_memory_size:
            # Remove least recently accessed memory
            oldest_id = min(
                self.working_memory.keys(),
                key=lambda x: self.working_memory[x].last_accessed,
            )
            del self.working_memory[oldest_id]

        self.working_memory[memory_id] = memory_trace

    def _cleanup_old_neocortical_memories(self):
        """Clean up old neocortical memories when at capacity"""
        if len(self.neocortical_network) < self.max_neocortical_size:
            return

        # Remove oldest 10% of memories
        target_size = int(self.max_neocortical_size * 0.9)
        sorted_memories = sorted(self.neocortical_network.items(), key=lambda x: x[1].last_accessed)

        # Remove oldest memories
        for memory_id, _ in sorted_memories[:-target_size]:
            del self.neocortical_network[memory_id]

        logger.info(f"Cleaned up neocortical memories: {len(self.neocortical_network)} remaining")

    async def _aggressive_memory_cleanup(self):
        """Perform aggressive memory cleanup to prevent leaks"""
        logger.info("Performing aggressive memory cleanup...")

        # Clean up indices
        for index_dict in [
            self.semantic_index,
            self.temporal_index,
            self.emotional_index,
        ]:
            if len(index_dict) > self.max_index_entries:
                # Remove least frequently used entries
                sorted_keys = sorted(index_dict.keys(), key=lambda x: len(index_dict[x]))
                for key in sorted_keys[: len(index_dict) - self.max_index_entries]:
                    del index_dict[key]

        # Limit replay buffer size aggressively
        if len(self.replay_buffer) > self.max_replay_buffer_size // 2:
            self.replay_buffer = self.replay_buffer[-(self.max_replay_buffer_size // 2) :]

        # Cancel and recreate background tasks if they're consuming too much memory
        if len(self.background_tasks) > 10:  # Should only be 4
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
            self.background_tasks = []
            self._start_background_tasks()

        logger.info("Aggressive memory cleanup completed")

    async def shutdown(self):
        """Properly shutdown the orchestrator and cleanup resources"""
        logger.info("Shutting down UnifiedMemoryOrchestrator...")

        # Cancel all background tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        # Clear all memory structures
        self.hippocampal_buffer.clear()
        self.neocortical_network.clear()
        self.working_memory.clear()
        self.semantic_index.clear()
        self.temporal_index.clear()
        self.emotional_index.clear()
        self.consolidation_queue.clear()
        self.replay_buffer.clear()

        logger.info("UnifiedMemoryOrchestrator shutdown complete")

    def get_memory_statistics(self) -> dict[str, Any]:
        """
        Get comprehensive memory system statistics
        """
        # Memory distribution by type
        type_distribution = defaultdict(int)
        for trace in self.hippocampal_buffer:
            type_distribution[trace.memory_type.value] += 1
        for trace in self.neocortical_network.values():
            type_distribution[trace.memory_type.value] += 1

        # Consolidation state distribution
        state_distribution = defaultdict(int)
        for trace in self.hippocampal_buffer:
            state_distribution[trace.consolidation_state.value] += 1

        # Average metrics
        all_traces = list(self.hippocampal_buffer) + list(self.neocortical_network.values())
        avg_encoding_strength = np.mean([t.encoding_strength for t in all_traces]) if all_traces else 0
        avg_replay_count = np.mean([t.replay_count for t in all_traces]) if all_traces else 0
        avg_access_count = np.mean([t.access_count for t in all_traces]) if all_traces else 0

        return {
            "total_memories": len(all_traces),
            "hippocampal_memories": len(self.hippocampal_buffer),
            "neocortical_memories": len(self.neocortical_network),
            "working_memories": len(self.working_memory),
            "type_distribution": dict(type_distribution),
            "state_distribution": dict(state_distribution),
            "average_encoding_strength": avg_encoding_strength,
            "average_replay_count": avg_replay_count,
            "average_access_count": avg_access_count,
            "encoding_count": self.encoding_count,
            "consolidation_count": self.consolidation_count,
            "retrieval_count": self.retrieval_count,
            "forgetting_count": self.forgetting_count,
            "current_sleep_stage": self.sleep_stage.value,
            "oscillations": {
                "theta_phase": self.oscillations.theta_phase,
                "gamma_phase": self.oscillations.gamma_phase,
                "ripple_amplitude": self.oscillations.ripple_amplitude,
                "spindle_density": self.oscillations.spindle_density,
                "slow_wave_power": self.oscillations.slow_wave_power,
            },
            "colony_validation_enabled": self.enable_colony_validation,
            "distributed_enabled": self.enable_distributed,
        }

    def run_memory_lifecycle_test(self) -> dict[str, Any]:
        """
        Run comprehensive memory lifecycle testing
        """
        try:
            if not self.comprehensive_memory_tester.get("initialized", False):
                return {
                    "status": "error",
                    "message": "Comprehensive memory tester not initialized",
                }

            test_func = self.comprehensive_memory_tester.get("test_memory_lifecycle")
            if test_func:
                # Run lifecycle test with current orchestrator
                result = test_func(self)
                return {
                    "status": "success",
                    "test_type": "memory_lifecycle",
                    "result": result,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            else:
                return {
                    "status": "error",
                    "message": "Memory lifecycle test function not available",
                }
        except Exception as e:
            logger.error(f"Memory lifecycle test error: {e}")
            return {"status": "error", "message": str(e)}

    def run_error_condition_test(self) -> dict[str, Any]:
        """
        Run comprehensive error condition testing
        """
        try:
            if not self.comprehensive_memory_tester.get("initialized", False):
                return {
                    "status": "error",
                    "message": "Comprehensive memory tester not initialized",
                }

            test_func = self.comprehensive_memory_tester.get("test_error_conditions")
            if test_func:
                # Run error condition test with current orchestrator
                result = test_func(self)
                return {
                    "status": "success",
                    "test_type": "error_conditions",
                    "result": result,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            else:
                return {
                    "status": "error",
                    "message": "Error condition test function not available",
                }
        except Exception as e:
            logger.error(f"Error condition test error: {e}")
            return {"status": "error", "message": str(e)}

    def get_comprehensive_memory_status(self) -> dict[str, Any]:
        """
        Get comprehensive memory system status and testing capabilities
        """
        return {
            "comprehensive_tester": {
                "initialized": self.comprehensive_memory_tester.get("initialized", False),
                "available_tests": ["test_memory_lifecycle", "test_error_conditions"],
                "test_functions_loaded": bool(
                    self.comprehensive_memory_tester.get("test_memory_lifecycle")
                    and self.comprehensive_memory_tester.get("test_error_conditions")
                ),
            },
            "memory_statistics": self.get_memory_statistics(),
            "system_health": {
                "running": True,
                "last_update": asyncio.get_event_loop().time(),
            },
        }


# Example usage and testing
async def demonstrate_unified_memory():
    """Demonstrate the unified memory orchestrator"""

    print("🧠 Unified Memory Orchestrator Demonstration")
    print("=" * 60)

    # Create orchestrator
    orchestrator = UnifiedMemoryOrchestrator(
        hippocampal_capacity=1000,
        neocortical_capacity=10000,
        enable_colony_validation=True,
        enable_distributed=False,  # Disable for demo
    )

    # Wait for initialization
    await asyncio.sleep(1)

    print("\n1. Encoding episodic memories...")

    # Encode some episodic memories
    memory1_id = await orchestrator.encode_memory(
        content={
            "event": "First day at LUKHAS AI",
            "location": "Bay Area",
            "people": ["team"],
        },
        memory_type=MemoryType.EPISODIC,
        tags=["work", "milestone", "personal"],
        emotional_valence=0.8,
        importance=0.9,
    )
    print(f"✅ Encoded memory: {memory1_id}")

    memory2_id = await orchestrator.encode_memory(
        content="Learned about hippocampal-neocortical memory consolidation",
        memory_type=MemoryType.SEMANTIC,
        tags=["neuroscience", "learning", "memory"],
        emotional_valence=0.3,
        importance=0.7,
        semantic_links=["hippocampus", "consolidation", "sleep"],
    )
    print(f"✅ Encoded memory: {memory2_id}")

    memory3_id = await orchestrator.encode_memory(
        content={"skill": "async programming", "context": "memory system"},
        memory_type=MemoryType.PROCEDURAL,
        tags=["programming", "python", "async"],
        emotional_valence=0.0,
        importance=0.6,
    )
    print(f"✅ Encoded memory: {memory3_id}")

    # Emotional memory
    memory4_id = await orchestrator.encode_memory(
        content="Breakthrough moment: system finally working!",
        memory_type=MemoryType.EMOTIONAL,
        tags=["achievement", "joy", "breakthrough"],
        emotional_valence=0.9,
        importance=0.8,
    )
    print(f"✅ Encoded memory: {memory4_id}")

    print("\n2. Testing memory retrieval...")

    # Test retrieval
    results = await orchestrator.retrieve_memory(query="LUKHAS", use_pattern_completion=True)

    print(f"Found {len(results)} memories for 'LUKHAS':")
    for trace, score in results[:3]:
        print(f"  - {trace.memory_type.value}: {str(trace.content)[:50]}... (score: {score:.3f})")

    print("\n3. Simulating sleep cycle consolidation...")

    # Enter sleep stages
    await orchestrator.enter_sleep_stage(SleepStage.NREM2)
    print("😴 Entered NREM2 sleep")
    await asyncio.sleep(2)

    await orchestrator.enter_sleep_stage(SleepStage.NREM3)
    print("😴 Entered NREM3 (slow-wave sleep) - consolidating memories...")
    await asyncio.sleep(3)

    await orchestrator.enter_sleep_stage(SleepStage.REM)
    print("😴 Entered REM sleep - creative consolidation...")
    await asyncio.sleep(2)

    await orchestrator.enter_sleep_stage(SleepStage.AWAKE)
    print("😊 Awake again")

    print("\n4. Memory system statistics:")
    stats = orchestrator.get_memory_statistics()

    print(f"  Total memories: {stats['total_memories']}")
    print(f"  Hippocampal: {stats['hippocampal_memories']}")
    print(f"  Neocortical: {stats['neocortical_memories']}")
    print(f"  Working: {stats['working_memories']}")
    print(f"  Consolidation count: {stats['consolidation_count']}")
    print(f"  Average encoding strength: {stats['average_encoding_strength']:.3f}")
    print(f"  Average replay count: {stats['average_replay_count']:.1f}")

    print("\n5. Testing emotional memory retrieval...")
    emotional_results = await orchestrator.retrieve_memory(
        {"emotion": 0.8, "tags": ["achievement"]},
        memory_types=[MemoryType.EMOTIONAL, MemoryType.EPISODIC],
    )

    print(f"Found {len(emotional_results)} emotional memories:")
    for trace, score in emotional_results:
        print(f"  - {trace.content} (valence: {trace.emotional_valence:.2f}, score: {score:.3f})")

    print("\n✅ Unified Memory Orchestrator demonstration complete!")
    print(
        f"\n📊 Final stats: {stats['encoding_count']} encoded, "
        f"{stats['consolidation_count']} consolidated, "
        f"{stats['retrieval_count']} retrieved"
    )


if __name__ == "__main__":
    asyncio.run(demonstrate_unified_memory())
