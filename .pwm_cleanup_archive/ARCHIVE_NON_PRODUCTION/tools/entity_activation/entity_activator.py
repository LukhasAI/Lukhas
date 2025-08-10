#!/usr/bin/env python3
"""
Entity Activator
Scans project modules for classes and generates activation code.
"""

from __future__ import annotations

import ast
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityActivator:
    """Activate inactive entities across the system."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.activation_log: List[Dict[str, int | str]] = []

    def analyze_python_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """Extract top-level classes and public functions from a Python file."""
        entities: List[Tuple[str, str]] = []
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    entities.append(("class", node.name))
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith(
                    "_"
                ):
                    entities.append(("function", node.name))
        except Exception as e:
            logger.warning(f"Error analyzing {file_path}: {e}")
        return entities

    def find_system_entities(
        self, system_path: str
    ) -> Dict[str, List[Tuple[str, str]]]:
        """Find all entities in a system directory."""
        system_dir = self.root_path / system_path
        entities_by_file: Dict[str, List[Tuple[str, str]]] = {}
        if not system_dir.exists():
            return entities_by_file
        for py_file in system_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            rel_path = py_file.relative_to(system_dir)
            entities = self.analyze_python_file(py_file)
            if entities:
                entities_by_file[str(rel_path)] = entities
        return entities_by_file

    def generate_activation_code(
        self, system_name: str, entities_by_file: Dict[str, List[Tuple[str, str]]]
    ) -> str:
        """Generate activation code for a system."""
        lines = [
            f"# Auto-generated entity activation for {system_name}",
            f"{system_name.upper()}_ENTITIES = [",
        ]
        for file_path, entities in entities_by_file.items():
            module_path = file_path.replace(".py", "").replace(os.sep, ".")
            for entity_type, entity_name in entities:
                if entity_type == "class":
                    lines.append(f'    ("{module_path}", "{entity_name}"),')
        lines.append("]\n")
        lines.extend(
            [
                f"def activate_{system_name}_entities(self):",
                f'    """Activate all {system_name} entities"""',
                f"    for module_path, class_name in {system_name.upper()}_ENTITIES:",
                "        try:",
                f"            full_module = f'{system_name}.{{module_path}}'",
                "            module = __import__(full_module, fromlist=[class_name])",
                "            cls = getattr(module, class_name)",
                "            try:",
                "                instance = cls()",
                "                service_name = class_name.lower()",
                "                self.register_service(service_name, instance)",
                "                logger.debug(f'Activated {class_name} as {service_name}')",
                "            except Exception:",
                "                self.register_service(class_name.lower() + '_class', cls)",
                "                logger.debug(f'Registered {class_name} class')",
                "        except (ImportError, AttributeError) as e:",
                "            logger.warning(f'Could not activate {class_name} from {module_path}: {e}')",
            ]
        )
        return "\n".join(lines)

    def activate_system(self, system_name: str, system_path: str) -> None:
        """Activate all entities in a system and generate activation file."""
        logger.info(f"Scanning {system_name} system ...")
        entities = self.find_system_entities(system_path)
        if not entities:
            logger.info(f"No entities found in {system_name}")
            return
        activation_code = self.generate_activation_code(system_name, entities)
        output_file = self.root_path / f"{system_name}_entity_activation.py"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(activation_code)
        entity_count = sum(len(ents) for ents in entities.values())
        logger.info(
            f"Generated activation code for {entity_count} entities in {system_name}"
        )
        self.activation_log.append(
            {
                "system": system_name,
                "entity_count": entity_count,
                "activation_file": str(output_file),
            }
        )

    def generate_activation_report(self) -> None:
        """Write summary report of activation results."""
        report = {
            "total_systems": len(self.activation_log),
            "total_entities": sum(item["entity_count"] for item in self.activation_log),
            "systems": self.activation_log,
        }
        report_file = self.root_path / "entity_activation_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info(f"Activation report written to {report_file}")

    def activate_all_systems(self) -> None:
        """Run activation for all known systems."""
        systems = [
            ("core", "core"),
            ("consciousness", "consciousness"),
            ("memory", "memory"),
            ("orchestration", "orchestration"),
            ("bio", "bio"),
            ("symbolic", "symbolic"),
            ("quantum", "quantum"),
            ("learning", "learning"),
        ]
        for system_name, system_path in systems:
            self.activate_system(system_name, system_path)
        self.generate_activation_report()


if __name__ == "__main__":
    activator = EntityActivator(Path(__file__).resolve().parents[2])
    activator.activate_all_systems()
