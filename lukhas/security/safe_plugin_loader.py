"""
Safe Plugin Loader - Secure alternative to exec() for plugin loading.

This module provides secure mechanisms for loading Python modules and plugins
without using exec() or eval(), which are dangerous and can execute arbitrary code.

Key Security Features:
- Path whitelisting to prevent loading from untrusted locations
- Uses importlib (safe) instead of exec() (dangerous)
- Comprehensive error handling and logging
- Path traversal attack prevention

Usage:
    from lukhas.security import SafePluginLoader

    loader = SafePluginLoader(allowed_directories=[Path("/app/plugins")])
    plugin = loader.load_plugin(Path("/app/plugins/my_plugin.py"), "my_plugin")
"""

import importlib.util
from pathlib import Path
from typing import Any, Optional, List, Union
import logging
import sys

logger = logging.getLogger(__name__)


class PluginSecurityError(Exception):
    """Raised when plugin loading fails security checks."""
    pass


class SafePluginLoader:
    """
    Secure plugin loading without exec().

    This class provides safe mechanisms to load Python modules dynamically
    using importlib instead of dangerous exec() calls.

    Attributes:
        allowed_directories: List of directories from which plugins can be loaded
    """

    def __init__(self, allowed_directories: Optional[List[Union[Path, str]]] = None):
        """
        Initialize the SafePluginLoader.

        Args:
            allowed_directories: List of directory paths where plugins can be loaded from.
                                If None, allows loading from current directory only.
        """
        if allowed_directories is None:
            allowed_directories = [Path.cwd()]

        self.allowed_directories = [
            Path(d).resolve() for d in allowed_directories
        ]
        logger.info(f"SafePluginLoader initialized with allowed directories: {self.allowed_directories}")

    def _validate_path(self, plugin_path: Path) -> None:
        """
        Validate that plugin path is in an allowed directory.

        Args:
            plugin_path: Path to validate

        Raises:
            PluginSecurityError: If path is not in allowed directories
        """
        resolved_path = plugin_path.resolve()

        # Check if path is in any allowed directory
        is_allowed = any(
            resolved_path.is_relative_to(allowed)
            for allowed in self.allowed_directories
        )

        if not is_allowed:
            raise PluginSecurityError(
                f"Plugin path {plugin_path} is not in allowed directories: "
                f"{self.allowed_directories}"
            )

        logger.debug(f"Path validation passed for: {plugin_path}")

    def load_plugin(
        self,
        plugin_path: Union[Path, str],
        plugin_name: Optional[str] = None
    ) -> Any:
        """
        Safely load a Python module from a whitelisted directory.

        Args:
            plugin_path: Path to the plugin file
            plugin_name: Name for the loaded module. If None, derives from filename.

        Returns:
            The loaded module object

        Raises:
            PluginSecurityError: If plugin path is not in allowed directories
            FileNotFoundError: If plugin file doesn't exist
        """
        plugin_path = Path(plugin_path)

        # Validate path is in allowed directory
        self._validate_path(plugin_path)

        # Check file exists
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin file not found: {plugin_path}")

        # Derive module name if not provided
        if plugin_name is None:
            plugin_name = plugin_path.stem

        try:
            # Load using importlib (safe)
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if not spec or not spec.loader:
                raise PluginSecurityError(
                    f"Could not load plugin spec from {plugin_path}"
                )

            module = importlib.util.module_from_spec(spec)

            # Add to sys.modules before executing
            sys.modules[plugin_name] = module

            # Execute module
            spec.loader.exec_module(module)

            logger.info(f"Successfully loaded plugin: {plugin_name} from {plugin_path}")
            return module

        except Exception as e:
            # Clean up sys.modules on failure
            sys.modules.pop(plugin_name, None)
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
            raise PluginSecurityError(
                f"Failed to load plugin {plugin_name} from {plugin_path}: {e}"
            ) from e
