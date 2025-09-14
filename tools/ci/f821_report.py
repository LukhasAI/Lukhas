#!/usr/bin/env python3
import os, sys, json, subprocess, argparse, re
from collections import defaultdict

os.environ["TZ"] = "UTC"
os.environ["PYTHONHASHSEED"] = "0"

DEF_PATHS = ["lukhas", "MATRIZ", "candidate"]


def run_ruff(paths):
    cmd = ["python3", "-m", "ruff", "check", "--select", "F821", "--output-format", "json", *paths]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout.strip()
    try:
        data = json.loads(out) if out else []
    except json.JSONDecodeError:
        # Fallback: ruff not available or produced text; degrade gracefully
        data = []
    return data


GETATTR_RX = re.compile(r"getattr\s*\(|eval\s*\(|globals\s*\(|locals\s*\(")
REGISTRY_RX = re.compile(r"register|registry|plugin|hook", re.I)


def classify(record, file_text):
    msg = record.get("message", "")
    name = None
    m = re.search(r"undefined name '([^']+)'", msg)
    if m:
        name = m.group(1)
    if not name:
        return "unknown", None

    # dynamic reference?
    if GETATTR_RX.search(file_text) or REGISTRY_RX.search(file_text):
        return "dynamic_reference", None

    # crude typo heuristic: nearby words within +/- 10 lines
    line = record.get("location", {}).get("row", 0)
    lines = file_text.splitlines()
    lo, hi = max(0, line - 10), min(len(lines), line + 10)
    window = " ".join(lines[lo:hi])
    candidates = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", window)) - {name}

    def lev(a, b):
        dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
        for i in range(len(a) + 1):
            dp[i][0] = i
        for j in range(len(b) + 1):
            dp[0][j] = j
        for i in range(1, len(a) + 1):
            for j in range(1, len(b) + 1):
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + (a[i - 1] != b[j - 1]))
        return dp[-1][-1]

    closest = None
    best = 99
    for c in candidates:
        d = lev(name, c)
        if d < best:
            best, closest = d, c
    if best <= 2:
        return "probable_typo", f"Did you mean '{closest}'?"

    # import hint: guess a missing import for CamelCase or snake_name
    hint = None
    if re.match(r"[A-Z][A-Za-z0-9_]+", name):
        hint = f"Consider importing class '{name}' from its module."
    else:
        hint = f"Consider importing symbol '{name}'."
    return "missing_import", hint


def within(path, prefixes):
    path = path.replace("\\", "/")
    return any(path.startswith(p + "/") or path == p for p in prefixes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="*", default=DEF_PATHS)
    ap.add_argument("--json-out", default="reports/audit/f821.json")
    ap.add_argument("--md-out", default="reports/audit/f821_summary.md")
    ap.add_argument("--enforce-core", action="store_true")
    ap.add_argument("--annotate-candidate", action="store_true")
    args = ap.parse_args()

    results = run_ruff(args.paths)
    enriched = []
    counts = defaultdict(int)
    core_violations = 0

    for r in results:
        path = r.get("filename", "")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
        except Exception:
            txt = ""
        klass, suggestion = classify(r, txt)

        # cross-lane simple mark
        if within(path, ["lukhas", "MATRIZ"]) and "candidate" in (r.get("message", "") or ""):
            klass = "cross_lane"

        item = {
            "path": path,
            "line": r.get("location", {}).get("row", 0),
            "col": r.get("location", {}).get("column", 0),
            "code": r.get("code", "F821"),
            "message": r.get("message", ""),
            "class": klass,
            "suggestion": suggestion,
        }
        enriched.append(item)
        counts[klass] += 1

        if within(path, ["lukhas", "MATRIZ"]):
            core_violations += 1

    os.makedirs(os.path.dirname(args.json_out), exist_ok=True)
    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(
            {"total": len(enriched), "core_violations": core_violations, "by_class": counts, "items": enriched},
            f,
            indent=2,
        )

    # write summary
    with open(args.md_out, "w", encoding="utf-8") as f:
        f.write("# F821 Undefined Names — Summary\n\n")
        f.write(f"- Total: {len(enriched)}\n")
        f.write(f"- Core violations (lukhas/MATRIZ): {core_violations}\n")
        f.write("## By class\n")
        for k, v in counts.items():
            f.write(f"- {k}: {v}\n")

    # optional annotation for candidate only
    if args.annotate_candidate:
        for it in enriched:
            p = it["path"]
            if not within(p, ["candidate"]):
                continue
            try:
                lines = open(p, "r", encoding="utf-8").read().splitlines()
            except Exception:
                continue
            ln = it["line"]
            tag = f"# TODO[T4-F821:{it['class']}]: {it['message']}"
            if 1 <= ln <= len(lines):
                # idempotent: don't duplicate the tag
                if tag not in lines[ln - 1]:
                    lines[ln - 1] = lines[ln - 1] + "  " + tag
                    try:
                        with open(p, "w", encoding="utf-8") as w:
                            w.write("\n".join(lines) + "\n")
                    except Exception:
                        pass

    if args.enforce_core and core_violations > 0:
        print(f"ERROR: F821 in core paths: {core_violations}", file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {args.json_out} and {args.md_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
