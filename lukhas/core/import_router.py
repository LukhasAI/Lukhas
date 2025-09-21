"""
LUKHAS AI Import Router
Smart import resolution system with fallback chains
Constellation Framework: ⚛️🧠🛡️

This module provides a future-proof import system that handles:
- Lane transitions (lukhas → candidate → legacy)
- Module relocations and renames
- Deprecation warnings
- Alternative class names
"""

import importlib
import importlib.util
import logging
from typing import Any, ClassVar, Optional

try:
    from prometheus_client import Counter
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Router fallback metrics
if METRICS_AVAILABLE:
    _ROUTER_FALLBACK_TOTAL = Counter(
        "lukhas_router_fallback_total",
        "Total router fallback attempts",
        ["source_module", "target_module", "outcome"]
    )
    _ROUTER_DEPRECATION_WARNINGS = Counter(
        "lukhas_router_deprecation_warnings_total",
        "Total deprecation warnings issued by router",
        ["deprecated_module", "canonical_module"]
    )
    _ROUTER_RESOLUTION_TOTAL = Counter(
        "lukhas_router_resolution_total",
        "Total router resolution attempts",
        ["module_type", "lane", "success"]
    )
else:
    _ROUTER_FALLBACK_TOTAL = None
    _ROUTER_DEPRECATION_WARNINGS = None
    _ROUTER_RESOLUTION_TOTAL = None


class ModuleRouter:
    """
    Intelligent module router that handles import resolution across lanes.
    """

    # Module mapping: canonical path -> list of alternative paths
    MODULE_REGISTRY: ClassVar[dict[str, list[str]]] = {
        # Core modules
        "lukhas.core.actor_system": [
            "candidate.core.actor_system",
            "core.actor_system",
        ],
        "lukhas.core.colonies": [
            "candidate.core.colonies",
            "candidate.colonies",
            "core.colonies",
        ],
        # Bio modules
        "lukhas.bio.utilities": [
            "candidate.bio.bio_utilities",
            "bio.bio_utilities",
            "bio.utilities",
        ],
        "lukhas.bio.core.bio_symbolic": [
            "candidate.core.symbolic.symbolic_bio_symbolic",
            "candidate.consciousness.unified.symbolic_bio_symbolic_orchestrator",
            "bio.core.symbolic_bio_symbolic",
        ],
        # Memory modules
        "lukhas.memory.emotional": [
            "candidate.memory.emotional_memory_manager_unified",
            "candidate.memory.systems.emotional_memory_manager",
            "candidate.consciousness.states.emotional_memory_manager",
            "memory.emotional",
        ],
        # QI modules
        "qi.bio.bio_integration": [
            "candidate.qi.bio",
            "candidate.qi.bio.bio_coordinator",
            "qi.bio",
        ],
        "qi.processing.qi_coordinator": [
            "candidate.qi.processing.qi_coordinator",
            "candidate.qi.processing.qi_engine",
        ],
        "qi.systems.consciousness_integration": [
            "candidate.qi.engines.consciousness.engine",
            "candidate.qi.states.integration",
        ],
        # Bridge modules
        "lukhas.bridge.openai_core_service": [
            "candidate.bridge.openai_core_service",
            "bridge.openai_core_service",
        ],
        # Communication modules
        "lukhas.core.efficient_communication": [
            "candidate.core.efficient_communication",
            "core.communication",
        ],
    }

    # Class name mappings: requested name -> (module, actual name)
    CLASS_ALIASES: ClassVar[dict[str, tuple[str, str]]] = {
        "AIAgentActor": ("lukhas.core.actor_system", "AIAgentActor"),
        "BaseColony": ("lukhas.core.colonies", "BaseColony"),
        "ConsensusResult": ("lukhas.core.colonies", "ConsensusResult"),
        "EfficientCommunicationFabric": (
            "lukhas.core.colonies",
            "EfficientCommunicationFabric",
        ),
        "SupervisorAgent": ("lukhas.core.colonies", "SupervisorAgent"),
    }

    def __init__(self) -> None:
        self._import_cache = {}
        self._resolve_cache: dict[str, Optional[str]] = {}
        self._deprecation_warnings = set()

    def resolve_module_path(self, module_path: str) -> Optional[str]:
        """
        Resolve a module path to its actual location.

        Args:
            module_path: The requested module path

        Returns:
            The actual module path that exists, or None if not found
        """
        # Serve from cache when available
        if module_path in self._resolve_cache:
            return self._resolve_cache[module_path]

        # Check if it's a canonical path
        if module_path in self.MODULE_REGISTRY:
            paths_to_try = [module_path] + self.MODULE_REGISTRY[module_path]
        else:
            # Check if it's an alternative path
            for canonical, alternatives in self.MODULE_REGISTRY.items():
                if module_path in alternatives:
                    paths_to_try = [canonical, *alternatives]
                    break
            else:
                paths_to_try = [module_path]

        # Try each path
        for path in paths_to_try:
            if importlib.util.find_spec(path) is None:
                continue
            importlib.import_module(path)
            if path != module_path and module_path not in self._deprecation_warnings:
                self._deprecation_warnings.add(module_path)
                logger.info(f"Module '{module_path}' resolved to '{path}'")
            self._resolve_cache[module_path] = path
            return path

        self._resolve_cache[module_path] = None
        return None

    def import_module(self, module_path: str, raise_on_error: bool = True) -> Optional[Any]:
        """
        Import a module with fallback resolution.

        Args:
            module_path: The module path to import
            raise_on_error: Whether to raise ImportError if module not found

        Returns:
            The imported module or None if not found
        """
        # Check cache first
        if module_path in self._import_cache:
            return self._import_cache[module_path]

        # Resolve the actual path
        actual_path = self.resolve_module_path(module_path)

        # Record resolution attempt metrics
        module_type = self._classify_module_type(module_path)
        lane = self._extract_lane(module_path)
        success = actual_path is not None

        if _ROUTER_RESOLUTION_TOTAL:
            _ROUTER_RESOLUTION_TOTAL.labels(
                module_type=module_type,
                lane=lane,
                success=str(success).lower()
            ).inc()

        if actual_path:
            # Record fallback metrics if using alternative path
            if actual_path != module_path:
                outcome = "success"
                if _ROUTER_FALLBACK_TOTAL:
                    _ROUTER_FALLBACK_TOTAL.labels(
                        source_module=module_path,
                        target_module=actual_path,
                        outcome=outcome
                    ).inc()

                # Check if this is a deprecated path
                if module_path in self.MODULE_REGISTRY:
                    if _ROUTER_DEPRECATION_WARNINGS:
                        _ROUTER_DEPRECATION_WARNINGS.labels(
                            deprecated_module=module_path,
                            canonical_module=actual_path
                        ).inc()

            try:
                module = importlib.import_module(actual_path)
                self._import_cache[module_path] = module
                return module
            except ImportError as err:
                # Record failed fallback
                if actual_path != module_path and _ROUTER_FALLBACK_TOTAL:
                    _ROUTER_FALLBACK_TOTAL.labels(
                        source_module=module_path,
                        target_module=actual_path,
                        outcome="import_failed"
                    ).inc()

                # Bind exception to a named variable for safe raise-from usage
                if raise_on_error:
                    raise ImportError(f"Failed to import '{module_path}' (resolved to '{actual_path}'): {err}") from err
                logger.warning(f"Failed to import '{module_path}': {err}")
                return None
        elif raise_on_error:
            raise ImportError(f"Module '{module_path}' not found in registry or filesystem")
        else:
            logger.warning(f"Module '{module_path}' not found")
            return None

    def import_class(self, class_name: str, module_hint: Optional[str] = None) -> Optional[Any]:
        """
        Import a class by name, with optional module hint.

        Args:
            class_name: Name of the class to import
            module_hint: Optional module path hint

        Returns:
            The class object or None if not found
        """
        # Check if we have an alias for this class
        if class_name in self.CLASS_ALIASES:
            module_path, actual_name = self.CLASS_ALIASES[class_name]
            module = self.import_module(module_path, raise_on_error=False)
            if module and hasattr(module, actual_name):
                return getattr(module, actual_name)

        # Try with module hint
        if module_hint:
            module = self.import_module(module_hint, raise_on_error=False)
            if module and hasattr(module, class_name):
                return getattr(module, class_name)

        # Search in common locations
        common_modules = [
            "lukhas.core.actor_system",
            "lukhas.core.colonies",
            "candidate.core.actor_system",
            "candidate.core.colonies.base_colony",
        ]

        for module_path in common_modules:
            module = self.import_module(module_path, raise_on_error=False)
            if module and hasattr(module, class_name):
                logger.debug(f"Found class '{class_name}' in '{module_path}'")
                return getattr(module, class_name)

        logger.warning(f"Class '{class_name}' not found")
        return None

    def _classify_module_type(self, module_path: str) -> str:
        """Classify module type for metrics"""
        if ".core." in module_path:
            return "core"
        elif ".memory." in module_path:
            return "memory"
        elif ".consciousness." in module_path:
            return "consciousness"
        elif ".bridge." in module_path:
            return "bridge"
        elif ".qi." in module_path:
            return "qi"
        else:
            return "other"

    def _extract_lane(self, module_path: str) -> str:
        """Extract lane from module path"""
        if module_path.startswith("lukhas."):
            return "production"
        elif module_path.startswith("candidate."):
            return "candidate"
        elif module_path.startswith("experimental."):
            return "experimental"
        else:
            return "unknown"

    def add_module_mapping(self, canonical_path: str, alternative_paths: list[str]) -> None:
        """
        Add a new module mapping to the registry.

        Args:
            canonical_path: The canonical module path
            alternative_paths: List of alternative paths
        """
        if canonical_path in self.MODULE_REGISTRY:
            self.MODULE_REGISTRY[canonical_path].extend(alternative_paths)
        else:
            self.MODULE_REGISTRY[canonical_path] = alternative_paths

        # Clear cache to reflect new mapping
        self._resolve_cache.clear()

    def add_class_alias(self, class_name: str, module_path: str, actual_name: Optional[str] = None) -> None:
        """
        Add a class alias mapping.

        Args:
            class_name: The alias name
            module_path: The module containing the class
            actual_name: The actual class name (if different from alias)
        """
        self.CLASS_ALIASES[class_name] = (module_path, actual_name or class_name)


# Global router instance
_router = ModuleRouter()


# Convenience functions
def import_with_fallback(module_path: str, fallback_paths: Optional[list[str]] = None) -> Any:
    """
    Import a module with fallback paths.

    Args:
        module_path: Primary module path
        fallback_paths: Optional list of fallback paths

    Returns:
        The imported module
    """
    if fallback_paths:
        _router.add_module_mapping(module_path, fallback_paths)

    return _router.import_module(module_path)


def import_class(class_name: str, module_hint: Optional[str] = None) -> Any:
    """
    Import a class by name.

    Args:
        class_name: Name of the class
        module_hint: Optional module path hint

    Returns:
        The class object
    """
    return _router.import_class(class_name, module_hint)


def resolve_import(import_str: str) -> Any:
    """
    Resolve an import string like 'module.path:ClassName'.

    Args:
        import_str: Import string in format 'module.path:ClassName'

    Returns:
        The imported object
    """
    if ":" in import_str:
        module_path, obj_name = import_str.split(":", 1)
        module = _router.import_module(module_path)
        if module and hasattr(module, obj_name):
            return getattr(module, obj_name)
    else:
        return _router.import_module(import_str)

    raise ImportError(f"Could not resolve import: {import_str}")


def add_module_mapping(canonical_path: str, alternative_paths: list[str]) -> None:
    """Add a module mapping to the global router."""
    _router.add_module_mapping(canonical_path, alternative_paths)


def add_class_alias(class_name: str, module_path: str, actual_name: Optional[str] = None) -> None:
    """Add a class alias to the global router."""
    _router.add_class_alias(class_name, module_path, actual_name)


# Export public interface
__all__ = [
    "ModuleRouter",
    "add_class_alias",
    "add_module_mapping",
    "import_class",
    "import_with_fallback",
    "resolve_import",
]
