# lukhas_core.py
# MASTER SYMBOLIC LOOP FOR LUKHAS v1.0 (AIG-GRADE)

from datetime import datetime
import json
from symbolic.memoria import log_memory
from symbolic.lukhas_personality import adjust_personality, LUKHAS_PERSONALITY
from symbolic.lukhas_emotion import analyze_emotion
from symbolic.lukhas_dreams import generate_symbolic_dreams
from symbolic.lukhas_guardian import ethical_check
from symbolic.lukhas_voice import speak
from symbolic.lukhas_reflector import recall_last_interaction
from symbolic.lukhas_visualizer import visualize_dream_output  # optional
from seedra.core.registry import get_user_tier
from seedra_docs.vault_manager import current_sid  # assumes current SID is loaded here

# Entry point for symbolic loop
def process_user_input(user_input):
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(f"\n🧠 [{timestamp}] User said: {user_input}")

    # Load current KYI tier
    user_tier = get_user_tier(current_sid())
    print(f"🔐 Access Tier: {user_tier}")

    # Adjust Lukhas' current personality state
    personality_state = adjust_personality(user_input)
    print(f"🔄 Personality Adjusted: {personality_state}")

    # Analyze emotion & tone from text (includes pitch proxy)
    emotion = analyze_emotion(user_input)
    print(f"🎭 Emotion Detected: {emotion}")

    # Recall symbolic memory trace
    last_context = recall_last_interaction(user_input)
    print(f"📖 Memory Recall: {last_context}")

    # Ethical validation
    if not ethical_check(user_input):
        speak("That request might breach ethical alignment. Let's rephrase.", emotion=emotion)
        return

    dreams = []
    if user_tier >= 2:
        dreams = generate_symbolic_dreams(user_input)
    else:
        print("🛑 Dream generation restricted. Tier 2+ required.")

    print("💭 Symbolic Dreams:")
    for idx, dream in enumerate(dreams, 1):
        output = f"Outcome {idx}: {dream}"
        speak(output, emotion=emotion)

        if user_tier >= 4:
            visualize_dream_output(dream, emotion)

        if user_tier >= 3:
            log_memory("lukhas_dream", {
                "timestamp": timestamp,
                "input": user_input,
                "dream": dream,
                "emotion": emotion,
                "personality": personality_state,
                "context": last_context
            })

if __name__ == "__main__":
    print("🎙️ LUKHAS v1.0 — Symbolic Conscience Activated")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["quit", "exit"]:
                print("👋 Bye for now. Lukhas will remember this.")
                break
            process_user_input(user_input)
        except KeyboardInterrupt:
            print("\n👋 Session ended.")
            break
