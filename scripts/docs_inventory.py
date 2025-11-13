#!/usr/bin/env python3
"""
LUKHAS Documentation Inventory Builder

Scans all *.md files in docs/ and generates a complete manifest with metadata.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict

# Constants
DOCS_ROOT = Path(__file__).parent.parent / "docs"
OUTPUT_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = OUTPUT_DIR / "docs_manifest.json"

# Exclude patterns
EXCLUDE_DIRS = {
    ".git", ".vscode", "__pycache__", ".pytest_cache", "node_modules",
    "venv", ".venv", "dist", "build", "*.egg-info",
}

FRONT_MATTER_PATTERN = re.compile(
    r'^---\s*\n(.*?)\n---\s*\n',
    re.DOTALL | re.MULTILINE
)


def sha256_file(filepath: Path) -> str:
    """Compute SHA256 hash of file content."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def extract_front_matter(content: str) -> Dict | None:
    """Extract YAML front-matter from markdown content."""
    match = FRONT_MATTER_PATTERN.match(content)
    if not match:
        return None

    # Simple YAML parsing (key: value pairs only)
    front_matter = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            front_matter[key.strip()] = value.strip()

    return front_matter


def extract_title(content: str, filepath: Path) -> str:
    """Extract title from first H1 or front-matter or filename."""
    # Try front-matter first
    fm = extract_front_matter(content)
    if fm and 'title' in fm:
        return fm['title']

    # Try first H1
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()

    # Fallback to filename
    return filepath.stem.replace('_', ' ').replace('-', ' ').title()


def infer_module(filepath: Path, docs_root: Path) -> str:
    """Infer module name from file path."""
    rel_path = filepath.relative_to(docs_root)
    parts = rel_path.parts

    if len(parts) <= 1:
        return "root"

    # First directory is typically the module
    return parts[0]


def infer_type(filepath: Path, content: str) -> str:
    """Infer document type from path and content."""
    path_str = str(filepath).lower()
    name = filepath.stem.lower()

    # Check front-matter first
    fm = extract_front_matter(content)
    if fm and 'type' in fm:
        return fm['type']

    # Path-based inference
    if '/api/' in path_str or name.startswith('api_'):
        return 'api'
    if '/architecture/' in path_str or 'architecture' in name:
        return 'architecture'
    if '/guides/' in path_str or 'guide' in name:
        return 'guide'
    if '/reports/' in path_str or 'report' in name:
        return 'report'
    if '/adr/' in path_str or name.startswith('adr-'):
        return 'adr'
    if name in ('index', 'readme', 'documentation_index'):
        return 'index'

    return 'misc'


def infer_status(content: str) -> str:
    """Infer document status from front-matter or content."""
    fm = extract_front_matter(content)
    if fm and 'status' in fm:
        return fm['status']

    # Simple heuristics
    content_lower = content.lower()
    if 'wip' in content_lower or 'work in progress' in content_lower:
        return 'wip'
    if 'draft' in content_lower[:500]:  # Check first 500 chars
        return 'draft'
    if 'deprecated' in content_lower or 'obsolete' in content_lower:
        return 'deprecated'

    return 'stable'


def get_git_date(filepath: Path) -> str | None:
    """Get last commit date for file from git."""
    try:
        result = subprocess.run(
            ['git', 'log', '--format=%cs', '-n', '1', '--', str(filepath)],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=filepath.parent
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_updated_at(filepath: Path) -> str:
    """Get file update date (git or mtime)."""
    git_date = get_git_date(filepath)
    if git_date:
        return git_date

    # Fallback to mtime
    mtime = filepath.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')


def scan_docs(docs_root: Path) -> list[Dict]:
    """Scan all markdown files and collect metadata."""
    docs = []

    for md_file in docs_root.rglob("*.md"):
        # Skip excluded directories
        if any(excluded in md_file.parts for excluded in EXCLUDE_DIRS):
            continue

        # Skip generated/inventory directories
        if '_generated' in md_file.parts or '_inventory' in md_file.parts:
            continue

        try:
            with open(md_file, encoding='utf-8') as f:
                content = f.read()

            # Extract metadata
            fm = extract_front_matter(content)

            doc_info = {
                "path": str(md_file.relative_to(docs_root.parent)),
                "title": extract_title(content, md_file),
                "slug": md_file.stem,
                "owner": (fm.get('owner', 'unknown') if fm else 'unknown'),
                "module": infer_module(md_file, docs_root),
                "status": infer_status(content),
                "type": infer_type(md_file, content),
                "updated_at": get_updated_at(md_file),
                "sha256": sha256_file(md_file),
                "has_front_matter": fm is not None,
                "redirect": (fm.get('redirect', 'false') if fm else 'false') == 'true',
                "moved_to": (fm.get('moved_to', None) if fm else None),
            }

            docs.append(doc_info)

        except Exception as e:
            print(f"⚠️  Error processing {md_file}: {e}")
            continue

    return docs


def compute_metrics(docs: list[Dict]) -> Dict:
    """Compute inventory metrics."""
    total = len(docs)
    missing_fm = sum(1 for d in docs if not d['has_front_matter'])

    # Group by status, type, module
    by_status = {}
    by_type = {}
    by_module = {}

    for doc in docs:
        by_status[doc['status']] = by_status.get(doc['status'], 0) + 1
        by_type[doc['type']] = by_type.get(doc['type'], 0) + 1
        by_module[doc['module']] = by_module.get(doc['module'], 0) + 1

    # Find duplicates by hash
    hash_groups = {}
    for doc in docs:
        h = doc['sha256']
        if h not in hash_groups:
            hash_groups[h] = []
        hash_groups[h].append(doc['path'])

    exact_dupes = {h: paths for h, paths in hash_groups.items() if len(paths) > 1}

    return {
        "total_files": total,
        "missing_front_matter": missing_fm,
        "by_status": by_status,
        "by_type": by_type,
        "by_module": by_module,
        "exact_duplicates": len(exact_dupes),
        "exact_duplicate_groups": exact_dupes,
    }


def main():
    """Main inventory builder."""
    print("=" * 80)
    print("LUKHAS Documentation Inventory Builder")
    print("=" * 80)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Scan docs
    print(f"📂 Scanning {DOCS_ROOT}...")
    docs = scan_docs(DOCS_ROOT)
    docs.sort(key=lambda d: d['path'])

    # Compute metrics
    print("📊 Computing metrics...")
    metrics = compute_metrics(docs)

    # Write manifest
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "docs_root": str(DOCS_ROOT),
        "total_documents": len(docs),
        "metrics": metrics,
        "documents": docs,
    }

    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Manifest written to {MANIFEST_PATH}")
    print()

    # Print summary
    print("=" * 80)
    print("INVENTORY SUMMARY")
    print("=" * 80)
    print(f"Total documents: {metrics['total_files']}")
    print(f"Missing front-matter: {metrics['missing_front_matter']} ({metrics['missing_front_matter']/metrics['total_files']*100:.1f}%)")
    print(f"Exact duplicates: {metrics['exact_duplicates']} groups")
    print()

    print("By Status:")
    for status, count in sorted(metrics['by_status'].items(), key=lambda x: -x[1]):
        print(f"  {status:12s}: {count:4d}")
    print()

    print("By Type:")
    for typ, count in sorted(metrics['by_type'].items(), key=lambda x: -x[1]):
        print(f"  {typ:12s}: {count:4d}")
    print()

    print("By Module (top 10):")
    sorted_modules = sorted(metrics['by_module'].items(), key=lambda x: -x[1])[:10]
    for module, count in sorted_modules:
        print(f"  {module:20s}: {count:4d}")
    print()

    if metrics['exact_duplicates'] > 0:
        print("Exact Duplicate Groups:")
        for hash_val, paths in list(metrics['exact_duplicate_groups'].items())[:5]:
            print(f"  Hash: {hash_val[:16]}...")
            for path in paths:
                print(f"    - {path}")
            print()

    print("=" * 80)
    print(f"✅ Phase 1 Complete - Inventory manifest: {MANIFEST_PATH}")
    print("=" * 80)


if __name__ == "__main__":
    main()
