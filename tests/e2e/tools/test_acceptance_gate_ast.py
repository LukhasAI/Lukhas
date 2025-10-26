#!/usr/bin/env python3
"""
Comprehensive test suite for the AST-based acceptance gate tool.
Validates T4 quality standards for security vulnerability detection and audit compliance.

Test Coverage:
- AST parsing and import detection
- Security vulnerability detection (banned imports)
- Facade pattern detection
- Audit trail generation
- Compliance validation
- Error handling and edge cases

Author: LUKHAS AI Testing & DevOps Specialist (Agent #3 - Demis Hassabis Standard)
"""

import ast
import json
import tempfile
from pathlib import Path
from textwrap import dedent

import pytest
from tools.acceptance_gate_ast import (
    BANNED,
    AuditTrail,
    ImportScannerAST,
    analyze_facade_pattern,
    py_files,
    scan_file_comprehensive,
)


class TestAuditTrail:
    """Test audit trail functionality with comprehensive coverage."""

    def test_audit_trail_initialization(self):
        """Test audit trail proper initialization."""
        audit = AuditTrail()

        assert audit.violations == []
        assert audit.facades == []
        assert audit.stats["files_scanned"] == 0
        assert audit.stats["total_imports"] == 0
        assert audit.stats["banned_imports"] == 0
        assert audit.stats["facade_files"] == 0
        assert "scan_timestamp" in audit.stats
        assert audit.stats["scan_mode"] == "pre_matriz_audit"

    def test_add_violation_critical(self):
        """Test adding critical violations to audit trail."""
        audit = AuditTrail()

        audit.add_violation("test/file.py", "illegal_import", "from module import Something", line_no=5)

        assert len(audit.violations) == 1
        violation = audit.violations[0]
        assert violation["file"] == "test/file.py"
        assert violation["type"] == "illegal_import"
        assert violation["details"] == "from module import Something"
        assert violation["line"] == 5
        assert violation["severity"] == "critical"
        assert audit.stats["banned_imports"] == 1

    def test_add_violation_warning(self):
        """Test adding warning-level violations."""
        audit = AuditTrail()

        audit.add_violation("test/file.py", "parse_error", "Syntax error in file", line_no=10)

        violation = audit.violations[0]
        assert violation["severity"] == "warning"
        assert audit.stats["banned_imports"] == 0  # Only increments for imports

    def test_add_facade_detection(self):
        """Test facade detection logging."""
        audit = AuditTrail()

        audit.add_facade("test/facade.py", facade_score=0.85, import_count=15, total_lines=20)

        assert len(audit.facades) == 1
        facade = audit.facades[0]
        assert facade["file"] == "test/facade.py"
        assert facade["facade_score"] == 0.85
        assert facade["import_statements"] == 15
        assert facade["total_lines"] == 20
        assert facade["risk_level"] == "high"  # score > 0.8
        assert audit.stats["facade_files"] == 1

    def test_add_facade_medium_risk(self):
        """Test facade detection with medium risk score."""
        audit = AuditTrail()

        audit.add_facade("test/facade.py", 0.75, 10, 20)

        facade = audit.facades[0]
        assert facade["risk_level"] == "medium"  # score <= 0.8

    def test_export_audit_report(self):
        """Test comprehensive audit report generation."""
        audit = AuditTrail()

        # Add test data
        audit.add_violation("file1.py", "illegal_import", "import test", 5)
        audit.add_facade("file2.py", 0.9, 20, 25)
        audit.stats["files_scanned"] = 10
        audit.stats["total_imports"] = 50

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            report = audit.export_audit_report(temp_path)

            # Verify report structure
            assert "audit_metadata" in report
            assert report["audit_metadata"]["tool"] == "lukhas_ast_acceptance_gate"
            assert report["audit_metadata"]["version"] == "2.0.0-audit"
            assert report["audit_metadata"]["purpose"] == "pre_post_matriz_workspace_validation"

            assert "scan_statistics" in report
            assert report["scan_statistics"]["files_scanned"] == 10
            assert report["scan_statistics"]["total_imports"] == 50

            assert len(report["violations"]) == 1
            assert len(report["facade_detections"]) == 1

            assert "compliance_status" in report
            assert report["compliance_status"]["accepts_ready"] is False  # Has violations and facades
            assert report["compliance_status"]["critical_issues"] == 1
            assert report["compliance_status"]["warnings"] == 0

            # Verify file was written
            assert temp_path.exists()
            with open(temp_path) as f:
                saved_report = json.load(f)
            assert saved_report == report

        finally:
            temp_path.unlink(missing_ok=True)

    def test_compliance_status_ready(self):
        """Test compliance status when system is ready."""
        audit = AuditTrail()
        # No violations or facades added

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            report = audit.export_audit_report(temp_path)
            assert report["compliance_status"]["accepts_ready"] is True
            assert report["compliance_status"]["critical_issues"] == 0
            assert report["compliance_status"]["warnings"] == 0
        finally:
            temp_path.unlink(missing_ok=True)


class TestImportScannerAST:
    """Test AST-based import scanning functionality."""

    def test_scan_regular_import_allowed(self):
        """Test scanning of allowed regular imports."""
        code = "import os\nimport sys"
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert len(scanner.imports) == 2
        assert scanner.imports[0]["module"] == "os"
        assert scanner.imports[0]["line"] == 1
        assert scanner.imports[0]["type"] == "import"
        assert scanner.imports[1]["module"] == "sys"
        assert scanner.imports[1]["line"] == 2
        assert len(scanner.violations) == 0

    def test_scan_regular_import_banned(self):
        """Test detection of banned regular imports."""
        code = "import module\nimport quarantine.test"
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert len(scanner.imports) == 2
        assert len(scanner.violations) == 2

        violation1 = scanner.violations[0]
        assert violation1["type"] == "illegal_import"
        assert violation1["module"] == "labs.module"
        assert violation1["line"] == 1
        assert violation1["statement"] == "import module"

        violation2 = scanner.violations[1]
        assert violation2["type"] == "illegal_import"
        assert violation2["module"] == "quarantine.test"
        assert violation2["line"] == 2

    def test_scan_from_import_allowed(self):
        """Test scanning of allowed from-imports."""
        code = "from pathlib import Path\nfrom typing import List"
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert len(scanner.from_imports) == 2
        assert scanner.from_imports[0]["module"] == "pathlib"
        assert scanner.from_imports[0]["names"] == ["Path"]
        assert scanner.from_imports[0]["line"] == 1
        assert scanner.from_imports[1]["names"] == ["List"]
        assert len(scanner.violations) == 0

    def test_scan_from_import_banned(self):
        """Test detection of banned from-imports."""
        code = "from core import Module\nfrom archive.old import Legacy"
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert len(scanner.violations) == 2

        violation1 = scanner.violations[0]
        assert violation1["type"] == "illegal_from_import"
        assert violation1["module"] == "labs.core"
        assert violation1["names"] == "Module"
        assert violation1["statement"] == "from core import Module"

        violation2 = scanner.violations[1]
        assert violation2["module"] == "archive.old"

    def test_scan_from_import_multiple_names(self):
        """Test from-import with multiple names."""
        code = "from test import Module1, Module2, Module3"
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert len(scanner.violations) == 1
        violation = scanner.violations[0]
        assert violation["names"] == "Module1, Module2, Module3"

    def test_scan_dynamic_import_allowed(self):
        """Test dynamic import scanning for allowed modules."""
        code = "__import__('pathlib')\nimportlib.import_module('typing')"
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert len(scanner.dynamic_imports) == 2
        assert scanner.dynamic_imports[0]["module"] == "pathlib"
        assert scanner.dynamic_imports[0]["method"] == "__import__"
        assert scanner.dynamic_imports[0]["line"] == 1
        assert scanner.dynamic_imports[1]["module"] == "typing"
        assert scanner.dynamic_imports[1]["method"] == "import_module"
        assert len(scanner.violations) == 0

    def test_scan_dynamic_import_banned(self):
        """Test detection of banned dynamic imports."""
        code = "__import__('candidate.test')\nimportlib.import_module('quarantine.module')"
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert len(scanner.violations) == 2

        violation1 = scanner.violations[0]
        assert violation1["type"] == "illegal_dynamic_import"
        assert violation1["module"] == "labs.test"
        assert violation1["method"] == "__import__"
        assert violation1["statement"] == "__import__('candidate.test')"

        violation2 = scanner.violations[1]
        assert violation2["module"] == "quarantine.module"
        assert violation2["method"] == "import_module"

    def test_scan_nested_banned_imports(self):
        """Test detection of nested banned imports."""
        code = "import core.module\nfrom quarantine.old.legacy import Item"
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert len(scanner.violations) == 2
        assert scanner.violations[0]["module"] == "labs.core.module"
        assert scanner.violations[1]["module"] == "quarantine.old.legacy"

    def test_statement_counting(self):
        """Test statement counting for analysis."""
        code = dedent(
            """
            import os
            from pathlib import Path
            x = 1
            def func(): pass
        """
        ).strip()
        tree = ast.parse(code)

        scanner = ImportScannerAST("test.py")
        scanner.visit(tree)

        assert scanner.total_statements == 2  # Only import statements counted


class TestFacadePatternAnalysis:
    """Test facade pattern detection with comprehensive coverage."""

    def test_analyze_empty_file(self):
        """Test facade analysis of empty file."""
        code = ""
        tree = ast.parse(code)

        is_facade, score, analysis = analyze_facade_pattern(Path("test.py"), tree, code)

        assert is_facade is False
        assert score == 0.0
        assert analysis["reason"] == "empty_file"

    def test_analyze_small_import_heavy_file(self):
        """Test facade detection for small, import-heavy files."""
        code = dedent(
            """
            import os
            import sys
            from pathlib import Path
            from typing import List, Dict

            # Simple wrapper
            def get_path(): return Path(".")
        """
        ).strip()
        tree = ast.parse(code)

        is_facade, score, analysis = analyze_facade_pattern(Path("test.py"), tree, code)

        # Should be detected as facade (small + import-heavy + low complexity)
        assert is_facade is True
        assert score > 0.7
        assert analysis["is_small"] is True
        assert analysis["is_import_heavy"] is True
        assert analysis["is_low_complexity"] is True
        assert analysis["import_count"] == 4

    def test_analyze_complex_file_not_facade(self):
        """Test that complex files are not flagged as facades."""
        code = dedent(
            """
            import os
            from pathlib import Path

            class ComplexProcessor:
                def __init__(self):
                    self.data = {}

                def process(self, input_data):
                    result = []
                    for item in input_data:
                        if self.validate(item):
                            result.append(self.transform(item))
                    return result

                def validate(self, item):
                    return item is not None

                def transform(self, item):
                    return str(item).upper()

            def main():
                processor = ComplexProcessor()
                data = [1, 2, 3, None, 4]
                result = processor.process(data)
                print(result)

            if __name__ == "__main__":
                main()
        """
        ).strip()
        tree = ast.parse(code)

        is_facade, score, analysis = analyze_facade_pattern(Path("test.py"), tree, code)

        # Should NOT be detected as facade (high complexity)
        assert is_facade is False
        assert score <= 0.7
        assert analysis["is_low_complexity"] is False
        assert analysis["code_complexity"] > 2

    def test_analyze_medium_facade_score(self):
        """Test facade with medium score (around threshold)."""
        code = dedent(
            """
            import os
            from pathlib import Path

            # Moderate complexity
            def simple_func():
                return "hello"

            class SimpleClass:
                pass
        """
        ).strip()
        tree = ast.parse(code)

        is_facade, score, analysis = analyze_facade_pattern(Path("test.py"), tree, code)

        # Should be close to threshold
        assert 0.4 <= score <= 0.8
        assert analysis["import_count"] == 2

    def test_facade_scoring_factors(self):
        """Test individual facade scoring factors."""
        # Test small file factor
        small_code = "import os\nprint('hello')"
        tree = ast.parse(small_code)
        _, score, analysis = analyze_facade_pattern(Path("test.py"), tree, small_code)
        assert analysis["is_small"] is True

        # Test import-heavy factor
        import_heavy_code = "\n".join([f"import mod{i}" for i in range(10)])
        tree = ast.parse(import_heavy_code)
        _, score, analysis = analyze_facade_pattern(Path("test.py"), tree, import_heavy_code)
        assert analysis["is_import_heavy"] is True
        assert analysis["import_ratio"] > 0.6


class TestFileScanComprehensive:
    """Test comprehensive file scanning functionality."""

    def test_scan_file_success(self):
        """Test successful file scanning."""
        code = dedent(
            """
            import os
            from pathlib import Path

            def main():
                return Path(".")
        """
        ).strip()

        # Create test file in repository directory to avoid path issues
        test_dir = Path(__file__).parent.parent.parent / "tests" / "tools"
        temp_path = test_dir / "temp_test_file.py"

        try:
            temp_path.write_text(code)
            audit = AuditTrail()
            result = scan_file_comprehensive(temp_path, audit)

            assert result["success"] is True
            assert result["imports"] == 1
            assert result["from_imports"] == 1
            assert result["dynamic_imports"] == 0
            assert result["violations"] == 0
            assert result["is_facade"] is False  # Small but not import-heavy enough

            assert audit.stats["files_scanned"] == 1
            assert audit.stats["total_imports"] == 2

        finally:
            temp_path.unlink(missing_ok=True)

    def test_scan_file_with_violations(self):
        """Test file scanning with banned imports."""
        code = dedent(
            """
            import module
            from quarantine.test import Item
            __import__('archive.legacy')

            def test(): pass
        """
        ).strip()

        # Create test file in repository directory
        test_dir = Path(__file__).parent.parent.parent / "tests" / "tools"
        temp_path = test_dir / "temp_violations_file.py"

        try:
            temp_path.write_text(code)
            audit = AuditTrail()
            result = scan_file_comprehensive(temp_path, audit)

            assert result["success"] is True
            assert result["violations"] == 3
            assert len(audit.violations) == 3
            assert audit.stats["banned_imports"] == 3

        finally:
            temp_path.unlink(missing_ok=True)

    def test_scan_file_facade_detected(self):
        """Test file scanning with facade detection."""
        code = dedent(
            """
            import os
            import sys
            from pathlib import Path
            from typing import List
            from collections import defaultdict

            # Tiny wrapper
            get_path = Path
        """
        ).strip()

        # Create test file in repository directory
        test_dir = Path(__file__).parent.parent.parent / "tests" / "tools"
        temp_path = test_dir / "temp_facade_file.py"

        try:
            temp_path.write_text(code)
            audit = AuditTrail()
            result = scan_file_comprehensive(temp_path, audit)

            assert result["success"] is True
            assert result["is_facade"] is True
            assert len(audit.facades) == 1
            assert audit.stats["facade_files"] == 1

        finally:
            temp_path.unlink(missing_ok=True)

    def test_scan_file_parse_error(self):
        """Test handling of file with parse errors."""
        invalid_code = "def invalid_syntax(\n  missing closing paren"

        # Create test file in repository directory
        test_dir = Path(__file__).parent.parent.parent / "tests" / "tools"
        temp_path = test_dir / "temp_parse_error_file.py"

        try:
            temp_path.write_text(invalid_code)
            audit = AuditTrail()
            result = scan_file_comprehensive(temp_path, audit)

            assert result["success"] is False
            assert "error" in result
            assert len(audit.violations) == 1
            assert audit.violations[0]["type"] == "parse_error"

        finally:
            temp_path.unlink(missing_ok=True)


class TestPyFilesGenerator:
    """Test Python file discovery functionality."""

    def test_py_files_discovery(self):
        """Test Python file discovery in directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "test1.py").write_text("# test1")
            (temp_path / "test2.py").write_text("# test2")
            (temp_path / "not_python.txt").write_text("not python")

            # Create subdirectory
            sub_dir = temp_path / "subdir"
            sub_dir.mkdir()
            (sub_dir / "test3.py").write_text("# test3")

            # Create __pycache__ (should be ignored)
            pycache = temp_path / "__pycache__"
            pycache.mkdir()
            (pycache / "cached.py").write_text("# cached")

            files = list(py_files(temp_path))
            file_names = [f.name for f in files]

            assert "test1.py" in file_names
            assert "test2.py" in file_names
            assert "test3.py" in file_names
            assert "not_python.txt" not in file_names
            assert "cached.py" not in file_names
            assert len(files) == 3

    def test_py_files_empty_directory(self):
        """Test file discovery in empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            files = list(py_files(temp_path))
            assert len(files) == 0

    def test_py_files_venv_ignored(self):
        """Test that .venv directories are ignored."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create .venv directory (should be ignored)
            venv_dir = temp_path / ".venv"
            venv_dir.mkdir()
            (venv_dir / "ignored.py").write_text("# ignored")

            # Create regular file
            (temp_path / "regular.py").write_text("# regular")

            files = list(py_files(temp_path))
            file_names = [f.name for f in files]

            assert "regular.py" in file_names
            assert "ignored.py" not in file_names
            assert len(files) == 1


class TestBannedImportConfiguration:
    """Test banned import configuration is correct."""

    def test_banned_modules_defined(self):
        """Test that banned modules are properly defined."""
        assert "labs" in BANNED
        assert "quarantine" in BANNED
        assert "archive" in BANNED
        assert len(BANNED) == 3

    def test_banned_modules_detection(self):
        """Test banned module detection logic."""
        # Test direct matches
        assert "labs" in BANNED
        assert "quarantine" in BANNED
        assert "archive" in BANNED

        # Test allowed modules
        assert "lukhas" not in BANNED
        assert "core" not in BANNED
        assert "pathlib" not in BANNED


@pytest.mark.integration
class TestAcceptanceGateIntegration:
    """Integration tests for the acceptance gate system."""

    def test_integration_audit_trail_with_scanner(self):
        """Test integration between audit trail and scanner."""
        code = dedent(
            """
            import os
            import test
            from quarantine.old import Item

            def simple(): pass
        """
        ).strip()

        # Create test file in repository directory
        test_dir = Path(__file__).parent.parent.parent / "tests" / "tools"
        temp_path = test_dir / "temp_integration_file.py"

        try:
            temp_path.write_text(code)
            audit = AuditTrail()
            result = scan_file_comprehensive(temp_path, audit)

            # Verify integration
            assert result["success"] is True
            assert result["violations"] == 2
            assert audit.stats["banned_imports"] == 2
            assert len(audit.violations) == 2

            # Verify violation details
            violation_types = [v["type"] for v in audit.violations]
            assert "illegal_import" in violation_types
            assert "illegal_from_import" in violation_types

        finally:
            temp_path.unlink(missing_ok=True)


@pytest.mark.security
class TestSecurityValidation:
    """Security-focused tests for the acceptance gate."""

    def test_security_banned_import_detection(self):
        """Test comprehensive security validation of banned imports."""
        security_test_cases = [
            ("import core", True),
            ("from security import Auth", True),
            ("import core.sensitive.data", True),
            ("__import__('quarantine.module')", True),
            ("importlib.import_module('archive.legacy')", True),
            ("import core", False),
            ("from pathlib import Path", False),
            ("import os", False),
        ]

        for code, should_be_banned in security_test_cases:
            tree = ast.parse(code)
            scanner = ImportScannerAST("test.py")
            scanner.visit(tree)

            has_violations = len(scanner.violations) > 0
            assert has_violations == should_be_banned, f"Failed for: {code}"

    def test_security_audit_completeness(self):
        """Test that security audit captures all required information."""
        audit = AuditTrail()

        # Add various security violations
        audit.add_violation("file1.py", "illegal_import", "import core", 1)
        audit.add_violation("file2.py", "illegal_from_import", "from quarantine import Old", 5)
        audit.add_violation("file3.py", "illegal_dynamic_import", "__import__('archive.data')", 10)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            report = audit.export_audit_report(temp_path)

            # Verify security audit completeness
            assert report["compliance_status"]["critical_issues"] == 3
            assert len(report["violations"]) == 3

            # Verify all violations have required security fields
            for violation in report["violations"]:
                assert "file" in violation
                assert "type" in violation
                assert "details" in violation
                assert "line" in violation
                assert "severity" in violation

        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
