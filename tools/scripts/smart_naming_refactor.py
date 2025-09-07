#!/usr/bin/env python3
"""
LUKHAS Smart Naming Refactor Tool
Applies naming conventions while preserving LUKHAS personality
"""

import argparse
import ast
import json
import re
import shutil
from datetime import datetime
from pathlib import Path


class SmartNamingRefactor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.changes_made = []
        self.backup_dir = Path(".naming_backup") / datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        # Load LUKHAS concepts from our conventions
        self.lukhas_concepts = {
            "memory_fold",
            "fold_system",
            "fold_type",
            "fold_id",
            "memory_helix",
            "helix_strand",
            "memory_cascade",
            "dream_recall",
            "dream_engine",
            "dream_resonance",
            "oneiric",
            "dream_state",
            "dream_scenario",
            "qi_state",
            "qi_consciousness",
            "qi_coherence",
            "qi_entanglement",
            "qi_superposition",
            "bio_oscillation",
            "bio_rhythm",
            "bio_coherence",
            "bio_adaptation",
            "bio_symbolic",
            "symbolic_mutation",
            "glyph",
            "glyph_token",
            "symbolic_drift",
            "symbolic_coherence",
            "symbolic_resonance",
            "emotional_drift",
            "emotional_vector",
            "emotion_cascade",
            "affect_grid",
            "mood_regulation",
            "crista",
            "trace_trail",
            "consciousness_state",
            "awareness_level",
            "reflection_depth",
            "tier_access",
            "identity_helix",
            "qi_identity",
            "guardian_protocol",
            "ethical_drift",
            "moral_compass",
            "lukhas",
            "",
            "sgi",
            "agi",
        }

    def backup_file(self, file_path: Path):
        """Create backup before modifying"""
        if not self.dry_run:
            backup_path = self.backup_dir / file_path.relative_to(".")
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)

    def refactor_file(self, file_path: Path) -> bool:
        """Refactor a single file's naming"""
        try:
            with open(file_path) as f:
                original_content = f.read()

            # Parse AST
            tree = ast.parse(original_content)

            # Create transformer
            transformer = LUKHASNameTransformer(self.lukhas_concepts)
            new_tree = transformer.visit(tree)

            # Generate new code
            new_content = ast.unparse(new_tree)

            # Check if changes were made
            if original_content != new_content:
                self.backup_file(file_path)

                if not self.dry_run:
                    with open(file_path, "w") as f:
                        f.write(new_content)

                self.changes_made.append({"file": str(file_path), "changes": transformer.changes})
                return True

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return False

    def refactor_filename(self, file_path: Path) -> Path:
        """Refactor filename if needed"""
        original_name = file_path.name

        if original_name == "__init__.py":
            return file_path

        # Apply snake_case to filename
        base_name = original_name.replace(".py", "")
        new_base = self._to_snake_case(base_name)

        if new_base != base_name:
            new_name = new_base + ".py"
            new_path = file_path.parent / new_name

            if not self.dry_run:
                self.backup_file(file_path)
                file_path.rename(new_path)

            self.changes_made.append(
                {
                    "type": "file_rename",
                    "original": str(file_path),
                    "new": str(new_path),
                }
            )

            return new_path

        return file_path

    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case preserving LUKHAS concepts"""
        # Handle special characters
        name = name.replace("Λ", "lambda").replace("λ", "lambda")

        # Convert from camelCase/PascalCase
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        # Preserve LUKHAS concepts
        for concept in self.lukhas_concepts:
            if concept in result:
                # Keep concept intact
                parts = result.split("_")
                concept_parts = concept.split("_")

                # Reconstruct preserving concept
                final_parts = []
                i = 0
                while i < len(parts):
                    # Check if we're at the start of a concept
                    if i + len(concept_parts) <= len(parts):
                        potential_concept = "_".join(parts[i : i + len(concept_parts)])
                        if potential_concept == concept:
                            final_parts.append(concept)
                            i += len(concept_parts)
                            continue
                    final_parts.append(parts[i])
                    i += 1

                result = "_".join(final_parts)

        return result

    def run(self, target_path: str = "."):
        """Run the refactoring process"""
        print("🔧 LUKHAS Smart Naming Refactor")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("=" * 60)

        target = Path(target_path)
        python_files = list(target.rglob("*.py"))

        # Filter out archives
        python_files = [
            f for f in python_files if not any(skip in str(f) for skip in ["._cleanup_archive", "__pycache__", ".git"])
        ]

        print(f"Found {len(python_files)} Python files to process")

        refactored_count = 0

        for file_path in python_files:
            # First refactor filename
            new_path = self.refactor_filename(file_path)

            # Then refactor contents
            if self.refactor_file(new_path):
                refactored_count += 1

        # Generate report
        self.generate_report()

        print("\n✅ Refactoring complete!")
        print(f"   Files processed: {len(python_files)}")
        print(f"   Files changed: {refactored_count}")
        print(f"   Total changes: {sum(len(c.get('changes', [])) for c in self.changes_made)}")

        if self.dry_run:
            print("\n⚠️  This was a DRY RUN. No files were actually modified.")
            print("   Run with --apply to make actual changes.")

    def generate_report(self):
        """Generate detailed report of changes"""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "dry_run" if self.dry_run else "applied",
            "changes": self.changes_made,
            "summary": {
                "files_changed": len(self.changes_made),
                "total_changes": sum(len(c.get("changes", [])) for c in self.changes_made),
            },
        }

        report_path = Path("docs/reports/analysis/naming_refactor_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: {report_path}")


class LUKHASNameTransformer(ast.NodeTransformer):
    """AST transformer that preserves LUKHAS concepts"""

    def __init__(self, lukhas_concepts: set[str]):
        self.lukhas_concepts = lukhas_concepts
        self.changes = []

    def visit_ClassDef(self, node):
        """Transform class names to PascalCase"""
        self.generic_visit(node)

        original = node.name
        refined = self._to_pascal_case(original)

        if original != refined:
            self.changes.append(
                {
                    "type": "class",
                    "line": node.lineno,
                    "original": original,
                    "refined": refined,
                }
            )
            node.name = refined

        return node

    def visit_FunctionDef(self, node):
        """Transform function names to snake_case"""
        self.generic_visit(node)

        # Skip dunder methods
        if node.name.startswith("__") and node.name.endswith("__"):
            return node

        original = node.name
        refined = self._to_snake_case(original)

        if original != refined:
            self.changes.append(
                {
                    "type": "function",
                    "line": node.lineno,
                    "original": original,
                    "refined": refined,
                }
            )
            node.name = refined

        return node

    def _to_pascal_case(self, name: str) -> str:
        """Convert to PascalCase preserving LUKHAS concepts"""
        # Handle special characters
        name = name.replace("Λ", "Lambda").replace("λ", "Lambda")

        # Handle acronyms
        for acronym in ["lukhas", "", "sgi", "agi"]:
            if acronym in name.lower():
                name = re.sub(f"\\b{acronym}\\b", acronym.upper(), name, flags=re.IGNORECASE)

        # Convert to PascalCase
        if "_" in name:
            parts = name.split("_")
            return "".join(
                (part.capitalize() if part.lower() not in ["", "SGI", "AGI", "LUKHAS"] else part) for part in parts
            )
        else:
            return name[0].upper() + name[1:] if name else name

    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case preserving LUKHAS concepts"""
        # Handle special characters
        name = name.replace("Λ", "lambda").replace("λ", "lambda")

        # Convert from camelCase/PascalCase
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        result = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        # Preserve LUKHAS concepts
        for concept in self.lukhas_concepts:
            if concept.replace("_", "") in result:
                result = result.replace(concept.replace("_", ""), concept)

        return result


def main():
    parser = argparse.ArgumentParser(description="LUKHAS Smart Naming Refactor")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    parser.add_argument("--path", default=".", help="Path to refactor (default: current directory)")

    args = parser.parse_args()

    refactor = SmartNamingRefactor(dry_run=not args.apply)
    refactor.run(args.path)


if __name__ == "__main__":
    main()
