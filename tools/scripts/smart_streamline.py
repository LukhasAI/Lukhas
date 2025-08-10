#!/usr/bin/env python3
"""
PWM Smart Streamline
====================
Post-modularization streamlining that preserves connectivity and functionality.
"""

import ast
import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class SmartStreamline:
    """Smart streamlining that preserves modularization work"""

    def __init__(self):
        self.root_path = Path("/Users/agi_dev/Lukhas_PWM")
        self.connectivity_map = defaultdict(set)
        self.import_fixes = []
        self.consolidations = []

    def analyze_connectivity(self):
        """Analyze module connectivity post-modularization"""
        logger.info("🔗 Analyzing module connectivity...")

        # Key modules that should be interconnected
        core_modules = {
            "core": ["common", "glyph", "symbolic", "orchestration"],
            "consciousness": ["unified", "dream", "reflection", "interfaces"],
            "memory": ["folds", "systems", "core"],
            "orchestration": ["brain", "monitoring", "agents"],
            "governance": ["guardian", "ethics", "policies"],
            "vivox": ["consciousness", "memory_expansion", "integration"],
        }

        for module, submodules in core_modules.items():
            module_path = self.root_path / module
            if not module_path.exists():
                continue

            logger.info(f"\n📦 Checking {module} connectivity...")

            # Check inter-module imports
            for submodule in submodules:
                submodule_path = module_path / submodule
                if submodule_path.exists():
                    self._check_submodule_connectivity(module, submodule)

    def _check_submodule_connectivity(self, module: str, submodule: str):
        """Check connectivity within a submodule"""
        submodule_path = self.root_path / module / submodule

        for py_file in submodule_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                relative_path = py_file.relative_to(self.root_path)

                # Find imports that need fixing
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.level == 0:  # Absolute import
                            # Check if import is valid
                            module_parts = node.module.split(".")
                            if module_parts[0] in [
                                "core",
                                "consciousness",
                                "memory",
                                "orchestration",
                            ]:
                                # This is a cross-module import - verify it exists
                                target_path = self.root_path / "/".join(module_parts)
                                if (
                                    not target_path.exists()
                                    and not (target_path.with_suffix(".py")).exists()
                                ):
                                    self.import_fixes.append(
                                        {
                                            "file": str(relative_path),
                                            "line": node.lineno,
                                            "import": node.module,
                                            "issue": "Module not found",
                                            "suggested_fix": self._suggest_import_fix(
                                                node.module
                                            ),
                                        }
                                    )

            except Exception:
                pass

    def _suggest_import_fix(self, import_module: str) -> str:
        """Suggest a fix for broken import"""
        parts = import_module.split(".")

        # Common import mappings post-modularization
        mappings = {
            "core.interfaces": "core.common.interfaces",
            "core.base": "core.common.base",
            "consciousness.base": "consciousness.unified.base",
            "memory.base": "memory.core.base",
            "orchestration.base": "orchestration.brain.base",
        }

        # Check if we have a direct mapping
        for old_path, new_path in mappings.items():
            if import_module.startswith(old_path):
                return import_module.replace(old_path, new_path)

        # Try to find the module
        search_name = parts[-1] + ".py"
        for py_file in self.root_path.rglob(search_name):
            relative = py_file.relative_to(self.root_path)
            module_path = str(relative.with_suffix("")).replace("/", ".")
            if module_path.endswith("." + parts[-1]):
                return module_path

        return import_module  # Return original if no fix found

    def consolidate_duplicate_utilities(self):
        """Consolidate duplicate utility functions while preserving functionality"""
        logger.info("\n🔧 Consolidating duplicate utilities...")

        # Focus on safe consolidations
        safe_consolidations = {
            "get_logger": {
                "target": "lukhas.common.utils",
                "preserve_local": True,  # Keep local versions that might have custom config
            },
            "load_config": {"target": "lukhas.common.utils", "preserve_local": False},
            "SingletonMeta": {
                "target": "lukhas.common.patterns",
                "preserve_local": False,
            },
        }

        for func_name, config in safe_consolidations.items():
            occurrences = self._find_function_occurrences(func_name)

            if len(occurrences) > 3:  # Only consolidate if many duplicates
                self.consolidations.append(
                    {
                        "function": func_name,
                        "occurrences": len(occurrences),
                        "target_module": config["target"],
                        "preserve_local": config["preserve_local"],
                        "files": [str(o["file"]) for o in occurrences[:5]],  # Sample
                    }
                )

    def _find_function_occurrences(self, func_name: str) -> list[dict]:
        """Find occurrences of a function"""
        occurrences = []

        for py_file in self.root_path.rglob("*.py"):
            if "archive" in str(py_file) or "__pycache__" in str(py_file):
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                if f"def {func_name}" in content:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef) and node.name == func_name:
                            occurrences.append(
                                {
                                    "file": py_file.relative_to(self.root_path),
                                    "line": node.lineno,
                                }
                            )

            except Exception:
                pass

        return occurrences

    def create_import_fixer_script(self):
        """Create a script to fix imports based on analysis"""
        logger.info("\n📝 Creating import fixer script...")

        fixer_content = '''#!/usr/bin/env python3
"""
Import Connectivity Fixer
========================
Fixes import issues post-modularization.
"""

import os
import re
from pathlib import Path

# Import mappings discovered during analysis
IMPORT_MAPPINGS = {
'''

        # Add discovered mappings
        seen_mappings = set()
        for fix in self.import_fixes[:50]:  # Limit to first 50
            if fix["suggested_fix"] != fix["import"]:
                mapping = f"    '{fix['import']}': '{fix['suggested_fix']}'"
                if mapping not in seen_mappings:
                    fixer_content += mapping + ",\n"
                    seen_mappings.add(mapping)

        fixer_content += '''}

def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply import mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            # Handle various import patterns
            patterns = [
                (f'from {old_import} import', f'from {new_import} import'),
                (f'import {old_import}', f'import {new_import}'),
            ]

            for old_pattern, new_pattern in patterns:
                content = content.replace(old_pattern, new_pattern)

        # Save if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return False

def main():
    """Fix imports across the codebase"""
    root = Path("/Users/agi_dev/Lukhas_PWM")
    fixed_count = 0

    print("🔧 Fixing imports post-modularization...")

    for py_file in root.rglob("*.py"):
        if 'archive' in str(py_file) or '__pycache__' in str(py_file):
            continue

        if fix_imports_in_file(py_file):
            print(f"   Fixed: {py_file.relative_to(root)}")
            fixed_count += 1

    print(f"\\n✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
'''

        fixer_path = (
            self.root_path / "tools" / "scripts" / "fix_post_modularization_imports.py"
        )
        with open(fixer_path, "w") as f:
            f.write(fixer_content)

        os.chmod(fixer_path, 0o755)
        logger.info(f"   Created: {fixer_path}")

    def create_connectivity_enhancer(self):
        """Create module to enhance cross-module connectivity"""
        logger.info("\n🌉 Creating connectivity enhancer...")

        enhancer_content = '''"""
Module Connectivity Enhancer
===========================
Enhances connectivity between LUKHAS modules post-modularization.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import importlib
import logging

class ModuleConnector:
    """Facilitates cross-module communication"""

    def __init__(self):
        self.module_registry = {}
        self.logger = logging.getLogger(__name__)
        self._register_core_modules()

    def _register_core_modules(self):
        """Register core LUKHAS modules"""
        core_modules = {
            'core': ['core.common', 'core.glyph', 'core.symbolic'],
            'consciousness': ['consciousness.unified', 'consciousness.dream'],
            'memory': ['memory.core', 'memory.folds'],
            'orchestration': ['orchestration.brain', 'orchestration.agents'],
            'governance': ['governance.guardian', 'governance.ethics'],
            'vivox': ['vivox.consciousness', 'vivox.integration']
        }

        for category, modules in core_modules.items():
            for module_name in modules:
                try:
                    module = importlib.import_module(module_name)
                    self.module_registry[module_name] = module
                    self.logger.info(f"Registered module: {module_name}")
                except ImportError as e:
                    self.logger.warning(f"Could not import {module_name}: {e}")

    def get_module(self, module_name: str) -> Optional[Any]:
        """Get a registered module"""
        return self.module_registry.get(module_name)

    def connect_modules(self, source: str, target: str) -> bool:
        """Establish connection between modules"""
        source_module = self.get_module(source)
        target_module = self.get_module(target)

        if source_module and target_module:
            # Establish bidirectional awareness
            if hasattr(source_module, '_connected_modules'):
                source_module._connected_modules.add(target)
            else:
                source_module._connected_modules = {target}

            if hasattr(target_module, '_connected_modules'):
                target_module._connected_modules.add(source)
            else:
                target_module._connected_modules = {source}

            self.logger.info(f"Connected {source} <-> {target}")
            return True

        return False

# Global connector instance
connector = ModuleConnector()

def enhance_import(module_name: str) -> Optional[Any]:
    """Enhanced import that uses the module registry"""
    # Try normal import first
    try:
        return importlib.import_module(module_name)
    except ImportError:
        # Fall back to connector
        module = connector.get_module(module_name)
        if module:
            return module

        # Try alternative paths
        alternatives = {
            'core.base': 'core.common.base',
            'consciousness.base': 'consciousness.unified.base',
            'memory.base': 'memory.core.base'
        }

        if module_name in alternatives:
            try:
                return importlib.import_module(alternatives[module_name])
            except ImportError:
                pass

        raise ImportError(f"Cannot import {module_name}")
'''

        enhancer_path = self.root_path / "lukhas" / "common" / "connectivity.py"
        enhancer_path.parent.mkdir(parents=True, exist_ok=True)

        with open(enhancer_path, "w") as f:
            f.write(enhancer_content)

        logger.info(f"   Created: {enhancer_path}")

    def generate_report(self) -> dict[str, Any]:
        """Generate analysis report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "import_issues": len(self.import_fixes),
            "suggested_consolidations": len(self.consolidations),
            "import_fixes": self.import_fixes[:20],  # Top 20
            "consolidations": self.consolidations,
            "recommendations": self._generate_recommendations(),
        }

        # Save report
        report_path = (
            self.root_path / "docs" / "reports" / "smart_streamline_report.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def _generate_recommendations(self) -> list[dict[str, str]]:
        """Generate smart recommendations"""
        recommendations = []

        if self.import_fixes:
            recommendations.append(
                {
                    "priority": "HIGH",
                    "action": "Fix broken imports",
                    "description": f"Fix {len(self.import_fixes)} import issues post-modularization",
                    "impact": "Restore module connectivity",
                    "command": "python3 tools/scripts/fix_post_modularization_imports.py",
                }
            )

        if self.consolidations:
            recommendations.append(
                {
                    "priority": "MEDIUM",
                    "action": "Consolidate common utilities",
                    "description": "Create shared utility modules for common functions",
                    "impact": "Reduce duplication without breaking functionality",
                    "note": "Preserves local customizations where needed",
                }
            )

        recommendations.append(
            {
                "priority": "MEDIUM",
                "action": "Enhance module connectivity",
                "description": "Use the ModuleConnector for better cross-module communication",
                "impact": "Improved module discovery and fallback imports",
            }
        )

        recommendations.append(
            {
                "priority": "LOW",
                "action": "Document module interfaces",
                "description": "Create clear documentation for module boundaries",
                "impact": "Easier maintenance and development",
            }
        )

        return recommendations

    def run(self):
        """Run smart streamline analysis"""
        logger.info("🧠 Smart Streamline Analysis (Post-Modularization)")
        logger.info("=" * 80)
        logger.info("Focus: Preserving and enhancing module connectivity\n")

        # Analyze connectivity
        self.analyze_connectivity()

        # Find safe consolidations
        self.consolidate_duplicate_utilities()

        # Create helper scripts
        self.create_import_fixer_script()
        self.create_connectivity_enhancer()

        # Generate report
        report = self.generate_report()

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 SMART STREAMLINE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Import issues found: {len(self.import_fixes)}")
        logger.info(f"Safe consolidations identified: {len(self.consolidations)}")

        if self.import_fixes:
            logger.info("\n🔧 Sample import fixes needed:")
            for fix in self.import_fixes[:5]:
                logger.info(
                    f"   {fix['file']}: {fix['import']} → {fix['suggested_fix']}"
                )

        if report["recommendations"]:
            logger.info("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                logger.info(f"\n   [{rec['priority']}] {rec['action']}")
                logger.info(f"   {rec['description']}")
                if "command" in rec:
                    logger.info(f"   Run: {rec['command']}")

        logger.info("\n📁 Full report: docs/reports/smart_streamline_report.json")
        logger.info("=" * 80)


def main():
    """Run smart streamline analysis"""
    analyzer = SmartStreamline()
    analyzer.run()


if __name__ == "__main__":
    main()
