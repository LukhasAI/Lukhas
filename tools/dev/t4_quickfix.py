#!/usr/bin/env python3
"""
T4 QuickFix: Cursor-aware LLM-powered quick fix generation for TODO[T4-AUTOFIX] markers.

This script provides interactive patch generation for TODO markers using LLM assistance,
with built-in safety features including policy validation, timeout handling, and fallback stubs.
"""

import argparse
import fnmatch
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import tomli as tomllib


def load_t4_config() -> dict:
    """Load T4 autofix configuration from .t4autofix.toml."""
    config_path = Path(".t4autofix.toml")
    if not config_path.exists():
        print("❌ .t4autofix.toml not found. Run from repository root.")
        sys.exit(1)

    with open(config_path, "rb") as f:
        return tomllib.load(f)


def run(cmd: list[str], input: str = None, timeout: int = None) -> str:
    """Run subprocess command with optional input and timeout."""
    result = subprocess.run(
        cmd, input=input, text=True, capture_output=True, timeout=timeout
    )
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
    return result.stdout.strip()


def call_ollama(prompt: str, model: str = None) -> str:
    """Call Ollama LLM with timeout and fallback handling."""
    model = model or os.environ.get("T4_LLM_MODEL", "deepseek-coder")
    timeout = int(os.environ.get("T4_LLM_TIMEOUT", "30"))

    try:
        return run(["ollama", "run", model], input=prompt, timeout=timeout)
    except Exception as e:
        # Generate fallback stub patch
        return f"""--- a/STUB
+++ b/STUB
# Quickfix stub: ollama model unavailable or timed out
# Error: {e}
# Original prompt (truncated):
# {prompt[:200]}
"""


def extract_todo_at_line(file_path: str, line_num: int) -> Optional[dict]:
    """Extract TODO[T4-AUTOFIX] marker at specified line."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        if line_num < 1 or line_num > len(lines):
            return None

        line = lines[line_num - 1].strip()
        if "TODO[T4-AUTOFIX]" not in line:
            return None

        # Extract TODO message
        todo_start = line.find("TODO[T4-AUTOFIX]")
        todo_msg = line[todo_start + len("TODO[T4-AUTOFIX]:") :].strip()
        if todo_msg.startswith(":"):
            todo_msg = todo_msg[1:].strip()

        return {"line": line_num, "message": todo_msg, "full_line": line}
    except Exception:
        return None


def get_context_lines(file_path: str, line_num: int, context: int = 30) -> str:
    """Get context lines around the TODO marker."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)

        context_lines = []
        for i in range(start, end):
            marker = " >>> " if i == line_num - 1 else "     "
            context_lines.append(f"{i+1:4d}{marker}{lines[i].rstrip(}")

        return "\n".join(context_lines)
    except Exception:
        return "Error reading file context"


def validate_policy_compliance(file_path: str, config: dict) -> bool:
    """Check if file path passes T4 policy allow/deny filters using glob patterns."""
    scope = config.get("scope", {})
    allow_patterns = scope.get("allow_patterns", [])
    deny_patterns = scope.get("deny_patterns", [])

    # Check deny patterns first
    for pattern in deny_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return False

    # Check allow patterns if specified
    if allow_patterns:
        return any(
            fnmatch.fnmatch(file_path, pattern) for pattern in allow_patterns
        # No allow pattern matched

    return True  # No allow patterns specified, just avoid deny patterns


def generate_patch_prompt(
    file_path: str, todo: dict, context: str, config: dict
) -> str:
    """Generate LLM prompt for patch creation."""
    rules = config.get("rules", {})
    allowlist_codes = ", ".join(rules.get("allowlist", []))

    return f"""You are a code assistant generating a unified diff patch to fix this TODO.

FILE: {file_path}
TODO: {todo['message']}
LINE: {todo['line']}

CONTEXT (±30 lines):
```
{context}
```

INSTRUCTIONS:
1. Generate a unified diff patch that addresses the TODO
2. Follow T4 autofix allowlist: {allowlist_codes}
3. Keep changes minimal and safe
4. Ensure proper syntax and indentation
5. Remove the TODO comment when fixed

OUTPUT FORMAT:
--- a/{file_path}
+++ b/{file_path}
@@ -X,Y +A,B @@
 context line
-old line
+new line
 context line
"""


def write_patch(file_path: str, line_num: int, patch_content: str) -> Path:
    """Write patch content to temporary file."""
    filename = f"t4_quickfix_{Path(file_path}.stem}_L{line_num}.patch"
    patch_path = Path(tempfile.gettempdir()) / filename

    with open(patch_path, "w", encoding="utf-8") as f:
        f.write(patch_content)

    return patch_path


def apply_patch(patch_path: Path, dry_run: bool = False) -> bool:
    """Apply patch using git apply with safety checks."""
    try:
        cmd = ["git", "apply", "--check"]
        if not dry_run:
            cmd.remove("--check")
        cmd.append(str(patch_path))

        run(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def run_tests(file_path: str = None) -> bool:
    """Run basic tests to validate changes."""
    try:
        # Try syntax check first
        if file_path and file_path.endswith(".py"):
            run(["python3", "-m", "py_compile", file_path])

        # Run quick linting if available
        try:
            run(["ruff", "check", file_path or "."], timeout=10)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass  # ruff not available or issues found, continue

        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="T4 QuickFix: Generate LLM-powered patches for TODO[T4-AUTOFIX] markers"
    )
    parser.add_argument("--file", required=True, help="File containing TODO marker")
    parser.add_argument(
        "--line", type=int, required=True, help="Line number of TODO marker"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply the patch immediately"
    )
    parser.add_argument(
        "--open", action="store_true", help="Open generated patch in VS Code"
    )
    parser.add_argument("--model", help="LLM model to use (default: deepseek-coder)")

    args = parser.parse_args()

    # Load T4 configuration
    try:
        config = load_t4_config()
        print("✅ T4 config loaded")
    except Exception as e:
        print(f"❌ Failed to load T4 config: {e}")
        sys.exit(1)

    # Validate policy compliance
    if not validate_policy_compliance(args.file, config):
        print(f"❌ File {args.file} not allowed by T4 policy")
        sys.exit(1)

    print("✅ Policy validation passed")

    # Extract TODO at specified line
    todo = extract_todo_at_line(args.file, args.line)
    if not todo:
        print(f"❌ No TODO[T4-AUTOFIX] found at {args.file}:{args.line}")
        sys.exit(1)

    print(f"🎯 Found TODO: {todo['message']}")

    # Get context around the TODO
    context = get_context_lines(args.file, args.line)

    # Generate LLM prompt
    prompt = generate_patch_prompt(args.file, todo, context, config)

    # Call LLM to generate patch
    print("🤖 Generating patch with LLM...")
    patch = call_ollama(prompt, args.model)

    # Add LLM provenance header
    args.model or os.environ.get("T4_LLM_MODEL", "deepseek-coder")
    int(os.environ.get("T4_LLM_TIMEOUT", "30"))
    prov = ""
    if patch.startswith("--- a/"):
        patch = prov + patch
    else:
        patch = prov + "# Non-standard patch payload below\n" + patch

    # Check if we got a stub (fallback)
    if "Quickfix stub:" in patch:
        print("⚠️  LLM unavailable or timed out, generated stub patch")

    # Write patch to file
    relpath = os.path.relpath(args.file)
    patch_path = write_patch(relpath, todo["line"], patch)

    # Open patch if requested
    if args.open:
        try:
            subprocess.check_call(["code", "-g", str(patch_path)])
            print(f"📂 Opened patch in VS Code: {patch_path}")
        except Exception:
            print(
                f"📝 Patch ready at: {patch_path} (install 'code' command to open automatically)"
            )
    else:
        print(f"📝 Patch written to: {patch_path}")

    # Apply patch if requested
    if args.apply:
        print("🔍 Validating patch...")
        if not apply_patch(patch_path, dry_run=True):
            print("❌ Patch validation failed")
            sys.exit(1)

        print("✅ Applying patch...")
        if not apply_patch(patch_path, dry_run=False):
            print("❌ Patch application failed")
            sys.exit(1)

        # Run basic tests
        print("🧪 Running validation tests...")
        if not run_tests(args.file):
            print("⚠️  Tests failed, reverting changes...")
            run(["git", "checkout", "HEAD", "--", args.file])
            print("🔄 Changes reverted")
            sys.exit(1)

        print("✅ Patch applied successfully!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
