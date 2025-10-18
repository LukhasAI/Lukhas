from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[4] / "tools" / "ci" / "check_unused_imports_todo.py"
SPEC = importlib.util.spec_from_file_location("check_unused_imports_todo", MODULE_PATH)
assert SPEC and SPEC.loader  # ΛTAG: module_loading_guard
check_unused_imports = importlib.util.module_from_spec(SPEC)
sys.modules.setdefault("_lukhas_check_unused_imports_todo_test", check_unused_imports)
SPEC.loader.exec_module(check_unused_imports)


def test_resolve_finding_path_returns_repo_and_relative(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # ΛTAG: repo_path_resolution_test
    """resolve_finding_path should map filenames to absolute and repo-relative paths."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr(check_unused_imports, "REPO", repo_root, raising=False)

    relative_path = Path("pkg/sample.py")
    target_file = repo_root / relative_path
    target_file.parent.mkdir(parents=True)
    target_file.write_text("print('hi')\n", encoding="utf-8")

    abs_path, rel_path = check_unused_imports.resolve_finding_path(str(relative_path))

    assert abs_path == target_file.resolve()
    assert rel_path == relative_path


def test_resolve_finding_path_handles_outside_repo(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # ΛTAG: repo_path_resolution_test
    """Absolute filenames outside the repo should be returned unchanged for display."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr(check_unused_imports, "REPO", repo_root, raising=False)

    outside_file = tmp_path / "external.py"
    outside_file.write_text("print('external')\n", encoding="utf-8")

    abs_path, rel_path = check_unused_imports.resolve_finding_path(str(outside_file))

    assert abs_path == outside_file
    assert rel_path == outside_file


def test_check_annotation_detects_todo_tag(tmp_path: Path) -> None:
    # ΛTAG: t4_annotation_check_test
    """check_annotation should detect TODO-tagged unused imports."""
    annotated_file = tmp_path / "annotated.py"
    annotated_file.write_text("import os  # noqa: F401 # TODO[T4-UNUSED-IMPORT]: reason\n", encoding="utf-8")

    assert check_unused_imports.check_annotation(str(annotated_file), 1)


def test_check_annotation_missing_tag(tmp_path: Path) -> None:
    # ΛTAG: t4_annotation_check_test
    """check_annotation should report missing annotations when tags are absent."""
    missing_file = tmp_path / "missing.py"
    missing_file.write_text("import os\n", encoding="utf-8")

    assert not check_unused_imports.check_annotation(str(missing_file), 1)
