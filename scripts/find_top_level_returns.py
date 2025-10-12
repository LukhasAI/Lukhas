#!/usr/bin/env python3
import ast
import sys
from pathlib import Path


def has_top_level_return(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    for node in tree.body:
        # Return found at module level
        if isinstance(node, ast.Return):
            return True
        # Return nested directly in an if/try at top-level is also suspicious
        if isinstance(node, (ast.If, ast.Try)):
            for n in node.body:
                if isinstance(n, ast.Return):
                    return True
    return False

def main():
    root = Path(".")
    suspects = []
    for py in root.rglob("*.py"):
        if "venv/" in str(py) or "/generated/" in str(py):
            continue
        if has_top_level_return(py):
            suspects.append(str(py))
    if suspects:
        print("\n".join(sorted(suspects)))
        sys.exit(1)
    print("[OK] no top-level returns detected")
    sys.exit(0)

if __name__ == "__main__":
    main()
