#!/usr/bin/env python3
"""
Module: notion_sync.py

This module is part of the LUKHAS repository.
Add detailed documentation and examples as needed.
"""

"""T4/0.01% Notion/Dashboard Sync Integration

Syncs META_REGISTRY.json and coverage trends to external dashboards.
Supports Notion, Grafana, and generic webhook integrations.

Features:
- Notion database sync (requires NOTION_TOKEN and NOTION_DATABASE_ID)
- Grafana dashboard updates (requires GRAFANA_URL and GRAFANA_API_KEY)
- Generic webhook POST (requires WEBHOOK_URL)
- Dry-run mode for testing
- Incremental sync (only changed modules)

Usage:
    # Sync to Notion
    python3 scripts/integrations/notion_sync.py --source docs/_generated/META_REGISTRY.json --target notion

    # Sync to Grafana
    python3 scripts/integrations/notion_sync.py --source docs/_generated/META_REGISTRY.json --target grafana

    # Dry-run (no actual API calls)
    python3 scripts/integrations/notion_sync.py --source docs/_generated/META_REGISTRY.json --dry-run

Environment variables:
    NOTION_TOKEN - Notion integration token
    NOTION_DATABASE_ID - Target Notion database ID
    GRAFANA_URL - Grafana instance URL
    GRAFANA_API_KEY - Grafana API key
    WEBHOOK_URL - Generic webhook endpoint

Exit codes:
    0 - Sync successful
    1 - Sync failed (missing config or API error)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("❌ requests library not installed")
    print("   Install with: pip install requests")
    sys.exit(1)


class SyncConfig:
    """Sync configuration from environment variables"""

    def __init__(self):
        self.notion_token = os.getenv("NOTION_TOKEN")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        self.grafana_url = os.getenv("GRAFANA_URL")
        self.grafana_api_key = os.getenv("GRAFANA_API_KEY")
        self.webhook_url = os.getenv("WEBHOOK_URL")

    def validate_notion(self) -> bool:
        """Check if Notion config is complete"""
        return bool(self.notion_token and self.notion_database_id)

    def validate_grafana(self) -> bool:
        """Check if Grafana config is complete"""
        return bool(self.grafana_url and self.grafana_api_key)

    def validate_webhook(self) -> bool:
        """Check if webhook config is complete"""
        return bool(self.webhook_url)


def load_meta_registry(path: Path) -> dict[str, Any]:
    """Load META_REGISTRY.json"""
    if not path.exists():
        print(f"❌ File not found: {path}")
        sys.exit(1)

    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"❌ Failed to parse {path}: {e}")
        sys.exit(1)


def sync_to_notion(data: dict[str, Any], config: SyncConfig, dry_run: bool) -> bool:
    """Sync data to Notion database"""
    if not config.validate_notion():
        print("❌ Notion configuration incomplete")
        print("   Set NOTION_TOKEN and NOTION_DATABASE_ID environment variables")
        return False

    print(f"📊 Syncing to Notion database: {config.notion_database_id}")

    if dry_run:
        print("   🔍 DRY RUN - Would sync:")
        print(f"      Modules: {data.get('module_count', 0)}")
        print(f"      Avg health: {data.get('summary', {}).get('avg_health_score', 0)}")
        return True

    headers = {
        "Authorization": f"Bearer {config.notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Sync each module as a Notion page
    modules = data.get("modules", [])
    synced = 0
    failed = 0

    for module in modules:
        try:
            # Create Notion page properties
            properties = {
                "Name": {"title": [{"text": {"content": module["module"]}}]},
                "Lane": {"select": {"name": module.get("lane", "L2")}},
                "Coverage": {"number": module.get("coverage", {}).get("observed", 0)},
                "Health Score": {"number": module.get("health_score", 0)},
                "Docs": {"number": module.get("docs_count", 0)},
                "Tests": {"number": module.get("tests_count", 0)},
            }

            payload = {
                "parent": {"database_id": config.notion_database_id},
                "properties": properties
            }

            response = requests.post(
                "https://api.notion.com/v1/pages",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code in (200, 201):
                synced += 1
            else:
                print(f"   ⚠️  Failed to sync {module['module']}: {response.status_code}")
                failed += 1

        except Exception as e:
            print(f"   ❌ Error syncing {module.get('module', 'unknown')}: {e}")
            failed += 1

    print(f"   ✅ Synced {synced}/{len(modules)} modules ({failed} failed)")
    return failed == 0


def sync_to_grafana(data: dict[str, Any], config: SyncConfig, dry_run: bool) -> bool:
    """Sync data to Grafana via metrics endpoint"""
    if not config.validate_grafana():
        print("❌ Grafana configuration incomplete")
        print("   Set GRAFANA_URL and GRAFANA_API_KEY environment variables")
        return False

    print(f"📊 Syncing to Grafana: {config.grafana_url}")

    if dry_run:
        print("   🔍 DRY RUN - Would sync:")
        print(f"      Modules: {data.get('module_count', 0)}")
        print(f"      Avg health: {data.get('summary', {}).get('avg_health_score', 0)}")
        return True

    # Prepare metrics in Grafana format
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    metrics = []

    for module in data.get("modules", []):
        module_name = module["module"]

        # Coverage metric
        if "coverage" in module and module["coverage"].get("observed") is not None:
            metrics.append({
                "name": "lukhas_coverage",
                "metric": f"coverage_{module_name}",
                "value": module["coverage"]["observed"],
                "timestamp": timestamp
            })

        # Health score metric
        if "health_score" in module:
            metrics.append({
                "name": "lukhas_health",
                "metric": f"health_{module_name}",
                "value": module["health_score"],
                "timestamp": timestamp
            })

    # Send to Grafana
    headers = {
        "Authorization": f"Bearer {config.grafana_api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{config.grafana_url}/api/datasources/proxy/1/api/v1/write",
            headers=headers,
            json=metrics,
            timeout=30
        )

        if response.status_code in (200, 204):
            print(f"   ✅ Synced {len(metrics)} metrics to Grafana")
            return True
        else:
            print(f"   ❌ Grafana sync failed: {response.status_code}")
            print(f"      {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Grafana sync error: {e}")
        return False


def sync_to_webhook(data: dict[str, Any], config: SyncConfig, dry_run: bool) -> bool:
    """Sync data to generic webhook"""
    if not config.validate_webhook():
        print("❌ Webhook configuration incomplete")
        print("   Set WEBHOOK_URL environment variable")
        return False

    print(f"📊 Syncing to webhook: {config.webhook_url}")

    if dry_run:
        print("   🔍 DRY RUN - Would POST data to webhook")
        return True

    try:
        response = requests.post(
            config.webhook_url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code in (200, 201, 202, 204):
            print(f"   ✅ Webhook sync successful ({response.status_code})")
            return True
        else:
            print(f"   ❌ Webhook sync failed: {response.status_code}")
            print(f"      {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Webhook sync error: {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync META_REGISTRY to external dashboards"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("docs/_generated/META_REGISTRY.json"),
        help="Source META_REGISTRY.json file"
    )
    parser.add_argument(
        "--target",
        choices=["notion", "grafana", "webhook", "all"],
        default="all",
        help="Target integration (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode (no actual API calls)"
    )

    args = parser.parse_args()

    print("🔄 T4/0.01% Dashboard Sync")
    print(f"   Source: {args.source}")
    print(f"   Target: {args.target}")
    print(f"   Dry-run: {args.dry_run}")
    print()

    # Load data
    data = load_meta_registry(args.source)
    config = SyncConfig()

    # Sync to targets
    results = []

    if args.target in ("notion", "all"):
        results.append(("Notion", sync_to_notion(data, config, args.dry_run)))

    if args.target in ("grafana", "all"):
        results.append(("Grafana", sync_to_grafana(data, config, args.dry_run)))

    if args.target in ("webhook", "all"):
        results.append(("Webhook", sync_to_webhook(data, config, args.dry_run)))

    # Summary
    print()
    print("=" * 80)
    print("SYNC SUMMARY")
    print("=" * 80)

    all_success = True
    for target, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{target:15} {status}")
        if not success:
            all_success = False

    print()

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
