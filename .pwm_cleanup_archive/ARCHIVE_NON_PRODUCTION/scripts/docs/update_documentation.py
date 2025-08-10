#!/usr/bin/env python3
"""
Simple script to update LUKHAS documentation standards across the project.

Usage:
    python update_documentation.py --help
    python update_documentation.py --memory-systems
    python update_documentation.py --all
    python update_documentation.py --specific-files file1.py file2.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add docs directory to path for importing the updater
sys.path.append(str(Path(__file__).parent / "docs"))


async def update_memory_systems():
    """Update documentation for memory systems specifically"""

    print("🧠 Updating LUKHAS Memory Systems Documentation...")

    memory_files = ["memory/systems/*.py", "memory/*.py"]

    results = await standardize_lukhas_documentation(
        project_root=".", specific_files=memory_files
    )

    print_results(results)
    return results


async def update_all_documentation():
    """Update documentation for entire project"""

    print("🚀 Updating All LUKHAS Documentation...")

    results = await standardize_lukhas_documentation(project_root=".")

    print_results(results)
    return results


async def update_specific_files(file_paths):
    """Update documentation for specific files"""

    print(f"📝 Updating Documentation for {len(file_paths)} files...")

    results = await standardize_lukhas_documentation(
        project_root=".", specific_files=file_paths
    )

    print_results(results)
    return results


def print_results(results):
    """Print formatted results"""

    summary = results["summary"]
    api_usage = results["api_usage"]

    print("\n" + "=" * 60)
    print("📊 LUKHAS DOCUMENTATION UPDATE RESULTS")
    print("=" * 60)

    print(f"✅ Files Successfully Processed: {summary['files_successfully_processed']}")
    print(f"📁 Total Files Analyzed: {summary['total_files_analyzed']}")
    print(f"🔄 Files Needing Update: {summary['files_needing_update']}")
    print(f"📈 Success Rate: {summary['processing_success_rate']:.1%}")

    print("\n💰 API Usage:")
    print(f"   Model: {api_usage['model_used']}")
    print(f"   Tokens Used: {api_usage['total_tokens_used']:,}")
    print(f"   Estimated Cost: ${api_usage['estimated_cost_usd']:.4f}")

    if results.get("failed_files"):
        print(f"\n❌ Failed Files ({len(results['failed_files'])}):")
        for file_path in results["failed_files"]:
            print(f"   • {file_path}")

    print("\n📄 Detailed report saved with timestamp")
    print("=" * 60)


def check_api_key():
    """Check if OpenAI API key is available"""

    # Check .env file first
    env_file = Path(".env")
    api_key = None

    if env_file.exists():
        try:
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENAI_API_KEY=") and not line.startswith("#"):
                        api_key = line.split("=", 1)[1].strip().strip("\"'")
                        break
        except:
            pass

    # Fallback to environment variable
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    # Fallback to config file
    if not api_key:
        config_path = Path("config/documentation_config.json")
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    api_key = config.get("openai_api_key")
            except:
                pass

    if not api_key or api_key in [
        "YOUR_OPENAI_API_KEY_HERE",
        "your-openai-api-key-here",
    ]:
        print("❌ OpenAI API key not found!")
        print(
            "\nPlease set your API key using one of these methods (in order of preference):"
        )
        print("1. Create a .env file: echo 'OPENAI_API_KEY=your-key-here' > .env")
        print("2. Set environment variable: export OPENAI_API_KEY='your-key-here'")
        print("3. Update config/documentation_config.json")
        print("\nRecommended: Copy .env.template to .env and add your key")
        print(
            "Note: This uses gpt-4o-mini (4.1) for cost efficiency (~$0.15/1K tokens)"
        )
        return False

    return True


async def main():
    """Main CLI interface"""

    import argparse

    parser = argparse.ArgumentParser(
        description="LUKHAS AI Documentation Updater",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python update_documentation.py --memory-systems
    python update_documentation.py --all
    python update_documentation.py --files memory/systems/memory_fold_system.py
    python update_documentation.py --dry-run --memory-systems
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--memory-systems",
        action="store_true",
        help="Update memory systems documentation",
    )
    group.add_argument(
        "--all", action="store_true", help="Update all project documentation"
    )
    group.add_argument(
        "--files", nargs="+", metavar="FILE", help="Update specific files"
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Analyze files without making changes"
    )
    parser.add_argument(
        "--cost-limit",
        type=float,
        default=5.0,
        help="Maximum cost limit in USD (default: $5.00)",
    )

    args = parser.parse_args()

    # Check API key
    if not check_api_key():
        return 1

    print("🚀 LUKHAS Documentation Standardization Engine")
    print("=" * 50)
    print("📝 Using gpt-4o-mini (4.1) for cost-efficient processing")
    print(f"💰 Cost limit: ${args.cost_limit:.2f}")

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")

    print()

    try:
        if args.dry_run:
            print("Dry run mode not yet implemented - coming soon!")
            return 0

        if args.memory_systems:
            results = await update_memory_systems()
        elif args.all:
            results = await update_all_documentation()
        elif args.files:
            results = await update_specific_files(args.files)

        # Check if cost limit exceeded
        actual_cost = results["api_usage"]["estimated_cost_usd"]
        if actual_cost > args.cost_limit:
            print(
                f"⚠️  Warning: Cost ${actual_cost:.4f} exceeded limit ${args.cost_limit:.2f}"
            )

        print("\n✅ Documentation standardization complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
