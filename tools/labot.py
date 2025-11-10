from __future__ import annotations
import argparse, json, os, subprocess, sys, textwrap
from pathlib import Path
from fnmatch import fnmatch

try:
    import yaml  # type: ignore
except Exception:
    print("Please: pip install pyyaml", file=sys.stderr); sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CONFIG = ROOT / ".labot" / "config.yml"
PROMPTS_DIR = ROOT / "prompts" / "labot"
REQUESTS_DIR = ROOT / "requests" / "labot"

DEFAULT_WEIGHTS = {"low_coverage": 0.55, "hotness": 0.30, "tier_bias": 0.15}
DEFAULT_TIERS = {"serve": 1, "lukhas": 1, "matriz": 2, "core": 3}

PR_TEMPLATE = """\
title: "test({module}): add coverage for {path_basename}"
labels:
  - labot
  - type:tests
body: |
  # Test Request (ΛBot)

  **Target file:** `{path}`
  **Tier:** {tier}
  **Rationale:** low coverage + high usage signal

  ## Requirements
  - Deterministic tests (freeze time, seeds; no sleeps)
  - Mock external IO (network, LLMs, stores)
  - Focus edge cases + error contracts
  - Coverage target: {cov_goal}%

  ## Notes
  - Protected surface must not be edited.
  - Use the prompt in `prompts/labot/{slug}.md`.
  - This PR is a **draft** from ΛBot and requires human review before merging.
"""

PROMPT_TEMPLATE_SERVE = """\
# LUKHΛS Test Surgeon — SERVE module

**File:** `{path}`
**Goal:** {cov_goal}%+ coverage, deterministic, no network, strong error contracts.

## Must test
- All FastAPI routes and methods
- Auth/headers/middleware behavior (401/403, CORS, trace-ids)
- Request validation (invalid payloads / missing fields)
- Response schema shape (OpenAPI compatibility)
- Streaming / SSE if applicable

## Constraints
- Do not widen try/except or delete tests
- No sleeps; freeze time and pin seeds
- Mock external services (LLMs, stores, analytics)

## Output
- One test file at: `tests/unit/{suite}/test_{slug}.py`
- Run locally:
```
pytest -q tests/unit/{suite}/test_{slug}.py --cov={module} --cov-report=term-missing
```
"""

PROMPT_TEMPLATE_LUKHAS = """\
# LUKHΛS Test Surgeon — LUKHAS module

**File:** `{path}`
**Goal:** {cov_goal}%+ coverage, deterministic, no network.

Focus:
- WebAuthn / JWT flows (positive + negative)
- Feature flags CRUD & evaluation
- Privacy-preserving analytics (no PII leakage)

Constraints:
- No auth weakening; no snapshot test loosening
- Mock external backends
"""

PROMPT_TEMPLATE_MATRIZ = """\
# LUKHΛS Test Surgeon — MATRIZ module (complex logic)

**File:** `{path}`
**Goal:** ≥{cov_goal}% coverage with **metamorphic** checks when possible.

Focus:
- Pipeline invariants (same input class → consistent phase transitions)
- Round-trips / idempotence for symbolic structures
- Error handling for degenerate inputs

Constraints:
- No network; freeze time; pin seeds
- Mock LLM/vector store calls
"""

def sh(cmd: str) -> str:
  return subprocess.check_output(cmd, shell=True, text=True, cwd=ROOT).strip()

def blame_lines(pyfile: str) -> int:
  try:
      out = sh(f"git blame --line-porcelain -- {pyfile} | grep '^author ' | wc -l")
      return int(out or "0")
  except Exception:
      return 0

def read_config():
  cfg = {"weights": DEFAULT_WEIGHTS, "tiers": DEFAULT_TIERS, "plan": {"top_n": 15}}
  if CONFIG.exists():
      cfg.update(yaml.safe_load(CONFIG.read_text()) or {})
  return cfg

def cov_map() -> dict[str, float]:
  """Return per-file coverage ratio in 0..100 (coarse)."""
  xml = REPORTS / "coverage.xml"
  if not xml.exists():
      # attempt to generate minimal coverage xml
      os.system("pytest --cov=. --cov-report=xml:reports/coverage.xml -q")
  try:
      from xml.etree import ElementTree as ET
      root = ET.parse(str(xml)).getroot()
      res: dict[str, float] = {}
      for pkg in root.iter("class"):
          fn = pkg.get("filename")
          ln_rate = pkg.get("line-rate")
          if fn and ln_rate is not None:
              try:
                  res[fn] = float(ln_rate) * 100.0
              except Exception:
                  pass
      return res
  except Exception:
      return {}

def tier_for(path: str, tiers: dict[str,int]) -> int:
  if path.startswith("serve/"): return tiers.get("serve", 1)
  if path.startswith("lukhas/"): return tiers.get("lukhas", 1)
  if path.startswith("matriz/"): return tiers.get("matriz", 2)
  return tiers.get("core", 3)

def score(path: str, cov: float, hot: int, tier: int, w: dict[str,float]) -> float:
  low_cov = 100.0 - cov
  tier_score = 4 - tier  # Tier1=3, Tier2=2, Tier3=1
  return (w["low_coverage"]*low_cov) + (w["hotness"]*min(hot, 500)/500.0*100.0) + (w["tier_bias"]*tier_score*33.3)

def list_py_files() -> list[str]:
  out = sh("git ls-files '*.py'")
  return [s for s in out.splitlines() if not s.startswith("tests/")]

def excluded(path: str, globs: list[str]) -> bool:
  return any(fnmatch(path, g) for g in globs)

def ensure_dirs():
  PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
  REQUESTS_DIR.mkdir(parents=True, exist_ok=True)

def prompt_template_for(path: str) -> tuple[str,str]:
  if path.startswith("serve/"):
      return PROMPT_TEMPLATE_SERVE, "serve"
  if path.startswith("lukhas/"):
      return PROMPT_TEMPLATE_LUKHAS, "lukhas"
  if path.startswith("matriz/"):
      return PROMPT_TEMPLATE_MATRIZ, "matriz"
  return PROMPT_TEMPLATE_SERVE, "core"

def slugify(path: str) -> str:
  return path.replace("/", "_").replace(".py", "")

def plan(top_n: int, cfg):
  w = cfg.get("weights", DEFAULT_WEIGHTS)
  tiers = cfg.get("tiers", DEFAULT_TIERS)
  excludes = cfg.get("plan", {}).get("exclude_globs", [])
  cov = cov_map()
  files = list_py_files()
  scored = []
  for f in files:
      if excluded(f, excludes): continue
      c = cov.get(f, 0.0)
      h = blame_lines(f)
      t = tier_for(f, tiers)
      s = score(f, c, h, t, w)
      scored.append((s, f, c, h, t))
  scored.sort(reverse=True)
  return scored[:top_n]

def gen_requests(candidates: list[tuple[float,str,float,int,int]]):
  ensure_dirs()
  created = []
  for s, path, cov, hot, tier in candidates:
      tpl, suite = prompt_template_for(path)
      slug = slugify(path)
      module = path.split("/")[0]
      cov_goal = 85 if module in ("serve","lukhas") else 70
      prompt = tpl.format(path=path, cov_goal=cov_goal, slug=slug, suite=suite, module=module)
      (PROMPTS_DIR / f"{slug}.md").write_text(prompt, encoding="utf-8")
      pr = PR_TEMPLATE.format(module=module, path=path, path_basename=Path(path).name, tier=tier, cov_goal=cov_goal, slug=slug)
      (REQUESTS_DIR / f"{slug}.pr.yml").write_text(pr, encoding="utf-8")
      created.append({"path": path, "prompt": str(PROMPTS_DIR / f"{slug}.md"), "pr": str(REQUESTS_DIR / f"{slug}.pr.yml")})
  return created

def open_pr_shell(slug: str):
  pr_file = REQUESTS_DIR / f"{slug}.pr.yml"
  if not pr_file.exists():
      print(f"Request missing: {pr_file}", file=sys.stderr); sys.exit(1)
  data = pr_file.read_text()
  # write a placeholder change to make a PR (docs-only change)
  changes = ROOT / "docs" / "labot" / f"{slug}.md"
  changes.parent.mkdir(parents=True, exist_ok=True)
  changes.write_text("# Test Request (ΛBot)\n\nSee prompts/ and PR body.\n", encoding="utf-8")
  branch = f"labot/tests/{slug}"
  os.system(f"git checkout -b {branch}")
  os.system(f"git add {changes} {pr_file} prompts/labot/{slug}.md")
  os.system(f"git commit -m 'chore(labot): request tests for {slug}'")
  # requires gh CLI
  title, body = None, None
  for line in data.splitlines():
      if line.startswith("title:"):
          title = line[len("title:"):].strip().strip('"')
          break
  body = data.split("body:", 1)[-1].strip() if "body:" in data else ""
  os.system(f"gh pr create --draft --title {json.dumps(title or 'test: add tests')} --body {json.dumps(body)}")
  print(f"Opened draft PR for {slug} on branch {branch}")

def main():
  ap = argparse.ArgumentParser(description="ΛBot v0.1 — Stage-A test planner")
  ap.add_argument("--mode", choices=["plan","gen","plan+gen","open-pr"], default="plan")
  ap.add_argument("--top", type=int, default=None, help="override top_n")
  ap.add_argument("--slug", help="slug to open PR shell (for --mode open-pr)")
  args = ap.parse_args()

  cfg = read_config()
  top_n = args.top or cfg.get("plan", {}).get("top_n", 15)

  if args.mode in ("plan","plan+gen"):
      cands = plan(top_n, cfg)
      out = [{"score": round(s,2), "path": p, "coverage": round(c,2), "hot_lines": h, "tier": t} for s,p,c,h,t in cands]
      REPORTS.mkdir(parents=True, exist_ok=True)
      (REPORTS / "evolve_candidates.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
      print(json.dumps(out, indent=2))

  if args.mode in ("gen","plan+gen"):
      if not (REPORTS / "evolve_candidates.json").exists():
          print("No candidates file; run --mode plan first", file=sys.stderr); sys.exit(1)
      cands = json.loads((REPORTS / "evolve_candidates.json").read_text())
      tuples = [(c["score"], c["path"], c["coverage"], c["hot_lines"], c["tier"]) for c in cands]
      created = gen_requests(tuples)
      print(json.dumps(created, indent=2))

  if args.mode == "open-pr":
      if not args.slug:
          print("--slug required for open-pr", file=sys.stderr); sys.exit(1)
      open_pr_shell(args.slug)

if __name__ == "__main__":
  main()
