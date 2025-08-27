#!/usr/bin/env python3
"""

#TAG:core
#TAG:integration
#TAG:neuroplastic
#TAG:colony

Neuroplastic Consolidator - Connects isolated files and creates unified modules
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path


class NeuroplasticConsolidator:

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.changes = []
        self.connections_made = 0

        # Define the 7 core neuroplastic modules
        self.core_modules = {
            "CORE": {
                "path": "core/",
                "description": "Central nervous system with GLYPH engine",
                "absorbs": [
                    "utilities",
                    "helpers",
                    "common",
                    "shared",
                    "base",
                ],
            },
            "CONSCIOUSNESS": {
                "path": "consciousness/",
                "description": "Awareness and decision-making systems",
                "absorbs": [
                    "awareness",
                    "reflection",
                    "decision",
                    "cognitive",
                ],
            },
            "MEMORY": {
                "path": "memory/",
                "description": "Fold-based memory with causal chains",
                "absorbs": [
                    "storage",
                    "recall",
                    "episodic",
                    "semantic",
                    "trace",
                ],
            },
            "QIM": {
                "path": "qim/",  # Already renamed from qi
                "description": "Quantum-Inspired Metaphors and algorithms",
                "absorbs": ["quantum", "probabilistic", "oscillator", "wave"],
            },
            "EMOTION": {
                "path": "emotion/",
                "description": "Emotional processing and VAD affect",
                "absorbs": ["affect", "mood", "sentiment", "feeling"],
            },
            "GOVERNANCE": {
                "path": "governance/",
                "description": "Guardian system and ethical oversight",
                "absorbs": [
                    "ethics",
                    "policy",
                    "compliance",
                    "security",
                    "auth",
                ],
            },
            "BRIDGE": {
                "path": "bridge/",
                "description": "External connections and API interfaces",
                "absorbs": [
                    "api",
                    "interface",
                    "connector",
                    "adapter",
                    "integration",
                ],
            },
        }

    def load_isolated_files(self):
        """Load the isolated files report"""
        with open("isolated_files_report.json") as f:
            return json.load(f)

    def categorize_file(self, filepath):
        """Determine which core module a file belongs to"""
        filename = Path(filepath).name.lower()
        filepath_lower = filepath.lower()

        # Check each module's absorption patterns
        for module, config in self.core_modules.items():
            for pattern in config["absorbs"]:
                if pattern in filepath_lower or pattern in filename:
                    return module

        # Special cases based on content
        if "learn" in filepath_lower:
            return "CONSCIOUSNESS"  # Learning goes to consciousness
        elif "dream" in filepath_lower:
            return "CONSCIOUSNESS"  # Dreams are part of consciousness
        elif "bio" in filepath_lower:
            return "QIM"  # Bio-inspired goes to QIM
        elif "voice" in filepath_lower or "speech" in filepath_lower:
            return "BRIDGE"  # Voice interfaces go to bridge
        elif "vision" in filepath_lower or "visual" in filepath_lower:
            return "BRIDGE"  # Visual interfaces go to bridge

        # Default based on current location
        for module, config in self.core_modules.items():
            if config["path"] in filepath:
                return module

        return "CORE"  # Default to core

    def create_module_connectors(self):
        """Create connector files for each core module"""
        for module, config in self.core_modules.items():
            module_path = Path(config["path"])

            # Create neuroplastic connector
            connector_path = module_path / "neuroplastic_connector.py"

            connector_content = f'''"""
Neuroplastic Connector for {module} Module
Auto-generated connector that integrates isolated components
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class {module.title()}Connector:
    """Connects isolated components into the {module} nervous system"""

    def __init__(self):
        self.connected_components = {{}}
        self.hormone_tags = {{}}  # For neuroplastic responses

    def connect_component(self, name: str, component: Any):
        """Connect an isolated component to this module"""
        self.connected_components[name] = component
        logger.info(f"Connected {{name}} to {module} module")

    def emit_hormone(self, hormone: str, intensity: float = 1.0):
        """Emit hormone signal for neuroplastic response"""
        self.hormone_tags[hormone] = intensity

    def get_stress_response(self) -> Dict[str, float]:
        """Get current stress hormones for neuroplastic reorganization"""
        return {{
            'cortisol': self.hormone_tags.get('cortisol', 0.0),
            'adrenaline': self.hormone_tags.get('adrenaline', 0.0),
            'norepinephrine': self.hormone_tags.get('norepinephrine', 0.0)
        }}

# Global connector instance
connector = {module.title()}Connector()

# Auto-import isolated components
try:
    # Components will be added here during consolidation
    pass
except ImportError as e:
    logger.warning(f"Failed to import some {module} components: {{e}}")
'''

            with open(connector_path, "w") as f:
                f.write(connector_content)

            self.changes.append(f"Created connector: {connector_path}")
            print(f"✅ Created neuroplastic connector for {module}")

    def connect_isolated_file(self, filepath, target_module):
        """Connect an isolated file to its target module"""
        source = Path(filepath)
        if not source.exists():
            return False

        # Determine target location
        module_config = self.core_modules[target_module]
        target_dir = Path(module_config["path"]) / "connected"
        target_dir.mkdir(exist_ok=True)

        # Copy file to connected directory
        target_path = target_dir / source.name

        try:
            shutil.copy2(source, target_path)

            # Update the module's connector to import this component
            self._update_connector(target_module, source.name)

            self.connections_made += 1
            self.changes.append(f"Connected {source.name} to {target_module}")
            return True

        except Exception as e:
            print(f"❌ Failed to connect {filepath}: {e}")
            return False

    def _update_connector(self, module, filename):
        """Update the module connector to import the new component"""
        connector_path = (
            Path(self.core_modules[module]["path"]) / "neuroplastic_connector.py"
        )

        if connector_path.exists():
            with open(connector_path) as f:
                content = f.read()

            # Add import to the try block
            import_line = f"    from .connected.{filename[:-3]} import *"
            content = content.replace(
                "    # Components will be added here during consolidation",
                f"{import_line}\n    ",
            )

            with open(connector_path, "w") as f:
                f.write(content)

    def consolidate_tools(self):
        """Consolidate scattered tools into organized structure"""
        tools_dir = Path("tools")

        # Create organized subdirectories
        subdirs = {
            "analysis": "Analysis and inspection tools",
            "scripts": "Utility scripts",
            "deployment": "Deployment and setup tools",
            "testing": "Testing utilities",
        }

        for subdir, _desc in subdirs.items():
            (tools_dir / subdir).mkdir(exist_ok=True)

        # Move root-level scripts to tools/scripts
        root_scripts = [
            "bootstrap.py",
            "health_monitor.py",
            "healing/simple_conflict_healer.py",
            "healing/syntax_doctor.py",
            "healing/advanced_syntax_fixer.py",
            "healing/targeted_syntax_fix.py",
        ]

        for script in root_scripts:
            if Path(script).exists():
                target = tools_dir / "scripts" / Path(script).name
                shutil.copy2(script, target)
                self.changes.append(f"Organized {script} -> {target}")

    def create_module_bridges(self):
        """Create bridges between modules for cross-communication"""
        bridge_content = '''"""
Neuroplastic Module Bridge
Enables cross-module communication with hormone-based signaling
"""

from typing import Dict, Optional, Any
import asyncio
from collections import defaultdict

class NeuroplasticBridge:
    """Central bridge for inter-module communication"""

    def __init__(self):
        self.modules = {}
        self.hormone_levels = defaultdict(float)
        self.connections = defaultdict(list)

    def register_module(self, name: str, connector: Any):
        """Register a module connector"""
        self.modules[name] = connector

    async def emit_hormone(self, hormone: str, intensity: float, source: str):
        """Emit hormone signal across all modules"""
        self.hormone_levels[hormone] = intensity

        # Notify all modules
        for module_name, connector in self.modules.items():
            if hasattr(connector, 'emit_hormone'):
                connector.emit_hormone(hormone, intensity)

    def create_synapse(self, module_a: str, module_b: str):
        """Create a connection between two modules"""
        self.connections[module_a].append(module_b)
        self.connections[module_b].append(module_a)

    def get_network_state(self) -> Dict[str, Any]:
        """Get current state of the neural network"""
        return {
            'modules': list(self.modules.keys()),
            'hormone_levels': dict(self.hormone_levels),
            'connections': dict(self.connections),
            'stress_level': self._calculate_stress_level()
        }

    def _calculate_stress_level(self) -> float:
        """Calculate overall system stress"""
        stress_hormones = ['cortisol', 'adrenaline', 'norepinephrine']
        total_stress = sum(self.hormone_levels.get(h, 0) for h in stress_hormones)
        return min(1.0, total_stress / 3.0)

# Global bridge instance
neural_bridge = NeuroplasticBridge()
'''

        bridge_path = Path("core/neural_bridge.py")
        with open(bridge_path, "w") as f:
            f.write(bridge_content)

        self.changes.append(f"Created neural bridge: {bridge_path}")
        print("✅ Created neuroplastic bridge for inter-module communication")

    def generate_report(self):
        """Generate consolidation report"""
        report = {
            "timestamp": self.timestamp,
            "connections_made": self.connections_made,
            "changes": self.changes,
            "module_summary": {},
        }

        # Count files per module
        for module, config in self.core_modules.items():
            module_path = Path(config["path"])
            if module_path.exists():
                py_files = list(module_path.rglob("*.py"))
                report["module_summary"][module] = {
                    "files": len(py_files),
                    "path": config["path"],
                    "description": config["description"],
                }

        return report


def main():
    print("🧠 LUKHAS Neuroplastic Consolidator")
    print("=" * 50)

    consolidator = NeuroplasticConsolidator()

    # Create module connectors
    print("\n📡 Creating neuroplastic connectors...")
    consolidator.create_module_connectors()

    # Create neural bridge
    print("\n🌉 Creating neural bridge...")
    consolidator.create_module_bridges()

    # Load isolated files
    print("\n🔗 Connecting isolated files...")
    report = consolidator.load_isolated_files()

    # Connect some high-priority isolated files
    priority_files = [
        "./orchestration/brain/cognitive/cognitive_updater.py",
        "./identity/auth/cognitive_sync_adapter.py",
        "./memory/systems/memory_trace.py",
    ]

    for filepath in priority_files:
        if os.path.exists(filepath):
            module = consolidator.categorize_file(filepath)
            print(f"  Connecting {Path(filepath).name} to {module}...")
            consolidator.connect_isolated_file(filepath, module)

    # Consolidate tools
    print("\n🔧 Consolidating tools...")
    consolidator.consolidate_tools()

    # Generate report
    report = consolidator.generate_report()

    print("\n✅ Consolidation Complete!")
    print(f"  - Connections made: {consolidator.connections_made}")
    print(f"  - Total changes: {len(consolidator.changes)}")

    print("\n📊 Module Summary:")
    for module, summary in report["module_summary"].items():
        print(f"  - {module}: {summary['files']} files")


if __name__ == "__main__":
    main()
