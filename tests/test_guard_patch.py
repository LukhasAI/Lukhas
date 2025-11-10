from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from tools import guard_patch


def _patch_guard_patch(monkeypatch: pytest.MonkeyPatch, *, changed: list[str], line_map: dict[str, int]) -> None:
    monkeypatch.setattr(guard_patch, "list_changed_files", lambda base, head: changed)
    monkeypatch.setattr(
        guard_patch,
        "diff_stats",
        lambda base, head, paths: sum(line_map.get(path, 0) for path in paths),
    )
    monkeypatch.setattr(guard_patch, "risky_exception_added", lambda base, head: False)
    monkeypatch.setattr(guard_patch, "any_protected_touched", lambda changed, protected: [])


def test_guard_patch_respects_whitelist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    whitelist = tmp_path / "whitelist.txt"
    whitelist.write_text("foo.py\n")

    changed = ["foo.py", "bar.py"]
    line_map = {"foo.py": 30, "bar.py": 10}

    _patch_guard_patch(monkeypatch, changed=changed, line_map=line_map)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "guard_patch",
            "--max-files",
            "1",
            "--max-lines",
            "20",
            "--whitelist-file",
            str(whitelist),
        ],
    )

    with pytest.raises(SystemExit) as exc:
        guard_patch.main()

    assert exc.value.code == 0

    captured = capsys.readouterr().out
    payload = json.loads(captured)
    assert payload["status"] == "ok"
    assert payload["counted_files"] == 1
    assert payload["counted_lines"] == 10
    assert payload["whitelisted_files"] == ["foo.py"]
    assert payload["changed_files"] == 2
    assert payload["changed_lines"] == 40


def test_guard_patch_enforces_limits_without_whitelist(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    changed = ["foo.py", "bar.py"]
    line_map = {"foo.py": 30, "bar.py": 10}

    _patch_guard_patch(monkeypatch, changed=changed, line_map=line_map)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "guard_patch",
            "--max-files",
            "1",
            "--max-lines",
            "20",
        ],
    )

    with pytest.raises(SystemExit) as exc:
        guard_patch.main()

    assert exc.value.code == 1

    captured = capsys.readouterr().out
    json_blob, _ = captured.split("\n\nPolicy", 1)
    payload = json.loads(json_blob)
    assert payload["status"] == "fail"
    assert payload["counted_files"] == 2
    assert payload["counted_lines"] == 40
    assert payload["whitelisted_files"] == []
