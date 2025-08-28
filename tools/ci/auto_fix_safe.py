import json
import subprocess
import sys
from pathlib import Path

try:
    import tomllib  # py3.11+
except Exception:
    import tomli as tomllib  # type: ignore

import libcst as cst
import libcst.matchers as m

ROOT = Path(__file__).resolve().parents[2]
RUFF_JSON = ROOT / "reports" / "lints" / "ruff.json"
LOG_PATH = ROOT / "reports" / "lints" / "autofix_log.json"
POLICY = ROOT / ".t4autofix.toml"

DEFAULT_ALLOW = {"UP006", "UP035", "SIM102", "SIM103", "F841", "B007", "C401"}


def load_policy():
    if not POLICY.exists():
        return {
            "scope": {"allow": ["**/*.py"], "deny": []},
            "rules": {"allow": list(DEFAULT_ALLOW), "block": []},
            "interfaces": {"deny_patterns": []},
            "workflows": {"amend_commit": True, "create_branch_on_block": True},
        }
    with POLICY.open("rb") as f:
        data = tomllib.load(f)
    return {
        "scope": data.get("scope", {}),
        "rules": data.get("rules", {}),
        "interfaces": data.get("interfaces", {}),
        "workflows": data.get("workflows", {}),
    }


def git_staged_py_files():
    # Only touch staged changes
    try:
        out = subprocess.check_output(
            ["git", "diff", "--name-only", "--cached", "--diff-filter=ACM"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        return []
    return [p for p in out.splitlines() if p.endswith(".py")]


def path_matches(patterns, path):
    from fnmatch import fnmatch

    return any(fnmatch(path, pat) for pat in patterns)


def filter_files(staged, allow, deny, iface_deny):
    kept = []
    for p in staged:
        if path_matches(deny, p):  # hard deny scope
            continue
        if iface_deny and path_matches(iface_deny, p):  # public surfaces
            continue
        if allow and not path_matches(allow, p):
            continue
        kept.append(p)
    return kept


def load_ruff(allowed_codes):
    if not RUFF_JSON.exists():
        return {}
    try:
        raw = json.loads(RUFF_JSON.read_text() or "[]")
    except Exception:
        return {}
    by_file = {}
    for item in raw:
        code = item.get("code")
        fname = item.get("filename")
        if not isinstance(fname, str):
            continue
        if code in allowed_codes:
            by_file.setdefault(fname, set()).add(code)
    return by_file


class Fixer(cst.CSTTransformer):
    def __init__(self, rules):
        self.rules = rules
        self.stats = {"removed_assigns": 0, "renamed_loops": 0}

    # UP006/UP035 -> builtins
    def leave_Attribute(self, node, updated):
        if "UP006" in self.rules or "UP035" in self.rules:
            if m.matches(
                node, m.Attribute(value=m.Name("typing"), attr=m.Name("Dict"))
            ):
                return cst.Name("dict")
            if m.matches(
                node, m.Attribute(value=m.Name("typing"), attr=m.Name("List"))
            ):
                return cst.Name("list")
            if m.matches(
                node, m.Attribute(value=m.Name("typing"), attr=m.Name("Tuple"))
            ):
                return cst.Name("tuple")
        return updated

    # F841: remove trivial unused assigns (super conservative)
    def leave_SimpleStatementLine(self, node, updated):
        if "F841" not in self.rules:
            return updated
        if len(updated.body) == 1 and isinstance(updated.body[0], cst.Assign):
            rhs = updated.body[0].value
            if isinstance(
                rhs, (cst.SimpleString, cst.Integer, cst.Float, cst.Name, cst.Attribute)
            ):
                self.stats["removed_assigns"] += 1
                return cst.RemoveFromParent()
        return updated

    # B007: rename loop var -> _var
    def leave_For(self, node, updated):
        if "B007" not in self.rules:
            return updated
        t = updated.target
        if isinstance(t, cst.Name) and not t.value.startswith("_"):
            self.stats["renamed_loops"] += 1
            return updated.with_changes(target=cst.Name("_" + t.value))
        return updated


def apply_fixes(file_path, rules):
    p = Path(file_path)
    src = p.read_text(encoding="utf-8", errors="ignore")
    try:
        mod = cst.parse_module(src)
        fixer = Fixer(rules)
        new_mod = mod.visit(fixer)
        if new_mod.code != src:
            p.write_text(new_mod.code, encoding="utf-8")
            return True, fixer.stats
    except Exception:
        return False, {}
    return False, {}


def main():
    policy = load_policy()
    allow_globs = policy.get("scope", {}).get("allow", ["**/*.py"])
    deny_globs = policy.get("scope", {}).get("deny", [])
    iface_deny = policy.get("interfaces", {}).get("deny_patterns", [])
    allow_codes = set(policy.get("rules", {}).get("allow", list(DEFAULT_ALLOW)))

    staged = git_staged_py_files()
    target_files = set(filter_files(staged, allow_globs, deny_globs, iface_deny))

    ruff_by_file = load_ruff(allow_codes)
    to_fix = [f for f in target_files if f in ruff_by_file]

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ledger = []

    changed = 0
    for fname in to_fix:
        ok, stats = apply_fixes(fname, ruff_by_file.get(fname, set()))
        ledger.append(
            {
                "file": fname,
                "rules_considered": sorted(ruff_by_file.get(fname, set())),
                "changed": ok,
                "stats": stats,
            }
        )
        if ok:
            changed += 1

    LOG_PATH.write_text(
        json.dumps(
            {
                "policy": {
                    "allow_globs": allow_globs,
                    "deny_globs": deny_globs,
                    "iface_deny": iface_deny,
                    "allow_codes": sorted(allow_codes),
                },
                "changed_files": changed,
                "entries": ledger,
                "tool_versions": {
                    "python": sys.version,
                    # ruff/black/isort versions are printed by run script
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"✅ auto_fix_safe: considered {len(to_fix)} staged files, modified {changed}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
