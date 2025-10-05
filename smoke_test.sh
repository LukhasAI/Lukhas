#!/bin/bash

# ==== CONFIG ====
# Change HOST to your MCP endpoint:
HOST="http://localhost:8766/mcp"
# HOST="https://YOUR-NGROK-HOST.ngrok-free.app/mcp"

# If you enabled API keys on your MCP, set one header below:
API_H=""
# Or leave API_H empty if no auth:
# API_H=""

J='application/json'

# Helper to POST JSON-RPC
rpc () {
  local body="$1"
  eval curl -s $API_H -H \"Content-Type: $J\" "$HOST" -d \"$body\"
}

echo "🧪 LUKHAS-MCP FILE I/O SMOKE TEST"
echo "=================================="

echo "1) CREATE FILE"
TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PATH1="docs/TEST_MCP_WRITE.md"
BODY1=$(jq -rn --arg p "$PATH1" --arg t "# Lukhas MCP Write Path
created at $TS
" \
  '{jsonrpc:"2.0",id:1,method:"tools/call",params:{name:"create_file",arguments:{path:$p,content:$t}}}')
rpc "$BODY1" | jq .

echo
echo "2) APPEND A LINE"
BODY2=$(jq -rn --arg p "$PATH1" --arg t "appended at $TS
" \
  '{jsonrpc:"2.0",id:2,method:"tools/call",params:{name:"append_file",arguments:{path:$p,content:$t}}}')
rpc "$BODY2" | jq .

echo
echo "3) LIST DIR (filter our file)"
BODY3=$(jq -rn --arg dir "docs" '{jsonrpc:"2.0",id:3,method:"tools/call",params:{name:"list_dir",arguments:{path:$dir,pattern:"TEST_MCP_WRITE*.md"}}}')
rpc "$BODY3" | jq -r '.result.content[0].text' | jq .

echo
echo "4) RENAME/MOVE"
PATH2="docs/TEST_MCP_WRITE_RENAMED.md"
BODY4=$(jq -rn --arg from "$PATH1" --arg to "$PATH2" \
  '{jsonrpc:"2.0",id:4,method:"tools/call",params:{name:"rename_file",arguments:{from:$from,to:$to}}}')
rpc "$BODY4" | jq .

echo
echo "5) DELETE (cleanup)"
BODY5=$(jq -rn --arg p "$PATH2" '{jsonrpc:"2.0",id:5,method:"tools/call",params:{name:"delete_file",arguments:{path:$p}}}')
rpc "$BODY5" | jq .

echo
echo "6) CREATE cockpit.html (minimal) for visual check"
COCKPIT_PATH="mcp-servers/lukhas-devtools-mcp/cockpit.html"
HTML=$(cat <<'EOF'
<!doctype html><meta charset="utf-8">
<title>LUKHAS Cockpit — Smoke</title>
<style>body{font:14px system-ui;background:#0b0d12;color:#e8eef8;padding:16px}pre{background:#111a2a;padding:8px;border-radius:8px}</style>
<h1>It lives 🎛️</h1>
<p>If your server serves static <code>cockpit.html</code>, this page should load. Open console for errors.</p>
<div>
  <input id="whyId" placeholder="canary_... | job_..." style="width:60%">
  <button id="btn">WHY</button>
</div>
<pre id="out"></pre>
<script>
async function rpc(name, args){
  const res = await fetch('/mcp',{method:'POST',headers:{'Content-Type':'application/json'},
    body: JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/call',params:{name,arguments:args}})});
  return res.json();
}
document.getElementById('btn').onclick = async ()=>{
  const id = document.getElementById('whyId').value.trim();
  const res = await rpc('why',{id});
  document.getElementById('out').textContent = res?.result?.content?.[0]?.text || 'no narrative';
};
</script>
EOF
)
BODY6=$(jq -rn --arg p "$COCKPIT_PATH" --arg t "$HTML" \
  '{jsonrpc:"2.0",id:6,method:"tools/call",params:{name:"write_file",arguments:{path:$p,content:$t}}}')
rpc "$BODY6" | jq .

echo
echo "✅ SMOKE TEST COMPLETE!"
echo "Open: http://localhost:8766/cockpit.html   (or your ngrok URL + /cockpit.html)"