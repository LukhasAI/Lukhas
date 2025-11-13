#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for quickstart examples.

Validates that all examples run without errors.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
EXAMPLES_DIR = PROJECT_ROOT / "examples" / "quickstart"


class TestQuickstartExamples:
    """Test all quickstart examples."""

    @pytest.mark.parametrize(
        "example_file",
        [
            "01_hello_lukhas.py",
            "02_reasoning_trace.py",
            "03_memory_persistence.py",
            "04_guardian_ethics.py",
            "05_full_workflow.py",
        ],
    )
    def test_example_runs_without_error(self, example_file: str) -> None:
        """Test that example runs without errors."""
        example_path = EXAMPLES_DIR / example_file

        assert example_path.exists(), f"Example not found: {example_path}"

        # Run the example
        result = subprocess.run(
            [sys.executable, str(example_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Should exit successfully
        assert result.returncode == 0, (
            f"Example {example_file} failed with exit code {result.returncode}\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

        # Should have some output
        assert len(result.stdout) > 0, f"Example {example_file} produced no output"

    def test_all_examples_exist(self) -> None:
        """Test that all required examples exist."""
        required_examples = [
            "01_hello_lukhas.py",
            "02_reasoning_trace.py",
            "03_memory_persistence.py",
            "04_guardian_ethics.py",
            "05_full_workflow.py",
        ]

        for example in required_examples:
            example_path = EXAMPLES_DIR / example
            assert example_path.exists(), f"Missing example: {example}"

    def test_examples_have_docstrings(self) -> None:
        """Test that all examples have proper documentation."""
        for example_file in EXAMPLES_DIR.glob("*.py"):
            with open(example_file) as f:
                content = f.read()

            # Should have module docstring
            assert '"""' in content, f"Missing docstring in {example_file.name}"

            # Should mention troubleshooting
            assert (
                "Troubleshooting" in content or "troubleshoot" in content
            ), f"Missing troubleshooting section in {example_file.name}"


class TestQuickstartCLI:
    """Test quickstart CLI tools."""

    def test_guided_cli_import(self) -> None:
        """Test that guided CLI can be imported."""
        from lukhas.cli import guided

        assert hasattr(guided, "GuidedCLI")

    def test_troubleshoot_cli_import(self) -> None:
        """Test that troubleshoot CLI can be imported."""
        from lukhas.cli import troubleshoot

        assert hasattr(troubleshoot, "TroubleshootAssistant")


class TestDemoDataGenerator:
    """Test demo data generator."""

    def test_generator_import(self) -> None:
        """Test that generator can be imported."""
        sys.path.insert(0, str(PROJECT_ROOT))

        from tools.generate_demo_data import DemoDataGenerator

        assert DemoDataGenerator

    def test_generator_initialization(self) -> None:
        """Test generator can be initialized."""
        sys.path.insert(0, str(PROJECT_ROOT))

        from tools.generate_demo_data import DemoDataGenerator

        generator = DemoDataGenerator(size="small")
        assert generator.size == "small"
        assert "small" in generator.sizes


class TestQuickstartScript:
    """Test quickstart shell script."""

    def test_quickstart_script_exists(self) -> None:
        """Test that quickstart script exists and is executable."""
        script_path = PROJECT_ROOT / "scripts" / "quickstart.sh"

        assert script_path.exists(), "quickstart.sh not found"
        assert script_path.stat().st_mode & 0o111, "quickstart.sh not executable"

    def test_script_has_shebang(self) -> None:
        """Test that script has proper shebang."""
        script_path = PROJECT_ROOT / "scripts" / "quickstart.sh"

        with open(script_path) as f:
            first_line = f.readline()

        assert first_line.startswith("#!/"), "Missing shebang"


class TestQuickstartDocumentation:
    """Test quickstart documentation."""

    def test_readme_exists(self) -> None:
        """Test that quickstart README exists."""
        readme_path = PROJECT_ROOT / "docs" / "quickstart" / "README.md"

        assert readme_path.exists(), "Quickstart README not found"

    def test_readme_completeness(self) -> None:
        """Test that README covers all important topics."""
        readme_path = PROJECT_ROOT / "docs" / "quickstart" / "README.md"

        with open(readme_path) as f:
            content = f.read()

        # Required sections
        required_sections = [
            "Prerequisites",
            "Installation",
            "Troubleshooting",
            "Next Steps",
            "FAQs",
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"

        # Should mention all examples
        for i in range(1, 6):
            assert f"0{i}_" in content, f"Missing reference to example {i}"
