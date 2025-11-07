#!/usr/bin/env python3
"""
Set owner in lukhas_context.md front-matter for T1/T2 modules.

Policy: T1/T2 must have an explicit owner. If the sibling manifest is T1_critical
or T2_important and lukhas_context.md either lacks 'owner' or has 'unassigned',
set owner: triage@lukhas in the front-matter block. Archives are ignored.
"""
from __future__ import annotations

import json
import pathlib
from typing import Tuple

ROOT = pathlib.Path(__file__).resolve().parents[1]


def find_front_matter_bounds(text: str) -> tuple[int, int]:
    """Locate the start and end line indices of YAML front matter.

    Searches for opening and closing '---' delimiters within the first 200 lines
    of text. Returns the line indices (0-based) that bound the front matter block,
    excluding the delimiters themselves.

    Args:
        text: Full text content to search for front matter boundaries.

    Returns:
        tuple[int, int]: A tuple (start_line, end_line) where start_line is 0
            (the opening '---' line) and end_line is the index of the closing
            '---' line. The actual YAML content is between start_line+1 and end_line.

    Raises:
        ValueError: If no opening '---' found at line 0 (message: 'no fm start'),
            or if no closing '---' found within first 200 lines (message: 'no fm end').

    Example:
        >>> find_front_matter_bounds("---\\nkey: value\\n---\\nBody")
        (0, 2)
        >>> find_front_matter_bounds("No front matter")
        Traceback (most recent call last):
        ValueError: no fm start
    """
    lines = text.splitlines()
    if not lines or not lines[0].strip() == '---':
        raise ValueError('no fm start')
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() == '---':
            return (0, i)
    raise ValueError('no fm end')


def patch_owner_in_fm(text: str, owner: str) -> str:
    """Update or insert owner field in YAML front matter.

    Modifies the front matter block to set the owner field to the specified value.
    If an existing 'owner:' line is found, it is replaced. If not found, the
    owner field is appended to the front matter. Preserves all other front matter
    fields and body content.

    Args:
        text: Full text content with YAML front matter to modify.
        owner: Owner identifier to set (e.g., 'triage@lukhas').

    Returns:
        str: Modified text with updated owner field in front matter. Preserves
            trailing newline if present in original text.

    Raises:
        ValueError: If front matter bounds cannot be determined (via
            find_front_matter_bounds).

    Example:
        >>> patch_owner_in_fm("---\\nmodule: test\\nowner: old\\n---\\nBody", "triage@lukhas")
        '---\\nmodule: test\\nowner: triage@lukhas\\n---\\nBody'
        >>> patch_owner_in_fm("---\\nmodule: test\\n---\\nBody", "triage@lukhas")
        '---\\nmodule: test\\nowner: triage@lukhas\\n---\\nBody'
    """
    lines = text.splitlines()
    start, end = find_front_matter_bounds(text)
    fm = lines[start + 1 : end]
    out_fm = []
    saw_owner = False
    for line in fm:
        if line.strip().startswith('owner:'):
            out_fm.append(f'owner: {owner}')
            saw_owner = True
        else:
            out_fm.append(line)
    if not saw_owner:
        out_fm.append(f'owner: {owner}')
    new_lines = []
    new_lines.extend(lines[: start + 1])
    new_lines.extend(out_fm)
    new_lines.append('---')
    new_lines.extend(lines[end + 1 :])
    return '\n'.join(new_lines) + ('\n' if text.endswith('\n') else '')


def get_tier_and_owner(mf: pathlib.Path) -> tuple[str, str]:
    """Extract quality tier and owner from module manifest file.

    Reads and parses a module.manifest.json file to extract the quality_tier
    from the testing section and the owner from the metadata section. Used to
    identify T1/T2 modules requiring owner enforcement.

    Args:
        mf: Path to the module.manifest.json file to read.

    Returns:
        tuple[str, str]: A tuple (tier, owner) where tier is the quality_tier
            value (e.g., 'T1_critical') and owner is the metadata owner value
            (e.g., 'security@lukhas'). Both are empty strings if not found.

    Raises:
        json.JSONDecodeError: If manifest file contains invalid JSON.
        OSError: If file cannot be read.

    Example:
        >>> get_tier_and_owner(Path("manifests/core/identity/module.manifest.json"))
        ('T1_critical', 'security@lukhas')
        >>> get_tier_and_owner(Path("manifests/candidate/experimental/module.manifest.json"))
        ('T4_experimental', 'unassigned')
    """
    m = json.loads(mf.read_text(encoding='utf-8'))
    tier = (m.get('testing', {}) or {}).get('quality_tier') or ''
    owner = (m.get('metadata', {}) or {}).get('owner') or ''
    return tier, owner


def is_archived(path: pathlib.Path) -> bool:
    """Check if a path contains an archived directory component.

    Determines whether a file path includes '.archive' as any directory component,
    indicating the file belongs to archived/deprecated modules that should be
    excluded from active processing.

    Args:
        path: File path to check for archive markers.

    Returns:
        bool: True if '.archive' appears in any path component, False otherwise.

    Example:
        >>> is_archived(Path("manifests/.archive/old_module/module.manifest.json"))
        True
        >>> is_archived(Path("manifests/core/identity/module.manifest.json"))
        False
    """
    return any(part == '.archive' for part in path.parts)


def main() -> None:
    """Set triage owner in T1/T2 context file front matter.

    Scans all module.manifest.json files to identify T1_critical and T2_important
    modules, then checks their sibling lukhas_context.md files for missing or
    unassigned owner fields in the YAML front matter. Updates owner to
    'triage@lukhas' for any T1/T2 context files lacking explicit ownership.

    This ensures consistency between manifest and context file ownership, enforcing
    the policy that high-tier modules must have accountable owners.

    Returns:
        None: Prints progress to stdout and modifies context files in place.

    Raises:
        No explicit raises, but silently continues on errors (missing files,
        parse failures, missing front matter) to process all discoverable modules.

    Example:
        $ python scripts/fix_t12_context_owners.py
        [OK] owner set: manifests/core/identity/lukhas_context.md
        [OK] owner set: manifests/lukhas/governance/lukhas_context.md
        Changed: 2 | Skipped(no-fm): 3
    """
    changed = 0
    skipped = 0
    for mf in ROOT.rglob('module.manifest.json'):
        if is_archived(mf):
            continue
        try:
            tier, _m_owner = get_tier_and_owner(mf)
        except Exception:
            continue
        if tier not in ('T1_critical', 'T2_important'):
            continue

        ctx = mf.parent / 'lukhas_context.md'
        if not ctx.exists():
            continue
        try:
            text = ctx.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        try:
            start, end = find_front_matter_bounds(text)
        except ValueError:
            skipped += 1
            continue
        fm_block = text.splitlines()[start + 1 : end]
        current = None
        for line in fm_block:
            if line.strip().startswith('owner:'):
                current = line.split(':', 1)[1].strip()
                break
        if current and current.lower() not in ('', 'unassigned', 'none', '-'):
            continue
        new_text = patch_owner_in_fm(text, 'triage@lukhas')
        ctx.write_text(new_text, encoding='utf-8')
        print(f'[OK] owner set: {ctx}')
        changed += 1
    print(f'Changed: {changed} | Skipped(no-fm): {skipped}')


if __name__ == '__main__':
    main()

