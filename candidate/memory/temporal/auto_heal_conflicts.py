#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


Auto-heal conflicts without user interaction
"""

import json
from datetime import datetime

from conflict_healer import ConflictHealer
from datetime import timezone


def main():
    print("🏥 Starting automatic conflict healing...")

    healer = ConflictHealer()

    # Find conflicts
    conflicts = healer.find_conflict_files()

    if not conflicts:
        print("✅ No conflicts found!")
        return

    print(f"Found {len(conflicts)} files with conflicts")
    print("Starting automatic healing with 'smart' strategy...")

    # Auto-heal all conflicts
    report = healer.heal_all(strategy="smart")

    # Save report
    report_path = f"healing/auto_healing_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📋 Report saved to: {report_path}")

    # Return status
    if report["status"] == "healed":
        print("✅ All conflicts healed successfully!")
        return 0
    else:
        print(f"⚠️  Partially healed: {report['files_failed']} files failed")
        return 1


if __name__ == "__main__":
    exit(main())