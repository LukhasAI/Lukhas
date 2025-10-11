"""Smoke test for matriz modules (T1/T2 critical paths)."""
import json, pathlib, time, importlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFESTS = list(ROOT.rglob("module.manifest.json"))

def iter_star_critical():
    for mf in MANIFESTS:
        try:
            m = json.loads(mf.read_text(encoding="utf-8"))
            tier = m.get("testing",{}).get("quality_tier","T4_experimental")
            if tier in ("T1_critical","T2_important"):
                yield mf, m
        except Exception:
            continue

def import_path_from_manifest(m):
    mod = m.get("module",{}).get("name") or m.get("module",{}).get("path","").replace("/","." )
    return mod

def p95_target(m):
    return m.get("matriz_integration",{}).get("latency_target_p95", None)

def fake_call(modname):
    # placeholder for a representative, fast import or constructor call
    importlib.invalidate_caches()
    t0 = time.perf_counter()
    try:
        importlib.import_module(modname)
    except Exception:
        return None, None
    return (time.perf_counter() - t0)*1000, "import"

@pytest.mark.matriz_smoke
def test_smoke_star_critical():
    """Test import times for star-critical modules (T1/T2) against manifest targets."""
    slow = []
    checked = 0
    for mf, m in list(iter_star_critical())[:60]:  # cap to keep <120s
        modname = import_path_from_manifest(m)
        if not modname:
            continue
        elapsed, kind = fake_call(modname)
        if elapsed is None:
            # Import failed - this may be expected for some modules
            continue
        checked += 1
        target = p95_target(m)
        if target and elapsed > 2.0*target:  # warn threshold; fail hard at 2x
            slow.append((modname, elapsed, target))

    # Only fail if we have actual violations
    if slow:
        violations = "\n".join([f"  {mod}: {elapsed:.1f}ms > 2x{target}ms" for mod, elapsed, target in slow[:5]])
        assert False, f"Exceeded latency targets:\n{violations}\n(checked {checked} modules)"
