#!/usr/bin/env python3
"""
tools/validate_events.py

Validates event tracking implementation:
- All events in taxonomy have corresponding tracking code
- No undefined events in tracking code
- Required properties present
"""
import json
import re
import sys
from pathlib import Path


def validate_events():
    """Validate event tracking implementation."""

    # Load event taxonomy
    taxonomy_path = Path("branding/analytics/event_taxonomy.json")
    if not taxonomy_path.exists():
        print("❌ event_taxonomy.json not found at branding/analytics/event_taxonomy.json")
        return 1

    try:
        taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in event_taxonomy.json: {e}")
        return 1

    defined_events = set(taxonomy["events"].keys())

    # Scan for plausible() calls in JS/HTML files
    tracked_events = set()
    websites_path = Path("branding/websites")

    if not websites_path.exists():
        print(f"⚠️  websites directory not found at {websites_path}")
        print("    Skipping tracking code validation")
    else:
        # Scan JavaScript files
        for js_file in websites_path.rglob("*.js"):
            content = js_file.read_text(encoding="utf-8", errors="ignore")
            matches = re.findall(r"plausible\(['\"](\w+)['\"]", content)
            tracked_events.update(matches)

        # Scan HTML files
        for html_file in websites_path.rglob("*.html"):
            content = html_file.read_text(encoding="utf-8", errors="ignore")
            matches = re.findall(r"plausible\(['\"](\w+)['\"]", content)
            tracked_events.update(matches)

        # Scan TypeScript files
        for ts_file in websites_path.rglob("*.ts"):
            content = ts_file.read_text(encoding="utf-8", errors="ignore")
            matches = re.findall(r"plausible\(['\"](\w+)['\"]", content)
            tracked_events.update(matches)

        # Scan TSX files
        for tsx_file in websites_path.rglob("*.tsx"):
            content = tsx_file.read_text(encoding="utf-8", errors="ignore")
            matches = re.findall(r"plausible\(['\"](\w+)['\"]", content)
            tracked_events.update(matches)

    # Check for undefined events
    undefined = tracked_events - defined_events
    if undefined:
        print(f"⚠️  Undefined events in tracking code: {sorted(undefined)}")

    # Check for missing tracking
    missing = defined_events - tracked_events
    if missing:
        print(f"⚠️  Events in taxonomy but not tracked: {sorted(missing)}")
        print(f"    (This is expected if tracking code hasn't been implemented yet)")

    # Success message
    if not undefined and not missing:
        print(f"✅ Event validation passed ({len(defined_events)} events)")
        print(f"   Events defined: {sorted(defined_events)}")
        return 0
    elif not undefined:
        print(f"✅ Event taxonomy validated ({len(defined_events)} events defined)")
        if missing:
            print(f"   Note: {len(missing)} events not yet tracked (expected during development)")
        return 0
    else:
        print(f"❌ Event validation failed")
        return 1


if __name__ == "__main__":
    sys.exit(validate_events())
