import json
from pathlib import Path
from typing import Any

import pytest
from tools import check_policy


class DummyResult:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _write_input(tmp_path: Path, payload: dict[str, Any]) -> Path:
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload))
    return path


def test_evaluate_policy_missing_opa(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(check_policy.shutil, "which", lambda _: None)
    with pytest.raises(FileNotFoundError):
        check_policy.evaluate_policy("opa", Path("policy.rego"), Path("input.json"))


def test_main_reports_policy_violations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    policy = tmp_path / "policy.rego"
    policy.write_text("package lukhas.guard\ndeny[msg] { msg := \"violation\" }")

    input_path = _write_input(tmp_path, {"status": "ok"})

    def fake_run(cmd: list[str]) -> DummyResult:
        output = {"result": [{"expressions": [{"value": ["violation"]}]}]}
        return DummyResult(0, json.dumps(output))

    monkeypatch.setattr(check_policy, "_run", fake_run)
    monkeypatch.setattr(check_policy.shutil, "which", lambda _: "opa")

    exit_code = check_policy.main([
        "--input",
        str(input_path),
        "--policy",
        str(policy),
        "--opa-bin",
        "opa",
    ])

    assert exit_code == 1


def test_main_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    policy = tmp_path / "policy.rego"
    policy.write_text("package lukhas.guard\ndeny[msg] { false }")

    input_path = _write_input(tmp_path, {"status": "ok"})

    def fake_run(cmd: list[str]) -> DummyResult:
        output = {"result": [{"expressions": [{"value": []}]}]}
        return DummyResult(0, json.dumps(output))

    monkeypatch.setattr(check_policy, "_run", fake_run)
    monkeypatch.setattr(check_policy.shutil, "which", lambda _: "opa")

    exit_code = check_policy.main([
        "--input",
        str(input_path),
        "--policy",
        str(policy),
    ])

    assert exit_code == 0
