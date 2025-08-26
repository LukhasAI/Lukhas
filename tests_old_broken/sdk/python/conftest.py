import sys
from pathlib import Path

# Add sdk/python/src to sys.path for tests without requiring installation
ROOT = Path(__file__).resolve().parents[2]
src = ROOT / "sdk" / "python" / "src"
if str(src) not in sys.path:
    sys.path.insert(0, str(src))
