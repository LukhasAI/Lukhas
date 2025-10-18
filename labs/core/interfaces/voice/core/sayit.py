# Path: symbolic_ai/personas/lukhas/sayit.py
# 🗣️ Lukhas Symbolic Speech Router

import sys

from symbolic.personas.lukhas_voice import VOICES, speak


def classify(text):
    text_lower = text.lower()
    if any(kw in text_lower for kw in ["dream", "memory", "beyond", "unseen", "imagine"]):
        return "cove"
    elif any(kw in text_lower for kw in ["danger", "alert", "risk", "urgent", "violation"]):
        return "alert"
    elif any(kw in text_lower for kw in ["echo", "log", "record", "recall", "archive"]):
        return "echo"
    elif any(kw in text_lower for kw in ["why", "feel", "meaning", "who am i", "conscious", "ethics"]):
        return "reflection"
    else:
        return "lukhas"


def route(text):
    tone = classify(text)
    speak(text, voice=tone)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sayit.py 'Your symbolic message here'")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    tone = classify(message)
    print(f"\n🗣️ LUKHAS: ({tone}) {message}")

    voice_name = VOICES.get(tone, "Alex")
    print(f"🎙️ Voice: lukhas_voice → {voice_name} ({tone})\n")

    route(message)
