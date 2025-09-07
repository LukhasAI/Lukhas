#!/usr/bin/env python3
"""
Enhanced AST-based acceptance gate for LUKHAS AI audit preparation.
Implements comprehensive import validation logic without execution.

This gate is designed for pre/post-MATRIZ workspace auditing:
- Scans ALL files under 'lukhas/' (the accepted lane)
- Blocks any import (static or dynamic) of candidate/, quarantine/, archive/
- Flags "facade" files (tiny wrappers that are mostly imports)
- Provides detailed audit trail for external reviewers

Exit code: 0 = pass, 2 = violations (ready for audit integration)
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys
from datetime import datetime, timezone
from typing import Any

REPO = pathlib.Path(__file__).resolve().parents[1]
ACCEPTED = REPO / "lukhas"
BANNED = ("candidate", "quarantine", "archive")


class AuditTrail:
    """Comprehensive audit trail for workspace validation."""

    def __init__(self):
        self.violations: list[dict[str, Any]] = []
        self.facades: list[dict[str, Any]] = []
        self.stats = {
            "files_scanned": 0,
            "total_imports": 0,
            "banned_imports": 0,
            "facade_files": 0,
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "scan_mode": "pre_matriz_audit",
        }

    def add_violation(self, file_path: str, violation_type: str, details: str, line_no: int | None = None):
        """Add import violation to audit trail."""
        self.violations.append(
            {
                "file": file_path,
                "type": violation_type,
                "details": details,
                "line": line_no,
                "severity": ("critical" if "import" in violation_type.lower() else "warning"),
            }
        )
        if "import" in violation_type.lower():
            self.stats["banned_imports"] += 1

    def add_facade(self, file_path: str, facade_score: float, import_count: int, total_lines: int):
        """Add facade file detection to audit trail."""
        self.facades.append(
            {
                "file": file_path,
                "facade_score": facade_score,
                "import_statements": import_count,
                "total_lines": total_lines,
                "risk_level": "high" if facade_score > 0.8 else "medium",
            }
        )
        self.stats["facade_files"] += 1

    def export_audit_report(self, output_path: pathlib.Path):
        """Export comprehensive audit report for external review."""
        report = {
            "audit_metadata": {
                "tool": "lukhas_ast_acceptance_gate",
                "version": "2.0.0-audit",
                "purpose": "pre_post_matriz_workspace_validation",
                "timestamp": self.stats["scan_timestamp"],
            },
            "scan_statistics": self.stats,
            "violations": self.violations,
            "facade_detections": self.facades,
            "compliance_status": {
                "accepts_ready": len(self.violations) == 0 and len(self.facades) == 0,
                "critical_issues": len([v for v in self.violations if v["severity"] == "critical"]),
                "warnings": len([v for v in self.violations if v["severity"] == "warning"]),
            },
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return report


def py_files(root: pathlib.Path):
    """Generator for Python files in accepted lane."""
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts or ".venv" in p.parts:
            continue
        yield p


class ImportScannerAST(ast.NodeVisitor):
    """Enhanced AST-based import scanner for audit preparation."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations = []
        self.imports = []
        self.from_imports = []
        self.dynamic_imports = []
        self.total_statements = 0

    def visit_Import(self, node):
        """Scan regular import statements."""
        for alias in node.names:
            module_name = alias.name or ""
            self.imports.append({"module": module_name, "line": node.lineno, "type": "import"})

            # Check for banned modules
            root_module = module_name.split(".")[0]
            if root_module in BANNED or any(module_name.startswith(b + ".") for b in BANNED):
                self.violations.append(
                    {
                        "type": "illegal_import",
                        "module": module_name,
                        "line": node.lineno,
                        "statement": f"import {module_name}",
                    }
                )

        self.total_statements += 1
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Scan from-import statements."""
        module = node.module or ""
        self.from_imports.append(
            {
                "module": module,
                "names": [n.name for n in node.names],
                "line": node.lineno,
                "type": "from_import",
            }
        )

        # Check for banned modules
        if module:
            root_module = module.split(".")[0]
            if root_module in BANNED or any(module.startswith(b + ".") for b in BANNED):
                names = ", ".join(n.name for n in node.names)
                self.violations.append(
                    {
                        "type": "illegal_from_import",
                        "module": module,
                        "names": names,
                        "line": node.lineno,
                        "statement": f"from {module} import {names}",
                    }
                )

        self.total_statements += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        """Scan dynamic import calls."""
        # Check for __import__ and importlib.import_module
        callee_name = ""
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            callee_name = node.func.attr

        if callee_name in {"__import__", "import_module"} and node.args:
            arg0 = node.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                module_name = arg0.value
                self.dynamic_imports.append(
                    {
                        "module": module_name,
                        "line": node.lineno,
                        "type": "dynamic_import",
                        "method": callee_name,
                    }
                )

                # Check for banned modules
                root_module = module_name.split(".")[0]
                if root_module in BANNED:
                    self.violations.append(
                        {
                            "type": "illegal_dynamic_import",
                            "module": module_name,
                            "line": node.lineno,
                            "method": callee_name,
                            "statement": f"{callee_name}('{module_name}')",
                        }
                    )

        self.generic_visit(node)


def analyze_facade_pattern(file_path: pathlib.Path, tree: ast.AST, source: str) -> tuple[bool, float, dict[str, Any]]:
    """
    Analyze file for facade pattern using multiple heuristics.
    Returns: (is_facade, facade_score, analysis_details)
    """
    lines = source.splitlines()
    total_lines = len([line for line in lines if line.strip()])

    if total_lines == 0:
        return False, 0.0, {"reason": "empty_file"}

    # Count different statement types
    import_count = 0
    assignment_count = 0
    function_count = 0
    class_count = 0
    other_count = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_count += 1
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            assignment_count += 1
        elif isinstance(node, ast.FunctionDef):
            function_count += 1
        elif isinstance(node, ast.ClassDef):
            class_count += 1
        elif isinstance(node, (ast.Expr, ast.If, ast.For, ast.While, ast.With, ast.Try)):
            other_count += 1

    # Calculate facade score based on multiple factors
    import_ratio = import_count / max(1, total_lines) if total_lines > 0 else 0
    code_complexity = function_count + class_count + other_count

    # Facade heuristics
    is_small = total_lines <= 40
    is_import_heavy = import_ratio > 0.6
    is_low_complexity = code_complexity <= 2
    has_banned_imports = any(node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))

    # Calculate composite facade score
    facade_score = 0.0
    if is_small:
        facade_score += 0.3
    if is_import_heavy:
        facade_score += 0.4
    if is_low_complexity:
        facade_score += 0.2
    if has_banned_imports:
        facade_score += 0.1

    analysis = {
        "total_lines": total_lines,
        "import_count": import_count,
        "import_ratio": import_ratio,
        "code_complexity": code_complexity,
        "is_small": is_small,
        "is_import_heavy": is_import_heavy,
        "is_low_complexity": is_low_complexity,
        "facade_score": facade_score,
    }

    is_facade = facade_score > 0.7  # Threshold for facade detection

    return is_facade, facade_score, analysis


def scan_file_comprehensive(file_path: pathlib.Path, audit: AuditTrail) -> dict[str, Any]:
    """Comprehensive file analysis for audit preparation."""
    rel_path = file_path.relative_to(REPO).as_posix()

    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(file_path))
    except Exception as e:
        audit.add_violation(rel_path, "parse_error", f"AST parse failed: {e}")
        return {"success": False, "error": str(e)}

    # Run import analysis
    scanner = ImportScannerAST(rel_path)
    scanner.visit(tree)

    audit.stats["files_scanned"] += 1
    audit.stats["total_imports"] += len(scanner.imports) + len(scanner.from_imports) + len(scanner.dynamic_imports)

    # Record violations
    for violation in scanner.violations:
        audit.add_violation(rel_path, violation["type"], violation["statement"], violation["line"])

    # Run facade analysis
    is_facade, facade_score, facade_details = analyze_facade_pattern(file_path, tree, source)

    if is_facade:
        audit.add_facade(
            rel_path,
            facade_score,
            facade_details["import_count"],
            facade_details["total_lines"],
        )

    return {
        "success": True,
        "imports": len(scanner.imports),
        "from_imports": len(scanner.from_imports),
        "dynamic_imports": len(scanner.dynamic_imports),
        "violations": len(scanner.violations),
        "is_facade": is_facade,
        "facade_score": facade_score,
    }


def main():
    """Main audit preparation logic - implements without execution."""
    if not ACCEPTED.exists():
        print(f"[audit-gate] '{ACCEPTED}' not found; nothing to scan.")
        sys.exit(0)

    print("[audit-gate] Starting comprehensive AST-based acceptance gate scan...")
    print(f"[audit-gate] Scanning accepted lane: {ACCEPTED}")
    print(f"[audit-gate] Banned imports: {', '.join(BANNED)}")

    audit = AuditTrail()

    # Scan all Python files in accepted lane
    for file_path in py_files(ACCEPTED):
        result = scan_file_comprehensive(file_path, audit)
        if not result["success"]:
            print(f"[audit-gate] ⚠️  Parse error in {file_path.relative_to(REPO)}")

    # Generate audit report
    report_path = REPO / "audit" / "acceptance_gate_audit.json"
    report_path.parent.mkdir(exist_ok=True)

    final_report = audit.export_audit_report(report_path)

    # Display results
    print("\n[audit-gate] 📊 Scan Results:")
    print(f"  Files scanned: {audit.stats['files_scanned']}")
    print(f"  Total imports: {audit.stats['total_imports']}")
    print(f"  Banned imports: {audit.stats['banned_imports']}")
    print(f"  Facade files: {audit.stats['facade_files']}")

    if audit.violations:
        print(f"\n❌ {len(audit.violations)} violations found:")
        for violation in audit.violations:
            print(f"  {violation['file']}:{violation.get('line', '?')} - {violation['details']}")
    else:
        print("\n✅ No import violations detected")

    if audit.facades:
        print(f"\n⚠️  {len(audit.facades)} facade files detected:")
        for facade in audit.facades:
            print(f"  {facade['file']} - score: {facade['facade_score']:.2f}")

    print(f"\n📋 Detailed audit report: {report_path}")
    print(f"🎯 Compliance status: {'READY' if final_report['compliance_status']['accepts_ready'] else 'NEEDS WORK'}")

    # Exit with appropriate code for CI integration
    exit_code = 0 if len(audit.violations) == 0 else 2
    print(f"[audit-gate] Exiting with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
