#!/usr/bin/env python3
"""
🔧 Simple LUKHAS Code Quality Fixer
===================================

A simplified version that uses local LLM + Ruff to fix code issues systematically.
Focuses on the most critical issues first with safe, automated fixes.
"""

import json
import os
import subprocess
from pathlib import Path

import requests


class SimpleLLMCodeFixer:
    """Simplified version of LLM code fixer"""

    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.ollama_url = "http://localhost:11434"
        self.model = "deepseek-coder:6.7b"

    def check_ollama_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def get_ruff_issues(self, limit: int = 20) -> list:
        """Get limited set of Ruff issues for processing"""

        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--output-format=json", "--no-fix"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.stdout:
                issues = json.loads(result.stdout)
                # Focus on syntax errors first (E9, F9 codes)
                critical_issues = [
                    issue
                    for issue in issues
                    if issue.get("code", "").startswith(("E9", "F9"))
                ][:limit]

                if not critical_issues:
                    # If no critical, take other high-priority issues
                    return issues[:limit]

                return critical_issues

            return []

        except Exception as e:
            print(f"❌ Failed to get Ruff issues: {e}")
            return []

    def fix_issue_with_llm(self, issue: dict) -> str:
        """Get fix suggestion from LLM"""

        file_path = issue.get("filename", "")
        line_num = issue.get("location", {}).get("row", 0)
        message = issue.get("message", "")
        code = issue.get("code", "")

        # Read file content for context
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Get context around the error line
            start_line = max(0, line_num - 5)
            end_line = min(len(lines), line_num + 5)
            context_lines = lines[start_line:end_line]

            # Build simple prompt
            prompt = f"""Fix this Python code issue:

File: {file_path}
Line: {line_num}
Error: {code} - {message}

Code context:
{''.join(f'{start_line + i + 1}: {line}' for i, line in enumerate(context_lines))}

Provide ONLY the corrected line {line_num}, nothing else:"""

            # Call Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 200},
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                fix_suggestion = result.get("response", "").strip()

                # Clean up the response
                if fix_suggestion:
                    # Remove line numbers and common prefixes
                    fix_suggestion = fix_suggestion.replace(f"{line_num}:", "").strip()
                    if fix_suggestion.startswith(f"{line_num}"):
                        fix_suggestion = fix_suggestion[len(str(line_num)) :].strip()

                    return fix_suggestion

            return ""

        except Exception as e:
            print(f"   ⚠️  LLM fix failed: {e}")
            return ""

    def run_simple_fixes(self, dry_run: bool = True):
        """Run simple automated fixes"""

        print("🧠 LUKHAS Simple Code Quality Fixer")
        print("=" * 40)
        print(f"📂 Project: {self.project_root}")
        print(f"🧪 Dry Run: {'Enabled' if dry_run else 'Disabled'}")

        # Check Ollama
        if not self.check_ollama_available():
            print("❌ Ollama not available. Using Ruff auto-fix only.")
            self.run_ruff_autofix()
            return

        print(f"✅ Ollama available with model: {self.model}")

        # Get issues to fix
        issues = self.get_ruff_issues(limit=10# Start small
        print(f"📋 Found {len(issues)} issues to process")

        if not issues:
            print("✅ No issues found!")
            return

        # Process each issue
        for i, issue in enumerate(issues, 1):
            file_path = issue.get("filename", "")
            line_num = issue.get("location", {}).get("row", 0)
            code = issue.get("code", "")
            message = issue.get("message", "")

            print(f"\n🔧 [{i}/{len(issues)}] {Path(file_path).name}:{line_num}")
            print(f"   Issue: {code} - {message}")

            if dry_run:
                print("   🧪 [DRY RUN] Would attempt LLM fix...")
                continue

            # Try to fix with LLM
            fix = self.fix_issue_with_llm(issue)
            if fix:
                print(f"   ✅ LLM suggested fix: {fix[:60]}...")
                # Here you would apply the fix
            else:
                print("   ❌ LLM couldn't suggest a fix")

    def run_ruff_autofix(self):
        """Run Ruff's built-in autofix for safe changes"""

        print("\n🔧 Running Ruff autofix for safe changes...")

        try:
            result = subprocess.run(
                ["ruff", "check", ".", "--fix"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            print("✅ Ruff autofix completed")
            if result.stdout:
                print("   Changes made:")
                for line in result.stdout.split("\n")[:10]:  # First 10 lines
                    if line.strip():
                        print(f"   {line}")

        except Exception as e:
            print(f"❌ Ruff autofix failed: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simple LUKHAS Code Fixer")
    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze without changes"
    )
    parser.add_argument("--autofix", action="store_true", help="Run Ruff autofix only")

    args = parser.parse_args()

    fixer = SimpleLLMCodeFixer()

    if args.autofix:
        fixer.run_ruff_autofix()
    else:
        fixer.run_simple_fixes(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
