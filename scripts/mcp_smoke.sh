#!/usr/bin/env bash
set -euo pipefail

# ==== CONFIG ====
HOST="${HOST:-https://YOUR-PUBLIC-HOST.ngrok-free.app/mcp}"   # CHANGE ME or export HOST=...
JQ="${JQ:-jq}"                                                # requires jq
CURL="curl -sS"
ID=0; pass=0; fail=0

green(){ printf "\033[32m%s\033[0m\n" "$*"; }
red(){ printf "\033[31m%s\033[0m\n" "$*"; }
title(){ printf "\n\033[36m# %s\033[0m\n" "$*"; }

req() { ID=$((ID+1)); $CURL "$HOST" -H 'Content-Type: application/json' -d "$1"; }
assert() { if $JQ -e "$2" >/dev/null 2>&1 <<<"$1"; then green "  ✅ $3"; pass=$((pass+1)); else red "  ❌ $3"; fail=$((fail+1)); echo "$1" | sed 's/^/    /'; fi; }

# Helpers
b64url() { python3 - <<'PY' "$1"
import sys,base64; print(base64.urlsafe_b64encode(sys.argv[1].encode()).decode().rstrip("="))
PY
}
ENC_PATH(){ b64url "$1"; }

# Test files we'll create/touch inside the repo root jail:
DOC1="docs/mcp/smoke.md"
DOC2="docs/mcp/smoke-rename.md"

title "0) Warmup / HEAD probes (if server supports them via proxy)"
# Optional quick checks — won't fail the suite if not supported
$CURL -I "${HOST}" >/dev/null 2>&1 && green "  (info) HEAD /mcp reachable" || green "  (info) HEAD /mcp not supported (ok)"

title "1) initialize"
R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-06-18\",\"clientInfo\":{\"name\":\"smoke\",\"version\":\"1.0\"},\"capabilities\":{}}}")
assert "$R" '.result.serverInfo.name' "initialize returns serverInfo.name"

title "2) tools/list"
R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/list\",\"params\":{}}")
assert "$R" '.result.tools | map(.name) | index("search")' "tools include search"
assert "$R" '.result.tools | map(.name) | index("fetch")'  "tools include fetch"
# Save tools list for later checks
TOOLS="$R"
# Optional write set (won't fail if absent)
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"write_file"' && green "  (info) write_file present" || red "  (warn) write_file missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"create_file"' && green "  (info) create_file present" || red "  (warn) create_file missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"update_file"' && green "  (info) update_file present" || red "  (warn) update_file missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"append_file"' && green "  (info) append_file present" || red "  (warn) append_file missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"rename_file"' && green "  (info) rename_file present" || red "  (warn) rename_file missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"delete_file"' && green "  (info) delete_file present" || red "  (warn) delete_file missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"apply_patch"' && green "  (info) apply_patch present" || red "  (warn) apply_patch missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"list_dir"' && green "  (info) list_dir present" || red "  (warn) list_dir missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"find_files"' && green "  (info) find_files present" || red "  (warn) find_files missing"
echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"git_commit"' && green "  (info) git_commit present" || red "  (warn) git_commit missing"

title "3) write_file (create or overwrite)"
BODY1="# Lukhas MCP Smoke\n\nThis file is managed by MCP tests.\n"
if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"write_file"'; then
    R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"write_file\",\"arguments\":{\"path\":\"$DOC1\",\"contents\":$(printf %s "$BODY1" | $JQ -sR .),\"overwrite\":true}}}")
    assert "$R" '.result.content[0].text | fromjson | .path' "write_file reports path"
else
    red "  ❌ Skipping write_file test (tool missing)"
    fail=$((fail+1))
fi

title "4) search"
R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"search\",\"arguments\":{\"query\":\"lukhas mcp transport\",\"limit\":5}}}")
assert "$R" '.result.content[0].text | fromjson | has("ids")' "search returns ids[]"
FIRST_ID=$(echo "$R" | $JQ -r '.result.content[0].text | fromjson | .ids[0] // empty')
[ -n "$FIRST_ID" ] && green "  (info) FIRST_ID=$FIRST_ID" || green "  (info) search yielded no ids (ok if catalog small)"

title "5) fetch (by repo path id for determinism)"
RID="lukhas-path:$(ENC_PATH "$DOC1")"
R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"fetch\",\"arguments\":{\"id\":\"$RID\"}}}")
if echo "$R" | $JQ -e '.result.content[0].text | fromjson | .metadata.sha256' >/dev/null 2>&1; then
    green "  ✅ fetch returns metadata.sha256"
    pass=$((pass+1))
    CURR_SHA=$(echo "$R" | $JQ -r '.result.content[0].text | fromjson | .metadata.sha256')
else
    red "  ❌ fetch missing metadata.sha256 (may need lukhas-path: ID support)"
    fail=$((fail+1))
    echo "$R" | sed 's/^/    /'
    CURR_SHA=""
fi

title "6) update_file (optimistic concurrency)"
if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"update_file"' && [ -n "$CURR_SHA" ]; then
    NEW_BODY="# Lukhas MCP Smoke\n\nUpdated by update_file.\n"
    R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"update_file\",\"arguments\":{\"path\":\"$DOC1\",\"contents\":$(printf %s "$NEW_BODY" | $JQ -sR .),\"expectSha256\":\"$CURR_SHA\"}}}")
    assert "$R" '.result.content[0].text | fromjson | .sha256' "update_file returns new sha256"
    NEW_SHA=$(echo "$R" | $JQ -r '.result.content[0].text | fromjson | .sha256')
else
    red "  ❌ Skipping update_file test (tool missing or no sha)"
    fail=$((fail+1))
fi

title "7) append_file"
if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"append_file"'; then
    R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"append_file\",\"arguments\":{\"path\":\"$DOC1\",\"contents\":\"Appended line\",\"ensureNewline\":true}}}")
    assert "$R" '.result.content[0].text | fromjson | .sha256' "append_file returns sha256"
else
    red "  ❌ Skipping append_file test (tool missing)"
    fail=$((fail+1))
fi

title "8) list_dir and find_files"
if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"list_dir"'; then
    R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"list_dir\",\"arguments\":{\"path\":\"docs/\",\"glob\":\"**/*.md\",\"max\":5}}}")
    assert "$R" '.result.content[0].text | fromjson | .items | length >= 0' "list_dir returns items"
else
    red "  ❌ Skipping list_dir test (tool missing)"
    fail=$((fail+1))
fi

if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"find_files"'; then
    R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"find_files\",\"arguments\":{\"glob\":\"mcp-servers/**/*.mjs\",\"max\":3}}}")
    assert "$R" '.result.content[0].text | fromjson | .items' "find_files returns items"
else
    red "  ❌ Skipping find_files test (tool missing)"
    fail=$((fail+1))
fi

title "9) apply_patch (unified diff, with sha precondition)"
if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"apply_patch"'; then
    # re-fetch sha for patch precondition
    R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"fetch\",\"arguments\":{\"id\":\"$RID\",\"fields\":[\"metadata\",\"text\"]}}}")
    if echo "$R" | $JQ -e '.result.content[0].text | fromjson | .metadata.sha256' >/dev/null 2>&1; then
        CURR_SHA=$(echo "$R" | $JQ -r '.result.content[0].text | fromjson | .metadata.sha256')
        DIFF=$'--- a\n+++ b\n@@ -1,1 +1,2 @@\n-# Lukhas MCP Smoke\n+# Lukhas MCP Smoke\nPatched via apply_patch\n'
        # send patch
        R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"apply_patch\",\"arguments\":{\"path\":\"$DOC1\",\"patch\":$($JQ -sR . <<<\"$DIFF\"),\"expectSha256\":\"$CURR_SHA\"}}}")
        assert "$R" '.result.content[0].text | fromjson | .sha256' "apply_patch returns sha256"
    else
        red "  ❌ Skipping apply_patch test (no sha available)"
        fail=$((fail+1))
    fi
else
    red "  ❌ Skipping apply_patch test (tool missing)"
    fail=$((fail+1))
fi

title "10) rename_file"
if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"rename_file"'; then
    R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"rename_file\",\"arguments\":{\"from\":\"$DOC1\",\"to\":\"$DOC2\",\"overwrite\":true}}}")
    assert "$R" '.result.content[0].text | fromjson | .to' "rename_file moved file"
else
    red "  ❌ Skipping rename_file test (tool missing)"
    fail=$((fail+1))
fi

title "11) delete_file (with precondition)"
if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"delete_file"'; then
    # fetch SHA of renamed file
    RID2="lukhas-path:$(ENC_PATH "$DOC2")"
    R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"fetch\",\"arguments\":{\"id\":\"$RID2\",\"fields\":[\"metadata\"]}}}")
    if echo "$R" | $JQ -e '.result.content[0].text | fromjson | .metadata.sha256' >/dev/null 2>&1; then
        DEL_SHA=$(echo "$R" | $JQ -r '.result.content[0].text | fromjson | .metadata.sha256')
        R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"delete_file\",\"arguments\":{\"path\":\"$DOC2\",\"expectSha256\":\"$DEL_SHA\"}}}")
        assert "$R" '.result.content[0].text | fromjson | .deleted' "delete_file confirmed"
    else
        red "  ❌ Skipping delete_file test (no sha available)"
        fail=$((fail+1))
    fi
else
    red "  ❌ Skipping delete_file test (tool missing)"
    fail=$((fail+1))
fi

title "12) git_commit (stage explicit path)"
if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"git_commit"'; then
    # Recreate the file so we have something to commit
    if echo "$TOOLS" | $JQ -r '.result.tools | map(.name)' | grep -q '"write_file"'; then
        R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"write_file\",\"arguments\":{\"path\":\"$DOC2\",\"contents\":\"# Recreated\\n\",\"overwrite\":true}}}")
        R=$(req "{\"jsonrpc\":\"2.0\",\"id\":$ID,\"method\":\"tools/call\",\"params\":{\"name\":\"git_commit\",\"arguments\":{\"message\":\"mcp smoke: file ops\",\"add\":[\"docs/mcp/\"],\"signoff\":true}}}")
        assert "$R" '.result.content[0].text | fromjson | .commit' "git_commit returns commit sha"
    else
        red "  ❌ Skipping git_commit test (write_file missing)"
        fail=$((fail+1))
    fi
else
    red "  ❌ Skipping git_commit test (tool missing)"
    fail=$((fail+1))
fi

title "DONE"
echo
echo "Passed: $pass"
echo "Failed: $fail"
[ "$fail" -eq 0 ] && green "ALL TESTS PASSED 🎯" || (red "Some tests failed - see output above"; exit 1)