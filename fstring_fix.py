#!/usr/bin/env python3
"""
fstring_fix.py — Conservative auto-fixer for common f-string brace syntax errors.

What it does (safe cases only):
  - Finds f-strings like: f"Hello {name"  → adds the missing "}" at the end
  - Skips complex expressions (nested braces, quotes inside expressions, triple-quoted f-strings)
  - Respects escaped literal braces: "{{" and "}}"
  - Writes diffs to stdout; --apply to write files in place
  - Excludes typical third-party/generated paths by default

What it does NOT do (by design):
  - Does not try to balance quotes
  - Does not change business logic or move code
  - Does not attempt deep parsing of f-string expressions

Usage:
  # Dry-run (print planned changes)
  python fstring_fix.py

  # Apply changes in place
  python fstring_fix.py --apply

  # Target a subdir
  python fstring_fix.py --path src/

  # Include/Exclude more paths (comma-separated globs)
  python fstring_fix.py --include "app/**/*.py" --exclude "migrations/**,third_party/**"

Tip: After running with --apply, validate:
  .venv/bin/ruff check . --select=SYNTAX --output-format=concise
  # Optionally only re-check changed files with --force-exclude and explicit paths.
"""
import argparse
import difflib
import sys
from pathlib import Path

DEFAULT_EXCLUDES = [
    ".venv/**", "venv/**", "env/**",
    "**/site-packages/**", "**/dist/**", "**/build/**",
    "**/__pycache__/**", "**/.mypy_cache/**", "**/.ruff_cache/**",
    "migrations/**", "third_party/**", "vendor/**", "generated/**",
]

def iter_python_files(root: Path, includes, excludes):
    """Yield Python files under root obeying include/exclude globs."""
    # Start from includes if provided, otherwise the root tree.
    if includes:
        inc_files = set()
        for pattern in includes:
            inc_files.update(root.glob(pattern))
        candidates = [p for p in inc_files if p.is_file() and p.suffix == ".py"]
    else:
        candidates = [p for p in root.rglob("*.py")]

    # Build exclude set
    excluded = set()
    for pattern in excludes or []:
        excluded.update(root.glob(pattern))

    for p in sorted(candidates):
        skip = False
        # If p is under any excluded dir/glob, skip.
        for ex in excluded:
            try:
                # For globs that are files or directories, compare parents.
                if p == ex or ex in p.parents:
                    skip = True
                    break
            except Exception:
                continue
        if not skip:
            yield p

def is_fstring_prefix(prefix: str) -> bool:
    # Valid f-string prefixes: f, F, rf, fr, rF, Fr, etc., but we skip raw forms to be safe.
    prefix_lower = prefix.lower()
    if 'f' not in prefix_lower:
        return False
    # Raw f-strings (rf/fr) have tricky escapes; skip them for safety
    if 'r' in prefix_lower:
        return False
    return True

def find_fstring_spans(line: str):
    """
    Return a list of (start_idx, end_idx, quote_char, triple) for f-string literals in a line.
    We do a lightweight scan: look for prefixes like f' or f" (case-insensitive).
    We skip triple-quoted strings to keep it simple/safe.
    """
    spans = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch in ('"', "'"):
            # Normal string without f-prefix; skip to its end
            q = ch
            j = i + 1
            while j < n:
                if line[j] == '\\':
                    j += 2
                    continue
                if line[j] == q:
                    j += 1
                    break
                j += 1
            i = j
            continue
        # Possible prefix sequence of letters before a quote
        if ch.isalpha():
            j = i
            while j < n and line[j].isalpha():
                j += 1
            if j < n and line[j] in ("'", '"'):
                prefix = line[i:j]
                q = line[j]
                # Check for triple quotes
                is_triple = (j + 2 < n and line[j+1] == q and line[j+2] == q)
                if is_fstring_prefix(prefix) and not is_triple:
                    # Find the end of the string
                    k = j + 1
                    while k < n:
                        if line[k] == '\\':
                            k += 2
                            continue
                        if line[k] == q:
                            k += 1
                            break
                        k += 1
                    spans.append((i, k, q, False))
                    i = k
                    continue
                else:
                    # Skip this string (either not f, or triple; consume it)
                    k = j + (3 if is_triple else 1)
                    while k < n:
                        if line[k] == '\\':
                            k += 2
                            continue
                        # End for triple vs single
                        if is_triple:
                            if (k + 2 < n) and line[k] == q and line[k+1] == q and line[k+2] == q:
                                k += 3
                                break
                        else:
                            if line[k] == q:
                                k += 1
                                break
                        k += 1
                    i = k
                    continue
        i += 1
    return spans

def simple_expression_ok(s: str) -> bool:
    """
    Heuristic gate: Only auto-fix if expressions are "simple".
    - No nested braces depth > 1
    - No quotes inside braces
    """
    depth = 0
    in_brace = False
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        # Handle escaped literal braces
        if c == '{':
            if i + 1 < n and s[i+1] == '{':
                i += 2
                continue
            depth += 1
            in_brace = True
            if depth > 1:
                return False
            i += 1
            continue
        if c == '}':
            if i + 1 < n and s[i+1] == '}':
                i += 2
                continue
            depth -= 1
            in_brace = depth > 0
            i += 1
            continue
        if in_brace and c in ("'", '"'):
            # Quotes inside expression => skip as complex
            return False
        i += 1
    return True

def missing_closing_braces_count(s: str) -> int:
    """Count how many closing braces are needed to balance top-level f-string fields."""
    depth = 0
    i = 0
    n = len(s)
    for i in range(n):
        c = s[i]
        if c == '{':
            if i + 1 < n and s[i+1] == '{':
                i += 1
                continue
            depth += 1
        elif c == '}':
            if i + 1 < n and s[i+1] == '}':
                i += 1
                continue
            if depth > 0:
                depth -= 1
            else:
                # Stray closing brace; we won't "fix" this automatically.
                pass
    return depth

def fix_line(line: str):
    """
    Attempt to fix missing '}' in simple f-strings on a single line.
    Returns (new_line, num_fixes_applied_on_line).
    """
    spans = find_fstring_spans(line)
    if not spans:
        return line, 0

    new_line = line
    offset = 0
    fixes = 0
    for (start, end, q, _triple) in spans:
        start += offset
        end += offset
        segment = new_line[start:end]

        # Extract the inner content between the opening quote and the ending quote
        # segment example: f"hello {name"
        first_quote_idx = segment.find(q)
        if first_quote_idx == -1:
            continue
        inner = segment[first_quote_idx+1:-1]  # omit surrounding quotes

        # Heuristic: only touch if simple enough
        if not simple_expression_ok(inner):
            continue

        missing = missing_closing_braces_count(inner)
        if missing <= 0:
            continue

        # Insert the missing number of '}' right before the closing quote.
        fixed_inner = inner + ('}' * missing)
        fixed_segment = segment[:first_quote_idx+1] + fixed_inner + segment[-1:]
        # Update line
        new_line = new_line[:start] + fixed_segment + new_line[end:]
        # Update offset for subsequent spans
        offset += len(fixed_segment) - (end - start)
        fixes += missing
    return new_line, fixes

def process_file(path: Path, apply: bool = False):
    original = path.read_text(encoding="utf-8", errors="ignore")
    fixed_lines = []
    total_fixes = 0
    changed = False
    for line in original.splitlines(keepends=True):
        new_line, fixes = fix_line(line)
        if fixes:
            changed = True
            total_fixes += fixes
        fixed_lines.append(new_line)

    if not changed:
        return False, 0, ""

    new_content = "".join(fixed_lines)

    if not apply:
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
        )
        return True, total_fixes, "".join(diff)
    else:
        path.write_text(new_content, encoding="utf-8")
        return True, total_fixes, ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=".", help="Root path to scan")
    parser.add_argument("--apply", action="store_true", help="Apply fixes in place")
    parser.add_argument("--include", default="", help="Comma-separated globs to include (relative to --path)")
    parser.add_argument("--exclude", default="", help="Comma-separated globs to exclude (relative to --path)")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Path not found: {root}", file=sys.stderr)
        sys.exit(2)

    includes = [g.strip() for g in args.include.split(",") if g.strip()] or None
    excludes = [g.strip() for g in args.exclude.split(",") if g.strip()] or []
    # Add defaults
    excludes = list(set(excludes + DEFAULT_EXCLUDES))

    changed_files = 0
    total_inserted = 0

    for py in iter_python_files(root, includes, excludes):
        changed, fixes, diff = process_file(py, apply=args.apply)
        if changed:
            changed_files += 1
            total_inserted += fixes
            if not args.apply and diff:
                sys.stdout.write(diff)

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] Changed files: {changed_files}, braces inserted: {total_inserted}")
    if not args.apply:
        print("Use --apply to write changes.")

if __name__ == "__main__":
    main()
