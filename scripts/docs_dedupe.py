#!/usr/bin/env python3
"""
LUKHAS Documentation Deduplication Tool

Detects exact and near-duplicate documents and generates a redirect/move plan.
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Constants
DOCS_ROOT = Path(__file__).parent.parent / "docs"
INVENTORY_DIR = DOCS_ROOT / "_inventory"
MANIFEST_PATH = INVENTORY_DIR / "docs_manifest.json"
OUTPUT_DIR = DOCS_ROOT / "_generated"
REDIRECTS_PATH = OUTPUT_DIR / "REDIRECTS.md"
DEDUPE_PLAN_PATH = INVENTORY_DIR / "dedupe_plan.json"

# Normalized taxonomy paths (preferred locations)
CANONICAL_PATHS = {
    'api': 'docs/api/',
    'architecture': 'docs/architecture/',
    'guide': 'docs/guides/',
    'report': 'docs/reports/',
    'adr': 'docs/adr/',
    'index': 'docs/reference/',
    'misc': 'docs/',
}

# Index files that reference documents
INDEX_FILES = [
    'docs/INDEX.md',
    'docs/reference/DOCUMENTATION_INDEX.md',
]


def load_manifest() -> Dict:
    """Load the documentation manifest."""
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_text_similarity(text1: str, text2: str) -> float:
    """
    Compute simple cosine similarity between two texts using word frequencies.
    Returns similarity score between 0 and 1.
    """
    # Tokenize and create word frequency vectors
    words1 = re.findall(r'\w+', text1.lower())
    words2 = re.findall(r'\w+', text2.lower())

    if not words1 or not words2:
        return 0.0

    # Build frequency maps
    freq1 = defaultdict(int)
    freq2 = defaultdict(int)

    for word in words1:
        freq1[word] += 1
    for word in words2:
        freq2[word] += 1

    # Compute cosine similarity
    all_words = set(freq1.keys()) | set(freq2.keys())

    dot_product = sum(freq1[w] * freq2[w] for w in all_words)
    magnitude1 = sum(v * v for v in freq1.values()) ** 0.5
    magnitude2 = sum(v * v for v in freq2.values()) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def read_doc_content(doc_path: str) -> str:
    """Read document content for similarity comparison."""
    try:
        full_path = Path(doc_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


def is_referenced_by_index(doc_path: str) -> bool:
    """Check if document is referenced by any index file."""
    for index_file in INDEX_FILES:
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for relative path reference
                if doc_path.replace('docs/', '') in content:
                    return True
        except Exception:
            continue
    return False


def canonical_preference_score(doc: Dict) -> Tuple[int, int, int, str]:
    """
    Score document for canonical preference.
    Returns tuple: (taxonomy_match, index_ref, fm_richness, -date)
    Higher is better.
    """
    doc_path = doc['path']
    doc_type = doc['type']

    # 1. Taxonomy path match
    taxonomy_score = 0
    if doc_type in CANONICAL_PATHS:
        preferred_path = CANONICAL_PATHS[doc_type]
        if doc_path.startswith(preferred_path):
            taxonomy_score = 10

    # 2. Index reference
    index_score = 10 if is_referenced_by_index(doc_path) else 0

    # 3. Front-matter richness
    fm_score = 0
    if doc['has_front_matter']:
        fm_score += 5
        if doc['owner'] != 'unknown':
            fm_score += 2
        if doc.get('moved_to'):
            fm_score -= 10  # Redirect stubs are less preferred

    # 4. Date (newer is better, use negative for reverse sort)
    date_str = doc.get('updated_at', '2000-01-01')

    return (taxonomy_score, index_score, fm_score, date_str)


def find_near_duplicates(docs: List[Dict], threshold: float = 0.92) -> List[List[Dict]]:
    """
    Find near-duplicate documents using MinHash-like approach.
    Returns list of duplicate groups.

    For performance with 1200+ docs, we use title/filename similarity only.
    """
    print(f"🔍 Finding near-duplicates by title/path similarity...")

    near_dupes = []
    checked = set()

    # Group by similar titles first (fast pre-filter)
    title_groups = defaultdict(list)
    for doc in docs:
        # Normalize title for grouping
        normalized = re.sub(r'[^a-z0-9]', '', doc['title'].lower())
        # Use first 20 chars as group key
        key = normalized[:20] if len(normalized) > 20 else normalized
        title_groups[key].append(doc)

    # Only check similarity within groups
    for key, group_docs in title_groups.items():
        if len(group_docs) < 2:
            continue

        for i, doc1 in enumerate(group_docs):
            if doc1['sha256'] in checked:
                continue

            similar_group = [doc1]

            for doc2 in group_docs[i+1:]:
                if doc2['sha256'] in checked:
                    continue

                # Compare titles with fuzzy matching
                title_sim = compute_text_similarity(doc1['title'], doc2['title'])
                if title_sim >= 0.7:  # Lower threshold for titles
                    similar_group.append(doc2)
                    checked.add(doc2['sha256'])

            if len(similar_group) > 1:
                near_dupes.append(similar_group)
                checked.add(doc1['sha256'])

    return near_dupes


def create_dedupe_plan(manifest: Dict) -> Dict:
    """
    Create deduplication plan with canonical selections.
    """
    docs = manifest['documents']
    plan = {
        "exact_duplicates": [],
        "near_duplicates": [],
        "redirects": [],
        "moves_to_archive": [],
    }

    # 1. Handle exact duplicates
    exact_dupes = manifest['metrics']['exact_duplicate_groups']
    print(f"📋 Processing {len(exact_dupes)} exact duplicate groups...")

    for hash_val, paths in exact_dupes.items():
        # Get full doc info for each path
        dupe_docs = [d for d in docs if d['path'] in paths]

        # Sort by preference
        dupe_docs.sort(key=canonical_preference_score, reverse=True)
        canonical = dupe_docs[0]
        duplicates = dupe_docs[1:]

        plan['exact_duplicates'].append({
            "canonical": canonical['path'],
            "duplicates": [d['path'] for d in duplicates],
            "hash": hash_val,
        })

        # Create redirect actions
        for dup in duplicates:
            plan['redirects'].append({
                "from": dup['path'],
                "to": canonical['path'],
                "reason": "exact_duplicate",
            })

    # 2. Find and handle near-duplicates
    # Only check docs not already in exact duplicate groups
    remaining_docs = [d for d in docs if d['sha256'] not in exact_dupes]

    near_dupes = find_near_duplicates(remaining_docs, threshold=0.92)
    print(f"📋 Found {len(near_dupes)} near-duplicate groups...")

    for group in near_dupes:
        # Sort by preference
        group.sort(key=canonical_preference_score, reverse=True)
        canonical = group[0]
        duplicates = group[1:]

        plan['near_duplicates'].append({
            "canonical": canonical['path'],
            "duplicates": [d['path'] for d in duplicates],
        })

        # For near-duplicates, suggest archival rather than redirect
        for dup in duplicates:
            plan['moves_to_archive'].append({
                "from": dup['path'],
                "reason": "near_duplicate",
                "canonical_alternative": canonical['path'],
            })

    return plan


def write_redirects_md(plan: Dict):
    """Write REDIRECTS.md table."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    content = [
        "# Documentation Redirects",
        "",
        "This file tracks all documentation redirects (moved or consolidated files).",
        "",
        "| From | To | Reason |",
        "|------|-----|--------|",
    ]

    for redirect in plan['redirects']:
        from_path = redirect['from'].replace('docs/', '')
        to_path = redirect['to'].replace('docs/', '')
        reason = redirect['reason']
        content.append(f"| [{from_path}]({from_path}) | [{to_path}]({to_path}) | {reason} |")

    content.append("")
    content.append(f"**Total Redirects:** {len(plan['redirects'])}")
    content.append("")

    with open(REDIRECTS_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

    print(f"✅ Redirects table written to {REDIRECTS_PATH}")


def main():
    """Main deduplication workflow."""
    print("=" * 80)
    print("LUKHAS Documentation Deduplication Tool")
    print("=" * 80)
    print()

    # Load manifest
    print(f"📂 Loading manifest from {MANIFEST_PATH}...")
    manifest = load_manifest()

    # Create deduplication plan
    plan = create_dedupe_plan(manifest)

    # Write plan
    with open(DEDUPE_PLAN_PATH, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print(f"✅ Dedupe plan written to {DEDUPE_PLAN_PATH}")

    # Write redirects markdown
    write_redirects_md(plan)

    # Print summary
    print()
    print("=" * 80)
    print("DEDUPLICATION SUMMARY")
    print("=" * 80)
    print(f"Exact duplicate groups: {len(plan['exact_duplicates'])}")
    print(f"Near-duplicate groups: {len(plan['near_duplicates'])}")
    print(f"Redirects to create: {len(plan['redirects'])}")
    print(f"Files to archive: {len(plan['moves_to_archive'])}")
    print()

    if plan['exact_duplicates']:
        print("Sample Exact Duplicates:")
        for dupe in plan['exact_duplicates'][:3]:
            print(f"  Canonical: {dupe['canonical']}")
            for dup_path in dupe['duplicates']:
                print(f"    → {dup_path}")
            print()

    if plan['near_duplicates']:
        print("Sample Near-Duplicates:")
        for dupe in plan['near_duplicates'][:3]:
            print(f"  Canonical: {dupe['canonical']}")
            for dup_path in dupe['duplicates']:
                print(f"    ≈ {dup_path}")
            print()

    print("=" * 80)
    print(f"✅ Phase 2 Complete - Dedupe plan: {DEDUPE_PLAN_PATH}")
    print("=" * 80)
    print()
    print("To apply this plan, use: python3 scripts/docs_dedupe.py --apply")


if __name__ == "__main__":
    import sys

    if '--apply' in sys.argv:
        print("❌ Apply mode not yet implemented - manual review required first")
        sys.exit(1)
    else:
        main()
