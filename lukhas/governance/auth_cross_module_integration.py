#!/usr/bin/env python3

"""
🔗 ΛiD Cross-Module Integration System
=====================================

Enables ΛiD authentication system to communicate with other LUKHAS modules
via GLYPH protocol and Trinity Framework integration. Provides seamless
authentication context sharing across consciousness, memory, reasoning,
and other LUKHAS AI modules.

This module provides:
- Cross-module GLYPH communication
- Trinity Framework integration
- Authentication context propagation
- Module-specific authentication adapters
- Consciousness-aware authentication
- Memory-integrated identity persistence

Author: LUKHAS AI System
Version: 1.0.0
Trinity Framework: ⚛️🧠🛡️
"""

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

# LUKHAS imports
try:
    from ..core.glyph.glyph_engine import GlyphEngine
    from ..orchestration.symbolic_kernel_bus import SymbolicKernelBus
    from .auth_glyph_registry import auth_glyph_registry
    from .auth_guardian_integration import AuthenticationGuardian, AuthEventType
except ImportError:
    # Fallback for development
    auth_glyph_registry = None
    AuthenticationGuardian = None
    AuthEventType = None
    GlyphEngine = None
    SymbolicKernelBus = None


class ModuleType(Enum):
    """LUKHAS AI module types"""

    CONSCIOUSNESS = "consciousness"
    MEMORY = "memory"
    REASONING = "reasoning"
    EMOTION = "emotion"
    CREATIVITY = "creativity"
    QUANTUM = "quantum"
    BIO = "bio"
    IDENTITY = "identity"
    GUARDIAN = "guardian"
    BRIDGE = "bridge"
    CORE = "core"


class AuthMessageType(Enum):
    """Authentication message types for cross-module communication"""

    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    TIER_CHANGE = "tier_change"
    SCOPE_UPDATE = "scope_update"
    IDENTITY_UPDATE = "identity_update"
    SECURITY_ALERT = "security_alert"
    CONSTITUTIONAL_VIOLATION = "constitutional_violation"
    BIAS_DETECTED = "bias_detected"
    GUARDIAN_ALERT = "guardian_alert"


@dataclass
class AuthModuleMessage:
    """Authentication message for cross-module communication"""

    id: str
    message_type: AuthMessageType
    source_module: ModuleType
    target_module: ModuleType
    user_id: str
    session_id: Optional[str]
    glyph_encoding: str
    payload: dict[str, Any]
    trinity_context: dict[str, str]
    timestamp: datetime
    priority: str = "normal"  # low, normal, high, critical
    requires_response: bool = False
    correlation_id: Optional[str] = None


@dataclass
class ModuleAuthContext:
    """Authentication context for a specific module"""

    module_type: ModuleType
    user_id: str
    tier_level: str
    scopes: list[str]
    session_id: str
    symbolic_identity: str
    constitutional_status: str
    guardian_status: str
    last_updated: datetime
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TrinityFrameworkIntegration:
    """
    ⚛️🧠🛡️ Trinity Framework Authentication Integration

    Aligns authentication with Trinity Framework principles across all modules.
    """

    def __init__(self):
        """Initialize Trinity Framework integration"""
        self.trinity_aspects = {
            "identity": "⚛️",  # Identity aspect
            "consciousness": "🧠",  # Consciousness aspect
            "guardian": "🛡️",  # Guardian aspect
        }

        self.module_trinity_mapping = {
            ModuleType.CONSCIOUSNESS: "consciousness",
            ModuleType.MEMORY: "consciousness",
            ModuleType.REASONING: "consciousness",
            ModuleType.EMOTION: "consciousness",
            ModuleType.CREATIVITY: "consciousness",
            ModuleType.IDENTITY: "identity",
            ModuleType.QUANTUM: "identity",
            ModuleType.BIO: "identity",
            ModuleType.GUARDIAN: "guardian",
            ModuleType.BRIDGE: "guardian",
            ModuleType.CORE: "guardian",
        }

    def get_trinity_context_for_module(
        self, module_type: ModuleType, auth_context: dict[str, Any]
    ) -> dict[str, str]:
        """Get Trinity Framework context for specific module"""
        primary_aspect = self.module_trinity_mapping.get(module_type, "identity")

        # Determine emphasis based on authentication context
        if auth_context.get("guardian_alert", False):
            emphasis = "guardian"
        elif auth_context.get("consciousness_integration", False):
            emphasis = "consciousness"
        else:
            emphasis = "identity"

        return {
            "primary_aspect": primary_aspect,
            "emphasis": emphasis,
            "symbol": self.trinity_aspects[emphasis],
            "framework": "⚛️🧠🛡️",
            "integration_level": self._calculate_integration_level(auth_context),
        }

    def _calculate_integration_level(self, auth_context: dict[str, Any]) -> str:
        """Calculate Trinity Framework integration level"""
        score = 0

        # Identity integration
        if auth_context.get("symbolic_identity"):
            score += 1

        # Consciousness integration
        if auth_context.get("consciousness_aware", False):
            score += 1

        # Guardian integration
        if auth_context.get("guardian_monitoring", False):
            score += 1

        if score >= 3:
            return "full"
        elif score >= 2:
            return "partial"
        elif score >= 1:
            return "basic"
        else:
            return "minimal"


class AuthCrossModuleIntegrator:
    """
    🔗 Authentication Cross-Module Integrator

    Manages authentication context sharing and GLYPH communication
    across all LUKHAS AI modules with Trinity Framework alignment.
    """

    def __init__(self):
        """Initialize cross-module integration system"""
        self.glyph_engine = GlyphEngine() if GlyphEngine else None
        self.kernel_bus = SymbolicKernelBus() if SymbolicKernelBus else None
        self.trinity_integration = TrinityFrameworkIntegration()

        # Module registrations and contexts
        self.registered_modules: dict[ModuleType, dict[str, Any]] = {}
        self.active_contexts: dict[str, ModuleAuthContext] = {}  # user_id -> context
        self.message_handlers: dict[ModuleType, Callable] = {}
        self.pending_messages: list[AuthModuleMessage] = []

        # Integration statistics
        self.integration_stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "active_sessions": 0,
            "module_connections": 0,
            "last_updated": datetime.now(),
        }

        # Initialize module adapters
        self._initialize_module_adapters()

    def _initialize_module_adapters(self) -> None:
        """Initialize adapters for different module types"""
        self.module_adapters = {
            ModuleType.CONSCIOUSNESS: self._create_consciousness_adapter(),
            ModuleType.MEMORY: self._create_memory_adapter(),
            ModuleType.REASONING: self._create_reasoning_adapter(),
            ModuleType.EMOTION: self._create_emotion_adapter(),
            ModuleType.CREATIVITY: self._create_creativity_adapter(),
            ModuleType.QUANTUM: self._create_quantum_adapter(),
            ModuleType.BIO: self._create_bio_adapter(),
            ModuleType.IDENTITY: self._create_identity_adapter(),
            ModuleType.GUARDIAN: self._create_guardian_adapter(),
            ModuleType.BRIDGE: self._create_bridge_adapter(),
            ModuleType.CORE: self._create_core_adapter(),
        }

    async def register_module(
        self,
        module_type: ModuleType,
        module_config: dict[str, Any],
        message_handler: Optional[Callable] = None,
    ) -> bool:
        """Register a LUKHAS module for authentication integration"""
        try:
            # Register module
            self.registered_modules[module_type] = {
                "config": module_config,
                "registered_at": datetime.now(),
                "active": True,
                "message_count": 0,
                "last_message": None,
            }

            # Register message handler
            if message_handler:
                self.message_handlers[module_type] = message_handler

            # Update statistics
            self.integration_stats["module_connections"] = len(self.registered_modules)
            self.integration_stats["last_updated"] = datetime.now()

            # Send registration confirmation
            if auth_glyph_registry:
                registration_glyph = auth_glyph_registry.get_cross_module_glyph_message(
                    target_module=module_type.value,
                    message_type="module_registered",
                    auth_context={"module_type": module_type.value},
                )

                await self._send_internal_message(
                    module_type,
                    "registration_confirmed",
                    {
                        "glyph": registration_glyph,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            return True

        except Exception as e:
            print(f"Error registering module {module_type.value}: {e}")
            return False

    async def propagate_auth_context(
        self,
        user_id: str,
        auth_event: AuthEventType,
        auth_context: dict[str, Any],
        target_modules: Optional[list[ModuleType]] = None,
    ) -> dict[str, bool]:
        """Propagate authentication context to LUKHAS modules"""
        try:
            results = {}

            # Determine target modules
            if target_modules is None:
                target_modules = list(self.registered_modules.keys())

            # Create module auth context
            module_context = await self._create_module_auth_context(user_id, auth_context)

            # Store context
            self.active_contexts[user_id] = module_context

            # Send to each target module
            for module_type in target_modules:
                if module_type in self.registered_modules:
                    success = await self._send_auth_context_to_module(
                        module_type, user_id, auth_event, auth_context
                    )
                    results[module_type.value] = success
                else:
                    results[module_type.value] = False

            # Update statistics
            self.integration_stats["messages_sent"] += len(target_modules)
            self.integration_stats["active_sessions"] = len(self.active_contexts)

            return results

        except Exception as e:
            print(f"Error propagating auth context: {e}")
            return {}

    async def _create_module_auth_context(
        self, user_id: str, auth_context: dict[str, Any]
    ) -> ModuleAuthContext:
        """Create authentication context for module consumption"""
        # Extract key authentication information
        tier_level = auth_context.get("tier_level", "T1")
        scopes = auth_context.get("scopes", [])
        session_id = auth_context.get("session_id", str(uuid.uuid4()))

        # Get symbolic identity
        symbolic_identity = "GLYPH[DEFAULT]"
        if auth_glyph_registry:
            symbolic_identity_obj = auth_glyph_registry.symbolic_identities.get(user_id)
            if symbolic_identity_obj:
                symbolic_identity = symbolic_identity_obj.composite_glyph

        # Determine constitutional and guardian status
        constitutional_status = (
            "valid" if auth_context.get("constitutional_valid", True) else "violation"
        )
        guardian_status = (
            "monitoring" if auth_context.get("guardian_monitoring", False) else "inactive"
        )

        return ModuleAuthContext(
            module_type=ModuleType.CORE,  # Will be updated per module
            user_id=user_id,
            tier_level=tier_level,
            scopes=scopes,
            session_id=session_id,
            symbolic_identity=symbolic_identity,
            constitutional_status=constitutional_status,
            guardian_status=guardian_status,
            last_updated=datetime.now(),
            metadata=auth_context,
        )

    async def _send_auth_context_to_module(
        self,
        module_type: ModuleType,
        user_id: str,
        auth_event: AuthEventType,
        auth_context: dict[str, Any],
    ) -> bool:
        """Send authentication context to specific module"""
        try:
            # Get module adapter
            adapter = self.module_adapters.get(module_type)
            if not adapter:
                return False

            # Get Trinity context for module
            trinity_context = self.trinity_integration.get_trinity_context_for_module(
                module_type, auth_context
            )

            # Create GLYPH message
            glyph_message = "GLYPH[DEFAULT]"
            if auth_glyph_registry:
                glyph_message = auth_glyph_registry.get_cross_module_glyph_message(
                    target_module=module_type.value,
                    message_type=auth_event.value,
                    auth_context=auth_context,
                )

            # Create module message
            message = AuthModuleMessage(
                id=str(uuid.uuid4()),
                message_type=AuthMessageType(auth_event.value),
                source_module=ModuleType.IDENTITY,
                target_module=module_type,
                user_id=user_id,
                session_id=auth_context.get("session_id"),
                glyph_encoding=glyph_message,
                payload=await adapter["prepare_payload"](auth_context),
                trinity_context=trinity_context,
                timestamp=datetime.now(),
                priority=self._determine_message_priority(auth_event),
            )

            # Send message
            success = await self._deliver_message(message)

            # Update module statistics
            if success and module_type in self.registered_modules:
                self.registered_modules[module_type]["message_count"] += 1
                self.registered_modules[module_type]["last_message"] = datetime.now()

            return success

        except Exception as e:
            print(f"Error sending auth context to {module_type.value}: {e}")
            return False

    def _determine_message_priority(self, auth_event: AuthEventType) -> str:
        """Determine message priority based on authentication event"""
        high_priority_events = {
            AuthEventType.CONSTITUTIONAL_VIOLATION,
            AuthEventType.BIAS_DETECTION,
            AuthEventType.LOGIN_FAILURE,
        }

        critical_priority_events = {
            AuthEventType.CONSTITUTIONAL_VIOLATION,
        }

        if auth_event in critical_priority_events:
            return "critical"
        elif auth_event in high_priority_events:
            return "high"
        else:
            return "normal"

    async def _deliver_message(self, message: AuthModuleMessage) -> bool:
        """Deliver message to target module"""
        try:
            # Try kernel bus first
            if self.kernel_bus:
                success = await self._send_via_kernel_bus(message)
                if success:
                    return True

            # Try direct module handler
            handler = self.message_handlers.get(message.target_module)
            if handler:
                await handler(message)
                return True

            # Store for later delivery
            self.pending_messages.append(message)
            return False

        except Exception as e:
            print(f"Error delivering message {message.id}: {e}")
            return False

    async def _send_via_kernel_bus(self, message: AuthModuleMessage) -> bool:
        """Send message via LUKHAS symbolic kernel bus"""
        try:
            if not self.kernel_bus:
                return False

            # Convert to kernel bus format
            kernel_message = {
                "type": "auth_context",
                "source": "lambda_auth",
                "target": message.target_module.value,
                "user_id": message.user_id,
                "session_id": message.session_id,
                "glyph": message.glyph_encoding,
                "payload": message.payload,
                "trinity": message.trinity_context,
                "timestamp": message.timestamp.isoformat(),
                "priority": message.priority,
            }

            await self.kernel_bus.publish(f"auth.{message.target_module.value}", kernel_message)
            return True

        except Exception as e:
            print(f"Error sending via kernel bus: {e}")
            return False

    async def _send_internal_message(
        self, target_module: ModuleType, message_type: str, payload: dict[str, Any]
    ) -> None:
        """Send internal system message"""
        try:
            message = AuthModuleMessage(
                id=str(uuid.uuid4()),
                message_type=AuthMessageType.AUTH_SUCCESS,  # Generic type
                source_module=ModuleType.IDENTITY,
                target_module=target_module,
                user_id="system",
                session_id=None,
                glyph_encoding="GLYPH[SYSTEM]",
                payload=payload,
                trinity_context={"aspect": "system", "symbol": "⚙️"},
                timestamp=datetime.now(),
                priority="normal",
            )

            await self._deliver_message(message)

        except Exception as e:
            print(f"Error sending internal message: {e}")

    # Module Adapter Creation Methods

    def _create_consciousness_adapter(self) -> dict[str, Callable]:
        """Create consciousness module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "consciousness_integration": True,
                "user_identity": auth_context.get("user_id"),
                "awareness_level": auth_context.get("tier_level", "T1"),
                "cognitive_permissions": auth_context.get("scopes", []),
                "consciousness_state": "authenticated",
                "trinity_aspect": "consciousness",
                "symbolic_identity": auth_context.get("symbolic_identity"),
                "memory_access": "consciousness:access" in auth_context.get("scopes", []),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.CONSCIOUSNESS,
            "trinity_aspect": "consciousness",
        }

    def _create_memory_adapter(self) -> dict[str, Callable]:
        """Create memory module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "memory_integration": True,
                "user_identity": auth_context.get("user_id"),
                "memory_permissions": [s for s in auth_context.get("scopes", []) if "memory:" in s],
                "fold_access_level": auth_context.get("tier_level", "T1"),
                "identity_persistence": True,
                "symbolic_memory": auth_context.get("symbolic_identity"),
                "consciousness_aware": True,
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.MEMORY,
            "trinity_aspect": "consciousness",
        }

    def _create_reasoning_adapter(self) -> dict[str, Callable]:
        """Create reasoning module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "reasoning_integration": True,
                "user_context": auth_context.get("user_id"),
                "reasoning_scope": auth_context.get("scopes", []),
                "logic_tier": auth_context.get("tier_level", "T1"),
                "constitutional_reasoning": auth_context.get("constitutional_valid", True),
                "bias_aware": True,
                "symbolic_logic": auth_context.get("symbolic_identity"),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.REASONING,
            "trinity_aspect": "consciousness",
        }

    def _create_emotion_adapter(self) -> dict[str, Callable]:
        """Create emotion module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "emotion_integration": True,
                "user_emotional_context": auth_context.get("user_id"),
                "emotional_permissions": auth_context.get("scopes", []),
                "mood_tier": auth_context.get("tier_level", "T1"),
                "constitutional_emotion": auth_context.get("constitutional_valid", True),
                "empathy_enabled": True,
                "symbolic_emotion": auth_context.get("symbolic_identity"),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.EMOTION,
            "trinity_aspect": "consciousness",
        }

    def _create_creativity_adapter(self) -> dict[str, Callable]:
        """Create creativity module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "creativity_integration": True,
                "creative_user": auth_context.get("user_id"),
                "creative_permissions": auth_context.get("scopes", []),
                "creative_tier": auth_context.get("tier_level", "T1"),
                "constitutional_creativity": auth_context.get("constitutional_valid", True),
                "imagination_enabled": True,
                "symbolic_creativity": auth_context.get("symbolic_identity"),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.CREATIVITY,
            "trinity_aspect": "consciousness",
        }

    def _create_quantum_adapter(self) -> dict[str, Callable]:
        """Create quantum module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "qi_integration": True,
                "qi_user": auth_context.get("user_id"),
                "qi_permissions": auth_context.get("scopes", []),
                "qi_tier": auth_context.get("tier_level", "T1"),
                "qi_identity": auth_context.get("symbolic_identity"),
                "entanglement_enabled": True,
                "superposition_access": "quantum:" in str(auth_context.get("scopes", [])),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.QUANTUM,
            "trinity_aspect": "identity",
        }

    def _create_bio_adapter(self) -> dict[str, Callable]:
        """Create bio module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "bio_integration": True,
                "bio_user": auth_context.get("user_id"),
                "bio_permissions": auth_context.get("scopes", []),
                "bio_tier": auth_context.get("tier_level", "T1"),
                "bio_identity": auth_context.get("symbolic_identity"),
                "adaptation_enabled": True,
                "oscillation_access": "bio:" in str(auth_context.get("scopes", [])),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.BIO,
            "trinity_aspect": "identity",
        }

    def _create_identity_adapter(self) -> dict[str, Callable]:
        """Create identity module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "identity_integration": True,
                "lambda_id": auth_context.get("user_id"),
                "identity_permissions": auth_context.get("scopes", []),
                "identity_tier": auth_context.get("tier_level", "T1"),
                "symbolic_self": auth_context.get("symbolic_identity"),
                "autonomy_enabled": True,
                "self_modification": "identity:" in str(auth_context.get("scopes", [])),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.IDENTITY,
            "trinity_aspect": "identity",
        }

    def _create_guardian_adapter(self) -> dict[str, Callable]:
        """Create guardian module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "guardian_integration": True,
                "protected_user": auth_context.get("user_id"),
                "guardian_permissions": auth_context.get("scopes", []),
                "protection_tier": auth_context.get("tier_level", "T1"),
                "guardian_identity": auth_context.get("symbolic_identity"),
                "monitoring_enabled": True,
                "ethical_oversight": auth_context.get("constitutional_valid", True),
                "bias_detection": auth_context.get("bias_flags", []),
                "drift_score": auth_context.get("drift_score", 0.0),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.GUARDIAN,
            "trinity_aspect": "guardian",
        }

    def _create_bridge_adapter(self) -> dict[str, Callable]:
        """Create bridge module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "bridge_integration": True,
                "bridged_user": auth_context.get("user_id"),
                "bridge_permissions": auth_context.get("scopes", []),
                "bridge_tier": auth_context.get("tier_level", "T1"),
                "bridge_identity": auth_context.get("symbolic_identity"),
                "communication_enabled": True,
                "api_access": "api:" in str(auth_context.get("scopes", [])),
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.BRIDGE,
            "trinity_aspect": "guardian",
        }

    def _create_core_adapter(self) -> dict[str, Callable]:
        """Create core module adapter"""

        async def prepare_payload(auth_context: dict[str, Any]) -> dict[str, Any]:
            return {
                "core_integration": True,
                "core_user": auth_context.get("user_id"),
                "core_permissions": auth_context.get("scopes", []),
                "core_tier": auth_context.get("tier_level", "T1"),
                "core_identity": auth_context.get("symbolic_identity"),
                "system_access": True,
                "glyph_enabled": True,
                "trinity_integrated": True,
            }

        return {
            "prepare_payload": prepare_payload,
            "module_type": ModuleType.CORE,
            "trinity_aspect": "guardian",
        }

    async def get_user_module_contexts(self, user_id: str) -> dict[str, Any]:
        """Get authentication contexts for user across all modules"""
        context = self.active_contexts.get(user_id)
        if not context:
            return {}

        module_contexts = {}
        for module_type in self.registered_modules:
            adapter = self.module_adapters.get(module_type)
            if adapter:
                module_contexts[module_type.value] = await adapter["prepare_payload"](
                    context.metadata
                )

        return {
            "user_id": user_id,
            "base_context": asdict(context),
            "module_contexts": module_contexts,
            "trinity_integration": self.trinity_integration.get_trinity_context_for_module(
                ModuleType.CORE, context.metadata
            ),
            "last_updated": datetime.now().isoformat(),
        }

    async def cleanup_user_contexts(self, user_id: str) -> bool:
        """Clean up authentication contexts for user"""
        try:
            # Remove active context
            if user_id in self.active_contexts:
                del self.active_contexts[user_id]

            # Send cleanup messages to all modules
            cleanup_results = await self.propagate_auth_context(
                user_id=user_id,
                auth_event=AuthEventType.SESSION_END,
                auth_context={"cleanup": True, "user_id": user_id},
            )

            # Update statistics
            self.integration_stats["active_sessions"] = len(self.active_contexts)

            return all(cleanup_results.values())

        except Exception as e:
            print(f"Error cleaning up contexts for user {user_id}: {e}")
            return False

    def get_integration_status(self) -> dict[str, Any]:
        """Get cross-module integration status"""
        return {
            "registered_modules": len(self.registered_modules),
            "active_contexts": len(self.active_contexts),
            "pending_messages": len(self.pending_messages),
            "module_types": [m.value for m in self.registered_modules],
            "trinity_integration": True,
            "glyph_communication": auth_glyph_registry is not None,
            "kernel_bus_available": self.kernel_bus is not None,
            "statistics": self.integration_stats,
            "last_updated": datetime.now().isoformat(),
        }


# Global cross-module integrator instance
auth_cross_module_integrator = AuthCrossModuleIntegrator()


# Export main classes and instance
__all__ = [
    "AuthCrossModuleIntegrator",
    "AuthMessageType",
    "AuthModuleMessage",
    "ModuleAuthContext",
    "ModuleType",
    "TrinityFrameworkIntegration",
    "auth_cross_module_integrator",
]
