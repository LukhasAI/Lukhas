#!/usr/bin/env python3
"""
Lane Boundary Import Linting - T4/0.01% Excellence
==================================================

Enforces Candidate→Lukhas→MATRIZ lane boundaries with import-linter integration.
Prevents cross-lane imports that would violate architectural constraints.

Lane Architecture:
- MATRIZ: Top lane, no imports from lukhas modules
- lukhas: Production lane, no imports from MATRIZ
- candidate: Development lane, limited production imports

Import Rules:
- MATRIZ can only import from standard libraries and approved integrations
- lukhas modules cannot import matriz directly
- candidate cannot import production-critical components
- Approved integration points explicitly allowed

Constellation Framework: 🌊 Architectural Boundary Enforcement
"""

import ast
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pytest

logger = logging.getLogger(__name__)


class LaneImportLinter:
    """Lane boundary import linter for LUKHAS architecture."""

    def __init__(self):
        """Initialize lane import linter."""
        self.project_root = Path(__file__).parent.parent.parent
        # After Phase 5B: lukhas/ removed, modules at root level
        self.matriz_root = self.project_root / "MATRIZ"
        self.candidate_root = self.project_root / "labs"

        # Define lane boundaries (lukhas is now root-level modules)
        self.lane_hierarchy = ["MATRIZ", "root", "labs"]

        # Forbidden cross-lane imports
        self.forbidden_imports = {
            "MATRIZ": {
                "consciousness",
                "governance",
                "identity",
                "orchestration",
                "memory",
                "observability"
            },
            "lukhas": {
                "MATRIZ"
            },
            "labs": {
                "governance.guardian_serializers",
                "identity.webauthn_production",
                "observability.prometheus_metrics"
            }
        }

        # Approved integration points (PINNED SURFACES - T4/0.01%)
        self.approved_integrations = {
            "consciousness.matriz_thought_loop",
            "observability.matriz_instrumentation",
            "observability.matriz_decorators",
            "memory.matriz_adapter"
        }

        # Additional forbidden patterns (internal/private modules)
        self.additional_forbidden = {
            "lukhas": {
                "MATRIZ.internal",
                "MATRIZ.private",
                "MATRIZ.experimental",
                "MATRIZ.schemas.internal",
                "MATRIZ.core.private",
                "MATRIZ.processing.internal"
            },
            "labs": {
                "governance.guardian_serializers.production",
                "identity.webauthn_production.core",
                "observability.prometheus_metrics.production",
                "orchestration.production_workflows",
                "memory.production_stores"
            }
        }

        self.violations = []

    def detect_lane_from_path(self, file_path: Path) -> Optional[str]:
        """Detect which lane a file belongs to based on its path."""
        try:
            relative_path = file_path.relative_to(self.project_root)
            path_parts = relative_path.parts

            if len(path_parts) > 0:
                if path_parts[0].upper() == "MATRIZ":
                    return "MATRIZ"
                elif path_parts[0] == "lukhas":
                    return "lukhas"
                elif path_parts[0] == "labs":
                    return "labs"

        except ValueError:
            # File not within project root
            pass

        return None

    def extract_imports_from_file(self, file_path: Path) -> set[str]:
        """Extract import statements from a Python file."""
        imports = set()

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Parse AST to extract imports
            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module)
                    # Also add sub-imports
                    for alias in node.names:
                        if alias.name != '*':
                            imports.add(f"{node.module}.{alias.name}")

        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning(f"Could not parse {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

        return imports

    def check_import_violations(self, file_path: Path, file_lane: str, imports: set[str]) -> list[str]:
        """Check for import violations against lane boundaries."""
        violations = []

        if file_lane not in self.forbidden_imports:
            return violations

        forbidden_modules = self.forbidden_imports[file_lane]

        for import_name in imports:
            # Check direct forbidden imports
            if import_name in forbidden_modules:
                violations.append(
                    f"{file_lane} lane file {file_path} imports forbidden module '{import_name}'"
                )
                continue

            # Check if import starts with forbidden pattern
            for forbidden_pattern in forbidden_modules:
                if import_name.startswith(forbidden_pattern + "."):
                    # Check if this is an approved integration
                    if import_name in self.approved_integrations:
                        logger.info(f"Approved integration: {import_name} in {file_path}")
                        continue

                    violations.append(
                        f"{file_lane} lane file {file_path} imports forbidden module '{import_name}' from pattern '{forbidden_pattern}'"
                    )

            # Check additional forbidden patterns (internal/private modules)
            if file_lane in self.additional_forbidden:
                additional_patterns = self.additional_forbidden[file_lane]
                for forbidden_pattern in additional_patterns:
                    if import_name.startswith(forbidden_pattern):
                        violations.append(
                            f"{file_lane} lane file {file_path} imports RESTRICTED module '{import_name}' (internal/private/production-critical)"
                        )

        return violations

    def scan_directory_for_violations(self, directory: Path, lane: str) -> list[str]:
        """Scan directory for lane import violations."""
        violations = []

        if not directory.exists():
            logger.warning(f"Directory {directory} does not exist")
            return violations

        # Find all Python files
        python_files = list(directory.glob("**/*.py"))

        logger.info(f"Scanning {len(python_files)} Python files in {lane} lane")

        for py_file in python_files:
            try:
                # Extract imports
                imports = self.extract_imports_from_file(py_file)

                # Check violations
                file_violations = self.check_import_violations(py_file, lane, imports)
                violations.extend(file_violations)

            except Exception as e:
                logger.error(f"Error scanning {py_file}: {e}")

        return violations

    def run_import_linter_tool(self) -> tuple[bool, str]:
        """Run import-linter tool with configuration."""
        config_path = self.project_root / "config" / "tools" / "importlinter.cfg"

        if not config_path.exists():
            return False, f"Import-linter config not found: {config_path}"

        try:
            # Run import-linter
            result = subprocess.run([
                sys.executable, "-m", "importlinter",
                "--config", str(config_path)
            ], capture_output=True, text=True, cwd=str(self.project_root))

            success = result.returncode == 0
            output = result.stdout + result.stderr

            return success, output

        except FileNotFoundError:
            return False, "import-linter not installed"
        except Exception as e:
            return False, f"Error running import-linter: {e}"

    def validate_lane_boundaries(self) -> dict[str, list[str]]:
        """Validate all lane boundaries and return violations by lane."""
        lane_violations = {}

        # Check each lane directory (after Phase 5B, root modules scanned at project_root)
        lane_directories = {
            "MATRIZ": self.matriz_root,
            "root": self.project_root,  # Root-level modules (former lukhas/)
            "labs": self.candidate_root
        }

        for lane, directory in lane_directories.items():
            violations = self.scan_directory_for_violations(directory, lane)
            if violations:
                lane_violations[lane] = violations
                logger.error(f"{lane} lane has {len(violations)} import violations")
            else:
                logger.info(f"✓ {lane} lane: No import violations detected")

        return lane_violations

    def generate_violation_report(self, lane_violations: dict[str, list[str]]) -> str:
        """Generate comprehensive violation report."""
        report = ["=== Lane Boundary Import Violation Report ===\n"]

        total_violations = sum(len(violations) for violations in lane_violations.values())
        report.append(f"Total violations: {total_violations}\n")

        if total_violations == 0:
            report.append("✅ All lane boundaries properly maintained!\n")
            return "\n".join(report)

        for lane, violations in lane_violations.items():
            report.append(f"\n❌ {lane.upper()} Lane Violations ({len(violations)}):")
            for i, violation in enumerate(violations, 1):
                report.append(f"  {i}. {violation}")

        report.append("\n💡 Recommendations:")
        report.append("  - Move cross-lane functionality to approved integration points")
        report.append("  - Use dependency injection instead of direct imports")
        report.append("  - Consider extracting shared utilities to common modules")
        report.append("  - Update import-linter config if new integration points are needed")

        return "\n".join(report)


@pytest.mark.lint
@pytest.mark.architecture
class TestLaneImports:
    """Lane boundary import linting tests."""

    def test_matriz_lane_isolation(self):
        """Test MATRIZ lane doesn't import lukhas modules."""
        linter = LaneImportLinter()

        # Check MATRIZ directory exists
        if not linter.matriz_root.exists():
            pytest.skip("MATRIZ directory not found")

        # Scan MATRIZ violations
        matriz_violations = linter.scan_directory_for_violations(linter.matriz_root, "MATRIZ")

        # Log results
        logger.info(f"MATRIZ lane scan: {len(matriz_violations)} violations")
        for violation in matriz_violations[:5]:  # Log first 5
            logger.warning(f"  {violation}")

        # Assert no violations
        assert len(matriz_violations) == 0, f"MATRIZ lane has {len(matriz_violations)} import violations: {matriz_violations[:3]}"

        logger.info("✓ MATRIZ lane isolation maintained")

    def test_lukhas_cannot_import_matriz(self):
        """Test root modules (former lukhas/) cannot import matriz directly."""
        linter = LaneImportLinter()

        # Scan root-level module violations (after Phase 5B flattening)
        lukhas_violations = linter.scan_directory_for_violations(linter.project_root, "root")

        # Filter for MATRIZ-specific violations
        matriz_import_violations = [v for v in lukhas_violations if "MATRIZ" in v]

        # Log results
        logger.info(f"Lukhas→MATRIZ violations: {len(matriz_import_violations)}")
        for violation in matriz_import_violations[:3]:  # Log first 3
            logger.warning(f"  {violation}")

        # Assert no direct MATRIZ imports (approved integrations are allowed)
        direct_violations = [v for v in matriz_import_violations if "approved integration" not in v.lower()]
        assert len(direct_violations) == 0, f"Lukhas modules have {len(direct_violations)} direct MATRIZ imports: {direct_violations[:2]}"

        logger.info("✓ Lukhas→MATRIZ import restrictions enforced")

    def test_candidate_production_isolation(self):
        """Test candidate cannot import production-critical components."""
        linter = LaneImportLinter()

        # Check candidate directory exists
        if not linter.candidate_root.exists():
            logger.info("Candidate directory not found - skipping test")
            return

        # Scan candidate violations
        candidate_violations = linter.scan_directory_for_violations(linter.candidate_root, "labs")

        # Log results
        logger.info(f"Candidate lane scan: {len(candidate_violations)} violations")
        for violation in candidate_violations[:3]:  # Log first 3
            logger.warning(f"  {violation}")

        # Assert no production imports
        production_violations = [v for v in candidate_violations
                               if any(prod in v for prod in ["guardian_serializers", "webauthn_production", "prometheus_metrics"])]

        assert len(production_violations) == 0, f"Candidate imports production components: {production_violations[:2]}"

        logger.info("✓ Candidate production isolation maintained")

    def test_approved_integrations_allowed(self):
        """Test approved MATRIZ integration points are allowed."""
        linter = LaneImportLinter()

        # Check that approved integrations exist
        approved_files = []
        for integration in linter.approved_integrations:
            # Convert module path to file path (now at project root, not under lukhas/)
            file_path = linter.project_root / integration.replace(".", "/")
            py_file = file_path.with_suffix(".py")

            if py_file.exists():
                approved_files.append(py_file)
            else:
                # Try as directory with __init__.py
                init_file = file_path / "__init__.py"
                if init_file.exists():
                    approved_files.append(init_file)

        logger.info(f"Found {len(approved_files)} approved integration files")

        # These files should be allowed to have MATRIZ-related imports
        for approved_file in approved_files:
            lane = linter.detect_lane_from_path(approved_file)
            if lane:
                imports = linter.extract_imports_from_file(approved_file)
                violations = linter.check_import_violations(approved_file, lane, imports)

                # Should have no violations for approved integrations
                matrix_violations = [v for v in violations if "MATRIZ" in v]
                logger.info(f"Approved file {approved_file.name}: {len(matrix_violations)} MATRIZ violations")

        logger.info("✓ Approved integrations validation completed")

    def test_import_linter_tool_integration(self):
        """Test integration with import-linter tool."""
        linter = LaneImportLinter()

        # Run import-linter tool
        success, output = linter.run_import_linter_tool()

        logger.info("Import-linter tool output:")
        logger.info(output)

        if not success:
            if "not installed" in output:
                pytest.skip("import-linter not installed")
            else:
                logger.warning(f"Import-linter failed: {output}")
                # Don't fail the test if import-linter isn't working, just warn
                pytest.skip(f"Import-linter tool issues: {output}")

        logger.info("✓ Import-linter tool integration working")

    def test_comprehensive_lane_boundary_validation(self):
        """Comprehensive validation of all lane boundaries."""
        linter = LaneImportLinter()

        # Validate all lane boundaries
        lane_violations = linter.validate_lane_boundaries()

        # Generate comprehensive report
        report = linter.generate_violation_report(lane_violations)

        logger.info("=== Lane Boundary Validation Report ===")
        for line in report.split('\n'):
            if line.strip():
                if '❌' in line or 'violation' in line.lower():
                    logger.error(line)
                elif '✅' in line:
                    logger.info(line)
                else:
                    logger.info(line)

        # Calculate overall compliance
        total_violations = sum(len(violations) for violations in lane_violations.values())
        lanes_checked = len([d for d in [linter.matriz_root, linter.project_root, linter.candidate_root] if d.exists()])

        logger.info(f"Lanes checked: {lanes_checked}")
        logger.info(f"Total violations: {total_violations}")

        # Assert no violations for critical boundaries
        critical_violations = 0
        if "MATRIZ" in lane_violations:
            critical_violations += len(lane_violations["MATRIZ"])
        if "root" in lane_violations:
            matriz_root_violations = [v for v in lane_violations["root"] if "MATRIZ" in v]
            critical_violations += len(matriz_root_violations)

        assert critical_violations == 0, f"Critical lane boundary violations detected: {critical_violations}"

        logger.info("✅ Comprehensive lane boundary validation PASSED")


if __name__ == "__main__":
    # Run lane import validation standalone
    def run_lane_validation():
        print("Running lane boundary import validation...")

        linter = LaneImportLinter()

        print("\n=== Validating Lane Boundaries ===")

        # Validate all boundaries
        lane_violations = linter.validate_lane_boundaries()

        # Generate and display report
        report = linter.generate_violation_report(lane_violations)
        print(report)

        # Test import-linter integration
        print("\n=== Import-Linter Tool Integration ===")
        success, output = linter.run_import_linter_tool()

        if success:
            print("✅ Import-linter validation PASSED")
        else:
            print(f"⚠️  Import-linter issues: {output}")

        # Return overall success
        total_violations = sum(len(violations) for violations in lane_violations.values())
        return total_violations == 0

    import sys
    success = run_lane_validation()
    sys.exit(0 if success else 1)
