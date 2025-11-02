"""Cluster import failures and pytest errors to target final bridge fixes."""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from collections.abc import Iterable

ARTIFACTS = Path("artifacts")
FAILURE_LOG = ARTIFACTS / "import_failures.ndjson"
COLLECTION_REPORT = ARTIFACTS / "pytest_collection_errors_detailed.json"
OUTPUT_TARGETS = ARTIFACTS / "phase11_bridge_targets.txt"


def load_ndjson(path: Path) -> list[dict[str, Any]]:
    """Load NDJSON file, skipping malformed lines."""
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _count_by_module(failures: Iterable[dict[str, Any]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for item in failures:
        module = item.get("module") or "<unknown>"
        counter[module] += 1
    return counter


def _tally_pytest_errors(report: dict[str, Any]) -> tuple[Counter[str], Counter[str]]:
    modules = Counter()
    symbols = Counter()
    for entry in report.get("detailed_errors", []):
        error_text = entry.get("error", "")
        mod_match = re.search(
            r"ModuleNotFoundError: No module named '([^']+)'", error_text
        )
        if mod_match:
            modules[mod_match.group(1)] += 1
        sym_match = re.search(
            r"ImportError.*cannot import name '([^']+)'", error_text
        )
        if sym_match:
            symbols[sym_match.group(1)] += 1
    return modules, symbols


def main() -> int:
    failures = load_ndjson(FAILURE_LOG)
    module_fail_counts = _count_by_module(failures)

    if COLLECTION_REPORT.exists():
        report_data = json.loads(COLLECTION_REPORT.read_text(encoding="utf-8"))
    else:
        report_data = {"detailed_errors": []}

    pytest_module_counts, pytest_symbol_counts = _tally_pytest_errors(report_data)
    combined_modules = module_fail_counts + pytest_module_counts

    print("\n=== HOT MODULES (telemetry + pytest) ===")
    for module, count in combined_modules.most_common(15):
        print(f"{count:3d}  {module}")

    print("\n=== TOP MISSING SYMBOLS ===")
    for symbol, count in pytest_symbol_counts.most_common(15):
        print(f"{count:3d}  {symbol}")

    todo: list[str] = []
    prefixes = (
        "lukhas.",
        "candidate.",
        "consciousness.",
        "core.",
        "governance.",
        "memory.",
        "observability.",
        "tools.",
    )

    for module, _count in combined_modules.most_common():
        if module.startswith(prefixes):
            todo.append(module)

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    OUTPUT_TARGETS.write_text("\n".join(todo), encoding="utf-8")
    print(f"\n→ wrote suggested targets: {OUTPUT_TARGETS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
