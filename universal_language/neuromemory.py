"""
Neuroscience-Inspired Memory System for Universal Language
==========================================================

Implements hippocampal-like episodic memory and cortical semantic memory.
Based on what Demis Hassabis/DeepMind would implement.
"""

import hashlib
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from universal_language.core import Symbol

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory based on neuroscience"""
    SENSORY = "sensory"  # Ultra-short term (milliseconds)
    WORKING = "working"  # Short-term active memory (seconds)
    EPISODIC = "episodic"  # Specific events with context
    SEMANTIC = "semantic"  # General knowledge
    PROCEDURAL = "procedural"  # How to do things
    PROSPECTIVE = "prospective"  # Future intentions


class ConsolidationState(Enum):
    """Memory consolidation states (like sleep stages)"""
    ENCODING = "encoding"  # Initial formation
    CONSOLIDATING = "consolidating"  # Strengthening connections
    RECONSOLIDATING = "reconsolidating"  # Updating after retrieval
    CONSOLIDATED = "consolidated"  # Long-term stable


@dataclass
class MemoryTrace:
    """
    Individual memory trace (engram) inspired by neuroscience.
    
    Like neurons encoding memories in the brain.
    """
    trace_id: str
    content: Any  # Symbol, Concept, or raw data
    memory_type: MemoryType
    timestamp: float = field(default_factory=time.time)
    strength: float = 1.0  # Synaptic strength
    activation_count: int = 0
    last_activation: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)
    associations: Set[str] = field(default_factory=set)  # Connected traces
    emotional_valence: float = 0.0  # -1 to 1
    importance: float = 0.5  # 0 to 1
    decay_rate: float = 0.01  # How fast it fades

    def activate(self):
        """Activate this memory trace (like neural firing)"""
        self.activation_count += 1
        self.last_activation = time.time()
        # Strengthen with use (Hebbian learning)
        self.strength = min(1.0, self.strength * 1.1)

    def decay(self, time_delta: float):
        """Apply forgetting curve decay"""
        # Ebbinghaus forgetting curve
        self.strength *= np.exp(-self.decay_rate * time_delta)

    def is_active(self) -> bool:
        """Check if trace is above activation threshold"""
        return self.strength > 0.1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp,
            "strength": self.strength,
            "activation_count": self.activation_count,
            "importance": self.importance,
            "emotional_valence": self.emotional_valence
        }


@dataclass
class EpisodicMemory:
    """
    Episodic memory for specific symbol usage events.
    
    Like the hippocampus encoding specific experiences.
    """
    episode_id: str
    symbols_used: List[Symbol]
    context: Dict[str, Any]
    outcome: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    location_encoding: Optional[np.ndarray] = None  # Place cells
    time_encoding: Optional[np.ndarray] = None  # Time cells
    emotional_context: Dict[str, float] = field(default_factory=dict)
    replay_count: int = 0  # Memory replay during consolidation

    def to_semantic(self) -> Dict[str, Any]:
        """Extract semantic knowledge from episodic memory"""
        return {
            "symbols": [s.name for s in self.symbols_used],
            "patterns": self._extract_patterns(),
            "associations": self._extract_associations()
        }

    def _extract_patterns(self) -> List[str]:
        """Extract patterns from symbol sequence"""
        patterns = []
        for i in range(len(self.symbols_used) - 1):
            pattern = f"{self.symbols_used[i].name}->{self.symbols_used[i+1].name}"
            patterns.append(pattern)
        return patterns

    def _extract_associations(self) -> Dict[str, List[str]]:
        """Extract symbol associations"""
        associations = {}
        for symbol in self.symbols_used:
            associations[symbol.name] = [
                s.name for s in self.symbols_used if s != symbol
            ]
        return associations


class HippocampalBuffer:
    """
    Hippocampal-like temporary buffer for new memories.
    
    Inspired by how the hippocampus temporarily stores memories
    before cortical consolidation.
    """

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.buffer: deque = deque(maxlen=capacity)
        self.pattern_separator: Dict[str, List[MemoryTrace]] = {}
        self.consolidation_queue: List[MemoryTrace] = []

    def encode(self, trace: MemoryTrace):
        """Encode new memory trace"""
        self.buffer.append(trace)

        # Pattern separation - avoid interference
        pattern_key = self._compute_pattern_key(trace)
        if pattern_key not in self.pattern_separator:
            self.pattern_separator[pattern_key] = []
        self.pattern_separator[pattern_key].append(trace)

        # Mark for consolidation if important
        if trace.importance > 0.7:
            self.consolidation_queue.append(trace)

    def replay(self, n_replays: int = 10) -> List[MemoryTrace]:
        """
        Sharp-wave ripple replay for consolidation.
        
        Like how the hippocampus replays memories during rest/sleep.
        """
        replayed = []

        for trace in self.consolidation_queue[:n_replays]:
            trace.activate()  # Strengthen through replay
            replayed.append(trace)

        # Remove replayed items from queue
        self.consolidation_queue = self.consolidation_queue[n_replays:]

        return replayed

    def pattern_complete(self, partial: Dict[str, Any]) -> Optional[MemoryTrace]:
        """
        Pattern completion from partial cues.
        
        Like CA3 region completing patterns from partial input.
        """
        best_match = None
        best_score = 0.0

        for trace in self.buffer:
            score = self._compute_similarity(partial, trace.context)
            if score > best_score:
                best_score = score
                best_match = trace

        if best_score > 0.5:  # Threshold for pattern completion
            return best_match
        return None

    def _compute_pattern_key(self, trace: MemoryTrace) -> str:
        """Compute pattern key for separation"""
        key_parts = [
            trace.memory_type.value,
            str(trace.emotional_valence > 0),
            str(int(trace.importance * 10))
        ]
        return "_".join(key_parts)

    def _compute_similarity(self, dict1: Dict, dict2: Dict) -> float:
        """Compute similarity between two contexts"""
        if not dict1 or not dict2:
            return 0.0

        common_keys = set(dict1.keys()) & set(dict2.keys())
        if not common_keys:
            return 0.0

        matches = sum(1 for k in common_keys if dict1[k] == dict2[k])
        return matches / len(common_keys)


class CorticalNetwork:
    """
    Cortical-like network for semantic memory.
    
    Distributed representation like neocortex.
    """

    def __init__(self):
        self.semantic_nodes: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, Set[str]] = {}  # Synaptic connections
        self.activation_threshold = 0.3
        self.spread_decay = 0.5

    def store_semantic(self, concept_id: str, attributes: Dict[str, Any]):
        """Store semantic knowledge"""
        if concept_id not in self.semantic_nodes:
            self.semantic_nodes[concept_id] = {
                "attributes": {},
                "activation": 0.0,
                "permanent_strength": 0.0
            }

        # Update attributes
        node = self.semantic_nodes[concept_id]
        node["attributes"].update(attributes)

        # Create connections based on shared attributes
        for other_id, other_node in self.semantic_nodes.items():
            if other_id != concept_id:
                similarity = self._compute_attribute_similarity(
                    node["attributes"],
                    other_node["attributes"]
                )
                if similarity > 0.3:
                    self._add_connection(concept_id, other_id, similarity)

    def spreading_activation(self, start_concept: str,
                           max_spread: int = 3) -> List[Tuple[str, float]]:
        """
        Spreading activation through semantic network.
        
        Like how concepts activate related concepts in the brain.
        """
        if start_concept not in self.semantic_nodes:
            return []

        activated = {start_concept: 1.0}
        to_process = [(start_concept, 1.0)]
        spread_count = 0

        while to_process and spread_count < max_spread:
            current_concept, current_activation = to_process.pop(0)

            if current_concept in self.connections:
                for connected in self.connections[current_concept]:
                    # Decay activation as it spreads
                    new_activation = current_activation * self.spread_decay

                    if new_activation > self.activation_threshold:
                        if connected not in activated or activated[connected] < new_activation:
                            activated[connected] = new_activation
                            to_process.append((connected, new_activation))

            spread_count += 1

        # Sort by activation strength
        return sorted(activated.items(), key=lambda x: x[1], reverse=True)

    def hebbian_learning(self, concept1: str, concept2: str):
        """
        Hebbian learning: neurons that fire together wire together.
        """
        self._add_connection(concept1, concept2,
                           strength_increase=0.1)

    def _add_connection(self, concept1: str, concept2: str,
                       strength: float = 0.5, strength_increase: float = 0.0):
        """Add or strengthen connection between concepts"""
        if concept1 not in self.connections:
            self.connections[concept1] = set()
        if concept2 not in self.connections:
            self.connections[concept2] = set()

        self.connections[concept1].add(concept2)
        self.connections[concept2].add(concept1)

        # Store connection strength (simplified)
        # In production, would use weighted edges

    def _compute_attribute_similarity(self, attrs1: Dict, attrs2: Dict) -> float:
        """Compute similarity between attribute sets"""
        if not attrs1 or not attrs2:
            return 0.0

        keys1 = set(attrs1.keys())
        keys2 = set(attrs2.keys())

        common = keys1 & keys2
        if not common:
            return 0.0

        return len(common) / len(keys1 | keys2)


class WorkingMemory:
    """
    Working memory system with limited capacity.
    
    Like prefrontal cortex maintaining active representations.
    """

    def __init__(self, capacity: int = 7):  # Miller's magical number 7±2
        self.capacity = capacity
        self.items: List[Tuple[Any, float]] = []  # (item, activation)
        self.focus: Optional[Any] = None  # Current focus of attention
        self.rehearsal_rate = 0.1

    def add(self, item: Any, priority: float = 0.5):
        """Add item to working memory"""
        # If at capacity, remove least activated
        if len(self.items) >= self.capacity:
            self.items.sort(key=lambda x: x[1])
            self.items.pop(0)

        self.items.append((item, priority))

        # Update focus if high priority
        if priority > 0.8:
            self.focus = item

    def rehearse(self):
        """Rehearse items to maintain in memory"""
        for i, (item, activation) in enumerate(self.items):
            # Decay without rehearsal
            new_activation = activation * (1 - self.rehearsal_rate)

            # Boost if in focus
            if item == self.focus:
                new_activation = min(1.0, new_activation + 0.2)

            self.items[i] = (item, new_activation)

        # Remove items below threshold
        self.items = [(item, act) for item, act in self.items if act > 0.1]

    def retrieve(self, cue: Any) -> Optional[Any]:
        """Retrieve item from working memory"""
        for item, activation in self.items:
            if self._matches_cue(item, cue):
                # Boost activation on retrieval
                self.items = [
                    (i, a + 0.1 if i == item else a)
                    for i, a in self.items
                ]
                return item
        return None

    def _matches_cue(self, item: Any, cue: Any) -> bool:
        """Check if item matches retrieval cue"""
        if item == cue:
            return True

        # Check attributes if available
        if hasattr(item, "__dict__") and hasattr(cue, "__dict__"):
            item_attrs = item.__dict__
            cue_attrs = cue.__dict__

            common = set(item_attrs.keys()) & set(cue_attrs.keys())
            if common:
                matches = sum(1 for k in common if item_attrs[k] == cue_attrs[k])
                return matches / len(common) > 0.5

        return False


class NeuroSymbolicMemory:
    """
    Complete neuroscience-inspired memory system.
    
    Integrates multiple memory systems like the human brain.
    """

    def __init__(self):
        self.hippocampus = HippocampalBuffer()
        self.cortex = CorticalNetwork()
        self.working_memory = WorkingMemory()
        self.episodic_memories: Dict[str, EpisodicMemory] = {}
        self.memory_traces: Dict[str, MemoryTrace] = {}
        self.consolidation_cycles = 0

        logger.info("NeuroSymbolic Memory System initialized")

    def encode_symbol_experience(self, symbols: List[Symbol],
                                context: Dict[str, Any],
                                outcome: Optional[str] = None) -> str:
        """
        Encode a new symbol usage experience.
        
        Creates episodic memory and extracts semantic knowledge.
        """
        # Create episodic memory
        episode = EpisodicMemory(
            episode_id=self._generate_episode_id(),
            symbols_used=symbols,
            context=context,
            outcome=outcome
        )

        self.episodic_memories[episode.episode_id] = episode

        # Create memory traces for each symbol
        for symbol in symbols:
            trace = MemoryTrace(
                trace_id=self._generate_trace_id(),
                content=symbol,
                memory_type=MemoryType.EPISODIC,
                context=context,
                importance=self._calculate_importance(symbol, context, outcome)
            )

            # Encode in hippocampus
            self.hippocampus.encode(trace)
            self.memory_traces[trace.trace_id] = trace

            # Add to working memory if important
            if trace.importance > 0.6:
                self.working_memory.add(symbol, trace.importance)

        # Extract and store semantic knowledge
        semantic = episode.to_semantic()
        for pattern in semantic["patterns"]:
            self.cortex.store_semantic(
                f"PATTERN_{hashlib.sha256(pattern.encode()).hexdigest()[:8]}",
                {"pattern": pattern, "frequency": 1}
            )

        return episode.episode_id

    def recall_by_symbol(self, symbol: Symbol) -> List[EpisodicMemory]:
        """Recall episodes containing a symbol"""
        recalled = []

        for episode in self.episodic_memories.values():
            if any(s.id == symbol.id for s in episode.symbols_used):
                recalled.append(episode)
                episode.replay_count += 1  # Strengthen by recall

        return recalled

    def semantic_search(self, concept: str) -> List[Tuple[str, float]]:
        """
        Search semantic memory using spreading activation.
        """
        return self.cortex.spreading_activation(concept)

    def consolidate_memories(self, cycles: int = 1):
        """
        Consolidate memories from hippocampus to cortex.
        
        Like sleep consolidation in the brain.
        """
        for _ in range(cycles):
            # Replay important memories
            replayed = self.hippocampus.replay()

            for trace in replayed:
                if isinstance(trace.content, Symbol):
                    # Store in semantic memory
                    self.cortex.store_semantic(
                        trace.content.id,
                        {
                            "name": trace.content.name,
                            "domain": trace.content.domain.value,
                            "importance": trace.importance,
                            "valence": trace.emotional_valence
                        }
                    )

            self.consolidation_cycles += 1

    def dream_recombination(self, n_symbols: int = 5) -> List[Symbol]:
        """
        Dream-like recombination of memory traces.
        
        Creates novel symbol combinations like REM sleep.
        """
        # Select random traces weighted by importance
        active_traces = [t for t in self.memory_traces.values() if t.is_active()]

        if len(active_traces) < 2:
            return []

        # Sample traces with probability proportional to importance
        importances = [t.importance for t in active_traces]
        total_importance = sum(importances)
        probs = [i/total_importance for i in importances]

        sampled_indices = np.random.choice(
            len(active_traces),
            size=min(n_symbols, len(active_traces)),
            p=probs,
            replace=False
        )

        recombined = []
        for idx in sampled_indices:
            trace = active_traces[idx]
            if isinstance(trace.content, Symbol):
                # Create dream variant
                dream_symbol = Symbol(
                    id=f"DREAM_{trace.content.id}",
                    domain=trace.content.domain,
                    name=f"dream_{trace.content.name}",
                    value=trace.content.value,
                    attributes={
                        **trace.content.attributes,
                        "is_dream": True,
                        "original_id": trace.content.id
                    }
                )
                recombined.append(dream_symbol)

        return recombined

    def prune_memories(self, threshold: float = 0.1):
        """
        Prune weak memory traces.
        
        Like synaptic pruning in the brain.
        """
        current_time = time.time()
        pruned = []

        for trace_id, trace in list(self.memory_traces.items()):
            # Apply decay
            if trace.last_activation:
                time_delta = (current_time - trace.last_activation) / 3600  # Hours
                trace.decay(time_delta)

            # Prune if below threshold
            if trace.strength < threshold:
                del self.memory_traces[trace_id]
                pruned.append(trace_id)

        logger.info(f"Pruned {len(pruned)} weak memory traces")
        return pruned

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        return {
            "total_traces": len(self.memory_traces),
            "episodic_memories": len(self.episodic_memories),
            "semantic_concepts": len(self.cortex.semantic_nodes),
            "working_memory_items": len(self.working_memory.items),
            "hippocampal_buffer": len(self.hippocampus.buffer),
            "consolidation_cycles": self.consolidation_cycles,
            "average_trace_strength": np.mean([
                t.strength for t in self.memory_traces.values()
            ]) if self.memory_traces else 0
        }

    def _calculate_importance(self, symbol: Symbol, context: Dict[str, Any],
                            outcome: Optional[str]) -> float:
        """Calculate importance of a memory"""
        importance = 0.5  # Base importance

        # Increase for emotional content
        if "emotion" in context:
            importance += 0.2

        # Increase for positive outcomes
        if outcome and "success" in outcome.lower():
            importance += 0.2

        # Increase for rare symbols
        if symbol.attributes.get("frequency", 1) < 0.1:
            importance += 0.1

        return min(1.0, importance)

    def _generate_episode_id(self) -> str:
        """Generate unique episode ID"""
        return f"EPISODE_{int(time.time() * 1000)}"

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        return f"TRACE_{int(time.time() * 1000000)}"


# Singleton instance
_neuromemory_instance = None


def get_neurosymbolic_memory() -> NeuroSymbolicMemory:
    """Get or create singleton NeuroSymbolic Memory"""
    global _neuromemory_instance
    if _neuromemory_instance is None:
        _neuromemory_instance = NeuroSymbolicMemory()
    return _neuromemory_instance
