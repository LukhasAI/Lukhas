# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# MODULE: core.adaptive_systems.crista_optimizer
# DESCRIPTION: Initializes the crista_optimizer package, exposing its main classes
#              for dynamic bio-symbolic network topology management within LUKHAS AGI.
# DEPENDENCIES: .crista_optimizer, .topology_manager, .symbolic_network, logging
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import structlog

# Initialize logger for ΛTRACE using structlog
# Assumes structlog is configured in a higher-level __init__.py (e.g., core/__init__.py)
logger = structlog.get_logger("ΛTRACE.core.adaptive_systems.crista_optimizer")
logger.info("ΛTRACE: Initializing crista_optimizer package.")

# Attempt to import key components from within the package
try:
    from .crista_optimizer import CristaOptimizer, NetworkConfig
    from .symbolic_network import (
        SymbolicNetwork,  # Assuming symbolic_network.py contains this class
    )
    from .topology_manager import (
        TopologyManager,  # Assuming topology_manager.py contains this class
    )

    logger.info(
        "ΛTRACE: Successfully imported CristaOptimizer, NetworkConfig, TopologyManager, SymbolicNetwork."
    )
except ImportError as e:
    logger.error(f"ΛTRACE: Error importing from crista_optimizer submodules: {e}")
    # Define placeholders if imports fail, to prevent outright crashing if possible,
    # though functionality will be severely impacted.
    CristaOptimizer = None
    NetworkConfig = None
    TopologyManager = None
    SymbolicNetwork = None

# Public API for the crista_optimizer package
# Specifies what is exported when 'from core.adaptive_systems.crista_optimizer import *' is used.
__all__ = ["CristaOptimizer", "NetworkConfig", "TopologyManager", "SymbolicNetwork"]

# Package version
__version__ = "1.0.1"  # Original was 1.0.0, incremented for JULES enhancements

logger.info(
    f"ΛTRACE: crista_optimizer package version: {__version__}. Public API via __all__: {__all__}"
)

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# VERSION: 1.0.1
# TIER SYSTEM: Tier 2-4 (Core components for an advanced adaptive system)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Package initialization, Exporting key classes for crista optimization.
# FUNCTIONS: None directly exposed.
# CLASSES: None directly defined; exports CristaOptimizer, NetworkConfig, TopologyManager, SymbolicNetwork.
# DECORATORS: None.
# DEPENDENCIES: logging, .crista_optimizer, .topology_manager, .symbolic_network.
# INTERFACES: Defines the public API of this package via __all__.
# ERROR HANDLING: Logs import errors for critical components.
# LOGGING: ΛTRACE_ENABLED via Python's logging module.
# AUTHENTICATION: Not applicable at package initialization level.
# HOW TO USE:
#   from core.adaptive_systems.crista_optimizer import CristaOptimizer, NetworkConfig
#   config = NetworkConfig()
#   optimizer = CristaOptimizer(network, config) # network needs to be an instance of SymbolicNetwork
# INTEGRATION NOTES: This package provides the core tools for adaptive network topology.
#                    Ensure all listed components in __all__ are correctly implemented in their respective files.
# MAINTENANCE: Update __all__ and imports if class names or file structures change.
#              Increment __version__ with significant changes.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
