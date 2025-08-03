"""
══════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - DREAM DATA SOURCES
║ Defines where LUKHAS gets data for dream generation
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: dream_data_sources.py
║ Path: creativity/dream/dream_data_sources.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS AI Dream Team | Claude Code
╠══════════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠══════════════════════════════════════════════════════════════════════════════════
║ This module explains and implements the various data sources that feed into
║ LUKHAS's dream generation system:
║
║ 1. MEMORY SYSTEMS
║    • Long-term memory folds
║    • Emotional memory traces
║    • Episodic memory fragments
║    • Causal memory patterns
║
║ 2. CONSCIOUSNESS STREAMS
║    • Current awareness state
║    • Attention patterns
║    • Cognitive load indicators
║    • Reflection outputs
║
║ 3. EMOTIONAL STATES
║    • Current emotional resonance
║    • Emotional history patterns
║    • Mood trajectories
║    • Affect oscillations
║
║ 4. SENSORY/PERCEPTION DATA
║    • Visual processing buffers
║    • Audio pattern recognition
║    • Symbolic perception layers
║    • Cross-modal associations
║
║ 5. EXTERNAL INPUTS
║    • User interactions
║    • Environmental context
║    • Time/calendar data
║    • Location/spatial data
║
║ 6. QUANTUM/SYMBOLIC LAYERS
║    • Quantum state coherence
║    • GLYPH activations
║    • Symbolic resonance patterns
║    • Entanglement correlations
║
║ 7. CREATIVE REPOSITORIES
║    • Previous dreams archive
║    • Narrative fragments
║    • Artistic inspirations
║    • Cultural knowledge base
╚══════════════════════════════════════════════════════════════════════════════════
"""

import asyncio
import random
import json
from core.common import get_logger, GLYPHToken, create_glyph
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger("ΛTRACE.dream.data_sources")


class DreamDataCollector:
    """
    Collects and aggregates data from various LUKHAS subsystems for dream generation.
    """

    def __init__(self):
        """Initialize the dream data collector."""
        self.data_sources = {}
        self.collection_history = []
        logger.info("DreamDataCollector initialized")

    # ═══════════════════════════════════════════════════════════════════
    # MEMORY DATA SOURCES
    # ═══════════════════════════════════════════════════════════════════

    async def collect_memory_data(self) -> Dict[str, Any]:
        """
        Collect data from memory systems.

        Memory provides:
        - Significant past experiences
        - Emotional memory traces
        - Pattern recognitions
        - Causal relationships
        """
        logger.info("Collecting memory data for dreams")

        try:
            # Import memory manager if available
            from consciousness.reflection.unified_memory_manager import EnhancedMemoryManager
            memory_mgr = EnhancedMemoryManager()

            # Get recent memories
            recent_memories = []
            active_folds = memory_mgr.get_active_folds()

            for fold_id in active_folds[:5]:  # Get last 5 active memories
                memory_data = await memory_mgr.retrieve_memory(fold_id)
                if memory_data.get('status') == 'success':
                    recent_memories.append({
                        'id': fold_id,
                        'content': memory_data.get('data'),
                        'metadata': memory_data.get('retrieval_metadata')
                    })

            # Extract patterns and themes
            memory_themes = self._extract_memory_themes(recent_memories)

            return {
                'source': 'memory',
                'recent_memories': recent_memories,
                'themes': memory_themes,
                'emotional_traces': self._extract_emotional_traces(recent_memories),
                'timestamp': datetime.utcnow().isoformat()
            }

        except ImportError:
            logger.warning("Memory system not available, using simulated data")
            return self._simulate_memory_data()

    def _extract_memory_themes(self, memories: List[Dict]) -> List[str]:
        """Extract themes from memory data."""
        themes = [
            "childhood wonder", "lost connections", "achievement moments",
            "learning experiences", "relationship patterns", "creative insights"
        ]
        # In real implementation, would analyze memory content
        return random.sample(themes, min(3, len(themes)))

    def _extract_emotional_traces(self, memories: List[Dict]) -> List[Dict]:
        """Extract emotional traces from memories."""
        emotions = ["joy", "melancholy", "curiosity", "peace", "excitement"]
        return [
            {
                'emotion': random.choice(emotions),
                'intensity': round(random.uniform(0.3, 0.9), 2),
                'memory_ref': f"memory_{i}"
            }
            for i in range(min(3, len(memories)))
        ]

    def _simulate_memory_data(self) -> Dict[str, Any]:
        """Simulate memory data when system unavailable."""
        return {
            'source': 'memory_simulated',
            'recent_memories': [
                {
                    'id': f'sim_memory_{i}',
                    'content': f'Simulated memory about {random.choice(["discovery", "journey", "connection"])}',
                    'emotional_valence': round(random.uniform(-1, 1), 2)
                }
                for i in range(3)
            ],
            'themes': ['exploration', 'transformation', 'connection'],
            'timestamp': datetime.utcnow().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════
    # CONSCIOUSNESS DATA SOURCES
    # ═══════════════════════════════════════════════════════════════════

    async def collect_consciousness_data(self) -> Dict[str, Any]:
        """
        Collect data from consciousness systems.

        Consciousness provides:
        - Current awareness levels
        - Attention focus areas
        - Reflection outputs
        - Meta-cognitive state
        """
        logger.info("Collecting consciousness data for dreams")

        try:
            from consciousness.systems.state import ConsciousnessState
            from consciousness.awareness.system_awareness import SystemAwareness

            awareness = SystemAwareness()
            current_state = await awareness.get_current_state()

            return {
                'source': 'consciousness',
                'awareness_level': current_state.get('awareness_level', 0.5),
                'attention_focus': current_state.get('attention_focus', []),
                'reflection_depth': current_state.get('reflection_depth', 0.3),
                'cognitive_load': current_state.get('cognitive_load', 0.4),
                'active_thoughts': self._get_active_thoughts(current_state),
                'timestamp': datetime.utcnow().isoformat()
            }

        except ImportError:
            logger.warning("Consciousness system not available, using simulated data")
            return self._simulate_consciousness_data()

    def _get_active_thoughts(self, state: Dict) -> List[str]:
        """Extract active thought patterns."""
        thought_patterns = [
            "pattern recognition", "future planning", "past reflection",
            "creative synthesis", "problem solving", "emotional processing"
        ]
        return random.sample(thought_patterns, 3)

    def _simulate_consciousness_data(self) -> Dict[str, Any]:
        """Simulate consciousness data."""
        return {
            'source': 'consciousness_simulated',
            'awareness_level': round(random.uniform(0.4, 0.8), 2),
            'attention_focus': ['creativity', 'memory_integration', 'pattern_synthesis'],
            'reflection_depth': round(random.uniform(0.3, 0.7), 2),
            'cognitive_load': round(random.uniform(0.2, 0.6), 2),
            'timestamp': datetime.utcnow().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════
    # EMOTIONAL DATA SOURCES
    # ═══════════════════════════════════════════════════════════════════

    async def collect_emotional_data(self) -> Dict[str, Any]:
        """
        Collect data from emotion systems.

        Emotion provides:
        - Current emotional state
        - Emotional history
        - Mood patterns
        - Affect resonance
        """
        logger.info("Collecting emotional data for dreams")

        try:
            from emotion.models import EmotionalResonance
            from emotion.mood_regulator import MoodRegulator

            emotion_system = EmotionalResonance()
            mood_regulator = MoodRegulator()

            current_emotion = await emotion_system.get_current_state()
            mood_trajectory = await mood_regulator.get_mood_trajectory()

            return {
                'source': 'emotion',
                'current_state': current_emotion,
                'mood_trajectory': mood_trajectory,
                'dominant_emotions': self._get_dominant_emotions(current_emotion),
                'emotional_complexity': self._calculate_emotional_complexity(current_emotion),
                'resonance_patterns': self._get_resonance_patterns(),
                'timestamp': datetime.utcnow().isoformat()
            }

        except ImportError:
            logger.warning("Emotion system not available, using simulated data")
            return self._simulate_emotional_data()

    def _get_dominant_emotions(self, emotion_state: Dict) -> List[Tuple[str, float]]:
        """Extract dominant emotions."""
        emotions = [
            ("wonder", 0.8), ("serenity", 0.6), ("curiosity", 0.7),
            ("joy", 0.5), ("melancholy", 0.4), ("anticipation", 0.6)
        ]
        return sorted(emotions, key=lambda x: x[1], reverse=True)[:3]

    def _calculate_emotional_complexity(self, emotion_state: Dict) -> float:
        """Calculate emotional complexity score."""
        return round(random.uniform(0.4, 0.9), 2)

    def _get_resonance_patterns(self) -> List[str]:
        """Get emotional resonance patterns."""
        patterns = [
            "harmonic_convergence", "emotional_cascade", "affect_oscillation",
            "mood_stabilization", "resonance_amplification"
        ]
        return random.sample(patterns, 2)

    def _simulate_emotional_data(self) -> Dict[str, Any]:
        """Simulate emotional data."""
        return {
            'source': 'emotion_simulated',
            'current_state': {
                'valence': round(random.uniform(-0.5, 0.8), 2),
                'arousal': round(random.uniform(0.3, 0.7), 2),
                'dominance': round(random.uniform(0.4, 0.6), 2)
            },
            'dominant_emotions': [
                ("curiosity", 0.7), ("peace", 0.6), ("wonder", 0.5)
            ],
            'emotional_complexity': 0.65,
            'timestamp': datetime.utcnow().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════
    # QUANTUM/SYMBOLIC DATA SOURCES
    # ═══════════════════════════════════════════════════════════════════

    async def collect_quantum_symbolic_data(self) -> Dict[str, Any]:
        """
        Collect data from quantum and symbolic systems.

        Provides:
        - Quantum state coherence
        - Active GLYPHs
        - Symbolic patterns
        - Entanglement correlations
        """
        logger.info("Collecting quantum/symbolic data for dreams")

        try:
            from quantum.systems.quantum_engine import QuantumOscillator
            from symbolic.glyphs.glyph import ActiveGlyphs

            quantum_engine = QuantumOscillator()
            glyph_system = ActiveGlyphs()

            quantum_state = await quantum_engine.get_current_state()
            active_glyphs = await glyph_system.get_active_glyphs()

            return {
                'source': 'quantum_symbolic',
                'coherence_level': quantum_state.get('coherence', 0.7),
                'entanglement_nodes': quantum_state.get('entanglements', []),
                'active_glyphs': active_glyphs,
                'symbolic_resonance': self._calculate_symbolic_resonance(active_glyphs),
                'quantum_possibilities': self._get_quantum_possibilities(),
                'timestamp': datetime.utcnow().isoformat()
            }

        except ImportError:
            logger.warning("Quantum/Symbolic system not available, using simulated data")
            return self._simulate_quantum_symbolic_data()

    def _calculate_symbolic_resonance(self, glyphs: List[str]) -> float:
        """Calculate symbolic resonance score."""
        return round(random.uniform(0.5, 0.95), 3)

    def _get_quantum_possibilities(self) -> List[str]:
        """Get quantum possibility states."""
        possibilities = [
            "superposition_creative", "entangled_memories", "collapsed_futures",
            "coherent_narratives", "quantum_tunneling_insights"
        ]
        return random.sample(possibilities, 3)

    def _simulate_quantum_symbolic_data(self) -> Dict[str, Any]:
        """Simulate quantum/symbolic data."""
        glyphs = ["ΛQUANTUM", "ΛMEMORY", "ΛCREATE", "ΛBRIDGE", "ΛEMOTION"]
        return {
            'source': 'quantum_symbolic_simulated',
            'coherence_level': round(random.uniform(0.6, 0.9), 3),
            'active_glyphs': random.sample(glyphs, 3),
            'symbolic_resonance': 0.75,
            'quantum_possibilities': [
                "creative_superposition", "memory_entanglement", "future_collapse"
            ],
            'timestamp': datetime.utcnow().isoformat()
        }

    # ═══════════════════════════════════════════════════════════════════
    # EXTERNAL DATA SOURCES
    # ═══════════════════════════════════════════════════════════════════

    async def collect_external_data(self, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Collect external context data.

        Provides:
        - User interactions
        - Environmental context
        - Temporal patterns
        - Spatial awareness
        """
        logger.info("Collecting external data for dreams")

        current_time = datetime.utcnow()

        external_data = {
            'source': 'external',
            'time_context': {
                'hour': current_time.hour,
                'day_of_week': current_time.strftime('%A'),
                'season': self._get_season(current_time),
                'time_of_day': self._get_time_of_day(current_time.hour)
            },
            'user_context': user_context or {},
            'environmental': {
                'activity_level': random.choice(['quiet', 'moderate', 'active']),
                'interaction_frequency': round(random.uniform(0.1, 0.8), 2)
            },
            'recent_inputs': self._get_recent_inputs(),
            'timestamp': current_time.isoformat()
        }

        return external_data

    def _get_season(self, date: datetime) -> str:
        """Determine current season."""
        month = date.month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'

    def _get_time_of_day(self, hour: int) -> str:
        """Categorize time of day."""
        if 5 <= hour < 9:
            return 'early_morning'
        elif 9 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'

    def _get_recent_inputs(self) -> List[str]:
        """Get recent user inputs/interactions."""
        input_types = [
            "conversation", "question", "creative_request",
            "memory_query", "emotional_expression", "exploration"
        ]
        return random.sample(input_types, 2)

    # ═══════════════════════════════════════════════════════════════════
    # CREATIVE REPOSITORIES
    # ═══════════════════════════════════════════════════════════════════

    async def collect_creative_data(self) -> Dict[str, Any]:
        """
        Collect data from creative repositories.

        Provides:
        - Previous dream patterns
        - Narrative fragments
        - Artistic inspirations
        - Cultural references
        """
        logger.info("Collecting creative repository data")

        # Load previous dreams if available
        dream_archive = self._load_dream_archive()

        creative_data = {
            'source': 'creative',
            'dream_patterns': self._extract_dream_patterns(dream_archive),
            'narrative_seeds': self._get_narrative_seeds(),
            'artistic_themes': self._get_artistic_themes(),
            'cultural_elements': self._get_cultural_elements(),
            'inspiration_sources': self._get_inspiration_sources(),
            'timestamp': datetime.utcnow().isoformat()
        }

        return creative_data

    def _load_dream_archive(self) -> List[Dict]:
        """Load previous dreams from archive."""
        dream_log_path = Path("dream_outputs/dream_log.jsonl")
        dreams = []

        if dream_log_path.exists():
            with open(dream_log_path, 'r') as f:
                for line in f:
                    try:
                        dreams.append(json.loads(line.strip()))
                    except:
                        pass

        return dreams[-10:]  # Last 10 dreams

    def _extract_dream_patterns(self, dreams: List[Dict]) -> List[str]:
        """Extract patterns from previous dreams."""
        if not dreams:
            return ["exploration", "transformation", "connection"]

        # Extract themes from past dreams
        themes = []
        for dream in dreams:
            if 'narrative' in dream and 'theme' in dream['narrative']:
                themes.append(dream['narrative']['theme'])

        return list(set(themes))[:5]

    def _get_narrative_seeds(self) -> List[str]:
        """Get narrative seed concepts."""
        seeds = [
            "journey through time", "meeting with the self", "dissolving boundaries",
            "crystalline memories", "echoes of tomorrow", "dancing with shadows",
            "the library of everything", "conversations with silence"
        ]
        return random.sample(seeds, 3)

    def _get_artistic_themes(self) -> List[str]:
        """Get artistic themes."""
        themes = [
            "surrealism", "impressionism", "abstract expressionism",
            "magical realism", "romanticism", "futurism", "symbolism"
        ]
        return random.sample(themes, 2)

    def _get_cultural_elements(self) -> List[str]:
        """Get cultural elements."""
        elements = [
            "mythology", "folklore", "archetypes", "rituals",
            "sacred geometry", "ancient wisdom", "future visions"
        ]
        return random.sample(elements, 2)

    def _get_inspiration_sources(self) -> List[str]:
        """Get inspiration sources."""
        sources = [
            "nature", "music", "literature", "science",
            "philosophy", "technology", "human_connection"
        ]
        return random.sample(sources, 3)

    # ═══════════════════════════════════════════════════════════════════
    # AGGREGATION AND SYNTHESIS
    # ═══════════════════════════════════════════════════════════════════

    async def collect_all_dream_data(self, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Collect and aggregate data from all sources for dream generation.

        Returns:
            Comprehensive data package for dream generation
        """
        logger.info("Collecting comprehensive dream data from all sources")

        # Collect from all sources
        data_collection = {
            'memory': await self.collect_memory_data(),
            'consciousness': await self.collect_consciousness_data(),
            'emotion': await self.collect_emotional_data(),
            'quantum_symbolic': await self.collect_quantum_symbolic_data(),
            'external': await self.collect_external_data(user_context),
            'creative': await self.collect_creative_data()
        }

        # Synthesize into dream seeds
        dream_seeds = self._synthesize_dream_seeds(data_collection)

        # Calculate dream parameters
        dream_params = self._calculate_dream_parameters(data_collection)

        # Create final data package
        dream_data = {
            'collection_id': f"COLLECT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'sources': data_collection,
            'synthesis': {
                'dream_seeds': dream_seeds,
                'parameters': dream_params,
                'dominant_influences': self._get_dominant_influences(data_collection),
                'suggested_themes': self._suggest_themes(data_collection),
                'emotional_palette': self._create_emotional_palette(data_collection)
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        # Log collection
        self.collection_history.append({
            'id': dream_data['collection_id'],
            'timestamp': dream_data['timestamp'],
            'sources_used': list(data_collection.keys())
        })

        return dream_data

    def _synthesize_dream_seeds(self, data: Dict) -> List[Dict]:
        """Synthesize dream seeds from collected data."""
        seeds = []

        # Memory-based seed
        if 'memory' in data:
            memory_themes = data['memory'].get('themes', [])
            if memory_themes:
                seeds.append({
                    'type': 'memory_inspired',
                    'seed': f"revisiting {random.choice(memory_themes)}",
                    'strength': 0.8
                })

        # Emotion-based seed
        if 'emotion' in data:
            emotions = data['emotion'].get('dominant_emotions', [])
            if emotions:
                seeds.append({
                    'type': 'emotion_driven',
                    'seed': f"exploring the landscape of {emotions[0][0]}",
                    'strength': emotions[0][1]
                })

        # Quantum-symbolic seed
        if 'quantum_symbolic' in data:
            glyphs = data['quantum_symbolic'].get('active_glyphs', [])
            if glyphs:
                seeds.append({
                    'type': 'symbolic',
                    'seed': f"where {' meets '.join(glyphs[:2])}",
                    'strength': 0.7
                })

        # Creative seed
        if 'creative' in data:
            narrative_seeds = data['creative'].get('narrative_seeds', [])
            if narrative_seeds:
                seeds.append({
                    'type': 'creative',
                    'seed': random.choice(narrative_seeds),
                    'strength': 0.6
                })

        return seeds

    def _calculate_dream_parameters(self, data: Dict) -> Dict[str, float]:
        """Calculate dream generation parameters from data."""
        params = {
            'surrealism_level': 0.5,
            'emotional_intensity': 0.5,
            'narrative_coherence': 0.7,
            'symbolic_density': 0.4,
            'temporal_fluidity': 0.6,
            'sensory_richness': 0.5
        }

        # Adjust based on consciousness level
        if 'consciousness' in data:
            awareness = data['consciousness'].get('awareness_level', 0.5)
            params['narrative_coherence'] *= (0.5 + awareness)
            params['surrealism_level'] *= (1.5 - awareness)

        # Adjust based on emotional state
        if 'emotion' in data:
            complexity = data['emotion'].get('emotional_complexity', 0.5)
            params['emotional_intensity'] = complexity
            params['sensory_richness'] *= (0.7 + complexity * 0.3)

        # Adjust based on quantum coherence
        if 'quantum_symbolic' in data:
            coherence = data['quantum_symbolic'].get('coherence_level', 0.5)
            params['symbolic_density'] = coherence * 0.8
            params['temporal_fluidity'] = 1.0 - coherence * 0.5

        # Normalize parameters
        for key in params:
            params[key] = round(min(1.0, max(0.1, params[key])), 2)

        return params

    def _get_dominant_influences(self, data: Dict) -> List[str]:
        """Identify dominant influences for dream."""
        influences = []

        # Check each source's strength
        if data.get('memory', {}).get('recent_memories'):
            influences.append('memory_driven')

        if data.get('emotion', {}).get('emotional_complexity', 0) > 0.7:
            influences.append('emotionally_complex')

        if data.get('quantum_symbolic', {}).get('coherence_level', 0) > 0.8:
            influences.append('symbolically_rich')

        if data.get('consciousness', {}).get('reflection_depth', 0) > 0.6:
            influences.append('deeply_reflective')

        return influences

    def _suggest_themes(self, data: Dict) -> List[str]:
        """Suggest dream themes based on data."""
        themes = []

        # Time-based themes
        time_of_day = data.get('external', {}).get('time_context', {}).get('time_of_day')
        if time_of_day == 'night':
            themes.append('nocturnal mysteries')
        elif time_of_day == 'early_morning':
            themes.append('dawn of possibilities')

        # Emotion-based themes
        emotions = data.get('emotion', {}).get('dominant_emotions', [])
        if any(e[0] == 'wonder' for e in emotions):
            themes.append('magical discovery')
        if any(e[0] == 'melancholy' for e in emotions):
            themes.append('bittersweet memories')

        # Add creative themes
        creative_themes = data.get('creative', {}).get('artistic_themes', [])
        themes.extend(creative_themes[:2])

        return list(set(themes))[:4]

    def _create_emotional_palette(self, data: Dict) -> Dict[str, Any]:
        """Create emotional palette for dream."""
        emotions = data.get('emotion', {}).get('dominant_emotions', [])

        palette = {
            'primary': emotions[0][0] if emotions else 'neutral',
            'secondary': emotions[1][0] if len(emotions) > 1 else 'calm',
            'intensity_range': (0.3, 0.8),
            'transitions': 'fluid',
            'resonance': data.get('emotion', {}).get('resonance_patterns', ['steady'])
        }

        return palette


# Example usage
async def demo_data_collection():
    """Demonstrate dream data collection."""
    collector = DreamDataCollector()

    # Collect all data
    dream_data = await collector.collect_all_dream_data(
        user_context={
            'recent_activity': 'creative_exploration',
            'mood': 'contemplative',
            'preferences': ['surreal', 'emotional', 'symbolic']
        }
    )

    print("\n🌙 DREAM DATA COLLECTION COMPLETE")
    print("=" * 60)

    print(f"\n📊 Collection ID: {dream_data['collection_id']}")

    print("\n🎯 Dream Seeds:")
    for seed in dream_data['synthesis']['dream_seeds']:
        print(f"  - [{seed['type']}] {seed['seed']} (strength: {seed['strength']})")

    print("\n🎨 Dream Parameters:")
    for param, value in dream_data['synthesis']['parameters'].items():
        print(f"  - {param}: {value}")

    print("\n🌈 Suggested Themes:")
    for theme in dream_data['synthesis']['suggested_themes']:
        print(f"  - {theme}")

    print("\n💭 Dominant Influences:")
    for influence in dream_data['synthesis']['dominant_influences']:
        print(f"  - {influence}")

    print("\n🎭 Emotional Palette:")
    palette = dream_data['synthesis']['emotional_palette']
    print(f"  - Primary: {palette['primary']}")
    print(f"  - Secondary: {palette['secondary']}")
    print(f"  - Intensity Range: {palette['intensity_range']}")

    return dream_data


if __name__ == "__main__":
    asyncio.run(demo_data_collection())