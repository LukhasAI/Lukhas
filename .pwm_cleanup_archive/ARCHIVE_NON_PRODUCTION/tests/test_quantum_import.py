#!/usr/bin/env python3
"""Debug quantum module import issue"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing quantum module import...")

try:
    import quantum

    print("✓ quantum module imported")
    print(f"  Available: {dir(quantum)}")
except Exception as e:
    print(f"✗ Failed to import quantum: {e}")
    import traceback

    traceback.print_exc()

try:
    from quantum import processor

    print("✓ quantum.processor imported")
    print(f"  Type: {type(processor)}")
except Exception as e:
    print(f"✗ Failed to import quantum.processor: {e}")

try:
    print("✓ lukhasQuantumProcessor imported")
    print(f"  Type: {type(lukhasQuantumProcessor)}")
except Exception as e:
    print(f"✗ Failed to import coreQuantumProcessor: {e}")

try:
    print("✓ Direct imports successful")
except Exception as e:
    print(f"✗ Failed direct imports: {e}")
    import traceback

    traceback.print_exc()
