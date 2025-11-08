# Trap dynamic imports of 'candidate*' and print a stacktrace with the importer
import builtins
import importlib
import traceback

_real___import__ = builtins.__import__
_real_import_module = importlib.import_module


def _dump(msg):
    print("\n🚨 CANDIDATE IMPORT TRAP:", msg)
    traceback.print_stack(limit=12)


def _guard___import__(name, *args, **kwargs):
    if name == "labs" or name.startswith("labs."):
        _dump(f"__import__('{name}')")
    return _real___import__(name, *args, **kwargs)


def _guard_import_module(name, *args, **kwargs):
    if name == "labs" or name.startswith("labs."):
        _dump(f"import_module('{name}')")
    return _real_import_module(name, *args, **kwargs)


builtins.__import__ = _guard___import__
importlib.import_module = _guard_import_module

# kick off the suspect import

print("✅ trap finished")
