#!/usr/bin/env python3
"""
LUKHAS Pre-Launch Audit - Phase 6: Documentation Quality Assessment
Analyzes documentation completeness, quality, and identifies gaps.
"""

import hashlib
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
AUDIT_DATA_DIR = ROOT_DIR / "audit_2025_launch" / "data"
AUDIT_REPORTS_DIR = ROOT_DIR / "audit_2025_launch" / "reports"

EXCLUDE_PATTERNS = [
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".venv", "venv", "env",
    "dist", "build", "*.egg-info",
    "node_modules", ".git", ".vscode", ".idea",
]

REQUIRED_DOCS = ["README.md", "claude.me", "lukhas_context.md"]
OPTIONAL_DOCS = ["ARCHITECTURE.md", "API.md", "CONTRIBUTING.md", "CHANGELOG.md"]

def should_exclude(path: Path) -> bool:
    """Check if path should be excluded."""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

def discover_all_docs():
    """Discover all markdown documentation files."""
    docs = []

    print("  Discovering markdown files...")
    for md_file in ROOT_DIR.rglob("*.md"):
        if should_exclude(md_file):
            continue

        try:
            docs.append({
                "path": str(md_file.relative_to(ROOT_DIR)),
                "absolute_path": str(md_file),
                "name": md_file.name,
                "size": md_file.stat().st_size,
                "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(),
                "directory": str(md_file.parent.relative_to(ROOT_DIR))
            })
        except (FileNotFoundError, OSError):
            # Skip broken symlinks
            pass

    print(f"  Found {len(docs)} markdown files")
    return docs

def check_module_documentation():
    """Check if major modules have required documentation."""
    major_modules = [
        "lukhas", "candidate", "matriz", "core",
        "docs", "tests", "branding", "mcp-servers",
        "scripts", "tools", "utils"
    ]

    module_docs = {}

    for module in major_modules:
        module_path = ROOT_DIR / module
        if not module_path.exists():
            continue

        existing = []
        missing = []

        for req_doc in REQUIRED_DOCS:
            doc_path = module_path / req_doc
            if doc_path.exists():
                existing.append(req_doc)
            else:
                missing.append(req_doc)

        optional_existing = []
        for opt_doc in OPTIONAL_DOCS:
            doc_path = module_path / opt_doc
            if doc_path.exists():
                optional_existing.append(opt_doc)

        completeness = len(existing) / len(REQUIRED_DOCS) if REQUIRED_DOCS else 0

        module_docs[module] = {
            "exists": True,
            "required_existing": existing,
            "required_missing": missing,
            "optional_existing": optional_existing,
            "completeness": round(completeness * 100, 1)
        }

    return module_docs

def analyze_doc_quality(doc_file):
    """Analyze quality metrics for a documentation file."""
    try:
        with open(doc_file["absolute_path"], encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Basic metrics
        word_count = len(content.split())
        line_count = content.count('\n')
        char_count = len(content)

        # Quality indicators
        has_code_examples = bool(re.search(r'```', content))
        code_block_count = len(re.findall(r'```', content)) // 2

        has_links = bool(re.search(r'\[.*?\]\(.*?\)', content))
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', content))

        has_headers = bool(re.search(r'^#+\s+', content, re.MULTILINE))
        header_count = len(re.findall(r'^#+\s+', content, re.MULTILINE))

        has_lists = bool(re.search(r'^\s*[-*+]\s+', content, re.MULTILINE))

        # Issue indicators
        todo_count = len(re.findall(r'TODO|FIXME', content, re.IGNORECASE))
        has_placeholder = bool(re.search(r'TODO|FIXME|XXX|TBD|PLACEHOLDER', content, re.IGNORECASE))

        # Check for outdated references
        years = re.findall(r'\b(20\d{2})\b', content)
        has_old_year = any(int(year) < 2024 for year in years)

        # Check for broken links (local references only)
        local_links = re.findall(r'\[.*?\]\(([^http].*?)\)', content)
        broken_links = []
        for link in local_links:
            # Clean link (remove anchors)
            link_path = link.split('#')[0]
            if link_path:
                full_path = (Path(doc_file["absolute_path"]).parent / link_path).resolve()
                if not full_path.exists():
                    broken_links.append(link)

        # Calculate quality score
        score = 0

        # Content depth (40 points)
        if word_count > 1000:
            score += 20
        elif word_count > 500:
            score += 15
        elif word_count > 200:
            score += 10
        elif word_count > 50:
            score += 5

        if header_count > 5:
            score += 10
        elif header_count > 2:
            score += 5

        if char_count > 100:  # Not just a stub
            score += 10

        # Examples and links (30 points)
        if has_code_examples:
            score += 15
        if code_block_count > 3:
            score += 5

        if has_links:
            score += 5
        if link_count > 5:
            score += 5

        # Structure (20 points)
        if has_lists:
            score += 10
        if header_count >= 3:
            score += 10

        # Freshness and completeness (10 points)
        if not has_placeholder:
            score += 5
        if not has_old_year:
            score += 5

        # Penalties
        if todo_count > 5:
            score -= 5
        if len(broken_links) > 0:
            score -= 10

        score = max(0, min(100, score))

        return {
            "word_count": word_count,
            "line_count": line_count,
            "char_count": char_count,
            "has_code_examples": has_code_examples,
            "code_block_count": code_block_count,
            "has_links": has_links,
            "link_count": link_count,
            "header_count": header_count,
            "has_lists": has_lists,
            "todo_count": todo_count,
            "has_placeholder": has_placeholder,
            "has_old_year": has_old_year,
            "broken_links_count": len(broken_links),
            "broken_links": broken_links[:5],  # Sample
            "quality_score": score
        }

    except Exception as e:
        return {
            "error": str(e),
            "quality_score": 0
        }

def find_duplicate_docs(docs):
    """Find duplicate documentation by content hash."""
    hash_map = defaultdict(list)

    for doc in docs:
        try:
            hasher = hashlib.sha256()
            with open(doc["absolute_path"], 'rb') as f:
                hasher.update(f.read())
            doc_hash = hasher.hexdigest()
            hash_map[doc_hash].append(doc["path"])
        except:
            pass

    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    return duplicates

def find_readme_files(docs):
    """Catalog all README files."""
    readmes = [doc for doc in docs if "readme" in doc["name"].lower()]

    # Group by directory
    by_dir = defaultdict(list)
    for readme in readmes:
        by_dir[readme["directory"]].append(readme)

    return readmes, dict(by_dir)

def categorize_docs_by_purpose(docs):
    """Categorize documentation by apparent purpose."""
    categories = {
        "readme": [],
        "architecture": [],
        "api": [],
        "tutorial": [],
        "context": [],
        "branding": [],
        "research": [],
        "other": []
    }

    for doc in docs:
        name_lower = doc["name"].lower()
        path_lower = doc["path"].lower()

        if "readme" in name_lower:
            categories["readme"].append(doc)
        elif "architecture" in name_lower or "design" in name_lower:
            categories["architecture"].append(doc)
        elif "api" in name_lower:
            categories["api"].append(doc)
        elif "tutorial" in name_lower or "guide" in name_lower or "howto" in name_lower:
            categories["tutorial"].append(doc)
        elif "context" in name_lower or "claude.me" in name_lower:
            categories["context"].append(doc)
        elif "branding" in path_lower:
            categories["branding"].append(doc)
        elif "research" in path_lower or "paper" in name_lower:
            categories["research"].append(doc)
        else:
            categories["other"].append(doc)

    return categories

def find_stale_docs(docs, months=6):
    """Find documentation not updated in specified months."""
    cutoff = datetime.now() - timedelta(days=months * 30)
    stale = []

    for doc in docs:
        modified = datetime.fromisoformat(doc["modified"])
        if modified < cutoff:
            days_old = (datetime.now() - modified).days
            stale.append({
                "path": doc["path"],
                "last_modified": doc["modified"],
                "days_old": days_old
            })

    return sorted(stale, key=lambda x: x["days_old"], reverse=True)

def generate_docs_report():
    """Generate comprehensive documentation quality report."""
    print("=" * 80)
    print("LUKHAS PRE-LAUNCH AUDIT - PHASE 6: DOCUMENTATION QUALITY")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Discover all docs
    print("[1/7] Discovering documentation files...")
    all_docs = discover_all_docs()

    # Check module documentation
    print("[2/7] Checking module documentation completeness...")
    module_docs = check_module_documentation()

    # Analyze quality
    print("[3/7] Analyzing documentation quality...")
    quality_scores = []
    for i, doc in enumerate(all_docs):
        if (i + 1) % 100 == 0:
            print(f"  Analyzed {i + 1}/{len(all_docs)} files...")

        quality = analyze_doc_quality(doc)
        doc["quality"] = quality
        quality_scores.append(quality["quality_score"])

    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0

    # Find duplicates
    print("[4/7] Finding duplicate documentation...")
    duplicate_docs = find_duplicate_docs(all_docs)

    # Catalog READMEs
    print("[5/7] Cataloging README files...")
    readmes, readmes_by_dir = find_readme_files(all_docs)

    # Categorize by purpose
    print("[6/7] Categorizing documentation...")
    doc_categories = categorize_docs_by_purpose(all_docs)

    # Find stale docs
    print("[7/7] Finding stale documentation...")
    stale_docs = find_stale_docs(all_docs, months=6)

    # Quality tiers
    excellent = [d for d in all_docs if d["quality"]["quality_score"] >= 90]
    good = [d for d in all_docs if 70 <= d["quality"]["quality_score"] < 90]
    needs_improvement = [d for d in all_docs if 50 <= d["quality"]["quality_score"] < 70]
    poor = [d for d in all_docs if d["quality"]["quality_score"] < 50]

    # Compile report
    docs_report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_docs": len(all_docs),
            "readme_count": len(readmes),
            "average_quality_score": round(avg_quality, 1),
            "duplicate_groups": len(duplicate_docs),
            "stale_docs_6mo": len(stale_docs),
            "quality_tiers": {
                "excellent_90plus": len(excellent),
                "good_70to89": len(good),
                "needs_improvement_50to69": len(needs_improvement),
                "poor_below50": len(poor)
            },
            "by_category": {
                cat: len(docs) for cat, docs in doc_categories.items()
            }
        },
        "module_completeness": module_docs,
        "quality_tiers": {
            "excellent": [{"path": d["path"], "score": d["quality"]["quality_score"]} for d in excellent[:20]],
            "good": [{"path": d["path"], "score": d["quality"]["quality_score"]} for d in good[:20]],
            "needs_improvement": [{"path": d["path"], "score": d["quality"]["quality_score"]} for d in needs_improvement[:20]],
            "poor": [{"path": d["path"], "score": d["quality"]["quality_score"]} for d in poor[:20]]
        },
        "duplicate_docs": {
            f"group_{i}": paths for i, paths in enumerate(duplicate_docs.values())
        },
        "stale_docs": stale_docs[:50],
        "all_docs": all_docs[:500]  # Limit size
    }

    # Save report
    output_file = AUDIT_REPORTS_DIR / "docs_quality_report.json"
    with open(output_file, 'w') as f:
        json.dump(docs_report, indent=2, fp=f)

    # Generate markdown summary
    md_output = AUDIT_REPORTS_DIR / "docs_quality_report.md"
    with open(md_output, 'w') as f:
        f.write("# LUKHAS Documentation Quality Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")

        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Documentation Files:** {len(all_docs)}\n")
        f.write(f"- **README Files:** {len(readmes)}\n")
        f.write(f"- **Average Quality Score:** {round(avg_quality, 1)}/100\n")
        f.write(f"- **Duplicate Groups:** {len(duplicate_docs)}\n")
        f.write(f"- **Stale Documentation (>6mo):** {len(stale_docs)}\n\n")

        f.write("## Quality Breakdown\n\n")
        f.write(f"- **Excellent (90-100):** {len(excellent)} files\n")
        f.write(f"- **Good (70-89):** {len(good)} files\n")
        f.write(f"- **Needs Improvement (50-69):** {len(needs_improvement)} files\n")
        f.write(f"- **Poor (<50):** {len(poor)} files\n\n")

        f.write("## Module Documentation Completeness\n\n")
        for module, info in sorted(module_docs.items(), key=lambda x: x[1]["completeness"], reverse=True):
            f.write(f"### {module} ({info['completeness']}% complete)\n")
            f.write(f"- **Required Docs:** {', '.join(info['required_existing']) if info['required_existing'] else 'None'}\n")
            if info['required_missing']:
                f.write(f"- **Missing:** {', '.join(info['required_missing'])}\n")
            if info['optional_existing']:
                f.write(f"- **Optional Docs:** {', '.join(info['optional_existing'])}\n")
            f.write("\n")

        f.write("## Top Quality Documents\n\n")
        for doc in excellent[:10]:
            f.write(f"- **[{doc['quality']['quality_score']}]** {doc['path']}\n")

        f.write("\n## Documents Needing Improvement\n\n")
        for doc in poor[:10]:
            f.write(f"- **[{doc['quality']['quality_score']}]** {doc['path']}\n")
            issues = []
            if doc['quality'].get('has_placeholder'):
                issues.append("contains placeholders")
            if doc['quality'].get('word_count', 0) < 100:
                issues.append("very short")
            if not doc['quality'].get('has_code_examples'):
                issues.append("no code examples")
            if doc['quality'].get('broken_links_count', 0) > 0:
                issues.append(f"{doc['quality']['broken_links_count']} broken links")
            if issues:
                f.write(f"  - Issues: {', '.join(issues)}\n")

        f.write("\n## Recommendations\n\n")
        if len(poor) > 0:
            f.write(f"1. **Update {len(poor)} low-quality documents** (score < 50)\n")
        if len(stale_docs) > 0:
            f.write(f"2. **Review {len(stale_docs)} stale documents** (>6 months old)\n")
        if len(duplicate_docs) > 0:
            f.write(f"3. **Consolidate {len(duplicate_docs)} duplicate document groups**\n")

        missing_count = sum(len(m['required_missing']) for m in module_docs.values())
        if missing_count > 0:
            f.write(f"4. **Add {missing_count} missing required documentation files**\n")

    # Print summary
    print("\n" + "=" * 80)
    print("DOCUMENTATION QUALITY SUMMARY")
    print("=" * 80)
    print(f"\nTotal Documentation: {len(all_docs)} files")
    print(f"Average Quality Score: {round(avg_quality, 1)}/100")

    print("\nQuality Distribution:")
    print(f"  Excellent (90-100): {len(excellent)}")
    print(f"  Good (70-89): {len(good)}")
    print(f"  Needs Improvement (50-69): {len(needs_improvement)}")
    print(f"  Poor (<50): {len(poor)}")

    print("\nModule Completeness:")
    for module, info in sorted(module_docs.items(), key=lambda x: x[1]["completeness"], reverse=True)[:5]:
        print(f"  {module}: {info['completeness']}%")

    print("\nIssues Found:")
    print(f"  Duplicate Groups: {len(duplicate_docs)}")
    print(f"  Stale Docs (>6mo): {len(stale_docs)}")
    print(f"  Poor Quality: {len(poor)}")

    print("\n✓ Documentation report saved to:")
    print(f"  JSON: {output_file}")
    print(f"  Markdown: {md_output}")
    print("=" * 80)

    return docs_report

if __name__ == "__main__":
    generate_docs_report()
