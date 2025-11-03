#!/usr/bin/env python3
"""
Generate a Markdown appendix summarizing differences between two Git tags.

Usage:
  tools/audit/mk_delta_appendix.py --old <OLD_TAG> --new <NEW_TAG> \
    --out reports/audit/appendix_delta.md
"""
from __future__ import annotations

import argparse
import hashlib
import subprocess
from collections import Counter
from pathlib import Path

KEY_JSONS = [
    "LUKHAS_ARCHITECTURE_MASTER.json",
    "DEPENDENCY_MATRIX.json",
    "SECURITY_ARCHITECTURE.json",
    "CONSCIOUSNESS_METRICS.json",
    "PERFORMANCE_BASELINES.json",
    "BUSINESS_METRICS.json",
    "EVOLUTION_ROADMAP.json",
    "VISUALIZATION_CONFIG.json",
    "AUDIT/LANES.yaml",
]
CODE_DIRS = ("lukhas/", "MATRIZ/", "ops/")
TEST_DIRS = ("tests/",)
CI_DIR = ".github/workflows/"


def sh(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def file_hash_at(ref, path):
    try:
        blob = subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True)
        return "sha256:" + hashlib.sha256(blob.encode("utf-8", "ignore")).hexdigest()
    except subprocess.CalledProcessError:
        return None


def exists_at(ref, path):
    try:
        subprocess.check_call(
            ["git", "cat-file", "-e", f"{ref}:{path}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


def classify(path):
    if any(path.startswith(d) for d in CODE_DIRS):
        return "code"
    if any(path.startswith(d) for d in TEST_DIRS):
        return "tests"
    if path.startswith(CI_DIR):
        return "ci"
    if path.startswith("AUDIT/") or path.startswith("reports/"):
        return "audit"
    if path.startswith("docs/") or path.endswith((".md", ".MD")):
        return "docs"
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True, help="old tag (baseline)")
    ap.add_argument("--new", required=True, help="new tag (current)")
    ap.add_argument("--out", required=True, help="output markdown path")
    args = ap.parse_args()

    old, new = args.old, args.new
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Diff lists
    # name-status: M = modified, A = added, D = deleted, R = renamed
    name_status = sh(f"git diff --name-status {old}..{new}")
    lines = [line for line in name_status.splitlines() if line.strip()]
    changes = []
    for ln in lines:
        parts = ln.split()
        status, path = parts[0], parts[-1]
        changes.append((status, path))

    # Stats overview
    stat = sh(f"git diff --stat {old}..{new} | tail -1 2>/dev/null || true")
    commits = sh(f"git log --oneline --no-merges {old}..{new} | wc -l")
    commit_list = sh(f"git log --oneline --no-merges {old}..{new}")

    # Buckets
    bucket_counts = Counter(classify(p) for _, p in changes)
    status_counts = Counter(s for s, _ in changes)

    # Key JSON deltas
    key_rows = []
    for p in KEY_JSONS:
        before = file_hash_at(old, p) if exists_at(old, p) else None
        after = file_hash_at(new, p) if exists_at(new, p) else None
        if before != after:
            key_rows.append((p, before or "—", after or "—"))

    # SBOM presence
    sbom_path = "reports/sbom/cyclonedx.json"
    sbom_before = exists_at(old, sbom_path)
    sbom_after = exists_at(new, sbom_path)

    # Test additions by marker-ish filename hint
    test_added = [p for s, p in changes if s.startswith("A") and p.startswith("tests/")]
    test_matriz = [p for p in test_added if ("matriz" in p.lower() or "golden" in p.lower() or "smoke" in p.lower())]

    # Cross-lane guard changes (lane guard script/workflow touched?)
    guard_touched = [
        p for s, p in changes if p.startswith("tools/ci/lane_guard.sh") or p.startswith(".github/workflows/")
    ]

    # CI workflow files touched
    ci_files = [p for s, p in changes if p.startswith(CI_DIR)]

    # Build appendix MD
    md = []
    md.append(f"# Appendix — Delta between `{old}` and `{new}`\n")
    md.append("## Summary\n")
    md.append(f"- Commits: **{int(commits)}**\n- File changes: **{len(changes)}**\n- Diff stat: `{stat or 'n/a'}`\n")
    md.append("### Change buckets\n")
    md.append("| Bucket | Files |\n|---|---:|\n")
    for k in ("code", "tests", "ci", "audit", "docs", "other"):
        md.append(f"| {k} | {bucket_counts.get(k,0)} |")
    md.append("")
    md.append("### Change types\n")
    md.append("| Type | Count |\n|---|---:|\n")
    for t in ("A", "M", "D", "R"):
        md.append(f"| {t} | {status_counts.get(t,0)} |")
    md.append("")

    if key_rows:
        md.append("## Key Governance Artifacts Changed\n")
        md.append("| File | Hash @ old | Hash @ new |\n|---|---|---|\n")
        for p, b, a in key_rows:
            md.append(f"| {p} | `{b}` | `{a}` |")
        md.append("")

    md.append("## SBOM\n")
    md.append(f"- Present @ old: **{sbom_before}**  \n- Present @ new: **{sbom_after}**\n")
    if sbom_after and not sbom_before:
        md.append("- **Note:** SBOM added in new tag — add link in SECURITY_ARCHITECTURE.json if missing.\n")

    if test_matriz:
        md.append("## MATRIZ/GOLDEN Test Additions\n")
        for p in sorted(test_matriz):
            md.append(f"- `{p}`")
        md.append("")

    if guard_touched or ci_files:
        md.append("## CI / Lane Guard Changes\n")
        for p in sorted(set(guard_touched + ci_files)):
            md.append(f"- `{p}`")
        md.append("")

    # Short action cues (do-not-regress)
    md.append("## Do-Not-Regress Checks (auto-derived)\n")
    cues = []
    if sbom_after and not sbom_before:
        cues.append("- Ensure CI job `audit-validate` publishes SBOM artifact; block merges if SBOM step fails.")
    if any(p.endswith("DEPENDENCY_MATRIX.json") for p, _, _ in key_rows):
        cues.append("- Re-run referential integrity (master ↔ dependency matrix) and update `provenance`.")
    if any(p.endswith("LUKHAS_ARCHITECTURE_MASTER.json") for p, _, _ in key_rows):
        cues.append("- Confirm all `module_uid`s exist and lanes match `AUDIT/LANES.yaml`.")
    if any(p.startswith("tests/") for _, p in changes):
        cues.append("- Keep `contracts-smoke` green; add new tests to nightly dashboard counts.")
    if any(p.startswith(".github/workflows/") for _, p in changes):
        cues.append("- Verify `SELF_HEALING_DISABLED=1` remains set in CI for safety.")
    if not cues:
        cues.append("- No critical governance deltas detected.")
    md.extend(cues)
    md.append("")

    # Optional: append a compact commit list (first 40)
    md.append("## Commits (compact)\n")
    clines = commit_list.splitlines()
    for line in clines[:40]:
        md.append(f"- {line}")
    if len(clines) > 40:
        md.append(f"- …(+{len(clines)-40} more)")

    out.write_text("\n".join(md), encoding="utf-8")
    print(f"OK: wrote {out}")


if __name__ == "__main__":
    main()
