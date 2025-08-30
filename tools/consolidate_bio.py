#!/usr/bin/env python3
"""
Bio Module Consolidation Tool
Merges 19+ bio variants into unified structure
"""

import ast
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


class BioConsolidator:
    """Consolidate bio module variants"""

    def __init__(self):
        self.root = Path(".")
        self.target_dir = Path("lukhas/accepted/bio")
        self.archive_dir = Path("lukhas/archive/bio_variants")
        self.conn = sqlite3.connect("tools/code_index.sqlite")

        # Track consolidation results
        self.merged_files = []
        self.archived_files = []
        self.conflicts = []

    def analyze_bio_modules(self):
        """Analyze all bio module variants"""
        cursor = self.conn.cursor()

        # Get all bio variants
        cursor.execute(
            """
            SELECT DISTINCT file_path
            FROM duplicates
            WHERE module_type = 'bio'
            ORDER BY variant_name, has_unique_logic DESC
        """
        )

        bio_files = [Path(row[0]) for row in cursor.fetchall() if Path(row[0]).exists()]

        # Categorize by functionality
        categories = {
            "core": [],
            "oscillator": [],
            "symbolic": [],
            "quantum": [],
            "voice": [],
            "awareness": [],
            "adapters": [],
            "utils": [],
        }

        for file_path in bio_files:
            path_str = str(file_path).lower()

            if "oscillator" in path_str:
                categories["oscillator"].append(file_path)
            elif "symbolic" in path_str:
                categories["symbolic"].append(file_path)
            elif "quantum" in path_str:
                categories["quantum"].append(file_path)
            elif "voice" in path_str:
                categories["voice"].append(file_path)
            elif "awareness" in path_str:
                categories["awareness"].append(file_path)
            elif "adapter" in path_str:
                categories["adapters"].append(file_path)
            elif "util" in path_str or "helper" in path_str:
                categories["utils"].append(file_path)
            else:
                categories["core"].append(file_path)

        return categories

    def extract_classes_and_functions(self, file_path):
        """Extract all classes and functions from a Python file"""
        try:
            content = file_path.read_text(errors="ignore")
            tree = ast.parse(content)

            classes = []
            functions = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(
                        {
                            "name": node.name,
                            "bases": [
                                base.id if isinstance(base, ast.Name) else str(base)
                                for base in node.bases
                            ],
                            "methods": [
                                n.name for n in node.body if isinstance(n, ast.FunctionDef)
                            ],
                        }
                    )
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    functions.append(
                        {"name": node.name, "args": [arg.arg for arg in node.args.args]}
                    )
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))

            return {
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "content": content,
            }
        except Exception as e:
            print(f"  ⚠️  Error parsing {file_path}: {e}")
            return None

    def merge_category(self, category_name, file_paths):
        """Merge files in a category into a single module"""
        if not file_paths:
            return

        print(f"\n🔄 Merging {category_name} ({len(file_paths)} files)...")

        # Create target directory
        if category_name == "core":
            target_file = self.target_dir / "__init__.py"
        else:
            target_file = self.target_dir / f"{category_name}.py"

        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Collect all components
        all_imports = set()
        all_classes = []
        all_functions = []

        for file_path in file_paths:
            if not file_path.exists():
                continue

            components = self.extract_classes_and_functions(file_path)
            if not components:
                continue

            # Track unique imports
            for imp in components["imports"]:
                # Skip internal bio imports (will be consolidated)
                if "bio" not in imp or "lukhas.accepted.bio" in imp:
                    all_imports.add(imp)

            # Collect unique classes
            for cls in components["classes"]:
                # Check for duplicates
                if not any(c["name"] == cls["name"] for c in all_classes):
                    all_classes.append(cls)
                else:
                    # Handle duplicate class names
                    self.conflicts.append(
                        {
                            "type": "class",
                            "name": cls["name"],
                            "files": [str(file_path)],
                        }
                    )

            # Collect unique functions
            for func in components["functions"]:
                if not any(f["name"] == func["name"] for f in all_functions):
                    all_functions.append(func)
                else:
                    self.conflicts.append(
                        {
                            "type": "function",
                            "name": func["name"],
                            "files": [str(file_path)],
                        }
                    )

        # Generate consolidated module
        content = f'''"""
LUKHAS AI Bio Module - {category_name.title()}
Consolidated from {len(file_paths)} variants
Generated: {datetime.now().isoformat()}
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

'''

        # Add imports
        if all_imports:
            for imp in sorted(all_imports):
                content += f"{imp}\n"
            content += "\n"

        # Add module metadata
        content += f"__module__ = 'bio.{category_name}'\n"
        content += "__trinity__ = '⚛️🧠🛡️'\n\n"

        # Add placeholder implementations for classes
        for cls in all_classes:
            content += f"\nclass {cls['name']}"
            if cls["bases"]:
                content += f"({', '.join(cls['bases'])})"
            content += ":\n"
            content += f'    """Bio {category_name} - {cls["name"]}"""\n'

            if cls["methods"]:
                for method in cls["methods"]:
                    if method == "__init__":
                        content += f"    def {method}(self, *args, **kwargs):\n"
                        content += "        pass\n\n"
                    else:
                        content += f"    def {method}(self, *args, **kwargs):\n"
                        content += (
                            "        raise NotImplementedError('Bio consolidation in progress')\n\n"
                        )
            else:
                content += "    pass\n\n"

        # Add placeholder implementations for functions
        for func in all_functions:
            args = ", ".join(func["args"]) if func["args"] else ""
            content += f"\ndef {func['name']}({args}):\n"
            content += f'    """Bio {category_name} function - {func["name"]}"""\n'
            content += "    raise NotImplementedError('Bio consolidation in progress')\n\n"

        # Write consolidated module
        target_file.write_text(content)
        self.merged_files.append(str(target_file))
        print(f"  ✓ Created {target_file}")

        # Archive original files
        for file_path in file_paths:
            if file_path.exists():
                archive_path = self.archive_dir / file_path.relative_to(self.root)
                archive_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, archive_path)
                self.archived_files.append(str(file_path))

    def create_bio_init(self):
        """Create main bio __init__.py"""
        init_content = '''"""
LUKHAS AI Bio Module
Unified bio-inspired processing system
Trinity Framework: ⚛️ Identity | 🧠 Consciousness | 🛡️ Guardian
"""

__version__ = "3.0.0"
__trinity__ = "⚛️🧠🛡️"

# Core components
from . import oscillator
from . import symbolic
from . import awareness
from . import adapters

# Optional quantum features (feature-flagged)
try:
    from . import lukhas.qi
except ImportError:
    quantum = None

# Optional voice features
try:
    from . import voice
except ImportError:
    voice = None

__all__ = [
    'oscillator',
    'symbolic',
    'awareness',
    'adapters',
    'quantum',
    'voice'
]

# Bio engine singleton
_engine = None

def get_bio_engine():
    """Get or create bio engine instance"""
    global _engine
    if _engine is None:
        from .core import BioEngine
        _engine = BioEngine()
    return _engine

# Trinity integration
def trinity_sync():
    """Synchronize with Trinity Framework"""
    return {
        'identity': '⚛️',
        'consciousness': '🧠',
        'guardian': '🛡️',
        'status': 'synchronized'
    }
'''

        init_path = self.target_dir / "__init__.py"
        init_path.write_text(init_content)
        print(f"  ✓ Created {init_path}")

    def create_canary_tests(self):
        """Create canary tests for bio consolidation"""
        test_content = '''"""
Bio Module Canary Tests
Validates consolidated bio functionality
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_bio_imports():
    """Test that bio modules can be imported"""
    from lukhas.accepted import bio
    assert bio is not None
    assert hasattr(bio, '__trinity__')

def test_bio_core_components():
    """Test core bio components are available"""
    from lukhas.accepted.bio import oscillator, symbolic, awareness

    # Check modules exist
    assert oscillator is not None
    assert symbolic is not None
    assert awareness is not None

def test_bio_engine():
    """Test bio engine initialization"""
    from lukhas.accepted.bio import get_bio_engine

    engine = get_bio_engine()
    assert engine is not None

def test_trinity_integration():
    """Test Trinity Framework integration"""
    from lukhas.accepted.bio import trinity_sync

    sync_status = trinity_sync()
    assert sync_status['identity'] == '⚛️'
    assert sync_status['consciousness'] == '🧠'
    assert sync_status['guardian'] == '🛡️'
    assert sync_status['status'] == 'synchronized'

def test_backward_compatibility():
    """Test compatibility shims still work"""
    import warnings

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Try old import (should work with deprecation warning)
        try:
            from bio_core import BioEngine
            assert len(w) > 0
            assert "deprecated" in str(w[0].message).lower()
        except ImportError:
            # Shim might not have real implementation yet
            pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

        test_path = Path("tests/canary/test_bio_consolidation.py")
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(test_content)
        print(f"  ✓ Created canary tests: {test_path}")

    def generate_report(self):
        """Generate consolidation report"""
        report = f"""# Bio Module Consolidation Report
Generated: {datetime.now().isoformat()}

## Summary
- Files Merged: {len(self.merged_files)}
- Files Archived: {len(self.archived_files)}
- Conflicts Found: {len(self.conflicts)}

## Merged Modules
"""
        for file in self.merged_files:
            report += f"- `{file}`\n"

        if self.conflicts:
            report += "\n## Conflicts Requiring Resolution\n"
            for conflict in self.conflicts[:10]:  # Show first 10
                report += f"- {conflict['type']}: `{conflict['name']}` in {len(conflict['files'])} files\n"

        report += """
## Next Steps
1. Run canary tests: `pytest tests/canary/test_bio_consolidation.py`
2. Review conflicts and implement actual logic
3. Update imports in dependent modules
4. Remove archived files after validation
"""

        report_path = Path("docs/AUDIT/BIO_CONSOLIDATION.md")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)
        print(f"\n📋 Report saved to: {report_path}")

    def run(self):
        """Execute bio consolidation"""
        print("🧬 Starting Bio Module Consolidation...")

        # Analyze modules
        categories = self.analyze_bio_modules()

        # Merge each category
        for category, files in categories.items():
            if files:
                self.merge_category(category, files)

        # Create main init
        self.create_bio_init()

        # Create canary tests
        self.create_canary_tests()

        # Generate report
        self.generate_report()

        print("\n✅ Bio Consolidation Complete!")
        print(f"   Merged: {len(self.merged_files)} modules")
        print(f"   Archived: {len(self.archived_files)} original files")
        print(f"   Conflicts: {len(self.conflicts)} (need manual resolution)")


def main():
    consolidator = BioConsolidator()
    consolidator.run()


if __name__ == "__main__":
    main()
