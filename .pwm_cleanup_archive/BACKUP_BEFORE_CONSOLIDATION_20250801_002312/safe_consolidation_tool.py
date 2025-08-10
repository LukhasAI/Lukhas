#!/usr/bin/env python3
"""
Safe Consolidation Tool for LUKHAS
Compares files before merging and identifies intruders
"""

import ast
import difflib
import hashlib
import json
from pathlib import Path
from typing import Dict, List


class SafeConsolidator:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.intruder_patterns = [
            "eval(",
            "exec(",
            "__import__",
            "compile(",
            "subprocess",
            "os.system",
            "pickle.loads",
            "marshal.loads",
            "importlib.import_module",
        ]
        self.safe_modules = {
            "dream": ["dream", "creativity/dream", "oneiric"],
            "memory": ["memory"],
            "consciousness": ["consciousness"],
            "bio": ["bio"],
            "quantum": ["quantum"],
            "identity": ["identity"],
        }

    def find_intruders(self) -> Dict[str, List[str]]:
        """Find files that don't belong in their current module"""
        intruders = {}

        for module, safe_dirs in self.safe_modules.items():
            module_intruders = []

            # Find files in this module
            for safe_dir in safe_dirs:
                dir_path = self.root_path / safe_dir
                if not dir_path.exists():
                    continue

                for file_path in dir_path.rglob("*.py"):
                    if self._is_intruder(file_path, module):
                        module_intruders.append(
                            str(file_path.relative_to(self.root_path))
                        )

            if module_intruders:
                intruders[module] = module_intruders

        return intruders

    def _is_intruder(self, file_path: Path, expected_module: str) -> bool:
        """Check if a file is an intruder in the given module"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for dangerous patterns
            for pattern in self.intruder_patterns:
                if pattern in content:
                    return True

            # Check if file belongs to a different module
            file_str = str(file_path).lower()
            for module, keywords in self.safe_modules.items():
                if module != expected_module:
                    # If file strongly belongs to another module
                    if any(keyword in file_str for keyword in keywords):
                        # But is in the wrong place
                        if expected_module in str(file_path.parent).lower():
                            return True

            # Check imports for module mismatch
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if self._is_wrong_import(alias.name, expected_module):
                                return True
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and self._is_wrong_import(
                            node.module, expected_module
                        ):
                            return True
            except:
                pass

        except Exception as e:
            print(f"Error checking {file_path}: {e}")

        return False

    def _is_wrong_import(self, import_name: str, current_module: str) -> bool:
        """Check if an import suggests the file is in the wrong module"""
        # If importing from a completely different system
        for module in self.safe_modules:
            if module != current_module and import_name.startswith(module):
                # But only if it's a core import, not a bridge
                if "bridge" not in import_name and "adapter" not in import_name:
                    return True
        return False

    def compare_duplicates(self, file_pattern: str) -> Dict[str, List[Dict]]:
        """Compare files with similar names to find true duplicates"""
        duplicates = {}

        # Find all files matching pattern
        files = list(self.root_path.rglob(file_pattern))

        if len(files) < 2:
            return duplicates

        # Compare each pair
        for i, file1 in enumerate(files):
            for file2 in files[i + 1 :]:
                similarity = self._compare_files(file1, file2)

                key = file_pattern
                if key not in duplicates:
                    duplicates[key] = []

                duplicates[key].append(
                    {
                        "file1": str(file1.relative_to(self.root_path)),
                        "file2": str(file2.relative_to(self.root_path)),
                        "similarity": similarity["ratio"],
                        "identical": similarity["identical"],
                        "size_diff": similarity["size_diff"],
                        "line_diff": similarity["line_diff"],
                        "unique_to_file1": similarity["unique_to_file1"],
                        "unique_to_file2": similarity["unique_to_file2"],
                    }
                )

        return duplicates

    def _compare_files(self, file1: Path, file2: Path) -> Dict:
        """Detailed comparison of two files"""
        try:
            with open(file1, encoding="utf-8") as f:
                content1 = f.read()
                lines1 = content1.splitlines()

            with open(file2, encoding="utf-8") as f:
                content2 = f.read()
                lines2 = content2.splitlines()

            # Check if identical
            hash1 = hashlib.md5(content1.encode()).hexdigest()
            hash2 = hashlib.md5(content2.encode()).hexdigest()

            # Calculate similarity
            sm = difflib.SequenceMatcher(None, lines1, lines2)
            ratio = sm.ratio()

            # Find unique content
            unique_to_file1 = []
            unique_to_file2 = []

            for tag, i1, i2, j1, j2 in sm.get_opcodes():
                if tag == "delete":
                    unique_to_file1.extend(lines1[i1:i2])
                elif tag == "insert":
                    unique_to_file2.extend(lines2[j1:j2])
                elif tag == "replace":
                    unique_to_file1.extend(lines1[i1:i2])
                    unique_to_file2.extend(lines2[j1:j2])

            return {
                "identical": hash1 == hash2,
                "ratio": ratio,
                "size_diff": abs(len(content1) - len(content2)),
                "line_diff": abs(len(lines1) - len(lines2)),
                "unique_to_file1": len(unique_to_file1),
                "unique_to_file2": len(unique_to_file2),
            }

        except Exception as e:
            return {
                "identical": False,
                "ratio": 0,
                "size_diff": -1,
                "line_diff": -1,
                "unique_to_file1": 0,
                "unique_to_file2": 0,
                "error": str(e),
            }

    def find_scattered_files(self, module: str) -> List[Dict]:
        """Find files belonging to a module but located elsewhere"""
        scattered = []
        module_keywords = self.safe_modules.get(module, [])

        # Search entire codebase
        for file_path in self.root_path.rglob("*.py"):
            file_str = str(file_path).lower()

            # Skip if already in correct location
            if any(safe_dir in file_str for safe_dir in self.safe_modules[module]):
                continue

            # Check if file belongs to this module
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                # Strong indicators
                strong_match = False
                if f"# {module.upper()}" in content:
                    strong_match = True
                if f"class {module.capitalize()}" in content:
                    strong_match = True
                if any(f"from {module}" in content for module in module_keywords):
                    strong_match = True

                # Weak indicators
                weak_match = (
                    sum(1 for keyword in module_keywords if keyword in content.lower())
                    >= 3
                )

                if strong_match or weak_match:
                    scattered.append(
                        {
                            "file": str(file_path.relative_to(self.root_path)),
                            "confidence": "high" if strong_match else "medium",
                            "current_location": str(
                                file_path.parent.relative_to(self.root_path)
                            ),
                            "suggested_location": f"{module}/{file_path.name}",
                        }
                    )

            except Exception:
                pass

        return scattered

    def generate_consolidation_plan(self):
        """Generate a safe consolidation plan"""
        plan = {
            "intruders": self.find_intruders(),
            "duplicates": {},
            "scattered": {},
            "warnings": [],
        }

        # Check for duplicates in key files
        duplicate_patterns = [
            "*engine.py",
            "*manager.py",
            "*hub.py",
            "*core.py",
            "*bridge.py",
        ]

        for pattern in duplicate_patterns:
            dups = self.compare_duplicates(pattern)
            if dups:
                plan["duplicates"].update(dups)

        # Find scattered files for each module
        for module in self.safe_modules:
            scattered = self.find_scattered_files(module)
            if scattered:
                plan["scattered"][module] = scattered

        # Add warnings for dangerous patterns
        plan["warnings"] = self._scan_for_dangers()

        return plan

    def _scan_for_dangers(self) -> List[Dict]:
        """Scan for potentially dangerous code patterns"""
        warnings = []

        for file_path in self.root_path.rglob("*.py"):
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                for i, line in enumerate(content.splitlines(), 1):
                    for pattern in self.intruder_patterns:
                        if pattern in line:
                            warnings.append(
                                {
                                    "file": str(file_path.relative_to(self.root_path)),
                                    "line": i,
                                    "pattern": pattern,
                                    "content": line.strip()[:100],
                                }
                            )

            except Exception:
                pass

        return warnings


def main():
    """Run safe consolidation analysis"""
    consolidator = SafeConsolidator(".")
    plan = consolidator.generate_consolidation_plan()

    # Save detailed plan
    with open("SAFE_CONSOLIDATION_PLAN.json", "w") as f:
        json.dump(plan, f, indent=2)

    # Generate summary report
    with open("CONSOLIDATION_SAFETY_REPORT.md", "w") as f:
        f.write("# LUKHAS Safe Consolidation Report\n\n")

        # Intruders
        if plan["intruders"]:
            f.write("## ⚠️ Intruder Files Found\n\n")
            for module, files in plan["intruders"].items():
                f.write(f"### {module.upper()}\n")
                for file in files[:10]:
                    f.write(f"- {file}\n")
                if len(files) > 10:
                    f.write(f"- ... and {len(files) - 10} more\n")
                f.write("\n")

        # Warnings
        if plan["warnings"]:
            f.write("## 🚨 Security Warnings\n\n")
            f.write("Found potentially dangerous patterns:\n\n")
            for warning in plan["warnings"][:20]:
                f.write(
                    f"- **{warning['file']}:{warning['line']}** - `{warning['pattern']}` found\n"
                )
            if len(plan["warnings"]) > 20:
                f.write(f"\n... and {len(plan['warnings']) - 20} more warnings\n")
            f.write("\n")

        # Duplicates
        if plan["duplicates"]:
            f.write("## 📋 Duplicate Analysis\n\n")
            for pattern, comparisons in plan["duplicates"].items():
                f.write(f"### {pattern}\n")
                for comp in comparisons:
                    if comp["identical"]:
                        f.write(f"- **IDENTICAL**: {comp['file1']} = {comp['file2']}\n")
                    else:
                        f.write(
                            f"- **{comp['similarity']:.1%} similar**: {comp['file1']} vs {comp['file2']}\n"
                        )
                        f.write(
                            f"  - Lines unique to file1: {comp['unique_to_file1']}\n"
                        )
                        f.write(
                            f"  - Lines unique to file2: {comp['unique_to_file2']}\n"
                        )
                f.write("\n")

        # Scattered files
        if plan["scattered"]:
            f.write("## 🌐 Scattered Files\n\n")
            for module, files in plan["scattered"].items():
                f.write(f"### {module.upper()} ({len(files)} files)\n")
                high_confidence = [f for f in files if f["confidence"] == "high"]
                if high_confidence:
                    f.write("\n**High Confidence:**\n")
                    for file in high_confidence[:10]:
                        f.write(f"- {file['file']} → {file['suggested_location']}\n")
                f.write("\n")

    print("Safe consolidation analysis complete!")
    print("Check SAFE_CONSOLIDATION_PLAN.json and CONSOLIDATION_SAFETY_REPORT.md")


if __name__ == "__main__":
    main()
