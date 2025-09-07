#!/usr/bin/env python3
"""
LUKHAS AI ΛBot Status Bar Designer

Customize the appearance and behavior of your LUKHAS AI ΛBot status bar indicator.
This script provides examples and options for different designs.
"""
from pathlib import Path


class BotStatusDesigner:
    """Customizable status bar designer for LUKHAS AI ΛBot."""

    def __init__(self, workspace: str):
        self.workspace = Path(workspace).resolve()
        self.widget_file = self.workspace / ".vscode" / "abot_widget.json"

    def create_custom_status(self, design_template: str, **kwargs):
        """Create custom status bar with different designs."""

        designs = {
            "minimal": {
                "text": "LUKHAS AI ΛBot",
                "icon": "🤖",
                "colors": {"success": "#28a745", "warning": "#ffc107", "error": "#dc3545"},
                "commands": ["LUKHAS AI ΛBot.showStatus"],
            },
            "detailed": {
                "text": "LUKHAS AI ΛBot Monitor - {status}",
                "icon": "🎯",
                "colors": {"success": "#00ff88", "warning": "#ffaa00", "error": "#ff4444"},
                "commands": ["LUKHAS AI ΛBot.scan", "LUKHAS AI ΛBot.showStatus"],
            },
            "compact": {
                "text": "Λ {violations}",
                "icon": "",
                "colors": {"success": "#00aa00", "warning": "#aa6600", "error": "#aa0000"},
                "commands": ["LUKHAS AI ΛBot.quickFix"],
            },
            "professional": {
                "text": "Quality: {quality_score}%",
                "icon": "📊",
                "colors": {"success": "#2ea043", "warning": "#fb8500", "error": "#d1242f"},
                "commands": ["LUKHAS AI ΛBot.showReport"],
            },
            "developer": {
                "text": "⚡ {files_scanned} files | {violations} issues",
                "icon": "",
                "colors": {"success": "#39d353", "warning": "#d4ac0d", "error": "#e74c3c"},
                "commands": ["LUKHAS AI ΛBot.scan", "LUKHAS AI ΛBot.applyFixes"],
            },
            "gaming": {
                "text": "🎮 Level {quality_level} | ⚔️ {critical} critical",
                "icon": "",
                "colors": {"success": "#00ff00", "warning": "#ffff00", "error": "#ff0000"},
                "commands": ["LUKHAS AI ΛBot.battleMode"],
            },
        }

        if design_template not in designs:
            raise ValueError(f"Unknown design: {design_template}")

        design = designs[design_template]
        return self.apply_design(design, **kwargs)

    def apply_design(self, design, **data):
        """Apply design template with current data."""

        # Format text with provided data
        text = design["text"].format(**data)
        icon = design["icon"]

        # Determine color based on status
        severity = data.get("severity", "success")
        color = design["colors"].get(severity, "#ffffff")

        # Create widget data
        widget_data = {
            "text": fix_later.strip(),
            "tooltip": self.create_tooltip(**data),
            "color": color,
            "command": "workbench.action.quickOpen",
            "arguments": ["LUKHAS AI ΛBot Commands"],
            "priority": 100,
            "alignment": "left",
        }

        return widget_data

    def create_tooltip(self, **data):
        """Create detailed tooltip."""
        return f"""LUKHAS AI ΛBot Quality Monitor

Status: {data.get("status", "unknown")}
Files Scanned: {data.get("files_scanned", 0)}
Violations: {data.get("violations", 0)} total
Critical: {data.get("critical", 0)}
Quality Score: {data.get("quality_score", 100)}%

Right-click for more options
Click for quick actions"""


# Example usage and design templates
if __name__ == "__main__":
    designer = LambdaBotStatusDesigner(".")

    # Example designs
    examples = {
        "minimal": designer.create_custom_status("minimal", status="monitoring", violations=0, critical=0),
        "detailed": designer.create_custom_status("detailed", status="5 issues found", violations=5, critical=1),
        "compact": designer.create_custom_status("compact", violations=3, critical=0),
        "professional": designer.create_custom_status("professional", quality_score=95, violations=2),
        "developer": designer.create_custom_status("developer", files_scanned=1250, violations=8, critical=2),
        "gaming": designer.create_custom_status("gaming", quality_level=7, critical=1, violations=4),
    }

    print("🎨 LUKHAS AI ΛBot Status Bar Design Examples:")
    print("=" * 50)

    for name, design in examples.items():
        print(fix_later)
        print(f"Color: {design['color']}")
        print(f"Tooltip: {design['tooltip'][:100]}...")

    print("\n💡 Choose your design by updating BotStatusBar.py")
