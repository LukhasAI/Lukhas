#!/usr/bin/env python3
"""
LUKHAS AI ΛBot Click Actions Configuration

Configure what happens when you click on the LUKHAS AI ΛBot status bar.
Multiple action types and combinations available.
"""


class BotClickActions:
    """Configure status bar click actions."""

    def __init__(self):
        self.action_templates = {
            # === SINGLE CLICK ACTIONS ===
            "quick_scan": {
                "command": "workbench.action.tasks.runTask",
                "arguments": ["LUKHAS AI ΛBot: Quick Scan"],
                "description": "Run immediate quality scan",
            },
            "show_report": {
                "command": "vscode.open",
                "arguments": ["${workspaceFolder}/naming_audit_report.json"],
                "description": "Open detailed quality report",
            },
            "show_status": {
                "command": "workbench.action.tasks.runTask",
                "arguments": ["LUKHAS AI ΛBot: Status Check"],
                "description": "Show current status in terminal",
            },
            "open_dashboard": {
                "command": "vscode.open",
                "arguments": ["${workspaceFolder}/quality-metrics-live.json"],
                "description": "Open live quality dashboard",
            },
            "apply_fixes": {
                "command": "workbench.action.tasks.runTask",
                "arguments": ["LUKHAS AI ΛBot: Apply Auto-Fixes"],
                "description": "Apply automatic fixes",
            },
            "command_palette": {
                "command": "workbench.action.quickOpen",
                "arguments": [">LUKHAS AI ΛBot"],
                "description": "Open LUKHAS AI ΛBot command palette",
            },
            "show_problems": {
                "command": "workbench.actions.view.problems",
                "description": "Show VS Code problems panel",
            },
            "terminal_focus": {
                "command": "workbench.action.terminal.focus",
                "description": "Focus on terminal",
            },
            # === CONTEXT MENU ACTIONS ===
            "context_menu": {
                "command": "extension.LUKHAS AI ΛBot.showContextMenu",
                "description": "Show LUKHAS AI ΛBot context menu with multiple options",
            },
            # === CUSTOM COMMANDS ===
            "full_audit": {
                "command": "workbench.action.tasks.runTask",
                "arguments": ["LUKHAS AI ΛBot: Full Audit"],
                "description": "Run comprehensive audit",
            },
            "start_scanner": {
                "command": "workbench.action.tasks.runTask",
                "arguments": ["LUKHAS AI ΛBot: Start Continuous Scanner"],
                "description": "Start continuous monitoring",
            },
            "stop_scanner": {
                "command": "workbench.action.tasks.runTask",
                "arguments": ["LUKHAS AI ΛBot: Stop Scanner"],
                "description": "Stop continuous monitoring",
            },
        }

        # Multi-action configurations
        self.multi_actions = {
            "scan_and_report": [
                {"action": "quick_scan", "delay": 0},
                {"action": "show_report", "delay": 3000},
            ],
            "fix_and_scan": [
                {"action": "apply_fixes", "delay": 0},
                {"action": "quick_scan", "delay": 2000},
            ],
        }

    def get_action_config(self, action_name: str):
        """Get configuration for specific action."""
        return self.action_templates.get(action_name, {})

    def create_context_menu_config(self):
        """Create context menu with multiple options."""
        return {
            "command": "extension.LUKHAS AI ΛBot.showMenu",
            "when": "true",
            "menu_items": [
                {
                    "label": "🔍 Quick Scan",
                    "command": "workbench.action.tasks.runTask",
                    "arguments": ["LUKHAS AI ΛBot: Quick Scan"],
                },
                {
                    "label": "📊 Show Report",
                    "command": "vscode.open",
                    "arguments": ["${workspaceFolder}/naming_audit_report.json"],
                },
                {
                    "label": "🔧 Apply Auto-Fixes",
                    "command": "workbench.action.tasks.runTask",
                    "arguments": ["LUKHAS AI ΛBot: Apply Auto-Fixes"],
                },
                {
                    "label": "⚙️ Settings",
                    "command": "workbench.action.openSettings",
                    "arguments": ["LUKHAS AI ΛBot"],
                },
                {
                    "label": "🛑 Stop Scanner",
                    "command": "workbench.action.tasks.runTask",
                    "arguments": ["LUKHAS AI ΛBot: Stop Scanner"],
                },
            ],
        }

    def print_all_options(self):
        """Print all available click action options."""
        print("🎯 LUKHAS AI ΛBot Status Bar Click Actions")
        print("=" * 50)

        print("\n📱 SINGLE CLICK ACTIONS:")
        for name, config in self.action_templates.items():
            print(f"  {name}: {config['description']}")

        print("\n🔄 MULTI-ACTION SEQUENCES:")
        for name, actions in self.multi_actions.items():
            print(f"  {name}: {len(actions)} sequential actions")

        print("\n📋 CONTEXT MENU OPTIONS:")
        menu_config = self.create_context_menu_config()
        for item in menu_config["menu_items"]:
            print(f"  {item['label']}")


# Usage examples
if __name__ == "__main__":
    actions = ΛBotClickActions()
    actions.print_all_options()

    print("\n💡 CUSTOMIZATION EXAMPLES:")
    print("=" * 30)

    examples = [
        ("Developer Workflow", "quick_scan → show_report"),
        ("Auto-Fix Mode", "apply_fixes → quick_scan"),
        ("Dashboard View", "open_dashboard"),
        ("Command Center", "command_palette"),
        ("Context Menu", "Right-click for multiple options"),
    ]

    for title, desc in examples:
        print(f"  {title}: {desc}")

    print("\n🔧 To customize:")
    print("  1. Edit BotStatusBar.py")
    print("  2. Choose action from above list")
    print("  3. Update widget_data['command']")
    print("  4. Restart LUKHAS AI ΛBot scanner")
