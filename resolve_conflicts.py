#!/usr/bin/env python3
"""
Resolve merge conflicts in branding markdown files.
Merges SEO front-matter from main with evidence_links from PR #1128.
"""

import re
from pathlib import Path

# Get list of conflicted files
conflicted_files = [
    "branding/websites/lukhas.ai/Updated_architecture_matriz_ready.md",
    "branding/websites/lukhas.ai/Updated_homepage_matriz_ready.md",
    "branding/websites/lukhas.app/architecture.md",
    "branding/websites/lukhas.cloud/architecture.md",
    "branding/websites/lukhas.com/Updated_homepage_matriz_ready.md",
    "branding/websites/lukhas.com/architecture.md",
    "branding/websites/lukhas.com/homepage.md",
    "branding/websites/lukhas.dev/Updated_architecture_matriz_ready.md",
    "branding/websites/lukhas.eu/architecture.md",
    "branding/websites/lukhas.id/architecture.md",
    "branding/websites/lukhas.store/architecture.md",
    "branding/websites/lukhas.team/architecture.md",
    "branding/websites/lukhas.us/Updated_notes_matriz_ready.md",
    "branding/websites/lukhas.us/architecture.md",
    "branding/websites/lukhas.xyz/architecture.md",
]

def resolve_conflict(filepath):
    """Resolve conflict by merging both front-matter sections."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Find conflict markers
    if '<<<<<<< HEAD' not in content:
        print(f"✓ {filepath} - no conflicts")
        return

    # Extract sections
    lines = content.split('\n')
    resolved_lines = []
    in_conflict = False
    head_section = []
    pr_section = []
    collecting_head = False
    collecting_pr = False

    for line in lines:
        if line.startswith('<<<<<<< HEAD'):
            in_conflict = True
            collecting_head = True
            continue
        elif line.startswith('======='):
            collecting_head = False
            collecting_pr = True
            continue
        elif line.startswith('>>>>>>> pr-1128'):
            in_conflict = False
            collecting_pr = False

            # Merge the sections
            # Head section has: canonical, seo, last_reviewed, keywords, ---
            # PR section has: evidence_links, ---
            # We want: canonical, seo, last_reviewed, keywords, evidence_links, ---

            # Add HEAD content (without the --- at end)
            for head_line in head_section:
                if head_line.strip() != '---':
                    resolved_lines.append(head_line)

            # Add PR content (without empty lines at start, keep ---  at end)
            pr_content_started = False
            for pr_line in pr_section:
                if pr_line.strip():
                    pr_content_started = True
                if pr_content_started:
                    resolved_lines.append(pr_line)

            head_section = []
            pr_section = []
            continue

        if collecting_head:
            head_section.append(line)
        elif collecting_pr:
            pr_section.append(line)
        elif not in_conflict:
            resolved_lines.append(line)

    # Write resolved content
    with open(filepath, 'w') as f:
        f.write('\n'.join(resolved_lines))

    print(f"✅ {filepath} - conflicts resolved")

# Resolve all conflicts
for filepath in conflicted_files:
    try:
        resolve_conflict(filepath)
    except Exception as e:
        print(f"❌ {filepath} - error: {e}")

print("\n✅ All conflicts resolved!")
