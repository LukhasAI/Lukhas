# dashboards/router.py

from id_portal.backend.app.tier_manager import get_user_tier

# import streamlit as st  # TODO: Install or implement streamlit

# #ΛGATEWAY_NODE

# TAG:bridge
# TAG:api
# TAG:neuroplastic
# TAG:colony


def route_user_dashboard(user_id: str):
    # #AIDENTITY_TRACE
    tier = get_user_tier(user_id)

    dashboard_map = {
        1: "dashboards/public_dashboard.py",
        2: "dashboards/dev_dashboard.py",
        3: "dashboards/dev_dashboard.py",
        4: "dashboards/research_dashboard.py",
        5: "dashboards/ai_supervision_dashboard.py",  # Placeholder for Tier 5
    }

    dashboard = dashboard_map.get(tier)

    if dashboard:
        st.switch_page(dashboard)
    else:
        st.error("🚫 Invalid tier level. Please contact an administrator.")
