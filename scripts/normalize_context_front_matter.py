#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

FRONT_MATTER_RE = re.compile(r"(?s)\A---\n(.*?)\n---\n(.*)\Z")
YAML_KV_RE = re.compile(r"^([a-zA-Z0-9_]+):\s*(.*)$")

CANONICAL_ORDER = [
    "title","slug","owner","lane","star","stability","last_reviewed",
    "constellation_stars","related_modules","manifests","links"
]

def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _write(p: Path, s: str):
    p.write_text(s, encoding="utf-8")

def _parse_front_matter(raw: str):
    """Very small YAML subset parser for key: value and simple lists/dicts.
    Avoids external deps; preserves unknowns later.
    """
    data = {}
    cur_list = None
    cur_dict = None

    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("- ") and cur_list is not None:
            cur_list.append(line.strip()[2:])
            continue
        # nested dict simple case: key: value under 'links:' etc
        if line.startswith("  ") and ":" in line and cur_dict is not None:
            k,v = line.strip().split(":",1)
            v = v.strip().strip('"')
            cur_dict[k] = v
            continue
        m = YAML_KV_RE.match(line)
        if not m:
            # unknown line, ignore
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "" and key in ("constellation_stars","related_modules","manifests"):
            cur_list = []
            data[key] = cur_list
        elif val == "" and key == "links":
            cur_dict = {}
            data[key] = cur_dict
        else:
            cur_list = None
            cur_dict = None
            data[key] = val.strip('"')
    return data

def _dump_yaml(data: dict) -> str:
    def dump_scalar(k,v):
        if v is None: return f"{k}:"
        if isinstance(v, str):
            # quote only if contains special chars
            if any(c in v for c in [":","#","{","}","[","]","'",'"']):
                return f'{k}: "{v}"'
            return f"{k}: {v}"
        if isinstance(v, (int,float)): return f"{k}: {v}"
        if isinstance(v, list):
            lines = [f"{k}:"]
            for item in v:
                lines.append(f"  - {item}")
            return "\n".join(lines)
        if isinstance(v, dict):
            lines = [f"{k}:"]
            for dk in sorted(v.keys()):
                dv = v[dk]
                if dv is None: lines.append(f"  {dk}:")
                else:
                    if any(c in str(dv) for c in [":","#","{","}","[","]","'",'"']):
                        lines.append(f'  {dk}: "{dv}"')
                    else:
                        lines.append(f"  {dk}: {dv}")
            return "\n".join(lines)
        return f"{k}: {v}"

    # order canonicals first, then any extras in stable alpha order
    out_lines = []
    seen = set()
    for k in CANONICAL_ORDER:
        if k in data:
            out_lines.append(dump_scalar(k, data[k]))
            seen.add(k)
    for k in sorted(k for k in data if k not in seen):
        out_lines.append(dump_scalar(k, data[k]))
    return "\n".join(out_lines)

def _merge(a: dict, b: dict) -> dict:
    """b overrides a; lists get merged/deduped/sorted; dicts merged shallowly"""
    out = dict(a)
    for k,v in b.items():
        if isinstance(v, list):
            existing = out.get(k, [])
            merged = sorted({*existing, *v})
            out[k] = list(merged)
        elif isinstance(v, dict):
            ex = out.get(k, {})
            m = dict(ex); m.update(v)  # TODO[T4-ISSUE]: {"code":"E702","ticket":"GH-1031","owner":"consciousness-team","status":"planned","reason":"Multiple statements on one line - split for readability","estimate":"5m","priority":"low","dependencies":"none","id":"_Users_agi_dev_LOCAL_REPOS_Lukhas_scripts_normalize_context_front_matter_py_L108"}
            out[k] = m
        else:
            out[k] = v
    return out

def _extract_or_default_front_matter(text: str):
    m = FRONT_MATTER_RE.match(text)
    if m:
        fm_raw, body = m.group(1), m.group(2)
        return _parse_front_matter(fm_raw), body
    return {}, text

def _render(fm: dict, body: str) -> str:
    return f"---\n{_dump_yaml(fm)}\n---\n{body.lstrip()}"

def _module_slug_from_path(root: Path, file_path: Path) -> str:
    # heuristic: docs/context/a/b/CONTEXT.md -> a.b
    try:
        rel = file_path.relative_to(root)
    except Exception:
        rel = file_path
    parts = list(rel.parts)
    # drop leading 'docs' 'context' like segments
    parts = [p for p in parts if p not in {"docs","context"}]
    if parts and parts[-1].lower().endswith(".md"):
        parts[-1] = parts[-1].rsplit(".",1)[0]
    return ".".join(p for p in parts if p not in {"CONTEXT","context","README"})

def _load_manifest_map(manifests_dir: Path):
    m = {}
    for p in manifests_dir.rglob("*.json"):
        try:
            js = json.loads(_read(p))
        except Exception:
            continue
        slug = js.get("module") or js.get("slug") or js.get("name")
        if not slug: continue
        if isinstance(slug, dict):
            slug = slug.get("name")

        m[slug] = {
            "title": js.get("title") or js.get("name") or (slug.split(".")[-1] if isinstance(slug, str) else ""),
            "lane": js.get("lane") or "labs",
            "star": js.get("star") or js.get("constellation") or "",
            "related": sorted(set(js.get("related_modules", []))),
            "path": str(p),
        }
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context-root", default="docs/context", help="Root directory for context files")
    ap.add_argument("--glob", default="**/*.md", help="Glob for context markdown")
    ap.add_argument("--manifests", default="manifests", help="Manifests root")
    ap.add_argument("--owner", default="T4", help="Default owner if missing")
    ap.add_argument("--stability", default="experimental", help="Default stability")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out-report", default="docs/audits/context_front_matter_report.json")
    args = ap.parse_args()

    ctx_root = Path(args.context_root)
    mdir = Path(args.manifests)
    manifest_map = _load_manifest_map(mdir)

    updated, skipped, missing = [], [], []
    today = dt.date.today().isoformat()

    files = sorted(ctx_root.glob(args.glob))
    for fp in files:
        text = _read(fp)
        fm, body = _extract_or_default_front_matter(text)

        slug = fm.get("slug") or _module_slug_from_path(ctx_root, fp)
        manifest = manifest_map.get(slug)

        # derive canonical fields from manifest (if present)
        derived = {
            "title": (manifest["title"] if manifest else fm.get("title") or slug.split(".")[-1]),
            "slug": slug,
            "owner": fm.get("owner") or args.owner,
            "lane": (manifest["lane"] if manifest else fm.get("lane") or "labs"),
            "star": (manifest["star"] if manifest else fm.get("star") or ""),
            "stability": fm.get("stability") or args.stability,
            "last_reviewed": fm.get("last_reviewed") or today,
            "constellation_stars": sorted(set(
                (fm.get("constellation_stars") or []) + ([manifest["star"]] if manifest and manifest["star"] else [])
            )),
            "related_modules": sorted(set(
                (fm.get("related_modules") or []) + (manifest.get("related", []) if manifest else [])
            )),
            "manifests": sorted(set(
                (fm.get("manifests") or []) + ([manifest["path"]] if manifest else [])
            )),
            "links": fm.get("links") or {},
        }

        new_fm = _merge(fm, derived)

        new_text = _render(new_fm, body)
        if new_text != text:
            updated.append(str(fp))
            if not args.dry_run:
                _write(fp, new_text)
        else:
            skipped.append(str(fp))

        if not manifest:
            missing.append({"file": str(fp), "slug": slug})

    report = {
        "updated_count": len(updated),
        "skipped_count": len(skipped),
        "missing_manifest": missing,
        "updated": updated[:200],  # cap for readability
    }
    Path(report_path := args.out_report).parent.mkdir(parents=True, exist_ok=True)
    Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    if missing:
        # non-fatal exit so CI can still pass; the report lists gaps
        sys.exit(0)

if __name__ == "__main__":
    main()
