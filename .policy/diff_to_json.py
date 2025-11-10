#!/usr/bin/env python3
"""Generate diff metadata for OPA policy evaluation."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any


def _git_diff(base: str, head: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "diff", base, head, "--no-color", "--unified=0"],
            text=True,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - surfaced in CI
        raise SystemExit(exc.returncode) from exc


def _start_file() -> dict[str, Any]:
    return {
        "old_path": None,
        "new_path": None,
        "added": [],
        "removed": [],
    }


def _normalize_path(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if value in {"", "/dev/null"}:
        return None
    return value


def _parse_diff(diff_text: str) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("diff --git"):
            if current is not None:
                files.append(current)
            current = _start_file()
            continue

        if current is None:
            continue

        if raw_line.startswith("--- "):
            current["old_path"] = _normalize_path(raw_line[6:] if raw_line.startswith("--- a/") else raw_line[4:])
            continue

        if raw_line.startswith("+++ "):
            current["new_path"] = _normalize_path(raw_line[6:] if raw_line.startswith("+++ b/") else raw_line[4:])
            continue

        if raw_line.startswith("@@") or raw_line.startswith("index ") or raw_line.startswith("new file mode") or raw_line.startswith("deleted file mode") or raw_line.startswith("Binary files "):
            continue

        if raw_line.startswith("+") and not raw_line.startswith("++"):
            current["added"].append(raw_line[1:])
            continue

        if raw_line.startswith("-") and not raw_line.startswith("--"):
            current["removed"].append(raw_line[1:])
            continue

    if current is not None:
        files.append(current)

    # Filter out entries that have no meaningful path information to avoid false positives
    filtered: list[dict[str, Any]] = []
    for entry in files:
        if entry.get("old_path") is None and entry.get("new_path") is None:
            continue
        filtered.append(entry)
    return filtered


def main() -> None:
    base = os.environ.get("BASE_SHA")
    head = os.environ.get("HEAD_SHA")

    if not head:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if not base:
        try:
            base = subprocess.check_output(["git", "rev-parse", f"{head}^"], text=True).strip()
        except subprocess.CalledProcessError:
            base = head

    diff_text = _git_diff(base, head)
    payload = {"files": _parse_diff(diff_text)}
    json.dump(payload, sys.stdout)


if __name__ == "__main__":
    main()
