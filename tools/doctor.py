import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
pkg = ROOT / "lukhas"
assert pkg.exists() and (pkg / "__init__.py").exists(), "lukhas package missing"

# non-prod lanes must NOT be packages
for lane in ["candidate", "quarantine", "archive"]:
    d = ROOT / lane
    if d.exists():
        bad = list(d.rglob("__init__.py"))
        assert not bad, f"Remove __init__.py from {lane}/: {bad}"

# in CI, sys.path must not include lane paths
if os.getenv("CI"):
    for p in sys.path:
        assert all(
            x not in p for x in ("candidate", "quarantine", "archive")
        ), f"Illegal path in sys.path: {p}"

print("doctor: OK")
