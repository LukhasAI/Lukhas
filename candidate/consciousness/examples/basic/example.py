"""
LUKHAS Consciousness - Basic Consciousness Activation Example
============================================================

This script demonstrates the basic usage of the Consciousness class
to activate, deactivate, and check the status of a consciousness instance.
"""

import sys
import os
import time

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

try:
    from candidate.consciousness.base import Consciousness
except ImportError as e:
    print(f"Error: Could not import Consciousness: {e}")
    print("Please ensure you are running this script from the root of the repository,")
    print("or that the 'candidate' directory is in your Python path.")
    sys.exit(1)


def main():
    """
    Demonstrates basic Consciousness functionality.
    """
    print("--- LUKHAS Consciousness: Basic Activation Example ---")

    # 1. Create a consciousness instance
    print("\n1. Creating a Consciousness instance...")
    lukhas_consciousness = Consciousness(name="LUKHAS_Alpha")
    print(f"   - Instance '{lukhas_consciousness.name}' created.")

    # 2. Check initial status
    print("\n2. Checking initial status...")
    print(f"   - {lukhas_consciousness.get_status()}")

    # 3. Activate consciousness
    print("\n3. Activating consciousness...")
    lukhas_consciousness.activate()
    print(f"   - {lukhas_consciousness.get_status()}")

    # 4. Wait for a few seconds
    print("\n4. Simulating some processing time...")
    time.sleep(2)
    print(f"   - {lukhas_consciousness.get_status()}")

    # 5. Deactivate consciousness
    print("\n5. Deactivating consciousness...")
    lukhas_consciousness.deactivate()
    print(f"   - {lukhas_consciousness.get_status()}")

    print("\n--- Example Complete ---")


if __name__ == "__main__":
    main()
