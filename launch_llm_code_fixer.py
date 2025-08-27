#!/usr/bin/env python3
"""
🚀 LUKHAS LLM Code Quality Launcher
====================================

Quick launcher for the Local LLM Code Quality Improvement System.
Provides easy access to the most common code improvement workflows.

Usage:
    ./launch_llm_code_fixer.py --help
    ./launch_llm_code_fixer.py --dry-run
    ./launch_llm_code_fixer.py --category syntax_errors
    ./launch_llm_code_fixer.py --fix-top-issues 50
"""

import subprocess
import sys
from pathlib import Path


# Colors for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"

def print_banner():
    """Print the LUKHAS banner"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("🧠 LUKHAS Local LLM Code Quality Improvement")
    print("⚛️🧠🛡️ Trinity Framework Consciousness Technology")
    print("=" * 55)
    print(f"{Colors.END}")

def check_prerequisites():
    """Check if prerequisites are available"""
    print(f"{Colors.YELLOW}🔍 Checking prerequisites...{Colors.END}")

    issues = []

    # Check Python version
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")

    # Check if Ruff is available
    try:
        result = subprocess.run(["ruff", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ruff available: {result.stdout.strip()}")
        else:
            issues.append("Ruff not found - install with: pip install ruff")
    except FileNotFoundError:
        issues.append("Ruff not found - install with: pip install ruff")

    # Check for local LLM services
    llm_services = [
        ("Ollama", "http://localhost:11434", "/api/tags"),
        ("LM Studio", "http://localhost:1234", "/v1/models"),
    ]

    llm_available = False
    for service_name, base_url, endpoint in llm_services:
        try:
            import requests
            response = requests.get(f"{base_url}{endpoint}", timeout=2)
            if response.status_code == 200:
                print(f"✅ {service_name} available at {base_url}")
                llm_available = True
                break
        except Exception:
            pass

    if not llm_available:
        issues.append("No local LLM service found. Please start Ollama or LM Studio.")
        print(f"{Colors.YELLOW}   To install Ollama: curl -fsSL https://ollama.ai/install.sh | sh{Colors.END}")
        print(f"{Colors.YELLOW}   To start Ollama: ollama serve{Colors.END}")

    return issues

def run_quick_analysis():
    """Run quick Ruff analysis to show current status"""
    print(f"\n{Colors.BLUE}📊 Running quick code quality analysis...{Colors.END}")

    try:
        # Run Ruff with statistics
        result = subprocess.run([
            "ruff", "check", ".",
            "--statistics",
            "--no-fix"
        ], capture_output=True, text=True, cwd=Path.cwd())

        if result.stdout:
            print(f"\n{Colors.CYAN}Current Code Quality Issues:{Colors.END}")
            lines = result.stdout.strip().split("\n")
            for line in lines[-10:]:  # Show last 10 lines (summary)
                if any(char.isdigit() for char in line):  # Lines with numbers
                    print(f"  {line}")

        if result.stderr:
            print(f"\n{Colors.YELLOW}Ruff messages:{Colors.END}")
            print(f"  {result.stderr[:200]}")

    except Exception as e:
        print(f"{Colors.RED}❌ Analysis failed: {e}{Colors.END}")

def main():
    """Main launcher function"""
    print_banner()

    # Check prerequisites
    issues = check_prerequisites()
    if issues:
        print(f"\n{Colors.RED}❌ Prerequisites not met:{Colors.END}")
        for issue in issues:
            print(f"  • {issue}")
        print(f"\n{Colors.YELLOW}Please resolve these issues and try again.{Colors.END}")
        return 1

    # Show current status
    run_quick_analysis()

    # Interactive menu
    print(f"\n{Colors.GREEN}🎯 What would you like to do?{Colors.END}")
    print("1. 🧪 Dry run - Analyze issues without making changes")
    print("2. 🔧 Fix syntax errors only (critical priority)")
    print("3. 🔨 Fix import issues (high priority)")
    print("4. 🎨 Fix all issues with LLM assistance")
    print("5. 📊 Generate detailed analysis report")
    print("6. ⚙️  Advanced - Custom parameters")
    print("0. ❌ Exit")

    choice = input(f"\n{Colors.CYAN}Enter your choice (0-6): {Colors.END}").strip()

    # Map choices to commands
    commands = {
        "1": ["python", "tools/llm_code_fixer.py", "--dry-run"],
        "2": ["python", "tools/llm_code_fixer.py", "--category", "syntax_errors"],
        "3": ["python", "tools/llm_code_fixer.py", "--category", "import_issues"],
        "4": ["python", "tools/llm_code_fixer.py"],
        "5": ["python", "tools/llm_code_fixer.py", "--dry-run", "--report-only"],
        "6": None,  # Custom
        "0": None   # Exit
    }

    if choice == "0":
        print(f"{Colors.GREEN}👋 Goodbye!{Colors.END}")
        return 0

    elif choice == "6":
        print(f"\n{Colors.CYAN}🔧 Advanced Options:{Colors.END}")
        print("Available parameters:")
        print("  --project-root <path>    - Root directory to analyze")
        print("  --dry-run               - Analyze without making changes")
        print("  --llm-service <service> - ollama or lmstudio")
        print("  --llm-url <url>         - LLM service URL")

        custom_args = input(f"\n{Colors.CYAN}Enter custom arguments: {Colors.END}").strip()
        if custom_args:
            command = ["python", "tools/llm_code_fixer.py"] + custom_args.split()
        else:
            print("No arguments provided, exiting.")
            return 0

    elif choice in commands and commands[choice]:
        command = commands[choice]
    else:
        print(f"{Colors.RED}❌ Invalid choice{Colors.END}")
        return 1

    # Execute the command
    print(f"\n{Colors.GREEN}🚀 Executing: {' '.join(command)}{Colors.END}")
    print(f"{Colors.YELLOW}⏳ This may take a while depending on codebase size...{Colors.END}")

    try:
        result = subprocess.run(command, cwd=Path.cwd())

        if result.returncode == 0:
            print(f"\n{Colors.GREEN}✅ Code improvement completed successfully!{Colors.END}")
            print(f"{Colors.CYAN}🔄 Next steps:{Colors.END}")
            print("  1. Review the changes made")
            print("  2. Run tests to ensure functionality")
            print("  3. Commit the improvements")
        else:
            print(f"\n{Colors.RED}❌ Code improvement failed with exit code {result.returncode}{Colors.END}")

        return result.returncode

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Process interrupted by user{Colors.END}")
        return 130
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
