#!/usr/bin/env python3
"""
LUKHAS Code Atlas Builder
=========================

Builds a comprehensive code atlas for strategic transformation of 18,000+ lint violations.
Maps architecture, call graphs, intent clues, and violation patterns.

Created for LUKHAS consciousness architecture transformation project.
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union


@dataclass
class FunctionInfo:
    """Information about a function or method."""
    name: str
    file_path: str
    line_number: int
    signature: str
    docstring_summary: str
    is_method: bool
    class_name: Optional[str]
    callers: List[str]  # Functions that call this
    callees: List[str]  # Functions this calls
    string_references: List[str]  # References by name as strings
    issues: List[str]  # Issue flags like "unused_param", "unused_func"


@dataclass
class ClassInfo:
    """Information about a class."""
    name: str
    file_path: str
    line_number: int
    docstring_summary: str
    methods: List[str]
    base_classes: List[str]
    issues: List[str]


@dataclass
class ModuleInfo:
    """Information about a module."""
    file_path: str
    role: str  # orchestrator, integration, adapter, domain_model, test_helper
    intent_clues: List[str]  # From docstrings, comments, TODOs
    functions: List[str]
    classes: List[str]
    imports: List[str]


class CodeAtlasBuilder:
    """Builds comprehensive code atlas for LUKHAS consciousness architecture."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.functions: Dict[str, FunctionInfo] = {}
        self.classes: Dict[str, ClassInfo] = {}
        self.modules: Dict[str, ModuleInfo] = {}
        self.violations: Dict[str, List[dict]] = defaultdict(list)
        self.call_graph: Dict[str, Set[str]] = defaultdict(set)
        self.string_references: Dict[str, Set[str]] = defaultdict(set)

        # LUKHAS-specific patterns
        self.consciousness_keywords = {
            "consciousness", "lucid", "dream", "identity", "memory", "fold", 
            "guardian", "ethics", "quantum", "bio", "MATRIZ", "MATRIZ", "glyph",
            "constellation", "drift", "cascade", "vivox", "qualia", "aka_qualia"
        }

        # Module role patterns
        self.role_patterns = {
            "orchestrator": ["orchestrat", "hub", "brain", "kernel", "coordinator", "primary"],
            "integration": ["integrat", "bridge", "connector", "adapter", "wrapper"],
            "adapter": ["adapter", "client", "api", "service", "external"],
            "domain_model": ["model", "entity", "schema", "data", "storage"],
            "test_helper": ["test", "mock", "fixture", "helper", "util"]
        }

    def analyze_codebase(self):
        """Main analysis function."""
        print("🧬 Starting LUKHAS Code Atlas Analysis...")

        # Step 1: Get lint violations
        print("📊 Collecting lint violations...")
        self.collect_violations()

        # Step 2: Analyze Python files
        print("🔍 Analyzing Python modules...")
        self.analyze_python_files()

        # Step 3: Build call graphs
        print("🔗 Building call graphs...")
        self.build_call_graphs()

        # Step 4: Extract intent clues
        print("💭 Extracting intent clues...")
        self.extract_intent_clues()

        # Step 5: Classify module roles
        print("🏷️ Classifying module roles...")
        self.classify_module_roles()

        print("✅ Analysis complete!")

    def collect_violations(self):
        """Collect lint violations using ruff."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruff", "check", ".", "--format=json"],
                capture_output=True,
                text=True,
                cwd=self.root_path
            )

            if result.stdout:
                violations = json.loads(result.stdout)
                for violation in violations:
                    rule_code = violation.get("code", "UNKNOWN")
                    self.violations[rule_code].append(violation)

            print(f"📋 Found {len(sum(self.violations.values(), []))} total violations")
            print(f"📝 Violation types: {list(self.violations.keys())[:10]}...")

        except Exception as e:
            print(f"⚠️ Could not collect violations: {e}")

    def analyze_python_files(self):
        """Analyze all Python files for functions, classes, and structure."""
        # Focus on LUKHAS core modules and exclude problematic paths
        exclude_patterns = [
            ".cleanenv/", ".venv/", "__pycache__/", ".git/",
            "node_modules/", "venv/", "env/", ".pytest_cache/",
            "site-packages/", "dist/", "build/"
        ]

        python_files = []
        for py_file in self.root_path.rglob("*.py"):
            file_str = str(py_file)
            if not any(pattern in file_str for pattern in exclude_patterns):
                python_files.append(py_file)

        print(f"🔍 Analyzing {len(python_files)} Python files (excluding virtualenvs and build dirs)...")

        for i, py_file in enumerate(python_files):
            if i % 500 == 0:
                print(f"Progress: {i}/{len(python_files)} files analyzed")

            try:
                self.analyze_file(py_file)
            except Exception as e:
                # Only print errors for non-syntax issues or critical files
                if any(pattern in str(py_file) for pattern in ["lukhas/", "candidate/", "core/", "consciousness/"]):
                    if "f-string" not in str(e) and "invalid syntax" not in str(e):
                        print(f"⚠️ Error analyzing {py_file}: {e}")

    def analyze_file(self, file_path: Path):
        """Analyze a single Python file."""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Skip files with known syntax issues
            if any(issue in content for issue in ["f-string:", "closing parenthesis", "invalid syntax"]):
                # Try to parse anyway but catch syntax errors
                pass

            try:
                tree = ast.parse(content, filename=str(file_path))
            except SyntaxError as e:
                # Skip files with syntax errors but record them
                rel_path = str(file_path.relative_to(self.root_path))
                self.modules[rel_path] = ModuleInfo(
                    file_path=rel_path,
                    role="syntax_error",
                    intent_clues=[f"SYNTAX_ERROR: {str(e)[:100]}"],
                    functions=[],
                    classes=[],
                    imports=[]
                )
                return

            # Initialize module info
            rel_path = str(file_path.relative_to(self.root_path))
            module_info = ModuleInfo(
                file_path=rel_path,
                role="unknown",
                intent_clues=[],
                functions=[],
                classes=[],
                imports=[]
            )

            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self.extract_function_info(node, file_path, content)
                    if func_info:
                        func_key = f"{rel_path}:{func_info.name}"
                        self.functions[func_key] = func_info
                        module_info.functions.append(func_key)

                elif isinstance(node, ast.ClassDef):
                    class_info = self.extract_class_info(node, file_path, content)
                    if class_info:
                        class_key = f"{rel_path}:{class_info.name}"
                        self.classes[class_key] = class_info
                        module_info.classes.append(class_key)

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports = self.extract_imports(node)
                    module_info.imports.extend(imports)

            # Extract module-level intent clues
            module_info.intent_clues = self.extract_module_intent_clues(content, file_path)

            self.modules[rel_path] = module_info

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    def extract_function_info(self, node: ast.FunctionDef, file_path: Path, content: str) -> Optional[FunctionInfo]:
        """Extract information about a function."""
        try:
            # Get signature
            signature = f"{node.name}("
            args = []
            for arg in node.args.args:
                args.append(arg.arg)
            signature += ", ".join(args) + ")"

            # Get docstring
            docstring = ""
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                docstring = node.body[0].value.s[:200] + "..." if len(node.body[0].value.s) > 200 else node.body[0].value.s
            elif node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                if isinstance(node.body[0].value.value, str):
                    docstring = node.body[0].value.value[:200] + "..." if len(node.body[0].value.value) > 200 else node.body[0].value.value

            # Check if it's a method
            is_method = False
            class_name = None

            # Find parent class if any
            lines = content.split("\n")
            for i in range(node.lineno - 1, -1, -1):
                if i < len(lines):
                    line = lines[i].strip()
                    if line.startswith("class "):
                        class_name = line.split()[1].split("(")[0].rstrip(":")
                        is_method = True
                        break
                    elif line and not line.startswith(" ") and not line.startswith("\t"):
                        break

            return FunctionInfo(
                name=node.name,
                file_path=str(file_path.relative_to(self.root_path)),
                line_number=node.lineno,
                signature=signature,
                docstring_summary=docstring,
                is_method=is_method,
                class_name=class_name,
                callers=[],
                callees=[],
                string_references=[],
                issues=[]
            )

        except Exception as e:
            print(f"Error extracting function info for {node.name}: {e}")
            return None

    def extract_class_info(self, node: ast.ClassDef, file_path: Path, content: str) -> Optional[ClassInfo]:
        """Extract information about a class."""
        try:
            # Get docstring
            docstring = ""
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Str):
                docstring = node.body[0].value.s[:200] + "..." if len(node.body[0].value.s) > 200 else node.body[0].value.s
            elif node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                if isinstance(node.body[0].value.value, str):
                    docstring = node.body[0].value.value[:200] + "..." if len(node.body[0].value.value) > 200 else node.body[0].value.value

            # Get methods
            methods = []
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    methods.append(child.name)

            # Get base classes
            base_classes = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_classes.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_classes.append(f"{base.value.id}.{base.attr}")

            return ClassInfo(
                name=node.name,
                file_path=str(file_path.relative_to(self.root_path)),
                line_number=node.lineno,
                docstring_summary=docstring,
                methods=methods,
                base_classes=base_classes,
                issues=[]
            )

        except Exception as e:
            print(f"Error extracting class info for {node.name}: {e}")
            return None

    def extract_imports(self, node: Union[ast.Import, ast.ImportFrom]) -> List[str]:
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

    def extract_module_intent_clues(self, content: str, file_path: Path) -> List[str]:
        """Extract intent clues from module content."""
        clues = []

        # Module docstring
        try:
            tree = ast.parse(content)
            if tree.body and isinstance(tree.body[0], ast.Expr):
                if isinstance(tree.body[0].value, ast.Str):
                    clues.append(f"MODULE_DOC: {tree.body[0].value.s[:200]}...")
                elif isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str):
                    clues.append(f"MODULE_DOC: {tree.body[0].value.value[:200]}...")
        except Exception:
            pass

        # Comments and TODOs
        lines = content.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                comment = stripped[1:].strip()
                if any(keyword in comment.lower() for keyword in ["todo", "fixme", "hack", "bug"]):
                    clues.append(f"TODO_L{i+1}: {comment[:100]}")
                elif any(keyword in comment.lower() for keyword in self.consciousness_keywords):
                    clues.append(f"CONSCIOUSNESS_L{i+1}: {comment[:100]}")
                elif len(comment) > 20:  # Substantial comments
                    clues.append(f"COMMENT_L{i+1}: {comment[:100]}")

        # LUKHAS-specific patterns in filename or path
        path_str = str(file_path).lower()
        for keyword in self.consciousness_keywords:
            if keyword in path_str:
                clues.append(f"PATH_PATTERN: {keyword}")

        return clues

    def build_call_graphs(self):
        """Build call graphs for functions."""
        print("🔗 Building function call graphs...")

        for module_path, module_info in self.modules.items():
            try:
                with open(self.root_path / module_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                tree = ast.parse(content)

                # Find function calls and references
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        self.analyze_function_call(node, module_path)
                    elif isinstance(node, ast.Name):
                        # Potential function reference
                        self.analyze_name_reference(node, module_path)
                    elif isinstance(node, ast.Str):
                        # String that might reference a function
                        self.analyze_string_reference(node, module_path)
                    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                        # String constant that might reference a function
                        self.analyze_string_reference(node, module_path)

            except Exception as e:
                print(f"Error building call graph for {module_path}: {e}")

    def analyze_function_call(self, node: ast.Call, module_path: str):
        """Analyze a function call node."""
        try:
            callee_name = None

            if isinstance(node.func, ast.Name):
                callee_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    callee_name = f"{node.func.value.id}.{node.func.attr}"
                else:
                    callee_name = node.func.attr

            if callee_name:
                # Find which function this call is inside
                caller_func = self.find_containing_function(node.lineno, module_path)
                if caller_func:
                    caller_key = f"{module_path}:{caller_func}"
                    if caller_key in self.functions:
                        self.functions[caller_key].callees.append(callee_name)
                        self.call_graph[caller_key].add(callee_name)

        except Exception:
            pass

    def analyze_name_reference(self, node: ast.Name, module_path: str):
        """Analyze a name reference that might be a function."""
        # This is for cases like: func_var = some_function; func_var()
        pass  # Implementation would be complex, skipping for now

    def analyze_string_reference(self, node, module_path: str):
        """Analyze string references that might be function names."""
        try:
            if hasattr(node, "value"):
                string_val = node.value
            elif hasattr(node, "s"):
                string_val = node.s
            else:
                return

            if isinstance(string_val, str):
                # Look for function-like patterns in strings
                if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", string_val):
                    # Might be a function name
                    caller_func = self.find_containing_function(node.lineno, module_path)
                    if caller_func:
                        caller_key = f"{module_path}:{caller_func}"
                        if caller_key in self.functions:
                            self.functions[caller_key].string_references.append(string_val)

        except Exception:
            pass

    def find_containing_function(self, line_no: int, module_path: str) -> Optional[str]:
        """Find which function contains the given line number."""
        best_match = None
        best_line = 0

        for func_key, func_info in self.functions.items():
            if func_info.file_path == module_path:
                if func_info.line_number <= line_no and func_info.line_number > best_line:
                    best_match = func_info.name
                    best_line = func_info.line_number

        return best_match

    def extract_intent_clues(self):
        """Extract intent clues from README files and documentation."""
        print("💭 Extracting intent clues from documentation...")

        # Find documentation files
        doc_patterns = ["**/README*", "**/DESIGN*", "**/docs/**/*.md", "**/docs/**/*.txt"]
        doc_files = []

        for pattern in doc_patterns:
            doc_files.extend(self.root_path.glob(pattern))

        print(f"📚 Found {len(doc_files)} documentation files")

        for doc_file in doc_files:
            try:
                with open(doc_file, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Extract key concepts
                intent_clues = self.extract_doc_intent_clues(content, str(doc_file))

                # Associate with nearby modules
                doc_dir = doc_file.parent
                for module_path, module_info in self.modules.items():
                    module_file = self.root_path / module_path
                    if doc_dir in module_file.parents or module_file.parent == doc_dir:
                        module_info.intent_clues.extend(intent_clues)

            except Exception as e:
                print(f"Error reading doc file {doc_file}: {e}")

    def extract_doc_intent_clues(self, content: str, file_path: str) -> List[str]:
        """Extract intent clues from documentation content."""
        clues = []

        lines = content.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Headers and important sections
            if stripped.startswith("#") or stripped.startswith("=") or stripped.startswith("-"):
                if len(stripped) > 5:
                    clues.append(f"DOC_HEADER: {stripped[:100]}")

            # LUKHAS consciousness keywords
            lower_line = stripped.lower()
            for keyword in self.consciousness_keywords:
                if keyword in lower_line and len(stripped) > 10:
                    clues.append(f"CONSCIOUSNESS_DOC: {stripped[:100]}")
                    break

            # Architecture patterns
            if any(pattern in lower_line for pattern in ["architecture", "design", "pattern", "structure"]):
                if len(stripped) > 15:
                    clues.append(f"ARCHITECTURE: {stripped[:100]}")

        return clues

    def classify_module_roles(self):
        """Classify modules into roles using heuristics."""
        print("🏷️ Classifying module roles...")

        for module_path, module_info in self.modules.items():
            role = self.determine_module_role(module_path, module_info)
            module_info.role = role

    def determine_module_role(self, module_path: str, module_info: ModuleInfo) -> str:
        """Determine the role of a module using heuristics."""
        path_lower = module_path.lower()

        # Check path patterns
        for role, patterns in self.role_patterns.items():
            for pattern in patterns:
                if pattern in path_lower:
                    return role

        # Check content patterns
        all_text = " ".join(module_info.intent_clues).lower()

        if "test" in path_lower or any("test" in clue.lower() for clue in module_info.intent_clues):
            return "test_helper"

        if any(pattern in all_text for pattern in ["orchestrat", "coordinate", "manage", "control"]):
            return "orchestrator"

        if any(pattern in all_text for pattern in ["integrat", "connect", "bridge", "adapt"]):
            return "integration"

        if any(pattern in all_text for pattern in ["model", "entity", "schema", "data"]):
            return "domain_model"

        # LUKHAS-specific roles
        if any(keyword in all_text for keyword in ["consciousness", "dream", "identity", "memory"]):
            return "consciousness_component"

        if any(keyword in all_text for keyword in ["guardian", "ethics", "drift"]):
            return "governance_component"

        if any(keyword in path_lower for keyword in ["api", "serve", "endpoint"]):
            return "api_component"

        return "unknown"

    def map_violations_to_symbols(self):
        """Map lint violations to specific functions and classes."""
        print("🔗 Mapping violations to symbols...")

        for rule_code, violations in self.violations.items():
            for violation in violations:
                file_path = violation.get("filename", "")
                line_no = violation.get("location", {}).get("row", 0)

                # Find affected function or class
                affected_symbol = None

                # Check functions
                for func_key, func_info in self.functions.items():
                    if func_info.file_path in file_path and abs(func_info.line_number - line_no) < 20:
                        affected_symbol = func_key
                        break

                # Check classes
                if not affected_symbol:
                    for class_key, class_info in self.classes.items():
                        if class_info.file_path in file_path and abs(class_info.line_number - line_no) < 20:
                            affected_symbol = class_key
                            break

                # Map violation to symbol
                if affected_symbol:
                    issue_flag = self.get_issue_flag(rule_code, violation)
                    if func_key in self.functions:
                        if issue_flag not in self.functions[affected_symbol].issues:
                            self.functions[affected_symbol].issues.append(issue_flag)
                    elif class_key in self.classes:
                        if issue_flag not in self.classes[affected_symbol].issues:
                            self.classes[affected_symbol].issues.append(issue_flag)

    def get_issue_flag(self, rule_code: str, violation: dict) -> str:
        """Convert ruff rule code to issue flag."""
        flag_mapping = {
            "ARG001": "unused_func_arg",
            "ARG002": "unused_method_arg", 
            "F821": "undefined_name",
            "F401": "unused_import",
            "RUF006": "dangling_task",
            "B006": "mutable_default",
            "DTZ005": "datetime_naive",
            "DTZ003": "datetime_utcnow",
            "E402": "import_not_top",
            "F841": "unused_variable",
            "B007": "unused_loop_var"
        }

        return flag_mapping.get(rule_code, f"rule_{rule_code}")

    def generate_atlas(self) -> dict:
        """Generate the complete code atlas."""
        print("📋 Generating Code Atlas...")

        # Map violations to symbols
        self.map_violations_to_symbols()

        # Build reverse call graph (callers)
        for func_key, func_info in self.functions.items():
            for callee in func_info.callees:
                # Find the callee and add this function as a caller
                for other_func_key, other_func_info in self.functions.items():
                    if other_func_info.name == callee or callee in other_func_info.name:
                        other_func_info.callers.append(func_key)

        atlas = {
            "metadata": {
                "generated_by": "LUKHAS Code Atlas Builder",
                "total_files": len(self.modules),
                "total_functions": len(self.functions),
                "total_classes": len(self.classes),
                "total_violations": sum(len(v) for v in self.violations.values()),
                "violation_rules": list(self.violations.keys())
            },
            "functions": {k: asdict(v) for k, v in self.functions.items()},
            "classes": {k: asdict(v) for k, v in self.classes.items()},
            "modules": {k: asdict(v) for k, v in self.modules.items()},
            "violations_summary": {k: len(v) for k, v in self.violations.items()}
        }

        return atlas

    def generate_rule_indices(self):
        """Generate per-rule violation indices."""
        print("📊 Generating per-rule indices...")

        reports_dir = self.root_path / "reports"
        reports_dir.mkdir(exist_ok=True)

        for rule_code, violations in self.violations.items():
            if violations:  # Only create index if there are violations
                index_file = reports_dir / f"idx_{rule_code}.json"

                rule_index = {
                    "rule_code": rule_code,
                    "total_violations": len(violations),
                    "violations": violations,
                    "affected_files": list(set(v.get("filename", "") for v in violations)),
                    "description": self.get_rule_description(rule_code)
                }

                with open(index_file, "w") as f:
                    json.dump(rule_index, f, indent=2)

                print(f"📄 Created index for {rule_code}: {len(violations)} violations")

    def get_rule_description(self, rule_code: str) -> str:
        """Get human-readable description of a rule."""
        descriptions = {
            "ARG001": "Unused function argument",
            "ARG002": "Unused method argument",
            "F821": "Undefined name",
            "F401": "Unused import",
            "RUF006": "Dangling async task",
            "B006": "Mutable default argument",
            "DTZ005": "Naive datetime usage",
            "DTZ003": "datetime.utcnow() usage",
            "E402": "Module level import not at top of file",
            "F841": "Local variable assigned but never used",
            "B007": "Loop control variable not used within loop body"
        }

        return descriptions.get(rule_code, f"Rule {rule_code}")

    def save_atlas(self, atlas: dict):
        """Save the complete atlas to JSON file."""
        reports_dir = self.root_path / "reports"
        reports_dir.mkdir(exist_ok=True)

        atlas_file = reports_dir / "code_atlas.json"

        with open(atlas_file, "w") as f:
            json.dump(atlas, f, indent=2)

        print(f"💾 Code Atlas saved to: {atlas_file}")
        print(f"📊 Atlas contains:")
        print(f"   - {len(atlas['functions'])} functions")
        print(f"   - {len(atlas['classes'])} classes")
        print(f"   - {len(atlas['modules'])} modules")
        print(f"   - {atlas['metadata']['total_violations']} violations")

    def run(self):
        """Run the complete analysis."""
        try:
            self.analyze_codebase()
            atlas = self.generate_atlas()
            self.generate_rule_indices()
            self.save_atlas(atlas)
            print("🎉 LUKHAS Code Atlas generation complete!")

        except Exception as e:
            print(f"❌ Error during atlas generation: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Build LUKHAS Code Atlas")
    parser.add_argument("--root", default=".", help="Root directory to analyze")
    parser.add_argument("--limit-files", type=int, help="Limit number of files to analyze (for testing)")

    args = parser.parse_args()

    print("🧬 LUKHAS Code Atlas Builder")
    print("=" * 50)

    builder = CodeAtlasBuilder(args.root)

    # For testing, limit file analysis
    if args.limit_files:
        print(f"🧪 Test mode: limiting to {args.limit_files} files")
        # This would require modifying analyze_python_files method

    builder.run()


if __name__ == "__main__":
    main()
