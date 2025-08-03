# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# MODULE: orchestration.monitoring.sub_agents
# DESCRIPTION: Initializes the sub_agents sub-package within monitoring.
#              Exports specialized micro-agents for targeted tasks.
# DEPENDENCIES: structlog, .ethics_guardian, .memory_cleaner
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

import structlog

# Initialize logger for ΛTRACE using structlog

#TAG:governance
#TAG:guardian
#TAG:neuroplastic
#TAG:colony


logger = structlog.get_logger("ΛTRACE.orchestration.monitoring.sub_agents")
logger.info("ΛTRACE: Initializing orchestration.monitoring.sub_agents package.")

"""
LUKHAS Guardian Sub-Agents Module

Specialized micro-agents for targeted remediation tasks:
- EthicsGuardian: Ethical alignment and moral decision-making
- MemoryCleaner: Memory optimization and cleanup
- ComplianceEnforcer: Regulatory compliance enforcement # ΛNOTE: ComplianceEnforcer mentioned but not currently imported/exported.

All sub-agents are spawned by the main RemediatorAgent when
specialized intervention is required.
"""

# AIMPORT_TODO: Ensure that ethics_guardian.py and memory_cleaner.py exist and are correctly structured for these imports.
from .ethics_guardian import EthicsGuardian
from .memory_cleaner import MemoryCleaner

__all__ = [
    "EthicsGuardian",
    "MemoryCleaner",
    # 'ComplianceEnforcer' # Add when implemented
]

logger.info(
    "ΛTRACE: orchestration.monitoring.sub_agents package initialized.", exports=__all__
)

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 2-4 (Sub-agent functionalities)
# ΛTRACE INTEGRATION: ENABLED
# CAPABILITIES: Package initialization for GUARDIAN sub-agents. Exports EthicsGuardian and MemoryCleaner.
# FUNCTIONS: None.
# CLASSES: Exports EthicsGuardian, MemoryCleaner.
# DECORATORS: None.
# DEPENDENCIES: structlog, .ethics_guardian, .memory_cleaner.
# INTERFACES: Public interface defined by __all__.
# ERROR HANDLING: Logger initialization. Relies on successful import of sub-agent modules.
# LOGGING: ΛTRACE_ENABLED via structlog.
# AUTHENTICATION: Not applicable at package initialization.
# HOW TO USE:
#   from orchestration.monitoring.sub_agents import EthicsGuardian
#   guardian = EthicsGuardian()
# INTEGRATION NOTES: Add new sub-agents to imports and __all__ list.
#                    The `ComplianceEnforcer` is mentioned in docstring but not yet included.
# MAINTENANCE: Update imports and __all__ as sub-agents are added or removed.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
