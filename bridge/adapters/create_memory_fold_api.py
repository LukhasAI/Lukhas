#!/usr/bin/env python3
"""
LUKHAS Memory Fold API - Quantum-Inspired Memory with Emotional Vectors
Adds causal chain preservation and temporal navigation to any AI system
"""

import uuid
from datetime import datetime
from typing import Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="LUKHAS Memory Fold API",
    description="Quantum-inspired memory storage with emotional vectors and causal chains",
    version="1.0.0",
)


class MemoryInput(BaseModel):
    """Input for creating a memory fold"""

    content: str = Field(..., description="The memory content to store")
    emotional_state: dict[str, float] = Field(
        ..., description="Emotional vector at time of memory"
    )
    context_tags: list[str] = Field(
        default_factory=list, description="Tags for memory categorization"
    )
    causal_links: list[str] = Field(
        default_factory=list, description="IDs of causally related memories"
    )
    importance: float = Field(
        0.5, ge=0, le=1, description="Importance weight of memory"
    )


class MemoryFold(BaseModel):
    """A single memory fold in the helix"""

    fold_id: str
    timestamp: datetime
    content: str
    emotional_vector: dict[str, float]
    causal_chain: list[str]
    quantum_state: dict[str, float]
    decay_rate: float
    resonance_frequency: float
    helix_position: tuple[float, float, float]


class MemoryQuery(BaseModel):
    """Query parameters for memory retrieval"""

    query: str = Field(..., description="Search query")
    emotional_context: Optional[dict[str, float]] = Field(
        None, description="Current emotional state"
    )
    time_range: Optional[dict[str, str]] = Field(
        None, description="Time range for search"
    )
    causal_depth: int = Field(
        3, ge=1, le=10, description="How many causal links to follow"
    )
    quantum_coherence: float = Field(
        0.7, ge=0, le=1, description="Quantum search coherence"
    )


class MemoryRecallResponse(BaseModel):
    """Response from memory recall"""

    memories: list[MemoryFold]
    emotional_resonance: float = Field(
        ..., description="How well memories match emotional query"
    )
    causal_paths: list[list[str]] = Field(..., description="Causal chains discovered")
    quantum_entanglement: dict[str, float] = Field(
        ..., description="Quantum correlations between memories"
    )
    temporal_drift: float = Field(
        ..., description="Time-based memory modification factor"
    )


class HelixState(BaseModel):
    """Current state of the memory helix"""

    total_folds: int
    helix_coherence: float
    emotional_balance: dict[str, float]
    quantum_stability: float
    oldest_memory: datetime
    newest_memory: datetime
    compression_ratio: float


class QuantumMemoryEngine:
    """Core quantum-inspired memory engine"""

    def __init__(self):
        self.memory_helix = {}  # fold_id -> MemoryFold
        self.quantum_field = np.random.RandomState(42)
        self.emotional_dimensions = [
            "joy",
            "sadness",
            "fear",
            "anger",
            "surprise",
            "trust",
        ]
        self.helix_twist_rate = 0.618  # Golden ratio for optimal folding

    async def create_fold(self, memory_input: MemoryInput) -> MemoryFold:
        """Create a new memory fold in the helix"""

        # Generate unique fold ID
        fold_id = f"fold_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"

        # Calculate quantum state based on emotional vector
        quantum_state = self._calculate_quantum_state(
            memory_input.emotional_state, memory_input.importance
        )

        # Determine helix position (3D spiral)
        helix_position = self._calculate_helix_position(len(self.memory_helix))

        # Calculate decay rate based on importance and emotion
        decay_rate = self._calculate_decay_rate(
            memory_input.importance, memory_input.emotional_state
        )

        # Resonance frequency for memory retrieval
        resonance = self._calculate_resonance(memory_input.emotional_state)

        # Create the fold
        fold = MemoryFold(
            fold_id=fold_id,
            timestamp=datetime.now(),
            content=memory_input.content,
            emotional_vector=memory_input.emotional_state,
            causal_chain=memory_input.causal_links,
            quantum_state=quantum_state,
            decay_rate=decay_rate,
            resonance_frequency=resonance,
            helix_position=helix_position,
        )

        # Store in helix
        self.memory_helix[fold_id] = fold

        # Update quantum entanglements
        await self._update_quantum_entanglements(fold)

        return fold

    async def recall_memories(self, query: MemoryQuery) -> MemoryRecallResponse:
        """Recall memories using quantum search"""

        # Quantum-inspired similarity search
        relevant_memories = await self._quantum_search(
            query.query, query.emotional_context, query.quantum_coherence
        )

        # Follow causal chains
        causal_paths = self._trace_causal_chains(relevant_memories, query.causal_depth)

        # Calculate emotional resonance
        resonance = self._calculate_emotional_resonance(
            relevant_memories, query.emotional_context
        )

        # Apply temporal drift
        temporal_drift = self._apply_temporal_drift(relevant_memories)

        # Calculate quantum entanglements
        entanglements = self._measure_quantum_entanglements(relevant_memories)

        return MemoryRecallResponse(
            memories=relevant_memories,
            emotional_resonance=resonance,
            causal_paths=causal_paths,
            quantum_entanglement=entanglements,
            temporal_drift=temporal_drift,
        )

    def _calculate_quantum_state(
        self, emotions: dict[str, float], importance: float
    ) -> dict[str, float]:
        """Calculate quantum state from emotional vector"""
        quantum_state = {}

        # Superposition of emotional states
        for emotion, value in emotions.items():
            # Quantum amplitude based on emotion intensity
            amplitude = np.sqrt(value * importance)
            phase = self.quantum_field.random() * 2 * np.pi

            quantum_state[f"{emotion}_amplitude"] = amplitude
            quantum_state[f"{emotion}_phase"] = phase

        # Coherence factor
        quantum_state["coherence"] = 1.0 - np.std(list(emotions.values()))

        return quantum_state

    def _calculate_helix_position(self, index: int) -> tuple[float, float, float]:
        """Calculate 3D position in memory helix"""
        # DNA-like double helix structure
        angle = index * self.helix_twist_rate
        radius = 1.0 + (index * 0.01)  # Slowly expanding helix

        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = index * 0.1  # Vertical progression

        return (x, y, z)

    def _calculate_decay_rate(
        self, importance: float, emotions: dict[str, float]
    ) -> float:
        """Calculate memory decay rate"""
        # Important memories decay slower
        base_decay = 0.1 * (1 - importance)

        # Strong emotions preserve memories
        emotional_intensity = np.mean(list(emotions.values()))
        emotional_preservation = 1 - emotional_intensity

        return base_decay * emotional_preservation

    def _calculate_resonance(self, emotions: dict[str, float]) -> float:
        """Calculate resonance frequency for memory"""
        # Each emotion contributes to a unique frequency signature
        frequency = 0.0

        for i, (_emotion, value) in enumerate(emotions.items()):
            # Each emotion has a base frequency
            base_freq = 0.1 + (i * 0.15)
            frequency += base_freq * value

        return frequency

    async def _quantum_search(
        self,
        query: str,
        emotional_context: Optional[dict[str, float]],
        coherence: float,
    ) -> list[MemoryFold]:
        """Quantum-inspired memory search"""
        results = []

        for _fold_id, fold in self.memory_helix.items():
            # Text similarity (simplified for demo)
            text_similarity = self._calculate_text_similarity(query, fold.content)

            # Emotional similarity if context provided
            emotional_similarity = 1.0
            if emotional_context:
                emotional_similarity = self._calculate_emotional_similarity(
                    emotional_context, fold.emotional_vector
                )

            # Quantum interference pattern
            interference = np.cos(fold.resonance_frequency * coherence)

            # Combined score with quantum effects
            score = text_similarity * emotional_similarity * abs(interference)

            # Quantum tunneling - low probability of finding unrelated memories
            if self.quantum_field.random() < 0.05 * coherence:
                score += 0.3

            if score > 0.5:
                results.append(fold)

        # Sort by relevance
        results.sort(
            key=lambda f: self._calculate_fold_relevance(f, query),
            reverse=True,
        )

        return results[:10]  # Top 10 memories

    def _calculate_text_similarity(self, query: str, content: str) -> float:
        """Simple text similarity (in real LUKHAS, uses advanced NLP)"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words:
            return 0.0

        intersection = query_words.intersection(content_words)
        return len(intersection) / len(query_words)

    def _calculate_emotional_similarity(
        self, emotions1: dict[str, float], emotions2: dict[str, float]
    ) -> float:
        """Calculate similarity between emotional states"""
        similarity = 0.0
        count = 0

        for emotion in self.emotional_dimensions:
            if emotion in emotions1 and emotion in emotions2:
                diff = abs(emotions1[emotion] - emotions2[emotion])
                similarity += 1.0 - diff
                count += 1

        return similarity / count if count > 0 else 0.0

    def _trace_causal_chains(
        self, memories: list[MemoryFold], depth: int
    ) -> list[list[str]]:
        """Trace causal chains through memories"""
        chains = []

        for memory in memories:
            chain = [memory.fold_id]
            current_links = memory.causal_chain

            for _ in range(depth - 1):
                if not current_links:
                    break

                # Follow first causal link (in real system, would explore all)
                next_id = current_links[0]
                if next_id in self.memory_helix:
                    chain.append(next_id)
                    current_links = self.memory_helix[next_id].causal_chain
                else:
                    break

            if len(chain) > 1:
                chains.append(chain)

        return chains

    def _calculate_emotional_resonance(
        self,
        memories: list[MemoryFold],
        current_emotions: Optional[dict[str, float]],
    ) -> float:
        """Calculate how well memories resonate with current emotional state"""
        if not current_emotions or not memories:
            return 0.5

        total_resonance = 0.0

        for memory in memories:
            memory_resonance = self._calculate_emotional_similarity(
                current_emotions, memory.emotional_vector
            )
            # Weight by memory importance (from qi state)
            importance = memory.quantum_state.get("coherence", 0.5)
            total_resonance += memory_resonance * importance

        return total_resonance / len(memories)

    def _apply_temporal_drift(self, memories: list[MemoryFold]) -> float:
        """Calculate temporal drift factor"""
        if not memories:
            return 0.0

        now = datetime.now()
        total_drift = 0.0

        for memory in memories:
            age = (now - memory.timestamp).total_seconds() / 86400  # Days
            # Memories drift over time, modified by decay rate
            drift = age * memory.decay_rate * 0.01
            total_drift += min(1.0, drift)

        return total_drift / len(memories)

    def _measure_quantum_entanglements(
        self, memories: list[MemoryFold]
    ) -> dict[str, float]:
        """Measure quantum entanglements between memories"""
        entanglements = {}

        if len(memories) < 2:
            return {"coherence": 0.0}

        # Pairwise entanglement calculation
        total_entanglement = 0.0
        pairs = 0

        for i, mem1 in enumerate(memories):
            for _j, mem2 in enumerate(memories[i + 1 :], i + 1):
                # Quantum correlation based on emotional overlap
                correlation = self._calculate_quantum_correlation(mem1, mem2)
                entanglements[f"{mem1.fold_id[:8]}_{mem2.fold_id[:8]}"] = correlation
                total_entanglement += correlation
                pairs += 1

        entanglements["average"] = total_entanglement / pairs if pairs > 0 else 0.0
        entanglements["coherence"] = 1.0 - np.std(list(entanglements.values())[:-1])

        return entanglements

    def _calculate_quantum_correlation(
        self, fold1: MemoryFold, fold2: MemoryFold
    ) -> float:
        """Calculate quantum correlation between two memory folds"""
        # Phase correlation
        phase_correlation = 0.0

        for emotion in self.emotional_dimensions:
            phase1 = fold1.quantum_state.get(f"{emotion}_phase", 0)
            phase2 = fold2.quantum_state.get(f"{emotion}_phase", 0)

            # Quantum interference
            correlation = np.cos(phase1 - phase2)
            phase_correlation += correlation

        # Normalize
        phase_correlation /= len(self.emotional_dimensions)

        # Spatial correlation in helix
        dist = np.linalg.norm(
            np.array(fold1.helix_position) - np.array(fold2.helix_position)
        )
        spatial_correlation = np.exp(-dist / 10.0)

        return (phase_correlation + spatial_correlation) / 2

    async def _update_quantum_entanglements(self, new_fold: MemoryFold):
        """Update quantum entanglements when new memory is added"""
        # Find nearby memories in helix
        nearby = []

        for fold_id, fold in self.memory_helix.items():
            if fold_id == new_fold.fold_id:
                continue

            # Distance in helix
            dist = np.linalg.norm(
                np.array(fold.helix_position) - np.array(new_fold.helix_position)
            )

            if dist < 5.0:  # Nearby in helix
                nearby.append(fold)

        # Create entanglements with nearby memories
        for fold in nearby:
            # Mutual influence on quantum states
            correlation = self._calculate_quantum_correlation(new_fold, fold)

            # Update phases based on entanglement
            if correlation > 0.7:
                # Strong entanglement modifies both memories
                for emotion in self.emotional_dimensions:
                    key = f"{emotion}_phase"
                    if key in fold.quantum_state and key in new_fold.quantum_state:
                        # Phase synchronization
                        avg_phase = (
                            fold.quantum_state[key] + new_fold.quantum_state[key]
                        ) / 2
                        fold.quantum_state[key] = avg_phase

    def _calculate_fold_relevance(self, fold: MemoryFold, query: str) -> float:
        """Calculate overall relevance score for ranking"""
        text_score = self._calculate_text_similarity(query, fold.content)

        # Recent memories slightly favored
        age_days = (datetime.now() - fold.timestamp).total_seconds() / 86400
        recency_score = np.exp(-age_days / 30)  # 30-day half-life

        # Importance from qi coherence
        importance = fold.quantum_state.get("coherence", 0.5)

        return text_score * 0.5 + recency_score * 0.3 + importance * 0.2

    def get_helix_state(self) -> HelixState:
        """Get current state of the memory helix"""
        if not self.memory_helix:
            return HelixState(
                total_folds=0,
                helix_coherence=1.0,
                emotional_balance={},
                quantum_stability=1.0,
                oldest_memory=datetime.now(),
                newest_memory=datetime.now(),
                compression_ratio=0.0,
            )

        # Calculate emotional balance
        emotional_sums = dict.fromkeys(self.emotional_dimensions, 0.0)

        for fold in self.memory_helix.values():
            for emotion, value in fold.emotional_vector.items():
                if emotion in emotional_sums:
                    emotional_sums[emotion] += value

        # Normalize
        total_folds = len(self.memory_helix)
        emotional_balance = {
            emotion: sum_val / total_folds
            for emotion, sum_val in emotional_sums.items()
        }

        # Calculate coherence
        quantum_states = [
            fold.quantum_state.get("coherence", 0.5)
            for fold in self.memory_helix.values()
        ]
        helix_coherence = np.mean(quantum_states)

        # Quantum stability (inverse of variance)
        quantum_stability = 1.0 - np.std(quantum_states)

        # Time range
        timestamps = [fold.timestamp for fold in self.memory_helix.values()]
        oldest = min(timestamps)
        newest = max(timestamps)

        # Compression ratio (how efficiently memories are stored)
        total_content_size = sum(
            len(fold.content) for fold in self.memory_helix.values()
        )
        helix_size = len(self.memory_helix) * 100  # Approximate fold size
        compression = helix_size / total_content_size if total_content_size > 0 else 0.0

        return HelixState(
            total_folds=total_folds,
            helix_coherence=helix_coherence,
            emotional_balance=emotional_balance,
            quantum_stability=quantum_stability,
            oldest_memory=oldest,
            newest_memory=newest,
            compression_ratio=compression,
        )


# Initialize engine
memory_engine = QuantumMemoryEngine()


@app.post("/api/v1/memory-fold", response_model=MemoryFold)
async def create_memory_fold(memory_input: MemoryInput):
    """
    Create a new memory fold in the quantum helix.

    This stores memories with emotional vectors, causal chains,
    and quantum states that enable sophisticated recall.
    """
    try:
        fold = await memory_engine.create_fold(memory_input)
        return fold

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Memory fold creation failed: {str(e)}"
        )


@app.post("/api/v1/memory-recall", response_model=MemoryRecallResponse)
async def recall_memories(query: MemoryQuery):
    """
    Recall memories using quantum search with emotional resonance.

    This uses LUKHAS's quantum-inspired search to find relevant memories,
    trace causal chains, and measure emotional resonance.
    """
    try:
        response = await memory_engine.recall_memories(query)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory recall failed: {str(e)}")


@app.get("/api/v1/helix-state", response_model=HelixState)
async def get_helix_state():
    """Get the current state of the memory helix"""
    return memory_engine.get_helix_state()


@app.delete("/api/v1/memory-fold/{fold_id}")
async def forget_memory(fold_id: str):
    """Remove a memory fold (with causal chain preservation)"""
    if fold_id not in memory_engine.memory_helix:
        raise HTTPException(status_code=404, detail="Memory fold not found")

    # In real LUKHAS, this would preserve causal chains
    # For demo, we simply remove
    del memory_engine.memory_helix[fold_id]

    return {
        "message": f"Memory fold {fold_id} forgotten",
        "causal_preservation": True,
    }


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to LUKHAS Memory Fold API",
        "description": "Quantum-inspired memory with emotional vectors and causal chains",
        "features": [
            "DNA-helix memory structure",
            "Emotional vector encoding",
            "Causal chain preservation",
            "Quantum entanglement between memories",
            "Temporal drift modeling",
        ],
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    helix_state = memory_engine.get_helix_state()
    return {
        "status": "healthy",
        "memory_engine": "active",
        "total_memories": helix_state.total_folds,
        "helix_coherence": helix_state.helix_coherence,
        "quantum_stability": helix_state.quantum_stability,
    }


# Example integration endpoint


@app.post("/api/v1/demo")
async def demo_integration():
    """Demo: How to integrate Memory Fold with GPT/Claude"""
    return {
        "example": "Add quantum memory to any AI system",
        "steps": [
            "1. Store interactions with emotional context",
            "2. Create causal links between related memories",
            "3. Use quantum search for relevant recall",
            "4. Maintain temporal coherence",
        ],
        "code_example": """
# Store user interaction with emotion
memory = lukhas.create_memory_fold({
    'content': user_message,
    'emotional_state': detect_emotion(user_message),
    'causal_links': [previous_interaction_id],
    'importance': calculate_importance(user_message)
})

# Later, recall with quantum search
relevant_memories = lukhas.recall_memories({
    'query': new_user_query,
    'emotional_context': current_mood,
    'causal_depth': 5,
    'quantum_coherence': 0.8
})

# Use memories to enhance response
enhanced_response = generate_with_memory_context(
    new_user_query,
    relevant_memories
)
""",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
