#!/usr/bin/env python3
"""
Data Integration Map
===================
Shows exactly how data flows from lukhas__modules into the monitoring system
"""
import time
from dataclasses import dataclass

import streamlit as st


@dataclass
class DataIntegrationMap:
    """Complete mapping of LUKHAS  data sources to monitoring system"""

    # 🧠 CONSCIOUSNESS MODULE DATA
    consciousness_sources = {
        "auto_consciousness.py": {
            "methods": [
                "assess_awareness()",
                "get_attention_targets()",
                "make_decision()",
                "get_consciousness_level()",
            ],
            "feeds_into": [
                "adaptive_metrics_collector.attention_focus",
                "adaptive_metrics_collector.decision_confidence",
                "bio_symbolic_coherence_monitor.consciousness_level",
                "endocrine_observability_engine.system_metrics",
            ],
            "trigger_influence": "High consciousness → stress/performance triggers",
        },
        "natural_language_interface.py": {
            "methods": ["_analyze_emotion()", "process_input()", "_determine_tone()"],
            "feeds_into": [
                "adaptive_metrics_collector.emotional_coherence",
                "adaptive_metrics_collector.communication_clarity",
                "hormone_driven_dashboard.interaction_quality",
            ],
            "trigger_influence": "Emotional analysis → emotional_regulation triggers",
        },
    }

    # 🧬 MEMORY MODULE DATA
    memory_sources = {
        "memoria.py": {
            "methods": [
                "get_memory_load()",
                "get_fold_count()",
                "search_memories()",
                "get_consolidation_rate()",
            ],
            "feeds_into": [
                "adaptive_metrics_collector.memory_efficiency",
                "adaptive_metrics_collector.learning_rate",
                "bio_symbolic_coherence_monitor.memory_operations",
                "neuroplastic_learning_orchestrator.learning_progress",
            ],
            "trigger_influence": "High memory load → performance optimization triggers",
        },
        "fold_memory.py": {
            "methods": [
                "get_fold_statistics()",
                "measure_cascade_prevention()",
                "get_emotional_context()",
            ],
            "feeds_into": [
                "bio_symbolic_coherence_monitor.learning_integration",
                "adaptive_metrics_collector.memory_operations",
            ],
            "trigger_influence": "Memory cascades → recovery consolidation triggers",
        },
    }

    # 💭 EMOTION MODULE DATA
    emotion_sources = {
        "service.py": {
            "methods": [
                "get_current_state()",
                "analyze_text()",
                "get_mood_indicators()",
            ],
            "feeds_into": [
                "adaptive_metrics_collector.emotional_coherence",
                "adaptive_metrics_collector.empathy_engagement",
                "endocrine_observability_engine.hormone_correlations",
                "bio_symbolic_coherence_monitor.emotional_symbolic_sync",
            ],
            "trigger_influence": "Emotional instability → emotional_regulation triggers",
        },
        "vad_affect.py": {
            "methods": ["get_valence()", "get_arousal()", "get_dominance()"],
            "feeds_into": [
                "hormone_driven_dashboard.emotional_state",
                "bio_symbolic_coherence_monitor.emotional_coherence",
            ],
            "trigger_influence": "Low valence → social_enhancement triggers",
        },
    }

    # 🧮 REASONING MODULE DATA
    reasoning_sources = {
        "causal_inference.py": {
            "methods": [
                "get_processing_depth()",
                "get_inference_rate()",
                "get_logical_coherence()",
                "assess_reasoning_quality()",
            ],
            "feeds_into": [
                "adaptive_metrics_collector.decision_confidence",
                "bio_symbolic_coherence_monitor.decision_biomarker_match",
                "neuroplastic_learning_orchestrator.causal_models",
            ],
            "trigger_influence": "Poor reasoning → performance optimization triggers",
        },
        "goal_processing.py": {
            "methods": [
                "get_goal_progress()",
                "assess_goal_conflicts()",
                "get_priority_weights()",
            ],
            "feeds_into": [
                "neuroplastic_learning_orchestrator.learning_goals",
                "adaptive_metrics_collector.goal_alignment",
            ],
            "trigger_influence": "Goal conflicts → stress adaptation triggers",
        },
    }

    # 🧬 BIOLOGICAL MODULE DATA
    biological_sources = {
        "endocrine_integration.py": {
            "methods": [
                "get_hormone_levels()",
                "get_homeostasis_state()",
                "trigger_stress_response()",
                "get_hormone_profile()",
            ],
            "feeds_into": [
                "endocrine_observability_engine.hormone_levels",
                "endocrine_observability_engine.homeostasis_state",
                "bio_symbolic_coherence_monitor.bio_component_state",
                "adaptive_metrics_collector.biological_correlation",
            ],
            "trigger_influence": "ALL TRIGGERS - Primary biological driver",
        },
        "hormone_system.py": {
            "methods": [
                "HormoneType.get_all()",
                "get_hormone_balance()",
                "calculate_stress_indicators()",
            ],
            "feeds_into": [
                "hormone_driven_dashboard.hormone_radar",
                "plasticity_trigger_manager.hormone_context",
            ],
            "trigger_influence": "Hormone imbalances → specific trigger types",
        },
    }

    # 🎨 CREATIVITY MODULE DATA
    creativity_sources = {
        "dream_engine.py": {
            "methods": [
                "get_creativity_level()",
                "assess_imaginative_capacity()",
                "get_dream_statistics()",
            ],
            "feeds_into": [
                "adaptive_metrics_collector.creative_engagement",
                "neuroplastic_learning_orchestrator.creative_experiments",
            ],
            "trigger_influence": "Low creativity → creative_boost triggers",
        }
    }

    # 🏛️ GOVERNANCE MODULE DATA
    governance_sources = {
        "audit_trail.py": {
            "methods": [
                "get_system_stability()",
                "get_ethical_compliance()",
                "assess_decision_quality()",
            ],
            "feeds_into": [
                "adaptive_metrics_collector.governance_metrics",
                "bio_symbolic_coherence_monitor.ethical_alignment",
            ],
            "trigger_influence": "Ethical concerns → governance triggers",
        }
    }

    # 🔄 ORCHESTRATION MODULE DATA
    orchestration_sources = {
        "signal_bus.py": {
            "methods": [
                "get_signal_statistics()",
                "get_processing_load()",
                "get_communication_efficiency()",
            ],
            "feeds_into": [
                "integrated_monitoring_system.signal_processing",
                "adaptive_metrics_collector.communication_metrics",
            ],
            "trigger_influence": "Signal overload → efficiency_tuning triggers",
        },
        "homeostasis_controller.py": {
            "methods": [
                "get_current_state()",
                "get_state_transitions()",
                "get_stability_metrics()",
            ],
            "feeds_into": [
                "endocrine_observability_engine.homeostasis_state",
                "bio_symbolic_coherence_monitor.homeostasis_consciousness",
            ],
            "trigger_influence": "State instability → resilience_building triggers",
        },
    }


def show_data_flow_example():
    """Show concrete example of data flowing through the system"""

    print("🌊 LUKHAS  → Enhanced Monitoring System Data Flow")
    print("=" * 60)

    # Example: User interaction triggers cascade
    print("\n📝 EXAMPLE: User asks 'I feel stressed about work'")
    print("   ↓")
    print("1️⃣  natural_language_interface._analyze_emotion()")
    print("   → detects: {'anger': 0.3, 'fear': 0.4, 'sadness': 0.2}")
    print("   ↓")
    print("2️⃣  consciousness.auto_consciousness.assess_awareness()")
    print("   → returns: {'awareness_level': 0.85, 'attention_targets': ['user_stress']}")
    print("   ↓")
    print("3️⃣  bio.endocrine_integration.get_hormone_levels()")
    print("   → simulates: {'cortisol': 0.8, 'adrenaline': 0.7, 'gaba': 0.3}")
    print("   ↓")
    print("4️⃣  adaptive_metrics_collector calculates:")
    print("   → stress_indicator = (0.8*0.4 + 0.7*0.3 + 0.6*0.3) = 0.71")
    print("   → emotional_coherence = (0.4 coherence from emotional analysis)")
    print("   ↓")
    print("5️⃣  endocrine_observability_engine._analyze_plasticity_triggers()")
    print("   → STRESS TRIGGER: 0.71 > threshold(0.68) ✅")
    print("   → EMOTIONAL TRIGGER: 0.4 < threshold(0.5) ✅")
    print("   ↓")
    print("6️⃣  plasticity_trigger_manager.evaluate_trigger()")
    print("   → Creates AdaptationPlan: IMMEDIATE stress response")
    print("   → Risk assessment: 0.2 (low risk)")
    print("   ↓")
    print("7️⃣  neuroplastic_learning_orchestrator applies adaptation")
    print("   → Activates stress protocols")
    print("   → Records experiment for learning")
    print("   ↓")
    print("8️⃣  hormone_driven_dashboard updates:")
    print("   → Shows stress alert")
    print("   → Predicts recovery timeline")
    print("   → Suggests coping strategies")

    print("\n🔄 This entire cascade happens in ~2-5 seconds!")
    print("🧠 System learns from outcome to improve future responses")


def show_threshold_calculation_details():
    """Show detailed threshold calculation examples"""

    print("\n🎯 DETAILED THRESHOLD CALCULATIONS")
    print("=" * 50)

    print("\n📊 STRESS TRIGGER THRESHOLD:")
    print("Base threshold: 0.70")
    print("+ Historical adaptation: -0.05 (recent values lower)")
    print("+ Circadian factor: -0.10 (work hours, more sensitive)")
    print("+ System load factor: +0.02 (moderate load)")
    print("+ Success rate factor: -0.03 (high success rate)")
    print("= Final threshold: 0.54")
    print("Current stress level: 0.71 → TRIGGER! ✅")

    print("\n📈 PERFORMANCE TRIGGER THRESHOLD:")
    print("Base threshold: 0.40 (inverted - low performance triggers)")
    print("+ Historical adaptation: +0.08 (performance declining)")
    print("+ Learning factor: -0.02 (learning is effective)")
    print("+ Context factor: -0.05 (problem-solving mode)")
    print("= Final threshold: 0.41")
    print("Current performance: 0.35 → TRIGGER! ✅")

    print("\n🤝 SOCIAL TRIGGER THRESHOLD:")
    print("Base threshold: 0.30 (inverted - low social triggers)")
    print("+ Historical adaptation: -0.03 (social interactions declining)")
    print("+ Time factor: +0.05 (evening, less social)")
    print("+ Context factor: +0.02 (no recent social interactions)")
    print("= Final threshold: 0.34")
    print("Current social level: 0.28 → TRIGGER! ✅")


if __name__ == "__main__":
    show_data_flow_example()
    show_threshold_calculation_details()
