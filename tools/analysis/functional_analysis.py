#!/usr/bin/env python3
"""
 Functional Analysis - Identify what actually WORKS vs what's just connected
Analyzes functional capabilities, dependencies, and operational readiness
"""

import ast
import json
import re
from pathlib import Path


class FunctionalAnalyzer:
    def __init__(self):
        self.functional_systems = {}
        self.broken_dependencies = {}
        self.capability_map = {}
        self.entry_points = {}
        self.critical_missing = []

    def analyze_functional_capability(self, file_path):
        """Analyze if a file has actual functional capability vs just imports/stubs"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                return {"type": "empty", "functional": False}

            try:
                tree = ast.parse(content)
            except SyntaxError:
                return {"type": "syntax_error", "functional": False}

            analysis = {
                "classes": [],
                "functions": [],
                "imports": [],
                "main_block": False,
                "decorators": [],
                "functional": False,
                "type": "unknown",
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    analysis["classes"].append(
                        {
                            "name": node.name,
                            "methods": methods,
                            "has_init": "__init__" in methods,
                            "method_count": len(methods),
                        }
                    )

                elif isinstance(node, ast.FunctionDef):
                    if node.name not in ["__init__", "__str__", "__repr__"]:
                        analysis["functions"].append(
                            {
                                "name": node.name,
                                "args": len(node.args.args),
                                "has_docstring": ast.get_docstring(node) is not None,
                                "decorators": [
                                    d.id if isinstance(d, ast.Name) else str(d)
                                    for d in node.decorator_list
                                ],
                            }
                        )

                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis["imports"].append(alias.name)
                    else:
                        if node.module:
                            analysis["imports"].append(node.module)

                elif isinstance(node, ast.If) and (
                    isinstance(node.test, ast.Compare)
                    and isinstance(node.test.left, ast.Name)
                    and node.test.left.id == "__name__"
                ):
                    analysis["main_block"] = True

            # Determine functionality
            has_substantial_classes = any(c["method_count"] > 2 for c in analysis["classes"])
            has_substantial_functions = len(analysis["functions"]) > 1
            has_main = analysis["main_block"]

            if has_substantial_classes or has_substantial_functions or has_main:
                analysis["functional"] = True
                if has_main:
                    analysis["type"] = "executable"
                elif has_substantial_classes:
                    analysis["type"] = "class_module"
                else:
                    analysis["type"] = "function_module"
            else:
                analysis["type"] = "import_only" if analysis["imports"] else "stub"

            return analysis

        except Exception as e:
            return {"type": "error", "functional": False, "error": str(e)}

    def check_missing_dependencies(self, file_path, imports):
        """Check if imported modules actually exist and are functional"""
        missing = []
        broken = []

        base_dir = Path(file_path).parent

        for imp in imports:
            if imp.startswith("."):
                # Relative import
                continue
            elif "." in imp:
                # Package import
                parts = imp.split(".")
                possible_paths = [
                    base_dir / f"{parts[0]}.py",
                    base_dir / parts[0] / "__init__.py",
                    Path(file_path).parent.parent / f"{parts[0]}.py",
                    Path(file_path).parent.parent / parts[0] / "__init__.py",
                ]

                found = False
                for path in possible_paths:
                    if path.exists():
                        found = True
                        # Check if it's functional
                        dep_analysis = self.analyze_functional_capability(path)
                        if not dep_analysis["functional"]:
                            broken.append(imp)
                        break

                if not found:
                    missing.append(imp)
            else:
                # Single module import
                if imp not in [
                    "os",
                    "sys",
                    "json",
                    "datetime",
                    "pathlib",
                    "re",
                    "collections",
                    "itertools",
                    "functools",
                    "typing",
                ]:
                    # Check local modules
                    possible_paths = [
                        base_dir / f"{imp}.py",
                        base_dir / imp / "__init__.py",
                    ]

                    found = False
                    for path in possible_paths:
                        if path.exists():
                            found = True
                            break

                    if not found:
                        missing.append(imp)

        return missing, broken

    def identify_system_capabilities(self):
        """Identify what each system can actually DO"""
        capabilities = {
            "consciousness": self.scan_for_capabilities(
                "consciousness",
                ["decision_making", "awareness", "state_management", "cognitive"],
            ),
            "memory": self.scan_for_capabilities(
                "memory", ["storage", "retrieval", "association", "learning", "recall"]
            ),
            "identity": self.scan_for_capabilities(
                "identity", ["formation", "validation", "authentication", "profile"]
            ),
            "bio": self.scan_for_capabilities(
                "bio", ["adaptation", "homeostasis", "signal", "endocrine", "synthesis"]
            ),
            "quantum": self.scan_for_capabilities(
                "quantum",
                ["processing", "entanglement", "superposition", "measurement"],
            ),
            "emotion": self.scan_for_capabilities(
                "emotion", ["processing", "response", "modeling", "regulation"]
            ),
            "orchestration": self.scan_for_capabilities(
                "orchestration",
                ["coordination", "workflow", "integration", "management"],
            ),
            "api": self.scan_for_capabilities(
                "api", ["endpoint", "service", "controller", "interface"]
            ),
            "security": self.scan_for_capabilities(
                "security",
                ["authentication", "authorization", "encryption", "compliance"],
            ),
        }

        return capabilities

    def scan_for_capabilities(self, system_name, capability_keywords):
        """Scan a system directory for specific capabilities"""
        system_path = Path(system_name)
        if not system_path.exists():
            return {"status": "missing", "capabilities": []}

        capabilities = []
        files_scanned = 0
        functional_files = 0

        for py_file in system_path.rglob("*.py"):
            files_scanned += 1
            analysis = self.analyze_functional_capability(py_file)

            if analysis["functional"]:
                functional_files += 1

                # Check for capability keywords in file name and content
                file_content = py_file.read_text(encoding="utf-8", errors="ignore").lower()
                file_name = py_file.name.lower()

                for keyword in capability_keywords:
                    if keyword in file_name or len(re.findall(rf"\b{keyword}\b", file_content)) > 2:
                        capabilities.append(
                            {
                                "capability": keyword,
                                "file": str(py_file),
                                "confidence": ("high" if keyword in file_name else "medium"),
                            }
                        )

        return {
            "status": "functional" if functional_files > 0 else "non_functional",
            "files_scanned": files_scanned,
            "functional_files": functional_files,
            "capabilities": capabilities,
            "functionality_ratio": (functional_files / files_scanned if files_scanned > 0 else 0),
        }

    def find_entry_points(self):
        """Find actual executable entry points"""
        entry_points = {}

        # Look for main.py files
        for main_file in Path(".").rglob("main.py"):
            analysis = self.analyze_functional_capability(main_file)
            if analysis["main_block"]:
                entry_points[str(main_file)] = {
                    "type": "main_executable",
                    "functional": analysis["functional"],
                }

        # Look for files with if __name__ == "__main__"
        for py_file in Path(".").rglob("*.py"):
            if py_file.name != "main.py":
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    if 'if __name__ == "__main__"' in content:
                        analysis = self.analyze_functional_capability(py_file)
                        entry_points[str(py_file)] = {
                            "type": "script_executable",
                            "functional": analysis["functional"],
                        }
                except BaseException:
                    continue

        return entry_points


def main():
    print("🔍  Functional Analysis - Scanning for actual working capabilities...")

    analyzer = FunctionalAnalyzer()

    # Identify system capabilities
    print("📊 Analyzing system capabilities...")
    capabilities = analyzer.identify_system_capabilities()

    # Find entry points
    print("🚀 Finding executable entry points...")
    entry_points = analyzer.find_entry_points()

    # Analyze critical files
    print("⚙️ Analyzing critical system files...")
    critical_analysis = {}

    for system in [
        "consciousness",
        "memory",
        "identity",
        "bio",
        "orchestration",
        "api",
        "core",
    ]:
        if Path(system).exists():
            critical_analysis[system] = analyzer.scan_for_capabilities(
                system, ["init", "main", "core", "engine", "manager", "controller"]
            )

    # Generate report
    report = {
        "timestamp": str(Path.cwd()),
        "system_capabilities": capabilities,
        "entry_points": entry_points,
        "critical_analysis": critical_analysis,
        "summary": {
            "functional_systems": len(
                [s for s in capabilities.values() if s["status"] == "functional"]
            ),
            "total_systems": len(capabilities),
            "executable_entry_points": len([e for e in entry_points.values() if e["functional"]]),
            "total_entry_points": len(entry_points),
        },
    }

    # Save detailed report
    with open("_FUNCTIONAL_ANALYSIS_REPORT.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("🎯  FUNCTIONAL CAPABILITY ANALYSIS")
    print("=" * 60)

    print("\n📊 SYSTEM STATUS:")
    for system, data in capabilities.items():
        status_emoji = (
            "✅" if data["status"] == "functional" else "❌" if data["status"] == "missing" else "⚠️"
        )
        if data["status"] != "missing":
            ratio = f" ({data['functionality_ratio']:.1%} functional)"
        else:
            ratio = ""
        print(f"   {status_emoji} {system}: {data['status']}{ratio}")

        if data["capabilities"]:
            print(f"      Capabilities: {len(data['capabilities'])} identified")
            for cap in data["capabilities"][:3]:  # Show top 3
                print(f"        • {cap['capability']} ({cap['confidence']})")

    print(f"\n🚀 EXECUTABLE ENTRY POINTS ({len(entry_points)}):")
    for path, data in entry_points.items():
        status_emoji = "✅" if data["functional"] else "❌"
        print(f"   {status_emoji} {path} ({data['type']})")

    print("\n📋 Report saved to _FUNCTIONAL_ANALYSIS_REPORT.json")


if __name__ == "__main__":
    main()
