#!/usr/bin/env python3
import os

# First, rename all files
for root, dirs, files in os.walk("."):
    for file in files:
        if "quantum" in file.lower() and file.endswith(".py"):
            old_path = os.path.join(root, file)
            # Replace quantum_ with qi_ or inspired_
            new_name = file.replace("quantum_", "qi_")
            new_name = new_name.replace("_quantum_", "_qi_")
            new_name = new_name.replace("_quantum.", "_qi.")
            # Special cases
            new_name = new_name.replace(
                "post_quantum_crypto", "post_quantum_crypto"
            )  # Keep this one

            if new_name != file:
                new_path = os.path.join(root, new_name)
                print(f"Renaming: {file} -> {new_name}")
                os.rename(old_path, new_path)

# Then rename directories (bottom-up to avoid path issues)
for root, dirs, files in os.walk(".", topdown=False):
    for dir_name in dirs:
        if "quantum" in dir_name.lower():
            old_path = os.path.join(root, dir_name)
            # Replace quantum with qi or inspired
            new_name = dir_name.replace("quantum_", "qi_")
            new_name = new_name.replace("_quantum", "_qi")
            # Special case
            if new_name == "post_quantum_crypto" or new_name == "post_quantum_crypto_enhanced":
                new_name = dir_name  # Keep post_quantum_crypto as is

            if new_name != dir_name:
                new_path = os.path.join(root, new_name)
                print(f"Renaming dir: {dir_name} -> {new_name}")
                os.rename(old_path, new_path)
