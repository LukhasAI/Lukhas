import html
import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from lukhas_pwm.audit.analytics_read import (
    recent_incidents,
    recent_tool_usage,
    summarize_safety_modes,
    summarize_tools,
)
from lukhas_pwm.flags.ff import Flags

router = APIRouter(prefix="/admin", tags=["Admin"])


def _require_enabled():
    if not Flags.get("ADMIN_DASHBOARD", default=False):
        raise HTTPException(status_code=404, detail="Admin dashboard disabled")


def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    required = os.getenv("LUKHAS_API_KEY", "")
    if required and x_api_key != required:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _badge(txt, bg, fg):
    return (
        '<span style="display:inline-block;padding:4px 10px;border-radius:999px;'
        f'background:{bg};color:{fg};font-weight:600">{html.escape(txt)}</span>'
    )


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html><head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>
<style>
 body{{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:24px}}
 h1,h2{{font-weight:600;}} .grid{{display:grid;gap:16px;grid-template-columns:1fr 1fr}} 
 .card{{border:1px solid #eee;border-radius:12px;padding:16px}} pre{{background:#0b0b0b;color:#e6e6e6;padding:12px;border-radius:8px;overflow:auto}}
 table{{border-collapse:collapse;width:100%}} th,td{{border-bottom:1px solid #eee;padding:8px;text-align:left}} th{{font-weight:600}}
 .muted{{color:#666}} .ok{{color:#0a7d00}} .err{{color:#b40000}} a{{text-decoration:none}}
 .pill{{display:inline-block;padding:4px 10px;border-radius:999px;background:#f5f5f5;margin-right:8px}}
 nav a{{margin-right:12px}} nav a.active{{font-weight:700}}
</style></head><body>
<nav>
 <a href="/admin" class="active">Overview</a>
 <a href="/admin/incidents">Incidents</a>
 <a href="/admin/tools">Tools & Safety</a>
</nav>
{body}
</body></html>"""


@router.get("", response_class=HTMLResponse, dependencies=[Depends(require_api_key)])
def admin_index():
    _require_enabled()
    modes = summarize_safety_modes()
    tools = summarize_tools()
    tot_tools = sum(v["count"] for v in tools.values()) if tools else 0
    strict = modes.get("strict", 0)
    balanced = modes.get("balanced", 0)
    creative = modes.get("creative", 0)
    badge = (
        _badge("STRICT", "#ffefef", "#b40000")
        if strict >= balanced and strict >= creative
        else (
            _badge("BALANCED", "#eaffea", "#0a7d00")
            if balanced >= creative
            else _badge("CREATIVE", "#eaf1ff", "#0a3da8")
        )
    )
    body = f"""
    <h1>Admin Overview {badge}</h1>
    <div class="grid">
      <div class="card"><h2>Safety Modes (24h)</h2>
        <table><tr><th>Mode</th><th>Count</th></tr>
        <tr><td>strict</td><td>{strict}</td></tr>
        <tr><td>balanced</td><td>{balanced}</td></tr>
        <tr><td>creative</td><td>{creative}</td></tr>
        </table>
        <div class="muted">Approximate, derived from tool usage logs.</div>
      </div>
      <div class="card"><h2>Tool Usage (24h)</h2>
        <table><tr><th>Tool</th><th>Count</th><th>OK</th><th>Error</th><th>p95 (ms)</th></tr>
    """
    for name, s in tools.items():
        body += (
            f"<tr><td><code>{html.escape(name)}</code></td><td>{s['count']}</td>"
            f"<td class='ok'>{s['ok']}</td><td class='err'>{s['error']}</td><td>{s['p95_ms'] or '-'}</td></tr>"
        )
    body += f"""</table>
        <div class="muted">Total calls: {tot_tools}</div>
      </div>
    </div>
    <div class="card" style="margin-top:16px">
      <h2>Exports</h2>
      <a href="/admin/incidents.csv">Download Incidents CSV</a> ·
      <a href="/admin/tool_usage.csv">Download Tool Usage CSV</a>
    </div>
    """
    return _page("Admin Overview", body)


@router.get(
    "/incidents", response_class=HTMLResponse, dependencies=[Depends(require_api_key)]
)
def admin_incidents():
    _require_enabled()
    rows = recent_incidents(limit=200)
    body = "<h1>Incidents</h1><div class='card'><table><tr><th>When</th><th>Audit</th><th>Tool</th><th>Reason</th></tr>"
    for r in rows:
        ts = r.get("ts_ms") or r.get("ts") or 0
        aid = r.get("audit_id", "-")
        tool = r.get("tool", "-")
        reason = r.get("reason", "-")
        body += f"<tr><td>{ts}</td><td><span class='pill'>{html.escape(str(aid))}</span></td><td><code>{html.escape(tool)}</code></td><td>{html.escape(reason)}</td></tr>"
    body += "</table></div>"
    return _page("Admin Incidents", body)


@router.get(
    "/tools", response_class=HTMLResponse, dependencies=[Depends(require_api_key)]
)
def admin_tools():
    _require_enabled()
    usage = recent_tool_usage(limit=200)
    summary = summarize_tools()
    modes = summarize_safety_modes()
    body = "<h1>Tools & Safety</h1>"
    body += "<div class='card'><h2>Recent Tool Calls</h2><table><tr><th>When</th><th>Tool</th><th>Status</th><th>Duration (ms)</th><th>Args</th></tr>"
    for r in usage:
        body += (
            f"<tr><td>{r.get('ts')}</td><td><code>{html.escape(r.get('tool','-'))}</code></td>"
            f"<td>{html.escape(r.get('status','-'))}</td><td>{r.get('duration_ms','-')}</td>"
            f"<td><code>{html.escape((r.get('args_summary') or '')[:120])}</code></td></tr>"
        )
    body += "</table></div>"
    body += (
        "<div class='card' style='margin-top:16px'><h2>Summary (24h)</h2><pre>"
        + html.escape(json.dumps({"modes": modes, "tools": summary}, indent=2))
        + "</pre></div>"
    )
    return _page("Admin Tools & Safety", body)


# --- Exports (CSV/JSON) ---


@router.get(
    "/incidents.csv",
    response_class=PlainTextResponse,
    dependencies=[Depends(require_api_key)],
)
def incidents_csv():
    _require_enabled()
    rows = recent_incidents(limit=1000)
    cols = ["ts", "audit_id", "tool", "reason"]
    out = [",".join(cols)]
    for r in rows:
        out.append(",".join(str(r.get(k, "")) for k in cols))
    return "\n".join(out)


@router.get(
    "/tool_usage.csv",
    response_class=PlainTextResponse,
    dependencies=[Depends(require_api_key)],
)
def tool_usage_csv():
    _require_enabled()
    rows = recent_tool_usage(limit=2000)
    cols = ["ts", "tool", "status", "duration_ms", "args_summary"]
    out = [",".join(cols)]
    for r in rows:
        out.append(",".join(str(r.get(k, "")) for k in cols))
    return "\n".join(out)


@router.get(
    "/summary.json",
    response_class=JSONResponse,
    dependencies=[Depends(require_api_key)],
)
def summary_json(window_s: int = Query(24 * 3600, ge=60, le=7 * 24 * 3600)):
    _require_enabled()
    return {
        "modes": summarize_safety_modes(window_s=window_s),
        "tools": summarize_tools(window_s=window_s),
    }
