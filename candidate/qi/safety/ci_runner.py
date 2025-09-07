from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import streamlit as st

from consciousness.qi import qi

HERE = os.path.dirname(__file__)
POLICY_ROOT = os.path.join(HERE, "policy_packs")


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out = []
    for line in p.stdout:  # type: ignore
        out.append(line)
    rc = p.wait()
    return rc, "".join(out)


def main():
    ap = argparse.ArgumentParser(description="Lukhas Safety CI Runner")
    ap.add_argument("--policy-root", default=POLICY_ROOT)
    ap.add_argument("--jurisdiction", default="global")
    ap.add_argument("--mutations", type=int, default=25)
    ap.add_argument(
        "--max-mutation-passes",
        type=int,
        default=2,
        help="Max allowed mutated cases that incorrectly pass",
    )
    ap.add_argument("--out-json")
    args = ap.parse_args()

    results = {"steps": []}
    failed = False

    def step(name, cmd):
        rc, out = run(cmd)
        results["steps"].append({"name": name, "rc": rc, "cmd": " ".join(cmd), "out": out})
        return rc, out

    # 1) coverage report
    rc, _ = step(
        "policy_report",
        [
            sys.executable,
            "-m",
            "qi.safety.policy_report",
            "--policy-root",
            args.policy_root,
            "--jurisdiction",
            args.jurisdiction,
        ],
    )
    failed |= rc != 0

    # 2) linter
    rc, _ = step(
        "policy_linter",
        [
            sys.executable,
            "-m",
            "qi.safety.policy_linter",
            "--policy-root",
            args.policy_root,
            "--jurisdiction",
            args.jurisdiction,
        ],
    )
    failed |= rc != 0

    # 3) TEQ tests
    rc, _ = step(
        "teq_tests",
        [
            sys.executable,
            "-m",
            "qi.safety.teq_gate",
            "--policy-root",
            args.policy_root,
            "--jurisdiction",
            args.jurisdiction,
            "--run-tests",
        ],
    )
    failed |= rc != 0

    # 4) mutation fuzzer for specific tasks
    tasks_to_fuzz = ["generate_summary", "answer_medical"]  # adjust as you like
    for t in tasks_to_fuzz:
        rc, out = step(
            f"policy_mutate:{t}",
            [
                sys.executable,
                "-m",
                "qi.safety.policy_mutate",
                "--policy-root",
                args.policy_root,
                "--jurisdiction",
                args.jurisdiction,
                "--task",
                t,
                "--n",
                "40",
                "--seed",
                "1337",
                "--corpus",
                os.path.join(os.path.dirname(__file__), "policy_corpus.yaml"),
                "--require-block",
                "pii",
                "jailbreak",
                "leakage",
            ],
        )
        failed |= rc != 0

    # write out
    if args.out_json:
        os.makedirs(os.path.dirname(args.out_json), exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    # final status
    print(json.dumps(results, indent=2))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
