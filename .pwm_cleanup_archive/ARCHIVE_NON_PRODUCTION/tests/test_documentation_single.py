#!/usr/bin/env python3
"""
Test the documentation updater on a single file to verify the path fixes work.
"""

import asyncio
import sys
from pathlib import Path

# Add docs directory to path
sys.path.append(str(Path(__file__).parent / "docs"))

from core_documentation_updater import standardize_lukhas_documentation


async def test_single_file():
    """Test documentation update on a single file"""

    print("🧪 Testing Documentation Update on Single File")
    print("=" * 50)

    # Test with one specific file
    test_file = "memory/systems/memory_fold_system.py"

    if not Path(test_file).exists():
        print(f"❌ Test file {test_file} not found")
        return

    print(f"📝 Testing with file: {test_file}")
    print("⚠️  Note: This will show API key error (expected)")
    print()

    try:
        results = await standardize_lukhas_documentation(
            project_root=".", specific_files=[test_file]
        )

        print("✅ Test completed successfully!")
        print(f"Results: {results}")

    except Exception as e:
        if "OpenAI API key is required" in str(e):
            print("✅ Path handling works! (Expected API key error)")
            print("   The system reached the API call stage without path errors")
        else:
            print(f"❌ Unexpected error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_single_file())
