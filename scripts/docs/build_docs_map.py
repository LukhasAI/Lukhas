#!/usr/bin/env python3
"""
Build documentation mapping with confidence scoring.

Scans all .md files and assigns them to modules based on:
1. Explicit frontmatter `module:` field (confidence: 1.0)
2. Path-based inference (confidence: 0.8)
3. Keyword matching (confidence: 0.5)
4. Unknown (confidence: 0.0)

Outputs:
  - artifacts/docs_mapping.json: Complete mapping with confidence scores
  - artifacts/docs_mapping_review.md: Human-readable review of <0.80 items
"""
import json
import re
import sys
from pathlib import Path
from typing import Dict, Optional

import yaml

ART = Path("artifacts")
ART.mkdir(exist_ok=True, parents=True)

EXCLUDE_DIRS = {
    ".venv", ".venv_*", "venv", "__pycache__", ".pytest_cache",
    "node_modules", ".git", "dist", "build", "*.egg-info", "htmlcov"
}


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from scanning."""
    for part in path.parts:
        if any(re.match(pattern.replace("*", ".*"), part) for pattern in EXCLUDE_DIRS):
            return True
    return False


def extract_frontmatter(md_path: Path) -> Optional[Dict]:
    """Extract YAML frontmatter from markdown file."""
    try:
        content = md_path.read_text()
        if not content.startswith("---"):
            return None

        parts = content.split("---", 2)
        if len(parts) < 3:
            return None

        return yaml.safe_load(parts[1])
    except Exception as e:
        print(f"⚠️  Error parsing frontmatter in {md_path}: {e}", file=sys.stderr)
        return None


def infer_module_from_path(md_path: Path) -> Optional[str]:
    """Infer module from file path (e.g., docs/consciousness/... -> consciousness)."""
    parts = md_path.parts

    # Check if under docs/<module>/
    if "docs" in parts:
        docs_idx = parts.index("docs")
        if docs_idx + 1 < len(parts):
            return parts[docs_idx + 1]

    # Check if already in module directory (e.g., consciousness/docs/...)
    if "docs" in parts:
        docs_idx = parts.index("docs")
        if docs_idx > 0:
            candidate = parts[docs_idx - 1]
            # Verify it's likely a module (has module.manifest.json)
            manifest = md_path.parent.parent / "module.manifest.json"
            if manifest.exists():
                return candidate

    return None


def infer_module_from_keywords(md_path: Path) -> Optional[str]:
    """Infer module from file content keywords (low confidence)."""
    try:
        content = md_path.read_text().lower()

        # Common module keywords
        keywords = {
            "consciousness": ["consciousness", "awareness", "phenomenology", "qualia"],
            "memory": ["memory", "fold", "cascade", "retention"],
            "identity": ["identity", "authentication", "webauthn", "lambda id"],
            "governance": ["governance", "guardian", "ethics", "constitutional"],
            "matriz": ["matriz", "cognitive", "symbolic dna"],
            "orchestration": ["orchestration", "pipeline", "workflow"],
        }

        for module, terms in keywords.items():
            if any(term in content for term in terms):
                return module

    except Exception:
        pass

    return None


def build_mapping() -> Dict[str, Dict]:
    """Build complete documentation mapping with confidence scores."""
    mapping = {}
    root = Path(".")

    for md_path in root.rglob("*.md"):
        if should_exclude(md_path):
            continue

        rel_path = str(md_path)
        module = None
        confidence = 0.0
        strategy = "unknown"

        # Strategy 1: Explicit frontmatter (highest confidence)
        frontmatter = extract_frontmatter(md_path)
        if frontmatter and isinstance(frontmatter, dict) and "module" in frontmatter and frontmatter["module"]:
            module = frontmatter["module"]
            confidence = 1.0
            strategy = "frontmatter"

        # Strategy 2: Path-based inference (high confidence)
        elif inferred := infer_module_from_path(md_path):
            module = inferred
            confidence = 0.8
            strategy = "path"

        # Strategy 3: Keyword matching (medium confidence)
        elif inferred := infer_module_from_keywords(md_path):
            module = inferred
            confidence = 0.5
            strategy = "keywords"

        # Strategy 4: Unknown (keep in root docs/)
        else:
            module = "root"
            confidence = 0.0
            strategy = "unknown"

        mapping[rel_path] = {
            "module": module,
            "confidence": confidence,
            "strategy": strategy,
            "frontmatter": frontmatter or {}
        }

    return mapping


def generate_review_report(mapping: Dict[str, Dict]) -> str:
    """Generate human-readable review report for <0.80 confidence items."""
    lines = []
    lines.append("# Documentation Mapping Review")
    lines.append("")
    lines.append("Items with confidence <0.80 need manual review:")
    lines.append("")

    # Group by strategy
    by_strategy = {}
    for path, info in mapping.items():
        if info["confidence"] < 0.80:
            strategy = info["strategy"]
            by_strategy.setdefault(strategy, []).append((path, info))

    # Unknown files (confidence 0.0)
    if "unknown" in by_strategy:
        lines.append(f"## Unknown Module Assignment ({len(by_strategy['unknown'])} files)")
        lines.append("")
        lines.append("These files could not be assigned to a module. Options:")
        lines.append("1. Add `module: <name>` to frontmatter")
        lines.append("2. Move to appropriate module docs/ directory")
        lines.append("3. Add `module: root` to keep in root docs/")
        lines.append("")
        for path, info in sorted(by_strategy["unknown"])[:20]:
            lines.append(f"- `{path}` (strategy: {info['strategy']})")
        if len(by_strategy["unknown"]) > 20:
            lines.append(f"- ... and {len(by_strategy['unknown']) - 20} more")
        lines.append("")

    # Keyword-based (confidence 0.5)
    if "keywords" in by_strategy:
        lines.append(f"## Keyword-Based Assignment ({len(by_strategy['keywords'])} files)")
        lines.append("")
        lines.append("These were assigned based on content keywords. Verify correctness:")
        lines.append("")
        for path, info in sorted(by_strategy["keywords"])[:20]:
            lines.append(f"- `{path}` → `{info['module']}` (confidence: {info['confidence']})")
        if len(by_strategy["keywords"]) > 20:
            lines.append(f"- ... and {len(by_strategy['keywords']) - 20} more")
        lines.append("")

    # Summary stats
    total = len(mapping)
    high_confidence = sum(1 for i in mapping.values() if i["confidence"] >= 0.80)
    review_needed = total - high_confidence

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total markdown files: {total}")
    lines.append(f"- High confidence (≥0.80): {high_confidence} ({high_confidence/total*100:.1f}%)")
    lines.append(f"- Review needed (<0.80): {review_needed} ({review_needed/total*100:.1f}%)")
    lines.append("")
    lines.append("## Next Steps")
    lines.append("")
    lines.append("1. Review files listed above")
    lines.append("2. Add `module:` frontmatter or move files as needed")
    lines.append("3. Re-run: `make docs-map`")
    lines.append("4. When review queue <10 items: `make docs-migrate-auto`")

    return "\n".join(lines)


def main():
    print("🔍 Building documentation mapping...")

    mapping = build_mapping()

    # Write JSON mapping
    json_path = ART / "docs_mapping.json"
    json_path.write_text(json.dumps(mapping, indent=2, sort_keys=True))
    print(f"✅ Wrote {json_path} ({len(mapping)} files)")

    # Write review report
    review_path = ART / "docs_mapping_review.md"
    review_path.write_text(generate_review_report(mapping))
    print(f"✅ Wrote {review_path}")

    # Print summary stats
    total = len(mapping)
    high_confidence = sum(1 for i in mapping.values() if i["confidence"] >= 0.80)
    review_needed = total - high_confidence

    print("\n📊 Summary:")
    print(f"  Total files: {total}")
    print(f"  High confidence (≥0.80): {high_confidence} ({high_confidence/total*100:.1f}%)")
    print(f"  Review needed (<0.80): {review_needed} ({review_needed/total*100:.1f}%)")

    if review_needed > 0:
        print(f"\n⚠️  {review_needed} files need review")
        print(f"   See: {review_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
