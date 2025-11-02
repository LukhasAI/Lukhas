#!/usr/bin/env python3
"""
LUKHAS Vault Inventory Generator (T4/0.01%)

Parametric inventory system for THE_VAULT with multi-format support:
- .md files (standard docs)
- .pdf files (research papers - extract metadata)
- .json/.md chat logs (conversation archives)
- Media files (images, videos - hash + sidecar metadata)

Usage:
  python3 scripts/vault_inventory.py --root /path/to/THE_VAULT
"""

import argparse
import hashlib
import json
import mimetypes
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import PyPDF2

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 not available - PDF metadata extraction disabled")
    print("   Install with: pip install PyPDF2")

# Constants
DEFAULT_ROOT = Path(__file__).resolve().parents[1] / "docs"
EXCLUDED_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", ".DS_Store", "Thumbs.db"}

# File type handlers
FILE_HANDLERS = {
    ".md": "markdown",
    ".pdf": "pdf",
    ".json": "json",
    ".txt": "text",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".mp4": "video",
    ".webm": "video",
}


def sha256_file(filepath: Path) -> str:
    """Compute SHA256 hash of file content."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def extract_pdf_metadata(filepath: Path) -> Dict:
    """Extract metadata from PDF file."""
    if not PDF_AVAILABLE:
        return {}

    try:
        with open(filepath, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            info = reader.metadata or {}

            return {
                "title": info.get("/Title", ""),
                "author": info.get("/Author", ""),
                "subject": info.get("/Subject", ""),
                "creator": info.get("/Creator", ""),
                "producer": info.get("/Producer", ""),
                "creation_date": info.get("/CreationDate", ""),
                "page_count": len(reader.pages),
            }
    except Exception as e:
        return {"error": str(e)[:100]}


def detect_chat_log_origin(filepath: Path) -> Optional[str]:
    """Detect chat log origin from filename or content."""
    filename = filepath.name.lower()

    # Filename patterns
    if "chatgpt" in filename or "gpt-" in filename:
        return "ChatGPT"
    if "claude" in filename:
        return "Claude"
    if "gemini" in filename or "bard" in filename:
        return "Gemini"

    # Content patterns (for .json files)
    if filepath.suffix == ".json":
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read(500)  # First 500 chars
                if '"model": "gpt-' in content:
                    return "ChatGPT"
                if '"model": "claude-' in content:
                    return "Claude"
        except Exception:
            pass

    return None


def extract_front_matter(content: str) -> Dict:
    """Extract YAML front-matter from markdown content."""
    import re

    pattern = re.compile(r"^---\n(.*?)\n---", re.DOTALL | re.MULTILINE)
    match = pattern.match(content)

    if not match:
        return {}

    fm_text = match.group(1)
    fm_dict = {}

    for line in fm_text.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Parse boolean/null
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.lower() == "null":
                value = None

            fm_dict[key] = value

    return fm_dict


def process_file(filepath: Path, root: Path) -> Dict:
    """Process a single file and extract metadata."""
    rel_path = str(filepath.relative_to(root.parent))
    file_type = FILE_HANDLERS.get(filepath.suffix, "other")

    doc = {
        "path": rel_path,
        "type": file_type,
        "size_bytes": filepath.stat().st_size,
        "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
        "hash": sha256_file(filepath),
    }

    # Type-specific processing
    if file_type == "markdown":
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            fm = extract_front_matter(content)
            doc["front_matter"] = fm
            doc["has_front_matter"] = bool(fm)

            # Extract title from H1
            import re

            h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            doc["title"] = h1_match.group(1) if h1_match else filepath.stem

        except Exception as e:
            doc["error"] = str(e)[:100]

    elif file_type == "pdf":
        doc["pdf_metadata"] = extract_pdf_metadata(filepath)
        doc["title"] = doc["pdf_metadata"].get("title", filepath.stem)

    elif file_type == "json":
        # Detect chat log origin
        origin = detect_chat_log_origin(filepath)
        if origin:
            doc["chat_origin"] = origin
            doc["title"] = f"{origin} conversation"

    elif file_type in ["image", "video"]:
        # Store hash and basic metadata
        doc["title"] = filepath.stem
        doc["mime_type"] = mimetypes.guess_type(filepath)[0]

    return doc


def scan_vault(root: Path) -> Dict:
    """Scan vault directory and build inventory."""
    print(f"📂 Scanning {root}...")

    documents = []
    stats = defaultdict(int)

    for file_path in root.rglob("*"):
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in EXCLUDED_DIRS):
            continue

        # Skip directories
        if file_path.is_dir():
            continue

        # Process file
        try:
            doc = process_file(file_path, root)
            documents.append(doc)
            stats[doc["type"]] += 1

        except Exception as e:
            print(f"   ⚠️  Error processing {file_path}: {e}")
            stats["errors"] += 1

    # Build manifest
    manifest = {
        "root": str(root),
        "generated": datetime.now().isoformat(),
        "total_files": len(documents),
        "stats": dict(stats),
        "documents": documents,
    }

    return manifest


def generate_vault_index(manifest: Dict, output_dir: Path):
    """Generate VAULT_INDEX.md from manifest."""
    docs = manifest["documents"]
    stats = manifest["stats"]

    lines = [
        "# THE_VAULT Index",
        "",
        f"**Generated**: {manifest['generated']}",
        f"**Total Files**: {manifest['total_files']}",
        "",
        "## Statistics by Type",
        "",
        "| Type | Count |",
        "|------|-------|",
    ]

    for file_type, count in sorted(stats.items(), key=lambda x: -x[1]):
        lines.append(f"| {file_type} | {count} |")

    lines.extend(
        [
            "",
            "## Documents by Type",
            "",
        ]
    )

    # Group by type
    by_type = defaultdict(list)
    for doc in docs:
        by_type[doc["type"]].append(doc)

    for file_type in sorted(by_type.keys()):
        lines.append(f"### {file_type.upper()} ({len(by_type[file_type])} files)")
        lines.append("")

        for doc in sorted(by_type[file_type], key=lambda d: d["path"])[:50]:
            title = doc.get("title", Path(doc["path"]).stem)
            lines.append(f"- [{title}]({doc['path']})")

        if len(by_type[file_type]) > 50:
            lines.append(f"  - *... and {len(by_type[file_type]) - 50} more*")

        lines.append("")

    index_content = "\n".join(lines)
    index_path = output_dir / "VAULT_INDEX.md"

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    return index_path


def find_duplicates(manifest: Dict) -> List[List[Dict]]:
    """Find duplicate files by hash."""
    by_hash = defaultdict(list)

    for doc in manifest["documents"]:
        by_hash[doc["hash"]].append(doc)

    # Return groups with >1 file
    duplicates = [group for group in by_hash.values() if len(group) > 1]

    return duplicates


def generate_duplicates_report(duplicates: List[List[Dict]], output_dir: Path):
    """Generate VAULT_DUPLICATES.md report."""
    lines = [
        "# THE_VAULT Duplicate Files Report",
        "",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Duplicate Groups**: {len(duplicates)}",
        "",
        "## Summary",
        "",
    ]

    total_duplicates = sum(len(group) for group in duplicates)
    lines.append(f"Total duplicate files: {total_duplicates}")
    lines.append("")

    lines.append("## Duplicate Groups")
    lines.append("")

    for idx, group in enumerate(sorted(duplicates, key=lambda g: -len(g)), start=1):
        lines.append(f"### Group {idx} ({len(group)} files, hash: {group[0]['hash'][:16]}...)")
        lines.append("")

        for doc in group:
            title = doc.get("title", Path(doc["path"]).stem)
            size_kb = doc["size_bytes"] / 1024
            lines.append(f"- `{doc['path']}` - {title} ({size_kb:.1f} KB)")

        lines.append("")

    report_content = "\n".join(lines)
    report_path = output_dir / "VAULT_DUPLICATES.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path


def main():
    """Main workflow."""
    parser = argparse.ArgumentParser(description="Generate inventory for THE_VAULT or any document repository")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Root directory to scan (default: docs/)")
    parser.add_argument("--output", type=Path, help="Output directory for generated files (default: ROOT/_inventory)")

    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists():
        print(f"❌ Root directory not found: {root}")
        return 1

    output_dir = args.output or (root / "_inventory")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("LUKHAS Vault Inventory Generator (T4/0.01%)")
    print("=" * 80)
    print()

    # Scan
    manifest = scan_vault(root)

    # Save manifest
    manifest_path = output_dir / "vault_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"✅ Manifest: {manifest_path}")

    # Generate index
    index_path = generate_vault_index(manifest, output_dir)
    print(f"✅ Index: {index_path}")

    # Find duplicates
    duplicates = find_duplicates(manifest)
    if duplicates:
        dup_path = generate_duplicates_report(duplicates, output_dir)
        print(f"✅ Duplicates: {dup_path}")
        print(f"   Found {len(duplicates)} duplicate groups")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Root: {root}")
    print(f"Total files: {manifest['total_files']}")
    print()
    print("By type:")
    for file_type, count in sorted(manifest["stats"].items(), key=lambda x: -x[1]):
        print(f"  {file_type:15s}: {count:5d}")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
