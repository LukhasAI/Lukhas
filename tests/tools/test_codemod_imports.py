"""
Golden tests for codemod_imports.py edge cases.

Prevents regressions on:
- CST/AST node handling (Attribute vs Name)
- String prefix preservation (r"", f"", b"")
- Multi-import forms
- importlib.import_module() string literals

Phase 3: Added as stability guarantee after codemod robustness fix (45d40b49c).
"""
import pathlib
import subprocess
import sys
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Golden test cases: (name, input_code, expected_output)
CASES = [
    # Basic import rewrites
    ("simple_from",
     "from candidate.foo import bar\n",
     "from labs.foo import bar\n"),

    ("simple_import",
     "import candidate.core\n",
     "import labs.core\n"),

    # Multi-import forms
    ("multi_from",
     "from tools.monitoring import a, b\n",
     "from lukhas.tools.monitoring import a, b\n"),

    ("multi_from_candidate",
     "from candidate.core import A, B, C\n",
     "from labs.core import A, B, C\n"),

    # importlib.import_module() string literals
    ("importlib_basic",
     "import importlib\nm = importlib.import_module('candidate.core')\n",
     "import importlib\nm = importlib.import_module('labs.core')\n"),

    ("importlib_lucas",
     "import importlib\nm = importlib.import_module('lucas.core')\n",
     "import importlib\nm = importlib.import_module('lukhas.core')\n"),

    # String prefix preservation
    ("fstring_preserved",
     "from candidate.mod import X\ns = f'{X.__name__}'\n",
     "from labs.mod import X\ns = f'{X.__name__}'\n"),

    ("raw_string_preserved",
     r"from candidate.path import P" + "\n" + r"pat = r'c:\\candidate\\x'" + "\n",
     r"from labs.path import P" + "\n" + r"pat = r'c:\\candidate\\x'" + "\n"),

    ("bytes_string_preserved",
     "from candidate.data import D\nb = b'raw bytes'\n",
     "from labs.data import D\nb = b'raw bytes'\n"),

    # Edge cases: no rewrites expected
    ("no_rewrite_stdlib",
     "import os\nfrom pathlib import Path\n",
     "import os\nfrom pathlib import Path\n"),

    ("no_rewrite_third_party",
     "import fastapi\nfrom pydantic import BaseModel\n",
     "import fastapi\nfrom pydantic import BaseModel\n"),

    # Attribute vs Name node handling
    ("attribute_chain",
     "from candidate.core.models import User\n",
     "from labs.core.models import User\n"),

    ("nested_modules",
     "from candidate.consciousness.core.processor import Process\n",
     "from labs.consciousness.core.processor import Process\n"),
]


def run_codemod(src: str, mapping: dict = None) -> str:
    """
    Run codemod_imports.py on source code via subprocess.

    Args:
        src: Python source code to transform
        mapping: Optional custom mapping (uses default if None)

    Returns:
        Transformed source code
    """
    # Default mapping matches Phase 2 codemods
    if mapping is None:
        mapping = {
            "candidate": "labs",
            "lucas": "lukhas",
            "tools": "lukhas.tools",
        }

    # Build command line
    cmd = [sys.executable, str(ROOT / "scripts/codemod_imports.py")]

    # For now, we'll write to a temp file since the script expects file paths
    # In a real scenario, you'd extend the script to support --stdin/--stdout
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(src)
        temp_path = f.name

    try:
        # Run codemod on temp file
        subprocess.run(
            cmd + [temp_path, "--apply"],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )

        # Read result
        with open(temp_path, 'r') as f:
            output = f.read()

        return output
    finally:
        # Cleanup
        import os
        os.unlink(temp_path)


@pytest.mark.parametrize("name,before,expected", CASES)
def test_codemod_golden_cases(name, before, expected):
    """Test codemod against golden cases to prevent regressions."""
    result = run_codemod(before)

    assert result == expected, (
        f"Codemod mismatch in case '{name}'\n"
        f"--- Input ---\n{before}\n"
        f"--- Expected ---\n{expected}\n"
        f"--- Got ---\n{result}"
    )


def test_codemod_preserves_formatting():
    """Test that codemod preserves indentation and spacing."""
    src = """
def foo():
    from candidate.core import A
    x = A()
    return x
"""
    expected = """
def foo():
    from labs.core import A
    x = A()
    return x
"""
    result = run_codemod(src)
    assert result == expected, "Codemod should preserve indentation"


def test_codemod_handles_mixed_imports():
    """Test mixed legacy and new imports in same file."""
    src = """
from candidate.core import A
from labs.other import B
import lukhas.tools
"""
    expected = """
from labs.core import A
from labs.other import B
import lukhas.tools
"""
    result = run_codemod(src)
    assert result == expected, "Codemod should handle mixed imports"


def test_codemod_idempotent():
    """Test that running codemod twice produces same result."""
    src = "from candidate.core import A\n"

    first = run_codemod(src)
    second = run_codemod(first)

    assert first == second, "Codemod should be idempotent"
    assert "labs" in first, "First run should transform"
    assert "candidate" not in second, "Second run should not revert"
