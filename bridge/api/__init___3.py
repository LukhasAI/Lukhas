# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# MODULE: lukhas_id.api.routes
# DESCRIPTION: Initializes the API routes sub-package for LUKHAS ΛiD.
#              This package typically contains modules that define various API
#              route blueprints (e.g., for ΛiD operations, user auth, etc.).
# DEPENDENCIES: logging
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

from core.common import get_logger

# Initialize ΛTRACE logger for this API routes package

#TAG:bridge
#TAG:api
#TAG:neuroplastic
#TAG:colony


logger = logging.getLogger("ΛTRACE.lukhas_id.api.routes")
logger.info("ΛTRACE: Initializing lukhas_id.api.routes package.")

# Define what symbols are exported when 'from . import *' is used.
# Example:
# from .lambd_id_routes import lambd_id_bp
# from .user_routes import user_bp
# __all__ = ["lambd_id_bp", "user_bp"]

__all__ = []
logger.debug(f"ΛTRACE: lukhas_id.api.routes package __all__ set to: {__all__}")

logger.info("ΛTRACE: lukhas_id.api.routes package initialized.")

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# VERSION: 1.0.0
# TIER SYSTEM: Not applicable to package init; tiers apply to specific routes.
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Package initialization for API route definitions.
# FUNCTIONS: None.
# CLASSES: None directly defined. (Exports Blueprints or route collections from submodules)
# DECORATORS: None.
# DEPENDENCIES: logging. (Submodules will have dependencies like Flask Blueprint).
# INTERFACES: Defines the public API of this package (currently empty via __all__).
# ERROR HANDLING: None specific to this initialization file.
# LOGGING: ΛTRACE_ENABLED via Python's logging module for package initialization.
# AUTHENTICATION: Defined at the individual route or blueprint level within submodules.
# HOW TO USE:
#   from identity.api.routes import some_blueprint
#   app.register_blueprint(some_blueprint)
# INTEGRATION NOTES: This __init__.py serves as the entry point for API route modules.
#                    Blueprints defined in submodules should be imported and potentially
#                    added to __all__ if they are to be directly accessible from this package.
# MAINTENANCE: Update __all__ as new route modules/blueprints are added.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
