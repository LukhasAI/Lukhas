"""Bridge: memory (namespace) with preserved submodule search path."""
from __future__ import annotations

from importlib import import_module
from collections.abc import Iterable

__all__: list[str] = []

_CANDIDATES: tuple[str, ...] = (
    "lukhas_website.memory",
    "labs.memory",
    "memory",
)


def _public_names(module: object) -> Iterable[str]:
    names = getattr(module, "__all__", None)
    if names:
        return list(names)
    return [name for name in dir(module) if not name.startswith("_")]


_backend = None
for _path in _CANDIDATES:
    try:
        _backend = import_module(_path)
    except Exception:
        continue
    else:
        break

if _backend is not None:
    for _name in _public_names(_backend):
        globals()[_name] = getattr(_backend, _name)
        __all__.append(_name)

    backend_path = list(getattr(_backend, "__path__", []))
    search_locations = list(getattr(__spec__, "submodule_search_locations", []) or [])
    for _location in backend_path:
        if _location not in search_locations:
            search_locations.append(_location)
    try:
        import memory as _root_memory  # pylint: disable=cyclic-import
    except Exception:
        _root_memory = None  # pragma: no cover - missing root package
    if _root_memory is not None:
        for _location in getattr(_root_memory, "__path__", []):
            if _location not in search_locations:
                search_locations.append(_location)
    if search_locations:
        __path__ = search_locations  # type: ignore[assignment]


# Bridge export for memory.ISOLATED_FILES_ASSESSMENT
try:
    from labs.memory import ISOLATED_FILES_ASSESSMENT
except (ImportError, SyntaxError):
    def ISOLATED_FILES_ASSESSMENT(*args, **kwargs):
        """Stub for ISOLATED_FILES_ASSESSMENT."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "ISOLATED_FILES_ASSESSMENT" not in __all__:
    __all__.append("ISOLATED_FILES_ASSESSMENT")


# Bridge export for memory.agimemory_fake
try:
    from labs.memory import agimemory_fake
except (ImportError, SyntaxError):
    def agimemory_fake(*args, **kwargs):
        """Stub for agimemory_fake."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "agimemory_fake" not in __all__:
    __all__.append("agimemory_fake")


# Bridge export for memory.base_manager
try:
    from labs.memory import base_manager
except (ImportError, SyntaxError):
    def base_manager(*args, **kwargs):
        """Stub for base_manager."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "base_manager" not in __all__:
    __all__.append("base_manager")


# Bridge export for memory.colony_memory_validator
try:
    from labs.memory import colony_memory_validator
except (ImportError, SyntaxError):
    def colony_memory_validator(*args, **kwargs):
        """Stub for colony_memory_validator."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "colony_memory_validator" not in __all__:
    __all__.append("colony_memory_validator")


# Bridge export for memory.dream_memory_fold
try:
    from labs.memory import dream_memory_fold
except (ImportError, SyntaxError):
    def dream_memory_fold(*args, **kwargs):
        """Stub for dream_memory_fold."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "dream_memory_fold" not in __all__:
    __all__.append("dream_memory_fold")


# Bridge export for memory.dreamseed_example
try:
    from labs.memory import dreamseed_example
except (ImportError, SyntaxError):
    def dreamseed_example(*args, **kwargs):
        """Stub for dreamseed_example."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "dreamseed_example" not in __all__:
    __all__.append("dreamseed_example")


# Bridge export for memory.event_replayer
try:
    from labs.memory import event_replayer
except (ImportError, SyntaxError):
    def event_replayer(*args, **kwargs):
        """Stub for event_replayer."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "event_replayer" not in __all__:
    __all__.append("event_replayer")


# Bridge export for memory.fold_engine
try:
    from labs.memory import fold_engine
except (ImportError, SyntaxError):
    def fold_engine(*args, **kwargs):
        """Stub for fold_engine."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "fold_engine" not in __all__:
    __all__.append("fold_engine")


# Bridge export for memory.healix_mapper
try:
    from labs.memory import healix_mapper
except (ImportError, SyntaxError):
    def healix_mapper(*args, **kwargs):
        """Stub for healix_mapper."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "healix_mapper" not in __all__:
    __all__.append("healix_mapper")


# Bridge export for memory.memory_endpoints
try:
    from labs.memory import memory_endpoints
except (ImportError, SyntaxError):
    def memory_endpoints(*args, **kwargs):
        """Stub for memory_endpoints."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "memory_endpoints" not in __all__:
    __all__.append("memory_endpoints")


# Bridge export for memory.memory_fold
try:
    from labs.memory import memory_fold
except (ImportError, SyntaxError):
    def memory_fold(*args, **kwargs):
        """Stub for memory_fold."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "memory_fold" not in __all__:
    __all__.append("memory_fold")


# Bridge export for memory.memory_systems_integration_test
try:
    from labs.memory import memory_systems_integration_test
except (ImportError, SyntaxError):
    def memory_systems_integration_test(*args, **kwargs):
        """Stub for memory_systems_integration_test."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "memory_systems_integration_test" not in __all__:
    __all__.append("memory_systems_integration_test")


# Bridge export for memory.openai_memory_adapter
try:
    from labs.memory import openai_memory_adapter
except (ImportError, SyntaxError):
    def openai_memory_adapter(*args, **kwargs):
        """Stub for openai_memory_adapter."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "openai_memory_adapter" not in __all__:
    __all__.append("openai_memory_adapter")


# Bridge export for memory.optimized_fold_engine
try:
    from labs.memory import optimized_fold_engine
except (ImportError, SyntaxError):
    def optimized_fold_engine(*args, **kwargs):
        """Stub for optimized_fold_engine."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "optimized_fold_engine" not in __all__:
    __all__.append("optimized_fold_engine")


# Bridge export for memory.qi_memory_manager
try:
    from labs.memory import qi_memory_manager
except (ImportError, SyntaxError):
    def qi_memory_manager(*args, **kwargs):
        """Stub for qi_memory_manager."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "qi_memory_manager" not in __all__:
    __all__.append("qi_memory_manager")


# Bridge export for memory.rem
try:
    from labs.memory import rem
except (ImportError, SyntaxError):
    def rem(*args, **kwargs):
        """Stub for rem."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "rem" not in __all__:
    __all__.append("rem")


# Bridge export for memory.scaffold_modules_reasoning_engine
try:
    from labs.memory import scaffold_modules_reasoning_engine
except (ImportError, SyntaxError):
    def scaffold_modules_reasoning_engine(*args, **kwargs):
        """Stub for scaffold_modules_reasoning_engine."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "scaffold_modules_reasoning_engine" not in __all__:
    __all__.append("scaffold_modules_reasoning_engine")


# Bridge export for memory.services
try:
    from labs.memory import services
except (ImportError, SyntaxError):
    def services(*args, **kwargs):
        """Stub for services."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "services" not in __all__:
    __all__.append("services")


# Bridge export for memory.smart_consolidation
try:
    from labs.memory import smart_consolidation
except (ImportError, SyntaxError):
    def smart_consolidation(*args, **kwargs):
        """Stub for smart_consolidation."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "smart_consolidation" not in __all__:
    __all__.append("smart_consolidation")


# Bridge export for memory.trait_sync
try:
    from labs.memory import trait_sync
except (ImportError, SyntaxError):
    def trait_sync(*args, **kwargs):
        """Stub for trait_sync."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "trait_sync" not in __all__:
    __all__.append("trait_sync")


# Bridge export for memory.unified_memory_core
try:
    from labs.memory import unified_memory_core
except (ImportError, SyntaxError):
    def unified_memory_core(*args, **kwargs):
        """Stub for unified_memory_core."""
        return None

try:
    __all__  # type: ignore[name-defined]
except NameError:
    __all__ = []
if "unified_memory_core" not in __all__:
    __all__.append("unified_memory_core")
