#!/usr/bin/env python3
"""
Guardian Override Visual - Console visualization for Guardian lockdown states
Shows real-time security status with symbolic chevron animations
"""
import streamlit as st

import asyncio
import math
import random
import sys
import time
from typing import Optional


# Console control sequences
class Console:
    """Enhanced console control for Guardian visualization"""

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
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    RESET = "\033[0m"

    # Background colors
    BG_RED = "\033[101m"
    BG_YELLOW = "\033[103m"
    BG_GREEN = "\033[102m"
    BG_BLUE = "\033[104m"

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


class GuardianVisualizer:
    """
    Real-time Guardian status visualization with lockdown animations
    Displays security state through symbolic chevron patterns and alerts
    """

    # Guardian status levels with visual patterns
    STATUS_PATTERNS = {
        "monitoring": {
            "level": 0,
            "glyph": "🛡️",
            "color": Console.GREEN,
            "bg_color": "",
            "animation": "pulse",
            "description": "Guardian - Active Monitoring",
            "chevron": "🔹",
            "blink": False,
        },
        "alert": {
            "level": 1,
            "glyph": "⚠️",
            "color": Console.YELLOW,
            "bg_color": "",
            "animation": "wave",
            "description": "Guardian - Alert State",
            "chevron": "🔸",
            "blink": False,
        },
        "intervention": {
            "level": 2,
            "glyph": "🚨",
            "color": Console.RED,
            "bg_color": "",
            "animation": "urgent",
            "description": "Guardian - Active Intervention",
            "chevron": "🔺",
            "blink": True,
        },
        "lockdown": {
            "level": 3,
            "glyph": "🔐",
            "color": Console.RED + Console.BOLD,
            "bg_color": Console.BG_RED,
            "animation": "lockdown",
            "description": "Guardian - SYSTEM LOCKDOWN",
            "chevron": "🔴",
            "blink": True,
        },
        "emergency": {
            "level": 4,
            "glyph": "🚨",
            "color": Console.RED + Console.BOLD + Console.BLINK,
            "bg_color": Console.BG_RED,
            "animation": "emergency",
            "description": "Guardian - EMERGENCY PROTOCOL",
            "chevron": "🟥",
            "blink": True,
        },
    }

    # Threat types and their visual representations
    THREAT_VISUALS = {
        "drift_spike": {
            "symbol": "🌪️",
            "color": Console.YELLOW,
            "pattern": ["🌪️", "🌀", "🌿"],
        },
        "entropy_surge": {
            "symbol": "🔥",
            "color": Console.RED,
            "pattern": ["🔥", "💨", "❄️"],
        },
        "pattern_anomaly": {
            "symbol": "❌",
            "color": Console.PURPLE,
            "pattern": ["❌", "🔄", "✅"],
        },
        "consciousness_instability": {
            "symbol": "⚡",
            "color": Console.CYAN,
            "pattern": ["⚓", "🧘", "🔒"],
        },
        "memory_fragmentation": {
            "symbol": "🧩",
            "color": Console.BLUE,
            "pattern": ["🧩", "🔧", "🏛️"],
        },
    }

    def __init__(self, update_interval: float = 0.1):
        self.update_interval = update_interval
        self.current_status = "monitoring"
        self.active_threats: list[dict] = []
        self.running = False
        self.start_time = time.time()

        # Animation state
        self.animation_phase = 0.0
        self.chevron_positions = [0, 0, 0, 0, 0]  # Five chevron bars
        self.alert_flash_state = False
        self.lockdown_active = False
        self.emergency_mode = False

        # Lockdown timing
        self.lockdown_start_time = None
        self.lockdown_duration = 0

        print(f"{Console.GREEN}🛡️ Guardian Visual Monitor initialized{Console.RESET}")

    async def start_monitoring(self):
        """Start the Guardian visual monitoring loop"""
        self.running = True

        # Hide cursor and clear screen
        print(Console.CURSOR_HIDE, end="")
        print(Console.clear_screen(), end="")

        try:
            # Run monitoring tasks concurrently
            await asyncio.gather(
                self._update_animation_state(),
                self._render_guardian_display(),
                self._simulate_threat_detection(),  # For demo purposes
            )
        except KeyboardInterrupt:
            print(f"\n{Console.YELLOW}🛡️ Guardian monitoring stopped{Console.RESET}")
        finally:
            # Restore cursor
            print(Console.CURSOR_SHOW, end="")
            self.running = False

    async def _update_animation_state(self):
        """Update animation phase and chevron positions"""
        while self.running:
            self.animation_phase += 0.1

            # Update chevron positions based on current status
            pattern = self.STATUS_PATTERNS[self.current_status]

            if pattern["animation"] == "pulse":
                # Gentle pulsing for monitoring
                for i in range(len(self.chevron_positions)):
                    self.chevron_positions[i] = 0.5 + 0.3 * math.sin(self.animation_phase + i * 0.5)

            elif pattern["animation"] == "wave":
                # Wave animation for alerts
                for i in range(len(self.chevron_positions)):
                    self.chevron_positions[i] = 0.7 + 0.3 * math.sin(self.animation_phase * 2 + i * 0.8)

            elif pattern["animation"] == "urgent":
                # Rapid pulsing for intervention
                for i in range(len(self.chevron_positions)):
                    self.chevron_positions[i] = 0.8 + 0.2 * math.sin(self.animation_phase * 4 + i * 0.3)

            elif pattern["animation"] == "lockdown":
                # Synchronized flashing for lockdown
                flash_value = 0.9 if int(self.animation_phase * 3) % 2 else 0.3
                for i in range(len(self.chevron_positions)):
                    self.chevron_positions[i] = flash_value

            elif pattern["animation"] == "emergency":
                # Chaotic emergency pattern
                for i in range(len(self.chevron_positions)):
                    self.chevron_positions[i] = 0.5 + 0.5 * math.sin(
                        self.animation_phase * 6 + i * random.uniform(0.5, 1.5)
                    )

            # Update flash state for blinking elements
            self.alert_flash_state = int(self.animation_phase * 4) % 2 == 0

            await asyncio.sleep(self.update_interval)

    async def _render_guardian_display(self):
        """Render the main Guardian visual display"""
        while self.running:
            pattern = self.STATUS_PATTERNS[self.current_status]

            # Clear screen and render frame
            await self._draw_header()
            await self._draw_status_display(pattern)
            await self._draw_chevron_array(pattern)
            await self._draw_threat_indicators()
            await self._draw_system_metrics()
            await self._draw_lockdown_overlay()

            await asyncio.sleep(self.update_interval)

    async def _draw_header(self):
        """Draw the Guardian system header"""
        print(Console.move_cursor(1, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}╔════════════════════════════════════════════════════════════════════════════╗{Console.RESET}",
            end="",
        )

        print(Console.move_cursor(2, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}║ 🛡️ LUKHAS GUARDIAN SYSTEM - VISUAL MONITORING INTERFACE                 ║{Console.RESET}",
            end="",
        )

        print(Console.move_cursor(3, 1), end="")
        print(
            f"{Console.BOLD}{Console.CYAN}╚════════════════════════════════════════════════════════════════════════════╝{Console.RESET}",
            end="",
        )

    async def _draw_status_display(self, pattern: dict):
        """Draw current Guardian status with glyph and description"""
        # Status line
        print(Console.move_cursor(5, 20), end="")
        print(Console.CLEAR_LINE, end="")

        status_color = pattern["color"]
        if pattern["blink"] and self.alert_flash_state:
            status_color += Console.REVERSE

        print(
            f"{status_color}{pattern['glyph']} {pattern['description']}{Console.RESET}",
            end="",
        )

        # Security level indicator
        print(Console.move_cursor(6, 20), end="")
        print(Console.CLEAR_LINE, end="")

        level_bars = "█" * (pattern["level"] + 1) + "░" * (4 - pattern["level"])
        level_color = Console.GREEN if pattern["level"] < 2 else Console.YELLOW if pattern["level"] < 3 else Console.RED

        print(
            f"{Console.WHITE}Security Level: {level_color}{level_bars}{Console.RESET} ({pattern['level']}/4)",
            end="",
        )

    async def _draw_chevron_array(self, pattern: dict):
        """Draw animated chevron array showing Guardian activity"""
        chevron_char = pattern["chevron"]
        base_color = pattern["color"]

        # Draw chevron bars
        for row in range(5):
            print(Console.move_cursor(9 + row, 30), end="")
            print(Console.CLEAR_LINE, end="")

            # Calculate intensity for this row
            intensity = self.chevron_positions[row]

            # Choose color based on intensity
            if intensity > 0.8:
                color = base_color + Console.BOLD
            elif intensity > 0.6:
                color = base_color
            elif intensity > 0.3:
                color = base_color + Console.DIM
            else:
                color = Console.DIM

            # Create chevron bar
            bar_length = int(intensity * 20)
            chevron_bar = chevron_char * bar_length + "░" * (20 - bar_length)

            print(f"{color}{chevron_bar}{Console.RESET}", end="")

        # Chevron array label
        print(Console.move_cursor(15, 30), end="")
        print(f"{Console.DIM}Guardian Activity Matrix{Console.RESET}", end="")

    async def _draw_threat_indicators(self):
        """Draw active threat indicators"""
        print(Console.move_cursor(8, 60), end="")
        print(f"{Console.BOLD}ACTIVE THREATS:{Console.RESET}", end="")

        if not self.active_threats:
            print(Console.move_cursor(9, 60), end="")
            print(f"{Console.GREEN}✅ No threats detected{Console.RESET}", end="")
        else:
            for i, threat in enumerate(self.active_threats[:5]):  # Show max 5 threats
                print(Console.move_cursor(9 + i, 60), end="")
                print(Console.CLEAR_LINE, end="")

                threat_visual = self.THREAT_VISUALS.get(
                    threat["type"],
                    {"symbol": "⚠️", "color": Console.YELLOW, "pattern": ["⚠️"]},
                )

                severity_color = Console.RED if threat["severity"] > 0.7 else Console.YELLOW
                severity_bar = "█" * int(threat["severity"] * 5)

                print(
                    f"{threat_visual['color']}{threat_visual['symbol']}{Console.RESET} ",
                    end="",
                )
                print(
                    f"{threat['type']} {severity_color}{severity_bar}{Console.RESET}",
                    end="",
                )

    async def _draw_system_metrics(self):
        """Draw system metrics and uptime"""
        uptime = time.time() - self.start_time

        print(Console.move_cursor(17, 20), end="")
        print(Console.CLEAR_LINE, end="")
        print(f"{Console.CYAN}Uptime:{Console.RESET} {uptime:.0f}s", end="")

        print(Console.move_cursor(18, 20), end="")
        print(Console.CLEAR_LINE, end="")
        print(
            f"{Console.CYAN}Status:{Console.RESET} {self.current_status.upper()}",
            end="",
        )

        print(Console.move_cursor(19, 20), end="")
        print(Console.CLEAR_LINE, end="")
        print(f"{Console.CYAN}Threats:{Console.RESET} {len(self.active_threats)}", end="")

        # Trinity Framework status
        print(Console.move_cursor(20, 20), end="")
        print(Console.CLEAR_LINE, end="")
        trinity_color = Console.GREEN if self.current_status in ["monitoring", "alert"] else Console.RED
        print(
            f"{Console.CYAN}Trinity:{Console.RESET} ⚛️🧠🛡️ {trinity_color}ACTIVE{Console.RESET}",
            end="",
        )

    async def _draw_lockdown_overlay(self):
        """Draw lockdown overlay when system is locked down"""
        if self.current_status in ["lockdown", "emergency"]:
            if not self.lockdown_active:
                self.lockdown_active = True
                self.lockdown_start_time = time.time()

            # Draw lockdown border
            if self.alert_flash_state:
                border_color = Console.RED + Console.BG_RED
                for row in range(1, 25):
                    # Left border
                    print(Console.move_cursor(row, 1), end="")
                    print(f"{border_color} {Console.RESET}", end="")

                    # Right border
                    print(Console.move_cursor(row, 78), end="")
                    print(f"{border_color} {Console.RESET}", end="")

            # Lockdown message
            print(Console.move_cursor(22, 25), end="")
            print(Console.CLEAR_LINE, end="")

            if self.current_status == "lockdown":
                message = "🚨🔐 SYSTEM LOCKDOWN ACTIVE 🔐🚨"
                color = Console.RED + Console.BOLD
            else:
                message = "🚨⚡ EMERGENCY PROTOCOL ENGAGED ⚡🚨"
                color = Console.RED + Console.BOLD + Console.BLINK

            if self.alert_flash_state:
                print(f"{color}{message}{Console.RESET}", end="")

            # Lockdown timer
            if self.lockdown_start_time:
                lockdown_time = time.time() - self.lockdown_start_time
                print(Console.move_cursor(23, 30), end="")
                print(Console.CLEAR_LINE, end="")
                print(
                    f"{Console.RED}Lockdown Duration: {lockdown_time:.0f}s{Console.RESET}",
                    end="",
                )
        else:
            if self.lockdown_active:
                self.lockdown_active = False
                self.lockdown_start_time = None

        # Instructions
        print(Console.move_cursor(24, 20), end="")
        print(Console.CLEAR_LINE, end="")
        print(
            f"{Console.DIM}Press 'q' to quit, '1-5' to change status, 't' to add threat{Console.RESET}",
            end="",
        )

    async def _simulate_threat_detection(self):
        """Simulate threat detection for demo purposes"""
        threat_types = list(self.THREAT_VISUALS.keys())

        while self.running:
            # Randomly add threats
            if random.random() < 0.05:  # 5% chance per cycle
                threat_type = random.choice(threat_types)
                severity = random.uniform(0.3, 0.9)

                threat = {
                    "type": threat_type,
                    "severity": severity,
                    "timestamp": time.time(),
                    "id": f"threat_{len(self.active_threats)}",
                }

                self.active_threats.append(threat)

                # Update status based on threat severity
                if severity > 0.8 and self.current_status == "monitoring":
                    await self.set_status("intervention")
                elif severity > 0.6 and self.current_status == "monitoring":
                    await self.set_status("alert")

            # Remove old threats
            current_time = time.time()
            self.active_threats = [
                t for t in self.active_threats if current_time - t["timestamp"] < 30
            ]  # Remove after 30s

            # Auto-escalate if many threats
            if len(self.active_threats) > 3 and self.current_status != "lockdown":
                await self.set_status("lockdown")
            elif len(self.active_threats) == 0 and self.current_status != "monitoring":
                await self.set_status("monitoring")

            await asyncio.sleep(2.0)  # Check every 2 seconds

    async def set_status(self, new_status: str):
        """Change Guardian status"""
        if new_status in self.STATUS_PATTERNS:
            old_status = self.current_status
            self.current_status = new_status

            # Log status change
            print(Console.move_cursor(25, 1), end="")
            print(Console.CLEAR_LINE, end="")
            print(
                f"{Console.YELLOW}Status changed: {old_status} → {new_status}{Console.RESET}",
                end="",
                flush=True,
            )

    async def add_threat(self, threat_type: Optional[str] = None, severity: Optional[float] = None):
        """Manually add a threat for testing"""
        threat_type = threat_type or random.choice(list(self.THREAT_VISUALS.keys()))
        severity = severity or random.uniform(0.5, 0.9)

        threat = {
            "type": threat_type,
            "severity": severity,
            "timestamp": time.time(),
            "id": f"manual_threat_{len(self.active_threats)}",
        }

        self.active_threats.append(threat)


class GuardianDemo:
    """Interactive demo for Guardian visualization"""

    def __init__(self):
        self.visualizer = GuardianVisualizer()

    async def run_interactive_demo(self):
        """Run interactive Guardian demo"""
        print(f"{Console.GREEN}🛡️ Starting Guardian interactive demo...{Console.RESET}")
        print(f"{Console.YELLOW}Use keys 1-5 for status, 't' for threat, 'q' to quit{Console.RESET}")

        # Start visualization
        viz_task = asyncio.create_task(self.visualizer.start_monitoring())

        # Start input handler
        input_task = asyncio.create_task(self._handle_input())

        try:
            await asyncio.gather(viz_task, input_task)
        except (KeyboardInterrupt, asyncio.CancelledError):
            viz_task.cancel()
            input_task.cancel()

    async def _handle_input(self):
        """Handle keyboard input for demo control"""
        # Note: This is a simplified input handler
        # In a full implementation, you'd use proper async input handling

        while self.visualizer.running:
            await asyncio.sleep(0.1)

            # For demo purposes, automatically cycle through states
            await asyncio.sleep(8)

            # Cycle through statuses
            current_level = self.visualizer.STATUS_PATTERNS[self.visualizer.current_status]["level"]
            next_level = (current_level + 1) % 5

            status_by_level = {v["level"]: k for k, v in self.visualizer.STATUS_PATTERNS.items()}
            next_status = status_by_level[next_level]

            await self.visualizer.set_status(next_status)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUKHAS Guardian Visual Monitor")
    parser.add_argument("--demo", action="store_true", help="Run interactive demo")
    parser.add_argument(
        "--status",
        type=str,
        choices=list(GuardianVisualizer.STATUS_PATTERNS.keys()),
        default="monitoring",
        help="Initial Guardian status",
    )

    args = parser.parse_args()

    if args.demo:
        demo = GuardianDemo()
        await demo.run_interactive_demo()
    else:
        visualizer = GuardianVisualizer()
        await visualizer.set_status(args.status)
        await visualizer.start_monitoring()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Console.YELLOW}🛡️ Guardian visual monitoring stopped by user{Console.RESET}")
    except Exception as e:
        print(f"\n{Console.RED}❌ Error: {e}{Console.RESET}")
        sys.exit(1)
