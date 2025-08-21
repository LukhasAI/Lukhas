"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: delivery_tracker_widget.py
Advanced: delivery_tracker_widget.py
Integration Date: 2025-05-31T07:55:30.487994
"""

"""
┌────────────────────────────────────────────────────────────────────────────┐
│ MODULE         : delivery_tracker_widget.py                                │
│ DESCRIPTION    :                                                           │
│   Dynamically generates and updates delivery tracking widgets across       │
│   vendors (FedEx, UberEats, USPS, RoyalMail).                             │
│   Integrates with Lukhas DST, NIAS, and Vendor APIs for real-time sync.     │
│ TYPE           : Real-Time Delivery Widget Engine                          │
│ VERSION        : v1.0.0                                                    │
│ AUTHOR         : LUKHAS SYSTEMS                                             │
│ CREATED        : 2025-04-22                                                │
└────────────────────────────────────────────────────────────────────────────┘
"""

import uuid
from datetime import datetime


def create_delivery_widget(
    vendor, delivery_id, user_tier, estimated_eta, delivery_status="in_transit"
):
    """
    Creates a delivery tracker widget for visualization in dashboard.

    Parameters:
    - vendor (str): Delivery vendor name (e.g. 'FedEx', 'Uber Eats')
    - delivery_id (str): Unique delivery or order ID
    - user_tier (int): Lukhas ID tier (0–5)
    - estimated_eta (str): ISO timestamp string for ETA
    - delivery_status (str): Initial status: 'in_transit', 'delayed', 'delivered'

    Returns:
    - dict: delivery widget spec
    """
    tier_icons = {0: "🕸️", 1: "📦", 2: "🚚", 3: "📍", 4: "🛰️", 5: "🌐"}
    color_map = {
        "in_transit": "#2196f3",
        "delayed": "#ff9800",
        "delivered": "#4caf50",
    }

    widget = {
        "type": "delivery_tracking",
        "vendor": vendor,
        "delivery_id": delivery_id,
        "status": delivery_status,
        "eta": estimated_eta,
        "created_at": datetime.utcnow().isoformat(),
        "tracking_id": str(uuid.uuid4()),
        "icon": tier_icons.get(user_tier, "📦"),
        "color": color_map.get(delivery_status, "#9e9e9e"),
        "cta": "Track Delivery" if user_tier >= 2 else "Status Only",
        "animation": {
            "type": "roadmap_path",
            "pulse": True,
            "loop_eta": estimated_eta,
        },
        "DST_hooks": {
            "auto_refresh": True,
            "check_interval_minutes": 10,
            "fallback_vendor_query": True,
        },
    }

    return widget


def update_delivery_status(widget, new_status, new_eta=None):
    """
    Updates delivery status and ETA of an existing widget.

    Parameters:
    - widget (dict): Existing widget dictionary
    - new_status (str): New status: 'delivered', 'delayed', etc.
    - new_eta (str): Optional updated ETA

    Returns:
    - dict: Updated widget
    """
    color_map = {
        "in_transit": "#2196f3",
        "delayed": "#ff9800",
        "delivered": "#4caf50",
    }

    widget["status"] = new_status
    widget["color"] = color_map.get(new_status, "#9e9e9e")

    if new_eta:
        widget["eta"] = new_eta

    return widget
