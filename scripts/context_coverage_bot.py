#!/usr/bin/env python3
"""
Context Coverage Bot

Computes coverage for manifests having a lukhas_context.md with valid-looking
front-matter. Writes a small report and exits non-zero if coverage is below
the specified threshold.

Usage:
  python scripts/context_coverage_bot.py --manifests manifests --min 0.95
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

FM_START = re.compile(r"^\s*---\s*$")
FM_END = re.compile(r"^\s*---\s*$")


def has_front_matter(p: pathlib.Path) -> bool:
    """Check if a file contains valid YAML front matter.

    Validates that the file begins with a '---' delimiter and contains a closing
    '---' delimiter within the first 200 lines. Used to verify context files have
    been migrated to the new front-matter format.

    Args:
        p: Path to the file to check for front matter.

    Returns:
        bool: True if valid front matter block found (opening and closing '---'),
            False if file cannot be read, has no content, or lacks proper delimiters.

    Example:
        >>> has_front_matter(Path("manifests/core/module/lukhas_context.md"))
        True
        >>> has_front_matter(Path("legacy_file.md"))
        False
    """
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    lines = text.splitlines()
    if not lines or not FM_START.match(lines[0]):
        return False
    return any(FM_END.match(lines[i]) for i in range(1, min(len(lines), 200)))


def main():
    """Compute and validate context file front-matter coverage.

    Scans all module.manifest.json files in the manifests directory (excluding
    archives), checks for sibling lukhas_context.md files, and validates whether
    they contain proper YAML front matter. Generates a coverage report and exits
    with non-zero status if coverage is below the specified threshold.

    This is used in CI to enforce documentation quality standards and prevent
    regression to legacy context file formats.

    Args:
        CLI args (via argparse):
            --manifests: Root directory containing manifests. Defaults to "manifests".
            --min: Minimum front-matter coverage threshold (0.0-1.0). Defaults to 0.95.
            --report: Output report path. Defaults to "docs/audits/context_coverage.txt".

    Raises:
        SystemExit: Exits with code 1 if front-matter coverage is below threshold.

    Example:
        $ python scripts/context_coverage_bot.py --min 0.95
        Front-matter coverage: 96.5% (threshold 95%)
        Debug: all=150 filtered=145 skipped=5
        (exits 0)

        $ python scripts/context_coverage_bot.py --min 0.98
        Front-matter coverage: 96.5% (threshold 98%)
        (exits 1 - below threshold)
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifests", default="manifests")
    ap.add_argument("--min", type=float, default=0.95)
    ap.add_argument("--report", default="docs/audits/context_coverage.txt")
    args = ap.parse_args()

    root = pathlib.Path(args.manifests)
    all_files = list(root.rglob("module.manifest.json"))
    def is_archived(path: pathlib.Path) -> bool:
        """Check if a path contains an archived directory component.

        Args:
            path: Path to check for archive markers.

        Returns:
            bool: True if any path component is '.archive', False otherwise.
        """
        return any(part == ".archive" for part in path.parts)
    manifest_files = [p for p in all_files if not is_archived(p)]
    ctx_files = [mf.parent / "lukhas_context.md" for mf in manifest_files]

    present = [p for p in ctx_files if p.exists()]
    with_fm = [p for p in present if has_front_matter(p)]

    total = len(manifest_files)
    present_pct = (len(present) / total) if total else 1.0
    fm_pct = (len(with_fm) / total) if total else 1.0

    out = pathlib.Path(args.report)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        (
            f"Context coverage report\n"
            f"Manifests: {total}\n"
            f"Context files present: {len(present)} ({present_pct:.1%})\n"
            f"With front-matter: {len(with_fm)} ({fm_pct:.1%})\n"
            f"Threshold (front-matter): {args.min:.0%}\n"
        ),
        encoding="utf-8",
    )

    skipped = len(all_files) - total
    print(f"Front-matter coverage: {fm_pct:.1%} (threshold {args.min:.0%})")
    print(f"Debug: all={len(all_files)} filtered={total} skipped={skipped}")
    if fm_pct + 1e-9 < args.min:
        sys.exit(1)


if __name__ == "__main__":
    main()
