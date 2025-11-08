#!/usr/bin/env python3
'''Update 'Last Updated' timestamps in all documentation'''

import re
from datetime import datetime
from pathlib import Path
import subprocess

def update_timestamps(doc_dir: Path):
    today = datetime.now().strftime("%Y-%m-%d")
    pattern = re.compile(r"Last [Uu]pdated:?\s*\d{4}-\d{2}-\d{2}")

    for md_file in doc_dir.rglob("*.md"):
        content = md_file.read_text()
        new_content = content

        # Check if file has been modified in git
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", str(md_file)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout:
            last_commit = result.stdout[:10]  # YYYY-MM-DD

            # Update or add timestamp
            if pattern.search(content):
                new_content = pattern.sub(f"Last Updated: {last_commit}", content)
            else:
                # Add to frontmatter if present, else add after first heading
                if content.startswith("# "):
                    lines = content.split("\n")
                    lines.insert(1, f"\n**Last Updated**: {last_commit}\n")
                    new_content = "\n".join(lines)
                else:
                    new_content = content

            if new_content != content:
                md_file.write_text(new_content)
                print(f"Updated: {md_file}")

if __name__ == "__main__":
    update_timestamps(Path("docs"))
