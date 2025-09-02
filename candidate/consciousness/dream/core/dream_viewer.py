"""
dream_viewer.py
----------------
Reads and displays symbolic dream logs from data/dream_log.jsonl.
"""

import json
import os

DREAM_LOG_PATH = "data/dream_log.jsonl"


def load_dreams():
    if not os.path.exists(DREAM_LOG_PATH):
        print("⚠️ No dream log found.")
        return []

    with open(DREAM_LOG_PATH) as file:
        lines = file.readlines()
        return [json.loads(line.strip()) for line in lines]


def display_dreams(dreams):
    if not dreams:
        print("🌙 No dreams to display.")
        return

    print(f"\n🌌 LUKHAS DREAM LOG ({len(dreams)} dreams total)\n")
    for _i, dream in enumerate(dreams[-10:], 1):  # Show last 10 dreams
        print(f"🔹 [{dream['timestamp']}] (Resonance: {dream['resonance']:.2f}) {dream['symbol']}")
        print(f"    💤 Dream: {dream['dream_text']}")
        print(f"    📜 Meaning: {dream['interpretation']}")
        print(f"    🧬 Suggestion: {dream['mutation_suggestion']}\n")


if __name__ == "__main__":
    dreams = load_dreams()
    display_dreams(dreams)

    # Functional script to view and interact with the dream log
    while True:
        action = input("Enter 'view' to display dreams, or 'exit' to quit: ").strip().lower()
        if action == "view":
            display_dreams(dreams)
        elif action == "exit":
            print("Exiting the dream viewer.")
            break
        else:
            print("Invalid input. Please enter 'view' or 'exit'.")
