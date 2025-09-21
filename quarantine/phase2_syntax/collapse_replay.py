#!/usr/bin/env python3
"""
LUKHΛS Phase 6 - Collapse Replay CLI Tool
Recreates symbolic cognition flows for validation.

Usage:
    python3 collapse_replay.py --session <id> --simulate
    python3 collapse_replay.py --session <id> --summary
    python3 collapse_replay.py --list-sessions
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

from lukhas.qi.core.wavefunction_manager import WavefunctionManager

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


class CollapseReplayTool:
    """CLI tool for replaying quantum consciousness collapse sequences"""

    def __init__(self, journal_path: str = "qi_core/drift_journal.json"):
        self.journal_path = Path(journal_path)
        self.journal_data = self._load_journal()

    def _load_journal(self) -> dict:
        """Load drift journal data"""
        if not self.journal_path.exists():
            print(f"❌ Error: Drift journal not found at {self.journal_path}")
            sys.exit(1)

        try:
            with open(self.journal_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading drift journal: {e}")
            sys.exit(1)

    def list_sessions(self) -> None:
        """List all available sessions"""
        print("🌌 LUKHΛS Quantum Sessions")
        print("=" * 60)
        print(f"{'Session ID':<20} {'Start Time':<20} {'Branch':<15} {'Glyphs'}")
        print("-" * 60)

        for session in self.journal_data.get("sessions", []):
            session_id = session["session_id"]
            start_time = session["start_time"][:19]  # Trim to seconds
            branch = session["dream_branch"]
            glyphs = " ".join(session["collapsed_glyphs"][:3])
            if len(session["collapsed_glyphs"]) > 3:
                glyphs += f" ... ({len(session['collapsed_glyphs'])} total)"

            print(f"{session_id:<20} {start_time:<20} {branch:<15} {glyphs}")

        print("\n" + "=" * 60)
        print(f"Total sessions: {len(self.journal_data.get('sessions', []))}")

    def get_session(self, session_id: str) -> Optional[dict]:
        """Get a specific session by ID"""
        for session in self.journal_data.get("sessions", []):
            if session["session_id"] == session_id:
                return session
        return None

    def show_summary(self, session_id: str) -> None:
        """Show summary of a session"""
        session = self.get_session(session_id)
        if not session:
            print(f"❌ Error: Session '{session_id}' not found")
            sys.exit(1)

        print("🔮 Session Summary")
        print("=" * 60)
        print(f"Session ID: {session['session_id']}")
        print(f"Start Time: {session['start_time']}")
        print(f"End Time: {session['end_time']}")
        print(f"Dream Branch: {session['dream_branch']}")
        print(f"Constellation Coherence: {session['triad_coherence']:.3f}")
        print(f"Observer: {session['observer']}")
        print(f"Notes: {session['notes']}")
        print("\n📊 Entropy Drift:")

        for drift in session["entropy_drift"]:
            phase_color = self._get_phase_color(drift["phase"])
            print(
                f"  {drift['timestamp'][11:23]} - Entropy: {drift['entropy']:.3f} - Phase: {phase_color}{drift['phase']}\033[0m"
            )

        print(f"\n💥 Collapsed Glyphs: {' → '.join(session['collapsed_glyphs'])}")

        if session["guardian_flags"]:
            print("\n🛡️ Guardian Flags:")
            for flag in session["guardian_flags"]:
                print(f"  - {flag}")
        else:
            print("\n✅ No Guardian interventions")

    def _get_phase_color(self, phase: str) -> str:
        """Get ANSI color for phase"""
        colors = {
            "calm": "\033[94m",  # Blue
            "drift": "\033[92m",  # Green
            "unstable": "\033[93m",  # Yellow
            "collapse": "\033[91m",  # Red
        }
        return colors.get(phase, "")

    def simulate_replay(self, session_id: str) -> None:
        """Simulate replay of a session"""
        session = self.get_session(session_id)
        if not session:
            print(f"❌ Error: Session '{session_id}' not found")
            sys.exit(1)

        print("🌀 Collapse Replay Simulation")
        print("=" * 60)
        print(f"Replaying session: {session['session_id']}")
        print(f"Dream branch: {session['dream_branch']}")
        print("\nInitializing quantum consciousness...\n")

        # Create wavefunction manager
        wm = WavefunctionManager()

        # Determine initial template based on dream branch
        template_map = {
            "grounded": "triad_coherence",
            "lucid": "reflective_dreaming",
            "chaotic": "entropy_chaos",
            "transcendent": "transcendent_awareness",
            "recursive": "reflective_dreaming",
        }
        template = template_map.get(session["dream_branch"], "triad_coherence")

        # Create initial wavefunction
        print(f"Creating wavefunction with template: {template}")
        initial_entropy = session["entropy_drift"][0]["entropy"]
        wf = wm.create_wavefunction(wf_id="replay_wf", template_name=template, initial_entropy=initial_entropy)

        print(f"Initial state: {' + '.join(wf.glyph_superposition)}")
        print(f"Initial entropy: {wf.entropy_score:.3f}")
        print(f"Constellation coherence: {wf.triad_coherence:.3f}")
        print("\n" + "-" * 40 + "\n")

        # Replay entropy drift
        print("📈 Drift Trace:")
        collapse_index = 0

        for i, drift_point in enumerate(session["entropy_drift"]):
            # Update entropy
            target_entropy = drift_point["entropy"]
            phase = drift_point["phase"]

            # Simulate entropy evolution
            if target_entropy > wf.entropy_score:
                wm.global_entropy = target_entropy
                wf.entropy_score = target_entropy

            phase_color = self._get_phase_color(phase)
            print(f"Step {i + 1}: Entropy {wf.entropy_score:.3f} - Phase: {phase_color}{phase}\033[0m")

            # Check for collapse conditions
            if phase in ["unstable", "collapse"] and collapse_index < len(session["collapsed_glyphs"]):
                collapsed_glyph = session["collapsed_glyphs"][collapse_index]
                print(f"  💥 Collapse triggered → {collapsed_glyph}")
                collapse_index += 1

                # Recreate wavefunction if more collapses expected
                if collapse_index < len(session["collapsed_glyphs"]):
                    wf = wm.create_wavefunction(
                        wf_id=f"replay_wf_{collapse_index}",
                        template_name=template,
                        initial_entropy=target_entropy,
                    )

            # Show guardian flags at appropriate times
            if i == len(session["entropy_drift"]) // 2 and session["guardian_flags"]:
                print(f"\n🛡️ Guardian Alert: {session['guardian_flags'][0]}")

            time.sleep(0.5)  # Dramatic pause

        print("\n" + "-" * 40 + "\n")

        # Final summary
        print("📋 Replay Summary:")
        print(f"  Final entropy: {session['entropy_drift'][-1]['entropy']:.3f}")
        print(f"  Collapse sequence: {' → '.join(session['collapsed_glyphs'])}")
        print(f"  Guardian involvement: {'Yes' if session['guardian_flags'] else 'No'}")
        print(f"  Final glyph: {session['collapsed_glyphs'][-1] if session['collapsed_glyphs'] else 'None'}")
        print(f"  Constellation coherence: {session['triad_coherence']:.3f}")

        # Symbolic interpretation
        print("\n🔮 Symbolic Interpretation:")
        final_glyph = session["collapsed_glyphs"][-1] if session["collapsed_glyphs"] else None
        interpretation = self._interpret_glyph(final_glyph)
        print(f"  {interpretation}")

        print("\n✅ Replay complete")

    def _interpret_glyph(self, glyph: Optional[str]) -> str:
        """Provide symbolic interpretation of collapsed glyph"""
        interpretations = {
            "🧠": "Consciousness achieved analytical clarity",
            "⚛️": "System returned to quantum coherence",
            "🛡️": "Guardian protection successfully maintained",
            "🔮": "Intuitive wisdom emerged from the process",
            "🌙": "Dream-like awareness persisted",
            "⚡": "Energetic breakthrough occurred",
            "🌪️": "The system resolved internal chaos",
            "🔥": "Transformative energy was released",
            "💥": "Critical transition point reached",
            "🪷": "A symbolic state of clarity has been reached",
            "🌌": "Transcendent awareness touched the void",
            "🕉️": "Unity consciousness briefly manifested",
            "💎": "Crystalline focus was achieved",
            "🧘": "Meditative equilibrium restored",
        }

        if glyph and glyph in interpretations:
            return interpretations[glyph]
        elif glyph:
            return f"The system collapsed to {glyph} - a unique symbolic state"
        else:
            return "No collapse occurred - the system maintained superposition"


def main():
    parser = argparse.ArgumentParser(
        description="LUKHΛS Collapse Replay Tool - Recreate symbolic cognition flows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 collapse_replay.py --list-sessions
  python3 collapse_replay.py --session q-1754265955 --summary
  python3 collapse_replay.py --session q-1754265955 --simulate
        """,
    )

    parser.add_argument("--session", type=str, help="Session ID to replay")
    parser.add_argument("--simulate", action="store_true", help="Run simulation replay")
    parser.add_argument("--summary", action="store_true", help="Show session summary")
    parser.add_argument("--list-sessions", action="store_true", help="List all available sessions")
    parser.add_argument(
        "--journal",
        type=str,
        default="qi_core/drift_journal.json",
        help="Path to drift journal (default: qi_core/drift_journal.json)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.list_sessions, args.session]):
        parser.print_help()
        sys.exit(1)

    if args.session and not any([args.simulate, args.summary]):
        print("❌ Error: Must specify --simulate or --summary with --session")
        sys.exit(1)

    # Create tool instance
    tool = CollapseReplayTool(args.journal)

    # Execute requested action
    if args.list_sessions:
        tool.list_sessions()
    elif args.session:
        if args.summary:
            tool.show_summary(args.session)
        elif args.simulate:
            tool.simulate_replay(args.session)


if __name__ == "__main__":
    main()
