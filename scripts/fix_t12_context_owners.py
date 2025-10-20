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


def find_front_matter_bounds(text: str) -> Tuple[int, int]:
    lines = text.splitlines()
    if not lines or not lines[0].strip() == '---':
        raise ValueError('no fm start')
    for i in range(1, min(len(lines), 200)):
        if lines[i].strip() == '---':
            return (0, i)
    raise ValueError('no fm end')


def patch_owner_in_fm(text: str, owner: str) -> str:
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
    m = json.loads(mf.read_text(encoding='utf-8'))
    tier = (m.get('testing', {}) or {}).get('quality_tier') or ''
    owner = (m.get('metadata', {}) or {}).get('owner') or ''
    return tier, owner


def is_archived(path: pathlib.Path) -> bool:
    return any(part == '.archive' for part in path.parts)


def main() -> None:
    changed = 0
    skipped = 0
    for mf in ROOT.rglob('module.manifest.json'):
        if is_archived(mf):
            continue
        try:
            tier, m_owner = get_tier_and_owner(mf)
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

