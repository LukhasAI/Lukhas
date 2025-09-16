import logging

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
import re
import shutil
from pathlib import Path

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
                    "dream_reflection_loop.py",
                ],
            },
            "memory_folds.py": {
                "path": self.core_memory_path,
                "tags": ["memory", "core", "critical", "patterns", "fold-engine"],
                "dependencies": ["numpy", "chromadb", "redis"],
            },
            "trauma_lock.py": {
                "path": self.core_memory_path,
                "tags": ["memory", "core", "critical", "security", "trauma"],
                "dependencies": ["memory_folds.py", "identity_legacy.py"],
            },
            "pattern_engine.py": {
                "path": self.core_memory_path,
                "tags": ["memory", "core", "critical", "patterns", "neural"],
                "dependencies": ["memory_folds.py", "numpy", "tensorflow"],
            },
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
        with open(source) as f:
            f.read()
        with open(target) as f:
            f.read()

        # Smart merging logic for memory implementations
        try:
            # Read source content
            with open(source, 'r', encoding='utf-8') as f:
                source_content = f.read()

            # Read target content
            with open(target, 'r', encoding='utf-8') as f:
                target_content = f.read()

            # Extract classes and functions from source
            source_classes = self._extract_classes(source_content)
            source_functions = self._extract_functions(source_content)

            # Merge unique components
            merged_content = target_content

            # Add missing classes from source
            for class_name, class_code in source_classes.items():
                if class_name not in target_content:
                    merged_content += f"\n\n{class_code}"
                    logger.info(f"Added class {class_name} from {source}")

            # Add missing functions from source
            for func_name, func_code in source_functions.items():
                if func_name not in target_content:
                    merged_content += f"\n\n{func_code}"
                    logger.info(f"Added function {func_name} from {source}")

            # Write merged content back to target
            with open(target, 'w', encoding='utf-8') as f:
                f.write(merged_content)

            logger.info(f"Successfully merged {source} into {target}")

        except Exception as e:
            logger.error(f"Failed to merge {source} into {target}: {e}")
            # Fallback: keep original target file
            logger.info(f"Keeping original {target} file due to merge error")

    def _extract_classes(self, content: str) -> dict:
        """Extract class definitions from Python content."""
        classes = {}
        class_pattern = r'^class\s+(\w+).*?(?=^class\s|\n^def\s|\Z)'
        matches = re.finditer(class_pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            class_name = match.group(1)
            class_code = match.group(0)
            classes[class_name] = class_code

        return classes

    def _extract_functions(self, content: str) -> dict:
        """Extract function definitions from Python content."""
        functions = {}
        # Match top-level functions (not inside classes)
        func_pattern = r'^def\s+(\w+).*?(?=^def\s|^class\s|\Z)'
        matches = re.finditer(func_pattern, content, re.MULTILINE | re.DOTALL)

        for match in matches:
            func_name = match.group(1)
            func_code = match.group(0)
            functions[func_name] = func_code

        return functions

    def _tag_critical_files(self):
        """Apply proper tagging to all critical files."""
        logger.info("Applying tags to critical files...")

        for filename, file_info in self.critical_files.items():
            file_path = file_info["path"] / filename

            if file_path.exists():
                self._apply_tags_to_file(file_path, file_info["tags"])
            else:
                logger.warning(f"Critical file not found: {file_path}")

    def _apply_tags_to_file(self, file_path: Path, tags: list):
        """Apply proper tags to a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if tags already exist
            if '#TAG:' in content:
                logger.info(f"Tags already exist in {file_path}")
                return

            # Create tag header
            tag_header = '\n'.join([f'#TAG:{tag}' for tag in tags])

            # Insert tags after docstring or at beginning
            if '"""' in content:
                # Find end of first docstring
                parts = content.split('"""', 2)
                if len(parts) >= 3:
                    new_content = f'{parts[0]}"""{parts[1]}"""\n\n{tag_header}\n{parts[2]}'
                else:
                    new_content = f'{tag_header}\n\n{content}'
            else:
                new_content = f'{tag_header}\n\n{content}'

            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"Applied tags to {file_path}: {', '.join(tags)}")

        except Exception as e:
            logger.error(f"Failed to apply tags to {file_path}: {e}")

    def validate_memory_system(self) -> dict:
        """Validate the consolidated memory system."""
        validation_results = {
            'critical_files_found': 0,
            'missing_files': [],
            'properly_tagged': 0,
            'dependency_issues': [],
            'status': 'unknown'
        }

        # Check critical files
        for filename, file_info in self.critical_files.items():
            file_path = file_info["path"] / filename

            if file_path.exists():
                validation_results['critical_files_found'] += 1

                # Check if properly tagged
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if '#TAG:' in content:
                    validation_results['properly_tagged'] += 1
            else:
                validation_results['missing_files'].append(str(file_path))

        # Determine overall status
        total_critical = len(self.critical_files)
        if validation_results['critical_files_found'] == total_critical:
            if validation_results['properly_tagged'] == total_critical:
                validation_results['status'] = 'excellent'
            else:
                validation_results['status'] = 'good'
        elif validation_results['critical_files_found'] > total_critical * 0.7:
            validation_results['status'] = 'acceptable'
        else:
            validation_results['status'] = 'critical_issues'

        return validation_results

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
                with open(filepath) as f:
                    content = f.read()

                # Remove existing docstring if present
                content = re.sub(r'"""[\s\S]*?"""', "", content, count=1)

                # Add new header
                header = header_template.format(
                    name=filename.replace(".py", " ").replace("_", " ").title(),
                    dependencies=", ".join(info["dependencies"]),
                    description="Core component of the LUKHAS memory system",
                    purpose="Provides critical memory system functionality",
                    role=(
                        "manages core memory operations"
                        if "manager" in filename
                        else "provides essential memory functionality"
                    ),
                    tags=", ".join(info["tags"]),
                )

                with open(filepath, "w") as f:
                    f.write(header + content)

                logger.info(f"Tagged {filename}")


def main():
    logging.basicConfig(level=logging.INFO)
    consolidator = MemorySystemConsolidator("/Users/A_G_I/Lukhas")
    consolidator.consolidate()


if __name__ == "__main__":
    main()
