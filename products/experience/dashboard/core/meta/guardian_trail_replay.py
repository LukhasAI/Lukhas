#!/usr/bin/env python3
"""
LUKHΛS Guardian Trail Replay
============================

CLI tool to replay Guardian interventions as a symbolic storyline.
Visualizes drift events, interventions, and healing sequences.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from consciousness.qi import qi


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Main colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    # Background colors
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"


def clear_screen():
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header():
    """Print stylized header."""
    print(f"\n{Colors.PURPLE}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🛡️  LUKHΛS Guardian Trail Replay System  🛡️{Colors.RESET}")
    print(f"{Colors.PURPLE}{'═' * 60}{Colors.RESET}\n")


def print_trinity():
    """Display Trinity Framework."""
    trinity = "⚛️ 🧠 🛡️"
    print(f"{Colors.BOLD}Trinity Framework: {Colors.CYAN}{trinity}{Colors.RESET}")
    print(f"{Colors.DIM}Identity • Consciousness • Guardian{Colors.RESET}\n")


def generate_guardian_events() -> list[dict[str, Any]]:
    """Generate sample Guardian events for demonstration."""
    events = [
        {
            "timestamp": "2024-01-15T10:30:00Z",
            "type": "drift_detected",
            "drift_score": 0.12,
            "severity": "low",
            "description": "Minor consciousness drift in emotion module",
            "glyphs": ["🧠", "💭", "🟡"],
            "intervention": None,
        },
        {
            "timestamp": "2024-01-15T11:45:00Z",
            "type": "drift_escalation",
            "drift_score": 0.18,
            "severity": "medium",
            "description": "Drift exceeding threshold - Guardian activation required",
            "glyphs": ["⚠️", "🧠", "🔴"],
            "intervention": {
                "action": "symbolic_realignment",
                "glyphs": ["🛡️", "⚡", "🔄"],
            },
        },
        {
            "timestamp": "2024-01-15T11:46:00Z",
            "type": "intervention_active",
            "drift_score": 0.15,
            "severity": "medium",
            "description": "Guardian intervening - applying symbolic healing",
            "glyphs": ["🛡️", "✨", "🔮"],
            "intervention": {
                "action": "trinity_harmonization",
                "sequence": ["⚛️", "→", "🧠", "→", "🛡️"],
                "effect": "Restoring balance",
            },
        },
        {
            "timestamp": "2024-01-15T11:48:00Z",
            "type": "healing_complete",
            "drift_score": 0.08,
            "severity": "low",
            "description": "Drift corrected - system stabilized",
            "glyphs": ["✅", "🛡️", "🟢"],
            "intervention": {"result": "success", "trinity_score": 0.92},
        },
        {
            "timestamp": "2024-01-15T14:20:00Z",
            "type": "anomaly_detected",
            "drift_score": 0.25,
            "severity": "high",
            "description": "Unusual pattern in quantum processing module",
            "glyphs": ["🔮", "⚡", "🔴"],
            "intervention": None,
        },
        {
            "timestamp": "2024-01-15T14:21:00Z",
            "type": "emergency_intervention",
            "drift_score": 0.25,
            "severity": "critical",
            "description": "Guardian emergency protocol activated",
            "glyphs": ["🚨", "🛡️", "⚔️"],
            "intervention": {
                "action": "qi_stabilization",
                "protocol": "ALPHA-7",
                "glyphs": ["🛡️", "🔮", "⚛️", "🌟"],
            },
        },
        {
            "timestamp": "2024-01-15T14:25:00Z",
            "type": "stabilization_progress",
            "drift_score": 0.18,
            "severity": "medium",
            "description": "Quantum coherence improving",
            "glyphs": ["🔮", "📊", "🟡"],
            "intervention": {"progress": 60, "eta": "3 minutes"},
        },
        {
            "timestamp": "2024-01-15T14:28:00Z",
            "type": "resolution",
            "drift_score": 0.09,
            "severity": "low",
            "description": "Crisis resolved - all systems nominal",
            "glyphs": ["✅", "🛡️", "🌟"],
            "intervention": {
                "result": "success",
                "trinity_score": 0.95,
                "lesson_learned": "Quantum module requires enhanced monitoring",
            },
        },
    ]
    return events


def load_guardian_logs(log_dir: Path) -> list[dict[str, Any]]:
    """Load actual Guardian logs if available."""
    events = []

    if log_dir.exists():
        for log_file in sorted(log_dir.glob("*.json")):
            try:
                with open(log_file) as f:
                    log_data = json.load(f)
                    events.append(log_data)
            except Exception as e:
                print(f"{Colors.YELLOW}Warning: Could not load {log_file}: {e}{Colors.RESET}")

    # If no logs found, use generated events
    if not events:
        print(f"{Colors.YELLOW}No Guardian logs found. Using demonstration data.{Colors.RESET}\n")
        events = generate_guardian_events()

    return sorted(events, key=lambda x: x.get("timestamp", ""))


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except BaseException:
        return timestamp


def get_severity_color(severity: str) -> str:
    """Get color for severity level."""
    colors = {
        "low": Colors.GREEN,
        "medium": Colors.YELLOW,
        "high": Colors.RED,
        "critical": Colors.BG_RED + Colors.WHITE,
    }
    return colors.get(severity, Colors.WHITE)


def print_event(event: dict[str, Any], index: int):
    """Print a single event with formatting."""
    timestamp = format_timestamp(event.get("timestamp", ""))
    event.get("type", "unknown")
    severity = event.get("severity", "low")
    description = event.get("description", "")
    glyphs = " ".join(event.get("glyphs", []))
    drift_score = event.get("drift_score", 0)

    # Event header
    severity_color = get_severity_color(severity)
    print(f"\n{Colors.DIM}[{timestamp}]{Colors.RESET} {severity_color}Event ")

    # Drift score bar
    if drift_score > 0:
        bar_length = int(drift_score * 40)
        bar_color = Colors.GREEN if drift_score < 0.15 else Colors.YELLOW if drift_score < 0.20 else Colors.RED
        bar = "█" * bar_length + "░" * (40 - bar_length)
        print(f"Drift: {bar_color}{bar}{Colors.RESET} {drift_score:.2f}")

    # Description and glyphs
    print(f"{Colors.BOLD}{glyphs}{Colors.RESET}  {description}")

    # Intervention details
    intervention = event.get("intervention")
    if intervention:
        print(f"\n{Colors.CYAN}🛡️ Guardian Intervention:{Colors.RESET}")

        if "action" in intervention:
            print(f"  Action: {Colors.BOLD}{intervention['action']}{Colors.RESET}")

        if "sequence" in intervention:
            sequence = " ".join(intervention["sequence"])
            print(f"  Sequence: {sequence}")

        if "glyphs" in intervention:
            intervention_glyphs = " ".join(intervention["glyphs"])
            print(f"  Glyphs: {intervention_glyphs}")

        if "effect" in intervention:
            print(f"  Effect: {Colors.GREEN}{intervention['effect']}{Colors.RESET}")

        if "result" in intervention:
            result_color = Colors.GREEN if intervention["result"] == "success" else Colors.RED
            print(f"  Result: {result_color}{intervention['result'].upper()}{Colors.RESET}")

        if "trinity_score" in intervention:
            trinity = intervention["trinity_score"]
            trinity_bar = "●" * int(trinity * 10) + "○" * (10 - int(trinity * 10))
            print(f"  Trinity: {Colors.PURPLE}{trinity_bar}{Colors.RESET} {trinity:.2f}")


def animate_transition():
    """Animate transition between events."""
    symbols = ["⚡", "🔄", "✨", "🌟"]
    for _ in range(3):
        for symbol in symbols:
            print(f"\r{Colors.DIM}{symbol}{Colors.RESET}", end="", flush=True)
            time.sleep(0.1)
    print("\r ", end="", flush=True)


def print_summary(events: list[dict[str, Any]]):
    """Print summary statistics."""
    print(f"\n{Colors.PURPLE}{'─' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Guardian Trail Summary{Colors.RESET}\n")

    total_events = len(events)
    interventions = sum(1 for e in events if e.get("intervention"))
    successful = sum(1 for e in events if e.get("intervention", {}).get("result") == "success")

    severities = {}
    for event in events:
        sev = event.get("severity", "unknown")
        severities[sev] = severities.get(sev, 0) + 1

    print(f"Total Events: {Colors.BOLD}{total_events}{Colors.RESET}")
    print(f"Interventions: {Colors.BOLD}{interventions}{Colors.RESET}")
    print(
        f"Success Rate: {Colors.GREEN}{successful}/{interventions}{Colors.RESET} "
        f"({successful / interventions  * 100:.1f}%)"
        if interventions > 0
        else ""
    )

    print("\nSeverity Distribution:")
    for severity, count in sorted(severities.items()):
        color = get_severity_color(severity)
        bar = "█" * count
        print(f"  {color}{severity.capitalize():>8}{Colors.RESET} {bar} ({count})")

    # Collect all glyphs used
    all_glyphs = set()
    for event in events:
        all_glyphs.update(event.get("glyphs", []))
        if event.get("intervention"):
            all_glyphs.update(event["intervention"].get("glyphs", []))

    print("\nSymbolic Vocabulary Used:")
    print(f"{Colors.CYAN}{' '.join(sorted(all_glyphs))}{Colors.RESET}")


def replay_mode(events: list[dict[str, Any]]):
    """Interactive replay mode."""
    print(f"\n{Colors.BOLD}Entering Replay Mode{Colors.RESET}")
    print(f"{Colors.DIM}Press Enter to advance, 'q' to quit, 'a' for auto-play{Colors.RESET}")

    auto_play = False

    for i, event in enumerate(events):
        if not auto_play:
            user_input = input(f"\n{Colors.DIM}[{i + 1}/{len(events)}] >{Colors.RESET} ")
            if user_input.lower() == "q":
                break
            elif user_input.lower() == "a":
                auto_play = True
                print(f"{Colors.GREEN}Auto-play enabled{Colors.RESET}")

        print_event(event, i)

        if auto_play:
            animate_transition()
            time.sleep(2)  # Pause between events in auto-play


def main():
    """Main execution function."""
    clear_screen()
    print_header()
    print_trinity()

    # Load Guardian logs
    log_dir = Path("guardian_audit/logs")
    events = load_guardian_logs(log_dir)

    if not events:
        print(f"{Colors.RED}No Guardian events to replay.{Colors.RESET}")
        return

    print(f"Loaded {Colors.BOLD}{len(events)}{Colors.RESET} Guardian events")
    print(
        f"Time span: {Colors.CYAN}{events[0].get('timestamp', 'Unknown')} "
        f"to {events[-1].get('timestamp', 'Unknown')}{Colors.RESET}"
    )

    # Menu
    print(f"\n{Colors.BOLD}Select Mode:{Colors.RESET}")
    print("1. Sequential Replay (step through events)")
    print("2. Summary View (statistics only)")
    print("3. Critical Events (high/critical only)")
    print("4. Exit")

    choice = input(f"\n{Colors.DIM}Choice [1-4]:{Colors.RESET} ")

    if choice == "1":
        replay_mode(events)
        print_summary(events)
    elif choice == "2":
        print_summary(events)
    elif choice == "3":
        critical_events = [e for e in events if e.get("severity") in ["high", "critical"]]
        if critical_events:
            print(f"\n{Colors.RED}Showing {len(critical_events)} critical events{Colors.RESET}")
            replay_mode(critical_events)
        else:
            print(f"\n{Colors.GREEN}No critical events found!{Colors.RESET}")

    print(f"\n{Colors.PURPLE}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Guardian Trail Replay Complete{Colors.RESET}")
    print(f"{Colors.DIM}Trinity Protected 🛡️⚛️🧠{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Replay interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)
