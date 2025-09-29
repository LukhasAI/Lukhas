# Thin package to enable file-level shims; actual code proxied by parent __getattr__
from .. import core  # re-export via parent alias
# Optional: expose selected names
for _k in dir(core):
    if not _k.startswith("_"):
        globals()[_k] = getattr(core, _k)