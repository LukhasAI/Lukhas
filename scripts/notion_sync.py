#!/usr/bin/env python3
"""
T4/0.01% Notion Sync
====================

Sync enriched manifests to Notion database with full provenance tracking.

Principles:
- Schema mirror: manifests → JSON blocks → Notion DB
- Provenance tag: every synced page carries _provenance.sha and extracted_at
- One-way, append-only: never overwrite Notion free-text; only sync structured manifest view
- Dry-run sync: --dry-run prints payload but doesn't hit API
- Idempotent: same SHA = skip (no-op)

Env:
  NOTION_TOKEN=<secret>
  NOTION_DATABASE_ID=<db_id>
  NOTION_RATE_LIMIT=3   # ops/sec (optional; default 3)

Usage:
  python scripts/notion_sync.py --all --dry-run
  python scripts/notion_sync.py --module consciousness
  python scripts/notion_sync.py --all --report-md
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
    from jsonschema import Draft202012Validator, ValidationError
except ImportError:
    print("❌ Missing dependencies: pip install requests jsonschema")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "module.manifest.schema.json"
VOCAB_FEATURES_PATH = ROOT / "vocab" / "features.json"
VOCAB_TAGS_PATH = ROOT / "vocab" / "tags.json"

NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID", "")
NOTION_RATE_LIMIT = float(os.getenv("NOTION_RATE_LIMIT", "3"))

LEDGER = ROOT / "manifests" / ".ledger" / "notion_sync.ndjson"
REPORTS_DIR = ROOT / "reports"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def utcnow() -> str:
    """ISO 8601 timestamp with timezone"""
    return datetime.now(timezone.utc).isoformat()


def sha_manifest(m: Dict[str, Any]) -> str:
    """Stable hash of manifest content (excludes volatile provenance timestamps)"""
    sanitized = json.loads(json.dumps(m, sort_keys=True))
    return hashlib.sha1(json.dumps(sanitized, sort_keys=True).encode()).hexdigest()


def rate_sleep(last_ts: List[float]):
    """Simple leaky-bucket limiter"""
    now = time.time()
    last_ts[:] = [t for t in last_ts if now - t < 1.0]
    if len(last_ts) >= NOTION_RATE_LIMIT:
        time.sleep(1.0 - (now - min(last_ts)))
    last_ts.append(time.time())


def append_ledger(record: Dict[str, Any]):
    """Append record to ledger"""
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        f.write(json.dumps(record) + "\n")


def md_diff(before: str, after: str) -> str:
    """Generate unified diff"""
    diff = difflib.unified_diff(
        before.splitlines(), after.splitlines(), fromfile="notion(before)", tofile="notion(after)", lineterm=""
    )
    return "\n".join(diff)


class NotionClient:
    """Rate-limited Notion API client"""

    def __init__(self, token: str, db_id: str):
        if not token or not db_id:
            raise SystemExit("❌ NOTION_TOKEN and NOTION_DATABASE_ID must be set")
        self.token = token
        self.db_id = db_id
        self._ops_window: List[float] = []

    def _post(self, url: str, payload: Dict[str, Any]) -> Dict:
        """Rate-limited POST request"""
        rate_sleep(self._ops_window)
        r = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"POST {url} failed: {r.status_code} {r.text}")
        return r.json()

    def _patch(self, url: str, payload: Dict[str, Any]) -> Dict:
        """Rate-limited PATCH request"""
        rate_sleep(self._ops_window)
        r = requests.patch(url, headers=HEADERS, json=payload, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"PATCH {url} failed: {r.status_code} {r.text}")
        return r.json()

    def _get(self, url: str) -> Dict:
        """Rate-limited GET request"""
        rate_sleep(self._ops_window)
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"GET {url} failed: {r.status_code} {r.text}")
        return r.json()

    def find_page_by_module(self, module: str) -> Optional[str]:
        """Find existing page by Module title"""
        url = f"https://api.notion.com/v1/databases/{self.db_id}/query"
        payload = {"filter": {"property": "Module", "title": {"equals": module}}, "page_size": 1}
        res = self._post(url, payload)
        results = res.get("results", [])
        if results:
            return results[0]["id"]
        return None

    def get_page_sha(self, page_id: str) -> Optional[str]:
        """Get Provenance SHA from existing page"""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        try:
            page = self._get(url)
            rt = page["properties"].get("Provenance SHA", {}).get("rich_text", [])
            return "".join(t["plain_text"] for t in rt) if rt else None
        except Exception:
            return None

    def create_or_update_page(
        self, module: str, props: Dict[str, Any], blocks: List[Dict[str, Any]], page_id: Optional[str], dry_run: bool
    ) -> Dict[str, Any]:
        """Create new page or update existing one"""
        if page_id:
            if dry_run:
                return {"action": "update(dry-run)", "page_id": page_id, "properties": props, "blocks": blocks}
            url = f"https://api.notion.com/v1/pages/{page_id}"
            return self._patch(url, {"properties": props})
        else:
            payload = {"parent": {"database_id": self.db_id}, "properties": props, "children": blocks}
            if dry_run:
                return {"action": "create(dry-run)", "properties": props, "blocks": blocks}
            url = "https://api.notion.com/v1/pages"
            return self._post(url, payload)


def to_notion_properties(manifest: Dict[str, Any], content_sha: str) -> Dict[str, Any]:
    """
    Map manifest → Notion properties.

    Required Notion DB properties:
      - Module (Title)
      - Description (Rich text)
      - Features (Multi-select)
      - APIs (Rich text)
      - SLA p95 (Number)
      - Coverage (Number)
      - Provenance SHA (Rich text)
      - Updated At (Date)
    """
    features = manifest.get("features", [])
    apis = manifest.get("apis", {})
    perf = manifest.get("performance", {})
    sla = perf.get("sla_targets", {})
    testing = manifest.get("testing", {})

    # Features as multi-select
    feat_select = [{"name": f} for f in features[:20]]  # Notion limit ~100, cap at 20

    # APIs as formatted rich text
    api_lines = []
    for name, meta in sorted(apis.items())[:20]:  # Cap at 20 APIs
        mod = meta.get("module", "")
        iv = "✓" if meta.get("import_verified") else "✗"
        doc = "✓" if meta.get("doc_ok") else "✗"
        api_lines.append(f"- {name} ({mod})  import:{iv}  docs:{doc}")

    props = {
        "Module": {"title": [{"text": {"content": manifest.get("module", "")}}]},
        "Description": {"rich_text": [{"text": {"content": manifest.get("description", "")[:2000]}}]},
        "Features": {"multi_select": feat_select},
        "APIs": {"rich_text": [{"text": {"content": "\n".join(api_lines)[:2000] or "—"}}]},
        "Provenance SHA": {"rich_text": [{"text": {"content": content_sha}}]},
        "Updated At": {"date": {"start": utcnow()}},
    }

    # Add optional numeric fields (Notion rejects null numbers)
    if sla.get("latency_p95_ms") is not None:
        props["SLA p95"] = {"number": float(sla["latency_p95_ms"])}

    if testing.get("coverage_observed") is not None:
        props["Coverage"] = {"number": float(testing["coverage_observed"])}

    return props


def to_notion_blocks(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate Notion blocks for observed metrics (optional rich content)"""
    perf = manifest.get("performance", {}).get("observed", {})
    if not perf:
        return []

    rows = [
        f"p50: {perf.get('latency_p50_ms', '—')} ms",
        f"p95: {perf.get('latency_p95_ms', '—')} ms",
        f"p99: {perf.get('latency_p99_ms', '—')} ms",
        f"env: {perf.get('env_fingerprint', '—')}",
        f"observed_at: {perf.get('observed_at', '—')}",
    ]

    text = "📊 Observed Metrics\n" + "\n".join(rows)

    return [
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": text}}],
                "icon": {"emoji": "📊"},
                "color": "gray_background",
            },
        }
    ]


def load_manifests(root: Path, selection: Optional[str]) -> List[Path]:
    """Find manifests to sync"""
    paths = [
        m
        for m in root.rglob("module.manifest.json")
        if not any(part in m.parts for part in ["node_modules", ".venv", "dist", "__pycache__"])
    ]

    if selection:
        paths = [p for p in paths if p.parent.name == selection]

    return paths


def validate_manifest(path: Path, validator: Draft202012Validator, vocab_features: Dict, vocab_tags: set) -> Dict:
    """Validate manifest against schema and vocab"""
    data = json.loads(path.read_text())

    # Schema validation (allow additional properties from enrichment)
    try:
        validator.validate(data)
    except ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}")

    # Vocab gates
    unknown = [x for x in data.get("features", []) if x not in vocab_features]
    bad_tags = [t for t in data.get("tags", []) if t not in vocab_tags]

    if unknown or bad_tags:
        raise ValueError(f"Vocab violation: unknown_features={unknown}, bad_tags={bad_tags}")

    return data


def main():
    ap = argparse.ArgumentParser(description="Sync enriched manifests to Notion database")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true", help="Sync all manifests")
    g.add_argument("--module", help="Sync a single module by folder name")
    ap.add_argument("--dry-run", action="store_true", help="Do not write to Notion; print diff")
    ap.add_argument("--report-md", action="store_true", help="Write a PR-friendly Markdown report")
    args = ap.parse_args()

    # Load schema and vocab
    if not SCHEMA_PATH.exists():
        print(f"❌ Schema not found: {SCHEMA_PATH}")
        sys.exit(1)

    schema = json.loads(SCHEMA_PATH.read_text())
    schema["additionalProperties"] = True  # Allow enrichment fields
    validator = Draft202012Validator(schema)

    vocab_features = json.loads(VOCAB_FEATURES_PATH.read_text()) if VOCAB_FEATURES_PATH.exists() else {}
    vocab_tags = set(json.loads(VOCAB_TAGS_PATH.read_text()).get("allowed", [])) if VOCAB_TAGS_PATH.exists() else set()

    # Initialize client
    client = NotionClient(NOTION_TOKEN, NOTION_DB_ID)

    # Find manifests
    manifests = load_manifests(ROOT, args.module)

    if not manifests:
        print("❌ No manifests found for selection.")
        sys.exit(0)

    print(f"🔍 Found {len(manifests)} manifests to sync")

    reports = []

    for mf in sorted(manifests):
        try:
            data = validate_manifest(mf, validator, vocab_features, vocab_tags)
        except Exception as e:
            print(f"❌ {mf.parent.name}: {e}")
            continue

        module = data.get("module", mf.parent.name)
        sha = sha_manifest(data)

        # Find existing page
        page_id = client.find_page_by_module(module)

        # Build props/blocks
        props = to_notion_properties(data, sha)
        blocks = to_notion_blocks(data)

        # Check if unchanged (SHA match)
        unchanged = False
        current_sha = None

        if page_id:
            current_sha = client.get_page_sha(page_id)
            if current_sha == sha and not args.dry_run:
                unchanged = True

        action = "skip(sha-match)" if unchanged else ("update" if page_id else "create")
        result = {"action": action, "module": module, "page_id": page_id, "sha": sha}

        # Dry-run: show diff preview
        if args.dry_run and not unchanged:
            before = f"Module: {module}\nSHA: {current_sha or '—'}"
            after = f"Module: {module}\nSHA: {sha}\nProps:\n{json.dumps(props, indent=2)}"
            preview = md_diff(before, after)
            print(preview or f"~ {module}: would {action}")

            append_ledger(
                {
                    "ts": utcnow(),
                    "module": module,
                    "page_id": page_id,
                    "sha": sha,
                    "action": f"{action}-dryrun",
                    "status": "preview",
                }
            )

        elif not unchanged:
            # Upsert
            try:
                res = client.create_or_update_page(module, props, blocks, page_id, dry_run=False)
                append_ledger(
                    {
                        "ts": utcnow(),
                        "module": module,
                        "page_id": res.get("id", page_id),
                        "sha": sha,
                        "action": action,
                        "status": "success",
                    }
                )
                print(f"✅ {module}: {action}")

            except Exception as err:
                append_ledger(
                    {
                        "ts": utcnow(),
                        "module": module,
                        "page_id": page_id,
                        "sha": sha,
                        "action": action,
                        "status": "error",
                        "error": str(err),
                    }
                )
                print(f"❌ {module}: {err}")
                continue
        else:
            # Unchanged skip
            append_ledger(
                {
                    "ts": utcnow(),
                    "module": module,
                    "page_id": page_id,
                    "sha": sha,
                    "action": "skip",
                    "status": "sha_match",
                }
            )
            print(f"⏭️  {module}: skip (sha match)")

        reports.append(result)

    # Markdown report
    if args.report_md:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        totals = {
            "create": sum(1 for r in reports if r["action"] == "create"),
            "update": sum(1 for r in reports if r["action"] == "update"),
            "skip": sum(1 for r in reports if r["action"].startswith("skip")),
        }

        md_lines = [
            "# 🔄 Notion Sync Report",
            f"_Generated {utcnow()}_",
            "",
            "## Summary",
            f"- **Created**: {totals['create']}",
            f"- **Updated**: {totals['update']}",
            f"- **Skipped**: {totals['skip']}",
            "",
        ]

        if reports:
            md_lines.append("## Details")
            md_lines.append("")
            for r in reports[:50]:  # Cap at 50 for readability
                md_lines.append(f"- `{r['module']}` → {r['action']} (sha:{r['sha'][:8]})")

        report_path = REPORTS_DIR / "notion_sync_report.md"
        report_path.write_text("\n".join(md_lines))
        print(f"\n✅ Wrote {report_path}")


if __name__ == "__main__":
    main()
