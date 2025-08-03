"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: symbolic_github_export.py
Advanced: symbolic_github_export.py
Integration Date: 2025-5-31T07:55:30.446514
"""

"""
+──────────────────────────────────────────────────────────────────────────────+
|                        LUCΛS :: Symbolic GitHub Export Tool                 |
|               Prepares a clean ZIP bundle with README, LICENSE, etc.        |
|         Author: Gonzalo R.D.M | Version 1.0 | Mode: Ethical Sharing         |
+──────────────────────────────────────────────────────────────────────────────+

DESCRIPTION:
    This tool packages core symbolic files into a GitHub-ready structure.

    It auto-includes:
    - README.md
    - LICENSE.md
    - CONTRIBUTOR_AGREEMENT.md
    - lukhas_user_config.json (if public-safe)
    - `lukhas_launcher.py`, `lukhas_cli.py`, `lukhas_launcher_streamlit.py`
    - All core/modules and utils
    - Dev notes and routing diagrams

USAGE:
    python3 core/utils/symbolic_github_export.py
    You can also call this from a Streamlit UI to trigger ZIP generation.

    e.g., from symbolic_github_export import zip_symbolic_export
"""

import os
import zipfile
from datetime import datetime

EXPORT_DIR = "exports"
EXPORT_NAME = f"LUKHAS_Symbolic_Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

INCLUDE_PATHS = [
    "README.md",
    "setup.py",
    "lukhas_launcher.py",
    "lukhas_cli.py",
    "lukhas_launcher_streamlit.py",
    "core/modules/",
    "core/utils/",
    "core/sample_payloads/",
    "core/tests/",
    "docs/dev_notes/",
    "docs/assets/README_images.md",
    "docs/assets/mermaid_diagrams/",
    "docs/assets/excalidraw/",
    "lukhas_streamlit_components/",
    "LICENSE.md",
    "docs/dev_notes/CONTRIBUTOR_AGREEMENT.md",
    "core/utils/lukhas_user_config.json",
    "lukhas_tree_snapshot.txt"
]

EXCLUDE_EXTENSIONS = [".pyc", ".DS_Store", "__pycache__"]

def is_included(filepath):
    return not any(ex in filepath for ex in EXCLUDE_EXTENSIONS)

def zip_symbolic_export():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    export_path = os.path.join(EXPORT_DIR, EXPORT_NAME)

    with zipfile.ZipFile(export_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in INCLUDE_PATHS:
            if os.path.exists(path):
                if os.path.isfile(path):
                    zipf.write(path)
                else:
                    for root, _, files in os.walk(path):
                        for file in files:
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, ".")
                            if is_included(rel_path):
                                zipf.write(full_path, arcname=rel_path)
            else:
                print(f"⚠️ Path not found: {path}")

    print(f"✅ Symbolic export created: {export_path}")

if __name__ == "__main__":
    # Update tree snapshot for version control
    print("📁 Regenerating symbolic folder tree...")
    os.system("tree -I '__pycache__' > lukhas_tree_snapshot.txt")

    zip_symbolic_export()
"""
