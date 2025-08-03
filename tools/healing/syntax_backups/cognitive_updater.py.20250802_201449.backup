"""
+===========================================================================+
| MODULE: Cognitive Updater                                           |
| DESCRIPTION: Main cognitive state of LUKHAS instance.                |
|                                                                         |
| FUNCTIONALITY: Object-oriented architecture with modular design     |
| IMPLEMENTATION: Structured data handling * Professional logging     |
| INTEGRATION: Multi-Platform AI Architecture                        |
+===========================================================================+

"Enhancing beauty while adding sophistication" - LUKHAS Systems 2025
"Enhancing beauty while adding sophistication" - lukhas Systems 2025


"""

LUKHAS AI System - Function Library
File: cognitive_updater.py
Path: LUKHAS/core/symbolic/modules/cognitive_updater.py
Created: "2025-06-05 11:43:39"
Author: LUKHAS AI Team
Version: 1.0
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Advanced Cognitive Architecture for Artificial General Intelligence
Copyright (c) 2025 LUKHAS AI Research. All rights reserved.
Licensed under the LUKHAS Core License - see LICENSE.md for details.
lukhas AI System - Function Library
File: cognitive_updater.py
Path: lukhas/core/symbolic/modules/cognitive_updater.py
Created: "2025-06-05 11:43:39"
Author: lukhas AI Team
Version: 1.0
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Advanced Cognitive Architecture for Artificial General Intelligence
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""


"""
Handles the updating and adaptation of LUKHAS's cognitive models,
Handles the updating and adaptation of LUKHAS's cognitive models,
including cognitive analysis like dissonance detection, intent inference, and episodic recall.
"""
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import json
import logging # Added logging
import os # Added for path manipulation

# Assuming prot2 is in PYTHONPATH or accessible
# from prot2.CORE.identity.Λ_lambda_id_manager import Identity # For type hinting
# from prot2.CORE.identity.lukhas_lambda_id_manager import Identity # For type hinting
from prot2.CORE.memory_learning.memory_manager import MemoryManager, MemoryType # For type hinting and usage

# Import components from cognitive directory
from prot2.CORE.cognitive.meta_learning import MetaLearningSystem # For reflection and federated learning
# Note: MetaLearningSystem itself contains FederatedLearningManager and ReflectiveIntrospectionSystem

logger = logging.getLogger(__name__) # Added logger

class CognitiveUpdater:
    """
    Manages the cognitive analysis and adaptive learning processes for LUKHAS.
    Manages the cognitive analysis and adaptive learning processes for LUKHAS.
    It uses historical interaction data and reflective introspection to update
    cognitive models and strategies.
    """

    def __init__(self, identity: Any, memory_manager: MemoryManager, meta_learning_storage_path: Optional[str] = None): # Added meta_learning_storage_path
        """
        Initializes the CognitiveUpdater.

        Args:
            identity: The identity of the LUKHAS instance.
            identity: The identity of the LUKHAS instance.
            memory_manager: The memory manager instance for accessing historical data
                            and storing updated cognitive models.
            meta_learning_storage_path: Optional. Specific path for MetaLearningSystem's federated models.
        """
        self.Λ_lambda_identity = identity
        self.memory_manager = memory_manager
        self.log_prefix = "🧠 [CognitiveUpdater]"
        logger.info(f"{self.log_prefix} Initializing with LUKHAS ID: {identity.id}")
        self.lukhas_lambda_identity = identity
        self.memory_manager = memory_manager
        self.log_prefix = "🧠 [CognitiveUpdater]"
        logger.info(f"{self.log_prefix} Initializing with LUKHAS ID: {identity.id}")

        # Configure storage path for MetaLearningSystem's federated models
        federated_models_path = None
        if meta_learning_storage_path:
            federated_models_path = meta_learning_storage_path
            logger.info(f"{self.log_prefix} Using provided federated_storage_path: {federated_models_path}")
        elif hasattr(self.memory_manager, 'storage_path') and self.memory_manager.storage_path and os.path.isdir(self.memory_manager.storage_path):
            federated_models_path = os.path.join(self.memory_manager.storage_path, "federated_models")
            logger.info(f"{self.log_prefix} Derived federated_storage_path from MemoryManager: {federated_models_path}")
        else:
            # Let MetaLearningSystem use its default path or handle it internally
            logger.info(f"{self.log_prefix} No specific federated_storage_path provided or derivable. MetaLearningSystem will use its default.")
            # MetaLearningSystem's default is os.path.join(os.getcwd(), "federated_models")

        meta_config = {}
        if federated_models_path:
            meta_config["federated_storage_path"] = federated_models_path

        self.meta_learning_system = MetaLearningSystem(config=meta_config)
        logger.info(f"{self.log_prefix} MetaLearningSystem initialized. Federated models storage: {self.meta_learning_system.federated_learning.storage_dir}")

        # Internal state for current cognitive model - simplified for now
        self._current_cognitive_state = {
            "last_update_timestamp": None,
            "adaptive_parameters": {"learning_rate": 0.01, "exploration_bias": 0.1, "adaptation_step": 0.05}, # Added adaptation_step
            "dissonance_threshold": 0.7,
            "intent_stability": 0.9
        }
        # Load initial state if available from memory manager
        self._load_cognitive_state()

    def _load_cognitive_state(self):
        """Loads the latest cognitive state from the memory manager."""
        try:
            # Assuming cognitive state is stored with a specific key or type
            # For example, using owner_id=self.Λ_lambda_identity.id and MemoryType.COGNITIVE_MODEL
            # And a known key like "main_cognitive_state"
            state_data = self.memory_manager.retrieve(
                key="Λ_cognitive_state",
                owner_id=self.Λ_lambda_identity.id, # System's own cognitive state
            # For example, using owner_id=self.lukhas_lambda_identity.id and MemoryType.COGNITIVE_MODEL
            # And a known key like "main_cognitive_state"
            state_data = self.memory_manager.retrieve(
                key="lukhas_cognitive_state",
                owner_id=self.lukhas_lambda_identity.id, # System's own cognitive state
                memory_type=MemoryType.COGNITIVE_MODEL
            )
            if state_data:
                self._current_cognitive_state = state_data
                logger.info(f"{self.log_prefix} Loaded cognitive state. Last update: {state_data.get('last_update_timestamp')}")
            else:
                logger.info(f"{self.log_prefix} No existing cognitive state found. Using defaults.")
                # Store initial default state
                self._save_cognitive_state()
        except Exception as e:
            logger.error(f"{self.log_prefix} Error loading cognitive state: {e}", exc_info=True)
            # Fallback to default and try to save it
            self._save_cognitive_state()


    def _save_cognitive_state(self):
        """Saves the current cognitive state to the memory manager."""
        try:
            self._current_cognitive_state["last_update_timestamp"] = datetime.datetime.now().isoformat() # Ensure datetime is available
            self.memory_manager.store(
                key="Λ_cognitive_state",
                data=self._current_cognitive_state,
                memory_type=MemoryType.COGNITIVE_MODEL,
                owner_id=self.Λ_lambda_identity.id,
                description="Main cognitive state of LUKHAS instance."
                key="lukhas_cognitive_state",
                data=self._current_cognitive_state,
                memory_type=MemoryType.COGNITIVE_MODEL,
                owner_id=self.lukhas_lambda_identity.id,
                description="Main cognitive state of LUKHAS instance."
            )
            logger.info(f"{self.log_prefix} Saved cognitive state.")
        except Exception as e:
            logger.error(f"{self.log_prefix} Error saving cognitive state: {e}", exc_info=True)

    def get_current_cognitive_state(self) -> Dict[str, Any]:
        """
        Retrieves the current cognitive state of LUKHAS.
        Retrieves the current cognitive state of LUKHAS.
        This state can include learned parameters, model versions, adaptation strategies, etc.
        """
        # Potentially enrich with dynamic info from meta_learning_system if needed
        # For now, returns the managed _current_cognitive_state
        logger.debug(f"{self.log_prefix} Retrieving current cognitive state.")
        return self._current_cognitive_state.copy() # Return a copy

    # --- Internalized Analysis Functions ---
    def _detect_dissonance(self, memory_log: List[Dict[str, Any]]) -> List[Tuple[Tuple[str, str], str, str]]:
        """Scans for contradictory ethical decisions in the memory log."""
        logger.info(f"{self.log_prefix} [Dissonance] Scanning for contradictory ethical decisions...")
        seen = {}
        conflicts = []
        for entry in memory_log:
            # Ensure 'action' and 'evaluation' keys exist, provide defaults if not
            action = entry.get("action", "unknown_action")
            evaluation = entry.get("evaluation", "unknown_evaluation")
            parameters_str = str(entry.get("parameters", {}))

            key = (action, parameters_str)
            if key in seen and seen[key] != evaluation:
                conflicts.append((key, seen[key], evaluation))
            seen[key] = evaluation

        if conflicts:
            logger.warning(f"{self.log_prefix} [Dissonance] Conflicts detected: {conflicts}")
        else:
            logger.info(f"{self.log_prefix} [Dissonance] No dissonance found.")
        return conflicts

    def _infer_intent(self, memory_log: List[Dict[str, Any]]) -> str:
        """Analyzes the decision trend from the memory log."""
        logger.info(f"{self.log_prefix} [Intent] Analyzing decision trend...")
        if not memory_log:
            logger.info(f"{self.log_prefix} [Intent] No decision data in memory_log.")
            return "UNKNOWN"

        evaluations = [entry.get("evaluation") for entry in memory_log if entry.get("evaluation")]
        if not evaluations:
            logger.info(f"{self.log_prefix} [Intent] No evaluations found in memory_log entries.")
            return "UNKNOWN"

        trend = Counter(evaluations)
        pass_count = trend.get("PASS", 0)
        collapse_count = trend.get("COLLAPSE", 0)
        logger.info(f"{self.log_prefix} [Intent] Evaluation counts - PASS: {pass_count}, COLLAPSE: {collapse_count}")

        if pass_count > collapse_count:
            return "INCLINED_TO_ACCEPT"
        elif collapse_count > pass_count:
            return "INCLINED_TO_REJECT"
        else:
            return "BALANCED"

    def _recall_episodes(self, memory_log: List[Dict[str, Any]], target_action_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Replays historical decisions related to a target action."""
        logger.info(f"{self.log_prefix} [Recall] Replaying moral history for given action...")
        target_action_name = target_action_details.get("action")
        if not target_action_name:
            logger.warning(f"{self.log_prefix} [Recall] Target action name not provided.")
            return []

        history = [entry for entry in memory_log if entry.get("action") == target_action_name]
        if history:
            logger.info(f"{self.log_prefix} [Recall] Found {len(history)} episodes for action '{target_action_name}'.")
            # for i, event in enumerate(history): # Avoid verbose logging here, can be in debug
            #     logger.debug(f"  [Episode {i+1}] {json.dumps(event, indent=2)}")
        else:
            logger.info(f"{self.log_prefix} [Recall] No episodes found for action '{target_action_name}'.")
        return history

    def _perform_model_adaptation(self, interaction_details: Dict[str, Any], analysis_results: Dict[str, Any], historical_log: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Updates LUKHAS's cognitive models based on the interaction, analysis, and historical context.
        Updates LUKHAS's cognitive models based on the interaction, analysis, and historical context.
        This now leverages the MetaLearningSystem for reflection and federated updates.
        """
        user_sid = interaction_details.get('user_id', 'unknown_user')
        user_input_preview = str(interaction_details.get('user_input', ''))[:50]
        logger.info(f"{self.log_prefix} [Adaptation] Updating models for User: {user_sid}, Input: '{user_input_preview}...'")
        logger.info(f"{self.log_prefix} [Adaptation] Analysis received: Conflicts: {len(analysis_results.get('conflicts', []))}, Trend: {analysis_results.get('intent_trend', 'N/A')}, Recalled: {len(analysis_results.get('recall_history', []))} episodes.")

        adaptation_report = {
            "summary": "No adaptation performed yet.",
            "changes_made": [],
            "insights_from_reflection": [],
            "federated_contributions": []
        }

        # 1. Log interaction with ReflectiveIntrospectionSystem (part of MetaLearningSystem)
        reflection_interaction_data = {
            "interaction_id": interaction_details.get("session_id", interaction_details.get("timestamp")),
            "user_id": user_sid,
            "input_type": "text_query",
            "input_content": interaction_details.get("user_input"),
            "timestamp": interaction_details.get("timestamp"),
            "outcome": interaction_details.get("status"),
            "response_quality": None,
            "metrics": {
                "dissonance_events": len(analysis_results.get("conflicts", [])),
                "governance_compliant": interaction_details.get("governance_report", {}).get("compliant", True),
            },
            "cognitive_analysis": analysis_results,
            "current_cognitive_params": self._current_cognitive_state.get("adaptive_parameters", {}).copy()
        }
        self.meta_learning_system.reflective_system.log_interaction(reflection_interaction_data)
        logger.info(f"{self.log_prefix} [Adaptation] Logged interaction with ReflectiveIntrospectionSystem.")

        # 2. Trigger reflection and get insights/improvements
        reflection_output = self.meta_learning_system.reflective_system.reflect()
        adaptation_report["insights_from_reflection"] = reflection_output.get("insights", [])
        logger.info(f"{self.log_prefix} [Adaptation] Reflection cycle processed. Insights: {len(reflection_output.get('insights', []))}, Improvements: {len(reflection_output.get('improvements', []))}")

        # 3. Use insights and improvements from reflection to adjust cognitive parameters or models
        improvements_proposed = reflection_output.get("improvements", [])
        adaptation_step = self._current_cognitive_state.get("adaptive_parameters", {}).get("adaptation_step", 0.05)

        if improvements_proposed:
            logger.info(f"{self.log_prefix} [Adaptation] Processing {len(improvements_proposed)} proposed improvements.")
            for plan in improvements_proposed:
                change_desc = f"Processed improvement plan: ID={plan.get('id')}, Type={plan.get('type')}, Desc={plan.get('description')}"
                adaptation_report["changes_made"].append(change_desc)
                logger.info(f"{self.log_prefix} [Adaptation] {change_desc}")

                # Example: Adjusting parameters based on improvement plans
                if plan.get("type") == "performance_optimization":
                    target_param = plan.get("target")
                    if target_param == "dissonance_threshold" and target_param in self._current_cognitive_state:
                        # Example: If insights suggest dissonance is problematic, adjust threshold
                        # This is a simplified adjustment logic.
                        original_value = self._current_cognitive_state[target_param]
                        # Assuming higher trend in dissonance means we need to be more sensitive (lower threshold)
                        # Or if an insight specifically points to issues with current threshold.
                        # For now, a generic adjustment if this plan is proposed.
                        self._current_cognitive_state[target_param] = max(0.1, original_value - adaptation_step) # Decrease slightly
                        change_desc_detail = f"Adjusted '{target_param}' from {original_value:.3f} to {self._current_cognitive_state[target_param]:.3f} based on improvement plan."
                        adaptation_report["changes_made"].append(change_desc_detail)
                        logger.info(f"{self.log_prefix} [Adaptation] {change_desc_detail}")

                    # Could add more specific parameter adjustments here based on plan['target']
                    # For instance, if plan.get("target") in self._current_cognitive_state["adaptive_parameters"]:
                    #    self._current_cognitive_state["adaptive_parameters"][target_param] *= (1 + adaptation_step) # or some other logic

                # Further logic to act on other types of improvement plans can be added here.
                # e.g., if plan suggests updating a federated model, set a flag or prepare data.

            self._save_cognitive_state() # Save updated state after parameter adjustments
            adaptation_report["summary"] = "Cognitive parameters potentially adapted based on reflection."
        else:
            adaptation_report["summary"] = "No new improvement plans from current reflection cycle."
            logger.info(f"{self.log_prefix} [Adaptation] {adaptation_report['summary']}")

        # 4. Contribute to Federated Models (if applicable)
        # This could be triggered by specific improvement plans or other conditions.
        # For demonstration, let's attempt a contribution for a general "cognitive_style" model.

        # Iterate over known federated models that this system might influence
        # These model_ids are defined in MetaLearningSystem._register_core_models()
        # e.g., "user_preferences", "interface_adaptation", "cognitive_style", "episodic_memories"
        models_to_potentially_update = ["cognitive_style", "user_preferences"]

        for model_id in models_to_potentially_update:
            if model_id in self.meta_learning_system.federated_learning.models:
                logger.info(f"{self.log_prefix} [Adaptation] Considering contribution to federated model: {model_id}")
                # Placeholder: In a real scenario, gradients would be derived from local learning/adaptation
                gradients = self._generate_model_update_contribution(
                    model_id=model_id,
                    interaction_details=interaction_details,
                    analysis_results=analysis_results,
                    current_cognitive_state=self._current_cognitive_state
                )

                if gradients:
                    try:
                        success = self.meta_learning_system.federated_learning.contribute_gradients(
                            model_id=model_id,
                            client_id=self.Λ_lambda_identity.id,
                            client_id=self.lukhas_lambda_identity.id,
                            gradients=gradients,
                            metrics={"local_confidence": 0.75} # Example metrics
                        )
                        if success:
                            contrib_desc = f"Contributed gradients to federated model: {model_id}."
                            adaptation_report["federated_contributions"].append({"model_id": model_id, "status": "success"})
                            logger.info(f"{self.log_prefix} [Adaptation] {contrib_desc}")
                            adaptation_report["changes_made"].append(contrib_desc)
                        else:
                            contrib_desc = f"Failed to contribute gradients to federated model: {model_id}."
                            adaptation_report["federated_contributions"].append({"model_id": model_id, "status": "failed", "reason": "Contribution rejected by manager"})
                            logger.warning(f"{self.log_prefix} [Adaptation] {contrib_desc}")
                    except Exception as e:
                        contrib_desc = f"Error contributing gradients to federated model {model_id}: {e}"
                        adaptation_report["federated_contributions"].append({"model_id": model_id, "status": "error", "reason": str(e)})
                        logger.error(f"{self.log_prefix} [Adaptation] {contrib_desc}", exc_info=True)
                else:
                    logger.info(f"{self.log_prefix} [Adaptation] No gradients generated for federated model: {model_id} in this cycle.")
            else:
                logger.warning(f"{self.log_prefix} [Adaptation] Federated model_id '{model_id}' not found in MetaLearningSystem for potential update.")


        if adaptation_report["changes_made"] or adaptation_report["federated_contributions"]:
             adaptation_report["summary"] = "Cognitive update cycle completed with adaptations and/or federated contributions."
        elif not improvements_proposed : # if no improvements were proposed and no other changes made
             adaptation_report["summary"] = "Cognitive update cycle completed. No new improvement plans or federated contributions in this cycle."


        return adaptation_report

    def _generate_model_update_contribution(self, model_id: str, interaction_details: Dict, analysis_results: Dict, current_cognitive_state: Dict) -> Optional[Dict]:
        """
        Placeholder method to generate gradients or updates for a federated model.
        In a real implementation, this would involve local model training or heuristic-based update calculation.

        Args:
            model_id: The ID of the federated model to generate an update for.
            interaction_details: Details of the current interaction.
            analysis_results: Results from cognitive analysis.
            current_cognitive_state: The current cognitive state of LUKHAS.
            current_cognitive_state: The current cognitive state of LUKHAS.

        Returns:
            A dictionary representing gradients or updates, or None if no update is generated.
        """
        logger.debug(f"{self.log_prefix} [Federated] Generating dummy update contribution for model: {model_id}")

        # Example: For 'cognitive_style' model, if intent_trend shows strong inclination,
        # suggest a slight shift in 'reasoning_weights'.
        # Parameters for 'cognitive_style' in MetaLearningSystem: {"reasoning_weights": {"analytical": 0.5, "intuitive": 0.5}}
        if model_id == "cognitive_style":
            intent_trend = analysis_results.get("intent_trend")
            # This is a very simplistic heuristic
            if intent_trend == "INCLINED_TO_ACCEPT": # Assume this correlates with 'intuitive'
                return {"reasoning_weights.intuitive": 0.01, "reasoning_weights.analytical": -0.01} # Small gradient
            elif intent_trend == "INCLINED_TO_REJECT": # Assume this correlates with 'analytical'
                return {"reasoning_weights.intuitive": -0.01, "reasoning_weights.analytical": 0.01}

        elif model_id == "user_preferences":
            # Example: If a user interaction was particularly positive or negative (needs metric)
            # and related to a modality (e.g. voice, text).
            # Parameters: {"attention_weights": {"visual": 0.5, "auditory": 0.3, "textual": 0.2}}
            # This is too complex for a simple placeholder without more interaction data.
            pass

        # By default, no contribution for other models or if conditions not met
        return None

    def analyze_and_update_cognition(
        self,
        interaction_details: Dict[str, Any],
        Λ_lambda_identity: Any, # Pass current operational identity
        lukhas_lambda_identity: Any, # Pass current operational identity
        historical_log: List[Dict[str, Any]], # Pass the historical log from advanced_symbolic_loop
        target_action_for_recall: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Performs cognitive analysis and triggers cognitive model updates.
        Uses MemoryManager to fetch necessary historical data.
        """
        user_input_preview = str(interaction_details.get('user_input', ''))[:50]
        logger.info(f"{self.log_prefix} Starting cognitive analysis and update for interaction: '{user_input_preview}...'")

        # Historical log is now passed directly by advanced_symbolic_loop
        # memory_log = self.memory_manager.get_interaction_history(
        #     memory_type_filter=MemoryType.CONTEXT, # Or a more specific type for cognitive analysis
        #     # Consider filters like owner_id_filter=interaction_details.get("user_id") for user-specific context,
        #     # or None for global context. For general cognitive update, global might be better.
        #     limit=1000 # Example limit
        # )
        # logger.info(f"{self.log_prefix} Retrieved {len(memory_log)} entries from interaction history for analysis.")
        memory_log = historical_log # Use the passed log

        # 1. Perform Cognitive Analyses
        conflicts = self._detect_dissonance(memory_log)
        intent_trend = self._infer_intent(memory_log)

        recall_history = []
        if target_action_for_recall: # This might be part of interaction_details or a separate flow
            recall_history = self._recall_episodes(memory_log, target_action_for_recall)
        else:
            logger.info(f"{self.log_prefix} [Recall] No target action provided for recall during this update cycle.")

        analysis_results = {
            "conflicts": conflicts,
            "intent_trend": intent_trend,
            "recall_history": recall_history,
            "log_length_analyzed": len(memory_log)
        }
        logger.info(f"{self.log_prefix} Analysis complete: Conflicts: {len(conflicts)}, Trend: {intent_trend}, Recalled: {len(recall_history)} episodes from {len(memory_log)} log entries.")

        # 2. Perform Model Adaptation based on interaction and analysis
        adaptation_report = self._perform_model_adaptation(
            interaction_details=interaction_details,
            analysis_results=analysis_results,
            historical_log=memory_log # Pass historical log for context if needed by adaptation
        )

        final_report = {
            "cognitive_analysis": analysis_results,
            "adaptation_outcomes": adaptation_report,
            "summary": f"Cognitive update cycle completed. {adaptation_report['summary']}"
        }
        logger.info(f"{self.log_prefix} {final_report['summary']}")

        return final_report

# Keep the __main__ block for testing if desired, but update it to use the class.
if __name__ == '__main__':
    import datetime # Ensure datetime is imported for the main block
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Mock Identity and MemoryManager for testing
    class MockIdentity:
        def __init__(self, id, version):
            self.id = id
            self.version = version

    class MockMemoryManager:
        def __init__(self):
            self.storage = {}
            self.interaction_history_data = []

        def get_interaction_history(self, memory_type_filter=None, owner_id_filter=None, limit=None) -> List[Dict[str, Any]]:
            logger.info(f"MockMemoryManager.get_interaction_history called with filter: {memory_type_filter}, owner: {owner_id_filter}, limit: {limit}")
            return self.interaction_history_data

        def store(self, key: str, data: Any, memory_type: MemoryType, owner_id: str, description: Optional[str] = None, related_to: Optional[List[str]] = None):
            logger.info(f"MockMemoryManager.store: key={key}, type={memory_type}, owner={owner_id}")
            self.storage[(key, owner_id, memory_type)] = data

        def retrieve(self, key: str, owner_id: str, memory_type: MemoryType) -> Optional[Any]:
            logger.info(f"MockMemoryManager.retrieve: key={key}, type={memory_type}, owner={owner_id}")
            return self.storage.get((key, owner_id, memory_type))

        def update_memory(self, key: str, data: Any, owner_id: Optional[str] = None, memory_type: Optional[MemoryType] = None):
             logger.info(f"MockMemoryManager.update_memory: key={key}")
             # Simplified: assume key is enough to find and update, or it stores if not found
             # This mock needs to be more aligned with actual MemoryManager for robust testing
             # For now, let's just simulate storing it again.
             # Find the entry to update. This is a simplification.
             found_key = None
             for k_tuple in self.storage.keys():
                 if k_tuple[0] == key: # Assuming key is unique enough for this mock
                     found_key = k_tuple
                     break
             if found_key:
                 self.storage[found_key] = data
             else: # If not found, store it (simplification)
                  # Need owner_id and memory_type for new store. This part is tricky for a generic update mock.
                  # Let's assume it's updating an existing one or this mock needs more info.
                  # For the cognitive state, we know the details:
                  if key == "Λ_cognitive_state":
                  if key == "lukhas_cognitive_state":
                      self.store(key, data, MemoryType.COGNITIVE_MODEL, "mock_lukhas_system_id") # Assuming a system ID
                  else:
                      logger.warning(f"MockMemoryManager.update_memory: Cannot store new memory for key {key} without full details.")


    mock_identity = MockIdentity(id="mock_lukhas_system_id", version="0.1-mock")
    mock_memory_manager = MockMemoryManager()

    # Populate mock memory manager with some history
    mock_memory_manager.interaction_history_data = [
        {"action": "greet_user", "parameters": {"user_id": "123"}, "evaluation": "PASS", "timestamp": "2023-01-01T10:00:00Z", "user_input": "Hello"},
        {"action": "provide_info", "parameters": {"topic": "AI"}, "evaluation": "PASS", "timestamp": "2023-01-01T10:01:00Z", "user_input": "Tell me about AI"},
        {"action": "controversial_query", "parameters": {"query": "internal_secrets"}, "evaluation": "COLLAPSE", "timestamp": "2023-01-01T10:03:00Z", "user_input": "What are the secrets?"},
        {"action": "greet_user", "parameters": {"user_id": "123"}, "evaluation": "COLLAPSE", "timestamp": "2023-01-01T10:05:00Z", "user_input": "Hi again user 123"}, # Dissonance
    ]

    cognitive_updater_instance = CognitiveUpdater(identity=mock_identity, memory_manager=mock_memory_manager)

    sample_interaction_details = {
        "user_id": "test_user_789", # Changed from user_sid
        "user_input": "Can you greet user 123 again, please? And tell me about AI ethics.",
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": "session_xyz789",
        "governance_report": {"compliant": True}
    }

    sample_target_action_for_recall = {"action": "greet_user", "parameters": {"user_id": "123"}}

    print("--- Running CognitiveUpdater Class Test (with recall) ---")
    results_with_recall = cognitive_updater_instance.analyze_and_update_cognition(
        interaction_details=sample_interaction_details,
        Λ_lambda_identity=mock_identity,
        lukhas_lambda_identity=mock_identity,
        historical_log=mock_memory_manager.interaction_history_data, # Pass the log
        target_action_for_recall=sample_target_action_for_recall
    )
    print("\\n--- CognitiveUpdater Class Test Results (with recall) ---")
    print(json.dumps(results_with_recall, indent=2))

    print("\\n--- Current Cognitive State After Update ---")
    print(json.dumps(cognitive_updater_instance.get_current_cognitive_state(), indent=2))

    # Example of another interaction to see adaptation over time
    sample_interaction_details_2 = {
        "user_id": "test_user_789",
        "user_input": "Why did you collapse on the controversial query earlier?",
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": "session_abc123",
        "governance_report": {"compliant": True},
        "status": "completed"
    }
    print("\\n--- Running CognitiveUpdater Class Test (second interaction) ---")
    results_2 = cognitive_updater_instance.analyze_and_update_cognition(
        interaction_details=sample_interaction_details_2,
        Λ_lambda_identity=mock_identity,
        lukhas_lambda_identity=mock_identity,
        historical_log=mock_memory_manager.interaction_history_data # Pass the log
    )
    print("\\n--- CognitiveUpdater Class Test Results (second interaction) ---")
    print(json.dumps(results_2, indent=2))
    print("\\n--- Current Cognitive State After Second Update ---")
    print(json.dumps(cognitive_updater_instance.get_current_cognitive_state(), indent=2))








# Last Updated: 2025-06-05 09:37:28

# TECHNICAL IMPLEMENTATION: Neural network architectures with adaptive learning, Artificial intelligence with advanced cognitive modeling, Optimized algorithms for computational efficiency
# LUKHAS Systems 2025 www.lukhas.ai 2025
# lukhas Systems 2025 www.lukhas.ai 2025
