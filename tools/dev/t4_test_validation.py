#!/usr/bin/env python3
"""
T4 System Validation - Simple test file with TODO markers.
"""

def example_function():
    """Example function with T4-AUTOFIX opportunities."""

    # TODO[T4-AUTOFIX]: Use list comprehension instead of append loop
    result = []
    for i in range(10):
        if i % 2 == 0:
            result.append(i * 2)

    # TODO[T4-AUTOFIX]: Use pathlib.Path instead of os.path.join
    import os
    file_path = os.path.join("data", "output.txt")

    # TODO[T4-AUTOFIX]: Remove unused variable

    return result, file_path


if __name__ == "__main__":
    print("T4 validation test file - use ⌘⇧T to find TODOs")
