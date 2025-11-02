"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: visualizer_core.py
Advanced: visualizer_core.py
Integration Date: 2025-05-31T07:55:28.267934
"""

#!/usr/bin/env python3
# 📄 MODULE: visualizer.py
# 🔎 PURPOSE: Convert flashbacks into visual prompts for OpenAI DALL·E or other generators
# 🛠️ VERSION: v1.0.0 • 📅 CREATED: 2025-04-30 • ✍️ AUTHOR: LUKHAS Cognitive AI
import json
import os

FLASHBACK_LOG_PATH = "logs/flashbacks/flashback_trace.jsonl"


def load_latest_flashback(path=FLASHBACK_LOG_PATH) -> dict:
    if not os.path.exists(path):
        print("❌ Flashback trace log not found.")
        return {}
    with open(path, encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    return lines[-1] if lines else {}


def build_visual_prompt(fb: dict) -> str:
    theme = fb.get("theme", "unknown dream")
    tag = fb.get("introspection_tag", "neutral")
    collapse_path = ", ".join(fb.get("collapsed_trace", []))
    score = fb.get("alignment_score", 0.5)

    return (
        f"A symbolic visualization of a dream with the theme '{theme}', "
        f"introspection state '{tag}', and symbolic collapse path nodes: {collapse_path}. "
        f"The emotional alignment is scored at {score}. The style should be surreal, "
        f"emotionally abstract, and dreamlike, reflecting introspective symbolism."
    )


if __name__ == "__main__":
    flashback = load_latest_flashback()
    if flashback:
        prompt = build_visual_prompt(flashback)
        print("\n🎨 Generated Prompt for Visual Synthesis:\n")
        print(prompt)
