from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from products.infrastructure.legado.legacy_systems.security import (
    SecurityError,
    check_safety_flags,
    log_incident,
    safe_eval,
    safe_subprocess_run,
    sanitize_input,
    shutdown_systems,
)


def test_sanitize_input_removes_script_content() -> None:
    malicious = "<script>alert('x')</script>secure"
    sanitized = sanitize_input(malicious)
    assert "script" not in sanitized.lower()
    assert "secure" in sanitized


def test_safe_eval_rejects_arbitrary_execution() -> None:
    assert safe_eval("{'key': 1}") == {"key": 1}
    with pytest.raises(SecurityError):
        safe_eval("__import__('os').system('echo hack')")


def test_safe_subprocess_run_enforces_argument_safety() -> None:
    result = safe_subprocess_run([sys.executable, "-c", "print('ok')"])
    assert result.stdout.strip() == "ok"

    with pytest.raises(SecurityError):
        safe_subprocess_run(["echo;rm"])


def test_check_safety_flags_detects_insufficient_tier() -> None:
    profile = {"safe_mode": False, "refuse_unknown": True, "minimum_tier": 2}
    assert check_safety_flags({"tier": 1, "user": "guest"}, safety_profile=profile)
    assert not check_safety_flags({"tier": 3, "user": "trusted"}, safety_profile=profile)


def test_log_incident_persists_guardian_entry(tmp_path: Path) -> None:
    log_path = tmp_path / "guardian.jsonl"
    result_path = log_incident(
        "guardian alert <script>remove</script>",
        {"user": "lambda", "tier": 4},
        safety_profile={"safe_mode": True},
        log_path=log_path,
    )

    assert result_path == log_path.resolve()
    entry = json.loads(log_path.read_text(encoding="utf-8").strip())
    assert entry["user"]["user"] == "lambda"
    assert "script" not in entry["reason"].lower()


def test_shutdown_systems_logs_and_sanitizes(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("CRITICAL")
    log_path = tmp_path / "shutdown.jsonl"

    shutdown_systems(
        "shutdown required <script>inject</script>",
        user_context={"user": "sentinel", "tier": 1},
        safety_profile={"safe_mode": True},
        log_path=log_path,
    )

    assert any("Guardian shutdown initiated" in record.message for record in caplog.records)

    entries = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert entries
    assert all("script" not in entry["reason"].lower() for entry in entries)
    assert entries[0]["profile"]["safe_mode"] is True
