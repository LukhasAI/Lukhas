from __future__ import annotations

import inspect
from importlib import import_module

from core.common import get_logger

# TAG:bridge
# TAG:protocols
# TAG:neuroplastic
# TAG:colony
# LUKHAS_TAG: freeze_protection, core_trace

logger = get_logger(__name__)


def is_locked(obj):
    """
    Checks if an object is locked.
    """
    return bool(hasattr(obj, "__doc__") and obj.__doc__ and "LOCKED: true" in obj.__doc__)


def freeze_protection_check(module):
    """
    Verifies that the LOCKED tags are respected in a module.
    """
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) or inspect.isfunction(obj):
            if is_locked(obj):
                logger.info(f"Object {name} is locked.")
            else:
                logger.warning(f"Object {name} is not locked.")


if __name__ == "__main__":
    module_path = "core.orchestration.brain.orchestration.core"
    try:
        orchestration_module = import_module(module_path)
    except ModuleNotFoundError:
        logger.warning("Orchestration module '%s' not available; skipping check", module_path)
    else:
        target = getattr(orchestration_module, "cognitive_brain_orchestrator", orchestration_module)
        freeze_protection_check(target)
