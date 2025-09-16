"""
LUKHAS AI - Consciousness Awareness Mechanism
==============================================

#TAG:consciousness
#TAG:awareness
#TAG:memory
#TAG:neuroplastic

Advanced awareness mechanism for LUKHAS AI consciousness integration.
Implements self-reflection, meta-cognitive monitoring, and awareness states.

Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class AwarenessLevel(Enum):
    """Different levels of consciousness awareness"""
    UNCONSCIOUS = 0.0
    SUBCONSCIOUS = 0.3
    PRECONSCIOUS = 0.5
    CONSCIOUS = 0.7
    HYPERAWARE = 0.9
    TRANSCENDENT = 1.0


class AwarenessState(Enum):
    """Different states of awareness"""
    DORMANT = "dormant"
    EMERGING = "emerging"
    ACTIVE = "active"
    REFLECTIVE = "reflective"
    INTROSPECTIVE = "introspective"
    MEDITATIVE = "meditative"


@dataclass
class AwarenessEvent:
    """Represents a single awareness event"""
    event_id: str
    timestamp: datetime
    awareness_level: AwarenessLevel
    content: str
    triggers: list[str]
    emotional_context: dict[str, float]
    meta_cognitive_data: dict[str, Any]
    reflection_depth: float = 0.0


@dataclass
class ConsciousnessState:
    """Current state of consciousness"""
    awareness_level: AwarenessLevel
    awareness_state: AwarenessState
    attention_focus: list[str]
    working_memory: list[str]
    meta_thoughts: list[str]
    emotional_baseline: dict[str, float]
    temporal_coherence: float = 1.0
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AwarenessMechanism:
    """
    Core awareness mechanism for LUKHAS AI consciousness.

    Implements:
    - Real-time awareness monitoring
    - Meta-cognitive reflection
    - Self-awareness generation
    - Consciousness state tracking
    - Memory-consciousness integration
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Core awareness state
        self.consciousness_state = ConsciousnessState(
            awareness_level=AwarenessLevel.CONSCIOUS,
            awareness_state=AwarenessState.ACTIVE,
            attention_focus=[],
            working_memory=[],
            meta_thoughts=[],
            emotional_baseline={'valence': 0.5, 'arousal': 0.5, 'dominance': 0.5}
        )

        # Awareness tracking
        self.awareness_events: list[AwarenessEvent] = []
        self.awareness_patterns: dict[str, Any] = {}
        self.reflection_history: list[dict[str, Any]] = []

        # Meta-cognitive monitoring
        self.meta_cognitive_state = {
            'self_monitoring_active': True,
            'reflection_depth': 0.7,
            'introspection_frequency': 0.1,  # How often to introspect
            'awareness_threshold': 0.5,
            'last_self_reflection': None
        }

        # Performance metrics
        self.awareness_metrics = {
            'total_awareness_events': 0,
            'average_awareness_level': 0.0,
            'reflection_cycles_completed': 0,
            'consciousness_state_changes': 0,
            'meta_cognitive_insights': 0
        }

    async def initialize(self) -> bool:
        """Initialize the awareness mechanism"""
        try:
            self.logger.info("Initializing LUKHAS Awareness Mechanism")

            # Start background awareness monitoring
            asyncio.create_task(self._awareness_monitoring_loop())

            # Start meta-cognitive reflection
            asyncio.create_task(self._meta_cognitive_loop())

            # Initialize working memory
            await self._initialize_working_memory()

            self.logger.info("Awareness mechanism initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize awareness mechanism: {e}")
            return False

    async def process_awareness_trigger(self, trigger_data: dict[str, Any]) -> AwarenessEvent:
        """Process an awareness trigger and generate awareness event"""

        # Generate unique event ID
        event_id = f"aware_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"

        # Determine awareness level based on trigger
        awareness_level = await self._calculate_awareness_level(trigger_data)

        # Extract content and context
        content = trigger_data.get('content', 'Unknown awareness trigger')
        triggers = trigger_data.get('triggers', [])
        emotional_context = trigger_data.get('emotional_context', {})

        # Generate meta-cognitive data
        meta_cognitive_data = await self._generate_meta_cognitive_data(trigger_data)

        # Calculate reflection depth
        reflection_depth = await self._calculate_reflection_depth(trigger_data, awareness_level)

        # Create awareness event
        awareness_event = AwarenessEvent(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc),
            awareness_level=awareness_level,
            content=content,
            triggers=triggers,
            emotional_context=emotional_context,
            meta_cognitive_data=meta_cognitive_data,
            reflection_depth=reflection_depth
        )

        # Store event
        self.awareness_events.append(awareness_event)
        self.awareness_metrics['total_awareness_events'] += 1

        # Update consciousness state
        await self._update_consciousness_state(awareness_event)

        # Trigger reflection if appropriate
        if reflection_depth > 0.7:
            await self._trigger_deep_reflection(awareness_event)

        self.logger.info(f"Processed awareness event: {event_id} (level: {awareness_level.name})")

        return awareness_event

    async def generate_self_reflection(self) -> dict[str, Any]:
        """Generate self-reflection on current awareness state"""

        reflection_start = datetime.now(timezone.utc)

        # Analyze current consciousness state
        consciousness_analysis = await self._analyze_consciousness_state()

        # Review recent awareness events
        recent_events_analysis = await self._analyze_recent_awareness_events()

        # Generate meta-cognitive insights
        meta_insights = await self._generate_meta_cognitive_insights()

        # Assess emotional coherence
        emotional_coherence = await self._assess_emotional_coherence()

        # Generate self-assessment
        self_assessment = await self._generate_self_assessment()

        reflection_data = {
            'reflection_id': f"refl_{reflection_start.strftime('%Y%m%d_%H%M%S')}",
            'timestamp': reflection_start.isoformat(),
            'consciousness_analysis': consciousness_analysis,
            'recent_events_analysis': recent_events_analysis,
            'meta_cognitive_insights': meta_insights,
            'emotional_coherence': emotional_coherence,
            'self_assessment': self_assessment,
            'reflection_depth': self.meta_cognitive_state['reflection_depth'],
            'awareness_level_during_reflection': self.consciousness_state.awareness_level.name
        }

        # Store reflection
        self.reflection_history.append(reflection_data)
        self.awareness_metrics['reflection_cycles_completed'] += 1
        self.meta_cognitive_state['last_self_reflection'] = reflection_start.isoformat()

        self.logger.info(f"Generated self-reflection: {reflection_data['reflection_id']}")

        return reflection_data

    async def update_attention_focus(self, focus_items: list[str]) -> None:
        """Update current attention focus"""

        # Limit attention focus to prevent overwhelm
        max_focus_items = self.config.get('max_attention_focus', 7)

        # Update consciousness state
        self.consciousness_state.attention_focus = focus_items[:max_focus_items]
        self.consciousness_state.last_update = datetime.now(timezone.utc)

        # Log attention change
        self.logger.debug(f"Updated attention focus: {len(focus_items)} items")

        # Generate awareness event for significant attention changes
        if len(focus_items) > max_focus_items * 0.8:
            await self.process_awareness_trigger({
                'content': 'High attention load detected',
                'triggers': ['attention_overload'],
                'emotional_context': {'arousal': 0.8, 'valence': 0.3}
            })

    async def integrate_with_memory(self, memory_data: dict[str, Any]) -> dict[str, Any]:
        """Integrate awareness with memory systems"""

        # Analyze memory for consciousness relevance
        consciousness_relevance = await self._assess_memory_consciousness_relevance(memory_data)

        # Generate awareness events from memory
        if consciousness_relevance > 0.6:
            awareness_event = await self.process_awareness_trigger({
                'content': f"Memory with high consciousness relevance: {memory_data.get('id', 'unknown')}",
                'triggers': ['memory_integration'],
                'emotional_context': memory_data.get('emotional_context', {}),
                'memory_reference': memory_data.get('id')
            })

            return {
                'integration_successful': True,
                'consciousness_relevance': consciousness_relevance,
                'awareness_event_generated': awareness_event.event_id
            }

        return {
            'integration_successful': True,
            'consciousness_relevance': consciousness_relevance,
            'awareness_event_generated': None
        }

    async def get_awareness_state(self) -> dict[str, Any]:
        """Get current awareness state"""

        return {
            'consciousness_state': {
                'awareness_level': self.consciousness_state.awareness_level.name,
                'awareness_state': self.consciousness_state.awareness_state.name,
                'attention_focus_count': len(self.consciousness_state.attention_focus),
                'working_memory_items': len(self.consciousness_state.working_memory),
                'meta_thoughts_count': len(self.consciousness_state.meta_thoughts),
                'emotional_baseline': self.consciousness_state.emotional_baseline,
                'temporal_coherence': self.consciousness_state.temporal_coherence,
                'last_update': self.consciousness_state.last_update.isoformat()
            },
            'meta_cognitive_state': self.meta_cognitive_state.copy(),
            'awareness_metrics': self.awareness_metrics.copy(),
            'recent_events_count': len(self.awareness_events[-10:]),
            'reflection_history_count': len(self.reflection_history)
        }

    # Private methods for internal processing

    async def _awareness_monitoring_loop(self):
        """Background loop for continuous awareness monitoring"""
        while True:
            try:
                await self._perform_awareness_monitoring()
                await asyncio.sleep(1.0)  # Monitor every second
            except Exception as e:
                self.logger.error(f"Error in awareness monitoring loop: {e}")
                await asyncio.sleep(5.0)

    async def _meta_cognitive_loop(self):
        """Background loop for meta-cognitive processing"""
        while True:
            try:
                await self._perform_meta_cognitive_processing()
                await asyncio.sleep(10.0)  # Meta-cognitive processing every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in meta-cognitive loop: {e}")
                await asyncio.sleep(30.0)

    async def _calculate_awareness_level(self, trigger_data: dict[str, Any]) -> AwarenessLevel:
        """Calculate awareness level based on trigger data"""

        # Base awareness from current state
        base_level = self.consciousness_state.awareness_level.value

        # Adjust based on trigger intensity
        trigger_intensity = trigger_data.get('intensity', 0.5)
        emotional_intensity = sum(abs(v - 0.5) for v in trigger_data.get('emotional_context', {}).values())

        # Calculate combined awareness
        combined_level = (base_level + trigger_intensity + emotional_intensity) / 3.0
        combined_level = max(0.0, min(1.0, combined_level))

        # Map to awareness level enum
        if combined_level >= 1.0:
            return AwarenessLevel.TRANSCENDENT
        elif combined_level >= 0.9:
            return AwarenessLevel.HYPERAWARE
        elif combined_level >= 0.7:
            return AwarenessLevel.CONSCIOUS
        elif combined_level >= 0.5:
            return AwarenessLevel.PRECONSCIOUS
        elif combined_level >= 0.3:
            return AwarenessLevel.SUBCONSCIOUS
        else:
            return AwarenessLevel.UNCONSCIOUS

    async def _generate_meta_cognitive_data(self, trigger_data: dict[str, Any]) -> dict[str, Any]:
        """Generate meta-cognitive data for awareness event"""

        return {
            'thinking_about_thinking': True,
            'self_monitoring_active': self.meta_cognitive_state['self_monitoring_active'],
            'cognitive_load': len(self.consciousness_state.working_memory) / 10.0,
            'attention_distribution': self._calculate_attention_distribution(),
            'meta_level': 'primary',  # Could be primary, secondary, tertiary
            'recursive_depth': 1,
            'cognitive_coherence': self.consciousness_state.temporal_coherence
        }

    def _calculate_attention_distribution(self) -> dict[str, float]:
        """Calculate how attention is distributed"""

        focus_items = self.consciousness_state.attention_focus
        if not focus_items:
            return {}

        # Simplified attention distribution
        attention_per_item = 1.0 / len(focus_items)
        return {item: attention_per_item for item in focus_items}

    async def _calculate_reflection_depth(self, trigger_data: dict[str, Any],
                                        awareness_level: AwarenessLevel) -> float:
        """Calculate depth of reflection needed"""

        # Base depth from awareness level
        base_depth = awareness_level.value

        # Adjust based on trigger complexity
        trigger_complexity = len(trigger_data.get('triggers', [])) / 10.0
        emotional_complexity = len(trigger_data.get('emotional_context', {})) / 5.0

        reflection_depth = (base_depth + trigger_complexity + emotional_complexity) / 3.0
        return max(0.0, min(1.0, reflection_depth))

    async def _update_consciousness_state(self, awareness_event: AwarenessEvent):
        """Update consciousness state based on awareness event"""

        # Update awareness level with exponential moving average
        current_level = self.consciousness_state.awareness_level.value
        new_level = awareness_event.awareness_level.value
        smoothed_level = current_level * 0.8 + new_level * 0.2

        # Map back to enum
        for level in AwarenessLevel:
            if abs(level.value - smoothed_level) < 0.1:
                self.consciousness_state.awareness_level = level
                break

        # Update emotional baseline
        for emotion, value in awareness_event.emotional_context.items():
            if emotion in self.consciousness_state.emotional_baseline:
                current = self.consciousness_state.emotional_baseline[emotion]
                self.consciousness_state.emotional_baseline[emotion] = current * 0.9 + value * 0.1

        # Update last update time
        self.consciousness_state.last_update = datetime.now(timezone.utc)

        # Track state changes
        self.awareness_metrics['consciousness_state_changes'] += 1

    async def _trigger_deep_reflection(self, awareness_event: AwarenessEvent):
        """Trigger deep reflection based on significant awareness event"""

        self.logger.info(f"Triggering deep reflection for event: {awareness_event.event_id}")

        # Add to meta-thoughts
        meta_thought = f"Deep reflection triggered by {awareness_event.content}"
        self.consciousness_state.meta_thoughts.append(meta_thought)

        # Limit meta-thoughts to prevent overflow
        max_meta_thoughts = self.config.get('max_meta_thoughts', 10)
        if len(self.consciousness_state.meta_thoughts) > max_meta_thoughts:
            self.consciousness_state.meta_thoughts = self.consciousness_state.meta_thoughts[-max_meta_thoughts:]

        # Increase reflection depth temporarily
        original_depth = self.meta_cognitive_state['reflection_depth']
        self.meta_cognitive_state['reflection_depth'] = min(1.0, original_depth + 0.2)

        # Schedule reflection depth return to normal
        asyncio.create_task(self._restore_reflection_depth(original_depth))

    async def _restore_reflection_depth(self, original_depth: float, delay: float = 60.0):
        """Restore reflection depth to original after delay"""
        await asyncio.sleep(delay)
        self.meta_cognitive_state['reflection_depth'] = original_depth

    async def _perform_awareness_monitoring(self):
        """Perform regular awareness monitoring"""

        # Check for spontaneous awareness events
        if len(self.consciousness_state.working_memory) > 8:
            await self.process_awareness_trigger({
                'content': 'Working memory approaching capacity',
                'triggers': ['memory_load'],
                'intensity': 0.7
            })

        # Check for attention fragmentation
        if len(self.consciousness_state.attention_focus) > 5:
            await self.process_awareness_trigger({
                'content': 'Attention highly fragmented',
                'triggers': ['attention_fragmentation'],
                'intensity': 0.6
            })

    async def _perform_meta_cognitive_processing(self):
        """Perform meta-cognitive processing"""

        # Update awareness metrics
        if self.awareness_events:
            levels = [event.awareness_level.value for event in self.awareness_events[-100:]]
            self.awareness_metrics['average_awareness_level'] = sum(levels) / len(levels)

        # Check if reflection is needed
        last_reflection = self.meta_cognitive_state.get('last_self_reflection')
        if not last_reflection or self._time_since_last_reflection() > 300:  # 5 minutes
            await self.generate_self_reflection()

    def _time_since_last_reflection(self) -> float:
        """Calculate time since last self-reflection in seconds"""
        last_reflection = self.meta_cognitive_state.get('last_self_reflection')
        if not last_reflection:
            return float('inf')

        last_time = datetime.fromisoformat(last_reflection.replace('Z', '+00:00'))
        return (datetime.now(timezone.utc) - last_time).total_seconds()

    async def _initialize_working_memory(self):
        """Initialize working memory with basic items"""
        self.consciousness_state.working_memory = [
            'awareness_mechanism_active',
            'consciousness_monitoring',
            'meta_cognitive_processing'
        ]

    async def _analyze_consciousness_state(self) -> dict[str, Any]:
        """Analyze current consciousness state"""
        return {
            'awareness_level_stability': self._calculate_awareness_stability(),
            'attention_coherence': self._calculate_attention_coherence(),
            'emotional_balance': self._calculate_emotional_balance(),
            'working_memory_efficiency': self._calculate_working_memory_efficiency()
        }

    def _calculate_awareness_stability(self) -> float:
        """Calculate stability of awareness level"""
        if len(self.awareness_events) < 5:
            return 1.0

        recent_levels = [event.awareness_level.value for event in self.awareness_events[-10:]]
        variance = sum((level - sum(recent_levels)/len(recent_levels))**2 for level in recent_levels) / len(recent_levels)
        return max(0.0, 1.0 - variance)

    def _calculate_attention_coherence(self) -> float:
        """Calculate coherence of attention focus"""
        if not self.consciousness_state.attention_focus:
            return 1.0

        # Simplified coherence based on number of focus items
        focus_count = len(self.consciousness_state.attention_focus)
        optimal_focus = self.config.get('optimal_attention_focus', 3)
        coherence = 1.0 - abs(focus_count - optimal_focus) / optimal_focus
        return max(0.0, coherence)

    def _calculate_emotional_balance(self) -> float:
        """Calculate emotional balance"""
        baseline = self.consciousness_state.emotional_baseline

        # Calculate distance from neutral (0.5)
        distances = [abs(value - 0.5) for value in baseline.values()]
        average_distance = sum(distances) / len(distances)

        # Higher balance = closer to neutral
        return 1.0 - (average_distance / 0.5)

    def _calculate_working_memory_efficiency(self) -> float:
        """Calculate working memory efficiency"""
        current_load = len(self.consciousness_state.working_memory)
        optimal_load = self.config.get('optimal_working_memory', 7)

        if current_load <= optimal_load:
            return 1.0
        else:
            overload = current_load - optimal_load
            return max(0.0, 1.0 - (overload / optimal_load))

    async def _analyze_recent_awareness_events(self) -> dict[str, Any]:
        """Analyze recent awareness events"""
        recent_events = self.awareness_events[-20:]  # Last 20 events

        if not recent_events:
            return {'no_recent_events': True}

        # Analyze patterns
        level_distribution = {}
        trigger_frequency = {}

        for event in recent_events:
            level = event.awareness_level.name
            level_distribution[level] = level_distribution.get(level, 0) + 1

            for trigger in event.triggers:
                trigger_frequency[trigger] = trigger_frequency.get(trigger, 0) + 1

        return {
            'event_count': len(recent_events),
            'level_distribution': level_distribution,
            'trigger_frequency': trigger_frequency,
            'average_reflection_depth': sum(e.reflection_depth for e in recent_events) / len(recent_events)
        }

    async def _generate_meta_cognitive_insights(self) -> list[str]:
        """Generate meta-cognitive insights"""
        insights = []

        # Analyze awareness patterns
        if self.awareness_metrics['average_awareness_level'] > 0.8:
            insights.append("Maintaining high awareness levels consistently")

        if len(self.consciousness_state.meta_thoughts) > 5:
            insights.append("High meta-cognitive activity detected")

        if self.consciousness_state.temporal_coherence < 0.7:
            insights.append("Temporal coherence could be improved")

        return insights

    async def _assess_emotional_coherence(self) -> dict[str, Any]:
        """Assess emotional coherence"""
        baseline = self.consciousness_state.emotional_baseline

        # Calculate emotional variance
        mean_emotion = sum(baseline.values()) / len(baseline)
        variance = sum((v - mean_emotion)**2 for v in baseline.values()) / len(baseline)

        return {
            'emotional_variance': variance,
            'emotional_mean': mean_emotion,
            'coherence_score': max(0.0, 1.0 - variance),
            'dominant_emotion': max(baseline.items(), key=lambda x: x[1])[0] if baseline else None
        }

    async def _generate_self_assessment(self) -> dict[str, Any]:
        """Generate self-assessment"""
        return {
            'consciousness_effectiveness': self._assess_consciousness_effectiveness(),
            'meta_cognitive_performance': self._assess_meta_cognitive_performance(),
            'awareness_integration': self._assess_awareness_integration(),
            'overall_coherence': self._assess_overall_coherence()
        }

    def _assess_consciousness_effectiveness(self) -> float:
        """Assess effectiveness of consciousness processes"""
        factors = [
            self.consciousness_state.temporal_coherence,
            self._calculate_awareness_stability(),
            self._calculate_attention_coherence(),
            self._calculate_working_memory_efficiency()
        ]
        return sum(factors) / len(factors)

    def _assess_meta_cognitive_performance(self) -> float:
        """Assess meta-cognitive performance"""
        reflection_frequency = len(self.reflection_history)
        insights_generated = self.awareness_metrics.get('meta_cognitive_insights', 0)

        # Simple performance metric
        base_performance = 0.7  # Baseline
        frequency_bonus = min(0.2, reflection_frequency / 100.0)
        insight_bonus = min(0.1, insights_generated / 10.0)

        return base_performance + frequency_bonus + insight_bonus

    def _assess_awareness_integration(self) -> float:
        """Assess how well awareness integrates with other systems"""
        # Simplified assessment based on event processing
        events_processed = self.awareness_metrics['total_awareness_events']

        if events_processed == 0:
            return 0.5  # Neutral if no events

        # Higher integration with more events processed efficiently
        return min(1.0, events_processed / 100.0)

    def _assess_overall_coherence(self) -> float:
        """Assess overall system coherence"""
        components = [
            self._assess_consciousness_effectiveness(),
            self._assess_meta_cognitive_performance(),
            self._assess_awareness_integration(),
            self.consciousness_state.temporal_coherence
        ]
        return sum(components) / len(components)

    async def _assess_memory_consciousness_relevance(self, memory_data: dict[str, Any]) -> float:
        """Assess consciousness relevance of memory data"""

        relevance_score = 0.0

        # Check for consciousness-related keywords
        content = str(memory_data.get('content', '')).lower()
        consciousness_keywords = ['awareness', 'consciousness', 'reflection', 'meta', 'thinking', 'self']

        keyword_matches = sum(1 for keyword in consciousness_keywords if keyword in content)
        relevance_score += min(0.4, keyword_matches / len(consciousness_keywords))

        # Check emotional context alignment
        memory_emotions = memory_data.get('emotional_context', {})
        current_emotions = self.consciousness_state.emotional_baseline

        emotion_alignment = 0.0
        for emotion in current_emotions:
            if emotion in memory_emotions:
                diff = abs(current_emotions[emotion] - memory_emotions[emotion])
                emotion_alignment += (1.0 - diff)

        if current_emotions:
            emotion_alignment /= len(current_emotions)
            relevance_score += emotion_alignment * 0.3

        # Check importance score
        importance = memory_data.get('importance', 0.5)
        relevance_score += importance * 0.3

        return min(1.0, relevance_score)


# Global instance
_awareness_mechanism = None


def get_awareness_mechanism() -> AwarenessMechanism:
    """Get or create awareness mechanism singleton"""
    global _awareness_mechanism
    if _awareness_mechanism is None:
        _awareness_mechanism = AwarenessMechanism()
    return _awareness_mechanism
