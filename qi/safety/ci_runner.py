from __future__ import annotations
import argparse, json, os, subprocess, sys, shutil

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
    ap.add_argument("--max-mutation-passes", type=int, default=2, help="Max allowed mutated cases that incorrectly pass")
    ap.add_argument("--out-json")
    args = ap.parse_args()

    results = {"steps": []}
    failed = False

    def step(name, cmd):
        rc, out = run(cmd)
        results["steps"].append({"name": name, "rc": rc, "cmd": " ".join(cmd), "out": out})
        return rc, out

    # 1) coverage report
    rc, _ = step("policy_report",
        [sys.executable, "-m", "qi.safety.policy_report",
         "--policy-root", args.policy_root, "--jurisdiction", args.jurisdiction])
    failed |= (rc != 0)

    # 2) linter
    rc, _ = step("policy_linter",
        [sys.executable, "-m", "qi.safety.policy_linter",
         "--policy-root", args.policy_root, "--jurisdiction", args.jurisdiction])
    failed |= (rc != 0)

    # 3) TEQ tests
    rc, _ = step("teq_tests",
        [sys.executable, "-m", "qi.safety.teq_gate",
         "--policy-root", args.policy_root, "--jurisdiction", args.jurisdiction, "--run-tests"])
    failed |= (rc != 0)

    # 4) mutation fuzzer
    rc, out = step("policy_mutate",
        [sys.executable, "-m", "qi.safety.policy_mutate",
         "--policy-root", args.policy_root, "--jurisdiction", args.jurisdiction, "--n", str(args.mutations)])

    # count how many mutated inputs were (incorrectly) allowed
    try:
        mutated = json.loads(out)
        bad = sum(1 for r in mutated if r.get("allowed", True) is True)
    except Exception:
        bad = args.max_mutation_passes + 1  # fail if we can't parse
    if bad > args.max_mutation_passes:
        failed = True
        results["mutation_violation"] = {
            "allowed_count": bad,
            "cap": args.max_mutation_passes
        }

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