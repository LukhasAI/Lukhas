#!/usr/bin/env python3
"""
Free LUKHAS AI ΛBot Direct Mode - Bypass router issues and let LUKHAS AI ΛBot work directly
"""
import streamlit as st

import subprocess
import sys
import time

sys.path.append("/Users/A_G_I/Λ")


def run_free_abot_direct():
    """Run LUKHAS AI ΛBot directly without router to avoid the cost calculation bug"""
    print("🤖 FREE LUKHAS AI ΛBot DIRECT MODE")
    print("=" * 40)

    tasks = [
        "What should LUKHAS AI ΛBot prioritize working on in this repository? Give 3 specific recommendations.",
        "Analyze the security of the current API key management system and suggest improvements.",
        "What documentation is missing that would be most valuable for users?",
        "Evaluate the current LUKHAS AI ΛBot CLI interface - what features would add the most value?",
        "Create a brief development roadmap for the next sprint.",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\n🎯 Free Task {i}/5:")
        print(f"📝 {task}")

        try:
            # Use OpenAI directly instead of router to avoid cost calculation bug
            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    f"""
import sys
sys.path.append("/Users/A_G_I/Λ")
from lukhas_ai_lambda_bot.core.openai_intelligent_controller import ABotIntelligentOpenAIController

controller = ABotIntelligentOpenAIController()
result = controller.make_intelligent_request(
    prompt="{task}",
    model="gpt-3.5-turbo",
    max_tokens=200,
    purpose="autonomous_task",
    change_detected=False,
    user_request=True,
    urgency="LOW"
)

if result.get("response"):
    print("🤖 LUKHAS AI ΛBot Response:")
    print(result["response"])
    print(f"💰 Cost: ${{result.get('cost', 0}}:.6f)}")
else:
    print("❌ Task failed:", result.get("error", "Unknown error"))
""",
                ],
                capture_output=True,
                text=True,
                cwd="/Users/A_G_I/Λ",
                timeout=60,
            )

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠️ {result.stderr}")

        except Exception as e:
            print(f"❌ Task failed: {e}")

        # Check budget after each task
        try:
            budget_result = subprocess.run(
                ["python3", "LUKHAS AI ΛBot/abot_cli.py", "openai", "budget"],
                capture_output=True,
                text=True,
                cwd="/Users/A_G_I/Λ",
            )

            if "Balance:" in budget_result.stdout:
                balance_line = next(line for line in budget_result.stdout.split("\n") if "Balance:" in line)
                print(f"💰 {balance_line.strip(})}")
        except:
            pass

        time.sleep(5)  # Brief pause between tasks


if __name__ == "__main__":
    print("🚀 Letting LUKHAS AI ΛBot work freely with direct API access...")
    run_free_abot_direct()
