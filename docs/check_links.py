#!/usr/bin/env python3
"""
Link checker for internal docs.

- Scans all Markdown files under ./docs and ./manifests for:
  - relative file links (./path.md, ../path, docs/foo.md)
  - in-file anchors (#heading) — verified against actual headings
  - optional external http(s) links (opt-in via --external)
- Writes a report to docs/audits/linkcheck.txt
- Exits 1 if any internal links are broken (external links are WARNs unless --strict)

Usage:
  python docs/check_links.py [--root .] [--external] [--strict]
"""
import argparse
import pathlib
import re
import sys
import urllib.error
import urllib.request

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*)\s*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def slugify(text: str) -> str:
    import unicodedata

    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[\s]+", "-", text)
    return text


def extract_headings(md_text: str):
    anchors = set()
    for line in md_text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            anchors.add("#" + slugify(m.group(1)))
    return anchors


def iter_markdown_files(root: pathlib.Path):
    for p in root.rglob("*.md"):
        if any(seg in p.parts for seg in (".venv", "venv", ".git")):
            continue
        yield p


def is_external(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def check_external(url: str) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as r:
            return 200 <= r.status < 400
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--external", action="store_true")
    ap.add_argument("--strict", action="store_true", help="fail build on bad external links too")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    docs = root / "docs"
    manifests = root / "manifests"
    audit_dir = docs / "audits"
    audit_dir.mkdir(parents=True, exist_ok=True)
    report = []

    broken_internal = 0
    broken_external = 0

    # cache headings for anchors
    heading_cache = {}

    for md in list(iter_markdown_files(docs)) + (list(iter_markdown_files(manifests)) if manifests.exists() else []):
        text = md.read_text(encoding="utf-8", errors="ignore")
        anchors = extract_headings(text)
        heading_cache[md] = anchors

    for md in list(iter_markdown_files(docs)) + (list(iter_markdown_files(manifests)) if manifests.exists() else []):
        base = md.parent
        text = md.read_text(encoding="utf-8", errors="ignore")
        for m in LINK_RE.finditer(text):
            url = m.group(1).strip()
            if url.startswith("mailto:") or url.startswith("tel:"):
                continue
            if is_external(url):
                if not args.external:
                    report.append(f"WARN external unchecked: {md}:{m.start()} → {url}")
                else:
                    ok = check_external(url)
                    if not ok:
                        broken_external += 1
                        report.append(f"FAIL external: {md}:{m.start()} → {url}")
                continue

            # split anchor
            path_part, anchor_part = (url.split("#", 1) + [""])[:2]
            target = (base / path_part).resolve() if path_part else md
            if not target.exists():
                broken_internal += 1
                report.append(f"FAIL missing file: {md}:{m.start()} → {url}")
                continue

            if anchor_part:
                anchor = "#" + slugify(anchor_part)
                # target headings
                if target.suffix.lower() == ".md":
                    if target not in heading_cache:
                        heading_cache[target] = extract_headings(target.read_text(encoding="utf-8", errors="ignore"))
                    if anchor not in heading_cache[target]:
                        broken_internal += 1
                        report.append(f"FAIL missing anchor: {md}:{m.start()} → {url}")

    out = "\n".join(report) + ("\n" if report else "")
    (audit_dir / "linkcheck.txt").write_text(out, encoding="utf-8")
    print(out or "OK: no issues found")
    print(f"Broken internal: {broken_internal}; Broken external: {broken_external}")
    if broken_internal or (args.strict and broken_external):
        sys.exit(1)


if __name__ == "__main__":
    main()
