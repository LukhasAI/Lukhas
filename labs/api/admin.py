import html
import json
import os
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse

from audit.analytics_read import (
    recent_incidents,
    recent_tool_usage,
    summarize_safety_modes,
    summarize_tools,
)
from flags import is_enabled

router = APIRouter(prefix="/admin", tags=["Admin"])


def _require_enabled():
    if not is_enabled("admin_dashboard"):
        raise HTTPException(status_code=404, detail="Admin dashboard disabled")


def require_api_key(x_api_key: Optional[str] = Header(default=None)):
    required = os.getenv("LUKHAS_API_KEY", "")
    if required and x_api_key != required:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _badge(txt, bg, fg):
    return (
        f'<span style="display:inline-block;padding:4px 10px;border-radius:999px;background:{bg};color:{fg};font-weight:600">{html.escape(txt)}</span>'
    )


def _sparkline(points, width=180, height=32, pad=4):
    """Inline SVG sparkline for a list of numeric 'y' values."""
    if not points:
        return f"<svg width='{width}' height='{height}'></svg>"
    ys = [p for p in points if isinstance(p, (int, float))]
    if not ys:
        return f"<svg width='{width}' height='{height}'></svg>"
    y_min, y_max = min(ys), max(ys)
    y_span = (y_max - y_min) or 1.0
    n = len(ys)
    xs = [pad + i * ((width - 2 * pad) / max(1, n - 1)) for i in range(n)]

    def map_y(y):
        # invert y for svg
        return pad + (height - 2 * pad) * (1 - ((y - y_min) / y_span))

    pts = " ".join(f"{xs[i]:.1f},{map_y(ys[i]):.1f}" for i in range(n))
    last = ys[-1]
    return (
        f"<svg width='{width}' height='{height}' aria-label='sparkline'>"
        f"<polyline fill='none' stroke='#0a3da8' stroke-width='2' points='{pts}'/>"
        f"<text x='{width - 4}' y='{height - 4}' text-anchor='end' font-size='10' fill='#333'>{last:.0f} ms</text></svg>"
    )


def _series(endpoint: str, hours: int = 24) -> list[float]:
    """Fetch performance series data for an endpoint."""
    try:
        # Read directly from file for server-side access
        p = Path(".lukhas_perf/k6_series.jsonl")
        now_ms = int(time.time() * 1000)
        win = hours * 3600 * 1000
        out = []
        if p.exists():
            for line in p.open("r", encoding="utf-8"):
                try:
                    row = json.loads(line)
                    if now_ms - int(row.get("ts", 0)) > win:
                        continue
                    v = (row.get("p95") or {}).get(endpoint)
                    if isinstance(v, (int, float)):
                        out.append(v)
                except Exception:
                    continue
        return out[-60:]  # last 60 points
    except Exception:
        return []


def _page(title: str, body: str) -> str:
    head = (
        "<!doctype html><html><head>\n"
        '<meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>'
        "\n<title>" + html.escape(title) + "</title>\n"
        "<style>\n"
        " body{font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:24px}\n"
        " h1,h2{font-weight:600;} .grid{display:grid;gap:16px;grid-template-columns:1fr 1fr}\n"
        " .card{border:1px solid #eee;border-radius:12px;padding:16px} pre{background:#0b0b0b;color:#e6e6e6;padding:12px;border-radius:8px;overflow:auto}\n"
        " table{border-collapse:collapse;width:100%} th,td{border-bottom:1px solid #eee;padding:8px;text-align:left} th{font-weight:600}\n"
        " .muted{color:#666} .ok{color:#0a7d00} .err{color:#b40000} a{text-decoration:none}\n"
        " .pill{display:inline-block;padding:4px 10px;border-radius:999px;background:#f5f5f5;margin-right:8px}\n"
        " nav a{margin-right:12px} nav a.active{font-weight:700}\n"
        "</style></head><body>\n"
        "<nav>\n"
        ' <a href="/admin" class="active">Overview</a>\n'
        ' <a href="/admin/incidents">Incidents</a>\n'
        ' <a href="/admin/tools">Tools & Safety</a>\n'
        "</nav>\n"
    )
    tail = "\n</body></html>"
    return head + body + tail


@router.get("", response_class=HTMLResponse, dependencies=[Depends(require_api_key)])
def admin_index(request: Request):
    _require_enabled()

    # Parse hours from query params
    try:
        hours = int(request.query_params.get("hours", "24"))
        if hours not in (24, 168):
            hours = 24
    except Exception:
        hours = 24

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
    """

    # Performance section with sparklines
    s_health = _series("health", hours)
    s_tools = _series("tools", hours)
    s_openapi = _series("openapi", hours)

    body += f"""
    <div class="card" style="margin-top:16px">
      <h2>Performance (p95)</h2>
      <div class="muted">Window:
        <a href="/admin?hours=24" {'style="font-weight:700"' if hours == 24 else ""}>24h</a> ·
        <a href="/admin?hours=168" {'style="font-weight:700"' if hours == 168 else ""}>7d</a>
      </div>
      <div class="grid" style="grid-template-columns: 1fr 1fr 1fr; margin-top:12px">
        <div><div class="muted">/feedback/health</div>{_sparkline(s_health)}</div>
        <div><div class="muted">/tools/registry</div>{_sparkline(s_tools)}</div>
        <div><div class="muted">/openapi.json</div>{_sparkline(s_openapi)}</div>
      </div>
    </div>
    <div class="card" style="margin-top:16px">
      <h2>Exports</h2>
      <a href="/admin/incidents.csv">Download Incidents CSV</a> ·
      <a href="/admin/tool_usage.csv">Download Tool Usage CSV</a>
    </div>
    """
    return _page("Admin Overview", body)


@router.get("/incidents", response_class=HTMLResponse, dependencies=[Depends(require_api_key)])
def admin_incidents(tool: Optional[str] = Query(None), since_hours: int = Query(168, ge=1, le=24 * 30)):
    _require_enabled()
    rows = recent_incidents(limit=2000)

    # Filter by tool and time window
    now = time.time()
    out = []
    for r in rows:
        ts = (r.get("ts_ms") or r.get("ts") or 0) / (1000 if r.get("ts_ms") else 1)
        if now - ts > since_hours * 3600:
            continue
        if tool and str(r.get("tool", "")).lower() != tool.lower():
            continue
        out.append(r)

    # Render filtered table with filter bar
    body = "<h1>Incidents</h1>"
    body += f"<div class='muted'>Filters: since <b>{since_hours}h</b>"
    if tool:
        body += f" · tool <b>{html.escape(tool)}</b>"
    body += " - "
    body += "<a href='/admin/incidents?since_hours=24'>24h</a> · "
    body += "<a href='/admin/incidents?since_hours=168'>7d</a> · "
    body += "<a href='/admin/incidents'>Clear filters</a>"
    body += "</div>"

    body += "<div class='card' style='margin-top:12px'><table><tr><th>When</th><th>Audit</th><th>Tool</th><th>Reason</th></tr>"
    for r in out:
        tsd = r.get("ts_ms") or r.get("ts")
        aid = r.get("audit_id", "-")
        tl = r.get("tool", "-")
        reason = r.get("reason", "-")
        body += f"<tr><td>{tsd}</td><td><span class='pill'>{html.escape(str(aid))}</span></td><td><code>{html.escape(tl)}</code></td><td>{html.escape(reason)}</td></tr>"
    body += "</table></div>"
    return _page("Admin Incidents", body)


@router.get("/tools", response_class=HTMLResponse, dependencies=[Depends(require_api_key)])
def admin_tools():
    _require_enabled()
    usage = recent_tool_usage(limit=200)
    summary = summarize_tools()
    modes = summarize_safety_modes()
    body = "<h1>Tools & Safety</h1>"
    body += "<div class='card'><h2>Recent Tool Calls</h2><table><tr><th>When</th><th>Tool</th><th>Status</th><th>Duration (ms)</th><th>Args</th></tr>"
    for r in usage:
        body += (
            f"<tr><td>{r.get('ts')}</td><td><code>{html.escape(r.get('tool', '-'))}</code></td>"
            f"<td>{html.escape(r.get('status', '-'))}</td><td>{r.get('duration_ms', '-')}</td>"
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
def incidents_csv(tool: Optional[str] = Query(None), since_hours: int = Query(168, ge=1, le=24 * 30)):
    _require_enabled()
    rows = recent_incidents(limit=5000)

    # Apply same filters as HTML view
    now = time.time()
    flt = []
    for r in rows:
        ts = (r.get("ts_ms") or r.get("ts") or 0) / (1000 if r.get("ts_ms") else 1)
        if now - ts > since_hours * 3600:
            continue
        if tool and str(r.get("tool", "")).lower() != tool.lower():
            continue
        flt.append(r)

    cols = ["ts", "audit_id", "tool", "reason"]
    out = [",".join(cols)]
    for r in flt:
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
