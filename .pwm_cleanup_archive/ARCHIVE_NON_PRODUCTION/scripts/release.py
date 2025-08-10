#!/usr/bin/env python3
"""Release helper script for LUKHAS AGI."""

import re
import subprocess
import sys
from pathlib import Path


def get_current_version():
    """Get current version from __version__.py."""
    version_file = Path("lukhas/__version__.py")
    content = version_file.read_text()
    match = re.search(r'__version__ = ["\'](.*)["\']', content)
    return match.group(1) if match else "0.0.0"


def bump_version(version: str, bump_type: str = "patch"):
    """Bump version number."""
    major, minor, patch = map(int, version.split("."))

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def update_changelog(version: str):
    """Update CHANGELOG.md with new version."""
    changelog = Path("CHANGELOG.md")
    content = changelog.read_text()

    # Add date to unreleased section
    from datetime import date

    today = date.today().strftime("%Y-%m-%d")

    content = content.replace(
        "## [Unreleased]", f"## [Unreleased]\n\n## [{version}] - {today}"
    )

    changelog.write_text(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: release.py [major|minor|patch]")
        sys.exit(1)

    bump_type = sys.argv[1]
    current = get_current_version()
    new_version = bump_version(current, bump_type)

    print(f"Releasing version {new_version} (was {current})")

    # Update version file
    version_file = Path("lukhas/__version__.py")
    version_file.write_text(f'__version__ = "{new_version}"\n')

    # Update changelog
    update_changelog(new_version)

    # Git operations
    subprocess.run(["git", "add", "lukhas/__version__.py", "CHANGELOG.md"])
    subprocess.run(["git", "commit", "-m", f"Release v{new_version}"])
    subprocess.run(["git", "tag", f"v{new_version}"])

    print(f"Tagged v{new_version}. Push with: git push && git push --tags")


if __name__ == "__main__":
    main()
