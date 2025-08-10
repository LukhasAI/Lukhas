#!/usr/bin/env python3
"""
Update __init__.py files with discovered entities
Makes all discovered classes and functions easily importable
"""

import json
import logging
from pathlib import Path
from typing import Dict

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InitFileUpdater:
    """Update __init__.py files with discovered entities"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        # Load the entity activation report
        report_file = self.root_path / "tools" / "entity_activation_report.json"
        with open(report_file) as f:
            self.report = json.load(f)

    def generate_init_content(self, system_name: str, entities_by_file: Dict) -> str:
        """Generate __init__.py content for a system"""

        content = f'''"""
{system_name.title()} System - Auto-generated entity exports
Generated from entity activation scan
Total entities: {sum(len(entities) for entities in entities_by_file.values())}
"""

# Lazy imports to avoid circular dependencies
import importlib
import logging

logger = logging.getLogger(__name__)

# Entity registry for lazy loading
_ENTITY_REGISTRY = {{
'''

        # Build registry of all entities
        for file_path, entities in sorted(entities_by_file.items()):
            if file_path.endswith("__init__.py"):
                continue

            module_path = file_path.replace(".py", "").replace("/", ".")

            for entity_type, entity_name, line_no in entities:
                if entity_type == "class":
                    content += (
                        f'    "{entity_name}": ("{module_path}", "{entity_name}"),\n'
                    )

        content += """}\n
# Function registry
_FUNCTION_REGISTRY = {
"""

        # Add functions
        for file_path, entities in sorted(entities_by_file.items()):
            if file_path.endswith("__init__.py"):
                continue

            module_path = file_path.replace(".py", "").replace("/", ".")

            for entity_type, entity_name, line_no in entities:
                if entity_type == "function" and not entity_name.startswith("_"):
                    content += (
                        f'    "{entity_name}": ("{module_path}", "{entity_name}"),\n'
                    )

        content += '''}\n

def __getattr__(name):
    """Lazy import entities on access"""
    # Check class registry first
    if name in _ENTITY_REGISTRY:
        module_path, attr_name = _ENTITY_REGISTRY[name]
        try:
            module = importlib.import_module(f".{module_path}", package=__package__)
            return getattr(module, attr_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to import {attr_name} from {module_path}: {e}")
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    # Check function registry
    if name in _FUNCTION_REGISTRY:
        module_path, attr_name = _FUNCTION_REGISTRY[name]
        try:
            module = importlib.import_module(f".{module_path}", package=__package__)
            return getattr(module, attr_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to import {attr_name} from {module_path}: {e}")
            raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """List all available entities"""
    return list(_ENTITY_REGISTRY.keys()) + list(_FUNCTION_REGISTRY.keys())


# Export commonly used entities directly for better IDE support
__all__ = [
'''

        # Add top 20 most likely used classes to __all__
        class_names = []
        for file_path, entities in sorted(entities_by_file.items()):
            for entity_type, entity_name, line_no in entities:
                if entity_type == "class" and len(class_names) < 20:
                    class_names.append(entity_name)

        for name in class_names:
            content += f'    "{name}",\n'

        content += """]

# System metadata
__system__ = "{}"
__total_entities__ = {}
__classes__ = {}
__functions__ = {}
""".format(
            system_name,
            sum(len(entities) for entities in entities_by_file.values()),
            len(
                [
                    e
                    for ents in entities_by_file.values()
                    for e in ents
                    if e[0] == "class"
                ]
            ),
            len(
                [
                    e
                    for ents in entities_by_file.values()
                    for e in ents
                    if e[0] == "function"
                ]
            ),
        )

        return content

    def update_system_init(self, system_data: Dict) -> None:
        """Update __init__.py for a system"""
        system_name = system_data["system"]
        entities_by_file = system_data.get("entities_by_file", {})

        if not entities_by_file:
            logger.warning(f"No entities found for {system_name}")
            return

        # Generate init content
        init_content = self.generate_init_content(system_name, entities_by_file)

        # Write to __init__.py
        init_file = self.root_path / system_name / "__init__.py"

        # Backup existing file if it exists
        if init_file.exists():
            backup_file = init_file.with_suffix(".py.backup")
            init_file.rename(backup_file)
            logger.info(f"Backed up existing {init_file} to {backup_file}")

        # Write new content
        init_file.parent.mkdir(parents=True, exist_ok=True)
        with open(init_file, "w") as f:
            f.write(init_content)

        logger.info(f"Updated {init_file} with {len(entities_by_file)} files")

    def update_all_systems(self) -> None:
        """Update all system __init__.py files"""
        logger.info(
            f"Updating __init__.py files for {len(self.report['systems'])} systems"
        )

        for system_data in self.report["systems"]:
            try:
                self.update_system_init(system_data)
            except Exception as e:
                logger.error(f"Failed to update {system_data['system']}: {e}")

        # Create a master __init__.py that imports all systems
        self.create_master_init()

        logger.info("✅ All __init__.py files updated successfully!")

    def create_master_init(self) -> None:
        """Create a master __init__.py that references all systems"""
        content = '''"""
LUKHAS AGI - Master System Registry
Auto-generated from entity activation scan
"""

# System imports
systems = {
'''

        for system_data in self.report["systems"]:
            system_name = system_data["system"]
            content += f'    "{system_name}": "{system_name}",\n'

        content += """}

# System statistics
SYSTEM_STATS = {
"""

        for system_data in self.report["systems"]:
            system_name = system_data["system"]
            content += f'    "{system_name}": {{\n'
            content += f'        "entities": {system_data["entity_count"]},\n'
            content += f'        "classes": {system_data["class_count"]},\n'
            content += f'        "functions": {system_data["function_count"]},\n'
            content += f'        "files": {system_data["files"]}\n'
            content += "    },\n"

        content += f"""}}\n
# Total statistics
TOTAL_ENTITIES = {self.report["total_entities"]}
TOTAL_CLASSES = {self.report["total_classes"]}
TOTAL_FUNCTIONS = {self.report["total_functions"]}
TOTAL_SYSTEMS = {self.report["total_systems"]}

print(f"LUKHAS AGI: {{TOTAL_ENTITIES}} entities across {{TOTAL_SYSTEMS}} systems ready for activation!")
"""

        # Write master init file
        master_init = self.root_path / "__init__.py"
        with open(master_init, "w") as f:
            f.write(content)

        logger.info(
            f"Created master __init__.py with {self.report['total_entities']} total entities"
        )


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update __init__.py files with discovered entities"
    )
    parser.add_argument(
        "--root",
        default="/Users/agi_dev/Downloads/Consolidation-Repo",
        help="Root directory of the project",
    )

    args = parser.parse_args()

    updater = InitFileUpdater(args.root)
    updater.update_all_systems()


if __name__ == "__main__":
    main()
