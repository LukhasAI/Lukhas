# Lane Import Enforcement

This document describes the import enforcement mechanism that prevents code in the `candidate/` directory from importing modules from the `lukhas/` directory.

## Purpose

The `candidate/` directory is intended for experimental code and features that are not yet ready for production. To maintain a clean separation between experimental and core code, we enforce a strict import restriction: **no code in `candidate/` can import from `lukhas/`**. This helps prevent unstable code from affecting the core application and makes it easier to manage dependencies.

## How it works

The enforcement is handled by the `scripts/lane_guard/enforce_imports.py` script. This script scans all Python files in the `candidate/` directory and checks their import statements. If it finds any import that starts with `lukhas`, it will print an error message and exit with a non-zero status code.

## Running the script

To run the script manually, use the following command from the root of the repository:

```bash
python3 scripts/lane_guard/enforce_imports.py
```

If the script finds any forbidden imports, it will print them to the console. Otherwise, it will print a success message.

## CI Integration

This script is designed to be run in a CI/CD pipeline to automatically check for forbidden imports in every pull request. The script's exit code can be used to determine whether the check passed or failed.
