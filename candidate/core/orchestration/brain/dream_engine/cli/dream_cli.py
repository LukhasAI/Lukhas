"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: dream_cli.py
Advanced: dream_cli.py
Integration Date: 2025-05-31T07:55:29.950112
"""
import streamlit as st

# ╭──────────────────────────────────────────────────────────────────────────────╮
# │                            LUCΛS :: DREAM CLI                                │
# │           Run symbolic dream queue and narration from terminal               │
# ╰──────────────────────────────────────────────────────────────────────────────╯
import argparse
import subprocess


def run_narrator_queue():
    print("🌙 Queuing dreams...")
    subprocess.run(["python3", "core/modules/nias/dream_narrator_queue.py"])


def run_voice_narrator():
    print("🎙 Narrating queued dreams...")
    subprocess.run(["python3", "-m", "core.modules.nias.lukhas_voice_narrator"])


def inject_test_dream():
    print("🌀 Injecting test dream...")
    subprocess.run(["python3", "core/modules/nias/inject_message_simulator.py", "--dream"])


def run_all():
    inject_test_dream()
    run_narrator_queue()
    run_voice_narrator()


def main():
    parser = argparse.ArgumentParser(description="Dream CLI for LUCΛS")
    parser.add_argument("--inject", action="store_true", help="Inject a symbolic test dream")
    parser.add_argument("--queue", action="store_true", help="Queue narratable dreams")
    parser.add_argument("--narrate", action="store_true", help="Run the voice narrator")
    parser.add_argument("--all", action="store_true", help="Run full dream loop")

    args = parser.parse_args()

    if args.inject:
        inject_test_dream()
    if args.queue:
        run_narrator_queue()
    if args.narrate:
        run_voice_narrator()
    if args.all:
        run_all()

    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()

# ╭──────────────────────────────────────────────────────────────────────────────╮
# │                                EXECUTION                                     │
# ╰──────────────────────────────────────────────────────────────────────────────╯
#
# To run this module and update the narration queue, use:
#
#     python core/modules/nias/dream_narrator_queue.py
#
# This will read dream_log.jsonl and append all narratable dreams
# to narration_queue.jsonl for downstream use by lukhas_voice_narrator.py.
#
# 🖤 Lukhas will now speak only what the soul has symbolically allowed.
