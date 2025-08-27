#!/usr/bin/env python3
"""
Trigger Flow Example
===================
Demonstrates how the monitoring system triggers adaptations from real LUKHAS data
"""

import asyncio
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any

from bio.endocrine_integration import EndocrineIntegration

# Import LUKHAS modules to demonstrate data integration
from lukhas.consciousness.unified.auto_consciousness import AutoConsciousness
from lukhas.emotion.service import EmotionService
from lukhas.memory.memoria import Memoria

# Import our monitoring system
from lukhas.monitoring import (
    MonitoringProfile,
    PlasticityTriggerType,
    start_complete_monitoring_system,
)
from lukhas.orchestration.signals.signal_bus import SignalBus
from reasoning.causal.causal_inference import CausalInferenceEngine


class LukhasDataFeeder:
    """
    Feeds real data from all LUKHAS  modules into the monitoring system.
    This shows how the monitoring system gets triggered by actual system state.
    """

    def __init__(self, monitoring_system):
        self.monitoring_system = monitoring_system
        self.data_sources = {}
        self.last_trigger_times = {}

    async def initialize_data_sources(self):
        """Initialize connections to all LUKHAS  modules"""

        print("🔌 Connecting to LUKHAS  modules...")

        try:
            # Connect to consciousness system
            self.data_sources["consciousness"] = AutoConsciousness()
            await self.data_sources["consciousness"].initialize()

            # Connect to memory system
            self.data_sources["memory"] = Memoria()
            await self.data_sources["memory"].initialize()

            # Connect to emotion service
            self.data_sources["emotion"] = EmotionService()
            await self.data_sources["emotion"].initialize()

            # Connect to reasoning system
            self.data_sources["reasoning"] = CausalInferenceEngine()
            await self.data_sources["reasoning"].initialize()

            # Connect to biological systems
            self.data_sources["endocrine"] = EndocrineIntegration()
            await self.data_sources["endocrine"].initialize()

            print("✅ Connected to all LUKHAS  data sources")

        except Exception as e:
            print(f"⚠️ Some modules unavailable: {e}")
            print("🔧 Creating mock data sources for demonstration...")
            await self._create_mock_data_sources()

    async def _create_mock_data_sources(self):
        """Create mock data sources that simulate real LUKHAS  data"""

        class MockConsciousness:
            async def get_awareness_level(self):
                return 0.75 + (time.time() % 10) * 0.02

            async def get_attention_targets(self):
                return ["user_interaction", "system_optimization"]

            async def get_decision_confidence(self):
                return 0.6 + (time.time() % 15) * 0.03

        class MockMemory:
            async def get_memory_load(self):
                return 0.4 + (time.time() % 20) * 0.01

            async def get_consolidation_rate(self):
                return 0.7 + (time.time() % 8) * 0.025

            async def get_recent_activity(self):
                return 15 + int(time.time() % 30)

        class MockEmotion:
            async def get_emotional_state(self):
                # Simulate emotional fluctuations
                base_time = time.time()
                return {
                    "valence": 0.6 + 0.2 * (base_time % 12) / 12,
                    "arousal": 0.5 + 0.3 * (base_time % 8) / 8,
                    "dominance": 0.7 + 0.2 * (base_time % 15) / 15,
                }

        class MockReasoning:
            async def get_processing_depth(self):
                return 0.8 + (time.time() % 25) * 0.008

            async def get_inference_rate(self):
                return 12 + int(time.time() % 18)

            async def get_logical_coherence(self):
                return 0.85 + (time.time() % 7) * 0.02

        class MockEndocrine:
            async def get_hormone_profile(self):
                # Simulate biological hormone fluctuations
                t = time.time()
                stress_cycle = (t % 300) / 300  # 5-minute stress cycle
                energy_cycle = (t % 120) / 120  # 2-minute energy cycle

                return {
                    "cortisol": 0.3 + stress_cycle * 0.5,  # Stress hormone
                    "dopamine": 0.5 + energy_cycle * 0.3,  # Motivation
                    "serotonin": 0.6 + 0.2 * ((t % 180) / 180),  # Mood
                    "oxytocin": 0.4 + 0.2 * ((t % 90) / 90),  # Social
                    "adrenaline": 0.2 + stress_cycle * 0.6,  # Alert state
                    "melatonin": 0.8 - 0.6 * ((t % 240) / 240),  # Rest cycle
                    "gaba": 0.7 - stress_cycle * 0.3,  # Calm
                    "endorphin": 0.5 + 0.3 * ((t % 150) / 150),  # Well-being
                }

            async def get_homeostasis_state(self):
                # Determine state based on hormone levels
                hormones = await self.get_hormone_profile()
                stress_level = (hormones["cortisol"] + hormones["adrenaline"]) / 2

                if stress_level > 0.8:
                    return "critical"
                elif stress_level > 0.6:
                    return "stressed"
                elif stress_level > 0.4:
                    return "balanced"
                else:
                    return "recovering"

        # Assign mock data sources
        self.data_sources = {
            "consciousness": MockConsciousness(),
            "memory": MockMemory(),
            "emotion": MockEmotion(),
            "reasoning": MockReasoning(),
            "endocrine": MockEndocrine(),
        }

        print("🎭 Mock data sources created - simulating real LUKHAS  behavior")

    async def feed_continuous_data(self):
        """Continuously feed data from lukhas_modules to monitoring system"""

        print("📊 Starting continuous data feed to monitoring system...")

        while True:
            try:
                # Collect comprehensive system state
                system_state = await self._collect_comprehensive_state()

                # Feed to monitoring system components
                await self._feed_to_monitoring_components(system_state)

                # Check for trigger conditions
                triggers_fired = await self._check_trigger_conditions(system_state)

                if triggers_fired:
                    print(
                        f"🔥 {len(triggers_fired)} triggers fired: {[t.name for t in triggers_fired]}"
                    )

                await asyncio.sleep(2.0)  # Feed data every 2 seconds

            except Exception as e:
                print(f"❌ Error in data feed: {e}")
                await asyncio.sleep(5.0)

    async def _collect_comprehensive_state(self) -> dict[str, Any]:
        """Collect comprehensive state from all LUKHAS  modules"""

        # Consciousness data
        consciousness_data = {
            "awareness_level": await self.data_sources[
                "consciousness"
            ].get_awareness_level(),
            "attention_targets": await self.data_sources[
                "consciousness"
            ].get_attention_targets(),
            "decision_confidence": await self.data_sources[
                "consciousness"
            ].get_decision_confidence(),
        }

        # Memory data
        memory_data = {
            "memory_load": await self.data_sources["memory"].get_memory_load(),
            "consolidation_rate": await self.data_sources[
                "memory"
            ].get_consolidation_rate(),
            "recent_activity": await self.data_sources["memory"].get_recent_activity(),
        }

        # Emotional data
        emotion_data = await self.data_sources["emotion"].get_emotional_state()

        # Reasoning data
        reasoning_data = {
            "processing_depth": await self.data_sources[
                "reasoning"
            ].get_processing_depth(),
            "inference_rate": await self.data_sources["reasoning"].get_inference_rate(),
            "logical_coherence": await self.data_sources[
                "reasoning"
            ].get_logical_coherence(),
        }

        # Endocrine/biological data
        biological_data = {
            "hormone_profile": await self.data_sources[
                "endocrine"
            ].get_hormone_profile(),
            "homeostasis_state": await self.data_sources[
                "endocrine"
            ].get_homeostasis_state(),
        }

        # Calculate derived metrics
        derived_metrics = await self._calculate_derived_metrics(
            consciousness_data,
            memory_data,
            emotion_data,
            reasoning_data,
            biological_data,
        )

        return {
            "timestamp": datetime.now(timezone.utc),
            "consciousness": consciousness_data,
            "memory": memory_data,
            "emotion": emotion_data,
            "reasoning": reasoning_data,
            "biological": biological_data,
            "derived": derived_metrics,
        }

    async def _calculate_derived_metrics(
        self, consciousness, memory, emotion, reasoning, biological
    ) -> dict[str, float]:
        """Calculate derived metrics that combine data from multiple modules"""

        # Stress indicator (combines biological and cognitive signals)
        stress_indicator = (
            biological["hormone_profile"]["cortisol"] * 0.4
            + biological["hormone_profile"]["adrenaline"] * 0.3
            + (1.0 - emotion["valence"]) * 0.2
            + (consciousness["awareness_level"] - 0.5)
            * 0.1  # High awareness can indicate stress
        )

        # Performance indicator (integrates cognitive functions)
        performance_indicator = (
            consciousness["decision_confidence"] * 0.3
            + reasoning["logical_coherence"] * 0.3
            + (1.0 - memory["memory_load"]) * 0.2  # Lower load = better performance
            + biological["hormone_profile"]["dopamine"] * 0.2
        )

        # Learning readiness (biological + cognitive factors)
        learning_readiness = (
            biological["hormone_profile"]["dopamine"] * 0.4
            + memory["consolidation_rate"] * 0.3
            + consciousness["awareness_level"] * 0.2
            + emotion["arousal"] * 0.1
        )

        # Social engagement potential
        social_engagement = (
            biological["hormone_profile"]["oxytocin"] * 0.5
            + emotion["valence"] * 0.3
            + consciousness["decision_confidence"] * 0.2
        )

        # Recovery need indicator
        recovery_need = (
            stress_indicator * 0.4
            + memory["memory_load"] * 0.3
            + (1.0 - biological["hormone_profile"]["gaba"]) * 0.3
        )

        return {
            "stress_indicator": max(0.0, min(1.0, stress_indicator)),
            "performance_indicator": max(0.0, min(1.0, performance_indicator)),
            "learning_readiness": max(0.0, min(1.0, learning_readiness)),
            "social_engagement": max(0.0, min(1.0, social_engagement)),
            "recovery_need": max(0.0, min(1.0, recovery_need)),
            "cpu_utilization": 0.3 + stress_indicator * 0.4,  # Simulated system load
            "response_time": 0.1 + (1.0 - performance_indicator) * 0.3,
            "emotional_coherence": emotion["valence"] * 0.7
            + (1.0 - abs(emotion["arousal"] - 0.5) * 2) * 0.3,
        }

    async def _feed_to_monitoring_components(self, system_state: dict[str, Any]):
        """Feed collected data to monitoring system components"""

        # Feed to endocrine engine
        if self.monitoring_system.endocrine_engine:
            # Update hormone levels directly
            await self._update_endocrine_engine(system_state)

        # Feed to metrics collector
        if self.monitoring_system.metrics_collector:
            # Update current metrics
            await self._update_metrics_collector(system_state)

        # Feed to coherence monitor
        if self.monitoring_system.coherence_monitor:
            # Update bio-symbolic state
            await self._update_coherence_monitor(system_state)

    async def _update_endocrine_engine(self, system_state: dict[str, Any]):
        """Update endocrine engine with biological data"""

        # The endocrine engine will automatically capture this data
        # through its monitoring loop, but we can also feed it directly
        biological = system_state["biological"]

        # Mock endocrine system update
        if hasattr(self.monitoring_system.endocrine_engine, "endocrine_system"):
            if hasattr(
                self.monitoring_system.endocrine_engine.endocrine_system,
                "_hormone_levels",
            ):
                self.monitoring_system.endocrine_engine.endocrine_system._hormone_levels = biological[
                    "hormone_profile"
                ]

    async def _update_metrics_collector(self, system_state: dict[str, Any]):
        """Update metrics collector with derived metrics"""

        if self.monitoring_system.metrics_collector:
            # Update endocrine state
            from monitoring.endocrine_observability_engine import EndocrineSnapshot

            snapshot = EndocrineSnapshot(
                hormone_levels=system_state["biological"]["hormone_profile"],
                homeostasis_state=system_state["biological"]["homeostasis_state"],
                system_metrics=system_state["derived"],
                coherence_score=system_state["derived"]["performance_indicator"],
            )

            self.monitoring_system.metrics_collector.update_endocrine_state(snapshot)

    async def _update_coherence_monitor(self, system_state: dict[str, Any]):
        """Update coherence monitor with bio-symbolic data"""

        if self.monitoring_system.coherence_monitor:
            # Update biological system state
            from monitoring.endocrine_observability_engine import EndocrineSnapshot

            bio_snapshot = EndocrineSnapshot(
                hormone_levels=system_state["biological"]["hormone_profile"],
                homeostasis_state=system_state["biological"]["homeostasis_state"],
                system_metrics=system_state["derived"],
                coherence_score=system_state["derived"]["performance_indicator"],
            )

            await self.monitoring_system.coherence_monitor.update_bio_system_state(
                bio_snapshot
            )

            # Update symbolic system state
            symbolic_data = {
                "glyph_processing_rate": system_state["derived"][
                    "performance_indicator"
                ],
                "consciousness_level": system_state["consciousness"]["awareness_level"],
                "decision_making_active": system_state["consciousness"][
                    "decision_confidence"
                ]
                > 0.7,
                "memory_operations": system_state["memory"]["recent_activity"],
                "reasoning_depth": system_state["reasoning"]["processing_depth"],
                "symbolic_complexity": system_state["reasoning"]["logical_coherence"],
                "processing_load": system_state["derived"]["cpu_utilization"],
            }

            await self.monitoring_system.coherence_monitor.update_symbolic_system_state(
                symbolic_data
            )

    async def _check_trigger_conditions(
        self, system_state: dict[str, Any]
    ) -> list[PlasticityTriggerType]:
        """Check if any trigger conditions are met"""

        triggers_fired = []
        current_time = datetime.now(timezone.utc)

        # Get current values
        biological = system_state["biological"]
        derived = system_state["derived"]
        hormones = biological["hormone_profile"]

        # **THRESHOLD CALCULATIONS** - This is where the magic happens!

        # 1. STRESS ADAPTATION TRIGGER
        # Combines cortisol, adrenaline, and derived stress indicator
        stress_level = (
            hormones["cortisol"] * 0.4
            + hormones["adrenaline"] * 0.3
            + derived["stress_indicator"] * 0.3
        )
        stress_threshold = self._calculate_adaptive_threshold(
            "stress", stress_level, 0.7
        )  # Base threshold 0.7

        if stress_level > stress_threshold and self._check_cooldown(
            "stress_adaptation", current_time
        ):
            triggers_fired.append(PlasticityTriggerType.STRESS_ADAPTATION)
            self.last_trigger_times["stress_adaptation"] = current_time
            print(
                f"🚨 STRESS TRIGGER: level={stress_level:.3f}, threshold={stress_threshold:.3f}"
            )

        # 2. PERFORMANCE OPTIMIZATION TRIGGER
        # Based on low performance and dopamine
        performance_level = derived["performance_indicator"]
        performance_threshold = self._calculate_adaptive_threshold(
            "performance", performance_level, 0.4, inverted=True
        )  # Low performance triggers

        if performance_level < performance_threshold and self._check_cooldown(
            "performance_optimization", current_time
        ):
            triggers_fired.append(PlasticityTriggerType.PERFORMANCE_OPTIMIZATION)
            self.last_trigger_times["performance_optimization"] = current_time
            print(
                f"📉 PERFORMANCE TRIGGER: level={performance_level:.3f}, threshold={performance_threshold:.3f}"
            )

        # 3. SOCIAL ENHANCEMENT TRIGGER
        # Based on low oxytocin and social engagement
        social_level = hormones["oxytocin"] * 0.6 + derived["social_engagement"] * 0.4
        social_threshold = self._calculate_adaptive_threshold(
            "social", social_level, 0.3, inverted=True
        )

        if social_level < social_threshold and self._check_cooldown(
            "social_enhancement", current_time
        ):
            triggers_fired.append(PlasticityTriggerType.SOCIAL_ENHANCEMENT)
            self.last_trigger_times["social_enhancement"] = current_time
            print(
                f"🤝 SOCIAL TRIGGER: level={social_level:.3f}, threshold={social_threshold:.3f}"
            )

        # 4. RECOVERY CONSOLIDATION TRIGGER
        # Based on high melatonin and recovery need
        recovery_level = hormones["melatonin"] * 0.5 + derived["recovery_need"] * 0.5
        recovery_threshold = self._calculate_adaptive_threshold(
            "recovery", recovery_level, 0.6
        )

        if recovery_level > recovery_threshold and self._check_cooldown(
            "recovery_consolidation", current_time
        ):
            triggers_fired.append(PlasticityTriggerType.RECOVERY_CONSOLIDATION)
            self.last_trigger_times["recovery_consolidation"] = current_time
            print(
                f"😴 RECOVERY TRIGGER: level={recovery_level:.3f}, threshold={recovery_threshold:.3f}"
            )

        # 5. EMOTIONAL REGULATION TRIGGER
        # Based on emotional volatility and coherence
        emotional_stability = derived["emotional_coherence"]
        emotion_threshold = self._calculate_adaptive_threshold(
            "emotion", emotional_stability, 0.5, inverted=True
        )

        if emotional_stability < emotion_threshold and self._check_cooldown(
            "emotional_regulation", current_time
        ):
            triggers_fired.append(PlasticityTriggerType.EMOTIONAL_REGULATION)
            self.last_trigger_times["emotional_regulation"] = current_time
            print(
                f"💭 EMOTION TRIGGER: stability={emotional_stability:.3f}, threshold={emotion_threshold:.3f}"
            )

        return triggers_fired

    def _calculate_adaptive_threshold(
        self,
        trigger_type: str,
        current_value: float,
        base_threshold: float,
        inverted: bool = False,
    ) -> float:
        """
        🎯 **KEY METHOD: ADAPTIVE THRESHOLD CALCULATION**

        This is how thresholds are dynamically calculated based on:
        1. Historical patterns
        2. System context
        3. Time-based cycles
        4. Individual adaptation
        """

        # Get historical data for this trigger type
        history_key = f"threshold_history_{trigger_type}"
        if history_key not in self.__dict__:
            setattr(self, history_key, deque(maxlen=100))

        history = getattr(self, history_key)
        history.append(current_value)

        # Adaptive threshold calculation factors:

        # 1. BASELINE: Start with configured base threshold
        threshold = base_threshold

        # 2. HISTORICAL ADAPTATION: Adjust based on recent patterns
        if len(history) > 10:
            recent_avg = sum(list(history)[-10:]) / 10
            historical_avg = sum(history) / len(history)

            # If recent values are consistently higher/lower, adjust threshold
            adaptation_factor = (recent_avg - historical_avg) * 0.3
            if not inverted:
                threshold += adaptation_factor
            else:
                threshold -= adaptation_factor

        # 3. CIRCADIAN RHYTHM: Time-based adjustments
        current_hour = datetime.now().hour
        if trigger_type == "stress":
            # Higher stress sensitivity during typical stress hours
            if 9 <= current_hour <= 17:  # Work hours
                threshold -= 0.1
            elif current_hour >= 22 or current_hour <= 6:  # Sleep hours
                threshold += 0.1
        elif trigger_type == "recovery":
            # More recovery triggers during evening/night
            if current_hour >= 20 or current_hour <= 8:
                threshold -= 0.15

        # 4. SYSTEM LOAD ADAPTATION: Adjust based on current system state
        if hasattr(self, "last_system_load"):
            if self.last_system_load > 0.8:  # High system load
                threshold += 0.05  # Be less sensitive to avoid overload
            elif self.last_system_load < 0.3:  # Low system load
                threshold -= 0.05  # Be more sensitive to optimize

        # 5. LEARNING FACTOR: Adjust based on past trigger success
        success_key = f"trigger_success_{trigger_type}"
        if hasattr(self, success_key):
            success_rate = getattr(self, success_key, 0.5)
            if success_rate > 0.8:  # High success rate
                threshold -= 0.02  # Be more aggressive
            elif success_rate < 0.3:  # Low success rate
                threshold += 0.02  # Be more conservative

        # 6. BOUNDS CHECKING: Keep threshold within reasonable bounds
        if inverted:
            threshold = max(0.1, min(0.8, threshold))
        else:
            threshold = max(0.2, min(0.95, threshold))

        return threshold

    def _check_cooldown(self, trigger_type: str, current_time: datetime) -> bool:
        """Check if trigger is off cooldown"""

        cooldown_periods = {
            "stress_adaptation": 30,  # seconds
            "performance_optimization": 120,
            "social_enhancement": 180,
            "recovery_consolidation": 300,
            "emotional_regulation": 60,
        }

        if trigger_type not in self.last_trigger_times:
            return True

        cooldown = cooldown_periods.get(trigger_type, 60)
        time_since_last = (
            current_time - self.last_trigger_times[trigger_type]
        ).total_seconds()

        return time_since_last >= cooldown


async def demonstrate_trigger_system():
    """Demonstrate the complete trigger system in action"""

    print("🚀 LUKHAS  Enhanced Monitoring System - Trigger Demonstration")
    print("=" * 70)

    # 1. Start the monitoring system
    signal_bus = SignalBus()
    monitoring_system = await start_complete_monitoring_system(
        signal_bus, config={"profile": MonitoringProfile.DEVELOPMENT}
    )

    print("✅ Monitoring system started")

    # 2. Create data feeder
    data_feeder = LukhasDataFeeder(monitoring_system)
    await data_feeder.initialize_data_sources()

    print("✅ Connected to LUKHAS  data sources")

    # 3. Run demonstration
    print("\n📊 Starting real-time monitoring and triggering...")
    print("Watch for trigger events based on simulated LUKHAS  data:")
    print("- 🚨 Stress triggers from high cortisol/adrenaline")
    print("- 📉 Performance triggers from low efficiency")
    print("- 🤝 Social triggers from low oxytocin")
    print("- 😴 Recovery triggers from high melatonin")
    print("- 💭 Emotional triggers from low coherence")
    print("\nPress Ctrl+C to stop...\n")

    try:
        await data_feeder.feed_continuous_data()
    except KeyboardInterrupt:
        print("\n🛑 Stopping demonstration...")
        await monitoring_system.stop_monitoring()
        print("✅ System stopped gracefully")


if __name__ == "__main__":
    asyncio.run(demonstrate_trigger_system())
