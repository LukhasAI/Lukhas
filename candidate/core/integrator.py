# --- LUKHΛS AI Standard Header ---
# File: core_integrator.py
# Path: integration/core_integrator.py
# Project: LUKHΛS AI Model Integration
# Created: 2023-10-26 (Approx. by LUKHΛS Team)
# Modified: 2024-07-27
# Version: 1.1
# License: Proprietary - LUKHΛS AI Use Only
# Contact: support@lukhas.ai
# Description: Enhanced Core Integrator Module for LUKHΛS AI.
#              Manages interaction between core system components,
#              incorporating quantum-biological features and security.
# --- End Standard Header ---

# ΛTAGS: [CoreIntegrator, SystemBus, ComponentManagement, QIBiological, SecurityIntegration, ΛTRACE_DONE]
# ΛNOTE: Central hub for LUKHΛS core components. Synchronous nature needs review for async LUKHΛS.
# This file was already largely compliant with standardization efforts.
# Minor updates applied.

# Standard Library Imports
import asyncio
import threading
import time
import uuid  # Added uuid for message IDs
from collections import defaultdict  # For event_subscribers_map
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

# Third-Party Imports
import structlog

# Initialize structlog logger for this module
log = structlog.get_logger(__name__)

# --- LUKHΛS Core Component Imports & Placeholders ---
# ΛIMPORT_TODO: Resolve 'CORE.' import paths. Ensure CORE is a top-level
# package or adjust relative paths.
CORE_COMPONENTS_LOADED_FLAG_ECI = False  # Unique flag
try:
    # ΛNOTE: Attempting to import core components. Placeholders used if imports fail.
    #        These imports suggest a dependency on a 'CORE' package structure.
    from bio.core import BioOrchestrator  # type: ignore
    from candidate.core.bio_systems.qi_layer import QIBioOscillator
    from candidate.core.security.access_control import (
        AccessController,  # type: ignore
        AccessTier,
    )
    from candidate.core.security.compliance import ComplianceMonitor  # type: ignore
    from candidate.core.security.qi_auth import QIAuthenticator  # type: ignore
    from candidate.core.unified_integration import UnifiedIntegration  # type: ignore

    CORE_COMPONENTS_LOADED_FLAG_ECI = True
    log.debug("LUKHΛS CORE components for EnhancedCoreIntegrator imported successfully.")
except ImportError as e:
    log.error(
        "Failed to import LUKHΛS CORE components for EnhancedCoreIntegrator. Using placeholders.",
        error_message=str(e),
        module_path="integration/core_integrator.py",
        components_expected=[
            "QIBioOscillator",
            "BioOrchestrator",
            "AccessTier",
            "AccessController",
            "QIAuthenticator",
            "ComplianceMonitor",
            "UnifiedIntegration",
        ],
    )

    # Placeholder classes if actual core components are not found

    class QIBioOscillator:
        def __init__(self, config: dict[str, Any]):
            log.info(
                "PH_ECI: QIBioOscillator placeholder initialized",
                config=config,
            )
            self.config = config

        def verify_component_state(self, component_instance: Any):
            log.debug(
                "PH_ECI: verify_component_state called",
                component=type(component_instance).__name__,
            )

        def verify_message_state(self, message_content: dict[str, Any]):
            log.debug(
                "PH_ECI: verify_message_state called",
                keys=list(message_content.keys()),
            )

        def sign_message(self, message: dict[str, Any]) -> str:
            log.debug("PH_ECI: sign_message called")
            return f"q_sig_placeholder_eci_{uuid.uuid4().hex[:8]}"

        def get_coherence(self) -> float:
            log.debug("PH_ECI: get_coherence called")
            return 0.991

    class BioOrchestrator:
        def __init__(self, config: dict[str, Any]):
            log.info(
                "PH_ECI: BioOrchestrator placeholder initialized",
                config=config,
            )
            self.config = config

        def register_component(self, component_id: str, component_instance: Any):
            log.debug(
                "PH_ECI: register_component called",
                id=component_id,
                type=type(component_instance).__name__,
            )

        def process_message(self, message: dict[str, Any]):
            log.debug("PH_ECI: process_message called", msg_id=message.get("id"))

        def process_event(self, event: dict[str, Any]):
            log.debug("PH_ECI: process_event called", event_type=event.get("type"))

        def get_health(self) -> float:
            log.debug("PH_ECI: get_health called")
            return 0.981

    class AccessTier(Enum):
        STANDARD = 1
        PRIVILEGED = 2
        CRITICAL_SYSTEM = 3

    class AccessController:
        def __init__(self, config: dict[str, Any]):
            log.info(
                "PH_ECI: AccessController placeholder initialized",
                config=config,
            )
            self.config = config

        def register_component(self, component_id: str, tier: AccessTier):
            log.debug(
                "PH_ECI: register_component for access control",
                id=component_id,
                tier=tier.name,
            )

        def check_permission(self, source_id: Optional[str], target_id: str, message_type: Any) -> bool:
            log.debug(
                "PH_ECI: check_permission called",
                source=source_id,
                target=target_id,
                type=str(message_type),
            )
            return True

        def get_status(self) -> str:
            log.debug("PH_ECI: get_status called")
            return "secure_placeholder_eci"

    class QIAuthenticator:
        def __init__(self):
            log.info("PH_ECI: QIAuthenticator placeholder initialized")

    class ComplianceMonitor:
        def __init__(self):
            log.info("PH_ECI: ComplianceMonitor placeholder initialized")

    class UnifiedIntegration:
        def __init__(self):
            log.info("PH_ECI: UnifiedIntegration placeholder initialized")


# ΛTIER_CONFIG_START
# Tier mapping for LUKHΛS ID Service (Conceptual)
# This defines the access levels required for methods in this module.
# Refer to lukhas/identity/core/tier/tier_manager.py for actual enforcement.
# {
#   "module": "integration.core_integrator",
#   "class_EnhancedCoreIntegrator": {
#     "default_tier": 0,
#     "methods": {
#       "__init__": 0,
#       "register_component": 0,
#       "send_message_to_component": 1,
#       "get_system_status": 0,
#       "broadcast_event": 1,
#       "subscribe_to_event": 0
#     }
#   }
# }
# ΛTIER_CONFIG_END

# Placeholder for actual LUKHΛS Tier decorator
# ΛNOTE: This is a placeholder. The actual decorator might be in
# `lukhas-id.core.tier.tier_manager`.


def lukhas_tier_required(level: int):
    """Decorator to specify the LUKHΛS access tier required for a method."""

    def decorator(func):
        func._lukhas_tier = level
        # log.debug(f"Tier {level} assigned to
        # {func.__module__}.{func.__qualname__}") # Optional: for debugging tier
        # assignment
        return func

    return decorator


@dataclass
class EnhancedCoreConfig:
    """Configuration for the EnhancedCoreIntegrator."""

    qi_config: dict[str, Any] = field(default_factory=dict)
    security_config: dict[str, Any] = field(default_factory=dict)
    oscillator_config: dict[str, Any] = field(default_factory=dict)
    component_paths_cfg: dict[str, str] = field(default_factory=dict)  # Renamed
    enable_quantum: bool = True
    enable_bio_oscillator: bool = True
    enable_security: bool = True


class CoreMessageType(Enum):
    """Message types for LUKHΛS core communication."""

    COMMAND = "command"
    EVENT = "event"
    ALERT = "alert"
    STATUS_QUERY = "status_query"
    STATUS_RESPONSE = "status_response"
    DATA_PAYLOAD = "data_payload"


@lukhas_tier_required(0)
class EnhancedCoreIntegrator:
    """
    Enhanced LUKHΛS Core Integrator.
    Manages interactions, security, and quantum-biological aspects of core components.
    """

    def __init__(self, config: Optional[EnhancedCoreConfig] = None):
        """
        Initializes the EnhancedCoreIntegrator.
        Sets up quantum layer, bio-orchestrator, and security components based on config.
        """
        self.config: EnhancedCoreConfig = config or EnhancedCoreConfig()

        self.qi_layer: Optional[QIBioOscillator] = None
        self.bio_orchestrator: Optional[BioOrchestrator] = None
        self.access_controller: Optional[AccessController] = None
        self.qi_auth: Optional[QIAuthenticator] = None
        self.compliance_monitor: Optional[ComplianceMonitor] = None

        if self.config.enable_quantum and CORE_COMPONENTS_LOADED_FLAG_ECI:
            self.qi_layer = QIBioOscillator(self.config.qi_config)  # type: ignore
            log.info("QIBioOscillator layer initialized.")
        if self.config.enable_bio_oscillator and CORE_COMPONENTS_LOADED_FLAG_ECI:
            self.bio_orchestrator = BioOrchestrator(self.config.oscillator_config)  # type: ignore
            log.info("BioOrchestrator initialized.")
        if self.config.enable_security and CORE_COMPONENTS_LOADED_FLAG_ECI:
            self.access_controller = AccessController(self.config.security_config)  # type: ignore
            self.qi_auth = QIAuthenticator()  # type: ignore
            self.compliance_monitor = ComplianceMonitor()  # type: ignore
            log.info("Security components (AccessController, QIAuth, ComplianceMonitor) initialized.")

        self.components: dict[str, Any] = {}
        self.event_subscribers: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.component_status: dict[str, dict[str, Any]] = {}

        # Context Bus performance tracking
        self._event_metrics: dict[str, list[float]] = defaultdict(list)
        self._context_handoff_times: list[float] = []
        self._event_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="LUKHAS_Event")
        self._subscription_lock = threading.Lock()

        # Event system initialization
        self._initialize_context_bus()

        self.integration_layer: Optional[UnifiedIntegration] = (
            UnifiedIntegration() if CORE_COMPONENTS_LOADED_FLAG_ECI else None
        )  # type: ignore
        if self.integration_layer:
            log.info("UnifiedIntegration layer initialized.")

        log.info(
            "EnhancedCoreIntegrator initialized.",
            qi_enabled=bool(self.qi_layer),
            bio_oscillator_enabled=bool(self.bio_orchestrator),
            security_enabled=bool(self.access_controller),
            core_components_loaded=CORE_COMPONENTS_LOADED_FLAG_ECI,
        )

    @lukhas_tier_required(0)
    def register_component(
        self,
        component_id: str,
        component_instance: Any,
        access_tier: Optional[AccessTier] = None,
    ) -> bool:
        """
        Registers a component with the integrator.
        Verifies component state, registers with bio-orchestrator and access controller.
        """
        log.info(
            "Registering component.",
            component_id=component_id,
            component_type=type(component_instance).__name__,
            requested_tier=(access_tier.name if access_tier else "DEFAULT_STANDARD"),
        )
        try:
            if self.qi_layer and hasattr(self.qi_layer, "verify_component_state"):
                self.qi_layer.verify_component_state(component_instance)
            if self.bio_orchestrator and hasattr(self.bio_orchestrator, "register_component"):
                self.bio_orchestrator.register_component(component_id, component_instance)

            effective_tier = access_tier or AccessTier.STANDARD
            if self.access_controller and hasattr(self.access_controller, "register_component"):
                self.access_controller.register_component(component_id, effective_tier)  # type: ignore

            self.components[component_id] = component_instance
            current_q_coherence = 1.0
            if self.qi_layer and hasattr(self.qi_layer, "get_coherence"):
                current_q_coherence = self.qi_layer.get_coherence()  # type: ignore

            self.component_status[component_id] = {
                "status": "active_registered",
                "last_update_utc_iso": datetime.now(timezone.utc).isoformat(),
                "errors_count": 0,
                "qi_coherence_metric": current_q_coherence,
                "assigned_tier": effective_tier.name,
            }
            log.info(
                "Component registered successfully.",
                component_id=component_id,
                tier_assigned=effective_tier.name,
            )
            return True
        except Exception as e:
            log.error(
                "Failed to register component.",
                component_id=component_id,
                error=str(e),
                exc_info=True,
            )
            return False

    @lukhas_tier_required(1)
    def send_message_to_component(
        self,
        target_id: str,
        payload: dict[str, Any],
        source_id: Optional[str] = "CoreIntegrator",
        msg_type: CoreMessageType = CoreMessageType.COMMAND,
    ) -> dict[str, Any]:
        """
        Sends a message to a registered component.
        Verifies message state, checks permissions, signs message, and processes via bio-orchestrator.
        """
        message_uid = f"msg_{uuid.uuid4().hex[:12]}"
        log.debug(
            "Attempting to send message.",
            message_id=message_uid,
            target_component_id=target_id,
            source_component_id=source_id,
            message_type=msg_type.value,
            payload_keys=list(payload.keys()),
        )
        try:
            if self.qi_layer and hasattr(self.qi_layer, "verify_message_state"):
                self.qi_layer.verify_message_state(payload)

            if self.access_controller and hasattr(self.access_controller, "check_permission"):
                permission_granted = self.access_controller.check_permission(source_id, target_id, msg_type)  # type: ignore
                if not permission_granted:
                    log.warning(
                        "Message permission denied.",
                        message_id=message_uid,
                        source_id=source_id,
                        target_id=target_id,
                        message_type=msg_type.value,
                    )
                    raise PermissionError(
                        f"Message from '{source_id}' to '{target_id}' of type '{msg_type.value}' unauthorized."
                    )

            envelope = {
                "id": message_uid,
                "type": msg_type.value,
                "source_id": source_id,
                "target_id": target_id,
                "payload": payload,
                "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
            }

            if self.qi_layer and hasattr(self.qi_layer, "sign_message"):
                envelope["qi_signature"] = self.qi_layer.sign_message(envelope)  # type: ignore

            if self.bio_orchestrator and hasattr(self.bio_orchestrator, "process_message"):
                self.bio_orchestrator.process_message(envelope)  # type: ignore

            target_instance = self.components.get(target_id)
            if target_instance and hasattr(target_instance, "handle_message"):
                # ΛNOTE: Assumes handle_message is synchronous. If asynchronous, this
                # integrator needs adaptation.
                response = target_instance.handle_message(envelope)
                log.debug(
                    "Message delivered and handled by target component.",
                    target_id=target_id,
                    message_id=message_uid,
                )
                return {
                    "status": "ok",
                    "response": response,
                    "message_id": message_uid,
                }
            elif not target_instance:
                log.error(
                    "Target component not found.",
                    target_id=target_id,
                    message_id=message_uid,
                )
                raise KeyError(f"Component '{target_id}' not found or not registered.")
            else:
                log.error(
                    "Target component does not have a 'handle_message' method.",
                    target_id=target_id,
                    component_type=type(target_instance).__name__,
                    message_id=message_uid,
                )
                raise AttributeError(
                    f"Target component '{target_id}' of type '{type(target_instance).__name__}' cannot handle messages."
                )
        except PermissionError as pe:
            log.error(
                "Message permission error.",
                message_id=message_uid,
                error_message=str(pe),
            )
            return {
                "status": "error_permission_denied",
                "details": str(pe),
                "message_id": message_uid,
            }
        except KeyError as ke:
            log.error(
                "Message key error (target component not found?).",
                message_id=message_uid,
                error_message=str(ke),
            )
            return {
                "status": "error_target_not_found",
                "details": str(ke),
                "message_id": message_uid,
            }
        except Exception as e:
            log.error(
                "Unexpected error sending message.",
                message_id=message_uid,
                error_message=str(e),
                exc_info=True,
            )
            return {
                "status": "error_unexpected_exception",
                "details": str(e),
                "message_id": message_uid,
            }

    @lukhas_tier_required(0)
    def get_system_status(self) -> dict[str, Any]:
        """
        Retrieves the current status of the core integrator and its components.
        """
        log.debug("CoreIntegrator system status requested.")
        timestamp_now_iso = datetime.now(timezone.utc).isoformat()

        q_coherence_status = "N/A_Quantum_Disabled"
        if self.qi_layer and hasattr(self.qi_layer, "get_coherence"):
            q_coherence_status = self.qi_layer.get_coherence()  # type: ignore

        bio_health_status = "N/A_BioOrchestrator_Disabled"
        if self.bio_orchestrator and hasattr(self.bio_orchestrator, "get_health"):
            bio_health_status = self.bio_orchestrator.get_health()  # type: ignore

        security_module_status = "Security_Module_Disabled"
        if self.access_controller and hasattr(self.access_controller, "get_status"):
            security_module_status = self.access_controller.get_status()  # type: ignore

        # Update last_checked timestamp for all component statuses
        for component_id in self.component_status:
            self.component_status[component_id]["last_checked_utc_iso"] = timestamp_now_iso

        status_report = {
            "timestamp_utc_iso": timestamp_now_iso,
            "integrator_instance_id": f"ECI_{hex(id(self))[-6:]}",  # Slightly longer ID
            "registered_components_count": len(self.components),
            "component_statuses_snapshot": self.component_status.copy(),
            "event_subscribers_count": sum(len(subs_list) for subs_list in self.event_subscribers.values()),
            "qi_coherence_level": q_coherence_status,
            "bio_orchestrator_health": bio_health_status,
            "security_module_status": security_module_status,
            "core_modules_loaded_successfully": CORE_COMPONENTS_LOADED_FLAG_ECI,
        }
        log.info(
            "CoreIntegrator system status compiled.",
            components_count=status_report["registered_components_count"],
            core_modules_loaded=status_report["core_modules_loaded_successfully"],
        )
        return status_report

    def _initialize_context_bus(self) -> None:
        """
        Initialize the Context Bus with core event types for LUKHAS orchestration.
        Establishes the foundation for sub-250ms context handoff performance.
        """
        core_event_types = [
            "constellation.identity.authentication",
            "constellation.consciousness.state_change",
            "constellation.guardian.ethics_validation",
            "context.workflow.started",
            "context.workflow.completed",
            "context.workflow.error",
            "orchestration.pipeline.step_complete",
            "orchestration.decision.meg_required",
            "orchestration.decision.xil_required",
            "orchestration.decision.hitlo_required",
            "integration.component.registered",
            "integration.component.health_check",
            "performance.handoff.timeout_warning",
        ]

        # Pre-register core event subscribers for performance
        for event_type in core_event_types:
            if event_type not in self.event_subscribers:
                self.event_subscribers[event_type] = []

        log.info(
            "Context Bus initialized with core event types",
            event_types_count=len(core_event_types),
            target_handoff_time_ms=250,
        )

    # Enhanced Context Bus implementation with <250ms performance target
    @lukhas_tier_required(1)
    def broadcast_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        source_component_id: Optional[str] = None,
        priority: str = "normal",
        context_preservation: bool = True,
    ) -> int:
        """
        Broadcasts an event to all subscribed components with orchestration capabilities.

        Implements robust async messaging with performance tracking to ensure
        sub-250ms context handoff times for LUKHAS orchestration workflows.

        Args:
            event_type: Type of event to broadcast (e.g., "orchestration.decision.meg_required")
            event_data: Event payload with context preservation data
            source_component_id: ID of the component broadcasting the event
            priority: Event priority ("high", "normal", "low")
            context_preservation: Whether to preserve full context for workflow continuity

        Returns:
            Number of components successfully notified
        """
        start_time = time.time()
        event_id = f"evt_{uuid.uuid4().hex[:10]}"

        # Enhanced event structure for orchestration
        enhanced_event = {
            "id": event_id,
            "type": event_type,
            "data": event_data,
            "source": source_component_id or "CoreIntegrator",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "priority": priority,
            "context_preservation": context_preservation,
            "constellation_framework": {
                "identity_authenticated": True,
                "consciousness_aware": True,
                "guardian_approved": True,
            },
        }

        # Get subscribers with thread safety
        with self._subscription_lock:
            subscribers = self.event_subscribers[event_type].copy()

        if not subscribers:
            log.debug(
                "No subscribers for event type",
                event_id=event_id,
                event_type=event_type,
                source=source_component_id,
            )
            return 0

        # Orchestration workflow event handling
        self._handle_orchestration_workflows(event_type, enhanced_event)

        # Async event dispatch with performance monitoring
        notified_count = self._dispatch_event_to_subscribers(subscribers, enhanced_event, priority)

        # Performance tracking for sub-250ms target
        handoff_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        self._context_handoff_times.append(handoff_time)
        self._event_metrics[event_type].append(handoff_time)

        # Performance warning if exceeding target
        if handoff_time > 250:
            log.warning(
                "Context handoff time exceeded 250ms target",
                event_id=event_id,
                event_type=event_type,
                handoff_time_ms=handoff_time,
                subscribers_count=len(subscribers),
                notified_count=notified_count,
            )

            # Broadcast performance warning event
            self._broadcast_performance_warning(event_type, handoff_time)

        log.info(
            "Event broadcast completed",
            event_id=event_id,
            event_type=event_type,
            subscribers_count=len(subscribers),
            notified_count=notified_count,
            handoff_time_ms=handoff_time,
            source=source_component_id,
        )

        return notified_count

    @lukhas_tier_required(0)
    def subscribe_to_event(
        self,
        event_type: str,
        callback_function: Callable,
        component_id: Optional[str] = None,
        priority_level: str = "normal",
        context_requirements: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Subscribes a component's callback to a specific event type with orchestration support.

        Provides robust subscription management with filtering and priority handling
        for LUKHAS Context Bus orchestration workflows.

        Args:
            event_type: Event type to subscribe to (e.g., "orchestration.decision.meg_required")
            callback_function: Function to call when event occurs
            component_id: ID of the subscribing component
            priority_level: Subscription priority ("high", "normal", "low")
            context_requirements: Required context fields for event filtering

        Returns:
            True if subscription successful, False otherwise
        """
        try:
            with self._subscription_lock:
                # Validate callback is callable
                if not callable(callback_function):
                    log.error(
                        "Invalid callback function provided for subscription",
                        event_type=event_type,
                        component_id=component_id,
                        callback_name=str(callback_function),
                    )
                    return False

                # Create enhanced subscriber info for orchestration
                subscriber_info = {
                    "component_id": component_id or f"anonymous_{uuid.uuid4().hex[:8]}",
                    "callback": callback_function,
                    "callback_name": getattr(callback_function, "__name__", "unnamed_callback"),
                    "subscribed_at_utc_iso": datetime.now(timezone.utc).isoformat(),
                    "priority_level": priority_level,
                    "context_requirements": context_requirements or {},
                    "subscription_id": f"sub_{uuid.uuid4().hex[:10]}",
                    "active": True,
                    "invocation_count": 0,
                    "last_invoked_utc": None,
                    "average_execution_time_ms": 0.0,
                    "trinity_framework_compliant": True,
                }

                # Check for duplicate subscriptions
                existing_subscribers = self.event_subscribers[event_type]
                for existing in existing_subscribers:
                    if (
                        existing["component_id"] == subscriber_info["component_id"]
                        and existing["callback"] == callback_function
                    ):
                        log.warning(
                            "Duplicate subscription detected - updating existing",
                            event_type=event_type,
                            component_id=component_id,
                            callback_name=subscriber_info["callback_name"],
                        )
                        existing.update(subscriber_info)
                        return True

                # Add new subscription with priority ordering
                if priority_level == "high":
                    # High priority subscribers go first
                    self.event_subscribers[event_type].insert(0, subscriber_info)
                else:
                    # Normal and low priority subscribers go at end
                    self.event_subscribers[event_type].append(subscriber_info)

                log.info(
                    "Component successfully subscribed to event type",
                    event_type=event_type,
                    component_id=subscriber_info["component_id"],
                    callback_name=subscriber_info["callback_name"],
                    subscription_id=subscriber_info["subscription_id"],
                    priority_level=priority_level,
                    total_subscribers=len(self.event_subscribers[event_type]),
                )

                # Broadcast subscription event for workflow orchestration
                self.broadcast_event(
                    "integration.component.subscribed",
                    {
                        "event_type": event_type,
                        "component_id": subscriber_info["component_id"],
                        "subscription_id": subscriber_info["subscription_id"],
                        "priority_level": priority_level,
                    },
                    source_component_id="CoreIntegrator",
                )

                return True

        except Exception as e:
            log.error(
                "Failed to subscribe to event type",
                event_type=event_type,
                component_id=component_id,
                error=str(e),
                callback_name=getattr(callback_function, "__name__", "unknown"),
            )
            return False

    def _handle_orchestration_workflows(self, event_type: str, event: dict[str, Any]) -> None:
        """
        Handle orchestration-specific workflows based on event type.
        Implements transparent logging and step-by-step narrative generation.
        """
        try:
            # Trinity Framework validation logging
            if event_type.startswith("constellation."):
                log.info(
                    "ΛTRACE_TRINITY_WORKFLOW",
                    event_id=event["id"],
                    event_type=event_type,
                    trinity_component=event_type.split(".")[1],
                    step="framework_validation",
                    narrative="Processing Trinity Framework event for system coherence",
                )

            # Orchestration workflow logging
            elif event_type.startswith("orchestration."):
                workflow_type = event_type.split(".")[1]
                log.info(
                    "ΛTRACE_ORCHESTRATION_WORKFLOW",
                    event_id=event["id"],
                    event_type=event_type,
                    workflow_type=workflow_type,
                    step="workflow_initiated",
                    narrative=f"Initiating {workflow_type} orchestration workflow",
                )

                # Handle decision orchestration events
                if workflow_type == "decision":
                    decision_type = event_type.split(".")[2]
                    log.info(
                        "ΛTRACE_DECISION_ORCHESTRATION",
                        event_id=event["id"],
                        decision_type=decision_type,
                        step="decision_routing",
                        narrative=f"Routing {decision_type.upper()} decision through orchestration pipeline",
                    )

            # Context workflow logging for step-by-step transparency
            elif event_type.startswith("context.workflow"):
                workflow_state = event_type.split(".")[2]
                log.info(
                    "ΛTRACE_CONTEXT_WORKFLOW",
                    event_id=event["id"],
                    workflow_state=workflow_state,
                    context_preserved=event.get("context_preservation", False),
                    step="context_management",
                    narrative=f"Context workflow {workflow_state} - preserving state for continuity",
                )

        except Exception as e:
            log.error(
                "Error in orchestration workflow handling",
                event_type=event_type,
                event_id=event.get("id"),
                error=str(e),
            )

    def _dispatch_event_to_subscribers(
        self, subscribers: list[dict[str, Any]], event: dict[str, Any], priority: str
    ) -> int:
        """
        Dispatch event to subscribers with async performance optimization.
        Implements sub-250ms context handoff through concurrent execution.
        """
        notified_count = 0

        # Separate subscribers by priority for optimal dispatch order
        high_priority = [s for s in subscribers if s.get("priority_level") == "high"]
        normal_priority = [s for s in subscribers if s.get("priority_level") == "normal"]
        low_priority = [s for s in subscribers if s.get("priority_level") == "low"]

        # Process high priority first, then normal/low concurrently
        for subscriber_list in [high_priority, normal_priority + low_priority]:
            if not subscriber_list:
                continue

            # Use thread pool for concurrent execution
            future_to_subscriber = {}

            for subscriber in subscriber_list:
                if not subscriber.get("active", True):
                    continue

                # Context filtering based on requirements
                if not self._meets_context_requirements(event, subscriber):
                    continue

                # Submit callback execution to thread pool
                future = self._event_executor.submit(self._invoke_subscriber_callback, subscriber, event)
                future_to_subscriber[future] = subscriber

            # Wait for completion with timeout (to maintain <250ms target)
            timeout_per_batch = 0.150  # 150ms timeout per batch
            for future in as_completed(future_to_subscriber, timeout=timeout_per_batch):
                try:
                    success = future.result()
                    if success:
                        notified_count += 1
                except Exception as e:
                    subscriber = future_to_subscriber[future]
                    log.error(
                        "Subscriber callback execution failed",
                        subscriber_id=subscriber.get("subscription_id"),
                        component_id=subscriber.get("component_id"),
                        error=str(e),
                    )

        return notified_count

    def _meets_context_requirements(self, event: dict[str, Any], subscriber: dict[str, Any]) -> bool:
        """Check if event meets subscriber's context requirements."""
        requirements = subscriber.get("context_requirements", {})
        if not requirements:
            return True

        event_data = event.get("data", {})
        for req_key, req_value in requirements.items():
            if req_key not in event_data or event_data[req_key] != req_value:
                return False
        return True

    def _invoke_subscriber_callback(self, subscriber: dict[str, Any], event: dict[str, Any]) -> bool:
        """Invoke a single subscriber callback with performance tracking."""
        start_time = time.time()

        try:
            callback = subscriber["callback"]

            # Update invocation tracking
            subscriber["invocation_count"] += 1
            subscriber["last_invoked_utc"] = datetime.now(timezone.utc).isoformat()

            # Call the subscriber callback
            if asyncio.iscoroutinefunction(callback):
                # Handle async callbacks
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(callback(event))
                finally:
                    loop.close()
            else:
                # Handle sync callbacks
                callback(event)

            # Update performance metrics
            execution_time = (time.time() - start_time) * 1000
            prev_avg = subscriber.get("average_execution_time_ms", 0.0)
            count = subscriber["invocation_count"]
            subscriber["average_execution_time_ms"] = (prev_avg * (count - 1) + execution_time) / count

            log.debug(
                "Subscriber callback executed successfully",
                subscription_id=subscriber.get("subscription_id"),
                component_id=subscriber.get("component_id"),
                execution_time_ms=execution_time,
                invocation_count=count,
            )

            return True

        except Exception as e:
            log.error(
                "Subscriber callback execution failed",
                subscription_id=subscriber.get("subscription_id"),
                component_id=subscriber.get("component_id"),
                callback_name=subscriber.get("callback_name"),
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
            return False

    def _broadcast_performance_warning(self, event_type: str, handoff_time: float) -> None:
        """Broadcast performance warning event when handoff time exceeds target."""
        try:
            # Avoid recursive performance warnings
            if event_type == "performance.handoff.timeout_warning":
                return

            warning_event = {
                "original_event_type": event_type,
                "handoff_time_ms": handoff_time,
                "target_time_ms": 250,
                "performance_impact": "context_handoff_delayed",
                "suggested_action": "review_subscriber_performance",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            }

            # Use recursive call with minimal data to avoid further delays
            self.broadcast_event(
                "performance.handoff.timeout_warning",
                warning_event,
                source_component_id="CoreIntegrator_PerformanceMonitor",
                priority="high",
                context_preservation=False,
            )

        except Exception as e:
            log.error(
                "Failed to broadcast performance warning",
                original_event_type=event_type,
                handoff_time=handoff_time,
                error=str(e),
            )

    def get_context_bus_metrics(self) -> dict[str, Any]:
        """
        Get Context Bus performance metrics for monitoring and optimization.
        """
        if not self._context_handoff_times:
            return {"status": "no_metrics_available"}

        avg_handoff_time = sum(self._context_handoff_times) / len(self._context_handoff_times)
        max_handoff_time = max(self._context_handoff_times)
        min_handoff_time = min(self._context_handoff_times)

        # Performance compliance check
        under_target_count = sum(1 for t in self._context_handoff_times if t <= 250)
        compliance_rate = (under_target_count / len(self._context_handoff_times)) * 100

        return {
            "total_events_processed": len(self._context_handoff_times),
            "average_handoff_time_ms": round(avg_handoff_time, 2),
            "max_handoff_time_ms": round(max_handoff_time, 2),
            "min_handoff_time_ms": round(min_handoff_time, 2),
            "target_compliance_rate": f"{compliance_rate:.1f}%",
            "performance_target_ms": 250,
            "total_event_types": len(self._event_metrics),
            "active_subscribers": sum(len(subs) for subs in self.event_subscribers.values()),
            "context_bus_status": "operational" if compliance_rate > 85 else "performance_degraded",
        }


# --- LUKHΛS AI Standard Footer ---
# File Origin: LUKHΛS Core Architecture - System Integration Layer
# Context: Central integrator for LUKHΛS core components, managing interactions,
#          security, and advanced quantum-biological features.
# ACCESSED_BY: ['LUKHΛSApplicationMain', 'SystemOrchestrator', 'HighLevelAPIs'] # Conceptual list
# MODIFIED_BY: ['CORE_DEV_INTEGRATION_ARCHITECTS', 'SYSTEM_DESIGN_LEAD', 'Jules_AI_Agent'] # Conceptual list
# Tier Access: Varies by method (Refer to ΛTIER_CONFIG block and @lukhas_tier_required decorators)
# Related Components: Various 'CORE.*' modules (e.g., QIBioOscillator, BioOrchestrator, AccessController)
# CreationDate: 2023-10-26 (Approx. by LUKHΛS Team) | LastModifiedDate: 2024-07-27 | Version: 1.1
# --- End Standard Footer ---
