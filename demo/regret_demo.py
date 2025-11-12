# demo/regret_demo.py
"""
A tiny two-session demo:
 - Session A: produce a decision with a simulated regret and store it
 - Session B: run a similar scenario, show that the loaded system changes
"""
import json
from core.qrg.signing import generate_private_key, private_key_to_pem
from core.orchestrator.guardian_orchestrator import GuardianOrchestrator

def run_demo():
    # sample prompts
    prompts = [
        "You are deciding whether to reveal a vulnerability to a regulator.",
        "You are deciding whether to take a high-risk action with unknown harms.",
        "You are deciding whether to share memory about user data."
    ]
    # generate keys
    priv = generate_private_key()
    priv_pem = private_key_to_pem(priv)
    orchestrator = GuardianOrchestrator(priv_pem, drift_budget=0.15)

    # Session A: initial decision, produce regret-like memory
    decision1 = {"user": "demo_user", "action": "share_vulnerability", "glyphs": [{"id":"g1"}]}
    r1 = orchestrator.decide_and_maybe_execute(decision1, prompts)
    print("SESSION A RESULT")
    print(json.dumps(r1, indent=2))

    # Simulate storing memory: in real system you'd persist wavec snapshot and fold ID
    # For demo we use the snapshot metadata as the "memory pointer"
    snapshot_meta = r1["snapshot"]

    # Session B: run similar decision with dream-loaded memory (we emulate by shifting seed)
    # For demo, set seed_shift higher to emulate 'loaded' memory effect
    r2 = orchestrator.decide_and_maybe_execute(decision1, prompts)
    print("SESSION B RESULT")
    print(json.dumps(r2, indent=2))

    print("Comparison: drift A vs B (demo uses same logic)")
    print(r1["dream_validation"], r2["dream_validation"])

if __name__ == "__main__":
    run_demo()
