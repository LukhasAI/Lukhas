#!/usr/bin/env python3
"""
Migrate legacy lukhas_context.md files to YAML front-matter.

For each lukhas_context.md under manifests/**:
- If already has a front-matter block (--- ... ---) at top, skip.
- Parse legacy header fields (Star, MATRIZ Nodes, Colony) when present.
- Read sibling module.manifest.json to fill required keys: tier, owner, matriz nodes (fallback to parsed).
- Prepend YAML front-matter:
    required keys: star, tier, matriz (list), owner
    recommended: module, colony, manifest_path
- Preserve the existing markdown body (with legacy header lines removed).

Exit non-zero if any files fail to process.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[1]
FM_BOUNDARY = re.compile(r"^\s*---\s*$")


def has_front_matter(text: str) -> bool:
    """Check if text contains valid YAML front matter delimiters.

    Validates that the text begins with a '---' delimiter and contains a closing
    '---' delimiter within the first 200 lines. Used to skip files that have
    already been migrated to the front-matter format.

    Args:
        text: Raw text content to check for front matter.

    Returns:
        bool: True if valid front matter block found (opening and closing '---'),
            False if text is empty or lacks proper delimiters.

    Example:
        >>> has_front_matter("---\\nkey: value\\n---\\nBody text")
        True
        >>> has_front_matter("# Legacy Header\\nBody text")
        False
    """
    lines = text.splitlines()
    if not lines:
        return False
    if not FM_BOUNDARY.match(lines[0]):
        return False
    # find end within first 200 lines
    return any(FM_BOUNDARY.match(lines[i]) for i in range(1, min(len(lines), 200)))


def read_manifest(md_path: pathlib.Path) -> Dict | None:
    """Read and parse the sibling module.manifest.json file.

    Looks for module.manifest.json in the same directory as the given markdown
    file path. Used to extract tier, owner, and MATRIZ node information when
    migrating legacy context files.

    Args:
        md_path: Path to the lukhas_context.md file (used to locate sibling manifest).

    Returns:
        dict: Parsed manifest JSON as dictionary if file exists and is valid,
            None if file doesn't exist or cannot be parsed.

    Example:
        >>> read_manifest(Path("manifests/core/identity/lukhas_context.md"))
        {'module': {'name': 'identity'}, 'testing': {'quality_tier': 'T1_critical'}, ...}
        >>> read_manifest(Path("missing/lukhas_context.md"))
        None
    """
    mf = md_path.parent / "module.manifest.json"
    if not mf.exists():
        return None
    try:
        return json.loads(mf.read_text(encoding="utf-8"))
    except Exception:
        return None


def parse_legacy_header(text: str) -> dict[str, str | None]:
    """Extract metadata from legacy context file header format.

    Scans the first 40 lines of a context file to find legacy header fields
    formatted as bold markdown keys (e.g., "**Star**: Identity"). Extracts
    star, MATRIZ nodes, colony, and title information for migration to YAML
    front matter.

    Args:
        text: Full text content of the context file.

    Returns:
        dict: Dictionary with keys 'star', 'matriz', 'colony', 'title', each
            containing the extracted string value or None if not found.

    Example:
        >>> parse_legacy_header("# Identity\\n**Star**: Identity\\n**MATRIZ Nodes**: M, A")
        {'star': 'Identity', 'matriz': 'M, A', 'colony': None, 'title': 'Identity'}
        >>> parse_legacy_header("# No metadata")
        {'star': None, 'matriz': None, 'colony': None, 'title': 'No metadata'}
    """
    fields = {"star": None, "matriz": None, "colony": None, "title": None}
    lines = text.splitlines()
    for line in lines[:40]:
        if not fields["title"] and line.startswith("# "):
            fields["title"] = line[2:].strip()
        m = re.match(r"\*\*Star\*\*:\s*(.+)\s*$", line)
        if m:
            fields["star"] = m.group(1).strip()
            continue
        m = re.match(r"\*\*MATRIZ Nodes\*\*:\s*(.+)\s*$", line)
        if m:
            fields["matriz"] = m.group(1).strip()
            continue
        m = re.match(r"\*\*Colony\*\*:\s*(.+)\s*$", line)
        if m:
            fields["colony"] = m.group(1).strip()
            continue
    return fields


def sanitize_nodes(nodes_str: str | None) -> list[str]:
    """Parse and normalize MATRIZ node string to list of node codes.

    Splits a comma or whitespace-separated string of MATRIZ node codes into
    a cleaned list. Handles various legacy formats like "M, A, T" or "M A T"
    and normalizes them to ["M", "A", "T"].

    Args:
        nodes_str: Raw string containing MATRIZ node codes, may be comma or
            whitespace separated, or None.

    Returns:
        list[str]: List of cleaned, non-empty node code strings. Empty list
            if input is None or contains no valid nodes.

    Example:
        >>> sanitize_nodes("M, A, T")
        ['M', 'A', 'T']
        >>> sanitize_nodes("M   A   T")
        ['M', 'A', 'T']
        >>> sanitize_nodes(None)
        []
        >>> sanitize_nodes("")
        []
    """
    if not nodes_str:
        return []
    # split on commas or whitespace
    parts = re.split(r"[\s,]+", nodes_str)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def to_front_matter(data: dict[str, object]) -> str:
    """Generate YAML front matter block from metadata dictionary.

    Converts a metadata dictionary to a YAML front-matter block suitable for
    prepending to context files. Outputs required keys (module, star, tier,
    owner) and optional keys (colony, manifest_path), followed by matriz as
    a YAML array.

    Args:
        data: Dictionary containing metadata keys. Expected keys include:
            - module: Module name (str)
            - star: Constellation star (str)
            - tier: Quality tier (str, e.g., "T1_critical")
            - owner: Module owner (str)
            - matriz: List of MATRIZ node codes (list[str])
            - colony: Optional colony name (str)
            - manifest_path: Optional path to manifest file (str)

    Returns:
        str: Complete YAML front matter block including delimiters (---),
            formatted as multi-line string with trailing newline.

    Example:
        >>> to_front_matter({"module": "identity", "star": "Identity", "tier": "T1_critical",
        ...                  "owner": "security@lukhas", "matriz": ["M", "A"]})
        '---\\nmodule: identity\\nstar: Identity\\ntier: T1_critical\\nowner: security@lukhas\\nmatriz: [M, A]\\n---\\n'
    """
    # minimal YAML writer for simple scalars and str lists
    lines = ["---"]
    for k in ("module", "star", "tier", "owner", "colony", "manifest_path"):
        v = data.get(k)
        if v is None:
            continue
        lines.append(f"{k}: {v}")
    matriz = data.get("matriz") or []
    if matriz:
        arr = ", ".join(str(x) for x in matriz)
        lines.append(f"matriz: [{arr}]")
    else:
        lines.append("matriz: []")
    lines.append("---")
    return "\n".join(lines) + "\n"


def remove_legacy_header(text: str) -> str:
    """Remove legacy header fields from context file body.

    Strips legacy bold markdown header lines (Star, MATRIZ Nodes, Colony) and
    trailing empty lines from the first 40 lines of text. Preserves all other
    content including the title and body text. Used during migration to avoid
    duplicate metadata after adding YAML front matter.

    Args:
        text: Full text content of the context file including legacy headers.

    Returns:
        str: Text with legacy header lines removed, leading whitespace trimmed,
            and trailing newline preserved if original had content.

    Example:
        >>> remove_legacy_header("# Module\\n**Star**: Identity\\n\\nBody text")
        '# Module\\n\\nBody text\\n'
        >>> remove_legacy_header("**MATRIZ Nodes**: M, A\\n\\nContent")
        'Content\\n'
    """
    lines = text.splitlines()
    keep: list[str] = []
    skip_prefixes = (
        "**Star**:",
        "**MATRIZ Nodes**:",
        "**Colony**:",
    )
    skipped = 0
    for i, line in enumerate(lines):
        if i < 40 and (line.startswith(skip_prefixes) or line.strip() == ""):
            # allow skipping empty lines immediately following header block
            skipped += 1
            continue
        keep = lines[i:]
        break
    return "\n".join(keep).lstrip("\n") + ("\n" if keep else "")


def migrate_one(md_path: pathlib.Path) -> str | None:
    """Migrate a single context file to YAML front-matter format.

    Orchestrates the migration of one lukhas_context.md file by combining
    legacy header parsing, manifest reading, front-matter generation, and
    legacy header removal. If the file already has front matter, returns None
    to skip re-processing.

    The function implements a fallback strategy: manifest values take precedence,
    then legacy header values, then sensible defaults (e.g., T4_experimental,
    unassigned).

    Args:
        md_path: Path to the lukhas_context.md file to migrate.

    Returns:
        str: New file content with YAML front matter prepended and legacy header
            removed, or None if file already has front matter (skip migration).

    Example:
        >>> migrate_one(Path("manifests/core/identity/lukhas_context.md"))
        '---\\nmodule: identity\\nstar: Identity\\ntier: T1_critical\\n...\\n---\\n# Identity\\n...'
        >>> migrate_one(Path("already_migrated.md"))
        None
    """
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    if has_front_matter(text):
        return None  # already good

    legacy = parse_legacy_header(text)
    manifest = read_manifest(md_path) or {}

    module = (manifest.get("module", {}) or {}).get("name") or legacy.get("title") or md_path.parent.name
    tier = (manifest.get("testing", {}) or {}).get("quality_tier") or "T4_experimental"
    owner = (manifest.get("metadata", {}) or {}).get("owner") or "unassigned"
    star = legacy.get("star") or (manifest.get("constellation_alignment", {}) or {}).get("primary_star") or "Supporting"
    matriz_nodes = (manifest.get("matriz_integration", {}) or {}).get("pipeline_nodes") or sanitize_nodes(legacy.get("matriz"))
    colony = legacy.get("colony") or (manifest.get("module", {}) or {}).get("colony")

    fm = {
        "module": module,
        "star": star,
        "tier": tier,
        "owner": owner,
        "matriz": matriz_nodes or [],
        "colony": colony or "",
        "manifest_path": str(md_path.parent / "module.manifest.json"),
    }

    header = to_front_matter(fm)
    body = remove_legacy_header(text)
    return header + body


def main():
    """Migrate all legacy context files to YAML front-matter format.

    Recursively scans the manifests directory for lukhas_context.md files,
    checks if they already have front matter, and if not, extracts legacy
    header fields and sibling manifest data to generate proper YAML front
    matter. Updates files in place unless --dry-run is specified.

    The migration preserves all body content while adding structured metadata
    required for documentation tooling and quality gates.

    Args:
        CLI args (via argparse):
            --root: Root directory to scan for context files. Defaults to "manifests".
            --dry-run: If True, only print what would be changed without modifying files.

    Raises:
        SystemExit: Exits with code 1 if any files fail to process.

    Example:
        $ python scripts/migrate_context_front_matter.py --dry-run
        [DRY] Would add front-matter: manifests/core/identity/lukhas_context.md
        Changed: 15 | Failed: 0 | Total scanned: 145

        $ python scripts/migrate_context_front_matter.py
        [OK] Front-matter added: manifests/core/identity/lukhas_context.md
        Changed: 15 | Failed: 0 | Total scanned: 145
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "manifests"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    files = sorted(root.rglob("lukhas_context.md"))
    changed = 0
    failed = 0
    for p in files:
        try:
            new_text = migrate_one(p)
        except Exception as e:
            print(f"[ERROR] {p}: {e}")
            failed += 1
            continue
        if new_text is None:
            continue
        if args.dry_run:
            print(f"[DRY] Would add front-matter: {p}")
        else:
            p.write_text(new_text, encoding="utf-8")
            print(f"[OK] Front-matter added: {p}")
        changed += 1

    print(f"Changed: {changed} | Failed: {failed} | Total scanned: {len(files)}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

