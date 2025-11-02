from __future__ import annotations

import datetime
import json
import os
import sys


def _md_code_block(text: str, lang: str = "") -> str:
    return f"```{lang}\n{text}\n```"


def _summarize(steps):
    rows = []
    for s in steps:
        name = s.get("name")
        rc = s.get("rc")
        status = "✅ PASS" if rc == 0 else "❌ FAIL"
        rows.append((name, status, s.get("cmd", "").strip()))
    return rows


def _mut_summary(results):
    mv = results.get("mutation_violation")
    if not mv:
        return "No mutation violations. ✅"
    return f"**Mutation violation**: {mv['allowed_count']} > cap {mv['cap']} ❌"


def render_markdown(report: dict) -> str:
    ts = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")  # noqa: F821  # TODO: timezone
    steps = report.get("steps", [])
    rows = _summarize(steps)
    lines = []
    lines.append("# 🔐 Safety CI Report")
    lines.append(f"_Generated: {ts}_")
    lines.append("")
    lines.append("## Steps")
    lines.append("| Step | Status | Command |")
    lines.append("|---|---|---|")
    for name, status, cmd in rows:
        lines.append(f"| `{name}` | {status} | `{cmd}` |")
    lines.append("")
    lines.append("## Mutation Fuzzer")
    lines.append(_mut_summary(report))
    lines.append("")
    # include raw JSON collapsed in a code block for debugging
    lines.append("<details><summary>Raw JSON</summary>")
    lines.append("")
    lines.append(_md_code_block(json.dumps(report, indent=2), "json"))
    lines.append("</details>")
    return "\n".join(lines)


def main():
    out_json = os.environ.get("SAFETY_CI_JSON") or os.path.expanduser(
        f"{os.environ.get('LUKHAS_STATE', os.path.expanduser('~/.lukhas/state'))}/safety_ci.json"
    )
    if not os.path.exists(out_json):
        print(f"Cannot find report JSON at {out_json}", file=sys.stderr)
        sys.exit(1)
    report = json.load(open(out_json, encoding="utf-8"))
    md = render_markdown(report)

    # Write alongside JSON
    md_path = out_json.replace(".json", ".md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(md_path)

    # GitHub Actions: append to job summary if available
    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        with open(gh_summary, "a", encoding="utf-8") as f:
            f.write(md + "\n")

    # Print to stdout so you can see it locally too
    print(md)


if __name__ == "__main__":
    main()
