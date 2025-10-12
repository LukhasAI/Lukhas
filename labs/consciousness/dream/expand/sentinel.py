"""
Ethical Sentinel: monitors thresholds and blocks unsafe dreams.
"""
THRESHOLDS = {"fear": 0.8}

def detect(snapshot: dict) -> bool:
    emo = snapshot.get("emotional_context", {})
    return any(emo.get(k,0) > v for k,v in THRESHOLDS.items())