"""
lukhas AI System - Function Library
File: lukhas_core_integrator.py
Path: lukhas/core/orchestration/lukhas_core_integrator.py
Author: lukhas AI Team
This file is part of the LUKHAS (Logical Unified Knowledge Hyper-Adaptable System)
Copyright (c) 2025 lukhas AI Research. All rights reserved.
Licensed under the lukhas Core License - see LICENSE.md for details.
"""


from .dreams.dream_processor import DreamProcessor
from .cognitive.federated_learning import FederatedLearningManager
from .cognitive.meta_learning import MetaLearningSystem
import logging
import time
from typing import Dict, Any, List, Optional, Callable
import os
import json
from enum import Enum
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.FileHandler("Λ_core.log"), logging.StreamHandler()]
    handlers=[logging.FileHandler("lukhas_core.log"), logging.StreamHandler()]
)
logger = logging.getLogger("CoreIntegrator")

# Import brain integration
try:
    from core.brain_integration import BrainIntegration
    BRAIN_INTEGRATION_AVAILABLE = True
    logger.info("Brain Integration module loaded successfully")
except ImportError:
    logger.warning(
        "Could not import brain integration module. Advanced memory functions will be limited.")
    BRAIN_INTEGRATION_AVAILABLE = False


class AccessTier(Enum):
    """Access tier levels for Lukhas Awareness Protocol"""
    RESTRICTED = 0
    BASIC = 1
    STANDARD = 2
    ENHANCED = 3
    FULL = 4


class CoreMessageType(Enum):
    """Message types for core communication"""
    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"
    EVENT = "event"
    ALERT = "alert"
    STATUS = "status"


class CoreIntegrator:
    """Core integration hub for LUKHAS AI System
    """Core integration hub for LUKHAS AI System

    This class provides the central integration point for Lukhas core components,
    including voice, nodes, awareness protocol, and other modules.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Lukhas Core Integrator

        Args:
            config_path: Optional path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize core components
        self.components = {}
        self.message_handlers = {}
        self.event_subscribers = {}

        # Component status tracking
        self.component_status = {}

        # Awareness protocol integration
        self.awareness = None
        self.current_access_tier = AccessTier.RESTRICTED

        # System state
        self.system_state = {
            "started": time.time(),
            "last_activity": time.time(),
            "message_count": 0,
            "error_count": 0
        }

        # Initialize brain integration if available
        self.brain = None
        if BRAIN_INTEGRATION_AVAILABLE:
            try:
                logger.info("Initializing Brain Integration module...")
                self.brain = BrainIntegration(self, self.config.get("brain_config"))
                logger.info("Brain Integration module initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Brain Integration: {e}")

        # Initialize cognitive components
        self.meta_learner = MetaLearningSystem(self.config.get("meta_learning"))
        self.dream_processor = DreamProcessor(self.config.get("dream_processing"))

        # Track system state
        self.last_reflection = datetime.now()
        self.interaction_count = 0
        self.system_state = {
            "initialized_at": datetime.now().isoformat(),
            "status": "ready",
            "active_modules": [
                "meta_learning",
                "federated_learning",
                "reflective_introspection",
                "dream_processing"
            ]
        }

        logger.info("Lukhas Core Integrator initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use default"""
        default_config = {
            "component_paths": {
                "voice": "VOICE/voice_processor.py",
                "awareness": "AWARENESS/awareness_protocol.py",
                "node_manager": "NODES/node_manager.py",
                "brain": "CORE/brain_integration.py"
            },
            "logging": {
                "level": "INFO",
                "trace_enabled": True,
                "trace_path": "logs/symbolic_trace.jsonl"
            },
            "security": {
                "default_access_tier": "RESTRICTED",
                "tier_escalation_timeout": 300,  # 5 minutes
                "symbolic_trace_retention": 7     # 7 days
            },
            "brain_config": {
                "memory_consolidation_enabled": True,
                "emotion_mapping_enabled": True,
                "consolidation_interval_minutes": 60,
                "memory_path": "./memory_store"
            }
        }

        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for section in default_config:
                        if section in loaded_config:
                            default_config[section].update(loaded_config[section])
                        else:
                            loaded_config[section] = default_config[section]
                    return loaded_config
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
                logger.warning("Using default configuration")

        return default_config

    def register_component(self,
                          component_id: str,
                          component_instance: Any,
                          message_handler: Optional[Callable] = None) -> bool:
        """Register a component with the core integrator

        Args:
            component_id: Unique identifier for the component
            component_instance: The component instance
            message_handler: Optional function to handle messages for this component

        Returns:
            bool: True if registration was successful
        """
        if component_id in self.components:
            logger.warning(f"Component {component_id} already registered")
            return False

        self.components[component_id] = component_instance
        self.component_status[component_id] = {
            "registered_at": time.time(),
            "status": "registered",
            "last_activity": time.time(),
            "error_count": 0
        }

        # Register message handler if provided
        if message_handler:
            self.register_message_handler(component_id, message_handler)

        logger.info(f"Component {component_id} registered")
        return True

    def register_message_handler(self, component_id: str, handler: Callable) -> bool:
        """Register a message handler for a component

        Args:
            component_id: Component ID to handle messages for
            handler: Function to handle messages(takes message dict as param)

        Returns:
            bool: True if registration was successful
        """
        self.message_handlers[component_id] = handler
        return True

    def subscribe_to_events(self,
                          event_type: str,
                          callback: Callable,
                          component_id: Optional[str] = None) -> bool:
        """Subscribe to system events

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
            component_id: Optional component ID for tracking

        Returns:
            bool: True if subscription was successful
        """
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []

        self.event_subscribers[event_type].append({
            "callback": callback,
            "component_id": component_id
        })

        return True

    def send_message(self,
                    target_component: str,
                    message: Dict[str, Any],
                    source_component: Optional[str] = None,
                    message_type: CoreMessageType = CoreMessageType.COMMAND) -> Dict[str, Any]:
        """Send a message to a component

        Args:
            target_component: Component to send message to
            message: Message content
            source_component: Component sending the message
            message_type: Type of message

        Returns:
            Dict containing response or status
        """
        # Update system state
        self.system_state["message_count"] += 1
        self.system_state["last_activity"] = time.time()

        # Check if component exists
        if target_component not in self.components:
            logger.error(
                f"Cannot send message to unknown component: {target_component}")
            return {
                "status": "error",
                "error": f"Unknown component: {target_component}",
                "timestamp": time.time()
            }

        # Check access tier if awareness protocol is active
        if self.awareness and message_type == CoreMessageType.COMMAND:
            # Log this for audit purposes
            self._log_symbolic_trace({
                "action": "message_sent",
                "source": source_component,
                "target": target_component,
                "message_type": message_type.value,
                "access_tier": self.current_access_tier.name,
                "timestamp": time.time()
            })

            # Check if action is allowed at current access tier
            if not self._check_action_permitted(
    target_component, message, self.current_access_tier):
                logger.warning(
                    f"Action not permitted at access tier {self.current_access_tier.name}")
                return {
                    "status": "denied",
                    "error": f"Action not permitted at access tier {self.current_access_tier.name}",
                    "timestamp": time.time()
                }

        # Update component status
        self.component_status[target_component]["last_activity"] = time.time()

        # Prepare the message envelope
        message_envelope = {
            "content": message,
            "metadata": {
                "source": source_component,
                "timestamp": time.time(),
                "message_type": message_type.value,
                "message_id": f"{int(time.time() * 1000)}-{self.system_state['message_count']}"
            }
        }

        # Try to deliver using registered handler
        try:
            if target_component in self.message_handlers:
                response = self.message_handlers[target_component](message_envelope)
                return response

            # Otherwise, try to call a process_message method
            component = self.components[target_component]
            if hasattr(
    component,
    'process_message') and callable(
        getattr(
            component,
             'process_message')):
                response = component.process_message(message_envelope)
                return response

            # If no handler, log error
            logger.error(f"No message handler for component: {target_component}")
            self.component_status[target_component]["error_count"] += 1
            self.system_state["error_count"] += 1

            return {
                "status": "error",
                "error": "No message handler available",
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"Error sending message to {target_component}: {e}")
            self.component_status[target_component]["error_count"] += 1
            self.system_state["error_count"] += 1

            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }

    def broadcast_event(self,
                       event_type: str,
                       event_data: Dict[str, Any],
                       source_component: Optional[str] = None) -> int:
        """Broadcast an event to all subscribers

        Args:
            event_type: Type of event to broadcast
            event_data: Event data
            source_component: Component broadcasting the event

        Returns:
            int: Number of subscribers that received the event
        """
        if event_type not in self.event_subscribers:
            return 0

        event_envelope = {
            "event_type": event_type,
            "data": event_data,
            "metadata": {
                "source": source_component,
                "timestamp": time.time(),
                "event_id": f"evt-{int(time.time() * 1000)}"
            }
        }

        # Log event for awareness protocol
        self._log_symbolic_trace({
            "action": "event_broadcast",
            "event_type": event_type,
            "source": source_component,
            "timestamp": time.time()
        })

        # Deliver to subscribers
        delivery_count = 0
        for subscriber in self.event_subscribers[event_type]:
            try:
                subscriber["callback"](event_envelope)
                delivery_count += 1
            except Exception as e:
                logger.error(f"Error delivering event to subscriber: {e}")

                # Update error count if component is known
                if subscriber["component_id"] and subscriber["component_id"] in self.component_status:
                    self.component_status[subscriber["component_id"]
                        ]["error_count"] += 1

        return delivery_count

    def initialize_awareness_protocol(self, awareness_instance: Any = None) -> bool:
        """Initialize the Lukhas Awareness Protocol

        Args:
            awareness_instance: Optional pre - configured awareness instance

        Returns:
            bool: True if initialization was successful
        """
        try:
            # Use provided instance or try to create one
            if awareness_instance:
                self.awareness = awareness_instance
            else:
                # Import dynamically from the configured path
                awareness_path = self.config["component_paths"]["awareness"]
                module_path = awareness_path.replace("/", ".").replace(".py", "")

                try:
                    module = __import__(module_path, fromlist=["AwarenessProtocol"])
                    awareness_class = getattr(module, "AwarenessProtocol")
                    self.awareness = awareness_class()
                except ImportError:
                    logger.error(
                        f"Could not import awareness protocol from {module_path}")
                    return False

            # Register with core
            self.register_component("awareness", self.awareness)

            # Set initial access tier
            default_tier_name = self.config["security"]["default_access_tier"]
            self.current_access_tier = AccessTier[default_tier_name]

            # Set up bidirectional communication
            if hasattr(
    self.awareness,
    'register_core_callback') and callable(
        getattr(
            self.awareness,
             'register_core_callback')):
                self.awareness.register_core_callback(self.process_awareness_alert)

            # Connect brain with awareness protocol
            if self.brain and self.awareness:
                try:
                    # Pass awareness to brain for access control
                    self.brain.connect_awareness(self.awareness)
                    logger.info("Connected brain integration with awareness protocol")
                except Exception as e:
                    logger.error(f"Failed to connect brain with awareness: {e}")

            logger.info("Lukhas Awareness Protocol initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize awareness protocol: {e}")
            return False

    def process_awareness_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process alerts from the awareness protocol

        Args:
            alert_data: Alert information

        Returns:
            Dict with status information
        """
        alert_type = alert_data.get("alert_type")

        # Log the alert
        self._log_symbolic_trace({
            "action": "awareness_alert",
            "alert_type": alert_type,
            "timestamp": time.time(),
            "details": alert_data
        })

        # Handle different alert types
        if alert_type == "access_tier_change":
            new_tier_name = alert_data.get("new_tier")
            try:
                self.current_access_tier = AccessTier[new_tier_name]
                logger.info(f"Access tier changed to {new_tier_name}")
            except KeyError:
                logger.error(f"Invalid access tier: {new_tier_name}")

            # Also inform brain of access tier changes for memory access control
            if self.brain:
                try:
                    self.brain.update_access_tier(self.current_access_tier)
                    logger.debug(f"Updated brain access tier to {new_tier_name}")
                except Exception as e:
                    logger.error(f"Failed to update brain access tier: {e}")

        elif alert_type == "security_violation":
            # Broadcast security event
            self.broadcast_event("security_violation", alert_data, "awareness")
            logger.warning(
                f"Security violation detected: {alert_data.get('description')}")

        # Return status
        return {
            "status": "processed",
            "timestamp": time.time()
        }

    def _check_action_permitted(self,
                              target_component: str,
                              message: Dict[str, Any],
                              access_tier: AccessTier) -> bool:
        """Check if an action is permitted at the current access tier

        Args:
            target_component: Target component for the action
            message: Message content
            access_tier: Current access tier

        Returns:
            bool: True if action is permitted
        """
        # If awareness protocol is disabled, permit everything
        if not self.awareness:
            return True

        # Ask awareness protocol if available
        if hasattr(
    self.awareness,
    'check_permission') and callable(
        getattr(
            self.awareness,
             'check_permission')):
            return self.awareness.check_permission(
    target_component, message, access_tier.name)

        # Default permission checks
        if access_tier == AccessTier.RESTRICTED:
            # In restricted mode, only allow status queries and awareness interactions
            allowed_targets = ["awareness"]
            allowed_actions = ["status", "query", "auth"]

            action = message.get("action", "").lower()
            return target_component in allowed_targets or action in allowed_actions

        # For other tiers, implement appropriate logic
        # This is simplified and should be expanded based on your requirements
        return access_tier.value >= AccessTier.BASIC.value

    def _log_symbolic_trace(self, trace_data: Dict[str, Any]) -> None:
        """Log symbolic trace data for auditing

        Args:
            trace_data: Trace information to log
        """
        if not self.config["logging"]["trace_enabled"]:
            return

        # Ensure trace directory exists
        trace_path = self.config["logging"]["trace_path"]
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)

        # Add standard fields
        trace_data["system_time"] = time.time()

        # Write to trace file
        with open(trace_path, 'a') as f:
            f.write(json.dumps(trace_data) + '\n')

    def get_component_status(
        self, component_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of a specific component or all components

        Args:
            component_id: Optional component ID to check

        Returns:
            Dict with component status information
        """
        if component_id:
            if component_id not in self.component_status:
                return {"error": f"Unknown component: {component_id}"}
            return self.component_status[component_id]

        # Return all component statuses
        return self.component_status

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status

        Returns:
            Dict with system status information
        """
        status = self.system_state.copy()
        status["uptime"] = time.time() - status["started"]
        status["component_count"] = len(self.components)
        status["current_access_tier"] = self.current_access_tier.name

        # Add brain status if available
        if self.brain:
            try:
                brain_stats = self.send_message("brain", {"action": "get_stats"})
                if brain_stats and "stats" in brain_stats:
                    status["brain"] = brain_stats["stats"]
            except Exception as e:
                logger.error(f"Error getting brain stats: {e}")
                status["brain"] = {"error": str(e)}

        return status

    def process_input(self, input_data: Dict, context: Dict = None) -> Dict:
        """Process input through the integrated cognitive system"""
        context = context or {}
        self.interaction_count += 1

        # Stage 1: Meta-Learning Analysis
        learning_approach = self.meta_learner.optimize_learning_approach(
            context, input_data
        )

        # Stage 2: Apply Selected Strategy
        processed_result = self._apply_learning_strategy(
            learning_approach["strategy"],
            input_data,
            context
        )

        # Stage 3: Update Federated Models
        if processed_result.get("gradients"):
            self._update_federated_models(processed_result, context)

        # Stage 4: Trigger Reflection if needed
        if self._should_reflect():
            reflection_result = self.meta_learner.trigger_reflection()
            if reflection_result.get("requires_adaptation"):
                self._adapt_system(reflection_result)

        # Stage 5: Queue for Dream Processing
        self.dream_processor.queue_experience({
            "input": input_data,
            "context": context,
            "result": processed_result,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "result": processed_result,
            "strategy_used": learning_approach["strategy"],
            "system_status": self.get_status()
        }

    def _apply_learning_strategy(
        self,
        strategy: str,
        input_data: Dict,
        context: Dict
    ) -> Dict:
        """Apply the selected learning strategy to process input"""
        if strategy == "federated_learning":
            # Use federated models for processing
            relevant_model = self.meta_learner.get_federated_model(
                context.get("model_id", "default"),
                context.get("client_id", "system")
            )
            return self._process_with_model(input_data, relevant_model)

        elif strategy == "transfer_learning":
            # Apply transfer learning approach
            source_model = self.meta_learner.get_federated_model(
                "source_" + context.get("model_id", "default"),
                "transfer"
            )
            return self._adapt_and_apply_model(input_data, source_model)

        else:
            # Default to direct processing
            return {"processed": input_data, "strategy": "direct"}

    def _process_with_model(self, input_data: Dict, model: Optional[Dict]) -> Dict:
        """Process input using a federated model"""
        if not model:
            return {"processed": input_data, "strategy": "fallback"}

        # Apply model weights to process input
        weights = model.get("weights", {})
        return {
            "processed": input_data,
            "weights_applied": weights,
            "gradients": self._calculate_gradients(input_data, weights)
        }

    def _adapt_and_apply_model(
    self,
    input_data: Dict,
     source_model: Optional[Dict]) -> Dict:
        """Adapt and apply a source model to new data"""
        if not source_model:
            return {"processed": input_data, "strategy": "fallback"}

        # Adapt source model weights for new task
        adapted_weights = self._adapt_weights(
            source_model.get("weights", {}),
            input_data
        )

        return {
            "processed": input_data,
            "adapted_weights": adapted_weights,
            "original_model": source_model.get("model_id")
        }

    def _update_federated_models(self, result: Dict, context: Dict) -> None:
        """Update federated models with new gradient"""
        if "gradients" in result:
            self.meta_learner.federated_learning.contribute_gradients(
                model_id=context.get("model_id", "default"),
                client_id=context.get("client_id", "system"),
                gradients=result["gradients"]
            )

    def _should_reflect(self) -> bool:
        """Determine if system should trigger reflection"""
        return (
            self.interaction_count % 10 == 0  # Every 10 interactions
            or (datetime.now() - self.last_reflection).seconds > 1800  # or 30 minutes
        )

    def _adapt_system(self, reflection_result: Dict) -> None:
        """Adapt system based on reflection insight"""
        insights = reflection_result.get("insights", {})

        # Apply recommended parameter adjustments
        params = reflection_result.get("parameter_adjustments", {})
        if params:
            self.meta_learner.incorporate_feedback({
                "type": "self_reflection",
                "insights": insights,
                "parameter_adjustments": params
            })

        # Update system state
        self.system_state["last_adaptation"] = datetime.now().isoformat()
        self.system_state["adaptation_details"] = insights

    def get_status(self) -> Dict:
        """Get current system status and metric"""
        return {
            "system_state": self.system_state,
            "interaction_count": self.interaction_count,
            "active_models": list(
                self.meta_learner.federated_learning.models.keys()
            )
        }

    def _calculate_gradients(self, input_data: Dict, weights: Dict) -> Dict:
        """Calculate gradients for model update"""
        # This would implement actual gradient calculation
        return {"update_direction": 1, "magnitude": 0.1}

    def _adapt_weights(self, source_weights: Dict, target_data: Dict) -> Dict:
        """Adapt weights from source domain to target domain"""
        # This would implement actual domain adaptation
        return {k: v * 0.8 for k, v in source_weights.items()}







# Last Updated: 2025-06-05 09:37:28
