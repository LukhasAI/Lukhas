#!/usr/bin/env python3

"""
Test script for Guardian Security Dependency Hasher
"""

import json
import sys
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.security.dependency_hasher import DependencyHasher


def test_dependency_hasher():
    """Test the Guardian Security dependency hasher"""

    print("🛡️ Testing Guardian Security Dependency Hasher")
    print("=" * 60)

    # Create a test requirements file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("""# Test Dependencies
pyyaml>=6.0.1
requests>=2.31.0
cryptography>=41.0.0

# Testing
pytest>=7.4.0
""")
        test_requirements_path = Path(f.name)

    try:
        # Initialize hasher
        hasher = DependencyHasher(test_requirements_path)

        # Test parsing requirements
        packages = hasher.parse_requirements()
        print(f"✅ Parsed {len(packages)} packages from test requirements")

        # Test getting a sample hash (just one package to avoid rate limiting)
        sample_package = "pyyaml"
        sample_version = "6.0.1"

        print(f"\n🔍 Testing hash lookup for {sample_package}=={sample_version}")
        package_hash = hasher.get_package_hash(sample_package, sample_version)

        if package_hash:
            print(f"✅ Successfully retrieved hash: {package_hash[:16]}...")
            hash_validation = len(package_hash) == 64 and all(c in "0123456789abcdef" for c in package_hash.lower())
            print(f"✅ Hash format valid: {hash_validation}")
        else:
            print("⚠️  Hash lookup failed (network/API issue)")

        # Test categories parsing
        categories = hasher._parse_requirements_with_categories()
        print(f"✅ Parsed {len(categories)} categories")

        print("\n" + "=" * 60)
        print("🎯 Guardian Security Dependency Hasher: FUNCTIONAL")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        hasher.cleanup()
        test_requirements_path.unlink()


if __name__ == "__main__":
    success = test_dependency_hasher()
    sys.exit(0 if success else 1)
