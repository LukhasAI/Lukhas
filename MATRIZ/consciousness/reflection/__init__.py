"""MATRIZ consciousness reflection modules."""

# Import modules individually to avoid circular dependency issues
try:
    from matriz.consciousness.reflection import id_reasoning_engine
except ImportError:
    id_reasoning_engine = None

try:
    from matriz.consciousness.reflection import swarm
except ImportError:
    swarm = None

try:
    from matriz.consciousness.reflection import orchestration_service
except ImportError:
    orchestration_service = None

try:
    from matriz.consciousness.reflection import memory_hub
except ImportError:
    memory_hub = None

try:
    from matriz.consciousness.reflection import dreamseed_unified
except ImportError:
    dreamseed_unified = None

try:
    from matriz.consciousness.reflection import reflection_layer
except ImportError:
    reflection_layer = None

try:
    from matriz.consciousness.reflection import symbolic_drift_analyzer
except ImportError:
    symbolic_drift_analyzer = None

try:
    from matriz.consciousness.reflection import integrated_safety_system
except ImportError:
    integrated_safety_system = None

__all__ = [
    "dreamseed_unified",
    "id_reasoning_engine",
    "memory_hub",
    "orchestration_service",
    "reflection_layer",
    "swarm",
    "symbolic_drift_analyzer",
    "integrated_safety_system",
]
