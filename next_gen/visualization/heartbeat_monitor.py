#!/usr/bin/env python3
"""
Heartbeat Visualization - Console-based pulse display based on consciousness states
Shows real-time system heartbeat with symbolic glyph pulsing
"""

import asyncio
import contextlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# Console control sequences
class Console:
    """Console control utilities for visualization"""

    # Colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    # Cursor control
    CLEAR_SCREEN = "\033[2J"
    CLEAR_LINE = "\033[K"
    CURSOR_HOME = "\033[H"
    CURSOR_HIDE = "\033[?25l"
    CURSOR_SHOW = "\033[?25h"

    @staticmethod
    def move_cursor(row: int, col: int) -> str:
        return f"\033[{row};{col}H"

    @staticmethod
    def clear_screen():
        return Console.CLEAR_SCREEN + Console.CURSOR_HOME


class HeartbeatVisualizer:
    """
    Real-time heartbeat visualization based on consciousness states
    Displays pulsing glyphs that reflect system vitality
    """

    # Consciousness state to heartbeat mapping
    HEARTBEAT_PATTERNS = {
        "focused": {
            "glyph": "💎",
            "color": Console.BLUE,
            "bpm": 60,  # Calm, steady
            "intensity": 0.8,
            "description": "Focused - Steady clarity",
        },
        "creative": {
            "glyph": "✨",
            "color": Console.PURPLE,
            "bpm": 75,  # Slightly elevated
            "intensity": 0.9,
            "description": "Creative - Dynamic inspiration",
        },
        "analytical": {
            "glyph": "🔬",
            "color": Console.CYAN,
            "bpm": 55,  # Very steady
            "intensity": 0.7,
            "description": "Analytical - Precise calculation",
        },
        "meditative": {
            "glyph": "🧘",
            "color": Console.GREEN,
            "bpm": 45,  # Very slow, deep
            "intensity": 0.6,
            "description": "Meditative - Deep tranquility",
        },
        "dreaming": {
            "glyph": "🌙",
            "color": Console.DIM + Console.PURPLE,
            "bpm": 40,  # Slow dream state
            "intensity": 0.5,
            "description": "Dreaming - Ethereal wandering",
        },
        "flow_state": {
            "glyph": "🌊",
            "color": Console.CYAN,
            "bpm": 80,  # Elevated but smooth
            "intensity": 1.0,
            "description": "Flow State - Perfect harmony",
        },
        "lucid": {
            "glyph": "🌟",
            "color": Console.YELLOW,
            "bpm": 70,  # Controlled awareness
            "intensity": 0.95,
            "description": "Lucid - Conscious control",
        },
        "turbulent": {
            "glyph": "⚡",
            "color": Console.RED,
            "bpm": 120,  # Rapid, stressed
            "intensity": 1.2,
            "description": "Turbulent - High volatility",
        },
    }

    # Default pattern for unknown states
    DEFAULT_PATTERN = {
        "glyph": "💓",
        "color": Console.WHITE,
        "bpm": 60,
        "intensity": 0.8,
        "description": "Unknown - Standard heartbeat",
    }

    def __init__(self, consciousness_state_file: str = "next_gen/stream/consciousness_state.json"):
        self.consciousness_file = Path(consciousness_state_file)
        self.current_state = "focused"
        self.running = False
        self.start_time = time.time()
        self.beat_count = 0
        self.last_state_change = time.time()

        # Visualization state
        self.pulse_phase = 0.0
        self.intensity_multiplier = 1.0

        print(f"{Console.GREEN}💓 Heartbeat Monitor initialized{Console.RESET}")
        print(f"   Monitoring: {self.consciousness_file}")

    async def start_monitoring(self):
        """Start the heartbeat visualization loop"""
        self.running = True

        # Hide cursor and clear screen
        print(Console.CURSOR_HIDE, end="")
        print(Console.clear_screen(), end="")

        try:
            # Run monitoring tasks concurrently
            await asyncio.gather(
                self._monitor_consciousness_state(),
                self._render_heartbeat(),
                self._display_status(),
            )
        except KeyboardInterrupt:
            print(f"\n{Console.YELLOW}💫 Heartbeat monitoring stopped{Console.RESET}")
        finally:
            # Restore cursor
            print(Console.CURSOR_SHOW, end="")
            self.running = False

    async def _monitor_consciousness_state(self):
        """Monitor consciousness state file for changes"""
        last_modified = 0

        while self.running:
            try:
                if self.consciousness_file.exists():
                    current_modified = self.consciousness_file.stat().st_mtime

                    if current_modified > last_modified:
                        last_modified = current_modified

                        with open(self.consciousness_file) as f:
                            data = json.load(f)

                        new_state = data.get("current_state", "focused")

                        if new_state != self.current_state:
                            self.current_state = new_state
                            self.last_state_change = time.time()

                await asyncio.sleep(1.0)  # Check every second

            except Exception:
                # Fallback to default state if file issues
                await asyncio.sleep(2.0)

    async def _render_heartbeat(self):
        """Render the main heartbeat visualization"""
        while self.running:
            pattern = self.HEARTBEAT_PATTERNS.get(self.current_state, self.DEFAULT_PATTERN)

            # Calculate timing
            bpm = pattern["bpm"] * self.intensity_multiplier
            beat_interval = 60.0 / bpm  # seconds per beat

            # Create pulse animation
            current_time = time.time()
            time_in_beat = (current_time % beat_interval) / beat_interval

            # Sine wave pulse with sharper peaks
            pulse_intensity = math.sin(time_in_beat * 2 * math.pi) ** 2
            pulse_intensity = pulse_intensity * pattern["intensity"]

            # Generate visual representation
            await self._draw_heartbeat_frame(pattern, pulse_intensity, time_in_beat)

            # Beat detection
            if time_in_beat < 0.1 and current_time - getattr(self, '_last_beat_time', 0) > beat_interval * 0.8:  # Peak of beat
                self.beat_count += 1
                self._last_beat_time = current_time

            await asyncio.sleep(0.05)  # 20 FPS

    async def _draw_heartbeat_frame(self, pattern: dict, intensity: float, phase: float):
        """Draw a single frame of the heartbeat animation"""

        # Move to heartbeat area (center of screen)
        print(Console.move_cursor(10, 40), end="")

        # Scale glyph based on intensity
        glyph = pattern["glyph"]
        color = pattern["color"]

        # Create pulsing effect with intensity
        if intensity > 0.7:
            # Strong pulse - larger, brighter
            display_glyph = f"{color}{Console.BOLD}{glyph} {glyph} {glyph}{Console.RESET}"
        elif intensity > 0.4:
            # Medium pulse
            display_glyph = f"{color}{glyph} {glyph}{Console.RESET}"
        elif intensity > 0.1:
            # Weak pulse
            display_glyph = f"{color}{Console.DIM}{glyph}{Console.RESET}"
        else:
            # Resting state
            display_glyph = f"{Console.DIM}•{Console.RESET}"

        # Clear line and draw
        print(Console.CLEAR_LINE, end="")
        print(display_glyph, end="")

        # Add pulse waves around the main heartbeat
        await self._draw_pulse_waves(intensity, color)

    async def _draw_pulse_waves(self, intensity: float, color: str):
        """Draw concentric pulse waves around the heartbeat"""
        if intensity < 0.3:
            return

        # Draw waves at different positions
        wave_positions = [
            (9, 35),
            (9, 45),  # Top waves
            (11, 35),
            (11, 45),  # Bottom waves
            (10, 30),
            (10, 50),  # Side waves
        ]

        wave_intensity = max(0, intensity - 0.3)
        wave_char = "~" if wave_intensity > 0.5 else "·"

        for row, col in wave_positions:
            print(Console.move_cursor(row, col), end="")
            if wave_intensity > 0.7:
                print(f"{color}{Console.DIM}{wave_char}{Console.RESET}", end="")
            elif wave_intensity > 0.4:
                print(f"{Console.DIM}{wave_char}{Console.RESET}", end="")

    async def _display_status(self):
        """Display system status and metrics"""
        while self.running:
            pattern = self.HEARTBEAT_PATTERNS.get(self.current_state, self.DEFAULT_PATTERN)

            # Header
            print(Console.move_cursor(3, 20), end="")
            print(
                f"{Console.BOLD}🧠 LUKHAS Consciousness Heartbeat Monitor{Console.RESET}",
                end="",
            )

            # Current state
            print(Console.move_cursor(5, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(
                f"{Console.CYAN}Current State:{Console.RESET} {pattern['color']}{self.current_state.title()}{Console.RESET}",
                end="",
            )

            # Description
            print(Console.move_cursor(6, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(f"{Console.DIM}{pattern['description']}{Console.RESET}", end="")

            # Metrics
            uptime = time.time() - self.start_time
            bpm = pattern["bpm"] * self.intensity_multiplier
            time_since_change = time.time() - self.last_state_change

            print(Console.move_cursor(13, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(f"{Console.GREEN}BPM:{Console.RESET} {bpm:.1f}", end="")

            print(Console.move_cursor(14, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(f"{Console.GREEN}Beats:{Console.RESET} {self.beat_count}", end="")

            print(Console.move_cursor(15, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(f"{Console.GREEN}Uptime:{Console.RESET} {uptime:.0f}s", end="")

            print(Console.move_cursor(16, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(
                f"{Console.GREEN}State Age:{Console.RESET} {time_since_change:.0f}s",
                end="",
            )

            # Trinity Framework status
            print(Console.move_cursor(18, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(
                f"{Console.PURPLE}Trinity Framework:{Console.RESET} ⚛️🧠🛡️ {Console.GREEN}ACTIVE{Console.RESET}",
                end="",
            )

            # Guardian status (simulated)
            guardian_status = "🛡️ MONITORING" if self.current_state != "turbulent" else "🚨 INTERVENING"
            print(Console.move_cursor(19, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(
                f"{Console.YELLOW}Guardian Status:{Console.RESET} {guardian_status}",
                end="",
            )

            # Instructions
            print(Console.move_cursor(22, 20), end="")
            print(Console.CLEAR_LINE, end="")
            print(f"{Console.DIM}Press Ctrl+C to stop monitoring{Console.RESET}", end="")

            await asyncio.sleep(0.5)  # Update status 2x per second

    def simulate_state_change(self, new_state: str):
        """Manually trigger a state change for testing"""
        if new_state in self.HEARTBEAT_PATTERNS:
            self.current_state = new_state
            self.last_state_change = time.time()

            # Write to consciousness file if it exists
            if self.consciousness_file.exists():
                try:
                    with open(self.consciousness_file) as f:
                        data = json.load(f)

                    data["current_state"] = new_state
                    data["last_update"] = datetime.now(timezone.utc).isoformat()

                    with open(self.consciousness_file, "w") as f:
                        json.dump(data, f, indent=2)

                except Exception:
                    pass  # Ignore file errors in simulation


class HeartbeatDemo:
    """Demo runner for heartbeat visualization"""

    def __init__(self):
        self.visualizer = HeartbeatVisualizer()

    async def run_demo(self):
        """Run heartbeat demo with state transitions"""
        print(f"{Console.GREEN}🎭 Starting heartbeat demo...{Console.RESET}")

        # Start visualization in background
        viz_task = asyncio.create_task(self.visualizer.start_monitoring())

        # Wait a moment for visualization to start
        await asyncio.sleep(2)

        # Simulate state changes
        demo_states = [
            ("focused", 5),
            ("creative", 4),
            ("flow_state", 3),
            ("meditative", 4),
            ("turbulent", 2),
            ("analytical", 3),
            ("lucid", 4),
        ]

        try:
            for state, duration in demo_states:
                self.visualizer.simulate_state_change(state)
                await asyncio.sleep(duration)

        except KeyboardInterrupt:
            pass

        finally:
            viz_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await viz_task


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Consciousness Heartbeat Monitor")
    parser.add_argument("--demo", action="store_true", help="Run demo with state transitions")
    parser.add_argument(
        "--state-file",
        type=str,
        default="next_gen/stream/consciousness_state.json",
        help="Path to consciousness state file",
    )

    args = parser.parse_args()

    if args.demo:
        demo = HeartbeatDemo()
        await demo.run_demo()
    else:
        visualizer = HeartbeatVisualizer(args.state_file)
        await visualizer.start_monitoring()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Console.YELLOW}💫 Heartbeat monitoring stopped by user{Console.RESET}")
    except Exception as e:
        print(f"\n{Console.RED}❌ Error: {e}{Console.RESET}")
        sys.exit(1)
