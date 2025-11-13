#!/usr/bin/env python3
"""
Heuristic import inserter for common undefined names.
Reads /tmp/ruff_f821.json and for undefined names matching HEUR,
inserts suggested import (dry-run or apply).

Usage:
# Dry-run:
python3 tools/ci/f821_import_inserter.py --dry-run

# Dry-run on the heuristic shard:
python3 tools/ci/f821_import_inserter.py --files $(cat /tmp/f821_first_shard.txt) --dry-run

# Apply (after reviewing diffs):
python3 tools/ci/f821_import_inserter.py --apply --files $(cat /tmp/f821_first_shard.txt)
"""

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

import libcst as cst

HEUR = {
    "np": "import numpy as np",
    "pd": "import pandas as pd",
    "torch": "import torch",
    "plt": "from matplotlib import pyplot as plt",
    "Path": "from pathlib import Path",
    "Optional": "from typing import Optional",
    "List": "from typing import List",
    "Dict": "from typing import Dict",
    "Any": "from typing import Any",
    "Tuple": "from typing import Tuple",
    "datetime": "from datetime import datetime",
}


def collect_targets(ruff_json_path):
    if not Path(ruff_json_path).exists():
        return {}
    data = json.loads(Path(ruff_json_path).read_text())
    files = {}
    for e in data:
        msg = e.get("message", "")
        if "Undefined name `" in msg:
            # Extract name between backticks
            parts = msg.split("`")
            if len(parts) >= 2:
                name = parts[1]
                if name in HEUR:
                    files.setdefault(e["filename"], set()).add(name)
    return files


class ImportInserter(cst.CSTTransformer):
    def __init__(self, imports_to_add):
        # imports_to_add: list of import strings e.g. "import numpy as np"
        self.to_add = imports_to_add
        super().__init__()
        self.added = False

    def leave_Module(self, original_node, updated_node):
        # Find insertion point: after docstring & existing imports
        body = list(updated_node.body)
        # if module starts with simple docstring, skip it
        idx = 0
        if body and isinstance(body[0], cst.SimpleStatementLine):
            stmt = body[0].body[0]
            if isinstance(stmt, cst.Expr) and isinstance(
                stmt.value, (cst.SimpleString, cst.ConcatenatedString)
            ):
                idx = 1
        # insert imports at idx
        import_nodes = []
        for imp_txt in self.to_add:
            # parse import snippet into Module and extract first top statement
            parsed = cst.parse_module(imp_txt)
            node = parsed.body[0]
            import_nodes.append(node)
        new_body = body[:idx] + import_nodes + body[idx:]
        self.added = True
        return updated_node.with_changes(body=new_body)


def run_inserter_on_file(path: Path, names: set, dry_run=True):
    # build import strings
    to_add = [HEUR[n] for n in sorted(names) if HEUR.get(n)]
    if not to_add:
        return False, ""
    src = path.read_text()
    module = cst.parse_module(src)
    ins = ImportInserter(to_add)
    new = module.visit(ins)
    if not ins.added:
        return False, ""
    if dry_run:
        with tempfile.NamedTemporaryFile("w", delete=False) as fh:
            fh.write(new.code)
            tmp = fh.name
        diff = subprocess.run(
            ["git", "diff", "--no-index", "--", str(path), tmp],
            capture_output=True,
            text=True,
        )
        os.unlink(tmp)
        return True, diff.stdout
    else:
        # backup
        bkdir = Path("codemod_backups")
        bkdir.mkdir(exist_ok=True)
        bakname = bkdir / f"{path.name}.bak"
        bakname.write_text(path.read_text())
        path.write_text(new.code)
        return True, f"APPLIED imports to {path}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ruff-json", default="/tmp/ruff_f821_clean.json")
    ap.add_argument("--files", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    targets = {}
    if args.files:
        # if explicit files, use ruff json to pick relevant names per file
        data = (
            json.loads(Path(args.ruff_json).read_text())
            if Path(args.ruff_json).exists()
            else []
        )
        by_file = {}
        for e in data:
            fn = e.get("filename")
            if fn in args.files:
                msg = e.get("message", "")
                if "Undefined name `" in msg:
                    parts = msg.split("`")
                    if len(parts) >= 2:
                        name = parts[1]
                        if name in HEUR:
                            by_file.setdefault(fn, set()).add(name)
        targets = by_file
    else:
        targets = collect_targets(args.ruff_json)

    if not targets:
        print("No heuristic targets found.")
        return

    for f, names in targets.items():
        p = Path(f)
        if not p.exists():
            print("Missing:", f)
            continue
        ok, out = run_inserter_on_file(p, names, dry_run=not args.apply)
        if ok:
            print(f"== {'DRY' if args.dry_run or not args.apply else 'APPLIED'} == {f}")
            print(out[:10000])
        else:
            print("No change:", f)


if __name__ == "__main__":
    main()
