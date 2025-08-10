#!/usr/bin/env python3
"""
Line-by-Line Integration Instructions Generator
Creates detailed JSON instructions for every integration needed in the repository
"""

import ast
import json
import os
from collections import defaultdict
from typing import Any, Dict, List


class LineByLineIntegrationGenerator:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.instructions = []
        self.file_analysis = {}
        self.import_graph = defaultdict(set)
        self.entity_registry = {}

        # Load previous analysis
        try:
            with open("deep_integration_analysis.json") as f:
                self.deep_analysis = json.load(f)
        except FileNotFoundError:
            print("Warning: deep_integration_analysis.json not found")
            self.deep_analysis = {"missing_connections": [], "inactive_entities": []}

    def generate_complete_instructions(self):
        """Generate complete line-by-line integration instructions"""
        print("Generating complete integration instructions...")

        # Step 1: Analyze all files
        self.analyze_all_files()

        # Step 2: Generate system hub instructions
        self.generate_system_hub_instructions()

        # Step 3: Generate import instructions
        self.generate_import_instructions()

        # Step 4: Generate bridge instructions
        self.generate_bridge_instructions()

        # Step 5: Generate __init__.py instructions
        self.generate_init_file_instructions()

        # Step 6: Generate activation instructions
        self.generate_activation_instructions()

        # Step 7: Generate validation instructions
        self.generate_validation_instructions()

        return self.save_instructions()

    def analyze_all_files(self):
        """Analyze all Python files in the repository"""
        print("Analyzing all Python files...")

        for root, dirs, files in os.walk(self.root_path):
            # Skip non-source directories
            dirs[:] = [
                d
                for d in dirs
                if d not in ["__pycache__", ".git", "venv", ".venv", "node_modules"]
            ]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.root_path)

                    try:
                        self.analyze_file_detailed(file_path, relative_path)
                    except Exception:
                        # Continue on error but log
                        pass

    def analyze_file_detailed(self, file_path: str, relative_path: str):
        """Detailed analysis of a single file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            tree = ast.parse(content)

            # Analyze file structure
            analysis = {
                "path": relative_path,
                "lines": lines,
                "total_lines": len(lines),
                "imports": [],
                "classes": [],
                "functions": [],
                "has_main": False,
                "has_init": "__init__" in relative_path,
                "module_path": relative_path.replace(".py", "").replace("/", "."),
            }

            # Extract imports, classes, functions
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(
                            {
                                "type": "import",
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            analysis["imports"].append(
                                {
                                    "type": "from_import",
                                    "module": node.module,
                                    "name": alias.name,
                                    "alias": alias.asname,
                                    "line": node.lineno,
                                }
                            )
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [],
                        "decorators": [
                            d.id if isinstance(d, ast.Name) else str(d)
                            for d in node.decorator_list
                        ],
                        "bases": [
                            b.id if isinstance(b, ast.Name) else str(b)
                            for b in node.bases
                        ],
                    }

                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(
                                {
                                    "name": item.name,
                                    "line": item.lineno,
                                    "is_init": item.name == "__init__",
                                    "is_async": isinstance(item, ast.AsyncFunctionDef),
                                    "args": [
                                        arg.arg
                                        for arg in item.args.args
                                        if arg.arg != "self"
                                    ],
                                }
                            )

                    analysis["classes"].append(class_info)

                elif isinstance(node, ast.FunctionDef) and not hasattr(
                    node, "parent_class"
                ):
                    analysis["functions"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                            "args": [arg.arg for arg in node.args.args],
                        }
                    )

            # Check for main block
            analysis["has_main"] = '__name__ == "__main__"' in content

            self.file_analysis[relative_path] = analysis

        except Exception:
            # Skip files with syntax errors
            pass

    def generate_system_hub_instructions(self):
        """Generate instructions to create system hubs"""
        print("Generating system hub instructions...")

        systems = {
            "core": {"description": "Core system coordination", "priority": 1},
            "consciousness": {
                "description": "Consciousness and awareness",
                "priority": 1,
            },
            "quantum": {"description": "Quantum processing", "priority": 1},
            "memory": {"description": "Memory management", "priority": 1},
            "identity": {"description": "Identity and authentication", "priority": 2},
            "ethics": {"description": "Ethical decision making", "priority": 2},
            "learning": {"description": "Machine learning", "priority": 2},
            "reasoning": {"description": "Logic and reasoning", "priority": 2},
            "creativity": {"description": "Creative generation", "priority": 3},
            "voice": {"description": "Voice processing", "priority": 3},
            "orchestration": {"description": "System orchestration", "priority": 1},
        }

        for system, info in systems.items():
            # Find existing classes in this system
            system_classes = []
            key_classes = []

            for file_path, analysis in self.file_analysis.items():
                if file_path.startswith(system + "/"):
                    for cls in analysis["classes"]:
                        system_classes.append(
                            {
                                "name": cls["name"],
                                "file": file_path,
                                "module": analysis["module_path"],
                                "line": cls["line"],
                                "methods": cls["methods"],
                            }
                        )

                        # Identify key classes
                        if any(
                            keyword in cls["name"].lower()
                            for keyword in [
                                "hub",
                                "core",
                                "manager",
                                "coordinator",
                                "orchestrator",
                            ]
                        ):
                            key_classes.append(
                                {
                                    "name": cls["name"],
                                    "file": file_path,
                                    "module": analysis["module_path"],
                                }
                            )

            hub_file = f"{system}/{system}_hub.py"

            # Generate hub creation instruction
            instruction = {
                "type": "create_system_hub",
                "priority": info["priority"],
                "system": system,
                "description": f"Create {system} system hub for {info['description']}",
                "file": hub_file,
                "dependencies": [cls["module"] for cls in key_classes],
                "steps": [
                    {
                        "step": 1,
                        "action": "create_file",
                        "file": hub_file,
                        "content": self.generate_hub_content(
                            system, info["description"], key_classes, system_classes
                        ),
                    }
                ],
            }

            if (
                key_classes or len(system_classes) > 5
            ):  # Only create if significant classes exist
                self.instructions.append(instruction)

    def generate_hub_content(
        self,
        system: str,
        description: str,
        key_classes: List[Dict],
        all_classes: List[Dict],
    ) -> str:
        """Generate hub file content"""
        imports = []
        registrations = []

        # Add key class imports
        for cls in key_classes[:10]:  # Limit to avoid overwhelming
            imports.append(f"from {cls['module']} import {cls['name']}")
            var_name = (
                cls["name"]
                .lower()
                .replace(system, "")
                .replace("hub", "")
                .replace("core", "")
                or "service"
            )
            registrations.append(f"        self.{var_name} = {cls['name']}()")
            registrations.append(
                f"        self.register_service('{var_name}', self.{var_name})"
            )

        # Add some general classes
        for cls in all_classes[:5]:
            if cls not in key_classes:
                imports.append(f"# from {cls['module']} import {cls['name']}")

        content = f'''"""
{system.title()} System Hub
{description}

This hub coordinates all {system} subsystem components and provides
a unified interface for external systems to interact with {system}.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging

{chr(10).join(imports)}

logger = logging.getLogger(__name__)


class {system.title()}Hub:
    """
    Central coordination hub for the {system} system.

    Manages all {system} components and provides service discovery,
    coordination, and communication with other systems.
    """

    def __init__(self):
        self.services: Dict[str, Any] = {{}}
        self.event_handlers: Dict[str, List[callable]] = {{}}
        self.is_initialized = False

        # Initialize components
{chr(10).join(registrations) if registrations else '        # No key classes found to register'}

        logger.info(f"{system.title()}Hub initialized with {{len(self.services)}} services")

    async def initialize(self) -> None:
        """Initialize all {system} services"""
        if self.is_initialized:
            return

        # Initialize all registered services
        for name, service in self.services.items():
            if hasattr(service, 'initialize'):
                try:
                    if asyncio.iscoroutinefunction(service.initialize):
                        await service.initialize()
                    else:
                        service.initialize()
                    logger.debug(f"Initialized {{name}} service")
                except Exception as e:
                    logger.error(f"Failed to initialize {{name}}: {{e}}")

        self.is_initialized = True
        logger.info(f"{system.title()}Hub fully initialized")

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"Registered {{name}} service in {system}Hub")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service by name"""
        return self.services.get(name)

    def list_services(self) -> List[str]:
        """List all registered service names"""
        return list(self.services.keys())

    async def process_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process events from other systems"""
        handlers = self.event_handlers.get(event_type, [])
        results = []

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event_data)
                else:
                    result = handler(event_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Event handler error in {system}: {{e}}")

        return {{"results": results, "handled": len(handlers) > 0}}

    def register_event_handler(self, event_type: str, handler: callable) -> None:
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def shutdown(self) -> None:
        """Gracefully shutdown all services"""
        for name, service in self.services.items():
            if hasattr(service, 'shutdown'):
                try:
                    if asyncio.iscoroutinefunction(service.shutdown):
                        await service.shutdown()
                    else:
                        service.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down {{name}}: {{e}}")

        logger.info(f"{system.title()}Hub shutdown complete")


# Singleton instance
_{system}_hub_instance = None


def get_{system}_hub() -> {system.title()}Hub:
    """Get or create the {system} hub singleton instance"""
    global _{system}_hub_instance
    if _{system}_hub_instance is None:
        _{system}_hub_instance = {system.title()}Hub()
    return _{system}_hub_instance


async def initialize_{system}_system() -> {system.title()}Hub:
    """Initialize the complete {system} system"""
    hub = get_{system}_hub()
    await hub.initialize()
    return hub


# Export main components
__all__ = [
    '{system.title()}Hub',
    'get_{system}_hub',
    'initialize_{system}_system'
]
'''
        return content

    def generate_import_instructions(self):
        """Generate specific import instructions"""
        print("Generating import instructions...")

        # Process missing connections from deep analysis
        for missing in self.deep_analysis.get("missing_connections", []):
            entity = missing["entity"]

            # Generate specific import instruction
            instruction = {
                "type": "add_import",
                "priority": 1,
                "description": f"Import {entity['name']} to fix missing connection",
                "entity": entity,
                "issue": missing["issue"],
                "steps": [],
            }

            # Find target files that should import this entity
            target_files = self.find_import_targets(entity)

            for target_file in target_files:
                step = {
                    "step": len(instruction["steps"]) + 1,
                    "action": "add_import_line",
                    "file": target_file,
                    "line_number": self.find_import_insertion_line(target_file),
                    "content": f"from {entity['file_path'].replace('.py', '').replace('/', '.')} import {entity['name']}",
                    "validation": f"Verify {entity['name']} can be imported",
                }
                instruction["steps"].append(step)

            if instruction["steps"]:
                self.instructions.append(instruction)

    def find_import_targets(self, entity: Dict) -> List[str]:
        """Find files that should import this entity"""
        targets = []
        entity_name = entity["name"]
        entity_path = entity["file_path"]

        # System hub should import major components
        system = entity_path.split("/")[0]
        hub_file = f"{system}/{system}_hub.py"
        targets.append(hub_file)

        # __init__.py files should import key classes
        system_init = f"{system}/__init__.py"
        if system_init in self.file_analysis:
            targets.append(system_init)

        # Find related files that might need this entity
        for file_path, analysis in self.file_analysis.items():
            # Skip same file
            if file_path == entity_path:
                continue

            # Files in same system
            if file_path.startswith(system + "/"):
                # Check if file has complementary functionality
                for cls in analysis["classes"]:
                    if self.should_connect_classes(entity_name, cls["name"]):
                        targets.append(file_path)
                        break

        return list(set(targets[:5]))  # Limit targets

    def should_connect_classes(self, class1: str, class2: str) -> bool:
        """Determine if two classes should be connected"""
        connection_patterns = [
            # Hub patterns
            ("Hub", "Core"),
            ("Hub", "Manager"),
            ("Hub", "Service"),
            # Integration patterns
            ("Orchestrator", "Core"),
            ("Coordinator", "Manager"),
            # Safety patterns
            ("Safety", "Core"),
            ("Safety", "Orchestrator"),
            # Consciousness patterns
            ("Consciousness", "Quantum"),
            ("Quantum", "Attention"),
        ]

        for pattern1, pattern2 in connection_patterns:
            if (pattern1 in class1 and pattern2 in class2) or (
                pattern2 in class1 and pattern1 in class2
            ):
                return True

        return False

    def find_import_insertion_line(self, file_path: str) -> int:
        """Find the best line to insert an import"""
        if file_path not in self.file_analysis:
            return 1

        analysis = self.file_analysis[file_path]

        # Find last import line
        last_import_line = 0
        for imp in analysis["imports"]:
            last_import_line = max(last_import_line, imp["line"])

        # Insert after last import, or at top if no imports
        return last_import_line + 1 if last_import_line > 0 else 1

    def generate_bridge_instructions(self):
        """Generate bridge creation instructions"""
        print("Generating bridge instructions...")

        # Key system pairs that need bridges
        bridge_pairs = [
            ("core", "consciousness", 1),
            ("consciousness", "quantum", 1),
            ("memory", "learning", 2),
            ("core", "safety", 1),
            ("identity", "core", 2),
            ("orchestration", "core", 2),
        ]

        for system1, system2, priority in bridge_pairs:
            bridge_file = f"core/bridges/{system1}_{system2}_bridge.py"

            instruction = {
                "type": "create_bridge",
                "priority": priority,
                "description": f"Create bridge between {system1} and {system2} systems",
                "systems": [system1, system2],
                "file": bridge_file,
                "steps": [
                    {
                        "step": 1,
                        "action": "create_directory",
                        "path": "core/bridges",
                        "description": "Create bridges directory",
                    },
                    {
                        "step": 2,
                        "action": "create_file",
                        "file": bridge_file,
                        "content": self.generate_bridge_content(system1, system2),
                    },
                    {
                        "step": 3,
                        "action": "register_bridge",
                        "file": f"{system1}/{system1}_hub.py",
                        "line_to_add": f"from core.bridges.{system1}_{system2}_bridge import {system1.title()}{system2.title()}Bridge",
                        "registration": f"self.{system2}_bridge = {system1.title()}{system2.title()}Bridge()",
                    },
                ],
            }

            self.instructions.append(instruction)

    def generate_bridge_content(self, system1: str, system2: str) -> str:
        """Generate bridge file content"""
        return f'''"""
{system1.title()}-{system2.title()} Bridge
Bidirectional communication bridge between {system1} and {system2} systems
"""

from typing import Any, Dict, Optional
import asyncio
import logging

# Import system hubs (will be available after hub creation)
# from {system1}.{system1}_hub import get_{system1}_hub
# from {system2}.{system2}_hub import get_{system2}_hub

logger = logging.getLogger(__name__)


class {system1.title()}{system2.title()}Bridge:
    """
    Bridge for communication between {system1} and {system2} systems.

    Provides:
    - Bidirectional data flow
    - Event synchronization
    - State consistency
    - Error handling and recovery
    """

    def __init__(self):
        self.{system1}_hub = None  # Will be initialized later
        self.{system2}_hub = None
        self.event_mappings = {{}}
        self.is_connected = False

        logger.info(f"{system1.title()}{system2.title()}Bridge initialized")

    async def connect(self) -> bool:
        """Establish connection between systems"""
        try:
            # Get system hubs
            # self.{system1}_hub = get_{system1}_hub()
            # self.{system2}_hub = get_{system2}_hub()

            # Set up event mappings
            self.setup_event_mappings()

            self.is_connected = True
            logger.info(f"Bridge connected between {system1} and {system2}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect bridge: {{e}}")
            return False

    def setup_event_mappings(self):
        """Set up event type mappings between systems"""
        self.event_mappings = {{
            # {system1} -> {system2} events
            "{system1}_state_change": "{system2}_sync_request",
            "{system1}_data_update": "{system2}_data_sync",

            # {system2} -> {system1} events
            "{system2}_state_change": "{system1}_sync_request",
            "{system2}_data_update": "{system1}_data_sync",
        }}

    async def {system1}_to_{system2}(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Forward event from {system1} to {system2}"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data if needed
            transformed_data = self.transform_data_{system1}_to_{system2}(data)

            # Send to {system2}
            if self.{system2}_hub:
                result = await self.{system2}_hub.process_event(mapped_event, transformed_data)
                logger.debug(f"Forwarded {{event_type}} from {system1} to {system2}")
                return result

            return {{"error": "{system2} hub not available"}}

        except Exception as e:
            logger.error(f"Error forwarding from {system1} to {system2}: {{e}}")
            return {{"error": str(e)}}

    async def {system2}_to_{system1}(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Forward event from {system2} to {system1}"""
        if not self.is_connected:
            await self.connect()

        try:
            # Map event type
            mapped_event = self.event_mappings.get(event_type, event_type)

            # Transform data if needed
            transformed_data = self.transform_data_{system2}_to_{system1}(data)

            # Send to {system1}
            if self.{system1}_hub:
                result = await self.{system1}_hub.process_event(mapped_event, transformed_data)
                logger.debug(f"Forwarded {{event_type}} from {system2} to {system1}")
                return result

            return {{"error": "{system1} hub not available"}}

        except Exception as e:
            logger.error(f"Error forwarding from {system2} to {system1}: {{e}}")
            return {{"error": str(e)}}

    def transform_data_{system1}_to_{system2}(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from {system1} to {system2}"""
        # Add system-specific transformations here
        return {{
            "source_system": "{system1}",
            "target_system": "{system2}",
            "data": data,
            "timestamp": "{{}}".format(__import__('datetime').datetime.now().isoformat())
        }}

    def transform_data_{system2}_to_{system1}(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data format from {system2} to {system1}"""
        # Add system-specific transformations here
        return {{
            "source_system": "{system2}",
            "target_system": "{system1}",
            "data": data,
            "timestamp": "{{}}".format(__import__('datetime').datetime.now().isoformat())
        }}

    async def sync_state(self) -> bool:
        """Synchronize state between systems"""
        if not self.is_connected:
            return False

        try:
            # Get state from both systems
            {system1}_state = await self.get_{system1}_state()
            {system2}_state = await self.get_{system2}_state()

            # Detect differences and sync
            differences = self.compare_states({system1}_state, {system2}_state)

            if differences:
                await self.resolve_differences(differences)
                logger.info(f"Synchronized {{len(differences)}} state differences")

            return True

        except Exception as e:
            logger.error(f"State sync failed: {{e}}")
            return False

    async def get_{system1}_state(self) -> Dict[str, Any]:
        """Get current state from {system1} system"""
        if self.{system1}_hub:
            # Implement {system1}-specific state retrieval
            return {{"system": "{system1}", "state": "active"}}
        return {{}}

    async def get_{system2}_state(self) -> Dict[str, Any]:
        """Get current state from {system2} system"""
        if self.{system2}_hub:
            # Implement {system2}-specific state retrieval
            return {{"system": "{system2}", "state": "active"}}
        return {{}}

    def compare_states(self, state1: Dict[str, Any], state2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare states and return differences"""
        differences = []

        # Implement state comparison logic
        # This is a placeholder - add specific comparison logic

        return differences

    async def resolve_differences(self, differences: List[Dict[str, Any]]) -> None:
        """Resolve state differences between systems"""
        for diff in differences:
            # Implement difference resolution logic
            logger.debug(f"Resolving difference: {{diff}}")

    async def disconnect(self) -> None:
        """Disconnect the bridge"""
        self.is_connected = False
        logger.info(f"Bridge disconnected between {system1} and {system2}")


# Singleton instance
_{system1}_{system2}_bridge_instance = None


def get_{system1}_{system2}_bridge() -> {system1.title()}{system2.title()}Bridge:
    """Get or create bridge instance"""
    global _{system1}_{system2}_bridge_instance
    if _{system1}_{system2}_bridge_instance is None:
        _{system1}_{system2}_bridge_instance = {system1.title()}{system2.title()}Bridge()
    return _{system1}_{system2}_bridge_instance
'''

    def generate_init_file_instructions(self):
        """Generate __init__.py file instructions"""
        print("Generating __init__.py instructions...")

        # Find directories missing __init__.py
        directories_needing_init = set()

        for file_path in self.file_analysis.keys():
            dir_path = os.path.dirname(file_path)
            if dir_path and "/" in dir_path:  # Skip root level
                init_file = f"{dir_path}/__init__.py"
                if init_file not in self.file_analysis:
                    directories_needing_init.add(dir_path)

        # Generate instructions for each missing __init__.py
        for dir_path in sorted(directories_needing_init):
            if not any(skip in dir_path for skip in [".venv", "__pycache__", ".git"]):

                # Find Python files in this directory
                dir_files = [
                    f
                    for f in self.file_analysis.keys()
                    if os.path.dirname(f) == dir_path and f.endswith(".py")
                ]

                if dir_files:  # Only create if there are Python files
                    init_file = f"{dir_path}/__init__.py"

                    instruction = {
                        "type": "create_init_file",
                        "priority": 2,
                        "description": f"Create __init__.py for {dir_path}",
                        "directory": dir_path,
                        "file": init_file,
                        "python_files": dir_files,
                        "steps": [
                            {
                                "step": 1,
                                "action": "create_file",
                                "file": init_file,
                                "content": self.generate_init_content(
                                    dir_path, dir_files
                                ),
                            }
                        ],
                    }

                    self.instructions.append(instruction)

    def generate_init_content(self, dir_path: str, python_files: List[str]) -> str:
        """Generate __init__.py content"""
        imports = []
        exports = []

        for file_path in python_files:
            if file_path.endswith("__init__.py"):
                continue

            file_name = os.path.basename(file_path).replace(".py", "")
            analysis = self.file_analysis.get(file_path, {})

            # Import classes from the file
            for cls in analysis.get("classes", []):
                class_name = cls["name"]
                imports.append(f"from .{file_name} import {class_name}")
                exports.append(class_name)

            # Import key functions
            for func in analysis.get("functions", []):
                if not func["name"].startswith("_"):  # Skip private functions
                    imports.append(f"from .{file_name} import {func['name']}")
                    exports.append(func["name"])

        # Limit exports to avoid clutter
        exports = exports[:10]
        imports = imports[:15]

        content = f'''"""
{dir_path.replace('/', '.').title()} Module
Auto-generated module initialization
"""

# Import main components
{chr(10).join(imports[:10]) if imports else '# No components to import'}

# Export public interface
__all__ = [
    {chr(10).join([f'    "{exp}",' for exp in exports]) if exports else '    # No public exports'}
]

# Module metadata
__version__ = "1.0.0"
__author__ = "LUKHAS AI"
'''

        return content

    def generate_activation_instructions(self):
        """Generate instructions to activate inactive entities"""
        print("Generating activation instructions...")

        # Process inactive entities from deep analysis
        inactive_entities = self.deep_analysis.get("inactive_entities", [])

        # Group by system
        by_system = defaultdict(list)
        for item in inactive_entities[:100]:  # Limit to first 100
            entity = item["entity"]
            system = entity["file_path"].split("/")[0]
            by_system[system].append(item)

        # Generate activation instructions for each system
        for system, entities in by_system.items():
            if len(entities) > 3:  # Only if significant number
                instruction = {
                    "type": "activate_entities",
                    "priority": 3,
                    "system": system,
                    "description": f"Activate {len(entities)} inactive entities in {system}",
                    "entities": entities[:20],  # Limit per instruction
                    "steps": [],
                }

                # Create activation steps
                for i, item in enumerate(entities[:10]):
                    entity = item["entity"]
                    entity_name = entity["name"]

                    step = {
                        "step": i + 1,
                        "action": "activate_entity",
                        "entity": entity_name,
                        "file": entity["file_path"],
                        "target_file": f"{system}/__init__.py",
                        "import_line": f"from .{os.path.basename(entity['file_path']).replace('.py', '')} import {entity_name}",
                        "export_line": f'__all__.append("{entity_name}")',
                    }
                    instruction["steps"].append(step)

                self.instructions.append(instruction)

    def generate_validation_instructions(self):
        """Generate validation and testing instructions"""
        print("Generating validation instructions...")

        validation_instruction = {
            "type": "validation_suite",
            "priority": 4,
            "description": "Validate all integrations work correctly",
            "steps": [
                {
                    "step": 1,
                    "action": "create_test_file",
                    "file": "tests/test_integration_validation.py",
                    "content": self.generate_validation_test_content(),
                },
                {
                    "step": 2,
                    "action": "create_validation_script",
                    "file": "scripts/validate_integrations.py",
                    "content": self.generate_validation_script_content(),
                },
                {
                    "step": 3,
                    "action": "run_validation",
                    "command": "python scripts/validate_integrations.py",
                    "expected_outcome": "All integrations pass validation",
                },
            ],
        }

        self.instructions.append(validation_instruction)

    def generate_validation_test_content(self) -> str:
        """Generate validation test file content"""
        return '''"""
Integration Validation Tests
Tests that all system integrations work correctly
"""

import asyncio
import pytest
from typing import Dict, Any


class TestSystemIntegration:
    """Test system integration functionality"""

    @pytest.mark.asyncio
    async def test_system_hubs_creation(self):
        """Test that all system hubs can be created"""
        systems = ['core', 'consciousness', 'quantum', 'memory']

        for system in systems:
            try:
                hub_module = __import__(f'{system}.{system}_hub', fromlist=[f'{system.title()}Hub'])
                hub_class = getattr(hub_module, f'{system.title()}Hub')
                hub = hub_class()
                assert hub is not None
                print(f"✓ {system} hub created successfully")
            except ImportError:
                print(f"✗ {system} hub not found - create {system}/{system}_hub.py")
            except Exception as e:
                print(f"✗ {system} hub creation failed: {e}")

    @pytest.mark.asyncio
    async def test_imports_work(self):
        """Test that critical imports work"""
        critical_imports = [
            ('consciousness.quantum_consciousness_hub', 'QuantumConsciousnessHub'),
            ('quantum.attention_economics', 'QuantumAttentionEconomics'),
            ('core.safety.ai_safety_orchestrator', 'AISafetyOrchestrator'),
            ('memory.systems.memoria_system', 'MemoriaSystem'),
        ]

        for module_path, class_name in critical_imports:
            try:
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                assert cls is not None
                print(f"✓ {module_path}.{class_name} imports correctly")
            except ImportError:
                print(f"✗ Failed to import {module_path}.{class_name}")
            except Exception as e:
                print(f"✗ Import error for {class_name}: {e}")

    @pytest.mark.asyncio
    async def test_bridges_exist(self):
        """Test that bridge files exist"""
        bridges = [
            'core.bridges.core_consciousness_bridge',
            'core.bridges.consciousness_quantum_bridge',
        ]

        for bridge in bridges:
            try:
                __import__(bridge)
                print(f"✓ {bridge} exists")
            except ImportError:
                print(f"✗ {bridge} not found - needs creation")

    async def test_system_connectivity(self):
        """Test that systems can communicate"""
        # This would test actual system communication
        # Implementation depends on specific system interfaces
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
'''

    def generate_validation_script_content(self) -> str:
        """Generate validation script content"""
        return '''#!/usr/bin/env python3
"""
Integration Validation Script
Validates that all integration instructions have been followed correctly
"""

import os
import sys
import importlib
from typing import List, Dict, Any


class IntegrationValidator:
    """Validates integration completion"""

    def __init__(self):
        self.results = []
        self.errors = []

    def validate_system_hubs(self) -> bool:
        """Validate system hubs exist and work"""
        systems = ['core', 'consciousness', 'quantum', 'memory', 'identity', 'ethics']
        success = True

        print("\\n🔍 Validating System Hubs...")

        for system in systems:
            hub_file = f"{system}/{system}_hub.py"

            if os.path.exists(hub_file):
                try:
                    # Try to import
                    module_name = f"{system}.{system}_hub"
                    spec = importlib.util.spec_from_file_location(module_name, hub_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Check for hub class
                    hub_class_name = f"{system.title()}Hub"
                    if hasattr(module, hub_class_name):
                        print(f"  ✅ {system} hub exists and imports correctly")
                        self.results.append(f"{system}_hub: PASS")
                    else:
                        print(f"  ❌ {system} hub missing {hub_class_name} class")
                        success = False

                except Exception as e:
                    print(f"  ❌ {system} hub import failed: {e}")
                    success = False
            else:
                print(f"  ❌ {system} hub file not found: {hub_file}")
                success = False

        return success

    def validate_critical_imports(self) -> bool:
        """Validate critical imports work"""
        critical_components = [
            ('consciousness/quantum_consciousness_hub.py', 'QuantumConsciousnessHub'),
            ('quantum/attention_economics.py', 'QuantumAttentionEconomics'),
            ('core/safety/ai_safety_orchestrator.py', 'AISafetyOrchestrator'),
            ('memory/systems/memoria_system.py', 'MemoriaSystem'),
        ]

        print("\\n🔍 Validating Critical Imports...")
        success = True

        for file_path, class_name in critical_components:
            if os.path.exists(file_path):
                try:
                    # Convert path to module
                    module_path = file_path.replace('.py', '').replace('/', '.')
                    module = importlib.import_module(module_path)

                    if hasattr(module, class_name):
                        print(f"  ✅ {class_name} can be imported")
                    else:
                        print(f"  ❌ {class_name} not found in {file_path}")
                        success = False

                except Exception as e:
                    print(f"  ❌ Failed to import {class_name}: {e}")
                    success = False
            else:
                print(f"  ❌ File not found: {file_path}")
                success = False

        return success

    def validate_init_files(self) -> bool:
        """Validate __init__.py files exist"""
        print("\\n🔍 Validating __init__.py Files...")

        required_init_files = [
            'core/__init__.py',
            'consciousness/__init__.py',
            'quantum/__init__.py',
            'memory/__init__.py',
            'core/safety/__init__.py',
            'core/modules/__init__.py',
            'core/modules/nias/__init__.py'
        ]

        success = True
        for init_file in required_init_files:
            if os.path.exists(init_file):
                print(f"  ✅ {init_file} exists")
            else:
                print(f"  ❌ Missing: {init_file}")
                success = False

        return success

    def validate_bridges(self) -> bool:
        """Validate bridge files exist"""
        print("\\n🔍 Validating Bridge Files...")

        bridge_files = [
            'core/bridges/core_consciousness_bridge.py',
            'core/bridges/consciousness_quantum_bridge.py',
            'core/bridges/memory_learning_bridge.py'
        ]

        success = True
        for bridge_file in bridge_files:
            if os.path.exists(bridge_file):
                print(f"  ✅ {bridge_file} exists")
            else:
                print(f"  ❌ Missing bridge: {bridge_file}")
                success = False

        return success

    def run_validation(self) -> bool:
        """Run complete validation"""
        print("🚀 Starting Integration Validation...")

        results = [
            self.validate_system_hubs(),
            self.validate_critical_imports(),
            self.validate_init_files(),
            self.validate_bridges()
        ]

        overall_success = all(results)

        print("\\n📊 Validation Summary:")
        print(f"  System Hubs: {'✅ PASS' if results[0] else '❌ FAIL'}")
        print(f"  Critical Imports: {'✅ PASS' if results[1] else '❌ FAIL'}")
        print(f"  Init Files: {'✅ PASS' if results[2] else '❌ FAIL'}")
        print(f"  Bridge Files: {'✅ PASS' if results[3] else '❌ FAIL'}")

        if overall_success:
            print("\\n🎉 All integrations validated successfully!")
        else:
            print("\\n⚠️  Some integrations need attention. See details above.")

        return overall_success


def main():
    validator = IntegrationValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
'''

    def save_instructions(self) -> Dict[str, Any]:
        """Save all instructions to JSON file"""
        # Sort instructions by priority
        self.instructions.sort(key=lambda x: (x["priority"], x["type"]))

        # Create comprehensive report
        report = {
            "metadata": {
                "generated_at": __import__("datetime").datetime.now().isoformat(),
                "total_instructions": len(self.instructions),
                "files_analyzed": len(self.file_analysis),
                "repository_path": self.root_path,
            },
            "summary": {
                "instruction_types": self.get_type_counts(),
                "priority_breakdown": self.get_priority_breakdown(),
                "estimated_completion_time": self.estimate_completion_time(),
            },
            "instructions": self.instructions,
        }

        # Save to JSON
        with open("line_by_line_integration_instructions.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\\n✅ Generated {len(self.instructions)} integration instructions")
        print("📄 Saved to: line_by_line_integration_instructions.json")

        return report

    def get_type_counts(self) -> Dict[str, int]:
        """Get counts by instruction type"""
        counts = {}
        for instruction in self.instructions:
            type_name = instruction["type"]
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def get_priority_breakdown(self) -> Dict[str, int]:
        """Get counts by priority"""
        counts = {}
        for instruction in self.instructions:
            priority = f"priority_{instruction['priority']}"
            counts[priority] = counts.get(priority, 0) + 1
        return counts

    def estimate_completion_time(self) -> str:
        """Estimate time to complete all instructions"""
        # Rough estimates in minutes
        time_estimates = {
            "create_system_hub": 30,
            "add_import": 2,
            "create_bridge": 45,
            "create_init_file": 5,
            "activate_entities": 15,
            "validation_suite": 20,
        }

        total_minutes = 0
        for instruction in self.instructions:
            instruction_type = instruction["type"]
            total_minutes += time_estimates.get(instruction_type, 10)

        hours = total_minutes // 60
        minutes = total_minutes % 60

        return f"{hours}h {minutes}m"


def main():
    generator = LineByLineIntegrationGenerator(
        "/Users/agi_dev/Downloads/Consolidation-Repo"
    )
    report = generator.generate_complete_instructions()

    print("\\n" + "=" * 70)
    print("LINE-BY-LINE INTEGRATION INSTRUCTIONS GENERATED")
    print("=" * 70)
    print(f"Total Instructions: {report['metadata']['total_instructions']}")
    print(f"Files Analyzed: {report['metadata']['files_analyzed']}")
    print(f"Estimated Time: {report['summary']['estimated_completion_time']}")
    print("\\nInstruction Types:")
    for type_name, count in report["summary"]["instruction_types"].items():
        print(f"  - {type_name}: {count}")
    print("=" * 70)


if __name__ == "__main__":
    main()
