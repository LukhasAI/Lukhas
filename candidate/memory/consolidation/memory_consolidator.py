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
        try:
            # Read source and target files
            with open(source, 'r', encoding='utf-8') as f:
                source_content = f.read()
            with open(target, 'r', encoding='utf-8') as f:
                target_content = f.read()

            # Implement smart merging logic
            merged_content = self._smart_merge_content(source_content, target_content, source, target)

            # Create backup before merging
            backup_path = target.with_suffix(f"{target.suffix}.backup")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(target_content)

            # Write merged content
            with open(target, 'w', encoding='utf-8') as f:
                f.write(merged_content)

            logger.info(f"Successfully merged {source} into {target} (backup: {backup_path})")

        except Exception as e:
            logger.error(f"Failed to merge {source} into {target}: {e}")

    def _smart_merge_content(self, source_content: str, target_content: str, source_path: Path, target_path: Path) -> str:
        """Perform intelligent content merging based on code analysis."""
        import ast
        import re

        # Extract metadata for merging decisions
        source_meta = self._extract_content_metadata(source_content, source_path)
        target_meta = self._extract_content_metadata(target_content, target_path)

        # Determine merge strategy based on content type
        if source_path.suffix == '.py' and target_path.suffix == '.py':
            return self._merge_python_files(source_content, target_content, source_meta, target_meta)
        elif source_path.suffix in ['.md', '.txt']:
            return self._merge_text_files(source_content, target_content, source_meta, target_meta)
        elif source_path.suffix == '.json':
            return self._merge_json_files(source_content, target_content)
        else:
            return self._merge_generic_files(source_content, target_content, source_meta, target_meta)

    def _extract_content_metadata(self, content: str, file_path: Path) -> dict:
        """Extract metadata from file content for merging decisions."""
        metadata = {
            "line_count": len(content.splitlines()),
            "imports": [],
            "classes": [],
            "functions": [],
            "docstrings": [],
            "todos": [],
            "lambda_annotations": [],
            "modification_markers": []
        }

        lines = content.splitlines()

        for i, line in enumerate(lines):
            # Extract imports
            if line.strip().startswith(('import ', 'from ')):
                metadata["imports"].append((i + 1, line.strip()))

            # Extract class definitions
            if line.strip().startswith('class '):
                metadata["classes"].append((i + 1, line.strip()))

            # Extract function definitions
            if line.strip().startswith('def '):
                metadata["functions"].append((i + 1, line.strip()))

            # Extract docstrings
            if '"""' in line or "'''" in line:
                metadata["docstrings"].append((i + 1, line.strip()))

            # Extract TODOs
            if 'TODO' in line.upper():
                metadata["todos"].append((i + 1, line.strip()))

            # Extract LAMBDA annotations
            if any(marker in line for marker in ['ΛTRACE', 'ΛNOTE', 'ΛEXPOSE', 'ΛSEED']):
                metadata["lambda_annotations"].append((i + 1, line.strip()))

        return metadata

    def _merge_python_files(self, source_content: str, target_content: str, source_meta: dict, target_meta: dict) -> str:
        """Merge Python files intelligently."""
        # Prioritize newer implementations and preserve LAMBDA annotations
        target_lines = target_content.splitlines()
        source_lines = source_content.splitlines()

        # Keep target structure but merge in valuable source content
        merged_lines = target_lines.copy()

        # Add missing imports from source
        source_imports = {imp[1] for imp in source_meta["imports"]}
        target_imports = {imp[1] for imp in target_meta["imports"]}
        missing_imports = source_imports - target_imports

        if missing_imports:
            # Find insertion point for imports (after existing imports)
            import_insert_line = 0
            for i, line in enumerate(target_lines):
                if line.strip().startswith(('import ', 'from ')):
                    import_insert_line = i + 1

            for imp in sorted(missing_imports):
                merged_lines.insert(import_insert_line, imp)
                import_insert_line += 1

        # Preserve LAMBDA annotations from source
        for line_num, annotation in source_meta["lambda_annotations"]:
            if not any(annotation in target_line for target_line in target_lines):
                # Add as comment near relevant function/class
                merged_lines.append(f"# {annotation}")

        # Add merge header
        merge_header = f"""# MERGED: Content from {source_meta.get('file_path', 'source')}
# Merge timestamp: {datetime.now(timezone.utc).isoformat()}
# Source functions: {len(source_meta['functions'])}, Target functions: {len(target_meta['functions'])}
"""
        merged_lines.insert(0, merge_header)

        return '\n'.join(merged_lines)

    def _merge_text_files(self, source_content: str, target_content: str, source_meta: dict, target_meta: dict) -> str:
        """Merge text/markdown files."""
        # Simple append strategy for text files with deduplication
        target_sections = set(line.strip() for line in target_content.splitlines() if line.strip())
        source_sections = set(line.strip() for line in source_content.splitlines() if line.strip())

        unique_source_content = source_sections - target_sections

        if unique_source_content:
            merged_content = target_content + "\n\n# MERGED CONTENT\n"
            merged_content += "\n".join(sorted(unique_source_content))
            return merged_content

        return target_content

    def _merge_json_files(self, source_content: str, target_content: str) -> str:
        """Merge JSON files by combining objects."""
        import json

        try:
            source_data = json.loads(source_content)
            target_data = json.loads(target_content)

            # Deep merge for dictionaries
            if isinstance(source_data, dict) and isinstance(target_data, dict):
                merged_data = target_data.copy()
                for key, value in source_data.items():
                    if key not in merged_data:
                        merged_data[key] = value
                    elif isinstance(value, dict) and isinstance(merged_data[key], dict):
                        merged_data[key].update(value)

                return json.dumps(merged_data, indent=2, ensure_ascii=False)

        except json.JSONDecodeError:
            pass

        # Fallback to text merge
        return target_content + "\n\n" + source_content

    def _merge_generic_files(self, source_content: str, target_content: str, source_meta: dict, target_meta: dict) -> str:
        """Generic file merging strategy."""
        # Conservative merge: append source to target with separator
        separator = f"\n\n{'=' * 50}\n# MERGED FROM SOURCE\n{'=' * 50}\n\n"
        return target_content + separator + source_content

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
