#!/usr/bin/env python3
"""
Fix inaccurate AGI->Cognitive document changes.

This script corrects specific instances where the mass migration was too broad,
particularly in documentation about AGI evolution and technical contexts.
"""

import os
import re
from pathlib import Path


class AGICognitiveAccuracyFixer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.corrections = [
            # Fix "traditional AGI to Superior Consciousness" back to "traditional AGI to Superior Consciousness"
            (r'traditional Cognitive AI to \*\*Superior Consciousness', 'traditional AGI to **Superior Consciousness'),
            (r'traditional AGI to Superior Consciousness', 'traditional AGI to Superior Consciousness'),

            # Fix references to "Cognitive AI Evolution" in technical contexts
            (r'AGI Evolution Specialist', 'AGI Evolution Specialist'),

            # Fix technical module descriptions
            (r'all AGI subsystems', 'all AGI subsystems'),

            # Fix historical/comparative references
            (r'from conventional AGI', 'from conventional AGI'),
            (r'beyond traditional AGI', 'beyond traditional AGI'),

            # Fix research terminology
            (r'AGI research', 'AGI research'),
            (r'in AGI development', 'in AGI development'),
        ]

        self.stats = {
            'files_processed': 0,
            'files_changed': 0,
            'total_corrections': 0
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed."""
        if not file_path.exists() or not file_path.is_file():
            return False

        # Focus on documentation and key module files
        if file_path.suffix in ['.md', '.py', '.json']:
            # Skip certain directories
            skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules'}
            return not any(part in skip_dirs for part in file_path.parts)

        return False

    def fix_file_content(self, content: str) -> tuple[str, int]:
        """Apply corrections to file content."""
        corrections_made = 0

        for pattern, replacement in self.corrections:
            new_content, count = re.subn(pattern, replacement, content)
            if count > 0:
                content = new_content
                corrections_made += count
                print(f"    ✓ Applied {count} correction(s): {pattern[:40]}...")

        return content, corrections_made

    def process_file(self, file_path: Path) -> bool:
        """Process a single file."""
        try:
            with open(file_path, encoding='utf-8') as f:
                original_content = f.read()

            new_content, corrections_made = self.fix_file_content(original_content)

            if corrections_made > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print(f"📝 {file_path.relative_to(self.root_path)}")
                self.stats['files_changed'] += 1
                self.stats['total_corrections'] += corrections_made
                return True

            return False

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return False

    def run(self) -> None:
        """Run the accuracy fixing process."""
        print("🔧 Starting AGI->Cognitive accuracy fixes...")
        print(f"📁 Root path: {self.root_path}")

        # Find all files to process
        files_to_process = []
        for root, _dirs, files in os.walk(self.root_path):
            for file in files:
                file_path = Path(root) / file
                if self.should_process_file(file_path):
                    files_to_process.append(file_path)

        print(f"📄 Found {len(files_to_process)} files to check")

        # Process files
        for file_path in files_to_process:
            self.stats['files_processed'] += 1
            self.process_file(file_path)

        # Report results
        print("\n✅ Accuracy fixes completed!")
        print(f"📊 Files processed: {self.stats['files_processed']}")
        print(f"📝 Files changed: {self.stats['files_changed']}")
        print(f"🔧 Total corrections: {self.stats['total_corrections']}")

if __name__ == "__main__":
    fixer = AGICognitiveAccuracyFixer()
    fixer.run()
