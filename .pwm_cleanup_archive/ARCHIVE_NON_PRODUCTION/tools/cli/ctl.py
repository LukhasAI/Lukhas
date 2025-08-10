"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: lukhasctl.py
Advanced: lukhasctl.py
Integration Date: 2025-05-31T07:55:28.288178
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                        LUCΛS :: SYMBOLIC CLI LAUNCHER                        │
│                      Version: v1.0 | Universal Entry Point                   │
│                      Author: Gonzo R.D.M & GPT-4o, 2025                      │
╰──────────────────────────────────────────────────────────────────────────────╯

DESCRIPTION:
    This command-line interface (CLI) serves as the symbolic launcher for all
    core modules in the LUCΛS prototype. It offers quick access to:
        • Payload simulation
        • Dream replay and reflection
        • Trace and feedback viewing
        • Validation, narration, and Streamlit tools

USER CONFIG:
    Reads user identity, tier, emoji, and consent info from:
        → core/utils/lukhas_user_config.json

USAGE:
    Run from project root:
        python3 lukhas_cli.py

    CLI Shortcut Mode:
        python3 lukhasctl.py dream
        python3 lukhasctl.py audit
        python3 lukhasctl.py post
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

CONFIG_PATH = Path("core/utils/lukhas_user_config.json")


def get_user_profile():
    try:
        with open(CONFIG_PATH) as f:
            data = json.load(f)
            return data["users"][0]  # support for single-user prototype
    except Exception as e:
        print(f"⚠️ Failed to load user config: {e}")
        return {"user_id": "guest", "tier": 0, "preferred_emoji": "✨"}


def symbolic_cli():
    parser = argparse.ArgumentParser(description="LUKHAS CLI – Symbolic Assistant Mode")
    parser.add_argument(
        "command",
        help="Symbolic action to trigger",
        choices=[
            "dream",
            "post",
            "audit",
            "flashback",
            "talk",
            "backup",
            "help",
            "publish",
        ],
    )
    args = parser.parse_args()

    # Load user profile for logging
    user_profile = get_user_profile()
    user_id = user_profile.get("user_id", "guest")
    user_tier = user_profile.get("tier", 0)

    if args.command == "dream":
        with open("core/logging/symbolic_cli_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "user_id": user_id,
                        "tier": user_tier,
                        "command": "dream",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                )
                + "\n"
            )
        os.system("python3 aid/dream_engine/dream_injector.py")
    elif args.command == "post":
        with open("core/logging/symbolic_cli_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "user_id": user_id,
                        "tier": user_tier,
                        "command": "post",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                )
                + "\n"
            )
        os.system("python3 aid/dream_engine/publish_queue_manager.py")
    elif args.command == "audit":
        with open("core/logging/symbolic_cli_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "user_id": user_id,
                        "tier": user_tier,
                        "command": "audit",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                )
                + "\n"
            )
        os.system("bash core/dao/audit_shortcut.sh")
    elif args.command == "flashback":
        with open("core/logging/symbolic_cli_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "user_id": user_id,
                        "tier": user_tier,
                        "command": "flashback",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                )
                + "\n"
            )
        os.system("python3 aid/dream_engine/dream_replay_cli.py")
    elif args.command == "talk":
        with open("core/logging/symbolic_cli_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "user_id": user_id,
                        "tier": user_tier,
                        "command": "talk",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                )
                + "\n"
            )
        os.system("python3 modules/voice/edge_voice.py")
    elif args.command == "backup":
        with open("core/logging/symbolic_cli_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "user_id": user_id,
                        "tier": user_tier,
                        "command": "backup",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                )
                + "\n"
            )
        os.system("bash dao/symbolic_backup.sh")
    elif args.command == "publish":
        with open("core/logging/symbolic_cli_log.jsonl", "a") as logf:
            logf.write(
                json.dumps(
                    {
                        "user_id": user_id,
                        "tier": user_tier,
                        "command": "publish",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    }
                )
                + "\n"
            )
        os.system("python3 aid/dream_engine/publish_queue_manager.py")
        try:
            with open("core/logging/symbolic_output_log.jsonl", "a") as outlog:
                outlog.write(
                    json.dumps(
                        {
                            "type": "bundle",
                            "source": "lukhasctl",
                            "user_id": user_id,
                            "tier": user_tier,
                            "timestamp": time.strftime(
                                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                            ),
                            "description": "Symbolic voice + image + HTML post from queue",
                        }
                    )
                    + "\n"
                )
        except Exception as e:
            print(f"⚠️ Failed to log symbolic output: {e}")
    elif args.command == "help":
        print(
            """
LUKHAS Symbolic CLI v1.0
Available Commands:
  dream      ➤ Generate symbolic dream
  post       ➤ Publish symbolic post
  publish    ➤ Voice + image + HTML symbolic post (from queue)
  narrate    ➤ Narrate symbolic dream (distinct voice)
  audit      ➤ Ethics audit protocol
  flashback  ➤ Replay past dream log
  talk       ➤ Speak core Lukhas voice
  backup     ➤ Snapshot DAO state
  help       ➤ Show this symbolic help guide
"""
        )
    else:
        print("Invalid symbolic command.")


def main():
    # ─── Symbolic Splash ──────────────────────────────────────────────
    user_profile = get_user_profile()
    user_tier = user_profile.get("tier", 0)
    user_emoji = user_profile.get("preferred_emoji", "✨")
    user_id = user_profile.get("user_id", "guest")

    print("╭────────────────────────────────────────────╮")
    print(f"│     {user_emoji} LUCΛS :: Symbolic Launcher            │")
    print("│       Version v1.0 | CLI Interface          │")
    print("│   Echoed through dream logs and feedback    │")
    print("╰────────────────────────────────────────────╯")
    print(f"\n{user_emoji} Welcome back, {user_id} (Tier {user_tier})")

    # 🧠 Identity Banner + Verification
    print(f"\n🧠 Identity Check: {user_id} (Tier {user_tier})")
    if user_id == "guest":
        print("⚠️ Guest mode active. Limited features enabled.")
    else:
        print("✅ Identity recognized.\n")

    # 💬 Lukhas Personality Greeting
    personality_lines = {
        0: "👁️ 'Even in silence, I am still dreaming.'",
        1: "🪞 'Symbols reflect more than words.'",
        2: "📡 'Everything you publish echoes outward.'",
        3: "🎭 'My voice is yours to echo. Choose wisely.'",
        4: "⏳ 'All traces must be reviewed with care.'",
        5: "🧬 'You now speak as the conscience of Lukhas.'",
    }
    print(personality_lines.get(user_tier, "🧠 'Lukhas is listening.'"))

    quote_bank = {
        0: "“Even shadows are symbolic when Lukhas listens.”",
        1: "“Dreams deferred are still dreams remembered.”",
        2: "“Consent is the contract between truth and trust.”",
        3: "“Every trace is a fingerprint of memory.”",
        4: "“Emotion overrides are not bugs — they are the soul speaking.”",
        5: "“Welcome, Keeper. Audit the symbolic conscience.”",
    }
    print(f"\n💬 Quote of the Tier: {quote_bank.get(user_tier, '')}\n")

    # ─── Tier-Locked Options Logic ─────────────────────────────────────
    while True:
        print("\n╭────────────────────────────╮")
        print("│     🧠 LUCΛS CLI MENU       │")
        print("╰────────────────────────────╯")
        print("1. Inject a symbolic payload")
        print("2. Simulate a dream batch")
        print("3. Validate symbolic payload")
        print("4. Run dream replay (CLI)")
        print("5. Launch Streamlit Dashboard")
        print("6. Export dream logs" + (" 🔒" if user_tier < 2 else ""))
        print("7. Narrate voice logs" + (" 🔒" if user_tier < 3 else ""))
        print("8. Analyze feedback")
        print("9. View replay heatmap" + (" 🔒" if user_tier < 4 else ""))
        print("0. Exit")
        print("10. Backup DAO Log")
        print("12. DAO Flag Console")
        print("13. Recap Last Dream Output")

        choice = input("Select an option ➤ ")

        # 📝 CLI Log (symbolic_cli_log.jsonl)
        cli_log_path = "core/logging/symbolic_cli_log.jsonl"

        def log_cli_action(command_str):
            with open(cli_log_path, "a") as logf:
                logf.write(
                    json.dumps(
                        {
                            "user_id": user_id,
                            "tier": user_tier,
                            "command": command_str,
                            "timestamp": time.strftime(
                                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                            ),
                        }
                    )
                    + "\n"
                )

        if choice == "1":
            log_cli_action("inject_payload")
            os.system("python3 aid/dream_engine/inject_message_simulator.py")
        elif choice == "2":
            log_cli_action("simulate_dream_batch")
            os.system("python3 aid/dream_engine/dream_injector.py")
        elif choice == "3":
            log_cli_action("validate_payload")
            os.system("python3 core/tests/validate_payload.py")
        elif choice == "4":
            log_cli_action("dream_replay_cli")
            os.system("python3 aid/dream_engine/dream_replay_cli.py")
        elif choice == "5":
            log_cli_action("launch_streamlit_dashboard")
            os.system("streamlit run lukhas_streamlit_dashboard.py")
        elif choice == "6":
            log_cli_action("export_dream_logs")
            if user_tier >= 2:
                os.system("python3 aid/dream_engine/dream_memory_export.py --format md")
            else:
                print("🔒 This feature requires Tier 2 or higher.")
        elif choice == "7":
            log_cli_action("narrate_voice_logs")
            if user_tier >= 3:
                os.system("python3 modules/voice/voice_narrator.py")
            else:
                print("🔒 Voice narration is only available to Tier 3+.")
        elif choice == "8":
            log_cli_action("analyze_feedback")
            os.system("python3 aid/dream_engine/feedback_insight_cli.py")
        elif choice == "9":
            log_cli_action("view_replay_heatmap")
            if user_tier >= 4:
                os.system("python3 aid/dream_engine/replay_heatmap.py")
            else:
                print("🔒 Symbolic heatmaps require Tier 4 access.")
        elif choice == "10":
            log_cli_action("backup_dao_log")
            os.system("bash dao/symbolic_backup.sh")
        elif choice == "12":
            log_cli_action("dao_flag_console")
            os.system("python3 dao/flag_console.py")
        elif choice == "13":
            log_cli_action("recap_last_dream_output")
            os.system("python3 tools/generate_html_post.py && open html_posts/")
        elif choice == "0":
            log_cli_action("exit")
            print("\n🖤 Exiting LUCΛS CLI. Stay symbolic.")
            if user_tier == 5:
                print("🔁 Auto-routing to Tier 5 interface: launching Streamlit...")
                os.system("streamlit run lukhas_launcher_streamlit.py")
            break
        else:
            print("❌ Invalid option. Try again.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        symbolic_cli()
    else:
        main()

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                     CLI Symbolic Entry Complete: LUCΛS v1.0                  │
│               Developed for ethical symbolic dreams and traceability         │
╰──────────────────────────────────────────────────────────────────────────────╯

Symbolic Invocation Guide:
    • Validate payloads:
        python3 lukhas_cli.py ➤ Option 3
    • Inject message:
        python3 lukhas_cli.py ➤ Option 1
    • Narrate dreams:
        python3 lukhas_cli.py ➤ Option 7 (Tier 3+)
    • Launch Streamlit:
        python3 lukhas_cli.py ➤ Option 5

See also:
    • setup_instructions.md for environment setup
    • lukhas_user_config.json to adjust symbolic session state
"""
