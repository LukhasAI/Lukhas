#!/usr/bin/env python3
"""
Promotion guard: validate MATRIZ-007 Week 6 completion and issue state.

Behavior:
- Fetch issue number from ISSUE_NUMBER env var (default 490)
- Fail if issue state != 'closed' OR if Week 6 checklist items contain any unchecked items.
- Produce clear error messages describing blocking items.

Exit codes:
0 = pass
1 = fail (blocked)
"""

import os
import re
import sys
from typing import List, Tuple

import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = os.environ.get("GITHUB_REPOSITORY")
ISSUE_NUMBER = os.environ.get("ISSUE_NUMBER", "490")
WEEK_HEADING = os.environ.get("WEEK_SECTION_HEADING", "Week 6")  # case-insensitive

if not GITHUB_TOKEN:
    print("ERROR: GITHUB_TOKEN not set. The workflow must run with a GITHUB_TOKEN available.")
    sys.exit(1)

if not REPO:
    print("ERROR: GITHUB_REPOSITORY not set.")
    sys.exit(1)

API_BASE = f"https://api.github.com/repos/{REPO}"

def fetch_issue(n: str) -> dict:
    url = f"{API_BASE}/issues/{n}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f"ERROR: failed to fetch issue #{n} (HTTP {resp.status_code}). Response: {resp.text}")
        sys.exit(1)
    return resp.json()

def extract_week6_checkboxes(body: str, heading: str = "Week 6") -> Tuple[List[Tuple[int,str]], List[Tuple[int,str]]]:
    """
    Return (checked_items, unchecked_items)
    Each item is (line_number, line_text)
    Strategy:
      - Find the first line that contains heading (case-insensitive)
      - Collect subsequent lines until a blank line followed by non-checkbox or end of body
      - Parse '- [ ]' and '- [x]' items
    """
    lines = body.splitlines()
    # Normalize heading search
    heading_idx = None
    for i, ln in enumerate(lines):
        if heading.lower() in ln.lower():
            heading_idx = i
            break
    # If heading not found, search for "Week 6" or "Week 6:" anywhere; if still not found, parse all checkboxes
    checked = []
    unchecked = []
    # If heading found, gather until a blank line followed by a non-list line or a new heading starting with '#' or 'Week'
    if heading_idx is not None:
        i = heading_idx + 1
    else:
        i = 0
    # Collect up to 200 lines or until we hit a new heading
    while i < len(lines):
        ln = lines[i].strip()
        # stop if we hit another top heading or "Week <n>" heading when we started under Week 6
        if heading_idx is not None:
            if re.match(r'^\s*#+\s+', lines[i]) or re.match(r'^\s*Week\s+\d+', lines[i], re.I):
                # Stop if it's a new heading and it's not the first lines immediately after our heading
                if i > heading_idx + 1 and ln != '':
                    break
        # Match checkbox patterns
        m_checked = re.match(r'^\s*[-*]\s*\[\s*[xX]\s*\]\s*(.+)', ln)
        m_unchecked = re.match(r'^\s*[-*]\s*\[\s*\]\s*(.+)', ln)
        if m_checked:
            checked.append((i+1, m_checked.group(1).strip()))
        elif m_unchecked:
            unchecked.append((i+1, m_unchecked.group(1).strip()))
        # Stop heuristics: if heading was not found and we've scanned a chunk with checkboxes, stop after pass
        if heading_idx is None and (checked or unchecked) and ln == '':
            # ended checkbox region
            break
        i += 1
    return checked, unchecked

def print_blockers(issue):
    state = issue.get("state")
    title = issue.get("title")
    number = issue.get("number")
    body = issue.get("body") or ""
    print("="*80)
    print(f"MATRIZ Issue #{number}: {title}")
    print(f"State: {state.upper()}")
    print("="*80)
    print()
    # Find week6 checkboxes
    checked, unchecked = extract_week6_checkboxes(body, WEEK_HEADING)
    # Compose detailed messages
    blockers = []
    if state.lower() != "closed":
        blockers.append("Issue is OPEN. Promotion blocked until MATRIZ-007 is CLOSED (completed).")
    if unchecked:
        blockers.append(f"Week 6 checklist has {len(unchecked)} unchecked item(s):")
        for ln, txt in unchecked:
            blockers.append(f" - Line {ln}: {txt}")
    # If no explicit Week 6 found and issue open, warn
    if not checked and not unchecked:
        blockers.append("No Week 6 checklist section found. Ensure a 'Week 6' checklist exists in the issue body and all items are checked.")
    if not blockers:
        print("No blockers found: Issue appears CLOSED and Week 6 checklist (if present) has all items checked.")
        return []
    # Print blockers with remediation hints
    print("BLOCKERS preventing promotion:")
    for b in blockers:
        print(" * " + b)
    print()
    print("REMEDIATION:")
    print(" - Close the issue #{} after confirming Week 6 completion. Use the issue checklist to mark items done.".format(ISSUE_NUMBER))
    print(" - Ensure the Week 6 checklist in the issue body contains items such as: 'Dilithium2 sign/verify passed', 'Key rotation implemented', 'Red-team sign-off', 'Performance validated', etc.")
    print(" - After closing and verifying, re-run CI to allow promotion.")
    print("="*80)
    return blockers

def main():
    issue = fetch_issue(ISSUE_NUMBER)
    blockers = print_blockers(issue)
    if blockers:
        # Fail the action with explicit exit code 1
        print("\nPromotion guard: BLOCKED")
        sys.exit(1)
    else:
        print("\nPromotion guard: PASS — MATRIZ-007 appears completed for Week 6.")
        sys.exit(0)

if __name__ == "__main__":
    main()
