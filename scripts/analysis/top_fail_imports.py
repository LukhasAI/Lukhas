"""Summarize most frequent import failures to guide bridge/stub creation."""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path
from typing import Any

_DEFAULT_PATH = Path("artifacts/import_failures.ndjson")
_DEFAULT_LIMIT = 25


def _load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _extract_key(record: dict[str, Any]) -> str:
    for key in ("module", "target", "import_path"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def main(path: Path = _DEFAULT_PATH, limit: int = _DEFAULT_LIMIT) -> int:
    if not path.exists():
        print(f"no import telemetry: {path}", file=sys.stderr)
        return 1

    counts: collections.Counter[str] = collections.Counter()
    for record in _load_records(path):
        key = _extract_key(record)
        if key:
            counts[key] += 1

    for module, count in counts.most_common(limit):
        print(f"{count:4d}  {module}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
