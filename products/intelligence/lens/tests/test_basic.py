"""
Basic tests for ΛLens functionality
"""
import streamlit as st

import asyncio
import os

# Add the parent directory to the path so we can import ΛLens
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lens_core import ΛLens


async def test_basic_transformation():
    """Test basic file transformation"""
    print("Testing ΛLens basic transformation...")

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(
            """
        Test Document for ΛLens

        This is a test document to verify that ΛLens can properly transform
        text files into symbolic representations.

        Key concepts:
        - Artificial Intelligence
        - Symbolic processing
        - File transformation
        - Dashboard generation
        """
        )
        test_file = f.name

    try:
        # Initialize ΛLens
        lens = ΛLens()

        # Transform the file
        dashboard = await lens.transform(test_file, {"format": "2d"})

        # Verify results
        assert dashboard.id is not None
        assert len(dashboard.symbols) > 0
        assert dashboard.lambda_signature.startswith("Λ")

        print("✅ Transformation successful!")
        print(f"   Dashboard ID: {dashboard.id}")
        print(f"   Symbols created: {len(dashboard.symbols}")
        print(f"   Lambda signature: {dashboard.lambda_signature}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e!s}")
        return False

    finally:
        # Clean up
        os.unlink(test_file)


if __name__ == "__main__":
    success = asyncio.run(test_basic_transformation())
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)
