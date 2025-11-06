import inspect

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
    pass
