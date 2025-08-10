"""
📄 MODULE       : log_viewer.py
🔍 DESCRIPTION  : CLI tool to inspect and filter symbolic approval logs
🔐 SOURCE       : zk_approval_log.jsonl
🖋️ AUTHOR       : LUKHAS AID SYSTEMS
"""

import argparse
import json
from pathlib import Path

LOG_PATH = Path("dao/zk_approval_log.jsonl")


def load_logs():
    if not LOG_PATH.exists():
        print("[⚠️] No log file found.")
        return []
    with open(LOG_PATH) as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def print_log(entry):
    print(f"\n[📌] Compound: {entry['compound']}")
    print(f"     Timestamp : {entry['timestamp']}")
    print(f"     Approved  : {'✅' if entry['approved'] else '❌'}")
    print("     Votes     :")
    for agent, vote in entry["votes"].items():
        status = "🟢 YES" if vote else ("🔴 NO" if vote is False else "⚫️ NULL")
        print(f"       - {agent}: {status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Symbolic Policy Log Viewer")
    parser.add_argument("--compound", type=str, help="Filter logs by compound name")
    parser.add_argument("--all", action="store_true", help="Show all logs")

    args = parser.parse_args()
    logs = load_logs()

    if args.compound:
        logs = [log for log in logs if log["compound"].lower() == args.compound.lower()]
        print(f"[🔍] Showing logs for compound: {args.compound}")

    elif not args.all:
        print("[ℹ️] Use --all to show all logs or --compound to filter by name.\n")
        exit(0)

    if not logs:
        print("[❌] No matching entries found.")
    else:
        for entry in logs:
            print_log(entry)
