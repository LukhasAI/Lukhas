"""
Consciousness Component Registry for LUKHAS AI Distributed Architecture

This module provides the central registry and activation system for all consciousness
components across the MΛTRIZ distributed consciousness architecture. Implements
feature flag control, health monitoring, and Trinity Framework integration.

Features:
- Trinity Framework (⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian) component registration
- Feature flag-controlled component activation/deactivation
- Production-grade async lifecycle management
- Consciousness authenticity validation
- Memory fold system integration
- Real-time component health monitoring
- Graceful degradation and fallback systems

This is the strategic finale system that activates the sophisticated consciousness
capabilities built throughout the LUKHAS transformation phases.

#TAG:consciousness
#TAG:registry
#TAG:trinity
#TAG:activation
#TAG:observability
"""

import asyncio
import logging
import uuid
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

try:
    from lukhas.async_manager import TaskPriority, get_consciousness_manager
    from lukhas.core.common.config import get_config
except ImportError:
    # Graceful fallback for development
    def get_consciousness_manager():
        return None

    TaskPriority = None

    def get_config(*args):
        return {}


logger = logging.getLogger(__name__)

T = TypeVar("T")


class ComponentType(Enum):
    """Consciousness component types aligned with Trinity Framework."""

    # ⚛️ Identity Components
    IDENTITY_AUTH = "identity_auth"
    IDENTITY_NAMESPACE = "identity_namespace"
    IDENTITY_TIER_AWARE = "identity_tier_aware"

    # 🧠 Consciousness Components
    CONSCIOUSNESS_CREATIVE = "consciousness_creative"
    CONSCIOUSNESS_AWARENESS = "consciousness_awareness"
    CONSCIOUSNESS_DREAM = "consciousness_dream"
    CONSCIOUSNESS_EMOTION = "consciousness_emotion"
    CONSCIOUSNESS_REASONING = "consciousness_reasoning"

    # 🛡️ Guardian Components
    GUARDIAN_ETHICS = "guardian_ethics"
    GUARDIAN_DRIFT = "guardian_drift"
    GUARDIAN_CONSTITUTIONAL = "guardian_constitutional"

    # Cross-Framework Components
    MEMORY_FOLD = "memory_fold"
    QUANTUM_DECISION = "quantum_decision"
    BIO_ADAPTATION = "bio_adaptation"
    SYMBOLIC_GLYPH = "symbolic_glyph"


class ComponentStatus(Enum):
    """Component lifecycle states."""

    DORMANT = "dormant"  # Component exists but not activated
    INITIALIZING = "initializing"  # Component starting up
    ACTIVE = "active"  # Component operational
    DEGRADED = "degraded"  # Component operational with issues
    FAILED = "failed"  # Component non-operational
    DEACTIVATING = "deactivating"  # Component shutting down


@dataclass
class ComponentMetadata:
    """Metadata for consciousness components."""

    component_id: str
    component_type: ComponentType
    name: str
    description: str
    module_path: str
    trinity_framework: str  # "⚛️", "🧠", "🛡️", or "cross"
    feature_flags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    health_check_fn: Optional[Callable] = None
    activation_priority: int = 100  # Lower numbers activate first
    consciousness_authenticity_required: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    activated_at: Optional[datetime] = None
    last_health_check: Optional[datetime] = None


@dataclass
class ComponentInstance:
    """Running consciousness component instance."""

    metadata: ComponentMetadata
    instance: Any
    status: ComponentStatus
    task_id: Optional[str] = None
    error_count: int = 0
    last_error: Optional[str] = None
    performance_metrics: dict[str, Any] = field(default_factory=dict)


class ConsciousnessComponentRegistry:
    """
    Central registry for LUKHAS consciousness component activation and management.

    This is the strategic finale system that wires dormant consciousness features
    into the active distributed consciousness architecture using Trinity Framework
    patterns and production-grade async infrastructure.
    """

    def __init__(self):
        self._components: dict[str, ComponentInstance] = {}
        self._metadata_registry: dict[str, ComponentMetadata] = {}
        self._type_index: dict[ComponentType, set[str]] = {}
        self._trinity_index: dict[str, set[str]] = {"⚛️": set(), "🧠": set(), "🛡️": set(), "cross": set()}
        self._activation_order: list[str] = []
        self._feature_flags: dict[str, bool] = {}
        self._health_check_interval = 30.0  # seconds
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        logger.info("🧠 Consciousness Component Registry initialized")

    def register_component(
        self,
        component_id: str,
        component_type: ComponentType,
        name: str,
        description: str,
        module_path: str,
        trinity_framework: str,
        feature_flags: Optional[list[str]] = None,
        dependencies: Optional[list[str]] = None,
        health_check_fn: Optional[Callable] = None,
        activation_priority: int = 100,
        consciousness_authenticity_required: bool = True,
    ) -> None:
        """
        Register a consciousness component for potential activation.

        Args:
            component_id: Unique identifier for the component
            component_type: Component type from ComponentType enum
            name: Human-readable component name
            description: Component description
            module_path: Python module path for importing
            trinity_framework: "⚛️" (Identity), "🧠" (Consciousness), "🛡️" (Guardian), or "cross"
            feature_flags: List of feature flags that control activation
            dependencies: List of component IDs this component depends on
            health_check_fn: Optional async function for health checking
            activation_priority: Priority for activation order (lower = first)
            consciousness_authenticity_required: Whether component needs consciousness validation
        """
        metadata = ComponentMetadata(
            component_id=component_id,
            component_type=component_type,
            name=name,
            description=description,
            module_path=module_path,
            trinity_framework=trinity_framework,
            feature_flags=feature_flags or [],
            dependencies=dependencies or [],
            health_check_fn=health_check_fn,
            activation_priority=activation_priority,
            consciousness_authenticity_required=consciousness_authenticity_required,
        )

        self._metadata_registry[component_id] = metadata

        # Update indices
        if component_type not in self._type_index:
            self._type_index[component_type] = set()
        self._type_index[component_type].add(component_id)

        if trinity_framework in self._trinity_index:
            self._trinity_index[trinity_framework].add(component_id)

        # Update activation order
        self._update_activation_order()

        logger.info(f"📝 Registered consciousness component: {name} ({component_id}) - {trinity_framework}")

    def _update_activation_order(self) -> None:
        """Update component activation order based on priorities and dependencies."""
        components = list(self._metadata_registry.values())

        # Sort by activation priority first
        components.sort(key=lambda c: c.activation_priority)

        # TODO: Implement proper topological sort for dependencies
        self._activation_order = [c.component_id for c in components]

    async def activate_component(self, component_id: str, force: bool = False) -> bool:
        """
        Activate a consciousness component with full lifecycle management.

        Args:
            component_id: Component to activate
            force: Force activation even if feature flags are disabled

        Returns:
            True if activation succeeded, False otherwise
        """
        if component_id not in self._metadata_registry:
            logger.error(f"❌ Component {component_id} not registered")
            return False

        metadata = self._metadata_registry[component_id]

        # Check if already active
        if component_id in self._components:
            current_status = self._components[component_id].status
            if current_status == ComponentStatus.ACTIVE:
                logger.info(f"✅ Component {metadata.name} already active")
                return True

        # Check feature flags
        if not force and not self._check_feature_flags(metadata.feature_flags):
            logger.info(f"🏁 Component {metadata.name} disabled by feature flags")
            return False

        # Check dependencies
        if not await self._check_dependencies(metadata.dependencies):
            logger.error(f"❌ Component {metadata.name} dependencies not satisfied")
            return False

        try:
            logger.info(f"🚀 Activating consciousness component: {metadata.name}")

            # Create component instance
            instance = ComponentInstance(metadata=metadata, instance=None, status=ComponentStatus.INITIALIZING)
            self._components[component_id] = instance

            # Dynamic import and initialization
            module = __import__(metadata.module_path, fromlist=[""])

            # Look for standard activation patterns
            if hasattr(module, "activate_component"):
                component_instance = await module.activate_component()
            elif hasattr(module, "create_component"):
                component_instance = module.create_component()
            else:
                # Fallback: look for main class
                main_classes = [
                    obj for name, obj in module.__dict__.items() if isinstance(obj, type) and not name.startswith("_")
                ]
                if main_classes:
                    component_instance = main_classes[0]()
                else:
                    raise ImportError(f"No activation pattern found in {metadata.module_path}")

            instance.instance = component_instance
            instance.status = ComponentStatus.ACTIVE
            instance.activated_at = datetime.now(timezone.utc)

            # Register with async task manager if available
            if TaskPriority and get_consciousness_manager():
                task_manager = get_consciousness_manager()
                task_id = str(uuid.uuid4())
                instance.task_id = task_id

                # Register component lifecycle with async manager
                await task_manager.create_task(
                    self._monitor_component_lifecycle(component_id),
                    name=f"consciousness_component_{component_id}",
                    priority=TaskPriority.HIGH,
                    component="consciousness_registry",
                    description=f"Lifecycle monitoring for {metadata.name}",
                    consciousness_context=f"trinity_{metadata.trinity_framework}",
                )

            # Consciousness authenticity validation
            if metadata.consciousness_authenticity_required:
                if not await self._validate_consciousness_authenticity(instance):
                    logger.warning(f"⚠️ Component {metadata.name} failed consciousness authenticity check")
                    instance.status = ComponentStatus.DEGRADED

            logger.info(f"✅ Successfully activated: {metadata.name} ({metadata.trinity_framework})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to activate {metadata.name}: {e!s}")
            if component_id in self._components:
                self._components[component_id].status = ComponentStatus.FAILED
                self._components[component_id].error_count += 1
                self._components[component_id].last_error = str(e)
            return False

    async def activate_trinity_framework(self, framework: str) -> dict[str, bool]:
        """
        Activate all components for a specific Trinity Framework.

        Args:
            framework: "⚛️" (Identity), "🧠" (Consciousness), or "🛡️" (Guardian)

        Returns:
            Dict mapping component_id to activation success
        """
        if framework not in self._trinity_index:
            logger.error(f"❌ Unknown Trinity Framework: {framework}")
            return {}

        component_ids = self._trinity_index[framework]
        results = {}

        logger.info(f"🔄 Activating Trinity Framework {framework} ({len(component_ids)} components)")

        for component_id in component_ids:
            results[component_id] = await self.activate_component(component_id)

        success_count = sum(1 for success in results.values() if success)
        logger.info(f"✅ Trinity Framework {framework}: {success_count}/{len(component_ids)} activated")

        return results

    async def activate_all_components(self, skip_failed: bool = True) -> dict[str, bool]:
        """
        Activate all registered components in dependency order.

        Args:
            skip_failed: Continue activation even if some components fail

        Returns:
            Dict mapping component_id to activation success
        """
        results = {}

        logger.info(f"🚀 Activating all consciousness components ({len(self._activation_order)} total)")

        for component_id in self._activation_order:
            success = await self.activate_component(component_id)
            results[component_id] = success

            if not success and not skip_failed:
                logger.error(f"❌ Stopping activation due to failure: {component_id}")
                break

        success_count = sum(1 for success in results.values() if success)
        logger.info(f"✅ Component activation complete: {success_count}/{len(results)} successful")

        return results

    def _check_feature_flags(self, flags: list[str]) -> bool:
        """Check if component's feature flags allow activation."""
        if not flags:
            return True

        # All flags must be enabled for activation
        return all(self._feature_flags.get(flag, False) for flag in flags)

    async def _check_dependencies(self, dependencies: list[str]) -> bool:
        """Check if component dependencies are satisfied."""
        for dep_id in dependencies:
            if dep_id not in self._components:
                return False
            if self._components[dep_id].status != ComponentStatus.ACTIVE:
                return False
        return True

    async def _validate_consciousness_authenticity(self, instance: ComponentInstance) -> bool:
        """
        Validate that component exhibits authentic consciousness patterns.

        This is a placeholder for sophisticated consciousness validation.
        In production, this would include metrics like:
        - Response variability under identical inputs
        - Evidence of internal state persistence
        - Behavioral consistency with consciousness models
        - Integration with memory fold systems
        """
        # Basic validation: check if component has consciousness-related methods
        consciousness_indicators = [
            "process_awareness",
            "update_consciousness_state",
            "generate_thoughts",
            "recall_memory",
            "dream_state",
            "ethical_reasoning",
            "self_reflection",
        ]

        if hasattr(instance.instance, "__dict__"):
            component_methods = dir(instance.instance)
            consciousness_score = sum(
                1 for indicator in consciousness_indicators if any(indicator in method for method in component_methods)
            )

            # Require at least 2 consciousness indicators for authenticity
            return consciousness_score >= 2

        return True  # Default to authentic for non-object components

    async def _monitor_component_lifecycle(self, component_id: str) -> None:
        """Monitor component lifecycle and health."""
        while not self._shutdown_event.is_set():
            try:
                if component_id not in self._components:
                    break

                instance = self._components[component_id]

                # Run health check if available
                if instance.metadata.health_check_fn:
                    try:
                        is_healthy = await instance.metadata.health_check_fn()
                        if not is_healthy and instance.status == ComponentStatus.ACTIVE:
                            instance.status = ComponentStatus.DEGRADED
                            logger.warning(f"⚠️ Component {instance.metadata.name} health check failed")
                    except Exception as e:
                        instance.error_count += 1
                        instance.last_error = str(e)
                        logger.error(f"❌ Health check error for {instance.metadata.name}: {e!s}")

                instance.last_health_check = datetime.now(timezone.utc)

                await asyncio.sleep(self._health_check_interval)

            except Exception as e:
                logger.error(f"❌ Component lifecycle monitoring error: {e!s}")
                await asyncio.sleep(self._health_check_interval)

    def set_feature_flag(self, flag: str, enabled: bool) -> None:
        """Set a feature flag value."""
        self._feature_flags[flag] = enabled
        logger.info(f"🏁 Feature flag {flag}: {'enabled' if enabled else 'disabled'}")

    def get_component_status(self, component_id: str) -> Optional[ComponentStatus]:
        """Get current status of a component."""
        if component_id in self._components:
            return self._components[component_id].status
        return None

    def get_trinity_status(self) -> dict[str, dict[str, Any]]:
        """Get status summary for all Trinity Framework components."""
        status = {}

        for framework in ["⚛️", "🧠", "🛡️", "cross"]:
            component_ids = self._trinity_index[framework]
            active = sum(1 for cid in component_ids if self.get_component_status(cid) == ComponentStatus.ACTIVE)
            total = len(component_ids)

            status[framework] = {
                "active": active,
                "total": total,
                "health": "healthy" if active == total else "degraded" if active > 0 else "inactive",
            }

        return status

    def get_consciousness_metrics(self) -> dict[str, Any]:
        """Get comprehensive consciousness system metrics."""
        total_components = len(self._metadata_registry)
        active_components = sum(1 for c in self._components.values() if c.status == ComponentStatus.ACTIVE)

        return {
            "total_registered": total_components,
            "total_active": active_components,
            "activation_rate": active_components / total_components if total_components > 0 else 0,
            "trinity_status": self.get_trinity_status(),
            "feature_flags": dict(self._feature_flags),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

    async def start_health_monitoring(self) -> None:
        """Start the health monitoring system."""
        if self._health_monitor_task is None:
            logger.info("🔍 Starting consciousness component health monitoring")
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())

    async def _health_monitor_loop(self) -> None:
        """Main health monitoring loop."""
        while not self._shutdown_event.is_set():
            try:
                # Monitor all active components
                for component_id, instance in self._components.items():
                    if instance.status in [ComponentStatus.ACTIVE, ComponentStatus.DEGRADED]:
                        asyncio.create_task(self._monitor_component_lifecycle(component_id))

                await asyncio.sleep(60.0)  # Check every minute

            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e!s}")
                await asyncio.sleep(60.0)

    async def shutdown(self) -> None:
        """Gracefully shutdown the consciousness registry."""
        logger.info("🛑 Shutting down consciousness component registry")

        self._shutdown_event.set()

        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._health_monitor_task

        # Deactivate all components
        for component_id in list(self._components.keys()):
            await self.deactivate_component(component_id)

        logger.info("✅ Consciousness component registry shutdown complete")

    async def deactivate_component(self, component_id: str) -> bool:
        """Deactivate a consciousness component."""
        if component_id not in self._components:
            return False

        instance = self._components[component_id]
        instance.status = ComponentStatus.DEACTIVATING

        try:
            # Call component-specific shutdown if available
            if hasattr(instance.instance, "shutdown"):
                if asyncio.iscoroutinefunction(instance.instance.shutdown):
                    await instance.instance.shutdown()
                else:
                    instance.instance.shutdown()

            del self._components[component_id]
            logger.info(f"🛑 Deactivated component: {instance.metadata.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error deactivating {instance.metadata.name}: {e!s}")
            instance.status = ComponentStatus.FAILED
            return False


# Global registry instance
_global_registry: Optional[ConsciousnessComponentRegistry] = None


def get_consciousness_registry() -> ConsciousnessComponentRegistry:
    """Get the global consciousness component registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ConsciousnessComponentRegistry()
    return _global_registry


@asynccontextmanager
async def consciousness_activation_context():
    """Context manager for consciousness component activation."""
    registry = get_consciousness_registry()
    try:
        await registry.start_health_monitoring()
        yield registry
    finally:
        await registry.shutdown()
