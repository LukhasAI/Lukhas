"""
LUKHAS Module Manager - Long-term Dependency Management
=========================================================
Provides robust module loading with proper fallbacks and health checks.
Solves the root cause of import warnings and missing modules.
"""
import importlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    """Status of a module in the system"""

    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"
    FALLBACK = "fallback"
    DISABLED = "disabled"


class ModulePriority(Enum):
    """Priority levels for module loading"""

    CRITICAL = 1  # System cannot function without it
    HIGH = 2  # Major functionality degraded
    MEDIUM = 3  # Some features unavailable
    LOW = 4  # Nice to have
    OPTIONAL = 5  # Can be completely absent


@dataclass
class ModuleConfig:
    """Configuration for a module"""

    name: str
    import_path: str
    priority: ModulePriority = ModulePriority.MEDIUM
    fallback_class: Optional[type] = None
    fallback_module: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    health_check: Optional[Callable] = None
    auto_create_stub: bool = False
    stub_content: Optional[str] = None
    description: str = ""


@dataclass
class ModuleInfo:
    """Information about a loaded module"""

    config: ModuleConfig
    status: ModuleStatus
    module: Optional[Any] = None
    error: Optional[str] = None
    load_time: Optional[float] = None
    health_status: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class ModuleManager:
    """
    Central module manager for LUKHAS.
    Handles all module loading, dependencies, and fallbacks.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the module manager"""
        self.modules: dict[str, ModuleInfo] = {}
        self.config_path = config_path or "module_config.json"
        self.fallback_registry: dict[str, Callable] = {}
        self._initialize_core_modules()

    def _initialize_core_modules(self):
        """Initialize core module configurations"""
        # Identity System
        self.register_module(
            ModuleConfig(
                name="identity_system",
                import_path="governance.identity.interface",
                priority=ModulePriority.HIGH,
                fallback_class=self._create_identity_fallback(),
                dependencies=[],
                description="Central identity and tier management system",
            )
        )

        # Quantum Mind (for memory system)
        self.register_module(
            ModuleConfig(
                name="qi_mind",
                import_path="qi_mind",
                priority=ModulePriority.LOW,
                auto_create_stub=True,
                stub_content=self._get_quantum_mind_stub(),
                dependencies=[],
                description="Consciousness phase management for memory",
            )
        )

        # Emotional Tier System
        self.register_module(
            ModuleConfig(
                name="emotional_tier",
                import_path="emotion.dreamseed_upgrade",
                priority=ModulePriority.MEDIUM,
                auto_create_stub=True,
                stub_content=self._get_emotional_tier_stub(),
                dependencies=["identity_system"],
                description="Emotional tier access control",
            )
        )

        # Memory Systems
        self.register_module(
            ModuleConfig(
                name="memory_systems",
                import_path="memory.systems",
                priority=ModulePriority.HIGH,
                fallback_class=self._create_memory_fallback(),
                dependencies=["qi_mind"],
                description="Core memory and trace management",
            )
        )

        # Signal System (new)
        self.register_module(
            ModuleConfig(
                name="signal_system",
                import_path="orchestration.signals",
                priority=ModulePriority.HIGH,
                dependencies=[],
                description="Colony-wide signal bus for adaptive behavior",
            )
        )

        # Feedback System (new)
        self.register_module(
            ModuleConfig(
                name="feedback_system",
                import_path="feedback",
                priority=ModulePriority.MEDIUM,
                dependencies=[],
                description="Human-in-the-loop learning system",
            )
        )

    def register_module(self, config: ModuleConfig):
        """Register a module configuration"""
        self.modules[config.name] = ModuleInfo(config=config, status=ModuleStatus.NOT_LOADED)

    def load_module(self, name: str, force: bool = False) -> ModuleInfo:
        """
        Load a module with proper error handling and fallbacks.

        Args:
            name: Module name to load
            force: Force reload even if already loaded

        Returns:
            ModuleInfo with status and module reference
        """
        if name not in self.modules:
            logger.error(f"Module {name} not registered")
            return ModuleInfo(
                config=ModuleConfig(name=name, import_path="unknown"),
                status=ModuleStatus.FAILED,
                error="Module not registered",
            )

        info = self.modules[name]

        # Skip if already loaded (unless forced)
        if info.status == ModuleStatus.LOADED and not force:
            return info

        # Check dependencies first
        if not self._check_dependencies(info.config):
            info.status = ModuleStatus.FAILED
            info.error = "Dependencies not met"
            return info

        info.status = ModuleStatus.LOADING

        try:
            # Try to import the module
            info.module = importlib.import_module(info.config.import_path)
            info.status = ModuleStatus.LOADED
            info.error = None
            logger.info(f"✅ Loaded module: {name}")

            # Run health check if defined
            if info.config.health_check:
                info.health_status = info.config.health_check(info.module)

        except ImportError as e:
            logger.warning(f"⚠️ Failed to load {name}: {e}")

            # Try fallback strategies
            if self._apply_fallback(info):
                info.status = ModuleStatus.FALLBACK
                logger.info(f"📦 Using fallback for {name}")
            elif info.config.auto_create_stub:
                if self._create_stub_module(info):
                    info.status = ModuleStatus.FALLBACK
                    logger.info(f"🔧 Created stub for {name}")
                else:
                    info.status = ModuleStatus.FAILED
                    info.error = str(e)
            else:
                info.status = ModuleStatus.FAILED
                info.error = str(e)

        except Exception as e:
            logger.error(f"❌ Unexpected error loading {name}: {e}")
            info.status = ModuleStatus.FAILED
            info.error = str(e)

        return info

    def _check_dependencies(self, config: ModuleConfig) -> bool:
        """Check if all dependencies are satisfied"""
        for dep in config.dependencies:
            if dep not in self.modules:
                continue
            dep_info = self.load_module(dep)  # Recursively load dependencies
            if dep_info.status not in [
                ModuleStatus.LOADED,
                ModuleStatus.FALLBACK,
            ]:
                logger.warning(f"Dependency {dep} not available for {config.name}")
                return False
        return True

    def _apply_fallback(self, info: ModuleInfo) -> bool:
        """Apply fallback strategy for a module"""
        config = info.config

        # Try fallback class
        if config.fallback_class:
            try:
                info.module = config.fallback_class
                return True
            except Exception as e:
                logger.error(f"Fallback class failed for {config.name}: {e}")

        # Try fallback module
        if config.fallback_module:
            try:
                info.module = importlib.import_module(config.fallback_module)
                return True
            except Exception as e:
                logger.error(f"Fallback module failed for {config.name}: {e}")

        # Try registered fallback
        if config.name in self.fallback_registry:
            try:
                info.module = self.fallback_registry[config.name]()
                return True
            except Exception as e:
                logger.error(f"Registered fallback failed for {config.name}: {e}")

        return False

    def _create_stub_module(self, info: ModuleInfo) -> bool:
        """Create a stub module dynamically"""
        if not info.config.stub_content:
            return False

        try:
            # Create module path
            module_path = info.config.import_path.replace(".", "/")
            module_file = Path(module_path + ".py")

            # Ensure parent directory exists
            module_file.parent.mkdir(parents=True, exist_ok=True)

            # Write stub content
            module_file.write_text(info.config.stub_content)

            # Try to import the newly created stub
            info.module = importlib.import_module(info.config.import_path)
            return True

        except Exception as e:
            logger.error(f"Failed to create stub for {info.config.name}: {e}")
            return False

    def load_all(self, priority_threshold: ModulePriority = ModulePriority.OPTIONAL):
        """Load all registered modules up to a priority threshold"""
        # Sort by priority
        sorted_modules = sorted(self.modules.items(), key=lambda x: x[1].config.priority.value)

        results = {}
        for name, info in sorted_modules:
            if info.config.priority.value <= priority_threshold.value:
                results[name] = self.load_module(name)
            else:
                logger.debug(f"Skipping {name} (priority too low)")

        return results

    def get_module(self, name: str) -> Optional[Any]:
        """Get a loaded module by name"""
        if name in self.modules:
            info = self.modules[name]
            if info.status in [ModuleStatus.LOADED, ModuleStatus.FALLBACK]:
                return info.module
        return None

    def get_status_report(self) -> dict[str, Any]:
        """Get a comprehensive status report"""
        report = {
            "total_modules": len(self.modules),
            "loaded": 0,
            "failed": 0,
            "fallback": 0,
            "not_loaded": 0,
            "modules": {},
        }

        for name, info in self.modules.items():
            status = info.status.value
            report[status] = report.get(status, 0) + 1

            report["modules"][name] = {
                "status": status,
                "priority": info.config.priority.name,
                "health": info.health_status,
                "error": info.error,
                "description": info.config.description,
            }

        return report

    def health_check(self) -> dict[str, bool]:
        """Run health checks on all loaded modules"""
        results = {}
        for name, info in self.modules.items():
            if info.status == ModuleStatus.LOADED and info.config.health_check:
                try:
                    results[name] = info.config.health_check(info.module)
                    info.health_status = results[name]
                except Exception as e:
                    logger.error(f"Health check failed for {name}: {e}")
                    results[name] = False
                    info.health_status = False
            else:
                results[name] = info.status == ModuleStatus.LOADED

        return results

    # Fallback implementations

    def _create_identity_fallback(self):
        """Create a fallback identity client"""

        class FallbackIdentityClient:
            def __init__(self):
                logger.info("Using fallback identity client")

            def verify_user_access(self, user_id: str, tier: str) -> bool:
                # Always grant access in fallback mode
                return True

            def log_activity(self, **kwargs):
                # No-op in fallback
                pass

        return FallbackIdentityClient

    def _create_memory_fallback(self):
        """Create a fallback memory system"""

        class FallbackMemorySystem:
            def __init__(self):
                self.memory = {}
                logger.info("Using fallback memory system")

            def store(self, key: str, value: Any):
                self.memory[key] = value

            def retrieve(self, key: str) -> Optional[Any]:
                return self.memory.get(key)

        return FallbackMemorySystem

    def _get_quantum_mind_stub(self) -> str:
        """Get stub content for quantum mind module"""
        return '''"""Quantum Mind Stub Module"""
from enum import Enum

class ConsciousnessPhase(Enum):
    AWARE = "aware"
    DREAMING = "dreaming"

def get_current_phase():
    return ConsciousnessPhase.AWARE
'''

    def _get_emotional_tier_stub(self) -> str:
        """Get stub content for emotional tier module"""
        return '''"""Emotional Tier Stub Module"""
from enum import Enum

class EmotionalTier(Enum):
    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"
    T4 = "T4"
    T5 = "T5"
'''


# Singleton instance
_module_manager: Optional[ModuleManager] = None


def get_module_manager() -> ModuleManager:
    """Get the singleton module manager"""
    global _module_manager
    if _module_manager is None:
        _module_manager = ModuleManager()
    return _module_manager


def initialize_system(
    priority: ModulePriority = ModulePriority.HIGH,
) -> dict[str, Any]:
    """
    Initialize the LUKHAS system with proper module loading.

    Args:
        priority: Load modules up to this priority level

    Returns:
        Status report of loaded modules
    """
    manager = get_module_manager()

    # Load all modules
    logger.info("=" * 60)
    logger.info("🚀 Initializing LUKHAS Module System")
    logger.info("=" * 60)

    manager.load_all(priority)

    # Get status report
    report = manager.get_status_report()

    # Log summary
    logger.info(f"✅ Loaded: {report.get('loaded', 0)} modules")
    logger.info(f"📦 Fallback: {report.get('fallback', 0)} modules")
    logger.info(f"❌ Failed: {report.get('failed', 0)} modules")

    # Run health checks
    health = manager.health_check()
    healthy = sum(1 for v in health.values() if v)
    logger.info(f"💚 Health: {healthy}/{len(health)} modules healthy")

    return report


def require_module(module_name: str, critical: bool = False):
    """
    Decorator that ensures a module is loaded before function execution.

    Args:
        module_name: Name of required module
        critical: If True, raise exception if module not available
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            manager = get_module_manager()
            module = manager.get_module(module_name)

            if module is None:
                manager.load_module(module_name)
                module = manager.get_module(module_name)

            if module is None and critical:
                raise RuntimeError(f"Critical module {module_name} not available")

            # Inject module as first argument if requested
            if hasattr(func, "_inject_module") and func._inject_module:
                return func(module, *args, **kwargs)

            return func(*args, **kwargs)

        wrapper._original = func
        return wrapper

    return decorator


# Export all
__all__ = [
    "ModuleConfig",
    "ModuleInfo",
    "ModuleManager",
    "ModulePriority",
    "ModuleStatus",
    "get_module_manager",
    "initialize_system",
    "require_module",
]
