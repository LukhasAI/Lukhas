#!/usr/bin/env python3
"""
Final comprehensive fix for all remaining shell injection vulnerabilities.
"""
import re
from pathlib import Path

ROOT = Path("/home/user/Lukhas")

# Files that still have issues
MANUAL_FIXES = {
    "tools/batch_cockpit.py": [
        (r'result = subprocess\.run\(cmd, shell=True,', 'result = safe_run_command(cmd,'),
    ],
    "tools/dashboard_bot.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "tools/module_manifest_upgrade.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "tools/burst_cockpit.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "tools/analysis/git_clean_file_hunter.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "tools/analysis/mass_restoration_script.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "tools/scripts/system_status_reporter.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "scripts/run_full_audit.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "scripts/high_risk_patterns.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
        (r'os\.system\(f"', 'safe_run_command(f"'),
    ],
    "scripts/todo_migration/assign_from_mapping.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_cli.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "labs/memory/temporal/secure_utils.py": [
        (r'subprocess\.run\(cmd, shell=True,', 'safe_run_command(cmd,'),
    ],
    "branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_customizer.py": [
        (r'os\.system\(f"clear"\)', 'safe_run_command(["clear"], check=False)'),
        (r'os\.system\("clear"\)', 'safe_run_command(["clear"], check=False)'),
    ],
    "tools/ml_integration_analyzer.py": [
        (r'os\.system\(f"', 'safe_run_command(f"'),
    ],
    "tools/analysis/ml_integration_analyzer.py": [
        (r'os\.system\(f"', 'safe_run_command(f"'),
    ],
    "scripts/example_integration.py": [
        (r'os\.system\("', 'safe_run_command("'),
    ],
    "scripts/fixes/cascade_crusher.py": [
        (r'os\.system\("python3 functional_test_suite\.py"\)', 'safe_run_command(["python3", "functional_test_suite.py"], check=False)'),
    ],
    "scripts/fixes/rapid_cascade_chaser.py": [
        (r'os\.system\(f"python3 {file}"\)', 'safe_run_command(["python3", file], check=False)'),
        (r'os\.system\("python3 functional_test_suite\.py"\)', 'safe_run_command(["python3", "functional_test_suite.py"], check=False)'),
    ],
}


def fix_file(file_path: Path, replacements):
    """Apply manual fixes to a file."""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False

    content = file_path.read_text()
    original_content = content

    # Add import if not present
    if "from lukhas.security.safe_subprocess import safe_run_command" not in content:
        # Find last import
        import_match = None
        for match in re.finditer(r'^(from .+ import .+|import .+)$', content, re.MULTILINE):
            import_match = match

        if import_match:
            insert_pos = import_match.end()
            content = content[:insert_pos] + "\n\nfrom lukhas.security.safe_subprocess import safe_run_command" + content[insert_pos:]

    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        file_path.write_text(content)
        print(f"✅ Fixed: {file_path}")
        return True
    else:
        print(f"ℹ️  No changes: {file_path}")
        return False


def main():
    print("🔧 Applying final shell injection fixes...")
    fixed_count = 0

    for file_rel, replacements in MANUAL_FIXES.items():
        file_path = ROOT / file_rel
        if fix_file(file_path, replacements):
            fixed_count += 1

    print(f"\n✨ Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
