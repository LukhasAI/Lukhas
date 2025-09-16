#!/usr/bin/env python3
"""
Fix broken docstrings caused by TODO removal
"""
import os
import re


def fix_broken_docstring(file_path):
    """Fix broken docstring in a single file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Pattern: function definition followed by broken docstring
        pattern = r'(def \w+\([^)]*\):\s*\n)\s*(This is a placeholder[^"]*""")'

        # Replacement: add proper opening docstring
        replacement = r'\1    """\n    \2'

        new_content = re.sub(pattern, replacement, content)

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Fixed: {file_path}")
            return True
        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Fix all broken docstrings in branding directory."""

    broken_files = [
        "./branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_click_actions.py",
        "./branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_designer.py",
        "./branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_financial_intelligence.py",
        "./branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_notion_sync.py",
        "./branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_bio_symbolic_lambda_bot.py",
        "./branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_free_abot_direct.py",
        "./branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_multi_brain_lambda_bot.py",
        "./branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_multi_brain_symphony_lambda_bot.py",
        "./branding/orchestration/content_orchestrator.py",
        "./branding/orchestration/system_consolidator.py",
        "./branding/orchestration/system_integrator.py",
        "./branding/poetry/legacy/advanced_haiku_generator.py",
        "./branding/vocabularies/vocabulary.py",
        "./branding/vocabularies/vocabulary_creativity_engine.py",
        "./quarantine/syntax_errors/lambda_bot_enterprise_multi_brain_lambda_bot.py",
    ]

    fixed_count = 0
    for file_path in broken_files:
        if os.path.exists(file_path):
            if fix_broken_docstring(file_path):
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
