"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: gui_launcher.py
Advanced: gui_launcher.py
Integration Date: 2025-05-31T07:55:28.291189
"""
# ===============================================================
# 📂 FILE: gui_launcher.py
# 📍 LOCATION: core/interface/
# ===============================================================
# 🧠 PURPOSE:
# Launches the correct Streamlit dashboard based on user tier.
# Tiers are determined via symbolic identity logic in tier_manager.py
#
# 🛡️ Symbolic Access:
# Tier 1 → Public Dashboard
# Tier 2–3 → Dev Dashboard
# Tier 4 → Research Dashboard
# Tier 5 → AI Supervision Dashboard (future)
#
# ===============================================================
import os
import sys

from lukhas.tools.session_logger import log_session_event


def launch_dashboard(user_id):
    from id_portal.backend.app.tier_manager import get_user_tier

    tier = get_user_tier(user_id)
    print(f"🧠 Launching dashboard for user: {user_id} (Tier {tier})")
    log_session_event(user_id, "launch_dashboard")

    dashboard_map = {
        1: "public_dashboard.py",
        2: "dev_dashboard.py",
        3: "dev_dashboard.py",
        4: "research_dashboard.py",
        5: "ai_supervision_dashboard.py",
    }

    if tier in dashboard_map:
        os.system(f"streamlit run dashboards/{dashboard_map[tier]}")
    else:
        print("❌ Unknown tier. Cannot launch dashboard.")


if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "lukhas_admin"
    launch_dashboard(user_id)
