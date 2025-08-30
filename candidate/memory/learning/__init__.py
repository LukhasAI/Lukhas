"""
Learning System - Auto-generated entity exports
Generated from entity activation scan
Total entities: 220
"""

# Lazy imports to avoid circular dependencies
import importlib

from candidate.core.common import get_logger

logger = get_logger(__name__)

# Entity registry for lazy loading
_ENTITY_REGISTRY = {
    "_BaseSparseCoding": ("_dict_learning", "_BaseSparseCoding"),
    "SparseCoder": ("_dict_learning", "SparseCoder"),
    "DictionaryLearning": ("_dict_learning", "DictionaryLearning"),
    "MiniBatchDictionaryLearning": ("_dict_learning", "MiniBatchDictionaryLearning"),
    "AdaptiveMetaLearningSystem": (
        "adaptive_meta_learning",
        "AdaptiveMetaLearningSystem",
    ),
    "GenerativeReflex": ("embodied_thought.generative_reflex", "GenerativeReflex"),
    "ExponentialLearningSystem": ("exponential_learning", "ExponentialLearningSystem"),
    "LearningAgent": ("federated_colony_learning", "LearningAgent"),
    "FederatedLearningColony": ("federated_colony_learning", "FederatedLearningColony"),
    "FederatedLearningManager": ("federated_learning", "FederatedLearningManager"),
    "LukhasFederatedModel": ("federated_learning_system", "LukhasFederatedModel"),
    "LukhasFederatedLearningManager": (
        "federated_learning_system",
        "LukhasFederatedLearningManager",
    ),
    "FederatedLearningManager": ("federated_meta_learning", "FederatedLearningManager"),
    "ReflectiveIntrospectionSystem": (
        "federated_meta_learning",
        "ReflectiveIntrospectionSystem",
    ),
    "LearningRequest": ("learning_gateway", "LearningRequest"),
    "LearningResponse": ("learning_gateway", "LearningResponse"),
    "LearningGatewayInterface": ("learning_gateway", "LearningGatewayInterface"),
    "LearningGateway": ("learning_gateway", "LearningGateway"),
    "LearningHub": ("learning_hub", "LearningHub"),
    "AdaptiveInterfaceGenerator": (
        "meta_adaptive.adaptive_interface_generator",
        "AdaptiveInterfaceGenerator",
    ),
    "FederatedModel": ("meta_adaptive.meta_learning", "FederatedModel"),
    "FederatedLearningManager": (
        "meta_adaptive.meta_learning",
        "FederatedLearningManager",
    ),
    "ReflectiveIntrospectionSystem": (
        "meta_adaptive.meta_learning",
        "ReflectiveIntrospectionSystem",
    ),
    "LearningMetrics": ("meta_learning", "LearningMetrics"),
    "MetaLearningSystem": ("meta_learning", "MetaLearningSystem"),
    "Federationstrategy": ("meta_learning.federated_integration", "Federationstrategy"),
    "Privacylevel": ("meta_learning.federated_integration", "Privacylevel"),
    "Federatednode": ("meta_learning.federated_integration", "Federatednode"),
    "Federatedlearningupdate": (
        "meta_learning.federated_integration",
        "Federatedlearningupdate",
    ),
    "Federatedlearningintegration": (
        "meta_learning.federated_integration",
        "Federatedlearningintegration",
    ),
    "MetaCore": ("meta_learning.meta_core", "MetaCore"),
    "Feedbacktype": ("meta_learning.symbolic_feedback", "Feedbacktype"),
    "Symboliccontext": ("meta_learning.symbolic_feedback", "Symboliccontext"),
    "Intentnodehistory": ("meta_learning.symbolic_feedback", "Intentnodehistory"),
    "Memoriasnapshot": ("meta_learning.symbolic_feedback", "Memoriasnapshot"),
    "Dreamreplayrecord": ("meta_learning.symbolic_feedback", "Dreamreplayrecord"),
    "Symbolicfeedbackloop": ("meta_learning.symbolic_feedback", "Symbolicfeedbackloop"),
    "Symbolicfeedbacksystem": (
        "meta_learning.symbolic_feedback",
        "Symbolicfeedbacksystem",
    ),
    "LearningPhase": ("meta_learning_adapter", "LearningPhase"),
    "FederatedState": ("meta_learning_adapter", "FederatedState"),
    "MetaLearningMetrics": ("meta_learning_adapter", "MetaLearningMetrics"),
    "LearningRateBounds": ("meta_learning_adapter", "LearningRateBounds"),
    "MetaLearningEnhancementAdapter": (
        "meta_learning_adapter",
        "MetaLearningEnhancementAdapter",
    ),
    "MetaLearningRecovery": ("meta_learning_recovery", "MetaLearningRecovery"),
    "Enhancementmode": ("metalearningenhancementsystem", "Enhancementmode"),
    "Systemintegrationstatus": (
        "metalearningenhancementsystem",
        "Systemintegrationstatus",
    ),
    "MetaLearningEnhancementsystem": (
        "metalearningenhancementsystem",
        "MetaLearningEnhancementsystem",
    ),
    "ContentType": ("plugin_learning_engine", "ContentType"),
    "UserLevel": ("plugin_learning_engine", "UserLevel"),
    "GenerationConfig": ("plugin_learning_engine", "GenerationConfig"),
    "PluginLearningEngine": ("plugin_learning_engine", "PluginLearningEngine"),
    "IdentityClient": ("service", "IdentityClient"),
    "LearningService": ("services", "LearningService"),
    "LearningType": ("system", "LearningType"),
    "LearningStrategy": ("system", "LearningStrategy"),
    "LearningEpisode": ("system", "LearningEpisode"),
    "MetaLearningResult": ("system", "MetaLearningResult"),
    "BaseMetaLearner": ("system", "BaseMetaLearner"),
    "ModelAgnosticMetaLearner": ("system", "ModelAgnosticMetaLearner"),
    "FewShotLearner": ("system", "FewShotLearner"),
    "ContinualLearner": ("system", "ContinualLearner"),
    "AdvancedLearningSystem": ("system", "AdvancedLearningSystem"),
    "LearningStyle": ("tutor", "LearningStyle"),
    "DifficultyLevel": ("tutor", "DifficultyLevel"),
    "TutorMessageType": ("tutor", "TutorMessageType"),
    "LearningObjective": ("tutor", "LearningObjective"),
    "TutorMessage": ("tutor", "TutorMessage"),
    "LearningSession": ("tutor", "LearningSession"),
    "TutorEngine": ("tutor", "TutorEngine"),
    "Config": ("tutor", "Config"),
    "TestTutorLearningEngine": ("tutor_learning_engine", "TestTutorLearningEngine"),
    "UserInteraction": ("usage_learning", "UserInteraction"),
    "InteractionPattern": ("usage_learning", "InteractionPattern"),
    "UsageBasedLearning": ("usage_learning", "UsageBasedLearning"),
}

# Function registry
_FUNCTION_REGISTRY = {
    "sparse_encode": ("_dict_learning", "sparse_encode"),
    "dict_learning_online": ("_dict_learning", "dict_learning_online"),
    "dict_learning": ("_dict_learning", "dict_learning"),
    "transform": ("_dict_learning", "transform"),
    "inverse_transform": ("_dict_learning", "inverse_transform"),
    "fit": ("_dict_learning", "fit"),
    "n_components_": ("_dict_learning", "n_components_"),
    "n_features_in_": ("_dict_learning", "n_features_in_"),
    "fit_transform": ("_dict_learning", "fit_transform"),
    "partial_fit": ("_dict_learning", "partial_fit"),
    "optimize_learning_approach": (
        "adaptive_meta_learning",
        "optimize_learning_approach",
    ),
    "generate_learning_report": ("adaptive_meta_learning", "generate_learning_report"),
    "demo_meta_learning": ("adaptive_meta_learning", "demo_meta_learning"),
    "fetch_narration_entries": (
        "aid.dream_engine.narration_controller",
        "fetch_narration_entries",
    ),
    "load_user_settings": (
        "aid.dream_engine.narration_controller",
        "load_user_settings",
    ),
    "filter_narration_queue": (
        "aid.dream_engine.narration_controller",
        "filter_narration_queue",
    ),
    "load_reflex": ("embodied_thought.generative_reflex", "load_reflex"),
    "generate_response": ("embodied_thought.generative_reflex", "generate_response"),
    "incorporate_experience": ("exponential_learning", "incorporate_experience"),
    "initialize_lukhas_federated_learning": (
        "federated_learning_system",
        "initialize_lukhas_federated_learning",
    ),
    "get_system_status": ("federated_learning_system", "get_system_status"),
    "optimize_learning_approach": (
        "federated_meta_learning",
        "optimize_learning_approach",
    ),
    "generate_learning_report": ("federated_meta_learning", "generate_learning_report"),
    "get_learning_gateway": ("learning_gateway", "get_learning_gateway"),
    "get_learning_hub": ("learning_hub", "get_learning_hub"),
    "register_service": ("learning_hub", "register_service"),
    "get_service": ("learning_hub", "get_service"),
    "register_event_handler": ("learning_hub", "register_event_handler"),
    "register_learning_feedback": ("learning_hub", "register_learning_feedback"),
    "reset_learning_metrics": ("learning_hub", "reset_learning_metrics"),
    "generate_interface": (
        "meta_adaptive.adaptive_interface_generator",
        "generate_interface",
    ),
    "update_with_gradients": ("meta_adaptive.meta_learning", "update_with_gradients"),
    "get_parameters": ("meta_adaptive.meta_learning", "get_parameters"),
    "serialize": ("meta_adaptive.meta_learning", "serialize"),
    "deserialize": ("meta_adaptive.meta_learning", "deserialize"),
    "register_model": ("meta_adaptive.meta_learning", "register_model"),
    "get_model": ("meta_adaptive.meta_learning", "get_model"),
    "contribute_gradients": ("meta_adaptive.meta_learning", "contribute_gradients"),
    "save_model": ("meta_adaptive.meta_learning", "save_model"),
    "load_models": ("meta_adaptive.meta_learning", "load_models"),
    "get_client_status": ("meta_adaptive.meta_learning", "get_client_status"),
    "log_interaction": ("meta_adaptive.meta_learning", "log_interaction"),
    "reflect": ("meta_adaptive.meta_learning", "reflect"),
    "get_status_report": ("meta_adaptive.meta_learning", "get_status_report"),
    "optimize_learning_approach": (
        "meta_adaptive.meta_learning",
        "optimize_learning_approach",
    ),
    "generate_learning_report": (
        "meta_adaptive.meta_learning",
        "generate_learning_report",
    ),
    "get_federated_model": ("meta_adaptive.meta_learning", "get_federated_model"),
    "trigger_reflection": ("meta_adaptive.meta_learning", "trigger_reflection"),
    "incorporate_feedback": ("meta_learning", "incorporate_feedback"),
    "enhance_meta_learning_with_federation": (
        "meta_learning.federated_integration",
        "enhance_meta_learning_with_federation",
    ),
    "integrate_with_enhancement_system": (
        "meta_learning.federated_integration",
        "integrate_with_enhancement_system",
    ),
    "register_node": ("meta_learning.federated_integration", "register_node"),
    "share_learning_insight": (
        "meta_learning.federated_integration",
        "share_learning_insight",
    ),
    "receive_federation_updates": (
        "meta_learning.federated_integration",
        "receive_federation_updates",
    ),
    "coordinate_learning_rates": (
        "meta_learning.federated_integration",
        "coordinate_learning_rates",
    ),
    "enhance_symbolic_reasoning_federation": (
        "meta_learning.federated_integration",
        "enhance_symbolic_reasoning_federation",
    ),
    "synchronize_federation": (
        "meta_learning.federated_integration",
        "synchronize_federation",
    ),
    "get_federation_status": (
        "meta_learning.federated_integration",
        "get_federation_status",
    ),
    "enhance_existing_meta_learning_system": (
        "meta_learning.federated_integration",
        "enhance_existing_meta_learning_system",
    ),
    "create_integrated_symbolic_feedback_system": (
        "meta_learning.symbolic_feedback",
        "create_integrated_symbolic_feedback_system",
    ),
    "simulate_intent_node_integration": (
        "meta_learning.symbolic_feedback",
        "simulate_intent_node_integration",
    ),
    "log_intent_node_interaction": (
        "meta_learning.symbolic_feedback",
        "log_intent_node_interaction",
    ),
    "log_memoria_snapshot": ("meta_learning.symbolic_feedback", "log_memoria_snapshot"),
    "log_dream_replay": ("meta_learning.symbolic_feedback", "log_dream_replay"),
    "create_symbolic_feedback_loop": (
        "meta_learning.symbolic_feedback",
        "create_symbolic_feedback_loop",
    ),
    "execute_symbolic_rehearsal": (
        "meta_learning.symbolic_feedback",
        "execute_symbolic_rehearsal",
    ),
    "get_optimization_insights": (
        "meta_learning.symbolic_feedback",
        "get_optimization_insights",
    ),
    "main": ("meta_learning_recovery", "main"),
    "explore_meta_learning_directory": (
        "meta_learning_recovery",
        "explore_meta_learning_directory",
    ),
    "convert_to_lukhas_format": ("meta_learning_recovery", "convert_to_lukhas_format"),
    "determine_target_directory": (
        "meta_learning_recovery",
        "determine_target_directory",
    ),
    "recover_meta_learning_components": (
        "meta_learning_recovery",
        "recover_meta_learning_components",
    ),
    "execute_recovery": ("meta_learning_recovery", "execute_recovery"),
    "get_optimal_complexity": ("plugin_learning_engine", "get_optimal_complexity"),
    "learn_from_data": ("service", "learn_from_data"),
    "adapt_behavior": ("service", "adapt_behavior"),
    "synthesize_knowledge": ("service", "synthesize_knowledge"),
    "transfer_learning": ("service", "transfer_learning"),
    "get_learning_metrics": ("service", "get_learning_metrics"),
    "verify_user_access": ("service", "verify_user_access"),
    "check_consent": ("service", "check_consent"),
    "log_activity": ("service", "log_activity"),
    "create_learning_service": ("services", "create_learning_service"),
    "process_user_input": ("systems.core_system", "process_user_input"),
    "manage_voice_handoff": ("systems.duet_conductor", "manage_voice_handoff"),
    "interpret_intent": ("systems.intent_language", "interpret_intent"),
    "log_interpretation": ("systems.intent_language", "log_interpretation"),
    "speak": ("systems.symbolic_voice_loop", "speak"),
    "reflect_with_lukhas": ("systems.symbolic_voice_loop", "reflect_with_lukhas"),
    "listen_and_log_feedback": (
        "systems.symbolic_voice_loop",
        "listen_and_log_feedback",
    ),
    "generate_dream_outcomes": (
        "systems.symbolic_voice_loop",
        "generate_dream_outcomes",
    ),
    "lukhas_emotional_response": (
        "systems.symbolic_voice_loop",
        "lukhas_emotional_response",
    ),
    "synthesize_voice": ("systems.voice_duet", "synthesize_voice"),
    "skg": ("tutor_learning_engine", "skg"),
    "tutor_engine": ("tutor_learning_engine", "tutor_engine"),
    "sample_config": ("tutor_learning_engine", "sample_config"),
    "update": ("usage_learning", "update"),
    "record_interaction": ("usage_learning", "record_interaction"),
    "identify_patterns": ("usage_learning", "identify_patterns"),
    "update_user_preferences": ("usage_learning", "update_user_preferences"),
    "get_document_effectiveness": ("usage_learning", "get_document_effectiveness"),
    "get_popular_sequences": ("usage_learning", "get_popular_sequences"),
    "recommend_next_docs": ("usage_learning", "recommend_next_docs"),
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
    "AdaptiveMetaLearningSystem",
    "DictionaryLearning",
    "ExponentialLearningSystem",
    "FederatedLearningColony",
    "FederatedLearningManager",
    "FederatedLearningManager",
    "FederatedModel",
    "GenerativeReflex",
    "LearningAgent",
    "LearningGateway",
    "LearningGatewayInterface",
    "LearningRequest",
    "LearningResponse",
    "LukhasFederatedLearningManager",
    "LukhasFederatedModel",
    "MetaLearningSystem",
    "MiniBatchDictionaryLearning",
    "ReflectiveIntrospectionSystem",
    "SparseCoder",
    "_BaseSparseCoding",
]

# System metadata
__system__ = "learning"
__total_entities__ = 220
__classes__ = 79
__functions__ = 141
