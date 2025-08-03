# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: diagnostic_payloads.py
# MODULE: core.diagnostic_engine
# DESCRIPTION: Diagnostic payload creation utilities for LUKHAS components
# DEPENDENCIES: structlog, core.common, core.helpers
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import structlog
from typing import Dict, Any, Optional

from core.utils import SystemStatus # ΛSHARED: System status enumeration
from core.helpers import get_utc_timestamp # ΛUTIL: UTC timestamp utility

# ΛTRACE: Initializing logger for diagnostic payloads

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


log = structlog.get_logger(__name__)

# ΛUTIL
def create_diagnostic_payload(component_id: str, status: SystemStatus, message: str, additional_data: Optional[Dict] = None) -> Dict:
    """
    Creates a standardized diagnostic payload for LUKHAS components.
    # ΛNOTE: This utility helps in creating consistent diagnostic messages across the system.
    #        Moved from core.lukhas_utils for better organization within diagnostic_engine.
    # ΛECHO: Reflects the state of a component for diagnostic purposes.
    """
    # ΛTRACE: Creating diagnostic payload
    log.debug("Creating diagnostic payload", component_id=component_id, status=status.value)
    payload = {
        "lukhas_diagnostic_version": "1.0",
        "timestamp_utc": get_utc_timestamp(), # ΛUTIL (from core.helpers)
        "component_id": component_id,
        "status": status.value, # ΛSHARED (enum from core.common)
        "message": message,
        "data": additional_data or {}
    }
    return payload

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: diagnostic_payloads.py
# VERSION: 1.0
# TIER SYSTEM: N/A
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: diagnostic_payload_creation
# FUNCTIONS: create_diagnostic_payload
# CLASSES: None
# DECORATORS: None
# DEPENDENCIES: structlog, core.common.SystemStatus, core.helpers.get_utc_timestamp
# INTERFACES: Dict-based diagnostic payload output
# ERROR HANDLING: Basic logging and validation
# LOGGING: ΛTRACE_ENABLED
# AUTHENTICATION: None required
# HOW TO USE:
#   from core.diagnostic_engine.diagnostic_payloads import create_diagnostic_payload
#   payload = create_diagnostic_payload("ComponentName", SystemStatus.OK, "All systems operational")
# INTEGRATION NOTES: Moved from core.lukhas_utils for better organization
# MAINTENANCE: Update diagnostic_version when payload format changes
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
