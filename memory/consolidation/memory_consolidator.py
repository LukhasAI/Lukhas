#!/usr/bin/env python3
"""
CRITICAL: Memory System Consolidation Script
Status: Active
Version: 1.0.0
Last Modified: 2025-06-20
Description: Consolidates memory system components and applies proper tagging.
Purpose: Helps organize and standardize the LUKHAS memory system.

This script helps consolidate and organize the memory system components.
Tags: memory, organization, consolidation, critical
"""

import os
import shutil
from pathlib import Path
from core.common import get_logger
from typing import Dict, List, Set
import json
import re

logger = logging.getLogger("memory_consolidation")

class MemorySystemConsolidator:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.core_memory_path = self.root_path / "core" / "memory"
        self.brain_memory_path = self.root_path / "brain" / "memory"

        # Critical files that need to be properly tagged and organized
        self.critical_files = {
            "memory_manager.py": {
                "path": self.core_memory_path,
                "tags": ["memory", "core", "critical", "identity", "security"],
                "dependencies": [
                    "memory_folds.py",
                    "trauma_lock.py",
                    "identity_legacy.py",
                    "memory_identity.py",
                    "dream_reflection_loop.py"
                ]
            },
            "memory_folds.py": {
                "path": self.core_memory_path,
                "tags": ["memory", "core", "critical", "patterns", "fold-engine"],
                "dependencies": [
                    "numpy",
                    "chromadb",
                    "redis"
                ]
            },
            "trauma_lock.py": {
                "path": self.core_memory_path,
                "tags": ["memory", "core", "critical", "security", "trauma"],
                "dependencies": [
                    "memory_folds.py",
                    "identity_legacy.py"
                ]
            },
            "pattern_engine.py": {
                "path": self.core_memory_path,
                "tags": ["memory", "core", "critical", "patterns", "neural"],
                "dependencies": [
                    "memory_folds.py",
                    "numpy",
                    "tensorflow"
                ]
            }
        }

    def consolidate(self):
        """Consolidate memory system files into proper structure."""
        logger.info("Starting memory system consolidation...")

        # Create necessary directories
        self.core_memory_path.mkdir(parents=True, exist_ok=True)

        # Move and consolidate files
        self._consolidate_memory_files()

        # Apply proper tagging
        self._tag_critical_files()

        logger.info("Memory system consolidation complete.")

    def _consolidate_memory_files(self):
        """Move and consolidate memory files to proper locations."""
        # Check for FoldEngine.py in brain/memory
        fold_engine = self.brain_memory_path / "FoldEngine.py"
        if fold_engine.exists():
            # Merge with existing memory_folds.py if it exists
            memory_folds = self.core_memory_path / "memory_folds.py"
            if memory_folds.exists():
                self._merge_implementations(fold_engine, memory_folds)
            else:
                # Move and rename
                shutil.move(str(fold_engine), str(memory_folds))

    def _merge_implementations(self, source: Path, target: Path):
        """Merge two implementations, keeping the best parts of each."""
        with open(source, 'r') as f:
            source_content = f.read()
        with open(target, 'r') as f:
            target_content = f.read()

        # TODO: Implement smart merging logic
        # For now, we'll keep this as a placeholder
        logger.info(f"Would merge {source} into {target}")

    def _tag_critical_files(self):
        """Apply proper tagging to all critical files."""
        logger.info("Applying tags to critical files...")

        header_template = '''"""
CRITICAL: {name}
Status: Active
Version: 1.0.0
Last Modified: 2025-06-20
Dependencies: {dependencies}
Description: {description}
Purpose: {purpose}

This is a critical system component that {role}
Tags: {tags}

Copyright (c) 2025 LUKHAS AGI Research. All rights reserved.
Licensed under the LUKHAS Core License - see LICENSE.md for details.
"""
'''

        for filename, info in self.critical_files.items():
            filepath = info["path"] / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    content = f.read()

                # Remove existing docstring if present
                content = re.sub(r'"""[\s\S]*?"""', '', content, count=1)

                # Add new header
                header = header_template.format(
                    name=filename.replace('.py', ' ').replace('_', ' ').title(),
                    dependencies=", ".join(info["dependencies"]),
                    description=f"Core component of the LUKHAS memory system",
                    purpose="Provides critical memory system functionality",
                    role="manages core memory operations" if "manager" in filename else "provides essential memory functionality",
                    tags=", ".join(info["tags"])
                )

                with open(filepath, 'w') as f:
                    f.write(header + content)

                logger.info(f"Tagged {filename}")

def main():
    logging.basicConfig(level=logging.INFO)
    consolidator = MemorySystemConsolidator("/Users/A_G_I/Lukhas")
    consolidator.consolidate()

if __name__ == "__main__":
    main()
