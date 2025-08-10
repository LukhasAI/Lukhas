# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# MODULE: core.autotest
# DESCRIPTION: Initializes the core.autotest package, providing a simplified
#              one-line API interface to the AutomaticTestingSystem.
# DEPENDENCIES: .automatic_testing_system
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════

"""
LUKHAS AGI Automatic Testing & Logging System
============================================

One-Line API Interface for Steve Jobs-level UX elegance:

```python
from prot2.CORE import autotest

# 🎯 Run all tests automatically
results = await autotest.run()

# 👁️ Start continuous monitoring
await autotest.watch()

# 📊 Generate comprehensive report
report = await autotest.report()

# 🔄 Capture specific operation
operation = await autotest.capture("python script.py")

# 🛑 Stop monitoring
autotest.stop()
```

Integration with existing LUKHAS framework and enhanced with:
- AI-powered test analysis and insights
- Real-time performance monitoring
- Terminal operation capture with sub-100ms tracking
- Comprehensive logging and metrics
- Future-proof architecture for AGI capabilities
"""

from .automatic_testing_system import (
    AITestAnalyzer,
    # Main classes
    AutomaticTestingSystem,
    PerformanceMonitor,
    TestOperation,
    TestSession,
    capture,
    report,
    # One-line API functions
    run,
    stop,
    watch,
)

# Module metadata
__version__ = "1.0.0"
__author__ = "LUKHAS AGI System"
__description__ = "Automatic Testing & Logging System with AI-powered insights"

# Quick access to main functionality
# Creates a convenient 'autotest' object that acts as a namespace for the one-line API functions.
# ΛNOTE: This uses dynamic type creation for the `autotest` object, providing a fluent API style (e.g., `autotest.run()`).
autotest = type(
    "AutoTest",
    (),
    {
        "run": run,
        "watch": watch,
        "report": report,
        "stop": stop,
        "capture": capture,
        "system": lambda: _get_autotest_instance(),
        "__doc__": "One-line automatic testing operations",
    },
)()

# Import helper for getting instance
from .automatic_testing_system import _get_autotest_instance

__all__ = [
    "AutomaticTestingSystem",
    "TestOperation",
    "TestSession",
    "PerformanceMonitor",
    "AITestAnalyzer",
    "run",
    "watch",
    "report",
    "stop",
    "capture",
    "autotest",
]

# ═══════════════════════════════════════════════════════════════════════════
# FILENAME: __init__.py
# VERSION: 1.0.0
# TIER SYSTEM: Tier 1-3 (Provides access to testing system capabilities)
# ΛTRACE INTEGRATION: Not directly applicable (facade module); underlying system has ΛTRACE.
# CAPABILITIES: Exports core classes and one-line API functions from the
#               AutomaticTestingSystem. Provides `autotest` convenience object.
# FUNCTIONS: run, watch, report, stop, capture (re-exported).
# CLASSES: AutomaticTestingSystem, TestOperation, TestSession, PerformanceMonitor,
#            AITestAnalyzer (re-exported). `autotest` (dynamically created type).
# DECORATORS: None.
# DEPENDENCIES: .automatic_testing_system.
# INTERFACES: Public interface defined by __all__.
# ERROR HANDLING: Relies on error handling within .automatic_testing_system.
# LOGGING: Not directly applicable; underlying system handles logging.
# AUTHENTICATION: Not applicable at this module level.
# HOW TO USE:
#   from core import autotest
#   results = await autotest.run()
#   # or
#   from core.autotest import run, AutomaticTestingSystem
#   results = await run()
# INTEGRATION NOTES: This module simplifies access to the automatic testing framework.
#                    The `autotest` object is a convenience wrapper.
# MAINTENANCE: Ensure __all__ is updated if new core components or API functions
#              are added to .automatic_testing_system and need to be exposed.
# CONTACT: LUKHAS DEVELOPMENT TEAM
# LICENSE: PROPRIETARY - LUKHAS AI SYSTEMS - UNAUTHORIZED ACCESS PROHIBITED
# ═══════════════════════════════════════════════════════════════════════════
