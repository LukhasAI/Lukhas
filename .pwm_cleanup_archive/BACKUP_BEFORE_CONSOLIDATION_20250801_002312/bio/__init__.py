"""
Bio System - Auto-generated entity exports
Generated from entity activation scan
Total entities: 255
"""

# Lazy imports to avoid circular dependencies
import importlib
import logging

logger = logging.getLogger(__name__)

# Entity registry for lazy loading
_ENTITY_REGISTRY = {
    "OscillationType": ("base_oscillator", "OscillationType"),
    "OscillatorConfig": ("base_oscillator", "OscillatorConfig"),
    "BaseOscillator": ("base_oscillator", "BaseOscillator"),
    "BioHub": ("bio_hub", "BioHub"),
    "StressSignal": ("bio_utilities", "StressSignal"),
    "CuriositySpark": ("bio_utilities", "CuriositySpark"),
    "ResilienceBoost": ("bio_utilities", "ResilienceBoost"),
    "ProteinSynthesizer": ("bio_utilities", "ProteinSynthesizer"),
    "StabilityAnchor": ("bio_utilities", "StabilityAnchor"),
    "BioCore": ("core", "BioCore"),
    "CuriositySpark": ("curiosity_spark", "CuriositySpark"),
    "BrainwaveBand": ("eeg_sync_bridge", "BrainwaveBand"),
    "SymbolicState": ("eeg_sync_bridge", "SymbolicState"),
    "TaskPriority": ("endocrine_daily_operations", "TaskPriority"),
    "TaskType": ("endocrine_daily_operations", "TaskType"),
    "EnhancedDailyOperations": (
        "endocrine_daily_operations",
        "EnhancedDailyOperations",
    ),
    "HormoneModulation": ("endocrine_integration", "HormoneModulation"),
    "EndocrineIntegration": ("endocrine_integration", "EndocrineIntegration"),
    "SecurityContext": ("oscillator", "SecurityContext"),
    "OscillationType": ("oscillator", "OscillationType"),
    "OscillatorState": ("oscillator", "OscillatorState"),
    "BioOscillator": ("oscillator", "BioOscillator"),
    "MoodOscillator": ("oscillator", "MoodOscillator"),
    "PrimeHarmonicOscillator": ("prime_oscillator", "PrimeHarmonicOscillator"),
    "ProteinSynthesizer": ("protein_synthesizer", "ProteinSynthesizer"),
    "QuantumBioConfig": ("quantum_layer", "QuantumBioConfig"),
    "QuantumBioOscillator": ("quantum_layer", "QuantumBioOscillator"),
    "BioRecoveryProtocol": ("recovery_protocol", "BioRecoveryProtocol"),
    "ResilienceBoost": ("resilience_boost", "ResilienceBoost"),
    "HormoneType": ("simulation_controller", "HormoneType"),
    "HormoneInteraction": ("simulation_controller", "HormoneInteraction"),
    "Hormone": ("simulation_controller", "Hormone"),
    "BioSimulationController": ("simulation_controller", "BioSimulationController"),
    "StabilityAnchor": ("stability_anchor", "StabilityAnchor"),
    "StressSignal": ("stress_signal", "StressSignal"),
    "AdaptiveThresholdColony": (
        "symbolic.adaptive_threshold_colony",
        "AdaptiveThresholdColony",
    ),
    "AnomalyType": ("symbolic.anomaly_filter_colony", "AnomalyType"),
    "AnomalyAction": ("symbolic.anomaly_filter_colony", "AnomalyAction"),
    "AnomalyFilterColony": ("symbolic.anomaly_filter_colony", "AnomalyFilterColony"),
    "SymbolicGlyph": ("symbolic.bio_symbolic", "SymbolicGlyph"),
    "BioSymbolic": ("symbolic.bio_symbolic", "BioSymbolic"),
    "CoherenceMetrics": ("symbolic.bio_symbolic_orchestrator", "CoherenceMetrics"),
    "ProcessingPipeline": ("symbolic.bio_symbolic_orchestrator", "ProcessingPipeline"),
    "BioSymbolicOrchestrator": (
        "symbolic.bio_symbolic_orchestrator",
        "BioSymbolicOrchestrator",
    ),
    "ContextLayer": ("symbolic.contextual_mapping_colony", "ContextLayer"),
    "ContextualMappingColony": (
        "symbolic.contextual_mapping_colony",
        "ContextualMappingColony",
    ),
    "CristaOptimizer": ("symbolic.crista_optimizer", "CristaOptimizer"),
    "DNASimulator": ("symbolic.dna_simulator", "DNASimulator"),
    "FallbackLevel": ("symbolic.fallback_systems", "FallbackLevel"),
    "FallbackReason": ("symbolic.fallback_systems", "FallbackReason"),
    "FallbackEvent": ("symbolic.fallback_systems", "FallbackEvent"),
    "BioSymbolicFallbackManager": (
        "symbolic.fallback_systems",
        "BioSymbolicFallbackManager",
    ),
    "FallbackCoherenceMetrics": (
        "symbolic.fallback_systems",
        "FallbackCoherenceMetrics",
    ),
    "FallbackCoherenceMetrics": (
        "symbolic.fallback_systems",
        "FallbackCoherenceMetrics",
    ),
    "FallbackCoherenceMetrics": (
        "symbolic.fallback_systems",
        "FallbackCoherenceMetrics",
    ),
    "FallbackCoherenceMetrics": (
        "symbolic.fallback_systems",
        "FallbackCoherenceMetrics",
    ),
    "GlyphIDHasher": ("symbolic.glyph_id_hash", "GlyphIDHasher"),
    "MitoEthicsSync": ("symbolic.mito_ethics_sync", "MitoEthicsSync"),
    "QuantumTunnelFilter": ("symbolic.mito_quantum_attention", "QuantumTunnelFilter"),
    "CristaGate": ("symbolic.mito_quantum_attention", "CristaGate"),
    "VivoxAttention": ("symbolic.mito_quantum_attention", "VivoxAttention"),
    "OxintusReasoner": ("symbolic.mito_quantum_attention", "OxintusReasoner"),
    "MAELayer": ("symbolic.mito_quantum_attention", "MAELayer"),
    "RespiModule": ("symbolic.mito_quantum_attention", "RespiModule"),
    "ATPAllocator": ("symbolic.mito_quantum_attention", "ATPAllocator"),
    "VivoxSection": ("symbolic.mito_quantum_attention", "VivoxSection"),
    "OxintusBrass": ("symbolic.mito_quantum_attention", "OxintusBrass"),
    "MAEPercussion": ("symbolic.mito_quantum_attention", "MAEPercussion"),
    "MitochondrialConductor": (
        "symbolic.mito_quantum_attention",
        "MitochondrialConductor",
    ),
    "CristaOptimizer": ("symbolic.mito_quantum_attention", "CristaOptimizer"),
    "BioPreprocessingColony": (
        "symbolic.preprocessing_colony",
        "BioPreprocessingColony",
    ),
    "QuantumState": ("symbolic.quantum_coherence_enhancer", "QuantumState"),
    "QuantumCoherenceEnhancer": (
        "symbolic.quantum_coherence_enhancer",
        "QuantumCoherenceEnhancer",
    ),
    "StressGate": ("symbolic.stress_gate", "StressGate"),
    "SymbolicEntropyObserver": ("symbolic_entropy_observer", "SymbolicEntropyObserver"),
    "MitochondriaModel": ("systems.mitochondria_model", "MitochondriaModel"),
    "VoiceBioAdapter": (
        "systems.orchestration.adapters.voice_adapter",
        "VoiceBioAdapter",
    ),
    "ModuleHealth": ("systems.orchestration.base_orchestrator", "ModuleHealth"),
    "ResourcePriority": ("systems.orchestration.base_orchestrator", "ResourcePriority"),
    "BaseBioOrchestrator": (
        "systems.orchestration.base_orchestrator",
        "BaseBioOrchestrator",
    ),
    "BioOrchestrator": ("systems.orchestration.bio_orchestrator", "BioOrchestrator"),
    "IdentityAwareBioOrchestrator": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "IdentityAwareBioOrchestrator",
    ),
    "DemoModule": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "DemoModule",
    ),
    "OrchestratorConfig": (
        "systems.orchestration.oscillator_orchestrator",
        "OrchestratorConfig",
    ),
    "OscillatorBioOrchestrator": (
        "systems.orchestration.oscillator_orchestrator",
        "OscillatorBioOrchestrator",
    ),
    "QuantumBioOscillator": (
        "systems.orchestration.oscillator_orchestrator",
        "QuantumBioOscillator",
    ),
    "QuantumLikeState": (
        "systems.orchestration.oscillator_orchestrator",
        "QuantumLikeState",
    ),
    "PrimeHarmonicOscillator": (
        "systems.orchestration.oscillator_orchestrator",
        "PrimeHarmonicOscillator",
    ),
    "OscillatorConfig": (
        "systems.orchestration.oscillator_orchestrator",
        "OscillatorConfig",
    ),
    "TrustBinder": ("trust_binder", "TrustBinder"),
}

# Function registry
_FUNCTION_REGISTRY = {
    "frequency": ("base_oscillator", "frequency"),
    "frequency": ("base_oscillator", "frequency"),
    "phase": ("base_oscillator", "phase"),
    "phase": ("base_oscillator", "phase"),
    "amplitude": ("base_oscillator", "amplitude"),
    "amplitude": ("base_oscillator", "amplitude"),
    "generate_value": ("base_oscillator", "generate_value"),
    "update_metrics": ("base_oscillator", "update_metrics"),
    "inject_narrative_repair": ("bio_affect_model", "inject_narrative_repair"),
    "fatigue_level": ("bio_homeostasis", "fatigue_level"),
    "get_bio_hub": ("bio_hub", "get_bio_hub"),
    "register_service": ("bio_hub", "register_service"),
    "get_service": ("bio_hub", "get_service"),
    "register_event_handler": ("bio_hub", "register_event_handler"),
    "weight_modulator": ("bio_utilities", "weight_modulator"),
    "weight_modulator": ("bio_utilities", "weight_modulator"),
    "weight_modulator": ("bio_utilities", "weight_modulator"),
    "fatigue_level": ("bio_utilities", "fatigue_level"),
    "inject_narrative_repair": ("bio_utilities", "inject_narrative_repair"),
    "weight_modulator": ("bio_utilities", "weight_modulator"),
    "get_system_status": ("core", "get_system_status"),
    "weight_modulator": ("curiosity_spark", "weight_modulator"),
    "ingest_mock_eeg": ("eeg_sync_bridge", "ingest_mock_eeg"),
    "map_to_symbolic_state": ("eeg_sync_bridge", "map_to_symbolic_state"),
    "add_task": ("endocrine_daily_operations", "add_task"),
    "get_operational_status": ("endocrine_daily_operations", "get_operational_status"),
    "get_modulation_factor": ("endocrine_integration", "get_modulation_factor"),
    "get_system_recommendations": (
        "endocrine_integration",
        "get_system_recommendations",
    ),
    "inject_system_feedback": ("endocrine_integration", "inject_system_feedback"),
    "get_daily_rhythm_phase": ("endocrine_integration", "get_daily_rhythm_phase"),
    "get_status": ("oscillator", "get_status"),
    "register_neuroplastic_event": ("oscillator", "register_neuroplastic_event"),
    "update_mood": ("oscillator", "update_mood"),
    "bio_affect_feedback": ("oscillator", "bio_affect_feedback"),
    "bio_drift_response": ("oscillator", "bio_drift_response"),
    "generate_value": ("prime_oscillator", "generate_value"),
    "update_metrics": ("prime_oscillator", "update_metrics"),
    "get_state": ("prime_oscillator", "get_state"),
    "oscillate": ("quantum_layer", "oscillate"),
    "create_entanglement": ("quantum_layer", "create_entanglement"),
    "apply_entanglement_effects": ("quantum_layer", "apply_entanglement_effects"),
    "measure_quantum_property": ("quantum_layer", "measure_quantum_property"),
    "evolve_quantum_like_state": ("quantum_layer", "evolve_quantum_like_state"),
    "get_oscillator_metrics": ("quantum_layer", "get_oscillator_metrics"),
    "reset_oscillator": ("quantum_layer", "reset_oscillator"),
    "synchronize_with_rhythm": ("quantum_layer", "synchronize_with_rhythm"),
    "create_coherence_field": ("quantum_layer", "create_coherence_field"),
    "weight_modulator": ("resilience_boost", "weight_modulator"),
    "update_level": ("simulation_controller", "update_level"),
    "add_hormone": ("simulation_controller", "add_hormone"),
    "recover": ("simulation_controller", "recover"),
    "trigger_phase_shift": ("simulation_controller", "trigger_phase_shift"),
    "stabilize_oscillator": ("simulation_controller", "stabilize_oscillator"),
    "get_hormone_state": ("simulation_controller", "get_hormone_state"),
    "get_cognitive_state": ("simulation_controller", "get_cognitive_state"),
    "inject_stimulus": ("simulation_controller", "inject_stimulus"),
    "register_state_callback": ("simulation_controller", "register_state_callback"),
    "suggest_action": ("simulation_controller", "suggest_action"),
    "weight_modulator": ("stability_anchor", "weight_modulator"),
    "weight_modulator": ("stress_signal", "weight_modulator"),
    "create_threshold_colony": (
        "symbolic.adaptive_threshold_colony",
        "create_threshold_colony",
    ),
    "create_anomaly_filter_colony": (
        "symbolic.anomaly_filter_colony",
        "create_anomaly_filter_colony",
    ),
    "process": ("symbolic.bio_symbolic", "process"),
    "process_rhythm": ("symbolic.bio_symbolic", "process_rhythm"),
    "process_energy": ("symbolic.bio_symbolic", "process_energy"),
    "process_dna": ("symbolic.bio_symbolic", "process_dna"),
    "process_stress": ("symbolic.bio_symbolic", "process_stress"),
    "process_homeostasis": ("symbolic.bio_symbolic", "process_homeostasis"),
    "process_neural": ("symbolic.bio_symbolic", "process_neural"),
    "process_generic": ("symbolic.bio_symbolic", "process_generic"),
    "get_statistics": ("symbolic.bio_symbolic", "get_statistics"),
    "reset": ("symbolic.bio_symbolic", "reset"),
    "create_bio_symbolic_orchestrator": (
        "symbolic.bio_symbolic_orchestrator",
        "create_bio_symbolic_orchestrator",
    ),
    "create_mapping_colony": (
        "symbolic.contextual_mapping_colony",
        "create_mapping_colony",
    ),
    "optimize": ("symbolic.crista_optimizer", "optimize"),
    "report_state": ("symbolic.crista_optimizer", "report_state"),
    "parse_sequence": ("symbolic.dna_simulator", "parse_sequence"),
    "entangle_with_colony": ("symbolic.dna_simulator", "entangle_with_colony"),
    "get_fallback_manager": ("symbolic.fallback_systems", "get_fallback_manager"),
    "register_service": ("symbolic.fallback_systems", "register_service"),
    "get_service": ("symbolic.fallback_systems", "get_service"),
    "get_system_health_report": (
        "symbolic.fallback_systems",
        "get_system_health_report",
    ),
    "generate_signature": ("symbolic.glyph_id_hash", "generate_signature"),
    "generate_base64_glyph": ("symbolic.glyph_id_hash", "generate_base64_glyph"),
    "update_phase": ("symbolic.mito_ethics_sync", "update_phase"),
    "assess_alignment": ("symbolic.mito_ethics_sync", "assess_alignment"),
    "is_synchronized": ("symbolic.mito_ethics_sync", "is_synchronized"),
    "generate_cl_signature": (
        "symbolic.mito_quantum_attention",
        "generate_cl_signature",
    ),
    "forward": ("symbolic.mito_quantum_attention", "forward"),
    "forward": ("symbolic.mito_quantum_attention", "forward"),
    "forward": ("symbolic.mito_quantum_attention", "forward"),
    "forward": ("symbolic.mito_quantum_attention", "forward"),
    "forward": ("symbolic.mito_quantum_attention", "forward"),
    "forward": ("symbolic.mito_quantum_attention", "forward"),
    "allocate": ("symbolic.mito_quantum_attention", "allocate"),
    "play": ("symbolic.mito_quantum_attention", "play"),
    "play": ("symbolic.mito_quantum_attention", "play"),
    "play": ("symbolic.mito_quantum_attention", "play"),
    "perform": ("symbolic.mito_quantum_attention", "perform"),
    "optimize": ("symbolic.mito_quantum_attention", "optimize"),
    "create_preprocessing_colony": (
        "symbolic.preprocessing_colony",
        "create_preprocessing_colony",
    ),
    "create_quantum_enhancer": (
        "symbolic.quantum_coherence_enhancer",
        "create_quantum_enhancer",
    ),
    "z_collapse": ("symbolic.quantum_coherence_enhancer", "z_collapse"),
    "drift_score": ("symbolic.quantum_coherence_enhancer", "drift_score"),
    "enhance_coherence": ("symbolic.quantum_coherence_enhancer", "enhance_coherence"),
    "get_quantum_summary": (
        "symbolic.quantum_coherence_enhancer",
        "get_quantum_summary",
    ),
    "update_stress": ("symbolic.stress_gate", "update_stress"),
    "should_fallback": ("symbolic.stress_gate", "should_fallback"),
    "reset": ("symbolic.stress_gate", "reset"),
    "report": ("symbolic.stress_gate", "report"),
    "calculate_entropy_delta": ("symbolic_entropy", "calculate_entropy_delta"),
    "entropy_state_snapshot": ("symbolic_entropy", "entropy_state_snapshot"),
    "get_latest_entropy_snapshot": (
        "symbolic_entropy_observer",
        "get_latest_entropy_snapshot",
    ),
    "get_entropy_history": ("symbolic_entropy_observer", "get_entropy_history"),
    "energy_output": ("systems.mitochondria_model", "energy_output"),
    "process_audio_chunk": (
        "systems.orchestration.adapters.voice_adapter",
        "process_audio_chunk",
    ),
    "optimize_for_realtime": (
        "systems.orchestration.adapters.voice_adapter",
        "optimize_for_realtime",
    ),
    "get_voice_metrics": (
        "systems.orchestration.adapters.voice_adapter",
        "get_voice_metrics",
    ),
    "register_module": ("systems.orchestration.base_orchestrator", "register_module"),
    "invoke_module": ("systems.orchestration.base_orchestrator", "invoke_module"),
    "get_status": ("systems.orchestration.base_orchestrator", "get_status"),
    "get_module_status": (
        "systems.orchestration.base_orchestrator",
        "get_module_status",
    ),
    "orchestrate": ("systems.orchestration.base_orchestrator", "orchestrate"),
    "enhanced_attention_hook": (
        "systems.orchestration.bio_orchestrator",
        "enhanced_attention_hook",
    ),
    "shutdown": ("systems.orchestration.bio_orchestrator", "shutdown"),
    "register_module": ("systems.orchestration.bio_orchestrator", "register_module"),
    "update_module": ("systems.orchestration.bio_orchestrator", "update_module"),
    "invoke_module": ("systems.orchestration.bio_orchestrator", "invoke_module"),
    "invoke_module_async": (
        "systems.orchestration.bio_orchestrator",
        "invoke_module_async",
    ),
    "allocate_resources": (
        "systems.orchestration.bio_orchestrator",
        "allocate_resources",
    ),
    "update_energy_buffers": (
        "systems.orchestration.bio_orchestrator",
        "update_energy_buffers",
    ),
    "check_system_health": (
        "systems.orchestration.bio_orchestrator",
        "check_system_health",
    ),
    "attempt_auto_repair": (
        "systems.orchestration.bio_orchestrator",
        "attempt_auto_repair",
    ),
    "rebalance_energy": ("systems.orchestration.bio_orchestrator", "rebalance_energy"),
    "get_system_status": (
        "systems.orchestration.bio_orchestrator",
        "get_system_status",
    ),
    "get_module_status": (
        "systems.orchestration.bio_orchestrator",
        "get_module_status",
    ),
    "orchestrate": ("systems.orchestration.bio_orchestrator", "orchestrate"),
    "get_status": ("systems.orchestration.bio_orchestrator", "get_status"),
    "wrapped_attention": (
        "systems.orchestration.bio_orchestrator",
        "wrapped_attention",
    ),
    "monitor_loop": ("systems.orchestration.bio_orchestrator", "monitor_loop"),
    "setup_import_redirects": (
        "systems.orchestration.compatibility",
        "setup_import_redirects",
    ),
    "get_service_info": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "get_service_info",
    ),
    "register_module": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "register_module",
    ),
    "unregister_module": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "unregister_module",
    ),
    "allocate_energy": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "allocate_energy",
    ),
    "heal_module": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "heal_module",
    ),
    "get_user_modules": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "get_user_modules",
    ),
    "get_tiered_system_status": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "get_tiered_system_status",
    ),
    "admin_override_allocation": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "admin_override_allocation",
    ),
    "cleanup_user_resources": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "cleanup_user_resources",
    ),
    "basic_status": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "basic_status",
    ),
    "detailed_status": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "detailed_status",
    ),
    "admin_status": (
        "systems.orchestration.identity_aware_bio_orchestrator",
        "admin_status",
    ),
    "process": ("systems.orchestration.identity_aware_bio_orchestrator", "process"),
    "add_oscillator": (
        "systems.orchestration.oscillator_orchestrator",
        "add_oscillator",
    ),
    "remove_oscillator": (
        "systems.orchestration.oscillator_orchestrator",
        "remove_oscillator",
    ),
    "monitor_coherence": (
        "systems.orchestration.oscillator_orchestrator",
        "monitor_coherence",
    ),
    "apply_resonance_pattern": (
        "systems.orchestration.oscillator_orchestrator",
        "apply_resonance_pattern",
    ),
    "correct_phase_drift": (
        "systems.orchestration.oscillator_orchestrator",
        "correct_phase_drift",
    ),
    "get_status": ("systems.orchestration.oscillator_orchestrator", "get_status"),
    "manage_quantum_like_states": (
        "systems.orchestration.oscillator_orchestrator",
        "manage_quantum_like_states",
    ),
    "get_quantum_metrics": (
        "systems.orchestration.oscillator_orchestrator",
        "get_quantum_metrics",
    ),
    "register_module": (
        "systems.orchestration.oscillator_orchestrator",
        "register_module",
    ),
    "invoke_module": ("systems.orchestration.oscillator_orchestrator", "invoke_module"),
    "process_affect": ("trust_binder", "process_affect"),
}


def __getattr__(name):
    """Lazy import entities on access"""
    # Check class registry first
    if name in _ENTITY_REGISTRY:
        module_path, attr_name = _ENTITY_REGISTRY[name]
        try:
            module = importlib.import_module(f".{module_path}", package=__package__)
            return getattr(module, attr_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to import {attr_name} from {module_path}: {e}")
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    # Check function registry
    if name in _FUNCTION_REGISTRY:
        module_path, attr_name = _FUNCTION_REGISTRY[name]
        try:
            module = importlib.import_module(f".{module_path}", package=__package__)
            return getattr(module, attr_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to import {attr_name} from {module_path}: {e}")
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """List all available entities"""
    return list(_ENTITY_REGISTRY.keys()) + list(_FUNCTION_REGISTRY.keys())


# Export commonly used entities directly for better IDE support
__all__ = [
    "OscillationType",
    "OscillatorConfig",
    "BaseOscillator",
    "BioHub",
    "StressSignal",
    "CuriositySpark",
    "ResilienceBoost",
    "ProteinSynthesizer",
    "StabilityAnchor",
    "BioCore",
    "CuriositySpark",
    "BrainwaveBand",
    "SymbolicState",
    "TaskPriority",
    "TaskType",
    "EnhancedDailyOperations",
    "HormoneModulation",
    "EndocrineIntegration",
    "SecurityContext",
    "OscillationType",
]

# System metadata
__system__ = "bio"
__total_entities__ = 255
__classes__ = 90
__functions__ = 165
