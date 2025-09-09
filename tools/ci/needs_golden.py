# tools/ci/needs_golden.py
import json
import sys
from pathlib import Path


def changed_lines():
    # naive: list changed files (nightly branch vs main), line granularity optional
    out = Path("reports/todos/index.json")
    files = []
    if out.exists():
        data = json.loads(out.read_text() or "{}")
        files = list(data.get("files", {}).keys())
    return files


def uncovered_files(coverage_json="reports/autofix/coverage.json"):
    p = Path(coverage_json)
    if not p.exists():
        return set()
    data = json.loads(p.read_text() or "{}")
    files = set()
    for path, meta in data.get("files", {}).items():
        summary = meta.get("summary", {})
        if summary.get("percent_covered", 0) <= 0:
            files.add(path)
    return files


def main():
    changed = set(changed_lines())
    uncov = uncovered_files()
    need = sorted(changed & uncov)
    print(json.dumps({"needs_golden": need}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())