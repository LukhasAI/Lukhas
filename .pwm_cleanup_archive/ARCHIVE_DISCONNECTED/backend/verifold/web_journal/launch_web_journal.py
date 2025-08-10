#!/usr/bin/env python3
"""
launch_web_journal.py

Quick launcher for VeriFold Web Journal.
Handles dependency checking and provides easy startup.

Usage:
    python3 launch_web_journal.py
    python3 launch_web_journal.py --port 8080
    python3 launch_web_journal.py --host 0.0.0.0 --port 5001 --debug
"""

import sys
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ["flask", "flask_socketio"]
    missing = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print("❌ Missing required packages:", ", ".join(missing))
        print("📦 Install with: pip install flask flask-socketio")
        print("   Or use: pip install -r web_journal_requirements.txt")
        return False

    return True


def main():
    print("🚀 VeriFold Web Journal Launcher")
    print("=" * 40)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check if journal_mode.py exists
    journal_file = Path("../journal_mode.py")
    if not journal_file.exists():
        print("⚠️ Warning: journal_mode.py not found in parent directory")
        print("   Some features may not work correctly")

    # Launch the web journal
    print("🌐 Starting VeriFold Web Journal...")
    print("📱 Interface will be available at: http://localhost:5001")
    print("🔮 Features:")
    print("   • Real-time quantum narrative updates")
    print("   • Interactive emotion-colored glyphs")
    print("   • GPT-4 powered symbolic summaries")
    print("   • Responsive quantum-themed design")
    print("\n🎯 Press Ctrl+C to stop the server")
    print("=" * 40)

    try:
        # Import and run the web journal
        from web_journal_app import main as run_web_journal

        run_web_journal()
    except KeyboardInterrupt:
        print("\n🛑 Web Journal stopped by user")
    except Exception as e:
        print(f"❌ Error starting Web Journal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
