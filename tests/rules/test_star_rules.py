import json
import re
from pathlib import Path

RULES = json.loads(Path("configs/star_rules.json").read_text(encoding="utf-8"))

CANON = set(RULES["canonical_stars"])
ALIAS = RULES.get("aliases", {})
CAP_OVR = {r["capability"]: r["star"] for r in RULES.get("capability_overrides", [])}
NODE_OVR = {r["node"]: r["star"] for r in RULES.get("node_overrides", [])}
RULES_RX = [(re.compile(r["pattern"], re.I), r["star"]) for r in RULES.get("rules", [])]
EXCL_RX  = [re.compile(r["pattern"], re.I) for r in RULES.get("exclusions", [])]
CONF_MIN = float(RULES["confidence"]["min_suggest"])
W = RULES["weights"]

def suggest_star(path_str: str, name: str, caps: list[str], nodes: list[str], owner: str = "", deps: list[str] = None):
    deps = deps or []
    # block by exclusions
    for rx in EXCL_RX:
        if rx.search(path_str):
            return None, 0.0, "excluded"

    candidates = []
    # caps
    for c in caps:
        if c in CAP_OVR:
            candidates.append((CAP_OVR[c], W["capability_override"], f"cap:{c}"))
    # nodes
    for n in nodes:
        if n in NODE_OVR:
            candidates.append((NODE_OVR[n], W["node_override"], f"node:{n}"))
    # path/name rules
    for rx, star in RULES_RX:
        if rx.search(path_str) or (name and rx.search(name)):
            candidates.append((star, W["path_regex"], f"rx:{rx.pattern}"))

    if not candidates:
        return None, 0.0, "none"

    candidates.sort(key=lambda x: (x[1], x[0]), reverse=True)
    best = candidates[0]
    if best[1] < CONF_MIN:  # simple threshold
        return None, best[1], "below_threshold"
    return best

def test_canonical_has_oracle_not_ambiguity():
    assert "🔮 Oracle (Quantum)" in CANON
    assert "⚛️ Ambiguity (Quantum)" not in CANON

def test_flow_by_path_or_node():
    star, conf, _ = suggest_star("candidate/consciousness/awareness", "awareness", [], ["attention"])
    assert star == "🌊 Flow (Consciousness)"
    assert conf >= 0.5

def test_memory_by_capability():
    star, conf, _ = suggest_star("candidate/bio/memory", "bio.memory", ["memory_consolidation"], [])
    assert star == "✦ Trail (Memory)"

def test_guardian_by_auth_capability():
    star, conf, _ = suggest_star("candidate/api/oidc", "oidc", ["authentication"], [])
    assert star == "🛡️ Watch (Guardian)"

def test_vision_by_path():
    star, conf, _ = suggest_star("tools/vision/ocr", "ocr", ["ocr"], [])
    assert star == "🔬 Horizon (Vision)"

def test_oracle_by_keyword():
    star, conf, _ = suggest_star("candidate/bio/quantum_attention", "quantum_attention", ["quantum_attention"], [])
    assert star == "🔮 Oracle (Quantum)"

def test_exclusion_stopwatch_not_guardian():
    star, conf, why = suggest_star("utils/stopwatch", "stopwatch", [], [])
    assert star is None
    assert why == "excluded"
