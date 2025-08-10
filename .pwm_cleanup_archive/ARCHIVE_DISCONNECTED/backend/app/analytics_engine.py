"""
╭──────────────────────────────────────────────────────────────╮
│ MODULE      : analytics_engine.py                            │
│ DESCRIPTION : Symbolic usage and resonance analytics engine  │
│ TYPE        : Insight + Pattern Analysis                     │
│ AUTHOR      : Lukhas Systems                                  │
│ UPDATED     : 2025-04-29                                     │
╰──────────────────────────────────────────────────────────────╯
"""

from datetime import datetime

analytics_log = []


def record_event(user_id: int, event: str, source: str = "unknown"):
    """
    Log a symbolic event into the analytics stream.
    """
    entry = {
        "timestamp": str(datetime.utcnow()),
        "user_id": user_id,
        "event": event,
        "source": source,
    }
    analytics_log.append(entry)
    print(f"📊 Analytics Logged: {entry}")
    return entry


def get_user_analytics(user_id: int):
    """
    Retrieve all analytics events linked to a user.
    """
    return [e for e in analytics_log if e["user_id"] == user_id]


def get_aggregate_events():
    """
    Return aggregate symbolic event counts by event type.
    """
    counts = {}
    for e in analytics_log:
        counts[e["event"]] = counts.get(e["event"], 0) + 1
    return counts
