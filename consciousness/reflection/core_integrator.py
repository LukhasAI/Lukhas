# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: lukhas_core_integrator.py
# MODULE: core.advanced.brain.lukhas_core_integrator
# DESCRIPTION: Central integration hub for LUKHAS AGI System, managing components,
#              message routing, event subscription, and awareness protocol integration.
# DEPENDENCIES: logging, time, typing, os, json, enum, pathlib
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
# ΛORIGIN_AGENT: Jules-02
# ΛTASK_ID: 191
# ΛCOMMIT_WINDOW: pre-audit
# ΛAPPROVED_BY: Human Overseer (GRDM)

import logging
import time
from typing import Dict, Any, List, Optional, Callable, Union # Added Union
import os
import json
from enum import Enum
from pathlib import Path # Added Path

# Initialize logger for ΛTRACE

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


logger = logging.getLogger("ΛTRACE.core.advanced.brain.lukhas_core_integrator")
logger.info("ΛTRACE: Initializing lukhas_core_integrator module.")

# TODO: Refactor path-based import to standard package imports if possible.
# Attempt to import brain integration
BRAIN_INTEGRATION_AVAILABLE = False
LUKHASBrainIntegration = None # Placeholder
try:
    from orchestration.brain.integration.brain_integration import LUKHASBrainIntegration # This is a non-standard import
    BRAIN_INTEGRATION_AVAILABLE = True
    logger.info("ΛTRACE: Brain Integration module (LUKHASBrainIntegration) loaded successfully via CORE path.")
except ImportError:
    logger.warning("ΛTRACE: Could not import LUKHASBrainIntegration from core.brain_integration. Advanced memory functions might be limited.")
except Exception as e_brain_import: # Catch other potential errors during this import
    logger.error(f"ΛTRACE: Unexpected error importing LUKHASBrainIntegration: {e_brain_import}", exc_info=True)


# TODO: Reconcile this AccessTier with the global LUKHAS Tier System (0-5, Free-Transcendent).
# This enum might be for internal resource access control within the integrator's context.
# Human-readable comment: Defines internal access tier levels for the Lukhas Awareness Protocol.
class AccessTier(Enum):
    """Access tier levels for Lukhas Awareness Protocol within this integrator."""
    RESTRICTED = 0
    BASIC = 1
    STANDARD = 2 
    ENHANCED = 3
    FULL = 4
logger.debug(f"ΛTRACE: Internal AccessTier Enum defined: {[tier.name for tier in AccessTier]}.")

# Human-readable comment: Defines message types for core system communication.
class CoreMessageType(Enum):
    """Message types for core communication within the LUKHAS system."""
    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"
    EVENT = "event"
    ALERT = "alert"
    STATUS = "status"
logger.debug(f"ΛTRACE: CoreMessageType Enum defined: {[msg_type.name for msg_type in CoreMessageType]}.")


# Placeholder for the tier decorator - this will be properly defined/imported later
# For now, this is a conceptual placeholder.
# Human-readable comment: Placeholder for tier requirement decorator.
def lukhas_tier_required(level: int):
    """Conceptual placeholder for a tier requirement decorator."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Real implementation would check user's actual tier against 'level'
            # For now, just log that a tier check would occur.
            logger.debug(f"ΛTRACE: (Placeholder) Tier check: Function '{func.__name__}' requires Tier {level}.")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Human-readable comment: Core integration hub for the LUKHAS AGI System.
class LUKHASCoreIntegrator:
    """
    Core integration hub for Lukhas AGI System.
    This class provides the central integration point for Lukhas core components,
    including voice, nodes, awareness protocol, and other modules.
    """
    
    # Human-readable comment: Initializes the Lukhas Core Integrator.
    #ΛEXPOSE
    @lukhas_tier_required(level=2) # Example: Initializing the core integrator might require Professional tier
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Lukhas Core Integrator.
        Args:
            config_path (Optional[str]): Path to a JSON configuration file.
        """
        self.instance_logger = logger.getChild("LUKHASCoreIntegratorInstance") # Instance-specific logger
        self.instance_logger.info("ΛTRACE: Initializing LUKHASCoreIntegrator instance.")
        
        self.config = self._load_config(config_path) # Logs internally
        
        self.components: Dict[str, Any] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.event_subscribers: Dict[str, List[Dict[str, Any]]] = {}
        self.component_status: Dict[str, Dict[str, Any]] = {}
        
        #AIDENTITY
        self.awareness: Optional[Any] = None # Placeholder for awareness protocol instance
        #ΛDRIFT_POINT
        # Initialize internal access tier based on config or default
        try:
            default_tier_name_str = self.config.get("security", {}).get("default_access_tier", "RESTRICTED")
            self.current_access_tier: AccessTier = AccessTier[default_tier_name_str.upper()]
        except KeyError:
            self.instance_logger.warning(f"ΛTRACE: Invalid default_access_tier '{default_tier_name_str}' in config. Defaulting to RESTRICTED.")
            self.current_access_tier = AccessTier.RESTRICTED
        self.instance_logger.debug(f"ΛTRACE: Initial internal access tier set to {self.current_access_tier.name}.")

        self.system_state: Dict[str, Any] = {
            "started": time.time(), "last_activity": time.time(),
            "message_count": 0, "error_count": 0
        }
        
        #AIDENTITY
        self.brain: Optional[Any] = None # Placeholder for brain integration instance
        if BRAIN_INTEGRATION_AVAILABLE and LUKHASBrainIntegration:
            try:
                self.instance_logger.info("ΛTRACE: Initializing Brain Integration module (LUKHASBrainIntegration)...")
                brain_config_data = self.config.get("brain_config", {})
                self.brain = LUKHASBrainIntegration(self, brain_config_data) # Pass self (integrator) and config
                self.instance_logger.info("ΛTRACE: LUKHASBrainIntegration module initialized successfully.")
            except Exception as e:
                self.instance_logger.error(f"ΛTRACE: Failed to initialize LUKHASBrainIntegration: {e}", exc_info=True)
        
        self.instance_logger.info("ΛTRACE: LUKHASCoreIntegrator instance fully initialized.")

    # Human-readable comment: Loads configuration from a file or uses defaults.
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        self.instance_logger.debug(f"ΛTRACE: Loading configuration. Provided path: '{config_path}'.")
        # TODO: Make default paths relative to a configurable project root or use package resources.
        default_config = {
            "component_paths": {
                "voice": "VOICE/voice_processor.py",
                "awareness": "AWARENESS/awareness_protocol.py",
                "node_manager": "NODES/node_manager.py",
                "brain": "CORE/brain_integration.py"
            },
            "logging": {
                "level": "INFO", "trace_enabled": True,
                "trace_path": "logs/symbolic_trace.jsonl"
            },
            "security": {
                "default_access_tier": "RESTRICTED",
                "tier_escalation_timeout": 300,
                "symbolic_trace_retention": 7
            },
            "brain_config": {
                "memory_consolidation_enabled": True, "emotion_mapping_enabled": True,
                "consolidation_interval_minutes": 60, "memory_path": "./memory_store"
            }
        }
        
        loaded_config = default_config.copy()

        if config_path:
            config_file = Path(config_path)
            if config_file.exists() and config_file.is_file():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)

                    for key, value in user_config.items():
                        if isinstance(value, dict) and isinstance(loaded_config.get(key), dict):
                            loaded_config[key].update(value)
                        else:
                            loaded_config[key] = value
                    self.instance_logger.info(f"ΛTRACE: Configuration loaded successfully from {config_file}.")
                except json.JSONDecodeError as e_json:
                    self.instance_logger.error(f"ΛTRACE: Error decoding JSON from config file {config_file}: {e_json}. Using default configuration.", exc_info=True)
                except Exception as e_load:
                    self.instance_logger.error(f"ΛTRACE: Error loading config from {config_file}: {e_load}. Using default configuration.", exc_info=True)
            else:
                self.instance_logger.warning(f"ΛTRACE: Config file not found at {config_path}. Using default configuration.")
        else:
            self.instance_logger.info("ΛTRACE: No config path provided. Using default configuration.")
        
        if "logging" not in loaded_config or not isinstance(loaded_config["logging"], dict):
             loaded_config["logging"] = default_config["logging"]
        if "trace_path" not in loaded_config["logging"]:
            loaded_config["logging"]["trace_path"] = default_config["logging"]["trace_path"]

        self.instance_logger.debug(f"ΛTRACE: Final configuration: {loaded_config}")
        return loaded_config
    
    # Human-readable comment: Registers a component with the core integrator.
    #ΛEXPOSE
    @lukhas_tier_required(level=3) # Example: Registering components might require Premium tier
    def register_component(self, 
                          component_id: str, 
                          component_instance: Any, 
                          message_handler: Optional[Callable[[Dict[str,Any]], Any]] = None) -> bool:
        """
        Register a component with the core integrator.
        Args:
            component_id (str): Unique identifier for the component.
            component_instance (Any): The component instance.
            message_handler (Optional[Callable]): Function to handle messages for this component.
        Returns:
            bool: True if registration was successful, False otherwise.
        """
        self.instance_logger.info(f"ΛTRACE: Attempting to register component '{component_id}'.")
        if not isinstance(component_id, str) or not component_id:
            self.instance_logger.error("ΛTRACE: Component ID must be a non-empty string.")
            return False
        if component_id in self.components:
            self.instance_logger.warning(f"ΛTRACE: Component '{component_id}' already registered.")
            return False
        
        self.components[component_id] = component_instance
        self.component_status[component_id] = {
            "registered_at": time.time(), "status": "registered",
            "last_activity": time.time(), "error_count": 0
        }
        
        if message_handler:
            if not callable(message_handler):
                self.instance_logger.error(f"ΛTRACE: Provided message_handler for '{component_id}' is not callable.")
            else:
                self.message_handlers[component_id] = message_handler
                self.instance_logger.info(f"ΛTRACE: Message handler registered for component '{component_id}'.")
        
        self.instance_logger.info(f"ΛTRACE: Component '{component_id}' registered successfully.")
        return True
    
    # Human-readable comment: Registers a message handler for a component.
    #ΛEXPOSE
    @lukhas_tier_required(level=3)
    def register_message_handler(self, component_id: str, handler: Callable[[Dict[str,Any]], Any]) -> bool:
        """Register a message handler for a component."""
        self.instance_logger.debug(f"ΛTRACE: Registering message handler for component '{component_id}'.")
        if not isinstance(component_id, str) or not component_id:
            self.instance_logger.error("ΛTRACE: Component ID must be a non-empty string for message handler registration.")
            return False
        if not callable(handler):
            self.instance_logger.error(f"ΛTRACE: Handler provided for '{component_id}' is not callable.")
            return False
        self.message_handlers[component_id] = handler
        self.instance_logger.info(f"ΛTRACE: Message handler registered for '{component_id}'.")
        return True
    
    # Human-readable comment: Subscribes a callback to a system event type.
    #ΛEXPOSE
    @lukhas_tier_required(level=1) # Example: Subscribing to events might be a Basic tier feature
    def subscribe_to_events(self, 
                          event_type: str, 
                          callback: Callable[[Dict[str,Any]], None],
                          component_id: Optional[str] = None) -> bool:
        """Subscribe to system events."""
        self.instance_logger.debug(f"ΛTRACE: Component '{component_id if component_id else 'Unknown'}' subscribing to event type '{event_type}'.")
        if not isinstance(event_type, str) or not event_type:
            self.instance_logger.error("ΛTRACE: Event type must be a non-empty string.")
            return False
        if not callable(callback):
            self.instance_logger.error(f"ΛTRACE: Callback for event '{event_type}' is not callable.")
            return False
            
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        
        self.event_subscribers[event_type].append({
            "callback": callback, "component_id": component_id
        })
        self.instance_logger.info(f"ΛTRACE: Subscription to event '{event_type}' for '{component_id if component_id else 'callback'}' successful.")
        return True
    
    # Human-readable comment: Sends a message to a target component.
    #ΛEXPOSE
    @lukhas_tier_required(level=1) # Example: Sending messages might require Basic tier
    def send_message(self, 
                    target_component: str, 
                    message: Dict[str, Any],
                    source_component: Optional[str] = None,
                    message_type: CoreMessageType = CoreMessageType.COMMAND) -> Dict[str, Any]:
        """Send a message to a component."""
        self.instance_logger.debug(f"ΛTRACE: Attempting to send message from '{source_component if source_component else 'System'}' to '{target_component}'. Type: {message_type.value}.")
        self.system_state["message_count"] += 1
        self.system_state["last_activity"] = time.time()
        
        if not isinstance(target_component, str) or not target_component:
            self.instance_logger.error("ΛTRACE: Target component ID must be a non-empty string.")
            return {"status": "error", "error": "Invalid target component ID", "timestamp": time.time()}

        if target_component not in self.components:
            self.instance_logger.error(f"ΛTRACE: Cannot send message. Unknown target component: '{target_component}'.")
            return {"status": "error", "error": f"Unknown component: {target_component}", "timestamp": time.time()}
        
        #ΛDRIFT_POINT
        if self.awareness and message_type == CoreMessageType.COMMAND:
            self._log_symbolic_trace({
                "action": "message_sent_attempt", "source": source_component, "target": target_component,
                "message_type": message_type.value, "access_tier": self.current_access_tier.name, "timestamp": time.time()
            })
            
            if not self._check_action_permitted(target_component, message, self.current_access_tier):
                self.instance_logger.warning(f"ΛTRACE: Action denied for '{target_component}' by '{source_component}'. Current internal tier: {self.current_access_tier.name}.")
                return {"status": "denied", "error": f"Action not permitted at access tier {self.current_access_tier.name}", "timestamp": time.time()}
        
        if target_component in self.component_status: # Ensure component status exists
            self.component_status[target_component]["last_activity"] = time.time()
        
        message_envelope = {
            "content": message,
            "metadata": {"source": source_component, "timestamp": time.time(), "message_type": message_type.value,
                         "message_id": f"{int(time.time() * 1000)}-{self.system_state['message_count']}"}
        }
        
        try:
            handler_to_call: Optional[Callable[[Dict[str,Any]], Any]] = None
            if target_component in self.message_handlers:
                handler_to_call = self.message_handlers[target_component]
            else:
                component_instance = self.components[target_component]
                if hasattr(component_instance, 'process_message') and callable(getattr(component_instance, 'process_message')):
                    handler_to_call = component_instance.process_message
            
            if handler_to_call:
                self.instance_logger.debug(f"ΛTRACE: Delivering message to '{target_component}' via registered handler/method.")
                response = handler_to_call(message_envelope)
                self.instance_logger.info(f"ΛTRACE: Message processed by '{target_component}'. Response type: {type(response).__name__}.")
                return response if isinstance(response, dict) else {"status": "processed_no_dict_response", "response_type": type(response).__name__}

            self.instance_logger.error(f"ΛTRACE: No message handler or 'process_message' method for component: '{target_component}'.")
            if target_component in self.component_status: self.component_status[target_component]["error_count"] += 1
            self.system_state["error_count"] += 1
            return {"status": "error", "error": "No message handler available", "timestamp": time.time()}
            
        except Exception as e:
            self.instance_logger.error(f"ΛTRACE: Error processing message for '{target_component}': {e}", exc_info=True)
            if target_component in self.component_status: self.component_status[target_component]["error_count"] += 1
            self.system_state["error_count"] += 1
            return {"status": "error", "error": str(e), "timestamp": time.time()}
    
    # Human-readable comment: Broadcasts an event to all subscribed components.
    #ΛEXPOSE
    @lukhas_tier_required(level=1)
    def broadcast_event(self, 
                       event_type: str, 
                       event_data: Dict[str, Any],
                       source_component: Optional[str] = None) -> int:
        """Broadcast an event to all subscribers."""
        self.instance_logger.info(f"ΛTRACE: Broadcasting event '{event_type}' from '{source_component if source_component else 'System'}'.")
        if not isinstance(event_type, str) or not event_type:
            self.instance_logger.error("ΛTRACE: Event type for broadcast must be a non-empty string.")
            return 0
        if event_type not in self.event_subscribers or not self.event_subscribers[event_type]:
            self.instance_logger.debug(f"ΛTRACE: No subscribers for event type '{event_type}'.")
            return 0
        
        event_envelope = {
            "event_type": event_type, "data": event_data,
            "metadata": {"source": source_component, "timestamp": time.time(), "event_id": f"evt-{int(time.time() * 1000)}"}
        }
        
        self._log_symbolic_trace({"action": "event_broadcast", "event_type": event_type, "source": source_component, "timestamp": time.time()})
        
        delivery_count = 0
        for subscriber_info in self.event_subscribers[event_type]:
            callback_func = subscriber_info.get("callback")
            sub_component_id = subscriber_info.get("component_id")
            if not callable(callback_func):
                self.instance_logger.warning(f"ΛTRACE: Subscriber callback for event '{event_type}' (component: {sub_component_id}) is not callable. Skipping.")
                continue
            try:
                self.instance_logger.debug(f"ΛTRACE: Delivering event '{event_type}' to subscriber (Component: '{sub_component_id if sub_component_id else 'Direct Callback'}').")
                callback_func(event_envelope)
                delivery_count += 1
            except Exception as e:
                self.instance_logger.error(f"ΛTRACE: Error delivering event '{event_type}' to subscriber '{sub_component_id if sub_component_id else 'callback'}': {e}", exc_info=True)
                if sub_component_id and sub_component_id in self.component_status:
                    self.component_status[sub_component_id]["error_count"] += 1
        
        self.instance_logger.info(f"ΛTRACE: Event '{event_type}' delivered to {delivery_count}/{len(self.event_subscribers[event_type])} subscribers.")
        return delivery_count
    
    # Human-readable comment: Initializes the Lukhas Awareness Protocol.
    #ΛEXPOSE
    @lukhas_tier_required(level=3)
    def initialize_awareness_protocol(self, awareness_instance: Optional[Any] = None) -> bool:
        """Initialize the Lukhas Awareness Protocol."""
        self.instance_logger.info("ΛTRACE: Attempting to initialize Lukhas Awareness Protocol.")
        # TODO: Refactor dynamic import to be more robust or use explicit imports if LUKHASAwarenessProtocol path is standardized.
        try:
            if awareness_instance:
                self.awareness = awareness_instance
                self.instance_logger.info("ΛTRACE: Using provided awareness_instance.")
            else:
                awareness_path_str = self.config.get("component_paths", {}).get("awareness", "AWARENESS/awareness_protocol.py")
                module_path_str = awareness_path_str.replace("/", ".").replace(".py", "") # Basic conversion
                self.instance_logger.debug(f"ΛTRACE: Attempting to dynamically import LUKHASAwarenessProtocol from '{module_path_str}'.")
                
                # This dynamic import is fragile. Proper packaging or a plugin system is preferred.
                module = __import__(module_path_str, fromlist=["LUKHASAwarenessProtocol"]) # type: ignore
                awareness_class_ref = getattr(module, "LUKHASAwarenessProtocol")
                self.awareness = awareness_class_ref()
                self.instance_logger.info(f"ΛTRACE: LUKHASAwarenessProtocol dynamically imported and instantiated from '{module_path_str}'.")
            
            self.register_component("awareness", self.awareness)
            
            current_config_security = self.config.get("security", {})
            default_tier_name_str = current_config_security.get("default_access_tier", "RESTRICTED")
            try:
                self.current_access_tier = AccessTier[default_tier_name_str.upper()]
            except KeyError:
                self.instance_logger.error(f"ΛTRACE: Invalid default_access_tier '{default_tier_name_str}' in config. Defaulting to RESTRICTED.")
                self.current_access_tier = AccessTier.RESTRICTED
            self.instance_logger.info(f"ΛTRACE: Default internal access tier set to {self.current_access_tier.name}.")
            
            if hasattr(self.awareness, 'register_core_callback') and callable(getattr(self.awareness, 'register_core_callback')):
                self.awareness.register_core_callback(self.process_awareness_alert)
                self.instance_logger.info("ΛTRACE: Registered core callback with awareness protocol.")
            
            if self.brain and self.awareness and hasattr(self.brain, 'connect_awareness'):
                try:
                    self.brain.connect_awareness(self.awareness)
                    self.instance_logger.info("ΛTRACE: Connected brain integration with awareness protocol.")
                except Exception as e_brain_aware:
                    self.instance_logger.error(f"ΛTRACE: Failed to connect brain with awareness: {e_brain_aware}", exc_info=True)
            
            self.instance_logger.info("ΛTRACE: Lukhas Awareness Protocol initialized successfully.")
            return True
            
        except ImportError as e_imp:
            self.instance_logger.error(f"ΛTRACE: Could not import awareness protocol. Check path in config: '{self.config.get('component_paths', {}).get('awareness')}'. Error: {e_imp}", exc_info=True)
            return False
        except Exception as e_init_aware:
            self.instance_logger.error(f"ΛTRACE: Failed to initialize awareness protocol: {e_init_aware}", exc_info=True)
            return False
    
    # Human-readable comment: Processes alerts received from the awareness protocol.
    #ΛEXPOSE
    @lukhas_tier_required(level=1)
    def process_awareness_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process alerts from the awareness protocol."""
        alert_type = alert_data.get("alert_type", "unknown_alert")
        self.instance_logger.info(f"ΛTRACE: Processing awareness alert of type '{alert_type}'. Data: {alert_data}")
        
        self._log_symbolic_trace({"action": "awareness_alert_received", "alert_type": alert_type, "timestamp": time.time(), "details": alert_data})
        
        #ΛDRIFT_POINT
        if alert_type == "access_tier_change":
            new_tier_name_str = alert_data.get("new_tier", self.current_access_tier.name)
            try:
                self.current_access_tier = AccessTier[new_tier_name_str.upper()]
                self.instance_logger.info(f"ΛTRACE: Internal access tier changed to {self.current_access_tier.name} due to awareness alert.")
                if self.brain and hasattr(self.brain, 'update_access_tier'):
                    try:
                        self.brain.update_access_tier(self.current_access_tier)
                        self.instance_logger.debug(f"ΛTRACE: Updated brain's internal access tier to {self.current_access_tier.name}.")
                    except Exception as e_brain_tier:
                        self.instance_logger.error(f"ΛTRACE: Failed to update brain access tier: {e_brain_tier}", exc_info=True)
            except KeyError:
                self.instance_logger.error(f"ΛTRACE: Invalid access tier '{new_tier_name_str}' received from awareness alert.")
        
        elif alert_type == "security_violation":
            self.instance_logger.warning(f"ΛTRACE: Security violation detected by awareness protocol: {alert_data.get('description', 'No description')}.")
            self.broadcast_event("security_violation", alert_data, "awareness")
        
        self.instance_logger.debug(f"ΛTRACE: Awareness alert '{alert_type}' processed.")
        return {"status": "processed", "timestamp": time.time()}
    
    # Human-readable comment: Internal check if an action is permitted based on internal AccessTier.
    def _check_action_permitted(self, target_component: str, message: Dict[str, Any], access_tier: AccessTier) -> bool:
        """Check if an action is permitted at the current internal access tier."""
        self.instance_logger.debug(f"ΛTRACE: Checking internal permission for target '{target_component}', AccessTier '{access_tier.name}'. Action: {message.get('action', 'N/A')}")
        if not self.awareness:
            self.instance_logger.debug("ΛTRACE: Awareness protocol not active, permitting action by default.")
            return True
            
        if hasattr(self.awareness, 'check_permission') and callable(getattr(self.awareness, 'check_permission')):
            try:
                is_permitted = self.awareness.check_permission(target_component, message, access_tier.name)
                self.instance_logger.debug(f"ΛTRACE: Awareness protocol permission check result: {is_permitted}.")
                return is_permitted
            except Exception as e_perm_check:
                self.instance_logger.error(f"ΛTRACE: Error calling awareness.check_permission: {e_perm_check}. Denying action by default.", exc_info=True)
                return False

        self.instance_logger.warning("ΛTRACE: Awareness protocol 'check_permission' method not found. Using basic fallback permission logic.")
        if access_tier == AccessTier.RESTRICTED:
            allowed_targets = ["awareness"]
            allowed_actions = ["status", "query", "auth"]
            action_type = message.get("action", "").lower()
            is_basic_allowed = target_component in allowed_targets or action_type in allowed_actions
            self.instance_logger.debug(f"ΛTRACE: Basic fallback for RESTRICTED tier: Allowed = {is_basic_allowed}.")
            return is_basic_allowed

        is_min_basic_tier = access_tier.value >= AccessTier.BASIC.value
        self.instance_logger.debug(f"ΛTRACE: Basic fallback for non-RESTRICTED: Allowed if tier >= BASIC -> {is_min_basic_tier}.")
        return is_min_basic_tier
    
    # Human-readable comment: Logs data to a specific symbolic trace file.
    def _log_symbolic_trace(self, trace_data: Dict[str, Any]) -> None:
        """Log symbolic trace data for auditing."""
        # Ensure logging config and trace_enabled are dictionaries or have defaults
        current_logging_config = self.config.get("logging", {})
        if not isinstance(current_logging_config, dict):
            current_logging_config = {} # Default to empty dict if not a dict

        if not current_logging_config.get("trace_enabled", False):
            return
            
        trace_file_path_str = current_logging_config.get("trace_path", "logs/symbolic_trace.jsonl")
        trace_file = Path(trace_file_path_str)
        
        try:
            trace_file.parent.mkdir(parents=True, exist_ok=True)
            trace_data["system_time_utc"] = datetime.utcnow().isoformat()

            with open(trace_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(trace_data) + '\n')
        except Exception as e_trace:
            self.instance_logger.error(f"ΛTRACE: Failed to write to symbolic trace file '{trace_file}': {e_trace}", exc_info=True)
    
    # Human-readable comment: Retrieves status for a specific component or all components.
    #ΛEXPOSE
    @lukhas_tier_required(level=0)
    def get_component_status(self, component_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of a specific component or all components."""
        self.instance_logger.debug(f"ΛTRACE: Requesting component status for '{component_id if component_id else 'ALL'}'.")
        if component_id:
            if not isinstance(component_id, str) or not component_id:
                self.instance_logger.warning("ΛTRACE: Invalid component ID for status request.")
                return {"error": "Invalid component ID"}
            if component_id not in self.component_status:
                self.instance_logger.warning(f"ΛTRACE: Unknown component ID '{component_id}' requested for status.")
                return {"error": f"Unknown component: {component_id}"}
            return self.component_status[component_id]
        return self.component_status
    
    # Human-readable comment: Retrieves the overall system status.
    #ΛEXPOSE
    @lukhas_tier_required(level=0)
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        self.instance_logger.info("ΛTRACE: Requesting overall system status.")
        status = self.system_state.copy()
        status["uptime_seconds"] = time.time() - status.get("started", time.time()) # Safely get 'started'
        status["component_count"] = len(self.components)
        status["current_internal_access_tier"] = self.current_access_tier.name
        
        if self.brain and hasattr(self.brain, 'get_status') and callable(getattr(self.brain, 'get_status')):
            try:
                brain_status = self.brain.get_status()
                status["brain_module_status"] = brain_status
                self.instance_logger.debug(f"ΛTRACE: Brain status retrieved: {brain_status}")
            except Exception as e_brain_status:
                self.instance_logger.error(f"ΛTRACE: Error getting brain status: {e_brain_status}", exc_info=True)
                status["brain_module_status"] = {"error": str(e_brain_status)}
        else:
             status["brain_module_status"] = "Not available or no get_status method."
             self.instance_logger.debug(f"ΛTRACE: Brain module not available or has no get_status method.")

        self.instance_logger.info(f"ΛTRACE: System status provided. Uptime: {status['uptime_seconds']:.2f}s.")
        return status

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: lukhas_core_integrator.py
# VERSION: 1.2.0
# TIER SYSTEM: Tier 1-4 (Core system integration; actions might be restricted by internal AccessTier or global system tiers)
#              Internal AccessTier enum (0-4) used for awareness protocol; needs reconciliation with global 0-5 system.
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Central component management, message routing, event subscription,
#               awareness protocol integration, configuration loading, system status reporting.
# FUNCTIONS: lukhas_tier_required
# CLASSES: AccessTier, CoreMessageType, LUKHASCoreIntegrator
# DECORATORS: @lukhas_tier_required
# DEPENDENCIES: logging, time, typing, os, json, enum, pathlib. Potentially CORE.brain_integration.LUKHASBrainIntegration.
# INTERFACES: Public methods of LUKHASCoreIntegrator class.
# ERROR HANDLING: Catches exceptions in major operations, logs them via ΛTRACE, and returns error statuses.
# LOGGING: ΛTRACE_ENABLED using hierarchical loggers. Also uses a separate symbolic trace log file.
# AUTHENTICATION: Relies on LUKHASAwarenessProtocol for internal access control based on AccessTier.
#                 Global tier checks via @lukhas_tier_required would depend on external user auth.
# HOW TO USE:
#   from core.advanced.brain.lukhas_core_integrator import LUKHASCoreIntegrator, CoreMessageType, AccessTier
#   integrator = LUKHASCoreIntegrator(config_path="path/to/config.json")
#   integrator.register_component("my_component", my_instance, my_handler)
#   integrator.send_message("my_component", {"action": "do_something"})
# INTEGRATION NOTES: Configuration paths (components, logs) should be robust (e.g., use Path objects, ensure dirs exist).
#                    The internal AccessTier enum (0-4) needs mapping or reconciliation with the
#                    global LUKHAS Tier System (0-5) for consistent tier enforcement.
#                    Dynamic imports (awareness, brain_integration) are fragile; prefer package structure.
# MAINTENANCE: Regularly review TODOs. Update default configurations.
#              Standardize import paths. Clarify tier system usage and reconcile AccessTier.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════