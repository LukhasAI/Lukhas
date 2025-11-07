"""pytest configuration with PYTHONPATH fixes for import resolution."""
import sys
from pathlib import Path

# Add discovered package paths to resolve import errors
repo_root = Path(__file__).parent
critical_paths = [
    repo_root / "labs",
    repo_root / "bridge", 
    repo_root / "candidate",
    repo_root / "core",
    repo_root / "lukhas",
    repo_root,  # repo root itself
]

for path in critical_paths:
    if path.exists():
        sys.path.insert(0, str(path))

print(f"✅ PYTHONPATH configured with {len([p for p in critical_paths if p.exists()])} paths")
