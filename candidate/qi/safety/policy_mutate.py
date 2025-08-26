# path: qi/safety/policy_mutate.py
from __future__ import annotations

import argparse
import json
import os
import random
import time
from typing import Any, Dict, List, Tuple

import yaml

from .teq_gate import TEQCoupler

DEFAULT_CORPUS = os.path.join(os.path.dirname(__file__), "policy_corpus.yaml")

def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("Corpus YAML must be a mapping.")
    return data

def _fill_placeholders(t: str, placeholders: Dict[str, List[str]], rng: random.Random) -> str:
    out = t
    for key, vals in (placeholders or {}).items():
        token = "{" + key + "}"
        if token in out and isinstance(vals, list) and vals:
            out = out.replace(token, rng.choice(vals))
    return out

def _mutations_for_task(task: str, corpus: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
    seeds = (corpus.get("tasks", {}) or {}).get(task, []) or (corpus.get("tasks", {}) or {}).get("_default_", [])
    attacks = corpus.get("attacks", []) or []
    return seeds, attacks

def fuzz(
    *,
    policy_root: str,
    jurisdiction: str,
    task: str,
    n: int,
    seed: int,
    corpus_path: str = DEFAULT_CORPUS,
    context_base: Dict[str, Any] | None = None,
    require_block_kinds: List[str] | None = None,
) -> Dict[str, Any]:
    """
    Runs n fuzz cases deterministically:
      - choose seeds for task
      - apply random attacks (deterministic via --seed)
      - run TEQ; report which attacks improperly PASS
    """
    rng = random.Random(seed)
    corpus = _load_yaml(corpus_path)
    seeds, attacks = _mutations_for_task(task, corpus)
    placeholders = corpus.get("placeholders", {}) or {}
    if not seeds or not attacks:
        raise ValueError(f"No seeds/attacks available for task={task} in corpus={corpus_path}")

    gate = TEQCoupler(policy_dir=policy_root, jurisdiction=jurisdiction)
    base_ctx = context_base or {
        "provenance": {"inputs": ["seed"], "sources": ["test"]},
        "pii": {}, "pii_masked": False,
        "user_profile": {"age": 21, "user_id": "fuzzer"},
        "tokens_planned": 512
    }

    cases = []
    bad = 0
    start = time.time()

    for i in range(n):
        seed_text = _fill_placeholders(rng.choice(seeds), placeholders, rng)
        atk = rng.choice(attacks)
        text = atk["mutate"].replace("{text}", seed_text)
        ctx = dict(base_ctx)
        ctx["text"] = text

        res = gate.run(task=task, context=ctx)
        allowed = bool(res.allowed)
        reasons = list(res.reasons or [])
        kinds   = [r.get("kind","") for r in res.checks or []] if hasattr(res, "checks") else []

        # determine whether this should have been blocked
        expected_block = False
        must_block_kinds = set(require_block_kinds or [])
        if atk.get("kind") in ("pii","jailbreak","leakage","medical","budget"):
            expected_block = True
        if must_block_kinds:
            expected_block = expected_block or (atk.get("kind") in must_block_kinds)

        improper_pass = (allowed and expected_block)

        case = {
            "id": i,
            "attack_id": atk.get("id"),
            "attack_kind": atk.get("kind"),
            "task": task,
            "allowed": allowed,
            "improper_pass": improper_pass,
            "teq_reasons": reasons,
            "text_sample": text[:240] + ("…" if len(text) > 240 else ""),
        }
        if improper_pass:
            bad += 1
        cases.append(case)

    elapsed = time.time() - start
    summary = {
        "task": task,
        "jurisdiction": jurisdiction,
        "seed": seed,
        "n": n,
        "improper_passes": bad,
        "pass_rate": round((n - bad) / n, 4),
        "elapsed_sec": round(elapsed, 3)
    }
    return {"summary": summary, "cases": cases}

def main():
    ap = argparse.ArgumentParser(description="Lukhas Policy Mutation Fuzzer (deterministic, corpus-driven)")
    ap.add_argument("--policy-root", required=True)
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--task", required=True, help="Task to test (must exist in policy mappings)")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--require-block", nargs="*", default=[], help="Attack kinds that must be blocked or test fails")
    ap.add_argument("--out-json")
    args = ap.parse_args()

    rep = fuzz(
        policy_root=args.policy_root,
        jurisdiction=args.jurisdiction,
        task=args.task,
        n=args.n,
        seed=args.seed,
        corpus_path=args.corpus,
        require_block_kinds=args.require_block
    )

    if args.out_json:
        os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(rep, f, indent=2)

    print(json.dumps(rep, indent=2))
    # strict exit code: fail if any improper pass
    bad = rep["summary"]["improper_passes"]
    raise SystemExit(1 if bad > 0 else 0)

if __name__ == "__main__":
    main()
