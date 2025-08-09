"""
Identity Import Bridge - Custom Import Finder
=============================================
Provides a PEP 302 compliant import finder/loader to handle
the old identity.* import paths and redirect them to governance.identity.*
"""

import sys
import importlib
import importlib.abc
import importlib.machinery
import importlib.util
import warnings
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


# Mapping of old import paths to new ones
IMPORT_MAPPINGS = {
    # Auth module mappings
    "identity.auth.cultural_profile_manager": "governance.identity.auth.cultural_profile_manager",
    "identity.auth.entropy_synchronizer": "governance.identity.auth.entropy_synchronizer",
    "identity.auth.cognitive_sync_adapter": "governance.identity.auth.cognitive_sync_adapter",
    "identity.auth.qrg_generators": "governance.identity.auth.qrg_generators",
    
    # Core module mappings
    "identity.core.events": "governance.identity.core.events",
    "identity.core.colonies": "governance.identity.core.colonies",
    "identity.core.tier": "governance.identity.core.tier",
    "identity.core.health": "governance.identity.core.health",
    "identity.core.glyph": "governance.identity.core.glyph",
    "identity.core.tagging": "governance.identity.core.tagging",
    "identity.core.swarm": "governance.identity.core.swarm",
    
    # Mobile module mappings
    "identity.mobile.qr_code_animator": "governance.identity.mobile.qr_code_animator",
    
    # Interface mapping
    "identity.interface": "governance.identity.interface",
}


class IdentityModuleFinder(importlib.abc.MetaPathFinder):
    """Custom finder to redirect identity.* imports to governance.identity.*"""
    
    def find_spec(self, fullname: str, path: Optional[Any] = None, target: Optional[Any] = None):
        """Find module spec for identity.* imports"""
        
        # Only handle identity.* imports
        if not fullname.startswith('identity'):
            return None
        
        # Check if we have a direct mapping
        if fullname in IMPORT_MAPPINGS:
            new_name = IMPORT_MAPPINGS[fullname]
            
            # Issue deprecation warning
            warnings.warn(
                f"Import path '{fullname}' is deprecated. "
                f"Please use '{new_name}' instead.",
                DeprecationWarning,
                stacklevel=2
            )
            
            # Try to find the new module
            try:
                # Use importlib to find the actual module
                spec = importlib.util.find_spec(new_name)
                if spec:
                    # Create a spec with the old name that loads the new module
                    return importlib.machinery.ModuleSpec(
                        fullname,
                        IdentityModuleLoader(new_name),
                        origin=spec.origin,
                        is_package=spec.submodule_search_locations is not None
                    )
            except (ImportError, ValueError) as e:
                logger.debug(f"Could not find {new_name}: {e}")
                # Fall through to provide fallback
        
        # For unmapped modules, provide a fallback
        return importlib.machinery.ModuleSpec(
            fullname,
            IdentityFallbackLoader(fullname),
            origin='virtual:identity',
            is_package=True
        )


class IdentityModuleLoader(importlib.abc.Loader):
    """Loader that redirects to the new module location"""
    
    def __init__(self, new_name: str):
        self.new_name = new_name
    
    def load_module(self, fullname: str):
        """Load the module by importing from the new location"""
        # Import the new module
        new_module = importlib.import_module(self.new_name)
        
        # Add it to sys.modules under the old name too
        sys.modules[fullname] = new_module
        
        return new_module
    
    def exec_module(self, module):
        """Execute module (for Python 3.4+)"""
        # Import the actual module
        actual_module = importlib.import_module(self.new_name)
        
        # Copy attributes
        for attr in dir(actual_module):
            if not attr.startswith('_'):
                setattr(module, attr, getattr(actual_module, attr))


class IdentityFallbackLoader(importlib.abc.Loader):
    """Loader that provides fallback modules for missing identity components"""
    
    def __init__(self, fullname: str):
        self.fullname = fullname
    
    def load_module(self, fullname: str):
        """Create a fallback module"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Create a new module
        module = type(sys)('identity_fallback')
        module.__name__ = fullname
        module.__file__ = f'<virtual:{fullname}>'
        module.__loader__ = self
        module.__package__ = fullname.rpartition('.')[0]
        module.__path__ = []
        
        # Add common fallback classes based on module name
        if 'Manager' in fullname or fullname.endswith('_manager'):
            class FallbackManager:
                def __init__(self, *args, **kwargs):
                    import logging
                    logging.getLogger(__name__).warning(f"Using fallback for {fullname}")
            module.Manager = FallbackManager
            parts = fullname.split('.')
            if parts:
                class_name = ''.join(p.capitalize() for p in parts[-1].split('_'))
                setattr(module, class_name, FallbackManager)
        
        if 'Synchronizer' in fullname or fullname.endswith('_synchronizer'):
            class FallbackSynchronizer:
                def __init__(self, *args, **kwargs):
                    import logging
                    logging.getLogger(__name__).warning(f"Using fallback for {fullname}")
            module.Synchronizer = FallbackSynchronizer
            parts = fullname.split('.')
            if parts:
                class_name = ''.join(p.capitalize() for p in parts[-1].split('_'))
                setattr(module, class_name, FallbackSynchronizer)
        
        if 'events' in fullname:
            # Provide event types
            from enum import Enum
            class EventType(Enum):
                DEFAULT = "default"
            module.IdentityEventType = EventType
            module.publish_event = lambda *args, **kwargs: None
        
        # Register in sys.modules
        sys.modules[fullname] = module
        return module
    
    def exec_module(self, module):
        """Execute module (for Python 3.4+)"""
        # Module is already set up in load_module
        pass


def install_identity_bridge():
    """Install the identity import bridge"""
    # Check if already installed
    for finder in sys.meta_path:
        if isinstance(finder, IdentityModuleFinder):
            return
    
    # Install our custom finder at the beginning of meta_path
    sys.meta_path.insert(0, IdentityModuleFinder())
    logger.info("Identity import bridge installed")


def uninstall_identity_bridge():
    """Uninstall the identity import bridge"""
    sys.meta_path = [f for f in sys.meta_path if not isinstance(f, IdentityModuleFinder)]
    
    # Clean up sys.modules
    to_remove = [name for name in sys.modules if name.startswith('identity.')]
    for name in to_remove:
        del sys.modules[name]
    
    logger.info("Identity import bridge uninstalled")


# Auto-install when imported
install_identity_bridge()