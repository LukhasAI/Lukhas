#!/usr/bin/env python3
"""
Deep Code Integration Analyzer
Analyzes actual classes, functions, and dataclasses to create specific integration tasks
"""

import ast
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CodeEntity:
    """Represents a code entity (class, function, dataclass)"""

    name: str
    type: str  # 'class', 'function', 'dataclass'
    file_path: str
    line_number: int
    methods: List[str] = None
    parameters: List[str] = None
    decorators: List[str] = None
    imports: List[str] = None
    docstring: str = None

    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.parameters is None:
            self.parameters = []
        if self.decorators is None:
            self.decorators = []
        if self.imports is None:
            self.imports = []


class DeepCodeAnalyzer(ast.NodeVisitor):
    """AST visitor to extract detailed code structure"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.entities = []
        self.imports = []
        self.current_class = None

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Check if it's a dataclass
        decorators = [
            (
                d.id
                if isinstance(d, ast.Name)
                else (
                    d.func.id
                    if isinstance(d, ast.Call) and isinstance(d.func, ast.Name)
                    else None
                )
            )
            for d in node.decorator_list
        ]

        is_dataclass = "dataclass" in decorators

        # Extract methods
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                # Get method signature
                params = [arg.arg for arg in item.args.args if arg.arg != "self"]
                methods.append(
                    {
                        "name": item.name,
                        "params": params,
                        "is_async": isinstance(item, ast.AsyncFunctionDef),
                    }
                )

        entity = CodeEntity(
            name=node.name,
            type="dataclass" if is_dataclass else "class",
            file_path=self.file_path,
            line_number=node.lineno,
            methods=[m["name"] for m in methods],
            decorators=decorators,
            docstring=ast.get_docstring(node),
        )

        self.entities.append(entity)

        # Store for nested function visits
        old_class = self.current_class
        self.current_class = entity
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        if self.current_class is None:  # Only top-level functions
            params = [arg.arg for arg in node.args.args]

            entity = CodeEntity(
                name=node.name,
                type="function",
                file_path=self.file_path,
                line_number=node.lineno,
                parameters=params,
                decorators=[
                    d.id if isinstance(d, ast.Name) else str(d)
                    for d in node.decorator_list
                ],
                docstring=ast.get_docstring(node),
            )

            self.entities.append(entity)

        self.generic_visit(node)


class DeepIntegrationAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.code_entities = defaultdict(list)  # file -> list of entities
        self.entity_index = {}  # entity_name -> entity
        self.potential_connections = []
        self.missing_connections = []
        self.inactive_entities = []

    def analyze_codebase(self):
        """Analyze entire codebase for code entities"""
        print("Performing deep code analysis...")

        for root, dirs, files in os.walk(self.root_path):
            # Skip non-source directories
            dirs[:] = [
                d for d in dirs if d not in ["__pycache__", ".git", "venv", ".venv"]
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.root_path)

                    # Skip test files
                    if "test" in relative_path:
                        continue

                    try:
                        self.analyze_file(file_path, relative_path)
                    except Exception:
                        # Continue on error
                        pass

        print(
            f"Analyzed {len(self.code_entities)} files with {len(self.entity_index)} entities"
        )

    def analyze_file(self, file_path: str, relative_path: str):
        """Analyze a single file for code entities"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            analyzer = DeepCodeAnalyzer(relative_path)
            analyzer.visit(tree)

            # Store entities
            self.code_entities[relative_path] = analyzer.entities

            # Index entities
            for entity in analyzer.entities:
                entity.imports = analyzer.imports
                self.entity_index[f"{relative_path}:{entity.name}"] = entity

        except:
            # Skip files with syntax errors
            pass

    def find_integration_opportunities(self):
        """Find specific integration opportunities based on code analysis"""
        print("Finding integration opportunities...")

        # Pattern matching for integration
        patterns = {
            "hub_pattern": {
                "indicators": [
                    "Hub",
                    "Coordinator",
                    "Manager",
                    "Registry",
                    "Orchestrator",
                ],
                "methods": ["register", "coordinate", "manage", "orchestrate"],
            },
            "bridge_pattern": {
                "indicators": ["Bridge", "Adapter", "Converter", "Translator"],
                "methods": ["convert", "translate", "adapt", "transform"],
            },
            "service_pattern": {
                "indicators": ["Service", "Provider", "Handler", "Processor"],
                "methods": ["process", "handle", "provide", "serve"],
            },
            "event_pattern": {
                "indicators": ["Event", "Emitter", "Listener", "Observer"],
                "methods": ["emit", "on", "listen", "publish", "subscribe"],
            },
        }

        # Find hubs and coordinators
        hubs = {}
        services = {}
        bridges = {}
        event_systems = {}

        for file_path, entities in self.code_entities.items():
            for entity in entities:
                if entity.type in ["class", "dataclass"]:
                    # Check for hub pattern
                    for indicator in patterns["hub_pattern"]["indicators"]:
                        if indicator in entity.name:
                            hubs[entity.name] = entity
                            break

                    # Check for service pattern
                    for indicator in patterns["service_pattern"]["indicators"]:
                        if indicator in entity.name:
                            services[entity.name] = entity
                            break

                    # Check for bridge pattern
                    for indicator in patterns["bridge_pattern"]["indicators"]:
                        if indicator in entity.name:
                            bridges[entity.name] = entity
                            break

                    # Check for event pattern
                    for indicator in patterns["event_pattern"]["indicators"]:
                        if indicator in entity.name:
                            event_systems[entity.name] = entity
                            break

        # Find specific missing connections
        self.find_missing_connections(hubs, services, bridges, event_systems)

        # Find inactive entities
        self.find_inactive_entities()

    def find_missing_connections(self, hubs, services, bridges, event_systems):
        """Find specific missing connections between entities"""

        # Key systems that should be connected
        key_systems = {
            "core": ["AIInterface", "IntegrationHub", "SwarmCoordinator"],
            "consciousness": ["QuantumConsciousnessHub", "ConsciousnessCore"],
            "memory": ["MemoriaSystem", "MemoryManager", "MemoryHub"],
            "quantum": ["QuantumAttentionEconomics", "QuantumSuperposition"],
            "safety": ["AISafetyOrchestrator", "ConstitutionalSafety"],
            "nias": ["NIASCore", "NIASHub", "SymbolicMatcher"],
        }

        # Check for missing hub connections
        for system, expected_classes in key_systems.items():
            for class_name in expected_classes:
                # Find if class exists
                matching_entities = [
                    (path, entity)
                    for path, entities in self.code_entities.items()
                    for entity in entities
                    if entity.name == class_name
                ]

                if matching_entities:
                    path, entity = matching_entities[0]

                    # Check if it's imported anywhere
                    imported_in = []
                    for other_path, other_entities in self.code_entities.items():
                        if other_path != path:
                            for other_entity in other_entities:
                                if any(
                                    class_name in imp for imp in other_entity.imports
                                ):
                                    imported_in.append(other_path)

                    if not imported_in:
                        self.missing_connections.append(
                            {
                                "entity": entity,
                                "issue": "Not imported anywhere",
                                "recommendation": f"Import {entity.name} in system hubs",
                                "specific_actions": self.generate_specific_actions(
                                    entity, system
                                ),
                            }
                        )

        # Check for missing method connections
        for hub_name, hub_entity in hubs.items():
            # Check if hub has registration methods
            has_register = any(
                "register" in method.lower() for method in hub_entity.methods
            )
            if not has_register:
                self.missing_connections.append(
                    {
                        "entity": hub_entity,
                        "issue": "Hub missing registration method",
                        "recommendation": f"Add register_service method to {hub_entity.name}",
                        "specific_actions": [
                            {
                                "file": hub_entity.file_path,
                                "class": hub_entity.name,
                                "add_method": 'def register_service(self, name: str, service: Any) -> None:\n    """Register a service with the hub"""\n    self.services[name] = service',
                            }
                        ],
                    }
                )

    def find_inactive_entities(self):
        """Find potentially inactive entities (not imported or used)"""
        # Track all imports
        all_imports = set()
        for entities in self.code_entities.values():
            for entity in entities:
                all_imports.update(entity.imports)

        # Find entities not imported anywhere
        for file_path, entities in self.code_entities.items():
            module_path = file_path.replace(".py", "").replace("/", ".")

            for entity in entities:
                if entity.type in ["class", "dataclass"]:
                    # Check if entity is imported
                    entity_import_patterns = [
                        f"from {module_path} import {entity.name}",
                        f"{module_path}.{entity.name}",
                        entity.name,  # Direct import
                    ]

                    is_imported = any(
                        any(pattern in imp for pattern in entity_import_patterns)
                        for imp in all_imports
                    )

                    # Check if it's a main/test file
                    is_main = entity.name.startswith("Test") or "__main__" in file_path

                    if not is_imported and not is_main:
                        self.inactive_entities.append(
                            {
                                "entity": entity,
                                "reason": "Not imported anywhere",
                                "activation_suggestions": self.generate_activation_suggestions(
                                    entity
                                ),
                            }
                        )

    def generate_specific_actions(self, entity: CodeEntity, system: str) -> List[Dict]:
        """Generate specific integration actions for an entity"""
        actions = []

        # Find appropriate hub for the system
        hub_candidates = [
            (path, e)
            for path, entities in self.code_entities.items()
            for e in entities
            if system in path and ("Hub" in e.name or "Coordinator" in e.name)
        ]

        if hub_candidates:
            hub_path, hub_entity = hub_candidates[0]
            actions.append(
                {
                    "file": hub_path,
                    "line": 1,  # Top of file
                    "add_import": f"from {entity.file_path.replace('.py', '').replace('/', '.')} import {entity.name}",
                }
            )

            # Add to hub's __init__ method
            if "__init__" in hub_entity.methods:
                actions.append(
                    {
                        "file": hub_path,
                        "class": hub_entity.name,
                        "method": "__init__",
                        "add_code": f"self.{entity.name.lower()} = {entity.name}()",
                    }
                )
        else:
            # Need to create hub first
            hub_path = f"{system}/{system}_hub.py"
            actions.append(
                {
                    "create_file": hub_path,
                    "content": f'''"""
{system.title()} System Hub
Central coordination for {system} subsystem
"""

from typing import Dict, Any, Optional
from {entity.file_path.replace('.py', '').replace('/', '.')} import {entity.name}

class {system.title()}Hub:
    """Central hub for {system} system coordination"""

    def __init__(self):
        self.services: Dict[str, Any] = {{}}
        self.{entity.name.lower()} = {entity.name}()
        self._initialize_services()

    def _initialize_services(self):
        """Initialize all {system} services"""
        self.register_service('{entity.name.lower()}', self.{entity.name.lower()})

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self.services.get(name)

# Singleton instance
_{system}_hub_instance = None

def get_{system}_hub() -> {system.title()}Hub:
    """Get or create the {system} hub instance"""
    global _{system}_hub_instance
    if _{system}_hub_instance is None:
        _{system}_hub_instance = {system.title()}Hub()
    return _{system}_hub_instance
''',
                }
            )

        return actions

    def generate_activation_suggestions(self, entity: CodeEntity) -> List[Dict]:
        """Generate suggestions to activate an inactive entity"""
        suggestions = []

        # Determine the system based on file path
        path_parts = entity.file_path.split("/")
        system = path_parts[0] if path_parts else "unknown"

        # Suggest adding to __init__.py
        init_file = f"{'/'.join(path_parts[:-1])}/__init__.py"
        suggestions.append(
            {
                "file": init_file,
                "action": "add_export",
                "code": f"from .{path_parts[-1].replace('.py', '')} import {entity.name}",
                "export": f"__all__.append('{entity.name}')",
            }
        )

        # Suggest integration points based on entity type
        if "Service" in entity.name or "Manager" in entity.name:
            suggestions.append(
                {
                    "integration_point": f"{system}_hub.py",
                    "action": "register_service",
                    "code": f"self.register_service('{entity.name.lower()}', {entity.name}())",
                }
            )

        if "Event" in entity.name or "Handler" in entity.name:
            suggestions.append(
                {
                    "integration_point": "event_bus.py",
                    "action": "register_handler",
                    "code": f"self.event_bus.register_handler('{entity.name.lower()}', {entity.name}())",
                }
            )

        return suggestions

    def generate_detailed_report(self):
        """Generate detailed integration report with specific actions"""
        # Analyze codebase
        self.analyze_codebase()
        self.find_integration_opportunities()

        # Convert entities to serializable format
        def entity_to_dict(entity):
            return {
                "name": entity.name,
                "type": entity.type,
                "file_path": entity.file_path,
                "line_number": entity.line_number,
                "methods": entity.methods,
                "parameters": entity.parameters,
                "decorators": entity.decorators,
                "has_docstring": bool(entity.docstring),
            }

        # Convert missing connections
        missing_connections_serializable = []
        for item in self.missing_connections:
            serializable_item = {
                "entity": entity_to_dict(item["entity"]),
                "issue": item["issue"],
                "recommendation": item["recommendation"],
                "specific_actions": item["specific_actions"],
            }
            missing_connections_serializable.append(serializable_item)

        # Convert inactive entities
        inactive_entities_serializable = []
        for item in self.inactive_entities:
            serializable_item = {
                "entity": entity_to_dict(item["entity"]),
                "reason": item["reason"],
                "activation_suggestions": item["activation_suggestions"],
            }
            inactive_entities_serializable.append(serializable_item)

        # Create detailed report
        report = {
            "summary": {
                "total_files_analyzed": len(self.code_entities),
                "total_entities": len(self.entity_index),
                "missing_connections": len(self.missing_connections),
                "inactive_entities": len(self.inactive_entities),
            },
            "missing_connections": missing_connections_serializable,
            "inactive_entities": inactive_entities_serializable,
            "specific_todos": self.generate_specific_todos(),
        }

        # Save report
        with open("deep_integration_analysis.json", "w") as f:
            json.dump(report, f, indent=2)

        # Generate specific TODO list
        self.generate_todo_markdown(report)

        return report

    def generate_specific_todos(self) -> List[Dict]:
        """Generate specific TODO items with exact code changes"""
        todos = []

        # TODOs for missing connections
        for missing in self.missing_connections:
            entity = missing["entity"]
            for action in missing["specific_actions"]:
                todo = {
                    "priority": "HIGH",
                    "entity": (
                        f"{entity.file_path}:{entity.name}"
                        if hasattr(entity, "file_path")
                        else str(entity)
                    ),
                    "issue": missing["issue"],
                    "action": action,
                }
                todos.append(todo)

        # TODOs for inactive entities
        for inactive in self.inactive_entities[:20]:  # Limit to top 20
            entity = inactive["entity"]
            for suggestion in inactive["activation_suggestions"]:
                todo = {
                    "priority": "MEDIUM",
                    "entity": (
                        f"{entity.file_path}:{entity.name}"
                        if hasattr(entity, "file_path")
                        else str(entity)
                    ),
                    "issue": inactive["reason"],
                    "action": suggestion,
                }
                todos.append(todo)

        return todos

    def generate_todo_markdown(self, report):
        """Generate specific TODO markdown with exact changes"""
        with open("specific_integration_todos.md", "w") as f:
            f.write("# Specific Integration TODOs\n\n")
            f.write("Generated from deep code analysis\n\n")

            # Group by priority
            high_priority = [
                t for t in report["specific_todos"] if t["priority"] == "HIGH"
            ]
            medium_priority = [
                t for t in report["specific_todos"] if t["priority"] == "MEDIUM"
            ]

            f.write("## 🔴 HIGH PRIORITY - Missing Critical Connections\n\n")
            for i, todo in enumerate(high_priority, 1):
                f.write(f"### {i}. Fix: {todo['entity']}\n")
                f.write(f"**Issue**: {todo['issue']}\n\n")

                action = todo["action"]
                if "file" in action:
                    f.write(f"**File**: `{action['file']}`\n")
                if "create_file" in action:
                    f.write(f"**Create File**: `{action['create_file']}`\n")
                if "add_import" in action:
                    f.write(
                        f"**Add Import**:\n```python\n{action['add_import']}\n```\n"
                    )
                if "add_method" in action:
                    f.write(
                        f"**Add Method to {action.get('class', 'class')}**:\n```python\n{action['add_method']}\n```\n"
                    )
                if "add_code" in action:
                    f.write(f"**Add Code**:\n```python\n{action['add_code']}\n```\n")

                f.write("\n---\n\n")

            f.write("## 🟡 MEDIUM PRIORITY - Activate Inactive Entities\n\n")
            for i, todo in enumerate(medium_priority[:20], 1):  # Limit output
                f.write(f"### {i}. Activate: {todo['entity']}\n")
                f.write(f"**Issue**: {todo['issue']}\n\n")

                action = todo["action"]
                if "file" in action:
                    f.write(f"**File**: `{action['file']}`\n")
                if "code" in action:
                    f.write(f"**Add Code**:\n```python\n{action['code']}\n```\n")
                if "export" in action:
                    f.write(f"**Add Export**:\n```python\n{action['export']}\n```\n")

                f.write("\n---\n\n")

            # Summary of inactive entities by system
            f.write("## 📊 Inactive Entity Summary\n\n")
            inactive_by_system = defaultdict(list)
            for item in report["inactive_entities"]:
                entity = item["entity"]
                system = (
                    entity["file_path"].split("/")[0]
                    if "file_path" in entity
                    else "unknown"
                )
                inactive_by_system[system].append(entity)

            for system, entities in sorted(
                inactive_by_system.items(), key=lambda x: len(x[1]), reverse=True
            ):
                if not system.startswith("."):
                    f.write(f"### {system} ({len(entities)} inactive)\n")
                    for entity in entities[:5]:
                        f.write(f"- `{entity['name']}` in `{entity['file_path']}`\n")
                    if len(entities) > 5:
                        f.write(f"- ... and {len(entities) - 5} more\n")
                    f.write("\n")


def main():
    analyzer = DeepIntegrationAnalyzer("/Users/agi_dev/Downloads/Consolidation-Repo")
    report = analyzer.generate_detailed_report()

    print("\n" + "=" * 70)
    print("DEEP CODE INTEGRATION ANALYSIS")
    print("=" * 70)
    print(f"Files Analyzed: {report['summary']['total_files_analyzed']}")
    print(f"Code Entities Found: {report['summary']['total_entities']}")
    print(f"Missing Connections: {report['summary']['missing_connections']}")
    print(f"Inactive Entities: {report['summary']['inactive_entities']}")
    print("\nReports generated:")
    print("  - deep_integration_analysis.json")
    print("  - specific_integration_todos.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
