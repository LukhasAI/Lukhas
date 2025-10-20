#!/usr/bin/env python3
"""
Validate that manifest-declared contracts exist and are well-formed.

Improvements:
- Recursive discovery of contracts/ (supports nested directories)
- More permissive ID regex (allow dash and slash in name segment)
- Suggest similar contract IDs on miss (Levenshtein via difflib)
- Summary output with counts
"""
import json
import pathlib
import re
import sys
from difflib import get_close_matches
from typing import Dict, Set

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFESTS = [m for m in ROOT.rglob("module.manifest.json") if ".archive" not in str(m)]
ID_RE = re.compile(r"^[A-Za-z0-9_.:/-]+@v\d+$")


def load_contract_index() -> Dict[str, pathlib.Path]:
    """Build an index of available contract IDs to file paths.

    Returns:
        Dict[str, pathlib.Path]: Mapping of contract ID (e.g., "foo.bar@v1") to
        the file path containing that contract JSON.

    Notes:
        - If a contract JSON omits the "id" field, the filename stem is used.
        - If no version suffix is present, "@v1" is appended.
    """
    idx: Dict[str, pathlib.Path] = {}
    base = ROOT / "contracts"
    if not base.exists():
        return idx
    for p in base.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            cid = str(data.get("id") or p.stem)
            if "@" not in cid:
                # enforce @vN suffix if missing using version in file or v1
                ver = str(data.get("version") or "v1")
                if not ver.startswith("v"):
                    ver = "v" + ver
                cid = f"{cid}@{ver}"
        except Exception:
            cid = p.stem
            if "@" not in cid:
                cid = cid + "@v1"
        idx[cid] = p
    return idx


def main():
    """Validate manifest-declared contract references and IDs.

    Scans module.manifest.json files for contract references and ensures the
    referenced contracts exist and that legacy event contract IDs are well-formed.

    Returns:
        None: Exits with code 1 on failures, 0 otherwise.
    """
    contracts = load_contract_index()
    failures = 0
    checked: int = 0
    unknown: Set[str] = set()
    bad_id: Set[str] = set()

    for mf in MANIFESTS:
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Could not read manifest {mf}: {e}")
            continue
        
        # Check module-level contracts array
        module_contracts = m.get("contracts", [])
        if module_contracts:
            for contract_path in module_contracts:
                checked += 1
                # Check if contract file exists
                full_path = ROOT / contract_path
                if not full_path.exists():
                    unknown.add(contract_path)
                    failures += 1
                    print(f"[FAIL] {mf}: contract file not found: {contract_path}")
        
        # Check observability event contracts (legacy format)
        ev = (m.get("observability", {}) or {}).get("events", {})
        for kind in ("publishes", "subscribes"):
            for item in ev.get(kind, []) or []:
                checked += 1
                stem = str(item)
                if not ID_RE.match(stem):
                    print(f"[FAIL] {mf}: invalid contract id: {stem}")
                    failures += 1
                    bad_id.add(stem)
                    continue
                if stem not in contracts:
                    unknown.add(stem)
                    failures += 1
                    # Suggest close matches by name part only
                    name = stem.split("@", 1)[0]
                    candidates = [c for c in contracts.keys() if c.startswith(name + "@")]
                    if not candidates:
                        candidates = list(contracts.keys())
                    hint = get_close_matches(stem, candidates, n=3)
                    if hint:
                        print(f"[FAIL] {mf}: unknown contract: {stem} — did you mean: {', '.join(hint)}?")
                    else:
                        print(f"[FAIL] {mf}: unknown contract: {stem}")

    print(
        f"Checked references: {checked} | Unknown: {len(unknown)} | Bad IDs: {len(bad_id)}"
    )
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
