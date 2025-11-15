#!/usr/bin/env python3
"""
Batch fix shell injection vulnerabilities in remaining files.
"""
import re
from pathlib import Path

# List of files to fix (excluding those already fixed)
FILES_TO_FIX = [
    "branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_cli.py",
    "branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_customizer.py",
    "bridge/api/validation.py",
    "labs/memory/temporal/secure_utils.py",
    "scripts/check_autonomous_guides_patch_status.py",
    "scripts/high_risk_patterns.py",
    "scripts/run_full_audit.py",
    "scripts/todo_migration/assign_from_mapping.py",
    "scripts/example_integration.py",
    "scripts/fixes/cascade_crusher.py",
    "scripts/fixes/rapid_cascade_chaser.py",
    "tools/analysis/git_clean_file_hunter.py",
    "tools/analysis/lambda_identity_audit.py",
    "tools/analysis/mass_restoration_script.py",
    "tools/analysis/ml_integration_analyzer.py",
    "tools/audit/mk_delta_appendix.py",
    "tools/batch_cockpit.py",
    "tools/burst_cockpit.py",
    "tools/dashboard_bot.py",
    "tools/guard_patch.py",
    "tools/ml_integration_analyzer.py",
    "tools/module_manifest_upgrade.py",
    "tools/scripts/system_status_reporter.py",
]

ROOT = Path("/home/user/Lukhas")


def fix_file(file_path: Path):
    """Fix shell injection vulnerabilities in a file."""
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False

    content = file_path.read_text()
    original_content = content
    modified = False

    # Check if import is already present
    has_import = "from lukhas.security.safe_subprocess import safe_run_command" in content

    # Add import if not present
    if not has_import and ("os.system" in content or 'shell=True' in content):
        # Find the last import statement
        import_match = None
        for match in re.finditer(r'^(from .+ import .+|import .+)$', content, re.MULTILINE):
            import_match = match

        if import_match:
            # Insert after the last import
            insert_pos = import_match.end()
            content = content[:insert_pos] + "\n\nfrom lukhas.security.safe_subprocess import safe_run_command" + content[insert_pos:]
            modified = True

    # Fix subprocess.run with shell=True
    # Pattern 1: subprocess.run("cmd", shell=True, ...)
    pattern1 = r'subprocess\.run\(\s*["\']([^"\']+)["\']\s*,\s*shell=True'
    def repl1(m):
        cmd = m.group(1)
        return f'safe_run_command("{cmd}"'

    new_content = re.sub(pattern1, repl1, content)
    if new_content != content:
        content = new_content
        modified = True

    # Pattern 2: subprocess.run(f"...", shell=True)
    pattern2 = r'subprocess\.run\(\s*f["\']([^"\']+)["\']\s*,\s*shell=True'
    def repl2(m):
        cmd = m.group(1)
        return f'safe_run_command(f"{cmd}"'

    new_content = re.sub(pattern2, repl2, content)
    if new_content != content:
        content = new_content
        modified = True

    # Pattern 3: subprocess.check_output("cmd", shell=True)
    pattern3 = r'subprocess\.check_output\(\s*["\']([^"\']+)["\']\s*,\s*shell=True'
    def repl3(m):
        cmd = m.group(1)
        return f'safe_run_command("{cmd}", check=True'

    new_content = re.sub(pattern3, repl3, content)
    if new_content != content:
        content = new_content
        modified = True

    # Pattern 4: subprocess.check_output(f"...", shell=True)
    pattern4 = r'subprocess\.check_output\(\s*f["\']([^"\']+)["\']\s*,\s*shell=True'
    def repl4(m):
        cmd = m.group(1)
        return f'safe_run_command(f"{cmd}", check=True'

    new_content = re.sub(pattern4, repl4, content)
    if new_content != content:
        content = new_content
        modified = True

    # Fix os.system calls - these need manual review as they might need list form
    # For now, just add a comment to review
    pattern_os = r'os\.system\(\s*["\']([^"\']+)["\']\s*\)'
    if re.search(pattern_os, content):
        print(f"⚠️  {file_path}: Contains os.system calls that need manual review")

    if modified and content != original_content:
        file_path.write_text(content)
        print(f"✅ Fixed: {file_path}")
        return True
    else:
        print(f"ℹ️  No changes: {file_path}")
        return False


def main():
    print("🔧 Batch fixing shell injection vulnerabilities...")
    fixed_count = 0
    for file_rel in FILES_TO_FIX:
        file_path = ROOT / file_rel
        if fix_file(file_path):
            fixed_count += 1

    print(f"\n✨ Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
