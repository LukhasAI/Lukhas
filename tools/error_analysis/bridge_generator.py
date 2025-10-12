#!/usr/bin/env python3
"""Automated Bridge Generator for LUKHAS.

Generates bridge modules following the canonical pattern:
website → candidate → root with graceful fallbacks.

Usage:
    python tools/error_analysis/bridge_generator.py <module_name>
    python tools/error_analysis/bridge_generator.py --batch <module_list_file>

Examples:
    python tools/error_analysis/bridge_generator.py lukhas.consciousness.meta_assessor
    python tools/error_analysis/bridge_generator.py --batch missing_modules.txt
"""
import argparse
import sys
from pathlib import Path
from typing import List

BRIDGE_TEMPLATE = '''"""Bridge for `{module_name}`.

Auto-generated bridge following canonical pattern:
  1) lukhas_website.lukhas.{module_name}
  2) candidate.{module_name}
  3) {root_module}

Graceful fallback to stubs if no backend available.
"""
from __future__ import annotations
from importlib import import_module
from typing import List

__all__: List[str] = []

def _try(n: str):
    try:
        return import_module(n)
    except Exception:
        return None

# Try backends in order
_CANDIDATES = (
    "lukhas_website.lukhas.{module_name}",
    "candidate.{module_name}",
    "{root_module}",
)

_SRC = None
for _cand in _CANDIDATES:
    _m = _try(_cand)
    if _m:
        _SRC = _m
        for _k in dir(_m):
            if not _k.startswith("_"):
                globals()[_k] = getattr(_m, _k)
                __all__.append(_k)
        break

# Add expected symbols as stubs if not found
{stub_definitions}

def __getattr__(name: str):
    """Lazy attribute access fallback."""
    if _SRC and hasattr(_SRC, name):
        return getattr(_SRC, name)
    raise AttributeError(f"module '{{__name__}}' has no attribute '{{name}}'")
'''

STUB_TEMPLATE = '''
if "{symbol}" not in globals():
    class {symbol}:  # pragma: no cover - stub
        """Stub for {symbol}."""
        def __init__(self, *a, **kw):
            pass
        def __call__(self, *a, **kw):
            return None
    __all__.append("{symbol}")'''


class BridgeGenerator:
    """Generates bridge modules following LUKHAS patterns."""
    
    def __init__(self, base_path: Path = Path(".")):
        self.base_path = base_path
    
    def generate_bridge(self, module_name: str, expected_symbols: List[str] = None) -> Path:
        """Generate a bridge module for the given module name."""
        # Determine paths
        if module_name.startswith('lukhas.'):
            # lukhas.x.y.z → lukhas/x/y/z
            rel_path = module_name.replace('.', '/')
            root_module = module_name[len('lukhas.'):]
        elif module_name.startswith('labs.'):
            # candidate.x.y.z → candidate/x/y/z
            rel_path = module_name.replace('.', '/')
            root_module = module_name[len('labs.'):]
        else:
            # x.y.z → x/y/z
            rel_path = module_name.replace('.', '/')
            root_module = module_name
        
        bridge_path = self.base_path / rel_path
        bridge_path.mkdir(parents=True, exist_ok=True)
        
        # Generate stub definitions
        stub_defs = ""
        if expected_symbols:
            for symbol in expected_symbols:
                stub_defs += STUB_TEMPLATE.format(symbol=symbol)
        
        # Write bridge file
        bridge_file = bridge_path / "__init__.py"
        content = BRIDGE_TEMPLATE.format(
            module_name=module_name,
            root_module=root_module,
            stub_definitions=stub_defs if stub_defs else "# No pre-defined stubs"
        )
        
        bridge_file.write_text(content)
        
        # Ensure parent __init__.py files exist
        current = bridge_path.parent
        while current != self.base_path and not (current / "__init__.py").exists():
            init_file = current / "__init__.py"
            init_file.write_text(f'"""Package: {current.name}."""\n')
            current = current.parent
        
        return bridge_file
    
    def generate_batch(self, module_list_file: Path, expected_symbols_map: dict = None) -> List[Path]:
        """Generate bridges for a batch of modules."""
        with open(module_list_file) as f:
            modules = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        generated = []
        for module in modules:
            # Check if line has format: module_name:symbol1,symbol2
            if ':' in module:
                module_name, symbols_str = module.split(':', 1)
                symbols = [s.strip() for s in symbols_str.split(',')]
            else:
                module_name = module
                symbols = expected_symbols_map.get(module_name, []) if expected_symbols_map else []
            
            try:
                bridge_file = self.generate_bridge(module_name, symbols)
                generated.append(bridge_file)
                print(f"✅ Generated: {bridge_file}")
            except Exception as e:
                print(f"❌ Failed {module_name}: {e}")
        
        return generated


def main():
    parser = argparse.ArgumentParser(description="Generate bridge modules for LUKHAS")
    parser.add_argument('module', nargs='?', help='Module name to generate bridge for')
    parser.add_argument('--batch', metavar='FILE', help='File with list of modules (one per line)')
    parser.add_argument('--symbols', help='Expected symbols (comma-separated)')
    parser.add_argument('--base-path', default='.', help='Base path for generation (default: .)')
    
    args = parser.parse_args()
    
    generator = BridgeGenerator(Path(args.base_path))
    
    if args.batch:
        batch_file = Path(args.batch)
        if not batch_file.exists():
            print(f"Error: {batch_file} not found")
            sys.exit(1)
        
        generated = generator.generate_batch(batch_file)
        print(f"\nGenerated {len(generated)} bridge modules")
    
    elif args.module:
        symbols = args.symbols.split(',') if args.symbols else []
        bridge_file = generator.generate_bridge(args.module, symbols)
        print(f"✅ Generated: {bridge_file}")
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
