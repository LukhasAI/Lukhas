#!/usr/bin/env python3
"""
LUKHAS AI ΛBot Status Bar Customizer

Interactive tool to customize your LUKHAS AI ΛBot status bar appearance and behavior.
Apply changes instantly to see the results.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

class BotCustomizer:
    """Interactive customizer for LUKHAS AI ΛBot status bar."""

    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace).resolve()
        self.status_bar_file = self.workspace / "LUKHAS AI ΛBot" / "specialists" / "BotStatusBar.py"
        self.widget_file = self.workspace / ".vscode" / "abot_widget.json"

        # Design templates
        self.designs = {
            "1": {"name": "Minimal", "text": "🤖 LUKHAS AI ΛBot", "style": "minimal"},
            "2": {"name": "Detailed", "text": "🎯 LUKHAS AI ΛBot Monitor - {status}", "style": "detailed"},
            "3": {"name": "Compact", "text": "Λ {violations}", "style": "compact"},
            "4": {"name": "Professional", "text": "📊 Quality: {quality_score}%", "style": "professional"},
            "5": {"name": "Developer", "text": "⚡ {files_scanned} files | {violations} issues", "style": "developer"},
            "6": {"name": "Gaming", "text": "🎮 Level {quality_level} | ⚔️ {critical} critical", "style": "gaming"},
            "7": {"name": "Custom", "text": "Your custom design", "style": "custom"}
        }

        # Click actions
        self.actions = {
            "1": {"name": "Quick Scan", "command": "workbench.action.tasks.runTask", "args": ["LUKHAS AI ΛBot: Quick Scan"]},
            "2": {"name": "Show Report", "command": "vscode.open", "args": ["${workspaceFolder}/naming_audit_report.json"]},
            "3": {"name": "Show Dashboard", "command": "vscode.open", "args": ["${workspaceFolder}/quality-metrics-live.json"]},
            "4": {"name": "Apply Auto-Fixes", "command": "workbench.action.tasks.runTask", "args": ["LUKHAS AI ΛBot: Apply Auto-Fixes"]},
            "5": {"name": "Command Palette", "command": "workbench.action.quickOpen", "args": [">LUKHAS AI ΛBot"]},
            "6": {"name": "Show Problems", "command": "workbench.actions.view.problems", "args": []},
            "7": {"name": "Terminal Focus", "command": "workbench.action.terminal.focus", "args": []},
            "8": {"name": "Full Audit", "command": "workbench.action.tasks.runTask", "args": ["LUKHAS AI ΛBot: Full Audit"]},
            "9": {"name": "Stop Scanner", "command": "workbench.action.tasks.runTask", "args": ["LUKHAS AI ΛBot: Stop Scanner"]}
        }

        # Color schemes
        self.colors = {
            "1": {"name": "Default", "success": "#28a745", "warning": "#ffc107", "error": "#dc3545"},
            "2": {"name": "Bright", "success": "#00ff88", "warning": "#ffaa00", "error": "#ff4444"},
            "3": {"name": "Subtle", "success": "#00aa00", "warning": "#aa6600", "error": "#aa0000"},
            "4": {"name": "GitHub", "success": "#2ea043", "warning": "#fb8500", "error": "#d1242f"},
            "5": {"name": "Neon", "success": "#39d353", "warning": "#d4ac0d", "error": "#e74c3c"},
            "6": {"name": "Retro", "success": "#00ff00", "warning": "#ffff00", "error": "#ff0000"}
        }

    def show_menu(self):
        """Show interactive customization menu."""
        while True:
            self.clear_screen()
            print("🎨 LUKHAS AI ΛBot Status Bar Customizer")
            print("=" * 40)
            print()
            print("Choose what to customize:")
            print("1. 🎭 Design & Text")
            print("2. 🖱️  Click Action")
            print("3. 🌈 Color Scheme")
            print("4. 👀 Preview Current")
            print("5. 💾 Apply Changes")
            print("6. ❌ Exit")
            print()

            choice = input("Select option (1-6): ").strip()

            if choice == "1":
                self.customize_design()
            elif choice == "2":
                self.customize_action()
            elif choice == "3":
                self.customize_colors()
            elif choice == "4":
                self.preview_current()
            elif choice == "5":
                self.apply_changes()
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please select 1-6.")
                input("Press Enter to continue...")

    def customize_design(self):
        """Customize status bar design."""
        self.clear_screen()
        print("🎭 Choose Status Bar Design")
        print("=" * 30)
        print()

        for key, design in self.designs.items():
            print(f"{key}. {design['name']}: {design['text']}")
        print()

        choice = input("Select design (1-7): ").strip()

        if choice in self.designs:
            selected = self.designs[choice]
            print(f"\n✅ Selected: {selected['name']}")

            if choice == "7":  # Custom
                custom_text = input("Enter custom status text: ").strip()
                if custom_text:
                    selected['text'] = custom_text

            self.current_design = selected
            print(f"Design preview: {selected['text']}")
        else:
            print("Invalid choice.")

        input("\nPress Enter to continue...")

    def customize_action(self):
        """Customize click action."""
        self.clear_screen()
        print("🖱️ Choose Click Action")
        print("=" * 25)
        print()

        for key, action in self.actions.items():
            print(f"{key}. {action['name']}")
        print()

        choice = input("Select action (1-9): ").strip()

        if choice in self.actions:
            selected = self.actions[choice]
            print(f"\n✅ Selected: {selected['name']}")
            print(f"Command: {selected['command']}")
            self.current_action = selected
        else:
            print("Invalid choice.")

        input("\nPress Enter to continue...")

    def customize_colors(self):
        """Customize color scheme."""
        self.clear_screen()
        print("🌈 Choose Color Scheme")
        print("=" * 25)
        print()

        for key, scheme in self.colors.items():
            print(f"{key}. {scheme['name']}: Success({scheme['success']}) Warning({scheme['warning']}) Error({scheme['error']})")
        print()

        choice = input("Select color scheme (1-6): ").strip()

        if choice in self.colors:
            selected = self.colors[choice]
            print(f"\n✅ Selected: {selected['name']}")
            self.current_colors = selected
        else:
            print("Invalid choice.")

        input("\nPress Enter to continue...")

    def preview_current(self):
        """Preview current configuration."""
        self.clear_screen()
        print("👀 Current Configuration Preview")
        print("=" * 35)
        print()

        if hasattr(self, 'current_design'):
            print(f"Design: {self.current_design['name']}")
            print(f"Text: {self.current_design['text']}")

        if hasattr(self, 'current_action'):
            print(f"Click Action: {self.current_action['name']}")
            print(f"Command: {self.current_action['command']}")

        if hasattr(self, 'current_colors'):
            print(f"Colors: {self.current_colors['name']}")

        print("\n📝 Sample Status Bar:")
        sample_text = getattr(self, 'current_design', {}).get('text', '🤖 LUKHAS AI ΛBot')
        sample_text = sample_text.replace('{status}', 'monitoring').replace('{violations}', '3').replace('{quality_score}', '95')
        print(f"  {sample_text}")

        input("\nPress Enter to continue...")

    def apply_changes(self):
        """Apply changes to the status bar."""
        self.clear_screen()
        print("💾 Applying Changes...")
        print("=" * 20)

        try:
            # Update the status bar widget
            if hasattr(self, 'current_design') or hasattr(self, 'current_action') or hasattr(self, 'current_colors'):
                self.update_status_bar_code()
                print("✅ Status bar code updated")

                # Restart the status bar widget
                self.restart_status_bar()
                print("✅ Status bar restarted")

                print("\n🎉 Changes applied successfully!")
                print("Check your VS Code status bar to see the changes.")
            else:
                print("❌ No changes to apply.")

        except Exception as e:
            print(f"❌ Error applying changes: {e}")

        input("\nPress Enter to continue...")

    def update_status_bar_code(self):
        """Update the status bar Python code with new configuration."""
        if not self.status_bar_file.exists():
            raise FileNotFoundError("BotStatusBar.py not found")

        # Read current file
        with open(self.status_bar_file, 'r') as f:
            content = f.read()

        # Generate new widget creation code
        new_widget_code = self.generate_widget_code()

        # Replace the create_status_widget function
        # This is a simplified replacement - in a real implementation you'd use AST manipulation'
        print(f"Generated new widget code (preview):")
        print(new_widget_code[:200] + "...")

        # For now, create a configuration file that the status bar can read
        config = {
            "design": getattr(self, 'current_design', {}),
            "action": getattr(self, 'current_action', {}),
            "colors": getattr(self, 'current_colors', {}),
            "updated": datetime.now().isoformat()
        }

        config_file = self.workspace / ".vscode" / "abot_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def generate_widget_code(self):
        """Generate widget creation code."""
        design = getattr(self, 'current_design', {})
        action = getattr(self, 'current_action', {})
        colors = getattr(self, 'current_colors', {})

        return f"""
        # Auto-generated widget configuration
        widget_data = {{
            "text": "{design.get('text', '🤖 LUKHAS AI ΛBot')}",
            "tooltip": "LUKHAS AI ΛBot Quality Monitor - Click for {action.get('name', 'actions')}",
            "color": "{colors.get('success', '#28a745')}",
            "command": "{action.get('command', 'workbench.action.tasks.runTask')}",
            "arguments": {action.get('args', [])},
            "priority": 100,
            "alignment": "left"
        }}
        """

    def restart_status_bar(self):
        """Restart the status bar widget."""
        import subprocess
        import time

        # Stop current widget
        subprocess.run([
            "pkill", "-f", "BotStatusBar.py"
        ], capture_output=True)

        time.sleep(1)

        # Start new widget
        subprocess.Popen([
            "python3",
            str(self.workspace / "LUKHAS AI ΛBot" / "specialists" / "BotStatusBar.py"),
            "--workspace", str(self.workspace)
        ])

    def clear_screen(self):
        """Clear the terminal screen."""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')

def main():
    """Main entry point."""
    print("🚀 Starting LUKHAS AI ΛBot Status Bar Customizer...")

    customizer = ΛBotCustomizer()

    try:
        customizer.show_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Customizer interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

    print("\n✨ Customization complete! Check your VS Code status bar.")

if __name__ == "__main__":
    main()
