"""Tests for the Keatsian replacer tooling."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / "branding" / "tools" / "keatsian_replacer.py"

spec = importlib.util.spec_from_file_location(
    "branding.tools.keatsian_replacer", MODULE_PATH
)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader  # pragma: no cover - importlib contract
spec.loader.exec_module(module)

fix_later = module.fix_later


@pytest.mark.tier3
def test_fix_later_records_diagnostics(tmp_path: Path) -> None:
    """Ensure the fallback handler logs diagnostics and returns a summary."""

    log_path = tmp_path / "fallbacks" / "keatsian.jsonl"

    message = fix_later(
        "process_markdown_file",
        file_path=Path("branding/example.md"),
        error=RuntimeError("boom"),
        metadata={"stage": "markdown_transformation"},
        log_path=log_path,
    )

    assert "process_markdown_file" in message
    assert "branding/example.md" in message
    assert log_path.exists()

    log_contents = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(log_contents) == 1

    payload = json.loads(log_contents[0])
    assert payload["context"] == "process_markdown_file"
    assert payload["file"] == "branding/example.md"
    assert payload["metadata"]["stage"] == "markdown_transformation"
    assert payload["error"]["type"] == "RuntimeError"

