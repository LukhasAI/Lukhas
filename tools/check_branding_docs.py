#!/usr/bin/env python3
"""
Branding Docs Drift Detector

Compares source files in docs/web with their canonical copies in branding/websites
to detect divergence. This ensures content governance and prevents accidental
updates to legacy docs/web locations after migration.

Usage:
    python3 tools/check_branding_docs.py

Exit codes:
    0 - All mapped files match
    1 - Usage error
    2 - Drift detected (files don't match)
"""

import hashlib
import sys
from pathlib import Path
from typing import Optional

# Mapping: source (docs/web) -> destination (branding/websites)
# Note: These are the canonical mappings after migration.
# The branding files should be the authoritative versions going forward.
MAPPING = {
    # Content management and governance
    "docs/web/content/shared/CONTENT_MANAGEMENT_GUIDE.md":
        "branding/websites/_content_management/CONTENT_MANAGEMENT_GUIDE.md",
    "docs/web/content/shared/vocabulary-usage/VOCABULARY_STANDARDS_QUICK_REFERENCE.md":
        "branding/websites/_content_management/vocabulary.md",

    # lukhas.dev landing (production-ready developer content)
    "docs/web/content/domains/lukhas-dev/landing_page.md":
        "branding/websites/lukhas.dev/homepage.md",
}

def sha256(p: Path) -> Optional[str]:
    """Compute SHA256 hash of file contents."""
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check_file_pair(src_path: str, dst_path: str) -> tuple:
    """
    Check if source and destination files match.

    Returns:
        (src_path, dst_path, status) where status is:
        - None: files match
        - "missing-source": source file doesn't exist
        - "missing-dest": destination file doesn't exist
        - "changed": files exist but content differs
    """
    src = Path(src_path)
    dst = Path(dst_path)

    src_hash = sha256(src)
    dst_hash = sha256(dst)

    if src_hash is None:
        return (src_path, dst_path, "missing-source")
    if dst_hash is None:
        return (src_path, dst_path, "missing-dest")
    if src_hash != dst_hash:
        return (src_path, dst_path, "changed")

    return (src_path, dst_path, None)

def main() -> int:
    """Main entry point."""
    print("🔍 Checking branding/websites against docs/web sources...\n")

    issues = []

    for src, dst in MAPPING.items():
        src_path, dst_path, status = check_file_pair(src, dst)

        if status is None:
            print(f"✅ {dst}")
            print(f"   (matches {src})")
        elif status == "missing-source":
            print(f"⚠️  MISSING SOURCE: {src}")
            print(f"   Expected to copy to: {dst}")
            issues.append((src, dst, status))
        elif status == "missing-dest":
            print(f"⚠️  MISSING DEST: {dst}")
            print(f"   Expected to match: {src}")
            issues.append((src, dst, status))
        elif status == "changed":
            print(f"❌ DRIFT DETECTED: {dst}")
            print(f"   Does not match source: {src}")
            print(f"   → Content has diverged. Review and reconcile.")
            issues.append((src, dst, status))

    print()

    if issues:
        print(f"❌ Found {len(issues)} issue(s):")
        for src, dst, status in issues:
            print(f"   - {status}: {src} → {dst}")
        print()
        print("Action required:")
        print("  • Review differences between source and destination")
        print("  • If branding/ is correct, update docs/web (legacy)")
        print("  • If docs/web is correct, update branding/ (canonical)")
        print("  • Per migration plan, branding/websites/ should be authoritative")
        return 2

    print("✅ All mapped branding documents match their docs/web sources.")
    print("   No drift detected. Content governance is maintained.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
