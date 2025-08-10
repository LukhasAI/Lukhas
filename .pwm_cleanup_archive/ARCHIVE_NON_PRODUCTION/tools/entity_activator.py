#!/usr/bin/env python3
"""
Entity Activation Script - Agent 5
Systematically activate all inactive entities across the LUKHAS AGI system
"""

import ast
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EntityActivator:
    """Activate inactive entities across the system"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.activation_log = []
        self.activated_entities = set()
        self.failed_entities = []
        self.entity_registry = {}

    def analyze_python_file(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """Extract classes and functions from a Python file"""
        entities = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Include line number for better tracking
                    entities.append(("class", node.name, node.lineno))
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith(
                    "_"
                ):
                    # Only public functions
                    entities.append(("function", node.name, node.lineno))

        except Exception as e:
            logger.warning(f"Error analyzing {file_path}: {e}")

        return entities

    def find_system_entities(
        self, system_path: str
    ) -> Dict[str, List[Tuple[str, str, int]]]:
        """Find all entities in a system directory"""
        system_dir = self.root_path / system_path
        entities_by_file = {}

        if not system_dir.exists():
            logger.warning(f"System directory does not exist: {system_dir}")
            return entities_by_file

        # Exclude test files and __pycache__
        exclude_patterns = ["test_", "_test.py", "__pycache__", ".pyc"]

        for py_file in system_dir.rglob("*.py"):
            # Skip excluded files
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            if py_file.name == "__init__.py":
                continue

            rel_path = py_file.relative_to(system_dir)
            entities = self.analyze_python_file(py_file)

            if entities:
                entities_by_file[str(rel_path)] = entities

        return entities_by_file

    def generate_hub_activation_code(
        self, system_name: str, entities_by_file: Dict[str, List[Tuple[str, str, int]]]
    ) -> str:
        """Generate activation code for a system hub"""

        # Group entities by type
        classes = []
        functions = []

        for file_path, entities in entities_by_file.items():
            module_path = file_path.replace(".py", "").replace("/", ".")

            for entity_type, entity_name, line_no in entities:
                if entity_type == "class":
                    classes.append((module_path, entity_name))
                else:
                    functions.append((module_path, entity_name))

        code = f'''"""
Auto-generated entity activation for {system_name} system
Generated: {datetime.now().isoformat()}
Total Classes: {len(classes)}
Total Functions: {len(functions)}
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Entity definitions
{system_name.upper()}_CLASS_ENTITIES = [
'''

        for module_path, class_name in sorted(classes):
            code += f'    ("{module_path}", "{class_name}"),\n'

        code += f"""]

{system_name.upper()}_FUNCTION_ENTITIES = [
"""

        for module_path, func_name in sorted(functions):
            code += f'    ("{module_path}", "{func_name}"),\n'

        code += f''']


class {system_name.title()}EntityActivator:
    """Activator for {system_name} system entities"""

    def __init__(self, hub_instance):
        self.hub = hub_instance
        self.activated_count = 0
        self.failed_count = 0

    def activate_all(self):
        """Activate all {system_name} entities"""
        logger.info(f"Starting {system_name} entity activation...")

        # Activate classes
        self._activate_classes()

        # Activate functions
        self._activate_functions()

        logger.info(f"{{system_name}} activation complete: {{self.activated_count}} activated, {{self.failed_count}} failed")

        return {{
            "activated": self.activated_count,
            "failed": self.failed_count,
            "total": len({system_name.upper()}_CLASS_ENTITIES) + len({system_name.upper()}_FUNCTION_ENTITIES)
        }}

    def _activate_classes(self):
        """Activate class entities"""
        for module_path, class_name in {system_name.upper()}_CLASS_ENTITIES:
            try:
                # Build full module path
                if module_path.startswith('.'):
                    full_path = f"{{system_name}}{{module_path}}"
                else:
                    full_path = f"{{system_name}}.{{module_path}}"

                # Import module
                module = __import__(full_path, fromlist=[class_name])
                cls = getattr(module, class_name)

                # Register with hub
                service_name = self._generate_service_name(class_name)

                # Try to instantiate if possible
                try:
                    instance = cls()
                    self.hub.register_service(service_name, instance)
                    logger.debug(f"Activated {{class_name}} as {{service_name}}")
                except:
                    # Register class if can't instantiate
                    self.hub.register_service(f"{{service_name}}_class", cls)
                    logger.debug(f"Registered {{class_name}} class")

                self.activated_count += 1

            except Exception as e:
                logger.warning(f"Failed to activate {{class_name}} from {{module_path}}: {{e}}")
                self.failed_count += 1

    def _activate_functions(self):
        """Activate function entities"""
        for module_path, func_name in {system_name.upper()}_FUNCTION_ENTITIES:
            try:
                # Build full module path
                if module_path.startswith('.'):
                    full_path = f"{{system_name}}{{module_path}}"
                else:
                    full_path = f"{{system_name}}.{{module_path}}"

                # Import module
                module = __import__(full_path, fromlist=[func_name])
                func = getattr(module, func_name)

                # Register function
                service_name = f"{{func_name}}_func"
                self.hub.register_service(service_name, func)
                logger.debug(f"Activated function {{func_name}}")

                self.activated_count += 1

            except Exception as e:
                logger.warning(f"Failed to activate function {{func_name}} from {{module_path}}: {{e}}")
                self.failed_count += 1

    def _generate_service_name(self, class_name: str) -> str:
        """Generate consistent service names"""
        import re
        # Convert CamelCase to snake_case
        name = re.sub('(.)([A-Z][a-z]+)', r'\\1_\\2', class_name)
        name = re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', name).lower()

        # Remove common suffixes
        for suffix in ['_manager', '_service', '_system', '_engine', '_handler']:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
                break

        return name


def get_{system_name}_activator(hub_instance):
    """Factory function to create activator"""
    return {system_name.title()}EntityActivator(hub_instance)
'''

        return code

    def save_activation_module(self, system_name: str, code: str) -> Path:
        """Save activation code as a Python module"""
        output_dir = self.root_path / "tools" / "activation_modules"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{system_name}_activation.py"
        with open(output_file, "w") as f:
            f.write(code)

        return output_file

    def activate_system(self, system_name: str, system_path: str) -> Dict[str, Any]:
        """Activate all entities in a system"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Activating entities in {system_name} system...")
        logger.info(f"{'='*60}")

        # Find entities
        entities = self.find_system_entities(system_path)

        if not entities:
            logger.warning(f"No entities found in {system_name}")
            return {"system": system_name, "status": "no_entities"}

        # Generate activation code
        activation_code = self.generate_hub_activation_code(system_name, entities)

        # Save activation module
        activation_file = self.save_activation_module(system_name, activation_code)

        # Count entities
        entity_count = sum(len(ents) for ents in entities.values())
        class_count = sum(
            1 for ents in entities.values() for e in ents if e[0] == "class"
        )
        func_count = sum(
            1 for ents in entities.values() for e in ents if e[0] == "function"
        )

        logger.info(f"Generated activation code for {entity_count} entities:")
        logger.info(f"  - Classes: {class_count}")
        logger.info(f"  - Functions: {func_count}")
        logger.info(f"  - Saved to: {activation_file}")

        result = {
            "system": system_name,
            "entity_count": entity_count,
            "class_count": class_count,
            "function_count": func_count,
            "files": len(entities),
            "activation_file": str(activation_file),
            "entities_by_file": entities,
        }

        self.activation_log.append(result)
        self.entity_registry[system_name] = entities

        return result

    def activate_all_systems(self) -> Dict[str, Any]:
        """Activate entities across all systems"""
        systems = [
            ("core", "core"),
            ("consciousness", "consciousness"),
            ("memory", "memory"),
            ("orchestration", "orchestration"),
            ("bio", "bio"),
            ("symbolic", "symbolic"),
            ("quantum", "quantum"),
            ("learning", "learning"),
            ("ethics", "ethics"),
            ("identity", "identity"),
            ("creativity", "creativity"),
            ("embodiment", "embodiment"),
            ("emotion", "emotion"),
        ]

        logger.info("\nStarting system-wide entity activation...")
        logger.info(f"Processing {len(systems)} systems\n")

        for system_name, system_path in systems:
            self.activate_system(system_name, system_path)

        # Generate summary report
        return self.generate_activation_report()

    def generate_activation_report(self) -> Dict[str, Any]:
        """Generate comprehensive activation summary report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_systems": len(self.activation_log),
            "total_entities": sum(item["entity_count"] for item in self.activation_log),
            "total_classes": sum(item["class_count"] for item in self.activation_log),
            "total_functions": sum(
                item["function_count"] for item in self.activation_log
            ),
            "systems": self.activation_log,
        }

        # Save report
        report_file = self.root_path / "tools" / "entity_activation_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Generate hub integration script
        self.generate_hub_integration_script()

        logger.info(f"\n{'='*60}")
        logger.info("📊 Entity Activation Summary")
        logger.info(f"{'='*60}")
        logger.info(f"Systems processed: {report['total_systems']}")
        logger.info(f"Total entities found: {report['total_entities']}")
        logger.info(f"  - Classes: {report['total_classes']}")
        logger.info(f"  - Functions: {report['total_functions']}")
        logger.info(f"Report saved to: {report_file}")
        logger.info(f"{'='*60}\n")

        return report

    def generate_hub_integration_script(self):
        """Generate script to integrate activation modules with hubs"""
        code = '''#!/usr/bin/env python3
"""
Hub Integration Script - Integrates all activation modules with system hubs
"""

import logging
from pathlib import Path
import sys

# Add activation modules to path
activation_dir = Path(__file__).parent / "activation_modules"
sys.path.insert(0, str(activation_dir))

logger = logging.getLogger(__name__)


def integrate_all_hubs():
    """Integrate activation modules with all system hubs"""

    integrations = []

'''

        for system in self.activation_log:
            system_name = system["system"]
            code += f"""    # {system_name.title()} System
    try:
        from {system_name}.{system_name}_hub import get_{system_name}_hub
        from {system_name}_activation import get_{system_name}_activator

        hub = get_{system_name}_hub()
        activator = get_{system_name}_activator(hub)
        result = activator.activate_all()

        integrations.append({{
            "system": "{system_name}",
            "status": "success",
            **result
        }})
        logger.info(f"{system_name}: Activated {{result['activated']}} entities")

    except Exception as e:
        logger.error(f"Failed to integrate {system_name}: {{e}}")
        integrations.append({{
            "system": "{system_name}",
            "status": "failed",
            "error": str(e)
        }})

"""

        code += """
    # Summary
    total_activated = sum(i.get('activated', 0) for i in integrations if i['status'] == 'success')
    total_failed = sum(i.get('failed', 0) for i in integrations if i['status'] == 'success')
    failed_systems = [i['system'] for i in integrations if i['status'] == 'failed']

    logger.info(f"\\n{'='*60}")
    logger.info(f"Hub Integration Complete")
    logger.info(f"{'='*60}")
    logger.info(f"Total entities activated: {total_activated}")
    logger.info(f"Total entities failed: {total_failed}")
    if failed_systems:
        logger.warning(f"Failed systems: {', '.join(failed_systems)}")
    logger.info(f"{'='*60}\\n")

    return integrations


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    integrate_all_hubs()
"""

        # Save integration script
        script_file = self.root_path / "tools" / "integrate_hubs.py"
        with open(script_file, "w") as f:
            f.write(code)

        # Make executable
        script_file.chmod(0o755)

        logger.info(f"Generated hub integration script: {script_file}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS AGI Entity Activator")
    parser.add_argument(
        "--root",
        default="/Users/agi_dev/Downloads/Consolidation-Repo",
        help="Root directory of the project",
    )
    parser.add_argument("--system", help="Activate specific system only")
    parser.add_argument(
        "--integrate", action="store_true", help="Run hub integration after activation"
    )

    args = parser.parse_args()

    activator = EntityActivator(args.root)

    if args.system:
        # Activate single system
        result = activator.activate_system(args.system, args.system)
        print(json.dumps(result, indent=2))
    else:
        # Activate all systems
        report = activator.activate_all_systems()

        if args.integrate:
            logger.info("\nRunning hub integration...")
            import subprocess

            result = subprocess.run(
                [sys.executable, str(Path(args.root) / "tools" / "integrate_hubs.py")],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("Hub integration successful")
                print(result.stdout)
            else:
                logger.error("Hub integration failed")
                print(result.stderr)


if __name__ == "__main__":
    main()
