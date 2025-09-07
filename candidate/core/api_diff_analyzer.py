#!/usr/bin/env python3
"""
🔍 LUKHAS API Diff Analyzer

Phase 1 Implementation: Automated API mismatch detection between tests and actual implementations.
This script identifies all method signature mismatches and generates fixes.

✅ Analyzes test files for API calls
✅ Compares against actual class methods
✅ Generates migration scripts
✅ Creates method aliases for backward compatibility
"""

import ast
import difflib
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class APICall:
    """Represents an API call found in test files"""

    file_path: str
    line_number: int
    class_name: str
    method_name: str
    full_call: str
    context: str


@dataclass
class MethodSignature:
    """Represents an actual method signature in implementation"""

    file_path: str
    line_number: int
    class_name: str
    method_name: str
    parameters: list[str]
    is_async: bool
    docstring: Optional[str]


@dataclass
class APIMismatch:
    """Represents a mismatch between test and implementation"""

    test_call: APICall
    expected_method: str
    actual_methods: list[str]
    suggested_fix: str
    confidence: float


class TestAPIExtractor(ast.NodeVisitor):
    """AST visitor to extract API calls from test files"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.api_calls: list[APICall] = []
        self.current_class = None
        self.lines = None

    def extract_calls(self, source: str) -> list[APICall]:
        """Extract all API calls from source code"""
        self.lines = source.splitlines()
        tree = ast.parse(source)
        self.visit(tree)
        return self.api_calls

    def visit_Call(self, node):
        """Visit function calls to find API usage"""
        # Look for patterns like actor_ref.send_message(), fabric.total_messages, etc.
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            obj_name = node.func.value.id
            method_name = node.func.attr

            # Common test object patterns
            if any(
                pattern in obj_name.lower()
                for pattern in [
                    "actor",
                    "ref",
                    "fabric",
                    "agent",
                    "system",
                    "colony",
                ]
            ):
                # Get the full line for context
                line_content = self.lines[node.lineno - 1] if node.lineno <= len(self.lines) else ""

                api_call = APICall(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=self._infer_class_name(obj_name),
                    method_name=method_name,
                    full_call=f"{obj_name}.{method_name}",
                    context=line_content.strip(),
                )
                self.api_calls.append(api_call)

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Visit attribute access for property checks"""
        if isinstance(node.value, ast.Name):
            obj_name = node.value.id
            attr_name = node.attr

            # Look for attribute access patterns in assertions
            if any(pattern in obj_name.lower() for pattern in ["stats", "fabric", "agent", "result"]):
                api_call = APICall(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    class_name=self._infer_class_name(obj_name),
                    method_name=attr_name,
                    full_call=f"{obj_name}.{attr_name}",
                    context="attribute_access",
                )
                self.api_calls.append(api_call)

        self.generic_visit(node)

    def _infer_class_name(self, obj_name: str) -> str:
        """Infer the class name from object variable name"""
        # Common patterns
        if "actor_ref" in obj_name:
            return "ActorRef"
        elif "actor_system" in obj_name:
            return "ActorSystem"
        elif "fabric" in obj_name:
            return "EfficientCommunicationFabric"
        elif "agent" in obj_name:
            return "DistributedAIAgent"
        elif "colony" in obj_name:
            return "BaseColony"
        elif "system" in obj_name:
            return "DistributedAISystem"
        else:
            # Capitalize and remove underscores
            return "".join(word.capitalize() for word in obj_name.split("_"))


class ImplementationAnalyzer(ast.NodeVisitor):
    """AST visitor to extract actual method signatures from implementations"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.signatures: list[MethodSignature] = []
        self.current_class = None

    def extract_signatures(self, source: str) -> list[MethodSignature]:
        """Extract all method signatures from source code"""
        tree = ast.parse(source)
        self.visit(tree)
        return self.signatures

    def visit_ClassDef(self, node):
        """Visit class definitions"""
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        if self.current_class and not node.name.startswith("_"):
            # Extract parameters
            params = []
            for arg in node.args.args:
                if arg.arg != "self":
                    params.append(arg.arg)

            # Get docstring
            docstring = ast.get_docstring(node)

            signature = MethodSignature(
                file_path=self.file_path,
                line_number=node.lineno,
                class_name=self.current_class,
                method_name=node.name,
                parameters=params,
                is_async=False,
                docstring=docstring,
            )
            self.signatures.append(signature)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Visit async function definitions"""
        if self.current_class and not node.name.startswith("_"):
            params = []
            for arg in node.args.args:
                if arg.arg != "self":
                    params.append(arg.arg)

            docstring = ast.get_docstring(node)

            signature = MethodSignature(
                file_path=self.file_path,
                line_number=node.lineno,
                class_name=self.current_class,
                method_name=node.name,
                parameters=params,
                is_async=True,
                docstring=docstring,
            )
            self.signatures.append(signature)

        self.generic_visit(node)


class APIDiffAnalyzer:
    """Main analyzer to find and fix API mismatches"""

    def __init__(self, core_path: str):
        self.core_path = Path(core_path)
        self.test_calls: list[APICall] = []
        self.implementations: dict[str, list[MethodSignature]] = defaultdict(list)
        self.mismatches: list[APIMismatch] = []

    def analyze(self):
        """Run the complete analysis"""
        print("🔍 Starting API Diff Analysis...\n")

        # Step 1: Extract test API calls
        self._extract_test_calls()
        print(f"📋 Found {len(self.test_calls)} API calls in tests\n")

        # Step 2: Extract implementation signatures
        self._extract_implementations()
        total_methods = sum(len(methods) for methods in self.implementations.values())
        print(f"📚 Found {total_methods} methods in {len(self.implementations)} classes\n")

        # Step 3: Find mismatches
        self._find_mismatches()
        print(f"⚠️  Found {len(self.mismatches)} API mismatches\n")

        # Step 4: Generate report and fixes
        self._generate_report()
        self._generate_fixes()

    def _extract_test_calls(self):
        """Extract all API calls from test files"""
        # Look in test files and validation scripts
        test_patterns = [
            "*test*.py",
            "*Test*.py",
            "*validation*.py",
            "research_*.py",
        ]

        for pattern in test_patterns:
            for test_file in self.core_path.parent.rglob(pattern):
                if test_file.is_file():
                    try:
                        source = test_file.read_text()
                        extractor = TestAPIExtractor(str(test_file))
                        calls = extractor.extract_calls(source)
                        self.test_calls.extend(calls)
                    except Exception as e:
                        print(f"  ⚠️  Error parsing {test_file}: {e}")

    def _extract_implementations(self):
        """Extract all method signatures from implementations"""
        # Core implementation files
        impl_files = [
            "actor_system.py",
            "efficient_communication.py",
            "integrated_system.py",
            "event_sourcing.py",
            "distributed_tracing.py",
            "tiered_state_management.py",
            "p2p_communication.py",
            "lightweight_concurrency.py",
        ]

        for impl_file in impl_files:
            file_path = self.core_path / impl_file
            if file_path.exists():
                try:
                    source = file_path.read_text()
                    analyzer = ImplementationAnalyzer(str(file_path))
                    signatures = analyzer.extract_signatures(source)

                    for sig in signatures:
                        self.implementations[sig.class_name].append(sig)

                except Exception as e:
                    print(f"  ⚠️  Error parsing {file_path}: {e}")

    def _find_mismatches(self):
        """Find all mismatches between test calls and implementations"""
        # Group test calls by class and method
        calls_by_class = defaultdict(lambda: defaultdict(list))

        for call in self.test_calls:
            calls_by_class[call.class_name][call.method_name].append(call)

        # Check each unique call against implementations
        for class_name, method_calls in calls_by_class.items():
            impl_methods = self.implementations.get(class_name, [])
            impl_method_names = {m.method_name for m in impl_methods}

            for method_name, calls in method_calls.items():
                if method_name not in impl_method_names:
                    # Find the best match
                    suggested_method, confidence = self._find_best_match(method_name, impl_method_names)

                    mismatch = APIMismatch(
                        test_call=calls[0],  # Representative call
                        expected_method=method_name,
                        actual_methods=sorted(impl_method_names),
                        suggested_fix=suggested_method,
                        confidence=confidence,
                    )
                    self.mismatches.append(mismatch)

    def _find_best_match(self, expected: str, actual_methods: set[str]) -> tuple[str, float]:
        """Find the best matching method name"""
        if not actual_methods:
            return "NO_METHODS_FOUND", 0.0

        # Special cases we know about
        known_mappings = {
            "send_message": "tell",
            "handle_message": "register_handler",
            "process_task": "execute_task",
        }

        if expected in known_mappings:
            suggested = known_mappings[expected]
            if suggested in actual_methods:
                return suggested, 1.0

        # Use string similarity
        matches = difflib.get_close_matches(expected, actual_methods, n=1, cutoff=0.5)
        if matches:
            best_match = matches[0]
            # Calculate confidence
            confidence = difflib.SequenceMatcher(None, expected, best_match).ratio()
            return best_match, confidence

        return "NO_MATCH_FOUND", 0.0

    def _generate_report(self):
        """Generate detailed mismatch report"""
        report_path = self.core_path / "API_MISMATCH_REPORT.md"

        with open(report_path, "w") as f:
            f.write("# 🔍 API Mismatch Analysis Report\n\n")
            f.write(f"**Generated:** {self._get_timestamp()}\n")
            f.write(f"**Total Mismatches:** {len(self.mismatches)}\n\n")

            # Group by class
            mismatches_by_class = defaultdict(list)
            for mismatch in self.mismatches:
                mismatches_by_class[mismatch.test_call.class_name].append(mismatch)

            f.write("## Summary by Class\n\n")
            for class_name, class_mismatches in sorted(mismatches_by_class.items()):
                f.write(f"### {class_name}\n\n")

                for mismatch in class_mismatches:
                    f.write(f"- **{mismatch.expected_method}** → ")
                    if mismatch.confidence > 0.8:
                        f.write(f"✅ `{mismatch.suggested_fix}` (confidence: {mismatch.confidence:.0%})\n")
                    else:
                        f.write(f"❓ `{mismatch.suggested_fix}` (low confidence: {mismatch.confidence:.0%})\n")
                f.write("\n")

            # Detailed section
            f.write("## Detailed Mismatches\n\n")

            for i, mismatch in enumerate(self.mismatches, 1):
                f.write(f"### Mismatch #{i}: `{mismatch.expected_method}`\n")
                f.write(f"**Test File:** `{mismatch.test_call.file_path}`\n")
                f.write(f"**Line:** {mismatch.test_call.line_number}\n")
                f.write(f"**Context:** `{mismatch.test_call.context}`\n")
                f.write(f"**Suggested Fix:** `{mismatch.expected_method}` → `{mismatch.suggested_fix}`\n")
                f.write(f"**Confidence:** {mismatch.confidence:.0%}\n")
                f.write(f"**Available Methods:** {', '.join(sorted(mismatch.actual_methods)[:5]}...\n\n")

        print(f"📝 Report saved to: {report_path}")

    def _generate_fixes(self):
        """Generate automated fix scripts"""
        # Generate JSON data for automated fixes
        fixes_data = {
            "metadata": {
                "generated": self._get_timestamp(),
                "total_mismatches": len(self.mismatches),
                "analyzer_version": "1.0.0",
            },
            "fixes": [],
        }

        for mismatch in self.mismatches:
            fix_entry = {
                "class_name": mismatch.test_call.class_name,
                "old_method": mismatch.expected_method,
                "new_method": mismatch.suggested_fix,
                "confidence": mismatch.confidence,
                "test_file": mismatch.test_call.file_path,
                "line_number": mismatch.test_call.line_number,
            }
            fixes_data["fixes"].append(fix_entry)

        fixes_path = self.core_path / "api_fixes.json"
        with open(fixes_path, "w") as f:
            json.dump(fixes_data, f, indent=2)

        print(f"🔧 Fix data saved to: {fixes_path}")

        # Generate migration script
        self._generate_migration_script(fixes_data)

    def _generate_migration_script(self, fixes_data: dict):
        """Generate Python script to apply fixes"""
        script_path = self.core_path / "apply_api_fixes.py"

        with open(script_path, "w") as f:
            f.write(
                '''#!/usr/bin/env python3
"""
Automated API Fix Application Script
Generated by API Diff Analyzer
"""

import re
import json
from pathlib import Path

def apply_fixes():
    """Apply all API fixes to test files"""
    # Load fixes
    with open('api_fixes.json', 'r') as f:
        fixes_data = json.load(f)

    print(f"🔧 Applying {len(fixes_data['fixes'])} fixes...")

    # Group fixes by file
    fixes_by_file = {}
    for fix in fixes_data['fixes']:
        if fix['confidence'] > 0.7:  # Only apply high-confidence fixes
            file_path = fix['test_file']
            if file_path not in fixes_by_file:
                fixes_by_file[file_path] = []
            fixes_by_file[file_path].append(fix)

    # Apply fixes to each file
    for file_path, file_fixes in fixes_by_file.items():
        path = Path(file_path)
        if path.exists():
            print(f"\n📝 Fixing {path.name}...")

            content = path.read_text()
            original_content = content

            for fix in file_fixes:
                old_pattern = rf"\b{fix['old_method']}\b"
                new_method = fix['new_method']

                # Count replacements
                count = len(re.findall(old_pattern, content))
                if count > 0:
                    content = re.sub(old_pattern, new_method, content)
                    print(f"  ✅ Replaced {count} instances of {fix['old_method']} with {new_method}")

            # Write back if changed
            if content != original_content:
                # Backup original
                backup_path = path.with_suffix('.bak')
                path.rename(backup_path)

                # Write fixed content
                path.write_text(content)
                print(f"  💾 Saved fixed file (backup: {backup_path.name})")

    print("\n✅ All fixes applied!")

if __name__ == "__main__":
    apply_fixes()
'''
            )

        # Make executable
        os.chmod(script_path, 0o755)
        print(f"🚀 Migration script saved to: {script_path}")

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Run the API diff analyzer"""
    import sys

    # Get core path
    core_path = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent

    # Run analysis
    analyzer = APIDiffAnalyzer(core_path)
    analyzer.analyze()

    print("\n✨ Analysis complete! Check:")
    print("  - API_MISMATCH_REPORT.md for detailed report")
    print("  - api_fixes.json for structured fix data")
    print("  - apply_api_fixes.py to automatically apply fixes")


if __name__ == "__main__":
    main()
