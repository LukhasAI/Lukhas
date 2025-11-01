import os
import sys
import warnings
from importlib import import_module
from pathlib import Path

# Allow optional pydantic imports for warning suppression without hard dependency
try:
    from pydantic.warnings import PydanticDeprecatedSince20
except ModuleNotFoundError:  # pragma: no cover - pydantic not installed
    PydanticDeprecatedSince20 = DeprecationWarning  # type: ignore[assignment]

# Ensure the repository root is on sys.path so legacy imports like
# `from bridge.adapters import ...` resolve correctly when pytest sets
# `tests/unit` as the root directory.
_TESTS_UNIT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _TESTS_UNIT_DIR.parent.parent
_repo_root_str = str(_REPO_ROOT)
if _repo_root_str in sys.path:
    sys.path.pop(sys.path.index(_repo_root_str))
sys.path.insert(0, _repo_root_str)

# Preserve the historical behaviour where `tests/` itself is available on the
# import path for fixtures that rely on relative imports within the test tree.
_TESTS_ROOT = _TESTS_UNIT_DIR.parent
_tests_root_str = str(_TESTS_ROOT)
if _tests_root_str in sys.path:
    sys.path.pop(sys.path.index(_tests_root_str))
sys.path.append(_tests_root_str)

# Bridge test packages share the same top-level namespace (`bridge`) as the
# production modules. When pytest collects the unit tests with import mode
# "importlib", it imports them as submodules of the existing `bridge` package.
# We extend the package search paths so that the production modules remain
# importable from within the test namespace.
_TESTS_BRIDGE_PATH = _TESTS_ROOT / "bridge"
prod_bridge = import_module("bridge")
if hasattr(prod_bridge, "__path__"):
    tests_bridge_str = str(_TESTS_BRIDGE_PATH)
    if tests_bridge_str not in prod_bridge.__path__:
        prod_bridge.__path__.append(tests_bridge_str)

for _subpkg in ("adapters", "api_gateway", "external_adapters"):
    try:
        module = import_module(f"bridge.{_subpkg}")
    except ModuleNotFoundError:
        continue
    if hasattr(module, "__path__"):
        tests_sub_path = _TESTS_BRIDGE_PATH / _subpkg
        tests_sub_str = str(tests_sub_path)
        if tests_sub_str not in module.__path__:
            module.__path__.append(tests_sub_str)

_TESTS_AKA_QUALIA_PATH = _TESTS_ROOT / "aka_qualia"
try:
    prod_aka_qualia = import_module("aka_qualia")
except ModuleNotFoundError:
    prod_aka_qualia = None
else:
    if hasattr(prod_aka_qualia, "__path__"):
        tests_aka_qualia_str = str(_TESTS_AKA_QUALIA_PATH)
        if tests_aka_qualia_str not in prod_aka_qualia.__path__:
            prod_aka_qualia.__path__.append(tests_aka_qualia_str)

os.environ.setdefault("LUKHAS_SUPPRESS_MATRIZ_COMPAT_WARNING", "1")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="products")
warnings.filterwarnings(
    "ignore",
    message=r"products\.experience: use via products\.experience",
    category=DeprecationWarning,
)
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
warnings.filterwarnings(
    "ignore",
    message=r"Top-level package 'dream' is deprecated; import 'labs\.consciousness\.dream' instead\..*",
    category=DeprecationWarning,
)
