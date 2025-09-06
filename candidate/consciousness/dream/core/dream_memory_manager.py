#!/usr/bin/env python3
"""
══════════════════════════════════════════════════════════════════════════════════
║ 🚀 LUKHAS AI - ══════════════════════════════════════════════════════════════════════════════════
║ Enhanced memory system with intelligent optimization
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: dream_memory_manager.py
║ Path: memory/dream_memory_manager.py
║ Version: 1.0.0 | Created: 2025-07-29
║ Authors: LUKHAS AI Development Team
╠══════════════════════════════════════════════════════════════════════════════════
║                             ◊ POETIC ESSENCE ◊
║
║ ║ 🧠 LUKHAS AI - DREAM MEMORY MANAGER
║ ║ Memory management for dream states and oneiric experiences
║ ║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║ Module: DREAM_MEMORY_MANAGER.PY
║ ║ Path: lukhas/memory/dream_memory_manager.py
║ ║ Version: 1.0.0 | Created: 2025-07-26
║ ║ Authors: LUKHAS AI Architecture Team
║ ╠══════════════════════════════════════════════════════════════════════════════════
║ ║                        IN THE REALM OF DREAMS: A MEMORY ARCHITECTURE
║ ║ In the labyrinthine corridors of the mind, where whispers of forgotten dreams
║ ║ flit like moths beneath a pale moon, the Dream Memory Manager emerges as a
║ ║ sentinel of memory, a custodian of ephemeral thoughts. This module,
║ ║ intricately woven with the threads of artificial cognition, stands as a beacon
║ ║ guiding the wayfarers of consciousness through the shifting sands of oneiric
║
╠══════════════════════════════════════════════════════════════════════════════════
║ TECHNICAL FEATURES:
║ • Advanced memory system implementation
║ • Optimized performance with intelligent caching
║ • Comprehensive error handling and validation
║ • Integration with LUKHAS AI architecture
║ • Extensible design for future enhancements
║
║ ΛTAG: ΛLUKHAS, ΛMEMORY, ΛSTANDARD, ΛPYTHON
╚══════════════════════════════════════════════════════════════════════════════════
"""

import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from .base_manager import BaseMemoryManager


class DreamMemoryManager(BaseMemoryManager):
    """
    Memory manager specialized for dream states and oneiric experiences.

    Extends BaseMemoryManager with:
    - Dream state classification
    - Oneiric pattern recognition
    - Dream-wake boundary management
    - Symbolic dream interpretation
    - Dream sequence tracking
    - Lucidity level monitoring
    """

    def __init__(self, config: Optional[dict[str, Any]] = None, base_path: Optional[Path] = None):
        """Initialize dream memory manager."""
        super().__init__(config, base_path)

        # Dream configuration
        self.dream_config = {
            "lucidity_threshold": 0.7,
            "symbol_extraction_depth": 3,
            "dream_fade_rate": 0.2,
            "consolidation_period": timedelta(hours=8),
            "max_dream_sequences": 10,
            **self.config.get("dream", {}),
        }

        # Dream state tracking
        self.dream_states: dict[str, dict[str, Any]] = {}
        self.dream_sequences: dict[str, list[str]] = {}
        self.dream_symbols: dict[str, set[str]] = {}
        self.lucidity_scores: dict[str, float] = {}

        # Dream types
        self.dream_types = [
            "lucid",
            "vivid",
            "recurring",
            "prophetic",
            "nightmare",
            "pleasant",
            "abstract",
            "symbolic",
        ]

        # Common dream symbols
        self.common_symbols = {
            "water": ["emotion", "unconscious", "purification"],
            "flying": ["freedom", "escape", "ambition"],
            "falling": ["loss_of_control", "anxiety", "letting_go"],
            "chase": ["avoidance", "fear", "pursuit"],
            "death": ["transformation", "ending", "rebirth"],
            "animals": ["instinct", "nature", "wisdom"],
            "house": ["self", "psyche", "security"],
            "journey": ["life_path", "progress", "discovery"],
        }

        self.logger.info("DreamMemoryManager initialized", dream_config=self.dream_config)

    async def store(
        self,
        memory_data: dict[str, Any],
        memory_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Store dream memory with oneiric analysis.

        Extracts dream symbols and establishes dream state.
        """
        # Generate ID if not provided
        if not memory_id:
            memory_id = self.generate_memory_id("dream")

        try:
            # Extract dream characteristics
            dream_state = self._analyze_dream_content(memory_data, metadata)
            self.dream_states[memory_id] = dream_state

            # Extract symbols
            symbols = self._extract_dream_symbols(memory_data)
            self.dream_symbols[memory_id] = symbols

            # Calculate lucidity score
            lucidity = self._calculate_lucidity(dream_state, memory_data)
            self.lucidity_scores[memory_id] = lucidity

            # Check for dream sequences
            sequence_id = self._identify_dream_sequence(memory_data, symbols)
            if sequence_id:
                if sequence_id not in self.dream_sequences:
                    self.dream_sequences[sequence_id] = []
                self.dream_sequences[sequence_id].append(memory_id)

            # Prepare enhanced metadata
            enhanced_metadata = {
                **(metadata or {}),
                "dream_state": dream_state,
                "dream_symbols": list(symbols),
                "lucidity_score": lucidity,
                "sequence_id": sequence_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            # Package memory with dream data
            memory_package = {
                "data": memory_data,
                "metadata": enhanced_metadata,
                "dream": {
                    "state": dream_state,
                    "symbols": list(symbols),
                    "lucidity": lucidity,
                    "interpretations": self._generate_interpretations(symbols),
                },
            }

            # Save to disk
            self._save_to_disk(memory_id, memory_package)

            # Update index
            self._update_index(memory_id, enhanced_metadata)

            self.logger.info(
                "Dream memory stored",
                memory_id=memory_id,
                dream_type=dream_state.get("type"),
                symbol_count=len(symbols),
            )

            return {
                "status": "success",
                "memory_id": memory_id,
                "dream_type": dream_state.get("type"),
                "lucidity": lucidity,
                "symbols": list(symbols),
            }

        except Exception as e:
            self.logger.error("Failed to store dream memory", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def retrieve(self, memory_id: str, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Retrieve dream memory with fade and interpretation.

        Applies dream fade effect and provides symbolic interpretation.
        """
        try:
            # Load memory package
            memory_package = self._load_from_disk(memory_id)

            # Apply dream fade
            faded_data = self._apply_dream_fade(memory_package["data"], memory_package["metadata"].get("created_at"))

            # Get current dream state
            self.dream_states.get(memory_id, memory_package["dream"]["state"])

            # Apply context-based modulation
            if context and context.get("interpret_symbols", False):
                interpretations = self._generate_interpretations(self.dream_symbols.get(memory_id, set()))
            else:
                interpretations = memory_package["dream"].get("interpretations", {})

            # Check for related dreams in sequence
            related_dreams = []
            for dream_ids in self.dream_sequences.values():
                if memory_id in dream_ids:
                    related_dreams = [did for did in dream_ids if did != memory_id]
                    break

            self.logger.info(
                "Dream memory retrieved",
                memory_id=memory_id,
                fade_applied=faded_data != memory_package["data"],
            )

            return {
                "status": "success",
                "data": faded_data,
                "metadata": {
                    **memory_package["metadata"],
                    "current_lucidity": self.lucidity_scores.get(memory_id, 0),
                    "interpretations": interpretations,
                    "related_dreams": related_dreams,
                },
            }

        except FileNotFoundError:
            self.logger.error("Memory not found", memory_id=memory_id)
            return {"status": "error", "error": f"Memory not found: {memory_id}"}
        except Exception as e:
            self.logger.error("Failed to retrieve dream memory", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def update(self, memory_id: str, updates: dict[str, Any], merge: bool = True) -> dict[str, Any]:
        """Update dream memory with re-analysis."""
        try:
            # Retrieve current state
            current = await self.retrieve(memory_id)
            if current["status"] == "error":
                return current

            # Update data
            updated_data = {**current["data"], **updates} if merge else updates

            # Re-analyze dream content
            new_dream_state = self._analyze_dream_content(updated_data, current["metadata"])

            # Update symbols
            new_symbols = self._extract_dream_symbols(updated_data)
            self.dream_symbols[memory_id] = new_symbols

            # Recalculate lucidity
            new_lucidity = self._calculate_lucidity(new_dream_state, updated_data)
            self.lucidity_scores[memory_id] = new_lucidity

            # Store updated memory
            result = await self.store(
                updated_data,
                memory_id,
                {
                    **current["metadata"],
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            self.logger.info(
                "Dream memory updated",
                memory_id=memory_id,
                symbol_change=len(new_symbols.symmetric_difference(self.dream_symbols.get(memory_id, set()))),
            )

            return result

        except Exception as e:
            self.logger.error("Failed to update dream memory", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def delete(self, memory_id: str, soft_delete: bool = True) -> dict[str, Any]:
        """Delete dream memory with sequence cleanup."""
        try:
            # Clean up dream tracking
            if memory_id in self.dream_states:
                del self.dream_states[memory_id]
            if memory_id in self.dream_symbols:
                del self.dream_symbols[memory_id]
            if memory_id in self.lucidity_scores:
                del self.lucidity_scores[memory_id]

            # Remove from sequences
            for seq_id, dream_ids in list(self.dream_sequences.items()):
                if memory_id in dream_ids:
                    dream_ids.remove(memory_id)
                    if not dream_ids:
                        del self.dream_sequences[seq_id]

            if soft_delete:
                # Mark as deleted in index
                if memory_id in self._memory_index:
                    self._memory_index[memory_id]["deleted"] = True
                    self._memory_index[memory_id]["deleted_at"] = datetime.now(timezone.utc).isoformat()
                    self._save_index()
                    from lukhas.memory.folds.fold_engine import MemoryIntegrityLedger

                    MemoryIntegrityLedger.log_fold_transition(
                        memory_id,
                        "delete",
                        self._memory_index[memory_id],
                        self._memory_index[memory_id],
                    )
            else:
                # Remove from disk
                file_path = self.base_path / f"{memory_id}.json"
                if file_path.exists():
                    file_path.unlink()

                # Remove from index
                if memory_id in self._memory_index:
                    del self._memory_index[memory_id]
                    self._save_index()

            self.logger.info("Dream memory deleted", memory_id=memory_id, soft_delete=soft_delete)

            return {"status": "success"}

        except Exception as e:
            self.logger.error("Failed to delete dream memory", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    async def search(self, criteria: dict[str, Any], limit: Optional[int] = None) -> list[dict[str, Any]]:
        """
        Search dream memories with oneiric filtering.

        Supports dream type, symbol, and lucidity searches.
        """
        results = []

        # Extract dream-specific criteria
        dream_type = criteria.pop("dream_type", None)
        symbols = set(criteria.pop("symbols", []))
        min_lucidity = criteria.pop("min_lucidity", 0.0)
        sequence_id = criteria.pop("sequence_id", None)

        for memory_id, index_data in self._memory_index.items():
            # Skip deleted memories
            if index_data.get("deleted", False):
                continue

            # Check dream type
            dream_state = index_data.get("dream_state", {})
            if dream_type and dream_state.get("type") != dream_type:
                continue

            # Check lucidity
            if self.lucidity_scores.get(memory_id, 0) < min_lucidity:
                continue

            # Check symbols
            if symbols:
                memory_symbols = self.dream_symbols.get(memory_id, set())
                if not symbols.issubset(memory_symbols):
                    continue

            # Check sequence
            if sequence_id and memory_id not in self.dream_sequences.get(sequence_id, []):
                continue

            # Load and check other criteria
            try:
                memory_data = self._load_from_disk(memory_id)
                if self._matches_criteria(memory_data["data"], criteria):
                    results.append(
                        {
                            "memory_id": memory_id,
                            "data": memory_data["data"],
                            "dream_type": dream_state.get("type"),
                            "lucidity": self.lucidity_scores.get(memory_id, 0),
                            "metadata": index_data,
                        }
                    )
            except Exception as e:
                self.logger.warning(
                    "Failed to load memory during search",
                    memory_id=memory_id,
                    error=str(e),
                )

        # Sort by lucidity if no limit
        if not limit:
            results.sort(key=lambda x: x["lucidity"], reverse=True)

        # Apply limit
        if limit and len(results) > limit:
            results = results[:limit]

        return results

    # === Dream-specific methods ===

    async def get_dream_sequence(self, sequence_id: str) -> dict[str, Any]:
        """Get all dreams in a sequence."""
        if sequence_id not in self.dream_sequences:
            return {
                "status": "error",
                "error": f"Dream sequence not found: {sequence_id}",
            }

        dream_ids = self.dream_sequences[sequence_id]
        dreams = []

        for dream_id in dream_ids:
            dream = await self.retrieve(dream_id)
            if dream["status"] == "success":
                dreams.append(
                    {
                        "memory_id": dream_id,
                        "data": dream["data"],
                        "metadata": dream["metadata"],
                    }
                )

        return {
            "status": "success",
            "sequence_id": sequence_id,
            "dream_count": len(dreams),
            "dreams": dreams,
        }

    async def analyze_dream_patterns(self) -> dict[str, Any]:
        """Analyze patterns across all dream memories."""
        patterns = {
            "total_dreams": len(self.dream_states),
            "dream_type_distribution": {},
            "common_symbols": {},
            "average_lucidity": 0.0,
            "recurring_sequences": [],
        }

        # Analyze dream types
        type_counts = {}
        for dream_state in self.dream_states.values():
            dream_type = dream_state.get("type", "unknown")
            type_counts[dream_type] = type_counts.get(dream_type, 0) + 1
        patterns["dream_type_distribution"] = type_counts

        # Analyze symbols
        symbol_counts = {}
        for symbols in self.dream_symbols.values():
            for symbol in symbols:
                symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

        # Get top 10 most common symbols
        patterns["common_symbols"] = dict(sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True)[:10])

        # Calculate average lucidity
        if self.lucidity_scores:
            patterns["average_lucidity"] = sum(self.lucidity_scores.values()) / len(self.lucidity_scores)

        # Find recurring sequences
        for seq_id, dream_ids in self.dream_sequences.items():
            if len(dream_ids) >= 3:  # Sequence with 3+ dreams
                patterns["recurring_sequences"].append(
                    {
                        "sequence_id": seq_id,
                        "dream_count": len(dream_ids),
                        "dreams": dream_ids[:5],  # First 5 dreams
                    }
                )

        return patterns

    async def enhance_lucidity(self, memory_id: str) -> dict[str, Any]:
        """Enhance lucidity of a dream memory."""
        try:
            # Verify memory exists
            memory = await self.retrieve(memory_id)
            if memory["status"] == "error":
                return memory

            # Get current lucidity
            current_lucidity = self.lucidity_scores.get(memory_id, 0.5)

            # Enhance lucidity (up to threshold)
            new_lucidity = min(current_lucidity * 1.2, self.dream_config["lucidity_threshold"])

            self.lucidity_scores[memory_id] = new_lucidity

            # Update dream state
            if memory_id in self.dream_states:
                self.dream_states[memory_id]["lucidity_enhanced"] = True
                self.dream_states[memory_id]["enhancement_time"] = datetime.now(timezone.utc).isoformat()

            self.logger.info(
                "Dream lucidity enhanced",
                memory_id=memory_id,
                old_lucidity=current_lucidity,
                new_lucidity=new_lucidity,
            )

            return {
                "status": "success",
                "memory_id": memory_id,
                "previous_lucidity": current_lucidity,
                "enhanced_lucidity": new_lucidity,
            }

        except Exception as e:
            self.logger.error("Failed to enhance lucidity", memory_id=memory_id, error=str(e))
            return {"status": "error", "memory_id": memory_id, "error": str(e)}

    # === Private helper methods ===

    def _analyze_dream_content(self, memory_data: dict[str, Any], metadata: Optional[dict[str, Any]]) -> dict[str, Any]:
        """Analyze dream content to determine dream state."""
        # Check if dream state is explicitly provided
        if metadata and "dream_state" in metadata:
            return metadata["dream_state"]

        # Analyze content for dream characteristics
        content_str = str(memory_data).lower()

        # Determine dream type based on content
        dream_type = "abstract"  # Default

        if any(word in content_str for word in ["lucid", "aware", "control"]):
            dream_type = "lucid"
        elif any(word in content_str for word in ["nightmare", "terror", "fear"]):
            dream_type = "nightmare"
        elif any(word in content_str for word in ["recurring", "again", "repeat"]):
            dream_type = "recurring"
        elif any(word in content_str for word in ["vivid", "clear", "detailed"]):
            dream_type = "vivid"
        elif any(word in content_str for word in ["pleasant", "happy", "peaceful"]):
            dream_type = "pleasant"
        elif any(word in content_str for word in ["future", "prophetic", "vision"]):
            dream_type = "prophetic"
        elif any(word in content_str for word in ["symbol", "meaning", "sign"]):
            dream_type = "symbolic"

        return {
            "type": dream_type,
            "intensity": random.uniform(0.3, 0.9),  # Simulated intensity
            "clarity": random.uniform(0.2, 0.8),  # Simulated clarity
            "emotional_tone": self._detect_emotional_tone(content_str),
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _extract_dream_symbols(self, memory_data: dict[str, Any]) -> set[str]:
        """Extract symbolic elements from dream content."""
        symbols = set()
        content_str = str(memory_data).lower()

        # Check for common dream symbols
        for symbol, keywords in self.common_symbols.items():
            if symbol in content_str or any(kw in content_str for kw in keywords):
                symbols.add(symbol)

        # Extract additional symbols based on patterns
        symbol_patterns = {
            "numbers": [
                "one",
                "two",
                "three",
                "four",
                "five",
                "six",
                "seven",
                "eight",
                "nine",
            ],
            "colors": ["red", "blue", "green", "yellow", "black", "white", "purple"],
            "elements": ["fire", "water", "earth", "air", "wind"],
            "celestial": ["sun", "moon", "stars", "sky", "clouds"],
            "nature": ["tree", "forest", "ocean", "mountain", "river"],
        }

        for category, patterns in symbol_patterns.items():
            if any(pattern in content_str for pattern in patterns):
                symbols.add(category)

        return symbols

    def _calculate_lucidity(self, dream_state: dict[str, Any], memory_data: dict[str, Any]) -> float:
        """Calculate lucidity score for dream."""
        base_lucidity = 0.3

        # Increase for lucid dream type
        if dream_state.get("type") == "lucid":
            base_lucidity += 0.4

        # Adjust based on clarity
        clarity = dream_state.get("clarity", 0.5)
        base_lucidity += clarity * 0.2

        # Check for lucidity indicators in content
        content_str = str(memory_data).lower()
        lucidity_indicators = [
            "realize",
            "aware",
            "control",
            "choose",
            "decide",
            "conscious",
            "lucid",
            "know",
            "understand",
        ]

        indicator_count = sum(1 for indicator in lucidity_indicators if indicator in content_str)
        base_lucidity += min(indicator_count * 0.05, 0.2)

        return min(base_lucidity, 1.0)

    def _identify_dream_sequence(self, memory_data: dict[str, Any], symbols: set[str]) -> Optional[str]:
        """Identify if dream belongs to a sequence."""
        # Check existing sequences for similarity
        for seq_id, dream_ids in self.dream_sequences.items():
            if not dream_ids:
                continue

            # Get symbols from sequence dreams
            sequence_symbols = set()
            for dream_id in dream_ids[:3]:  # Check first 3 dreams
                sequence_symbols.update(self.dream_symbols.get(dream_id, set()))

            # Calculate symbol overlap
            if sequence_symbols:
                overlap = len(symbols.intersection(sequence_symbols)) / len(sequence_symbols)
                if overlap > 0.6:  # 60% symbol overlap
                    return seq_id

        # Create new sequence if recurring indicators found
        content_str = str(memory_data).lower()
        if any(word in content_str for word in ["recurring", "again", "repeat", "same dream"]):
            return f"seq_{datetime.now(timezone.utc).timestamp()}"

        return None

    def _generate_interpretations(self, symbols: set[str]) -> dict[str, list[str]]:
        """Generate symbolic interpretations for dream symbols."""
        interpretations = {}

        for symbol in symbols:
            if symbol in self.common_symbols:
                interpretations[symbol] = self.common_symbols[symbol]
            else:
                # Generate generic interpretation
                interpretations[symbol] = [
                    "personal_significance",
                    "unconscious_message",
                    "symbolic_representation",
                ]

        return interpretations

    def _apply_dream_fade(self, memory_data: dict[str, Any], created_at: Optional[str]) -> dict[str, Any]:
        """Apply dream fade effect based on time elapsed."""
        if not created_at:
            return memory_data

        try:
            created_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            elapsed = datetime.now(timezone.utc) - created_time

            # Calculate fade factor
            hours_elapsed = elapsed.total_seconds() / 3600
            fade_factor = max(0, 1 - (hours_elapsed * self.dream_config["dream_fade_rate"] / 24))

            if fade_factor < 1.0:
                # Apply fade by adding metadata
                faded_data = memory_data.copy()
                faded_data["_dream_fade"] = {
                    "fade_factor": fade_factor,
                    "hours_elapsed": hours_elapsed,
                    "clarity_reduction": 1 - fade_factor,
                }
                return faded_data
        except Exception as e:
            self.logger.warning("Failed to apply dream fade", error=str(e))

        return memory_data

    def _detect_emotional_tone(self, content: str) -> str:
        """Detect emotional tone of dream content."""
        positive_words = ["happy", "joy", "peace", "love", "light", "beautiful"]
        negative_words = ["fear", "dark", "scary", "sad", "angry", "lost"]
        neutral_words = ["strange", "different", "unusual", "curious"]

        positive_count = sum(1 for word in positive_words if word in content)
        negative_count = sum(1 for word in negative_words if word in content)
        neutral_count = sum(1 for word in neutral_words if word in content)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        elif neutral_count > 0:
            return "neutral"
        else:
            return "ambiguous"

    def _matches_criteria(self, data: dict[str, Any], criteria: dict[str, Any]) -> bool:
        """Check if data matches search criteria."""
        for key, value in criteria.items():
            if key not in data:
                return False
            if data[key] != value:
                return False
        return True

    async def get_statistics(self) -> dict[str, Any]:
        """Get dream memory statistics."""
        base_stats = await super().get_statistics()

        # Calculate dream-specific statistics
        dream_types = {}
        total_symbols = 0

        for dream_state in self.dream_states.values():
            dream_type = dream_state.get("type", "unknown")
            dream_types[dream_type] = dream_types.get(dream_type, 0) + 1

        for symbols in self.dream_symbols.values():
            total_symbols += len(symbols)

        # Add dream-specific stats
        dream_stats = {
            **base_stats,
            "dream_memories": len(self.dream_states),
            "dream_type_distribution": dream_types,
            "total_symbols_extracted": total_symbols,
            "average_symbols_per_dream": (total_symbols / len(self.dream_symbols) if self.dream_symbols else 0),
            "average_lucidity": (
                sum(self.lucidity_scores.values()) / len(self.lucidity_scores) if self.lucidity_scores else 0
            ),
            "dream_sequences": len(self.dream_sequences),
            "lucidity_threshold": self.dream_config["lucidity_threshold"],
        }

        return dream_stats
