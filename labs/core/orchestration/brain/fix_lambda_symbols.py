#!/usr/bin/env python3
"""
Script to replace all λ symbols with 'lambda' in Python files
"""

import os
import re
import sys


def fix_lambda_symbols(directory):
    """
    Recursively finds and replaces all λ symbols with 'lambda' in Python files
    """
    count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()

                    # Replace λ with lambda
                    new_content = re.sub(r"λ\s+", "lambda ", content)

                    if new_content != content:
                        count += 1
                        print(f"Fixing {file_path}")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                except UnicodeDecodeError:
                    print(f"Could not process {file_path} due to encoding issues")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    return count


if __name__ == "__main__":
    directory = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "brain")

    if not os.path.isdir(directory):
        print(f"Directory '{directory}' not found")
        sys.exit(1)

    print(f"Fixing lambda symbols in {directory}...")
    count = fix_lambda_symbols(directory)
    print(f"Fixed lambda symbols in {count} files")
