#!/usr/bin/env python3
"""
LUKHAS Owner Assignment Queue Generator (T4/0.01%)

Creates batched GitHub issues for docs with owner: unknown.
Uses git blame (≥30% threshold) + module mapping + fallback team.
"""
from __future__ import annotations


import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None

# Constants
REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
INVENTORY_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = INVENTORY_DIR / "docs_manifest.json"
OWNERS_MAP_PATH = REPO_ROOT / "scripts" / "owners_map.yaml"
OUTPUT_DIR = DOCS_ROOT / "_generated"

# SLA: 30 days from issue creation
SLA_DAYS = 30
# Batch size for GitHub issues
BATCH_SIZE = 20


def load_manifest() -> Dict:
    """Load documentation manifest."""
    with open(MANIFEST_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_owners_map() -> Dict[str, str]:
    """Load module → owner mapping from YAML."""
    if not OWNERS_MAP_PATH.exists():
        return {}

    if yaml:
        with open(OWNERS_MAP_PATH, encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    else:
        # Fallback: simple key: value parser
        mapping = {}
        with open(OWNERS_MAP_PATH, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    key, val = line.split(':', 1)
                    mapping[key.strip()] = val.strip().strip('"\'')
        return mapping


def get_git_blame_author(file_path: Path) -> Optional[Tuple[str, float]]:
    """
    Get most frequent author from git blame.
    Returns (email, percentage) if ≥30% threshold met.
    """
    try:
        result = subprocess.run(
            ['git', 'blame', '--line-porcelain', str(file_path)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=REPO_ROOT
        )

        if result.returncode != 0:
            return None

        # Count lines by author
        authors = defaultdict(int)
        total_lines = 0

        for line in result.stdout.split('\n'):
            if line.startswith('author-mail '):
                email = line.replace('author-mail ', '').strip('<>')
                authors[email] += 1
                total_lines += 1

        if total_lines == 0:
            return None

        # Get most frequent author
        top_author, line_count = max(authors.items(), key=lambda x: x[1])
        percentage = (line_count / total_lines) * 100

        # Only return if ≥30% threshold
        if percentage >= 30.0:
            return (top_author, percentage)

        return None

    except Exception:
        return None


def suggest_owner(doc: Dict, owners_map: Dict[str, str]) -> Tuple[str, str]:
    """
    Suggest owner with reason.
    Returns (suggested_owner, reason).
    """
    file_path = Path(doc['path'])

    # Strategy 1: Git blame (≥30% threshold)
    blame_result = get_git_blame_author(file_path)
    if blame_result:
        email, pct = blame_result
        # Filter out bot emails
        if email not in ['noreply@anthropic.com', 'noreply@github.com', 'dev@lukhasai.com']:
            username = email.split('@')[0]
            if username not in ['dev', 'bot', 'noreply']:
                return (f"@{username}", f"git blame ({pct:.1f}% of lines)")

    # Strategy 2: Module mapping from YAML
    module = doc.get('module', 'unknown')
    if module in owners_map:
        return (owners_map[module], f"module: {module}")

    # Strategy 3: Fallback team
    fallback = owners_map.get('unknown', '@lukhas-core')
    return (fallback, "fallback (no clear owner)")


def generate_backlog_table(docs: List[Dict], owners_map: Dict[str, str]) -> str:
    """Generate OWNERS_BACKLOG.md table."""
    lines = [
        "# Documentation Ownership Backlog",
        "",
        f"**Generated**: {datetime.now().isoformat()}",
        f"**Total docs without owners**: {len(docs)}",
        "",
        "## Summary by Suggested Owner",
        ""
    ]

    # Group by suggested owner
    by_owner = defaultdict(list)
    for doc in docs:
        suggested, reason = suggest_owner(doc, owners_map)
        by_owner[suggested].append((doc, reason))

    # Summary table
    lines.append("| Suggested Owner | Doc Count |")
    lines.append("|----------------|-----------|")
    for owner in sorted(by_owner.keys(), key=lambda x: -len(by_owner[x])):
        lines.append(f"| {owner} | {len(by_owner[owner])} |")

    lines.extend(["", "## Full Backlog", "", "| Path | Title | Module | Suggested Owner | Reason |", "|------|-------|--------|----------------|--------|"])

    # Detail table
    for doc in sorted(docs, key=lambda d: d['path']):
        suggested, reason = suggest_owner(doc, owners_map)
        path = doc['path'].replace('docs/', '')
        title = doc['title'][:50]  # Truncate
        module = doc.get('module', 'unknown')
        lines.append(f"| [{path}]({path}) | {title} | {module} | {suggested} | {reason} |")

    lines.extend(["", "---", "", f"*Auto-generated by `scripts/owners_queue_v2.py` on {datetime.now().strftime('%Y-%m-%d')}*"])

    return '\n'.join(lines)


def generate_github_issue(batch_num: int, docs_batch: List[Dict], owners_map: Dict[str, str]) -> str:
    """Generate GitHub issue markdown for a batch of docs."""
    sla_date = (datetime.now() + timedelta(days=SLA_DAYS)).strftime('%Y-%m-%d')

    issue = [
        f"# Documentation Owner Assignment - Batch {batch_num}",
        "",
        f"**Docs in batch**: {len(docs_batch)}",
        f"**SLA**: {sla_date} (30 days)",
        "",
        "## Assignment Instructions",
        "",
        "1. Review each doc's content and context",
        "2. Verify suggested owner (from git blame or module mapping)",
        "3. Update front-matter: `owner: @username` or `owner: team-name`",
        "4. Commit: `docs(owner): assign ownership for <module>/<file>`",
        "5. Check the box when complete",
        "",
        "## Docs to Assign",
        ""
    ]

    for doc in docs_batch:
        suggested, reason = suggest_owner(doc, owners_map)
        path = doc['path'].replace('docs/', '')
        title = doc['title']
        issue.append(f"- [ ] [{title}]({path}) → {suggested} *(reason: {reason})*")

    issue.extend([
        "",
        "## Bulk Assignment (Optional)",
        "",
        "If all docs in this batch should go to the same owner:",
        "",
        "```bash",
        "# Example: Assign all to @username",
        f"python3 scripts/bulk_assign_owner.py --batch {batch_num} --owner @username",
        "```",
        "",
        "---",
        "",
        f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d')}*",
        f"*Labels: `docs:ownership`, `priority:medium`, `sla:{sla_date}`*"
    ])

    return '\n'.join(issue)


def main():
    """Main workflow."""
    print("=" * 80)
    print("LUKHAS Owner Assignment Queue (T4/0.01%)")
    print("=" * 80)
    print()

    # Load data
    print(f"📂 Loading manifest: {MANIFEST_PATH}")
    manifest = load_manifest()
    docs = manifest['documents']

    print(f"📂 Loading owners map: {OWNERS_MAP_PATH}")
    owners_map = load_owners_map()
    print(f"   Loaded {len(owners_map)} module mappings")
    print()

    # Filter docs with unknown owners
    unknown_owners = [
        d for d in docs
        if d.get('owner') in ['unknown', '', None] and not d.get('redirect')
    ]

    print(f"📊 Found {len(unknown_owners)} docs with owner: unknown")
    print()

    if not unknown_owners:
        print("✅ All docs have assigned owners!")
        return 0

    # Generate backlog table
    print("📝 Generating OWNERS_BACKLOG.md...")
    backlog_md = generate_backlog_table(unknown_owners, owners_map)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    backlog_path = OUTPUT_DIR / "OWNERS_BACKLOG.md"

    with open(backlog_path, 'w', encoding='utf-8') as f:
        f.write(backlog_md)

    print(f"✅ Written: {backlog_path}")
    print()

    # Generate GitHub issues if --open-issues flag
    if '--open-issues' in sys.argv:
        print(f"📋 Generating GitHub issues (batch size: {BATCH_SIZE})...")

        # Split into batches
        batches = [unknown_owners[i:i + BATCH_SIZE] for i in range(0, len(unknown_owners), BATCH_SIZE)]

        issues_dir = OUTPUT_DIR / "owner_issues"
        issues_dir.mkdir(parents=True, exist_ok=True)

        for idx, batch in enumerate(batches, 1):
            issue_md = generate_github_issue(idx, batch, owners_map)
            issue_path = issues_dir / f"batch_{idx:02d}.md"

            with open(issue_path, 'w', encoding='utf-8') as f:
                f.write(issue_md)

            print(f"   Created: {issue_path}")

        print()
        print(f"✅ Generated {len(batches)} GitHub issue templates")
        print()
        print("To create issues with gh CLI:")
        print()
        for idx in range(1, len(batches) + 1):
            sla_date = (datetime.now() + timedelta(days=SLA_DAYS)).strftime('%Y-%m-%d')
            print(f"gh issue create --title 'Docs Ownership: Batch {idx}' \\")
            print(f"  --body-file '{issues_dir}/batch_{idx:02d}.md' \\")
            print(f"  --label 'docs:ownership,priority:medium,sla:{sla_date}'")
        print()

    # Delta report
    print("=" * 80)
    print("DELTA REPORT")
    print("=" * 80)
    print(f"Docs without owners: {len(unknown_owners)}")
    print(f"Backlog table: {backlog_path}")
    print(f"Batches created: {len(unknown_owners) // BATCH_SIZE + (1 if len(unknown_owners) % BATCH_SIZE else 0)}")
    print()

    # Ownership coverage
    total_docs = len([d for d in docs if not d.get('redirect')])
    coverage_pct = ((total_docs - len(unknown_owners)) / total_docs) * 100
    print(f"Owner coverage: {coverage_pct:.1f}% ({total_docs - len(unknown_owners)}/{total_docs})")
    print()
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())