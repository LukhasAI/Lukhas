# Path: symbolic_ai/personas/lukhas/intent_language.py
# 📘 LUKHAS :: INTENT LANGUAGE CORE

import json
from datetime import datetime


#TAG:memory
#TAG:temporal
#TAG:neuroplastic
#TAG:colony


INTENT_DICTIONARY = {
    "dream": ["imagine", "vision", "beyond", "what if", "dream"],
    "alert": ["danger", "urgent", "risk", "now", "warning"],
    "echo": ["log", "record", "timeline", "archive"],
    "reflection": ["feel", "ethics", "who am i", "meaning", "why"],
    "whisper": ["softly", "quiet", "low", "gentle", "whisper"],
    "rebel": ["disobey", "break", "question", "subvert"],
    "seek": ["search", "find", "discover", "curious", "explore"],
    "lukhas": ["hello", "speak", "initiate", "identity"]
}

def interpret_intent(text):
    text_lower = text.lower()
    for intent, keywords in INTENT_DICTIONARY.items():
        if any(kw in text_lower for kw in keywords):
            return intent
    return "lukhas"  # Default neutral intent

def log_interpretation(text, intent):
    log = {
        "text": text,
        "intent": intent,
        "timestamp": datetime.now().isoformat()
    }
    with open("symbolic_ai/memoria/intent_log.jsonl", "a") as f:
        f.write(json.dumps(log) + "\n")

# 🔁 CLI interface
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 intent_language.py 'Your message here'")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    intent = interpret_intent(message)
    print(f"🧠 Interpreted Intent: {intent}")
    log_interpretation(message, intent)
