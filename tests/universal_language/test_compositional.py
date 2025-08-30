import importlib.util
import re
from pathlib import Path
from typing import Union


def _load_module(module_name: str, rel_path: str):
    root = Path(__file__).resolve().parents[2]
    file_path = root / rel_path
    # Provide a dummy universal_language.constitutional to avoid heavy imports
    import sys
    import types

    if "universal_language" not in sys.modules:
        sys.modules["universal_language"] = types.ModuleType("universal_language")
    # Minimal stubs for submodules to allow import
    if "universal_language.constitutional" not in sys.modules:
        cons = types.ModuleType("universal_language.constitutional")
        cons.get_constitutional_api = lambda: None
        sys.modules["universal_language.constitutional"] = cons
    if "universal_language.core" not in sys.modules:
        core = types.ModuleType("universal_language.core")

        class Symbol:  # type: ignore
            def __init__(
                self,
                id: str = "",
                domain=None,
                name: str = "",
                value: float = 0.0,
                glyph: Union[str, None] = None,
            ):
                self.id, self.domain, self.name, self.value, self.glyph = (
                    id,
                    domain,
                    name,
                    value,
                    glyph,
                )

        class SymbolicDomain:  # type: ignore
            pass

        core.Symbol = Symbol
        core.SymbolicDomain = SymbolicDomain
        sys.modules["universal_language.core"] = core
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


comp_mod = _load_module("ul_compositional", "universal_language/compositional.py")
SymbolProgram = comp_mod.SymbolProgram
SymbolicComposer = getattr(comp_mod, "SymbolComposer", None)
SymbolProgramSynthesizer = comp_mod.SymbolProgramSynthesizer


def test_execute_line_ignores_comments():
    comp = SymbolProgramSynthesizer()
    env = {"operations": {"nop": lambda: None}, "results": {}}
    # Should not raise, should not modify env
    comp._execute_line("# this is a comment", env)
    assert env["results"] == {}


def test_generate_and_execute_simple_program():
    comp = SymbolProgramSynthesizer()
    ops = [{"op": "emit", "symbol": "X"}]
    code = comp._generate_code_from_ops(ops)
    assert re.match(r"^emit\(X\)$", code)
