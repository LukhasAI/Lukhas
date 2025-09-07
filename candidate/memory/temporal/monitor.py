#!/usr/bin/env python3
"""

#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


ΛBot AGI Real-Time Status Monitor
===============================
Monitor the autonomous AGI system in real-time
"""
import streamlit as st

import json
import os
import time
from datetime import datetime, timezone


def monitor_agi_system():
    """Monitor the running AGI system"""
    print("🤖 ΛBot AGI Real-Time Monitor")
    print("=" * 50)
    print("Monitoring autonomous operations...")
    print("Press Ctrl+C to stop monitoring")
    print("=" * 50)

    while True:
        try:
            # Check for recent status files
            status_files = [f for f in os.listdir(".") if f.startswith("autonomous_") and f.endswith(".json")]

            if status_files:
                latest_file = sorted(status_files)[-1]

                try:
                    with open(latest_file) as f:
                        status = json.load(f)

                    print(f"\n🕐 {datetime.now(timezone.utc).strftime('%H:%M:%S')} - Latest Status:")
                    print(f"📊 Tasks: {status.get('completed', 0)} completed, {status.get('failed', 0)} failed")
                    print(f"💰 Budget Used: ${status.get('budget_used', 0):.4f}")

                    if "recent_prs" in status:
                        print(f"🔗 PRs Created: {len(status['recent_prs'])}")
                        for pr in status["recent_prs"][-3:]:
                            print(f"   • {pr}")

                except BaseException:
                    pass

            # Check budget controller state
            try:
                with open("token_budget_state.json") as f:
                    budget_state = json.load(f)

                daily_spend = budget_state.get("daily_spend", 0)
                print(f"💳 Total Spend Today: ${daily_spend:.4f}")

            except BaseException:
                pass

            time.sleep(10)  # Update every 10 seconds

        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            break
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    monitor_agi_system()
