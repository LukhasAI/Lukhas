#!/usr/bin/env python3
"""
Sync owners in module.manifest.json for T1/T2 modules.

For each manifest (excluding .archive):
- If testing.quality_tier is T1_critical or T2_important and metadata.owner is
  missing/unassigned, set owner to triage@lukhas and update last_updated.
"""
from __future__ import annotations

import datetime
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def is_archived(path: pathlib.Path) -> bool:
    """Check if a path contains an archived directory component.

    Determines whether a file path includes '.archive' as any directory component,
    indicating the file belongs to archived/deprecated modules that should be
    excluded from active processing.

    Args:
        path: File path to check for archive markers.

    Returns:
        bool: True if '.archive' appears in any path component, False otherwise.

    Example:
        >>> is_archived(Path("manifests/.archive/old_module/module.manifest.json"))
        True
        >>> is_archived(Path("manifests/core/identity/module.manifest.json"))
        False
    """
    return any(part == ".archive" for part in path.parts)


def now_iso() -> str:
    """Generate current UTC timestamp in ISO 8601 format.

    Creates a timestamp string suitable for manifest metadata updates,
    formatted as ISO 8601 with Zulu (UTC) timezone indicator. Microseconds
    are truncated for cleaner timestamps in manifest files.

    Returns:
        str: Current UTC timestamp in format "YYYY-MM-DDTHH:MM:SSZ".

    Example:
        >>> now_iso()
        '2025-10-20T14:32:15Z'
    """
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def main() -> None:
    """Assign triage owner to T1/T2 manifests with missing owners.

    Scans all module.manifest.json files in the repository (excluding archives),
    identifies T1_critical and T2_important modules without explicit owners,
    and assigns them to 'triage@lukhas' for ownership tracking. Updates the
    last_updated timestamp and writes changes back to disk.

    This enforces the policy that high-tier modules must have explicit ownership
    for accountability and maintenance tracking.

    Returns:
        None: Prints progress to stdout and modifies manifest files in place.

    Raises:
        No explicit raises, but silently continues on read/parse errors for
        individual manifests to process all discoverable files.

    Example:
        $ python scripts/sync_t12_manifest_owners.py
        [OK] owner synced: manifests/core/identity/module.manifest.json
        [OK] owner synced: manifests/lukhas/governance/module.manifest.json
        Changed: 2
    """
    changed = 0
    for mf in ROOT.rglob("module.manifest.json"):
        if is_archived(mf):
            continue
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            continue
        tier = (data.get("testing", {}) or {}).get("quality_tier") or ""
        if tier not in ("T1_critical", "T2_important"):
            continue
        meta = data.setdefault("metadata", {})
        owner = (meta.get("owner") or "").strip().lower()
        if owner in ("", "unassigned", "none", "-"):
            meta["owner"] = "triage@lukhas"
            meta["last_updated"] = now_iso()
            mf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"[OK] owner synced: {mf}")
            changed += 1
    print(f"Changed: {changed}")


if __name__ == "__main__":
    main()

