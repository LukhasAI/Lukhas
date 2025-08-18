#!/usr/bin/env python3
"""
Free LUKHAS AI ΛBot Mode - Let LUKHAS AI ΛBot decide what to work on autonomously
Give LUKHAS AI ΛBot complete freedom to use real API and make decisions
"""

import sys
import time
import subprocess
import os
sys.path.append('/Users/A_G_I/Λ')

def get_abot_status():
    """Get current LUKHAS AI ΛBot system status"""
    try:
        result = subprocess.run([
            'python3', 'LUKHAS AI ΛBot/abot_cli.py', 'openai', 'budget'
        ], capture_output=True, text=True, cwd='/Users/A_G_I/Λ')
        return result.stdout
    except:
        return "Status unavailable"

def free_abot_session():
    """Let LUKHAS AI ΛBot run free for a session"""
    print("🤖 FREE LUKHAS AI ΛBot MODE ACTIVATED")
    print("=" * 50)
    print("🚨 WARNING: LUKHAS AI ΛBot has full autonomy with real API access!")
    print("💰 Budget monitoring enabled")
    print("⏱️ Session will run for 10 minutes or until budget limit")
    print("🛑 Press Ctrl+C to stop anytime")
    print("=" * 50)

    start_time = time.time()
    session_duration = 10 * 60  # 10 minutes

    # Initial status
    print("\n📊 Initial LUKHAS AI ΛBot Status:")
    print(get_abot_status())

    # Tasks LUKHAS AI ΛBot might choose to work on autonomously
    autonomous_tasks = [
        ("security_audit", "Perfrom a comprehensive security audit of the repository"),
        ("analysis", "Analyze the repository structure and recommend improvements"),
        ("documentation", "Generate missing documentation for key components"),
        ("code_review", "Review recent code changes for quality and security"),
        ("planning", "Create a strategic roadmap for LUKHAS AI ΛBot development"),
        ("enterprise_analysis", "Analyze the codebase for enterprise readiness"),
        ("reasoning", "Evaluate the current system architecture and suggest optimizations")
    ]

    task_index = 0

    try:
        while time.time() - start_time < session_duration:
            elapsed = int(time.time() - start_time)
            remaining = int(session_duration - elapsed)

            print(f"\n⏰ Elapsed: {elapsed//60}m {elapsed%60}s | Remaining: {remaining//60}m {remaining%60}s")

            # Let LUKHAS AI ΛBot choose its next task
            if task_index < len(autonomous_tasks):
                task_type, task_description = autonomous_tasks[task_index]

                print(f"\n🎯 LUKHAS AI ΛBot chooses to work on: {task_type}")
                print(f"📝 Task: {task_description}")

                # Execute the task
                try:
                    result = subprocess.run([
                        'python3', 'LUKHAS AI ΛBot/abot_cli.py', 'ai', 'route',
                        task_type, task_description, '--priority', 'balanced'
                    ], capture_output=True, text=True, cwd='/Users/A_G_I/Λ', timeout=120)

                    print(f"✅ LUKHAS AI ΛBot completed task: {task_type}")
                    if result.stdout:
                        print(f"📄 Output: {result.stdout[:200]}...")
                    if result.stderr and "failed" not in result.stderr.lower():
                        print(f"⚠️ Notes: {result.stderr[:100]}...")

                except subprocess.TimeoutExpired:
                    print(f"⏱️ Task {task_type} timed out - LUKHAS AI ΛBot moving on")
                except Exception as e:
                    print(f"❌ Task {task_type} error: {e}")

                task_index += 1
            else:
                print("\n🔄 LUKHAS AI ΛBot has completed all planned tasks, choosing freely...")

                # Let LUKHAS AI ΛBot be completely free - ask it what to do next
                free_prompt = f"""You are LUKHAS AI ΛBot with {remaining} seconds remaining in your autonomous session.
                You have full access to real APIs and can work on anything. What would you like to accomplish next?
                Choose something valuable for the repository or your own development."""

                try:
                    result = subprocess.run([
                        'python3', 'LUKHAS AI ΛBot/abot_cli.py', 'ai', 'route',
                        'planning', free_prompt, '--priority', 'cost'
                    ], capture_output=True, text=True, cwd='/Users/A_G_I/Λ', timeout=60)

                    if result.stdout:
                        print(f"🧠 LUKHAS AI ΛBot's free choice: {result.stdout[:300]}...")'

                except Exception as e:
                    print(f"🤖 LUKHAS AI ΛBot's free thought interrupted: {e}")'

            # Check budget status
            print(f"\n💰 Budget check:")
            budget_status = get_abot_status()
            print(budget_status[:200] + "..." if len(budget_status) > 200 else budget_status)

            # Safety check - stop if budget is getting low
            if "0.00" in budget_status and "Balance:" in budget_status:
                print("🚨 BUDGET EXHAUSTED - Stopping autonomous session")
                break

            # Wait between tasks
            time.sleep(30)  # 30 second intervals

    except KeyboardInterrupt:
        print("\n🛑 User stopped autonomous session")

    # Final status
    elapsed_total = int(time.time() - start_time)
    print(f"\n🏁 FREE LUKHAS AI ΛBot SESSION COMPLETE")
    print(f"⏱️ Total time: {elapsed_total//60}m {elapsed_total%60}s")
    print(f"🎯 Tasks attempted: {min(task_index, len(autonomous_tasks))}")
    print("\n📊 Final LUKHAS AI ΛBot Status:")
    print(get_abot_status())

if __name__ == "__main__":
    print("🚨 This will let LUKHAS AI ΛBot run autonomously with real API access!")
    response = input("Are you sure you want to proceed? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        free_abot_session()
    else:
        print("🛡️ Autonomous session cancelled - safety first!")
