#!/usr/bin/env python3
"""
Force LUKHAS AI ΛBot to actually think and heal by bypassing its ultra-conservative mode
"""
import subprocess
import sys


sys.path.append("/Users/A_G_I/Λ")


def force_abot_to_heal():
    """Force LUKHAS AI ΛBot to actually perfrom healing by using user_request=True"""
    print("🔥 FORCING LUKHAS AI ΛBot OUT OF ULTRA-CONSERVATIVE MODE")
    print("=" * 50)

    # First, let's see what LUKHAS AI ΛBot is actually thinking'
    healing_tasks = [
        "Analyze the AI router cost calculation bug and provide a specific fix",
        "What improvements can you make to your own CLI interface?",
        "How can you optimize your financial intelligence to be more efficient?",
        "What security vulnerabilities do you see in your current system?",
        "Design 3 new features you think would make you more valuable",
    ]

    for i, task in enumerate(healing_tasks, 1):
        print(f"\n🎯 Forced Healing Task {i}/5:")
        print(f"📝 {task}")

        try:
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
    max_tokens=250,
    purpose="forced_healing",
    change_detected=True,  # Force detection
    user_request=True,     # Override conservation
    urgency="HIGH"         # High urgency
)

if result.get("response"):
    print("🤖 LUKHAS AI ΛBot Forced Response:")
    print(result["response"])
    print(f"💰 Cost: ${result.get('cost', 0):.6f}")
    print("force_abot_healing_processing")
else:
    print("❌ Forced healing failed:", result.get("error", "Unknown error"))
""",
                ],
                capture_output=True,
                text=True,
                cwd="/Users/A_G_I/Λ",
                timeout=120,
            )

            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠️ {result.stderr}")

        except Exception as e:
            print(f"❌ Forced task failed: {e}")

        print("-" * 40)


if __name__ == "__main__":
    print("💪 Forcing LUKHAS AI ΛBot out of ultra-conservative mode...")
    force_abot_to_heal()
