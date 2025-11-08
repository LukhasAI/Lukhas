#!/usr/bin/env python3
"""
Pre-commit hook: Matrix Tracks Demo Script Validation

Validates demo scripts are executable and syntactically correct.
Provides fast feedback on demo script quality before commit.
"""

import pathlib
import stat
import subprocess
import sys
def validate_demo_script(script_path: str) -> list[str]:
    """Validate a demo script for common issues."""
    errors = []
    script_file = pathlib.Path(script_path)

    try:
        # Check file exists
        if not script_file.exists():
            errors.append("Script file not found")
            return errors

        # Check file is executable
        file_stat = script_file.stat()
        if not (file_stat.st_mode & stat.S_IXUSR):
            errors.append("Script is not executable (missing +x permission)")

        # Check shebang
        with open(script_file) as f:
            first_line = f.readline().strip()

        if not first_line.startswith('#!/'):
            errors.append("Missing shebang line")
        elif 'bash' not in first_line and 'sh' not in first_line:
            errors.append("Shebang should use bash or sh")

        # Basic syntax check with bash -n
        try:
            result = subprocess.run(
                ['bash', '-n', script_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                errors.append(f"Bash syntax error: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            errors.append("Syntax check timed out")
        except FileNotFoundError:
            errors.append("bash not available for syntax check")

        # Check for common anti-patterns
        with open(script_file) as f:
            content = f.read()

        # Check for set -e (fail fast)
        if 'set -e' not in content:
            errors.append("Consider adding 'set -e' for fail-fast behavior")

        # Check for hardcoded paths that might not work in CI
        suspicious_paths = ['/usr/local/', '/home/', '~/', '/Users/']
        for line_num, line in enumerate(content.split('\n'), 1):
            for path in suspicious_paths:
                if path in line and not line.strip().startswith('#'):
                    errors.append(f"Line {line_num}: Suspicious hardcoded path: {path}")

        # Check for missing error handling on critical commands
        critical_commands = ['python3', 'make', 'docker', 'git']
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if (any(cmd in line for cmd in critical_commands) and (not line.startswith('#'))) and ('|| ' not in line and 'set -e' not in content):
                # Check if command has error handling (|| true, or next line handles error)
                next_line = lines[line_num] if line_num < len(lines) else ""
                if not ('if' in next_line or 'echo' in line):
                    # This is just a warning, not an error
                    pass

        # Check for demo-specific requirements
        if 'matrix_tracks' in script_path:
            # Demo should have descriptive output
            if 'echo' not in content:
                errors.append("Demo script should have descriptive echo statements for user feedback")

            # Demo should handle tool availability gracefully
            tools = ['prism', 'ipfs', 'osv-scanner']
            for tool in tools:
                if tool in content and 'command -v' not in content:
                    errors.append(f"Demo uses {tool} but doesn't check availability with 'command -v'")

    except Exception as e:
        errors.append(f"Validation error: {e}")

    return errors


def main():
    """Main pre-commit hook entry point."""
    if len(sys.argv) < 2:
        print("Usage: pre_commit_demo_lint.py <script_file> [<script_file>...]", file=sys.stderr)
        sys.exit(1)

    script_files = sys.argv[1:]
    total_errors = 0
    total_warnings = 0

    print(f"🧪 Validating {len(script_files)} demo script(s)...")

    for script_path in script_files:
        errors = validate_demo_script(script_path)

        # Separate errors from warnings
        real_errors = [e for e in errors if not e.startswith("Consider") and "should have" not in e]
        warnings = [e for e in errors if e.startswith("Consider") or "should have" in e]

        if real_errors:
            print(f"❌ {script_path}:")
            for error in real_errors:
                print(f"   {error}")
            total_errors += len(real_errors)

        if warnings:
            print(f"⚠️ {script_path}:")
            for warning in warnings:
                print(f"   {warning}")
            total_warnings += len(warnings)

        if not errors:
            print(f"✅ {script_path}")

    if total_errors > 0:
        print(f"\n❌ Found {total_errors} error(s) in demo scripts")
        print("Fix these errors before committing to ensure demo quality")
        sys.exit(1)
    elif total_warnings > 0:
        print(f"\n⚠️ Found {total_warnings} warning(s) in demo scripts")
        print("Consider addressing these warnings to improve demo experience")
    else:
        print("\n✅ All demo scripts look good")


if __name__ == "__main__":
    main()
