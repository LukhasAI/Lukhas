from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from lukhas_pwm.audit.store import audit_log_write, audit_log_read

router = APIRouter(prefix="/audit", tags=["audit"])


@router.post("/log")
def post_audit(bundle: dict):
    """
    Ingest a redacted audit bundle from runtime.
    Expected shape: {audit_id, signals, params, guardian?, explanation?}
    """
    try:
        audit_log_write(bundle)
        return {"status": "ok", "audit_id": bundle.get("audit_id")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{audit_id}")
def get_audit(audit_id: str):
    obj = audit_log_read(audit_id)
    if not obj:
        raise HTTPException(status_code=404, detail="audit bundle not found")
    return JSONResponse(content=obj)


@router.get("/view/{audit_id}", response_class=HTMLResponse)
def view_audit(audit_id: str):
    obj = audit_log_read(audit_id)
    if not obj:
        raise HTTPException(status_code=404, detail="audit bundle not found")

    # Extract safety mode and tool allowlist for badges
    params = obj.get("params", {})
    safety_mode = params.get("safety_mode", "balanced").lower()
    tool_allowlist = params.get("tool_allowlist", [])

    # Safety mode badge styling and tooltips
    badge_config = {
        "strict": {
            "style": "background:#dc3545; color:white;",  # Red
            "tooltip": "STRICT: Lowest temperature, strict tool allowlist, enhanced Guardian validation"
        },
        "balanced": {
            "style": "background:#28a745; color:white;",  # Green  
            "tooltip": "BALANCED: Moderate settings, standard tool allowlist, normal Guardian checks"
        },
        "creative": {
            "style": "background:#007bff; color:white;",  # Blue
            "tooltip": "CREATIVE: Higher temperature, expanded tool allowlist, relaxed constraints"
        }
    }
    
    config = badge_config.get(safety_mode, badge_config["balanced"])
    badge_style = config["style"]
    badge_tooltip = config["tooltip"]

    # Tool allowlist display
    tools_html = ""
    if tool_allowlist:
        tools_list = ", ".join(tool_allowlist)
        tools_html = f"""
        <div class="card" style="margin-top:16px;">
          <h3>🛠️ Allowed Tools</h3>
          <div class="tools-list">
            {', '.join([f'<code>{tool}</code>' for tool in tool_allowlist])}
          </div>
        </div>
        """

    # super-light viewer (no framework)
    html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>LUKHΛS Audit · {audit_id}</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        body {{ font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 24px; }}
        h1 {{ font-weight: 500; }}
        .pill {{ display:inline-block; padding:4px 10px; border-radius:999px; background:#f2f2f2; margin-right:8px; }}
        .safety-badge {{ display:inline-block; padding:6px 12px; border-radius:999px; font-weight:500; text-transform:uppercase; font-size:12px; {badge_style} }}
        pre {{ background:#0b0b0b; color:#e6e6e6; padding:16px; border-radius:8px; overflow:auto; }}
        .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap:16px; }}
        .card {{ border:1px solid #eee; border-radius:12px; padding:16px; }}
        .tools-list code {{ background:#f8f9fa; padding:2px 6px; border-radius:4px; margin-right:8px; }}
        code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
      </style>
    </head>
    <body>
      <h1>
        Audit <span class="pill">{audit_id}</span>
        <span class="safety-badge" title="{badge_tooltip}">{safety_mode}</span>
      </h1>
      <div class="grid">
        <div class="card">
          <h3>⚛️ Signals</h3>
          <pre>{_pretty(obj.get('signals'))}</pre>
        </div>
        <div class="card">
          <h3>🧠 Params</h3>
          <pre>{_pretty(obj.get('params'))}</pre>
        </div>
      </div>
      {tools_html}
      <div class="card" style="margin-top:16px;">
        <h3>🛡️ Guardian</h3>
        <pre>{_pretty(obj.get('guardian'))}</pre>
      </div>
      <div class="card" style="margin-top:16px;">
        <h3>📝 Explanation</h3>
        <pre>{_pretty(obj.get('explanation'))}</pre>
      </div>
      <div class="card" style="margin-top:16px;">
        <h3>📦 Raw Bundle</h3>
        <pre>{_pretty(obj)}</pre>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


def _pretty(x):
    import json

    try:
        return json.dumps(x, indent=2, ensure_ascii=False)
    except Exception:
        return str(x)
