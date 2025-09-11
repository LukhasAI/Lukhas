#!/usr/bin/env python3
"""
Focused LUKHAS Code Atlas Builder
=================================

A more targeted version that focuses on core LUKHAS consciousness modules.
"""

import ast
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional, Union


@dataclass
class SymbolInfo:
    """Information about a function or class."""

    name: str
    type: str  # 'function', 'class', 'method'
    file_path: str
    line_number: int
    signature: str
    docstring_summary: str
    class_name: Optional[str]  # For methods
    issues: list[str]  # Issue flags


@dataclass
class ModuleInfo:
    """Information about a module."""

    file_path: str
    role: str
    intent_clues: list[str]
    symbols: list[str]
    imports: list[str]
    violations: list[dict]


class FocusedAtlasBuilder:
    """Builds focused code atlas for LUKHAS consciousness architecture."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.symbols: dict[str, SymbolInfo] = {}
        self.modules: dict[str, ModuleInfo] = {}
        self.violations: dict[str, list[dict]] = defaultdict(list)

        # Focus on LUKHAS core directories
        self.focus_dirs = [
            "lukhas/",
            "candidate/",
            "consciousness/",
            "memory/",
            "identity/",
            "governance/",
            "core/",
            "orchestration/",
            "quantum/",
            "bio/",
            "creativity/",
            "emotion/",
            "vivox/",
            "bridge/",
            "api/",
            "branding/",
            "agents/",
        ]

        # LUKHAS consciousness keywords
        self.consciousness_keywords = {
            "consciousness",
            "lucid",
            "dream",
            "identity",
            "memory",
            "fold",
            "guardian",
            "ethics",
            "quantum",
            "bio",
            "matriz",
            "glyph",
            "constellation",
            "drift",
            "cascade",
            "vivox",
            "qualia",
        }

    def run(self):
        """Run focused analysis."""
        print("🧬 LUKHAS Focused Code Atlas Analysis")
        print("=" * 50)

        # 1. Collect violations
        print("📊 Collecting lint violations...")
        self.collect_violations()

        # 2. Analyze focused Python files
        print("🔍 Analyzing focused Python modules...")
        self.analyze_focused_files()

        # 3. Extract intent clues
        print("💭 Extracting intent clues...")
        self.extract_intent_clues()

        # 4. Generate atlas
        print("📋 Generating focused atlas...")
        atlas = self.generate_atlas()

        # 5. Generate per-rule indices
        print("📊 Generating violation indices...")
        self.generate_rule_indices()

        # 6. Save results
        self.save_atlas(atlas)

        print("🎉 Focused LUKHAS Code Atlas complete!")

    def collect_violations(self):
        """Collect lint violations focusing on target directories."""
        try:
            # Focus only on key directories to reduce noise
            focus_paths = [d for d in self.focus_dirs if (self.root_path / d).exists()]

            if not focus_paths:
                focus_paths = ["."]  # Fallback to current directory

            for focus_path in focus_paths[:3]:  # Limit to first 3 to avoid timeout
                print(f"  Checking violations in {focus_path}...")
                result = subprocess.run(
                    [sys.executable, "-m", "ruff", "check", focus_path, "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout per directory
                )

                if result.stdout:
                    violations = json.loads(result.stdout)
                    for violation in violations:
                        rule_code = violation.get("code", "UNKNOWN")
                        self.violations[rule_code].append(violation)

        except subprocess.TimeoutExpired:
            print("⚠️ Ruff timeout - using partial results")
        except Exception as e:
            print(f"⚠️ Could not collect violations: {e}")

        total_violations = sum(len(v) for v in self.violations.values())
        print(f"📋 Found {total_violations} violations across {len(self.violations)} rule types")

    def analyze_focused_files(self):
        """Analyze files in focus directories only."""
        python_files = []

        # Get files from focus directories
        for focus_dir in self.focus_dirs:
            focus_path = self.root_path / focus_dir
            if focus_path.exists():
                python_files.extend(focus_path.rglob("*.py"))

        # Remove duplicates and limit for performance
        python_files = list(set(python_files))[:2000]  # Limit to 2000 files max

        print(f"🔍 Analyzing {len(python_files)} focused Python files...")

        analyzed = 0
        for i, py_file in enumerate(python_files):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(python_files)} files")

            try:
                if self.analyze_file(py_file):
                    analyzed += 1
            except Exception as e:
                if any(pattern in str(py_file) for pattern in ["lukhas/", "candidate/"]):
                    if "syntax" not in str(e).lower():
                        print(f"⚠️ Error analyzing {py_file.name}: {e}")

        print(f"✅ Successfully analyzed {analyzed} files")

    def analyze_file(self, file_path: Path) -> bool:
        """Analyze a single Python file."""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Skip very large files
            if len(content) > 100000:  # Skip files > 100KB
                return False

            # Try to parse, skip on syntax errors
            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError:
                # Record as syntax error module
                rel_path = str(file_path.relative_to(self.root_path))
                self.modules[rel_path] = ModuleInfo(
                    file_path=rel_path,
                    role="syntax_error",
                    intent_clues=["SYNTAX_ERROR"],
                    symbols=[],
                    imports=[],
                    violations=[],
                )
                return False

            # Initialize module info
            rel_path = str(file_path.relative_to(self.root_path))
            module_info = ModuleInfo(
                file_path=rel_path,
                role=self.determine_module_role(rel_path),
                intent_clues=self.extract_module_intent_clues(content, file_path),
                symbols=[],
                imports=[],
                violations=[],
            )

            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbol_info = self.extract_symbol_info(node, file_path, content, "function")
                    if symbol_info:
                        symbol_key = f"{rel_path}:{symbol_info.name}"
                        self.symbols[symbol_key] = symbol_info
                        module_info.symbols.append(symbol_key)

                elif isinstance(node, ast.ClassDef):
                    symbol_info = self.extract_symbol_info(node, file_path, content, "class")
                    if symbol_info:
                        symbol_key = f"{rel_path}:{symbol_info.name}"
                        self.symbols[symbol_key] = symbol_info
                        module_info.symbols.append(symbol_key)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports = self.extract_imports(node)
                    module_info.imports.extend(imports)

            # Find violations for this module
            module_violations = []
            for rule_violations in self.violations.values():
                for violation in rule_violations:
                    if rel_path in violation.get("filename", ""):
                        module_violations.append(violation)
            module_info.violations = module_violations

            self.modules[rel_path] = module_info
            return True

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return False

    def extract_symbol_info(self, node, file_path: Path, content: str, symbol_type: str) -> Optional[SymbolInfo]:
        """Extract information about a symbol (function or class)."""
        try:
            name = node.name
            line_number = node.lineno

            # Get signature
            if symbol_type == "function":
                signature = f"{name}("
                if hasattr(node, "args"):
                    args = []
                    for arg in node.args.args:
                        args.append(arg.arg)
                    signature += ", ".join(args)
                signature += ")"
            else:  # class
                signature = f"class {name}"
                if hasattr(node, "bases") and node.bases:
                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                    if bases:
                        signature += f"({', '.join(bases)})"

            # Get docstring
            docstring = ""
            if node.body and isinstance(node.body[0], ast.Expr):
                value = node.body[0].value
                if isinstance(value, ast.Str):
                    docstring = value.s[:200]
                elif isinstance(value, ast.Constant) and isinstance(value.value, str):
                    docstring = value.value[:200]

            # Check if it's a method (for functions)
            class_name = None
            if symbol_type == "function":
                # Simple heuristic: check indentation level
                lines = content.split("\n")
                if line_number > 0 and line_number <= len(lines):
                    line = lines[line_number - 1]
                    if line.startswith("    ") and not line.startswith("        "):
                        # Likely a method (class-level indentation)
                        for i in range(line_number - 1, -1, -1):
                            if i < len(lines):
                                prev_line = lines[i].strip()
                                if prev_line.startswith("class "):
                                    class_name = prev_line.split()[1].split("(")[0].rstrip(":")
                                    symbol_type = "method"
                                    break
                                elif prev_line and not prev_line.startswith(" "):
                                    break

            return SymbolInfo(
                name=name,
                type=symbol_type,
                file_path=str(file_path.relative_to(self.root_path)),
                line_number=line_number,
                signature=signature,
                docstring_summary=docstring,
                class_name=class_name,
                issues=[],
            )

        except Exception as e:
            print(f"Error extracting symbol info for {node.name}: {e}")
            return None

    def extract_imports(self, node: Union[ast.Import, ast.ImportFrom]) -> list[str]:
        """Extract import statements."""
        imports = []
        try:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        except Exception:
            pass
        return imports

    def extract_module_intent_clues(self, content: str, file_path: Path) -> list[str]:
        """Extract intent clues from module content."""
        clues = []

        # Module docstring
        try:
            tree = ast.parse(content)
            if tree.body and isinstance(tree.body[0], ast.Expr):
                value = tree.body[0].value
                if isinstance(value, ast.Str):
                    clues.append(f"MODULE_DOC: {value.s[:150]}...")
                elif isinstance(value, ast.Constant) and isinstance(value.value, str):
                    clues.append(f"MODULE_DOC: {value.value[:150]}...")
        except Exception:
            pass

        # Key comments and TODOs (sample first 50 lines to avoid performance issues)
        lines = content.split("\n")[:50]
        for _i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#") and len(stripped) > 5:
                comment = stripped[1:].strip()
                if any(keyword in comment.lower() for keyword in ["todo", "fixme", "bug", "hack"]):
                    clues.append(f"TODO: {comment[:80]}")
                elif any(keyword in comment.lower() for keyword in self.consciousness_keywords):
                    clues.append(f"CONSCIOUSNESS: {comment[:80]}")

        # Path-based clues
        path_str = str(file_path).lower()
        for keyword in self.consciousness_keywords:
            if keyword in path_str:
                clues.append(f"PATH_KEYWORD: {keyword}")

        return clues[:10]  # Limit to 10 clues per module

    def determine_module_role(self, module_path: str) -> str:
        """Determine the role of a module using heuristics."""
        path_lower = module_path.lower()

        # Direct path matching
        if "test" in path_lower:
            return "test"
        elif any(pattern in path_lower for pattern in ["api", "serve", "endpoint"]):
            return "api"
        elif any(pattern in path_lower for pattern in ["orchestrat", "hub", "brain", "kernel"]):
            return "orchestrator"
        elif any(pattern in path_lower for pattern in ["bridge", "integrat", "adapter"]):
            return "integration"
        elif any(pattern in path_lower for pattern in ["consciousness", "dream", "identity", "memory"]):
            return "consciousness_core"
        elif any(pattern in path_lower for pattern in ["guardian", "ethics", "governance"]):
            return "governance"
        elif any(pattern in path_lower for pattern in ["quantum", "bio"]):
            return "advanced_processing"
        elif "candidate" in path_lower:
            return "experimental"
        elif "lukhas" in path_lower:
            return "production"

        return "utility"

    def extract_intent_clues(self):
        """Extract intent clues from documentation files."""
        print("💭 Extracting documentation intent clues...")

        doc_patterns = ["README*", "DESIGN*", "docs/**/*.md"]
        doc_files = []

        for pattern in doc_patterns:
            doc_files.extend(self.root_path.glob(pattern))

        # Limit to first 20 docs to avoid performance issues
        doc_files = doc_files[:20]
        print(f"📚 Processing {len(doc_files)} documentation files")

        for doc_file in doc_files:
            try:
                with open(doc_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()[:5000]  # Limit content size

                # Extract key architecture concepts
                intent_clues = []
                lines = content.split("\n")[:50]  # First 50 lines only

                for line in lines:
                    stripped = line.strip()
                    if len(stripped) > 20:  # Substantial content only
                        if any(keyword in stripped.lower() for keyword in self.consciousness_keywords):
                            intent_clues.append(f"DOC: {stripped[:100]}")
                        elif stripped.startswith("#") or stripped.startswith("-") or stripped.startswith("*"):
                            intent_clues.append(f"HEADER: {stripped[:100]}")

                # Associate with nearby modules (simplified)
                doc_stem = doc_file.stem.lower()
                for module_path, module_info in self.modules.items():
                    if doc_stem in module_path.lower() or any(
                        doc_stem in clue.lower() for clue in module_info.intent_clues
                    ):
                        module_info.intent_clues.extend(intent_clues[:5])  # Limit to 5 clues

            except Exception as e:
                print(f"Error reading doc {doc_file}: {e}")

    def generate_atlas(self) -> dict:
        """Generate the focused code atlas."""
        print("📋 Generating focused atlas...")

        # Map violations to symbols
        for symbol_info in self.symbols.values():
            for rule_violations in self.violations.values():
                for violation in rule_violations:
                    if symbol_info.file_path in violation.get("filename", ""):
                        line_no = violation.get("location", {}).get("row", 0)
                        if abs(symbol_info.line_number - line_no) < 10:  # Within 10 lines
                            issue_flag = self.get_issue_flag(violation.get("code", ""))
                            if issue_flag not in symbol_info.issues:
                                symbol_info.issues.append(issue_flag)

        atlas = {
            "metadata": {
                "generator": "LUKHAS Focused Code Atlas Builder",
                "focus_directories": self.focus_dirs,
                "total_modules": len(self.modules),
                "total_symbols": len(self.symbols),
                "total_violations": sum(len(v) for v in self.violations.values()),
                "violation_types": list(self.violations.keys()),
                "consciousness_keywords": list(self.consciousness_keywords),
            },
            "symbols": {k: asdict(v) for k, v in self.symbols.items()},
            "modules": {k: asdict(v) for k, v in self.modules.items()},
            "violations_by_rule": {k: len(v) for k, v in self.violations.items()},
            "module_roles": {
                role: [k for k, v in self.modules.items() if v.role == role]
                for role in set(m.role for m in self.modules.values())
            },
        }

        return atlas

    def get_issue_flag(self, rule_code: str) -> str:
        """Convert ruff rule code to issue flag."""
        flag_mapping = {
            "ARG001": "unused_func_arg",
            "ARG002": "unused_method_arg",
            "F821": "undefined_name",
            "F401": "unused_import",
            "RUF006": "dangling_async_task",
            "B006": "mutable_default",
            "DTZ005": "datetime_naive",
            "DTZ003": "datetime_utcnow",
            "E402": "import_not_top",
            "F841": "unused_variable",
            "B007": "unused_loop_var",
        }
        return flag_mapping.get(rule_code, f"rule_{rule_code}")

    def generate_rule_indices(self):
        """Generate per-rule violation indices."""
        reports_dir = self.root_path / "reports"
        reports_dir.mkdir(exist_ok=True)

        for rule_code, violations in self.violations.items():
            if violations:
                index_file = reports_dir / f"idx_{rule_code}.json"

                rule_index = {
                    "rule_code": rule_code,
                    "description": self.get_rule_description(rule_code),
                    "total_violations": len(violations),
                    "violations": violations,
                    "affected_files": list(set(v.get("filename", "") for v in violations)),
                    "focus_directories_affected": [
                        d for d in self.focus_dirs if any(d in v.get("filename", "") for v in violations)
                    ],
                }

                with open(index_file, "w") as f:
                    json.dump(rule_index, f, indent=2)

    def get_rule_description(self, rule_code: str) -> str:
        """Get description for rule code."""
        descriptions = {
            "ARG001": "Unused function argument",
            "ARG002": "Unused method argument",
            "F821": "Undefined name",
            "F401": "Unused import",
            "RUF006": "Dangling async task",
            "B006": "Mutable default argument",
            "DTZ005": "Naive datetime usage",
            "DTZ003": "datetime.utcnow() usage",
            "E402": "Module level import not at top",
            "F841": "Unused local variable",
            "B007": "Unused loop control variable",
        }
        return descriptions.get(rule_code, f"Rule {rule_code}")

    def save_atlas(self, atlas: dict):
        """Save the atlas to JSON file."""
        reports_dir = self.root_path / "reports"
        reports_dir.mkdir(exist_ok=True)

        atlas_file = reports_dir / "code_atlas.json"

        with open(atlas_file, "w") as f:
            json.dump(atlas, f, indent=2)

        print(f"💾 Focused Code Atlas saved to: {atlas_file}")
        print("📊 Atlas Summary:")
        print(f"   • {len(atlas['symbols'])} symbols analyzed")
        print(f"   • {len(atlas['modules'])} modules processed")
        print(f"   • {atlas['metadata']['total_violations']} violations mapped")
        print(f"   • {len(atlas['module_roles'])} different module roles identified")

        # Print top violation types
        violation_counts = atlas["violations_by_rule"]
        if violation_counts:
            sorted_violations = sorted(violation_counts.items(), key=lambda x: x[1], reverse=True)
            print(f"   • Top violations: {', '.join([f'{k}({v})' for k, v in sorted_violations[:5]])}")


if __name__ == "__main__":
    print("🧬 LUKHAS Focused Code Atlas Builder")
    print("Building comprehensive code intelligence for consciousness architecture...")

    builder = FocusedAtlasBuilder(".")
    builder.run()
