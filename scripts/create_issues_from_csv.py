#!/usr/bin/env python3
"""
Generate a shell script with GitHub CLI commands from docs/audits/todos.csv.
(We do NOT call gh directly; we produce a reviewable script.)

Usage:
  python3 scripts/create_issues_from_csv.py \
    --csv docs/audits/todos.csv \
    --out docs/audits/todos_gh.sh \
    --repo LukhasAI/Lukhas \
    --milestone "MATRIZ-R2" \
    --label-extra matriz

Then:
  gh auth status
  bash docs/audits/todos_gh.sh
"""
from __future__ import annotations
import argparse, csv, shlex, sys
from pathlib import Path

def mk_labels(owner_hint:str, priority:str, extra:str|None):
    labels = ["debt"]
    if extra:
        labels.append(extra)
    if owner_hint:
        labels.append(f"owner/{owner_hint}")
    if priority:
        labels.append(f"priority/{priority.upper()}")
    return labels

def summarize(text:str, limit:int=80):
    t = (text or "").strip().replace("\n"," ")
    return t[:limit] + ("…" if len(t) > limit else "")

def esc_body(body:str)->str:
    # Use ANSI-C quoting via $'..' to keep newlines; escape single quotes
    return "$'" + body.replace("\\","\\\\").replace("'", r"'\''").replace("\n", r"\n") + "'"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="docs/audits/todos.csv")
    ap.add_argument("--out", default="docs/audits/todos_gh.sh")
    ap.add_argument("--repo", default="")
    ap.add_argument("--milestone", default="")
    ap.add_argument("--assignee", default="")  # e.g., @me or a username
    ap.add_argument("--label-extra", default="")  # e.g., matriz
    args = ap.parse_args()

    src = Path(args.csv)
    if not src.exists():
        print(f"[ERR] missing {src}", file=sys.stderr)
        return 2

    lines = ["#!/usr/bin/env bash", "set -euo pipefail", 'echo "Creating issues from CSV…"']
    created = 0

    with src.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            path = row.get("path","")
            line = row.get("line","")
            kind = row.get("kind","general")
            owner_hint = row.get("owner_hint","")
            priority = row.get("priority","P3")
            tag = row.get("tag","").strip()
            text = row.get("text","").strip()

            title = f"TODO: {summarize(text or f'{kind} in {path}:{line}')}"
            body = f"""# Auto-generated from {src}
**Path:** `{path}`:{line}
**Kind:** {kind}
**Owner hint:** {owner_hint or '-'}
**Priority:** {priority}
**Tag:** {tag or '-'}

**Context:**
{text or '(no additional context)'}
"""
            cmd = ["gh","issue","create","--title",title,"--body", body]
            if args.repo:
                cmd += ["--repo", args.repo]
            for lab in mk_labels(owner_hint, priority, args.label_extra or None):
                cmd += ["--label", lab]
            if args.milestone:
                cmd += ["--milestone", args.milestone]
            if args.assignee:
                cmd += ["--assignee", args.assignee]

            # Emit a line to create the issue
            # Note: we use ANSI-C quoted body for safe newlines
            pieces = []
            for i, c in enumerate(cmd):
                if i == 4 and c == body:  # --body value
                    pieces.append("--body")
                    pieces.append(esc_body(body))
                else:
                    pieces.append(shlex.quote(c))
            lines.append(" ".join(pieces))
            created += 1

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] wrote {outp} with {created} gh issue commands")
    return 0

if __name__ == "__main__":
    sys.exit(main())
