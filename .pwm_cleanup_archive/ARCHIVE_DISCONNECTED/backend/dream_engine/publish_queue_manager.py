# ╭──────────────────────────────────────────────────────────────────────────────╮
# │                             LUClukhasS :: CONTROL PANEL                          │
# │                              Module: lucasctl.py                           │
# │                              Author: Gonzo R.D.M | Version: v2.1             │
# ╰──────────────────────────────────────────────────────────────────────────────╯
#
# 📜 Description:
#    This module provides the CLI interface for Lukhas AI assistant,
#    handling user commands and symbolic inputs.
#
# 🔗 Related Modules:
#    - publish_queue_manager.py (queue management)
#    - voice_narrator.py (voice output)
#    - dream_recorder.py (dream logging)
#
# 🧠 Symbolic CLI Input Handler: Extended to include publishing queue trigger.

import os


def main_menu():
    menu_options = """
    1. 📝 Record a Dream
    2. 🎙 Narrate Dreams
    3. 🔍 Search Dreams
    4. 📚 Review Dream Logs
    5. ⚙ Settings
    6. 🧠 Analyze Dreams
    7. 🛠 Maintenance
    8. 🗑 Clear Queues
    9. 📡 Sync Data
    10. 📤 Queue Dreams for Publishing
    11. 🌐 Generate HTML Post (Symbolic)
    12. 🌀 Narrate + Visualize + HTML Export (from publish queue)
    0. 🚪 Exit
    """
    print(menu_options)


def symbolic_cli_handler():
    while True:
        choice = input("Choose an option (1–12): ").strip()
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            os.system("python3 core/dream_recorder.py")
        elif choice == "2":
            os.system("python3 core/voice_narrator.py")
        elif choice == "3":
            os.system("python3 core/dream_search.py")
        elif choice == "4":
            os.system("cat core/logs/dream_log.jsonl")
        elif choice == "5":
            os.system("python3 core/settings.py")
        elif choice == "6":
            os.system("python3 core/dream_analyzer.py")
        elif choice == "7":
            os.system("python3 core/maintenance.py")
        elif choice == "8":
            os.system("python3 core/queue_clear.py")
        elif choice == "9":
            os.system("python3 core/sync_data.py")
        elif choice == "10":
            os.system("python3 aid/dream_engine/publish_queue_manager.py")
        elif choice == "11":
            os.system("python3 tools/generate_html_post.py")
        elif choice == "12":
            # Use the publish_queue_manager to handle narration, visualization, and export
            try:
                import aid.dream_engine.publish_queue_manager as pqm

                pqm.handle_publish_queue()
            except Exception as e:
                print(f"⚠️ Failed to process publish queue: {e}")
        else:
            print("❓ Invalid choice. Please try again.")


if __name__ == "__main__":
    symbolic_cli_handler()
