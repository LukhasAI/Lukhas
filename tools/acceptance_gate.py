from __future__ import annotations
import json, re, sys, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
RG = ["rg","-n","--hidden","--glob","!.git"]

def list_added_under_accepted(base="origin/main"):
    out = subprocess.check_output(["git","diff","--name-status",f"{base}...HEAD"], text=True)
    return [line.split()[1] for line in out.splitlines()
            if line.startswith("A") and line.split()[1].startswith("lukhas/") and line.endswith(".py")]

def has_illegal_imports(pyfile: pathlib.Path)->bool:
    txt = pyfile.read_text(encoding="utf-8", errors="ignore")
    return bool(re.search(r'\bimport\s+(candidate|quarantine|archive)\b|from\s+(candidate|quarantine|archive)\s+import', txt))

def has_manifest(mod_root: pathlib.Path)->bool:
    return (mod_root / "MODULE_MANIFEST.json").exists()

def find_module_root(pyfile: pathlib.Path)->pathlib.Path:
    # ascend until leaving lukhas/ or hitting a dir without __init__.py
    p = pyfile.parent
    last = p
    while (p / "__init__.py").exists() and p.as_posix().startswith("lukhas/"):
        last = p
        p = p.parent
    return last

def main():
    base = sys.argv[1] if len(sys.argv)>1 else "origin/main"
    failures=[]
    added = list_added_under_accepted(base)
    for f in added:
        p = ROOT / f
        if not p.exists(): 
            continue
        reasons=[]
        if has_illegal_imports(p):
            reasons.append("illegal import from candidate/quarantine/archive")
        modroot = find_module_root(p)
        if not has_manifest(modroot):
            reasons.append(f"missing MODULE_MANIFEST.json at {modroot}")
        if reasons:
            failures.append((f,reasons))
    if failures:
        print("❌ Acceptance gate failed:")
        for f, rs in failures:
            print(f" - {f}")
            for r in rs: print(f"    • {r}")
        sys.exit(1)
    else:
        print("✅ Acceptance gate: no violations")
        sys.exit(0)

if __name__ == "__main__":
    main()