import json
from datetime import datetime


def log_symbolic_event(event_type, context, details):
    entry = {
        "event_type": event_type,
        "context": context,
        "details": details,
        "timestamp": datetime.now().isoformat(),
    }
    with open("trace_logs/symbolic_events.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


# Example usage:
# log_symbolic_event("tier_escalation", user_context, {"from": "Tier3", "to": "Tier5"})
# log_symbolic_event("ethical_violation", user_context, {"pattern": "falsification"})
# log_symbolic_event("intervention", user_context, {"action": "freeze", "reason": "security"})
