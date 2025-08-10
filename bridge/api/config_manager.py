# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: config_manager.py
# MODULE: core.config_manager
# DESCRIPTION: Provides a legacy compatibility layer and re-exports the LUKHAS AI system configuration.
#              Primarily imports and exposes the 'config' object from .config.
#              Includes basic get/set functions for legacy compatibility.
# DEPENDENCIES: .config, logging
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

from core.common.config import config
from core.common.config import (
    LukhasConfig,  # Import LukhasConfig for type hinting if needed
)

# Initialize logger for ΛTRACE

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony

logger = logging.getLogger("ΛTRACE.core.config_manager")
logger.info("ΛTRACE: Initializing config_manager module.")

# --- Legacy Compatibility Functions ---

# Human-readable comment: Function to get the current configuration object.


def get_config() -> LukhasConfig:
    """
    Returns the global LUKHAS configuration object.
    Provided for legacy compatibility. Direct import of 'config' is preferred.
    """
    logger.debug("ΛTRACE: get_config() called. Returning global 'config' instance.")
    return config

# Human-readable comment: Function to set/update the configuration object (discouraged).


def set_config(new_config: LukhasConfig) -> None:
    """
    Allows replacing the global configuration object.
    This is strongly discouraged for general use and primarily for testing or specific bootstrap scenarios.
    Modifying config at runtime can lead to unpredictable behavior.
    Provided for legacy compatibility.
    Args:
        new_config (LukhasConfig): The new configuration object to set globally.
    """
    global config
    logger.warning(
        "ΛTRACE: set_config() called. Overwriting global 'config' instance. This is generally discouraged."
    )
    if not isinstance(new_config, LukhasConfig):
        logger.error(
            f"ΛTRACE: set_config() failed. Expected LukhasConfig instance,"
            got {type(new_config)}."
        )
        raise TypeError(f"Expected LukhasConfig instance, got {type(new_config)}")
    config = new_config
    logger.info(
        f"ΛTRACE: Global 'config' instance has been updated by set_config(). New tier: {config.tier.value if config else 'N/A'}"
    )

# --- Public API Exposure ---


# Human-readable comment: Defines the public API of this module for `from
# .config_manager import *`.
__all__ = ["config", "get_config", "set_config"]

logger.info(
    f"ΛTRACE: config_manager module initialized. Exposed symbols in __all__: {__all__}"
)

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: config_manager.py
# VERSION: 1.0.0
# TIER SYSTEM: Applicable to all Tiers (Configuration management utility)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Re-exports the global 'config' object. Provides legacy get_config and set_config functions.
# FUNCTIONS: get_config, set_config
# CLASSES: None (imports LukhasConfig for type hinting)
# DECORATORS: None
# DEPENDENCIES: .config (imports 'config' object and LukhasConfig class), logging
# INTERFACES: Exports 'config', 'get_config', 'set_config'.
# ERROR HANDLING: set_config logs warnings and raises TypeError for incorrect input type.
# LOGGING: ΛTRACE_ENABLED for initialization and function calls.
# AUTHENTICATION: Not applicable.
# HOW TO USE:
#   from core.config_manager import config, get_config
#   current_cfg = get_config()
#   # Direct use of 'config' is often preferred:
#   # print(config.openai_api_key)
# INTEGRATION NOTES: This module is mainly for compatibility. New code should consider
#                    importing 'config' directly from 'core.config'.
# MAINTENANCE: Ensure compatibility functions behave as expected if 'core.config' changes.
#              Evaluate the necessity of these legacy functions over time.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════