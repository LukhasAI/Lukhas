"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: main.py
Advanced: main.py
Integration Date: 2025-05-31T07:55:27.735633
"""
from __future__ import annotations


# ╔════════════════════════════════════════════════════════════╗
# ║ 🌿 LUKHAS Cognitive AI MAIN INTERFACE - symbolic_brainstem v1.0      ║
# ║ 🧠 CLI | GUI | SOCKET | VOICE | DAO-SAFE ENTRY             ║
# ║ 📦 Designed by LUKHAS Systems • Inspired by Sam + Steve     ║
# ╚════════════════════════════════════════════════════════════╝

import argparse
import os
import platform
import subprocess
from datetime import datetime

import pyfiglet

from core.interfaces.voice.edge_voice import speak

LOG_PATH = "core/logging/symbolic_output_log.jsonl"


def log_event(timezone, source, event, tier="sys"):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "source": source,
        "tier": tier,
    }
    with open(LOG_PATH, "a") as f:
        f.write(str(entry) + "\n")


def symbolic_intro():
    cmd = ["clear"] if platform.system() != "Windows" else ["cls"]
    subprocess.run(cmd, shell=(platform.system() == "Windows"), check=False)
    print(pyfiglet.figlet_format("LUKHAS Cognitive AI", font="slant"))
    print("🌱 Welcome back. Lukhas is awake.\n")
    try:
        import asyncio

        asyncio.run(speak("Lukhas is now awake. Symbolic interface is ready."))
    except Exception as e:
        print(f"⚠️ Voice startup failed: {e}")


def symbolic_menu():
    print(
        """
1. 🌐 GUI Dashboard
2. 💻 Symbolic CLI
3. 🌀 Socket Listener
4. 🔁 Narrate Last Dream
5. ❌ Exit
"""
    )


def launch_gui():
    log_event("main", "launch_gui")
    os.system("python3 core/interface/gui_launcher.py")


def launch_cli():
    log_event("main", "launch_cli")
    os.system("python3 core/interface/lukhasctl.py")


def launch_socket():
    log_event("main", "launch_socket")
    os.system("python3 core/interface/lukhas_socket.py")


def launch_narration():
    log_event("main", "narrate_last_dream")
    os.system("python3 tools/html_social_generator.py")


def main():
    parser = argparse.ArgumentParser(description="Symbolic Cognitive AI entry hub.")
    parser.add_argument("--gui", action="store_true", help="Launch GUI dashboard")
    parser.add_argument("--cli", action="store_true", help="Launch symbolic CLI")
    parser.add_argument("--socket", action="store_true", help="Start symbolic socket listener")
    parser.add_argument("--narrate", action="store_true", help="Narrate last symbolic post")

    args = parser.parse_args()

    if args.gui:
        launch_gui()
        return
    if args.cli:
        launch_cli()
        return
    if args.socket:
        launch_socket()
        return
    if args.narrate:
        launch_narration()
        return

    symbolic_intro()
    while True:
        symbolic_menu()
        choice = input("Select an interface ➤ ").strip().lower()

        if choice in ["1", "g", "gui"]:
            launch_gui()
        elif choice in ["2", "c", "cli"]:
            launch_cli()
        elif choice in ["3", "s", "socket"]:
            launch_socket()
        elif choice in ["4", "n", "narrate"]:
            launch_narration()
        elif choice in ["5", "q", "x", "exit"]:
            log_event("main", "exit_system")
            print("🌙 Exiting Lukhas. Your symbolic trace ends here.")
            break
        else:
            print("⚠️ Unknown option. Try 1–5 or type q to quit.")


if __name__ == "__main__":
    main()