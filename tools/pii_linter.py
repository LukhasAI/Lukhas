#!/usr/bin/env python3
"""
PII Linter for LUKHAS AI
Detects potential PII patterns in Python source files
"""

import pathlib
import re
import sys

# PII Detection Patterns
PII = [
    # SSN-like patterns (XXX-XX-XXXX)
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    # Email addresses
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    # Phone numbers (various formats)
    re.compile(r"\b(\+?\d{1,3})?[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"),
    # Credit card patterns (16 digits with optional spaces/dashes)
    re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
    # IPv4 addresses (excluding common local/test ranges)
    re.compile(
        r"\b(?!(?:127\.0\.0\.1|localhost|0\.0\.0\.0|192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.))(?:\d{1,3}\.){3}\d{1,3}\b"
    ),
    # API keys and secrets (common patterns)
    re.compile(
        r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|private[_-]?key)\s*[:=]\s*["\'][^"\']{20,}["\']'
    ),
]

# Exclude patterns (safe to ignore)
EXCLUDE_PATTERNS = [
    "test@example.com",
    "user@domain.com",
    "admin@localhost",
    "noreply@anthropic.com",
    "example@email.com",
    "user@example.com",
    "admin@example.com",
    "127.0.0.1",
    "0.0.0.0",
    "localhost",
    "192.168.",
    "10.",
    "172.16.",
    "172.17.",
    "172.18.",
    "172.19.",
    "172.20.",
    "172.21.",
    "172.22.",
    "172.23.",
    "172.24.",
    "172.25.",
    "172.26.",
    "172.27.",
    "172.28.",
    "172.29.",
    "172.30.",
    "172.31.",
    "555-555-5555",  # Fake phone number
    "123-45-6789",  # Example SSN
    "sk-test_",  # Test API keys
    "pk_test_",  # Test public keys
    "test_key_",  # Test keys
    "example_key",  # Example keys
    "YOUR_API_KEY",  # Placeholder text
    "your_secret_here",  # Placeholder text
    "PLACEHOLDER",  # Placeholder text
    "api_key_here",  # Placeholder text
]


def check_file(filepath):
    """Check a single file for PII patterns"""
    try:
        content = filepath.read_text(errors="ignore")

        # Skip if content matches exclude patterns
        for exclude in EXCLUDE_PATTERNS:
            content = content.replace(exclude, "")

        # Check for PII patterns
        for pattern in PII:
            match = pattern.search(content)
            if match:
                # Get line number for better reporting
                lines = content[: match.start()].count("\n") + 1
                return {
                    "file": str(filepath),
                    "line": lines,
                    "pattern": (
                        pattern.pattern[:50] + "..."
                        if len(pattern.pattern) > 50
                        else pattern.pattern
                    ),
                    "match": match.group()[:50],  # Truncate for security
                }
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return None


def main():
    """Main PII linter function"""
    bad_files = []

    # Define paths to scan
    scan_paths = [
        "lukhas",
        "candidate",
        "tools",
        "api",
        "ethics",
        "system",
    ]

    # Skip test directories and specific files
    skip_patterns = [
        "**/tests/**",
        "**/test_*.py",
        "**/*_test.py",
        "**/fixtures/**",
        "**/mock_*.py",
        "**/.env*",
        "**/requirements*.txt",
    ]

    # Scan for Python files
    for scan_path in scan_paths:
        base_path = pathlib.Path(scan_path)
        if not base_path.exists():
            continue

        for filepath in base_path.rglob("*.py"):
            # Skip if matches skip pattern
            if any(filepath.match(pattern) for pattern in skip_patterns):
                continue

            result = check_file(filepath)
            if result:
                bad_files.append(result)

    # Report results
    if bad_files:
        print("❌ PII patterns found in the following files:", file=sys.stderr)
        print("-" * 60, file=sys.stderr)
        for result in bad_files:
            print(f"  File: {result['file']}", file=sys.stderr)
            print(f"  Line: {result['line']}", file=sys.stderr)
            print(f"  Pattern: {result['pattern']}", file=sys.stderr)
            print(f"  Match: {result['match']}...", file=sys.stderr)
            print("-" * 60, file=sys.stderr)

        print(f"\n⚠️  Total files with PII: {len(bad_files)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("✅ PII linter: No PII patterns detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
