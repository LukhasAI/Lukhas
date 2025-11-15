"""
Safe Import Utilities - Secure alternatives to exec() for dynamic imports.

This module provides safe mechanisms for dynamic imports without using exec().

Key Security Features:
- Uses importlib (safe) instead of exec() (dangerous)
- Proper error handling
- Type checking support
- Validation of module and class names

Usage:
    from lukhas.security import safe_import_module, safe_import_class

    # Import a module
    module = safe_import_module("mypackage.mymodule")

    # Import a specific class
    MyClass = safe_import_class("mypackage.mymodule", "MyClass")
"""

import importlib
from typing import Any, Optional, Type
import logging

logger = logging.getLogger(__name__)


class ImportSecurityError(Exception):
    """Raised when import operation fails security checks or validation."""
    pass


def safe_import_module(module_name: str) -> Any:
    """
    Safely import a module by name using importlib.

    This is a secure alternative to: exec(f"import {module_name}")

    Args:
        module_name: Fully qualified module name (e.g., "package.submodule")

    Returns:
        The imported module object

    Raises:
        ImportSecurityError: If module cannot be imported

    Example:
        >>> module = safe_import_module("pathlib")
        >>> isinstance(module.Path("."), module.Path)
        True
    """
    if not module_name or not isinstance(module_name, str):
        raise ImportSecurityError(f"Invalid module name: {module_name}")

    try:
        module = importlib.import_module(module_name)
        logger.debug(f"Successfully imported module: {module_name}")
        return module
    except ImportError as e:
        logger.error(f"Failed to import module {module_name}: {e}")
        raise ImportSecurityError(
            f"Failed to import module {module_name}: {e}"
        ) from e


def safe_import_class(module_name: str, class_name: str) -> Type[Any]:
    """
    Safely import a specific class from a module.

    This is a secure alternative to: exec(f"from {module_name} import {class_name}")

    Args:
        module_name: Fully qualified module name
        class_name: Name of the class to import

    Returns:
        The imported class object

    Raises:
        ImportSecurityError: If module or class cannot be imported

    Example:
        >>> PathClass = safe_import_class("pathlib", "Path")
        >>> PathClass(".")
        PosixPath('.')
    """
    if not module_name or not isinstance(module_name, str):
        raise ImportSecurityError(f"Invalid module name: {module_name}")

    if not class_name or not isinstance(class_name, str):
        raise ImportSecurityError(f"Invalid class name: {class_name}")

    try:
        # Import the module
        module = importlib.import_module(module_name)

        # Get the class from the module
        if not hasattr(module, class_name):
            raise ImportSecurityError(
                f"Module {module_name} has no attribute {class_name}"
            )

        cls = getattr(module, class_name)
        logger.debug(f"Successfully imported {class_name} from {module_name}")
        return cls

    except ImportError as e:
        logger.error(f"Failed to import {class_name} from {module_name}: {e}")
        raise ImportSecurityError(
            f"Failed to import {class_name} from {module_name}: {e}"
        ) from e


def safe_import_from(module_name: str, *names: str, package: Optional[str] = None) -> dict[str, Any]:
    """
    Safely import multiple items from a module.

    This is a secure alternative to: exec(f"from {module_name} import {', '.join(names)}")

    Args:
        module_name: Fully qualified module name
        *names: Names of items to import from the module
        package: Package context for relative imports

    Returns:
        Dictionary mapping names to imported objects

    Raises:
        ImportSecurityError: If module or any item cannot be imported

    Example:
        >>> items = safe_import_from("pathlib", "Path", "PurePath")
        >>> items["Path"](".")
        PosixPath('.')
    """
    if not module_name or not isinstance(module_name, str):
        raise ImportSecurityError(f"Invalid module name: {module_name}")

    if not names:
        raise ImportSecurityError("No import names specified")

    try:
        # Import the module
        module = importlib.import_module(module_name, package=package)

        # Collect all requested items
        result = {}
        for name in names:
            if not hasattr(module, name):
                raise ImportSecurityError(
                    f"Module {module_name} has no attribute {name}"
                )
            result[name] = getattr(module, name)

        logger.debug(f"Successfully imported {names} from {module_name}")
        return result

    except ImportError as e:
        logger.error(f"Failed to import from {module_name}: {e}")
        raise ImportSecurityError(
            f"Failed to import from {module_name}: {e}"
        ) from e


def safe_import_wildcard(module_name: str, package: Optional[str] = None) -> dict[str, Any]:
    """
    Safely import all public items from a module (equivalent to "from module import *").

    This is a secure alternative to: exec(f"from {module_name} import *")

    Note: This respects __all__ if defined, otherwise imports all non-private items.

    Args:
        module_name: Fully qualified module name
        package: Package context for relative imports

    Returns:
        Dictionary mapping names to imported objects

    Raises:
        ImportSecurityError: If module cannot be imported

    Example:
        >>> items = safe_import_wildcard("pathlib")
        >>> "Path" in items
        True
    """
    if not module_name or not isinstance(module_name, str):
        raise ImportSecurityError(f"Invalid module name: {module_name}")

    try:
        # Import the module
        module = importlib.import_module(module_name, package=package)

        # Get items to import
        if hasattr(module, "__all__"):
            # Respect __all__ if defined
            names = module.__all__
        else:
            # Import all non-private items
            names = [name for name in dir(module) if not name.startswith("_")]

        # Collect all items
        result = {}
        for name in names:
            if hasattr(module, name):
                result[name] = getattr(module, name)

        logger.debug(f"Successfully imported {len(result)} items from {module_name}")
        return result

    except ImportError as e:
        logger.error(f"Failed to import from {module_name}: {e}")
        raise ImportSecurityError(
            f"Failed to import from {module_name}: {e}"
        ) from e
