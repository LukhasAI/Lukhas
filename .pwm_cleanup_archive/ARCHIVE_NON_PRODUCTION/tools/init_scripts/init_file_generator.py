#!/usr/bin/env python3
"""
Init File Generator
Automatically creates __init__.py files for specified directories.
"""

import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_init_file(directory_path: str, components: list = None):
    """Create an __init__.py file for a directory"""
    init_path = Path(directory_path) / "__init__.py"

    if init_path.exists():
        logger.debug(f"Skipping {init_path} - already exists")
        return

    os.makedirs(directory_path, exist_ok=True)

    module_name = Path(directory_path).name.replace("_", " ").title()

    if components is None:
        components = []
        try:
            for file in os.listdir(directory_path):
                if file.endswith(".py") and file != "__init__.py":
                    component_name = file[:-3]
                    class_name = "".join(
                        word.capitalize() for word in component_name.split("_")
                    )
                    components.append((component_name, class_name))
        except FileNotFoundError:
            pass

    lines = [
        '"""',
        f"{module_name} Module",
        "Auto-generated module initialization file",
        '"""',
        "",
        "import logging",
        "",
        "logger = logging.getLogger(__name__)",
        "",
    ]

    for component_name, class_name in components:
        lines.extend(
            [
                "try:",
                f"    from .{component_name} import {class_name}",
                f'    logger.debug("Imported {class_name} from .{component_name}")',
                "except ImportError as e:",
                f'    logger.warning(f"Could not import {class_name}: {{e}}")',
                f"    {class_name} = None",
                "",
            ]
        )

    if components:
        lines.append("__all__ = [")
        for _, class_name in components:
            lines.append(f"    '{class_name}',")
        lines.append("]")
        lines.append("")
        lines.append("# Filter out None values from __all__ if imports failed")
        lines.append(
            "__all__ = [name for name in __all__ if globals().get(name) is not None]"
        )
        lines.append("")
    else:
        lines.append("__all__ = []")
        lines.append("")

    lines.append(
        f'logger.info(f"{module_name.lower()} module initialized. Available components: {{__all__}}")'
    )
    lines.append("")

    with open(init_path, "w") as f:
        f.write("\n".join(lines))

    logger.info(f"Created {init_path}")


def create_batch(batch_directories):
    """Create init files for a batch of directories"""
    for directory in batch_directories:
        create_init_file(directory)


if __name__ == "__main__":
    directories_file = Path(__file__).with_name("init_directories_final.txt")
    if directories_file.exists():
        with open(directories_file) as f:
            batch_dirs = [line.strip() for line in f if line.strip()]
    else:
        batch_dirs = []

    if not batch_dirs:
        logger.error("No directories found to process")
        sys.exit(1)

    create_batch(batch_dirs)
