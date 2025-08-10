"""
┌────────────────────────────────────────────────────────────────────────────┐
│ 📦 MODULE      : command_registry.py                                       │
│ 🧾 DESCRIPTION : Registry of developer tools and commands for LUKHAS_AGI_3  │
│ 🧩 TYPE        : Developer Utility       🔧 VERSION: v1.0.0                 │
│ 🖋️ AUTHOR      : LUCAS SYSTEMS          📅 UPDATED: 2025-04-28              │
├────────────────────────────────────────────────────────────────────────────┤
│ 📚 DEPENDENCIES:                                                           │
│   - None (Standard Python)                                                 │
│   - Referenced by developers during CLI use                                │
└────────────────────────────────────────────────────────────────────────────┘
"""

# ==============================================================================
# 🛠 COMMAND REGISTRY
# ==============================================================================

COMMANDS = {
    "Generate Module Footer": {
        "shortcut": "Ctrl+Shift+G",
        "script": "python3 tools/gen_module_header.py",
        "description": "Creates standard doctrings and footer templates.",
    },
    "Compliance Drift Simulation": {
        "shortcut": "Ctrl+Shift+D",
        "script": "python3 tools/gen_compliance_drift_scan.py",
        "description": "Runs a simulated compliance drift event and logs outcome.",
    },
    "Audit Logger Compliance Check": {
        "shortcut": "Ctrl+Shift+A",
        "script": "python3 tools/gen_audit_logger_check.py",
        "description": "Triggers a compliance audit logger entry simulation.",
    },
    "Generate DAO Snapshot": {
        "shortcut": "Ctrl+Shift+S",
        "script": "python3 dao/init_config.py export",
        "description": "Exports current DAO configuration snapshot to logs/dao_config_snapshot.json",
    },
    "List DAO Quorum Rules": {
        "shortcut": "Ctrl+Shift+Q",
        "script": "python3 dao/init_config.py show",
        "description": "Displays current symbolic quorum, weights, and override flags.",
    },
    "Launch Public Dashboard": {
        "shortcut": "Ctrl+Shift+L",
        "script": "python3 dashboards/main.py",
        "description": "Starts the LUCAS public companion dashboard(voice, thoughts,
                                                                    visuals).",
    },
    "Trigger Audit Log (CLI)": {
        "shortcut": "Ctrl+Alt+A",
        "script": "sh tools/audit_shortcut.sh",
        "description": "Runs audit entry logger to manifest pipeline and logs result.",
    },
}

# ==============================================================================
# 🔍 USAGE: Print Available Developer Commands
# ==============================================================================


def list_commands():
    """Prints all available registered developer commands."""
    print("\n🧠 Available LUKHAS_AGI_3 Developer Commands:\n")
    for name, meta in COMMANDS.items():
        print(f"• {name}")
        print(f"    - Shortcut: {meta['shortcut']}")
        print(f"    - Script   : {meta['script']}")
        print(f"    - Info     : {meta['description']}\n")

# ==============================================================================
# 💻 CLI EXECUTION
# ==============================================================================


if __name__ == "__main__":
    list_commands()

# ============================================================================
#
# END OF FILE
