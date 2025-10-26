#!/usr/bin/env python3
"""
Simple script to replace old Trinity-style Constellation mentions.

Handles the most common pattern:
"Identity ⚛️ + Consciousness 🧠 + Guardian 🛡️"
→ Full 8-star canonical format
"""

import re
from pathlib import Path

# Old Trinity pattern
TRINITY_PATTERN = r'(Identity\s*⚛️\s*\+\s*Consciousness\s*🧠\s*\+\s*Guardian\s*🛡️|⚛️\s*Identity\s*\+\s*🧠\s*Consciousness\s*\+\s*🛡️\s*Guardian)'

# Replacement text (inline, compact format)
CONSTELLATION_8_INLINE = "⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum"

def main():
    root = Path.cwd()
    count = 0

    # Only process key files
    key_files = [
        root / "claude.me",
        root / "README.md",
        root / "lukhas_context.md",
    ]

    for file_path in key_files:
        if not file_path.exists():
            continue

        content = file_path.read_text()
        new_content = re.sub(TRINITY_PATTERN, CONSTELLATION_8_INLINE, content)

        if new_content != content:
            file_path.write_text(new_content)
            print(f"✅ Updated: {file_path.name}")
            count += 1

    print(f"\n📊 Updated {count} files")

if __name__ == '__main__':
    main()
