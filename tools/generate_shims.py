#!/usr/bin/env python3
"""
Generate compatibility shims for LUKHAS AI migration
Creates backward-compatible imports with deprecation warnings
"""
import sqlite3
from datetime import datetime
from pathlib import Path

SHIM_TEMPLATE = '''"""
Compatibility shim for {old_module}
DEPRECATED: This module will be removed on {deprecation_date}
Please update imports to: {new_module}
"""

import warnings
from {new_module} import *

warnings.warn(
    "Import '{old_module}' is deprecated and will be removed on {deprecation_date}. "
    "Please update to '{new_module}'",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = dir()
'''


class ShimGenerator:
    """Generate compatibility shims for migration"""

    def __init__(self, db_path="tools/code_index.sqlite"):
        self.conn = sqlite3.connect(db_path)
        self.root = Path(".")
        self.shims_created = []

    def generate_shims(self):
        """Generate all compatibility shims"""
        cursor = self.conn.cursor()

        # Get all migration mappings that need shims
        cursor.execute(
            """
            SELECT old_import, new_import, deprecation_date
            FROM migrations
            WHERE shim_required = 1
        """
        )

        for old_import, new_import, deprecation_date in cursor.fetchall():
            self.create_shim(old_import, new_import, deprecation_date)

    def create_shim(self, old_module, new_module, deprecation_date):
        """Create a single compatibility shim"""
        # Convert module path to file path
        old_path = Path(old_module.replace(".", "/"))

        # Handle different import styles
        if old_path.suffix != ".py":
            old_path = old_path / "__init__.py"

        # Skip if shim already exists
        if old_path.exists():
            content = old_path.read_text()
            if "Compatibility shim" in content:
                print(f"  ✓ Shim already exists: {old_path}")
                return

        # Create shim content
        shim_content = SHIM_TEMPLATE.format(
            old_module=old_module,
            new_module=new_module,
            deprecation_date=deprecation_date,
        )

        # Create parent directories
        old_path.parent.mkdir(parents=True, exist_ok=True)

        # Write shim
        old_path.write_text(shim_content)
        self.shims_created.append(str(old_path))
        print(f"  ✓ Created shim: {old_path}")

    def create_bio_shims(self):
        """Create shims for bio module consolidation"""
        bio_shims = {
            "bio_core/__init__.py": "lukhas.accepted.bio",
            "bio_orchestrator/__init__.py": "lukhas.accepted.bio.orchestrator",
            "bio_symbolic/__init__.py": "lukhas.accepted.bio.symbolic",
            "bio_optimization_adapter/__init__.py": "lukhas.accepted.bio.optimizer",
            "bio_quantum_radar_integration/__init__.py": "lukhas.candidate.bio.quantum",
            "bio_core/bio_symbolic/__init__.py": "lukhas.accepted.bio.symbolic",
            "bio/bio_hub/__init__.py": "lukhas.accepted.bio.hub",
            "bio/bio_engine/__init__.py": "lukhas.accepted.bio.engine",
            "bio/bio_utilities/__init__.py": "lukhas.accepted.bio.utils",
        }

        for old_path, new_module in bio_shims.items():
            path = Path(old_path)
            if not path.exists() or not self.is_real_module(path):
                path.parent.mkdir(parents=True, exist_ok=True)
                shim_content = SHIM_TEMPLATE.format(
                    old_module=old_path.replace("/__init__.py", "").replace("/", "."),
                    new_module=new_module,
                    deprecation_date="2025-11-01",
                )
                path.write_text(shim_content)
                self.shims_created.append(str(path))
                print(f"  ✓ Created bio shim: {path}")

    def create_memory_shims(self):
        """Create shims for memory module consolidation"""
        memory_shims = {
            "memory/fold_manager.py": "lukhas.accepted.memory.fold",
            "memory/memory_consolidation.py": "lukhas.accepted.memory.consolidation",
            "memory/episodic.py": "lukhas.accepted.memory.episodic",
            "memory/causal.py": "lukhas.accepted.memory.causal",
            "memory/hippocampal.py": "lukhas.accepted.memory.hippocampal",
            "memory/compression.py": "lukhas.accepted.memory.compression",
            "memory/dna_helix.py": "lukhas.accepted.memory.helix",
            "memory/fold_system.py": "lukhas.accepted.memory.fold",
            "memory/colonies.py": "lukhas.accepted.memory.colonies",
        }

        for old_path, new_module in memory_shims.items():
            path = Path(old_path)
            if not path.exists() or not self.is_real_module(path):
                path.parent.mkdir(parents=True, exist_ok=True)
                module_name = path.stem
                shim_content = f'''"""
Compatibility shim for memory.{module_name}
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: {new_module}
"""

import warnings
try:
    from {new_module} import *
except ImportError:
    # Fallback for gradual migration
    pass

warnings.warn(
    "Import 'memory.{module_name}' is deprecated and will be removed on 2025-11-01. "
    "Please update to '{new_module}'",
    DeprecationWarning,
    stacklevel=2
)
'''
                path.write_text(shim_content)
                self.shims_created.append(str(path))
                print(f"  ✓ Created memory shim: {path}")

    def create_core_shims(self):
        """Create shims for core module migrations"""
        core_shims = {
            "core/glyph.py": "lukhas.accepted.core.glyph",
            "identity/core.py": "lukhas.accepted.identity",
            "governance/guardian.py": "lukhas.accepted.governance.guardian",
            "orchestration/brain.py": "lukhas.accepted.orchestrator.brain",
            "bridge/adapter.py": "lukhas.accepted.adapters.base",
        }

        for old_path, new_module in core_shims.items():
            path = Path(old_path)
            if not path.exists() or not self.is_real_module(path):
                path.parent.mkdir(parents=True, exist_ok=True)
                shim_content = SHIM_TEMPLATE.format(
                    old_module=old_path.replace(".py", "").replace("/", "."),
                    new_module=new_module,
                    deprecation_date="2025-11-01",
                )
                path.write_text(shim_content)
                self.shims_created.append(str(path))
                print(f"  ✓ Created core shim: {path}")

    def create_candidate_shims(self):
        """Create shims for candidate modules"""
        candidate_shims = {
            "universal_language/__init__.py": "lukhas.candidate.ul",
            "vivox/__init__.py": "lukhas.candidate.vivox",
            "qim/__init__.py": "lukhas.candidate.qim",
        }

        for old_path, new_module in candidate_shims.items():
            path = Path(old_path)
            if path.exists() and self.is_real_module(path):
                # Don't overwrite real modules, just note them
                print(f"  ⚠️  Real module exists, skipping: {path}")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                shim_content = f'''"""
Compatibility shim for {old_path.replace("/__init__.py", "")}
DEPRECATED: This module will be removed on 2025-11-01
Please update imports to: {new_module}

NOTE: This is a candidate module. Enable with feature flag:
  {new_module.split(".")[-1].upper()}_ENABLED=true
"""

import os
import warnings

warnings.warn(
    "Import '{old_path.replace("/__init__.py", "").replace("/", ".")}' is deprecated. "
    "Please update to '{new_module}' and enable feature flag",
    DeprecationWarning,
    stacklevel=2
)

# Check if feature flag is enabled
flag_name = "{new_module.split(".")[-1].upper()}_ENABLED"
if os.getenv(flag_name, "false").lower() == "true":
    try:
        from {new_module} import *
    except ImportError:
        pass
'''
                path.write_text(shim_content)
                self.shims_created.append(str(path))
                print(f"  ✓ Created candidate shim: {path}")

    def is_real_module(self, path):
        """Check if path contains real module code (not just shim)"""
        if not path.exists():
            return False

        content = path.read_text(errors="ignore")

        # Check if it's already a shim
        if "Compatibility shim" in content:
            return False

        # Check for real code indicators
        real_code_indicators = [
            "class ",
            "def ",
            "async def",
            "import ",
            "from ",
        ]

        return any(indicator in content and len(content) > 100 for indicator in real_code_indicators)

    def report(self):
        """Generate shim report"""
        print("\n📋 Shim Generation Complete!")
        print(f"   Created {len(self.shims_created)} compatibility shims")
        print("   Deprecation date: 2025-11-01")
        print("\n   Shims will provide backward compatibility during migration")

        # Save shim list
        shim_list_path = Path("docs/AUDIT/SHIMS.md")
        shim_list_path.parent.mkdir(parents=True, exist_ok=True)

        content = f"""# LUKHAS AI Compatibility Shims
Generated: {datetime.now().isoformat()}

## Active Shims ({len(self.shims_created)})

These files provide backward compatibility during migration:

"""
        for shim in sorted(self.shims_created):
            content += f"- `{shim}`\n"

        content += """
## Deprecation Schedule

All shims will be removed on **2025-11-01**

## Usage

Old imports will continue working but show deprecation warnings:

```python
# Old import (shows warning)
from bio_core import BioEngine

# New import (recommended)
from lukhas.accepted.bio import BioEngine
```

## Testing

Run tests with deprecation warnings visible:
```bash
python -W default::DeprecationWarning -m pytest
```
"""

        shim_list_path.write_text(content)
        print(f"   Report saved to: {shim_list_path}")

    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    """Main entry point"""
    generator = ShimGenerator()

    try:
        print("🔄 Generating compatibility shims...")

        # Generate shims from database
        generator.generate_shims()

        # Generate specific module shims
        print("\n📦 Creating Bio module shims...")
        generator.create_bio_shims()

        print("\n🧠 Creating Memory module shims...")
        generator.create_memory_shims()

        print("\n⚙️ Creating Core module shims...")
        generator.create_core_shims()

        print("\n🔬 Creating Candidate module shims...")
        generator.create_candidate_shims()

        # Generate report
        generator.report()

    finally:
        generator.close()


if __name__ == "__main__":
    main()
