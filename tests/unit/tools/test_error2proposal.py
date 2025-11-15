"""Tests for error2proposal tool"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_module(module_name: str, file_path: Path):
    """Load a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader  # for type checking
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


error2proposal = _load_module("error2proposal", REPO_ROOT / "tools" / "error2proposal.py")


@pytest.fixture
def sample_pytest_output() -> str:
    """Sample pytest output with various error types"""
    return """============================= test session starts ==============================
platform linux -- Python 3.11.14, pytest-8.4.2, pluggy-1.6.0 -- /root/.local/share/uv/tools/pytest/bin/python
cachedir: .pytest_cache
rootdir: /home/user/Lukhas/tests/unit
configfile: pytest.ini
collecting ... collected 0 items / 5 errors

==================================== ERRORS ====================================
_ ERROR collecting tests/unit/adapters/test_bio_adapter.py _
ImportError while importing test module '/home/user/Lukhas/tests/unit/adapters/test_bio_adapter.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/root/.local/share/uv/tools/pytest/lib/python3.11/site-packages/_pytest/python.py:498: in importtestmodule
    mod = import_path(
tests/unit/adapters/test_bio_adapter.py:4: in <module>
    from matriz.adapters.bio_adapter import BioAdapter
matriz/adapters/__init__.py:19: in <module>
    from pydantic import BaseModel, Field
E   ModuleNotFoundError: No module named 'pydantic'
_ ERROR collecting tests/unit/adapters/test_bridge_adapter.py _
ImportError while importing test module '/home/user/Lukhas/tests/unit/adapters/test_bridge_adapter.py'.
Traceback:
tests/unit/adapters/test_bridge_adapter.py:4: in <module>
    from matriz.adapters.bridge_adapter import BridgeAdapter
matriz/adapters/__init__.py:19: in <module>
    from pydantic import BaseModel, Field
E   ModuleNotFoundError: No module named 'pydantic'
_ ERROR collecting tests/unit/core/test_engine.py _
ImportError while importing test module.
E   ImportError: cannot import name 'EngineCore' from 'matriz.core'
FAILED tests/unit/bridge/test_api.py::test_authentication - AttributeError: 'NoneType' object has no attribute 'token'
=========================== short test summary info ============================
ERROR tests/unit/adapters/test_bio_adapter.py
ERROR tests/unit/adapters/test_bridge_adapter.py
ERROR tests/unit/core/test_engine.py
FAILED tests/unit/bridge/test_api.py::test_authentication
!!!!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!
============================== 4 errors in 1.71s ===============================
"""


@pytest.fixture
def temp_test_results(tmp_path: Path, sample_pytest_output: str) -> Path:
    """Create temporary test results file"""
    test_file = tmp_path / "test_results.txt"
    test_file.write_text(sample_pytest_output, encoding="utf-8")
    return test_file


def test_parse_module_not_found_error(temp_test_results: Path) -> None:
    """Test parsing ModuleNotFoundError"""
    parser = error2proposal.TestFailureParser()
    failures = parser.parse_file(temp_test_results)

    # Should find at least 2 pydantic errors
    pydantic_errors = [
        f for f in failures
        if f.error_type == "ModuleNotFoundError" and "pydantic" in f.error_message
    ]
    assert len(pydantic_errors) >= 2

    # Check error details
    error = pydantic_errors[0]
    assert error.error_type == "ModuleNotFoundError"
    assert "pydantic" in error.error_message


def test_parse_import_error(temp_test_results: Path) -> None:
    """Test parsing ImportError"""
    parser = error2proposal.TestFailureParser()
    failures = parser.parse_file(temp_test_results)

    import_errors = [f for f in failures if f.error_type == "ImportError"]
    assert len(import_errors) >= 1

    error = import_errors[0]
    assert error.error_type == "ImportError"


def test_parse_test_failure(temp_test_results: Path) -> None:
    """Test parsing test failures"""
    parser = error2proposal.TestFailureParser()
    failures = parser.parse_file(temp_test_results)

    # Should find the FAILED test
    test_failures = [f for f in failures if "test_authentication" in f.test_file]
    assert len(test_failures) >= 1


def test_generate_missing_dependency_proposal(tmp_path: Path) -> None:
    """Test generating proposal for missing dependency"""
    generator = error2proposal.ProposalGenerator(REPO_ROOT)

    failures = [
        error2proposal.TestFailure(
            test_file="tests/unit/test_one.py",
            error_type="ModuleNotFoundError",
            error_message="No module named 'pydantic'",
        ),
        error2proposal.TestFailure(
            test_file="tests/unit/test_two.py",
            error_type="ModuleNotFoundError",
            error_message="No module named 'pydantic'",
        ),
    ]

    report = generator.generate_proposals(failures)

    assert report.total_failures == 2
    assert report.proposals_generated >= 1
    assert report.high_confidence_proposals >= 1

    # Find pydantic proposal
    pydantic_proposal = next(
        (p for p in report.proposals if "pydantic" in p.title.lower()), None
    )
    assert pydantic_proposal is not None
    assert pydantic_proposal.confidence >= 0.8
    assert pydantic_proposal.fix_type == "dependency"
    assert len(pydantic_proposal.affected_files) == 2
    assert pydantic_proposal.patch_content is not None
    assert "pydantic" in pydantic_proposal.patch_content


def test_generate_import_error_proposal(tmp_path: Path) -> None:
    """Test generating proposal for import error"""
    generator = error2proposal.ProposalGenerator(REPO_ROOT)

    failures = [
        error2proposal.TestFailure(
            test_file="tests/unit/test_core.py",
            error_type="ImportError",
            error_message="cannot import name 'EngineCore' from 'matriz.core'",
        ),
    ]

    report = generator.generate_proposals(failures)

    assert report.total_failures == 1
    assert report.proposals_generated >= 1

    proposal = report.proposals[0]
    assert proposal.fix_type == "import"
    assert proposal.confidence > 0


def test_generate_attribute_error_proposal(tmp_path: Path) -> None:
    """Test generating proposal for attribute error"""
    generator = error2proposal.ProposalGenerator(REPO_ROOT)

    failures = [
        error2proposal.TestFailure(
            test_file="tests/unit/test_api.py",
            error_type="AttributeError",
            error_message="'NoneType' object has no attribute 'token'",
        ),
    ]

    report = generator.generate_proposals(failures)

    assert report.total_failures == 1
    assert report.proposals_generated >= 1

    proposal = report.proposals[0]
    assert proposal.fix_type == "attribute"
    assert "attribute error" in proposal.description.lower()


def test_converter_end_to_end(temp_test_results: Path, tmp_path: Path) -> None:
    """Test complete conversion process"""
    output_dir = tmp_path / "proposals"

    converter = error2proposal.Error2ProposalConverter(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
    )

    report = converter.convert(
        test_results_file=temp_test_results, generate_patches=True
    )

    # Check report
    assert report.total_failures > 0
    assert report.proposals_generated > 0

    # Check JSON output
    json_file = output_dir / "proposals.json"
    assert json_file.exists()

    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_failures"] == report.total_failures
    assert data["proposals_generated"] == report.proposals_generated
    assert len(data["proposals"]) == report.proposals_generated

    # Check patch files for high-confidence proposals
    patch_dir = output_dir / "patches"
    if report.high_confidence_proposals > 0:
        assert patch_dir.exists()
        patch_files = list(patch_dir.glob("*.patch"))
        assert len(patch_files) > 0


def test_no_patches_option(temp_test_results: Path, tmp_path: Path) -> None:
    """Test disabling patch generation"""
    output_dir = tmp_path / "proposals"

    converter = error2proposal.Error2ProposalConverter(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
    )

    converter.convert(test_results_file=temp_test_results, generate_patches=False)

    # Check that patch directory was not created
    patch_dir = output_dir / "patches"
    assert not patch_dir.exists()


def test_empty_test_results(tmp_path: Path) -> None:
    """Test handling empty test results"""
    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    parser = error2proposal.TestFailureParser()
    failures = parser.parse_file(empty_file)

    assert len(failures) == 0


def test_nonexistent_file() -> None:
    """Test handling nonexistent file"""
    parser = error2proposal.TestFailureParser()
    failures = parser.parse_file(Path("/nonexistent/file.txt"))

    assert len(failures) == 0


def test_proposal_to_dict() -> None:
    """Test proposal serialization"""
    proposal = error2proposal.Proposal(
        id="test-1",
        title="Test Proposal",
        description="Test description",
        fix_type="test",
        affected_files=["test.py"],
        confidence=0.9,
        priority="high",
    )

    data = proposal.to_dict()

    assert data["id"] == "test-1"
    assert data["title"] == "Test Proposal"
    assert data["confidence"] == 0.9
    assert data["affected_files"] == ["test.py"]


def test_report_to_dict() -> None:
    """Test report serialization"""
    proposal = error2proposal.Proposal(
        id="test-1",
        title="Test Proposal",
        description="Test description",
        fix_type="test",
        affected_files=["test.py"],
        confidence=0.9,
    )

    report = error2proposal.ProposalReport(
        total_failures=5,
        unique_error_types=3,
        proposals_generated=2,
        high_confidence_proposals=1,
        proposals=[proposal],
    )

    data = report.to_dict()

    assert data["total_failures"] == 5
    assert data["unique_error_types"] == 3
    assert data["proposals_generated"] == 2
    assert data["high_confidence_proposals"] == 1
    assert len(data["proposals"]) == 1
