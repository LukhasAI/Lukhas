"""
Entropy Visualizer
==================

A simple command-line tool to visualize the entropy of byte strings.
This tool is for internal research and debugging purposes.
"""

from __future__ import annotations

import sys
from collections import Counter

# tools/analysis/entropy_visualizer.py




def visualize_entropy(data: bytes):
    """
    Prints a simple histogram of the byte distribution of the input data.

    Args:
        data: A byte string.
    """
    if not isinstance(data, bytes):
        raise TypeError("Input data must be a byte string.")

    if not data:
        print("Input data is empty. No entropy to visualize.")
        return

    print(f"Analyzing {len(data)} bytes of data.\n")

    counts = Counter(data)
    max_count = 0
    if counts:
        max_count = counts.most_common(1)[0][1]

    # Sort by byte value for a consistent output
    sorted_counts = sorted(counts.items())

    print("Byte Value (Hex) | Count      | Distribution")
    print("-----------------|------------|--------------------------------------------------")

    for byte_val, count in sorted_counts:
        # Scale the histogram bar
        bar_length = int((count / max_count) * 50) if max_count > 0 else 0
        bar = "#" * bar_length

        # Format the output
        hex_val = f"0x{byte_val:02x}"
        print(f"{hex_val:<16} | {count:<10} | {bar}")

if __name__ == "__main__":
    # This allows the script to be used with pipes, e.g.:
    # python -m security.secure_random | python tools/analysis/entropy_visualizer.py
    # Or with a file:
    # python tools/analysis/entropy_visualizer.py some_file.bin

    if len(sys.argv) > 1:
        # Read from file
        try:
            with open(sys.argv[1], 'rb') as f:
                input_data = f.read()
            visualize_entropy(input_data)
        except FileNotFoundError:
            print(f"Error: File not found at {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            sys.exit(1)
    elif not sys.stdin.isatty():
        # Read from stdin (pipe)
        try:
            input_data = sys.stdin.buffer.read()
            visualize_entropy(input_data)
        except Exception as e:
            print(f"An error occurred while reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage:")
        print("  - Pipe data to this script: cat some_file.bin | python tools/analysis/entropy_visualizer.py")
        print("  - Provide a file path as an argument: python tools/analysis/entropy_visualizer.py some_file.bin")
        sys.exit(1)
