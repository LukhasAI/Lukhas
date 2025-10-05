"""
T4/0.01% Atomic Writer with Append-Only Ledger
==============================================

All writes are:
1. Atomic (tmp file + rename)
2. Audited (ledger entry)
3. Deterministic (sorted keys)
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict


def atomic_write(path: Path, data: Dict):
    """
    Atomic write with deterministic JSON formatting.

    Steps:
    1. Write to .tmp file
    2. Atomic rename (os.replace)

    This prevents partial writes and race conditions.
    """
    # Ensure deterministic output
    content = json.dumps(data, indent=2, sort_keys=True) + "\n"

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content)

    # Atomic rename
    os.replace(tmp_path, path)


def ledger_append(root: Path, module_dir: Path, before: Dict, after: Dict):
    """
    Append audit record to module's ledger file.

    Format: NDJSON (newline-delimited JSON)
    Location: manifests/.ledger/<module>.ndjson

    Record schema:
    {
      "module": "consciousness",
      "timestamp": "2025-10-03T12:34:56.789Z",
      "sha": "abc123...",  // SHA1 of after manifest
      "diff_fields": ["features", "apis", "description"]
    }
    """
    ledger_dir = root / "manifests" / ".ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)

    module_name = module_dir.name
    ledger_file = ledger_dir / f"{module_name}.ndjson"

    # Compute SHA of resulting manifest
    manifest_json = json.dumps(after, sort_keys=True)
    sha = hashlib.sha1(manifest_json.encode()).hexdigest()

    # Find changed fields
    diff_fields = sorted(
        set(after.keys()) ^ set(before.keys()) |
        {k for k in after if before.get(k) != after.get(k)}
    )

    # Create audit record
    record = {
        "module": module_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sha": sha,
        "diff_fields": diff_fields
    }

    # Append to ledger (NDJSON format)
    with ledger_file.open("a") as f:
        f.write(json.dumps(record) + "\n")


def compute_content_hash(path: Path) -> str:
    """
    Compute SHA256 of file content.
    Used for --only-changed-sources optimization.
    """
    if not path.exists():
        return ""

    return hashlib.sha256(path.read_text().encode()).hexdigest()


def has_source_changed(module_dir: Path, last_hashes: Dict[str, str]) -> bool:
    """
    Check if any source files (claude.me, __init__.py, bench config) changed.

    Args:
        module_dir: Path to module directory
        last_hashes: Dict of {filename: sha256} from previous run

    Returns:
        True if any source changed since last enrichment
    """
    current_hashes = {}

    # Files to track
    sources = [
        "claude.me",
        "lukhas_context.md",
        "__init__.py",
        "module.manifest.json"  # Check if someone manually edited
    ]

    for source in sources:
        path = module_dir / source
        if path.exists():
            current_hashes[source] = compute_content_hash(path)

    # Compare with last run
    for filename, current_hash in current_hashes.items():
        if last_hashes.get(filename) != current_hash:
            return True

    return False
