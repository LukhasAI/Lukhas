#!/usr/bin/env python3
"""
Generate lukhas package shims from artifacts/lukhas_shim_map.json.
Reads the data-driven map and creates only the hot-path packages tests need.
"""
import json
from pathlib import Path

HEADER = """# auto-generated lukhas compat shim
try:
    from {real} import *
except Exception:
    from candidate.{real} import *
"""


def ensure_pkg(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    init = path / "__init__.py"
    if not init.exists():
        init.write_text("# package shim\n")


def write_shim(pkg_dir: Path, leaf: str):
    if leaf == "__init__":
        ensure_pkg(pkg_dir)
        return
    # lukhas/<pkg_dir>/leaf.py -> real module name without 'lukhas.'
    # Convert 'lukhas/x/y' → 'x.y'
    real_base = ".".join(pkg_dir.parts[1:])
    real = f"{real_base}.{leaf}"
    (pkg_dir / f"{leaf}.py").write_text(HEADER.format(real=real))


def main():
    manifest = Path("artifacts/lukhas_shim_map.json")
    if not manifest.exists():
        print("No artifacts/lukhas_shim_map.json found. Run tools/import_doctor.py first.")
        return 1

    mapping = json.loads(manifest.read_text())
    for pkg, leaves in mapping.items():
        pkg_dir = Path(pkg)
        ensure_pkg(pkg_dir)
        for leaf in leaves:
            write_shim(pkg_dir, leaf)

    print("✅ Generated lukhas package shims from artifacts/lukhas_shim_map.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
