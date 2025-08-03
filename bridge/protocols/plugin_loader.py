# LUKHAS_TAG: plugin_loader, orchestration_extension
import os
import importlib
from pathlib import Path
import logging


#TAG:bridge
#TAG:protocols
#TAG:neuroplastic
#TAG:colony


logger = logging.getLogger(__name__)

def load_plugins(plugin_dir: str = "core/plugins"):
    """
    Dynamically loads plugins from a specified directory.
    """
    plugins = {}
    plugin_path = Path(plugin_dir)
    if not plugin_path.is_dir():
        logger.warning(f"Plugin directory not found: {plugin_dir}")
        return plugins

    for file_path in plugin_path.glob("*.py"):
        if file_path.name == "__init__.py":
            continue

        module_name = f"{plugin_dir.replace('/', '.')}.{file_path.stem}"
        try:
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, "plugin", None)
            if plugin_class:
                plugin_instance = plugin_class()
                plugin_name = getattr(plugin_instance, "name", file_path.stem)
                plugins[plugin_name] = plugin_instance
                logger.info(f"Registered plugin: {plugin_name}")
        except Exception as e:
            logger.error(f"Failed to load plugin {module_name}: {e}")
    return plugins
