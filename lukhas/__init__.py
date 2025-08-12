"""
LUKHAS AI - Unified Module System
Core module initialization and exports
"""

# Import core modules with error handling
modules = {}

try:
    from . import consciousness
    modules['consciousness'] = consciousness
except ImportError:
    pass

try:
    from . import memory
    modules['memory'] = memory
except ImportError:
    pass

try:
    from . import governance
    modules['governance'] = governance
except ImportError:
    pass

try:
    from . import identity
    modules['identity'] = identity
except ImportError:
    pass

try:
    from . import bio
    modules['bio'] = bio
except ImportError:
    pass

try:
    from . import quantum
    modules['quantum'] = quantum
except ImportError:
    pass

# Export available modules
__all__ = list(modules.keys())

def get_module(name):
    """Get a module by name"""
    return modules.get(name)

def list_modules():
    """List all available modules"""
    return list(modules.keys())
