import crypto from 'crypto';
import { promises as fs } from 'fs';
import { createServer } from 'node:http';
import { URL } from 'node:url';
import path from 'path';

const PORT = parseInt(process.env.PORT || "8766");

// === Constants and Utilities ===
const REPO_ROOT = process.env.LUKHAS_REPO_ROOT || path.resolve(process.cwd(), '../../');
const MAX_BYTES = 2 * 1024 * 1024; // 2MB
const REQ_TIMEOUT_MS = 8000;
const FETCH_TTL_MS = Number(process.env.FETCH_TTL_MS ?? 10 * 60 * 1000);
const FETCH_CACHE_MAX = Number(process.env.FETCH_CACHE_MAX ?? 256);

// Simple LRU+TTL cache
const _cache = new Map();
function cacheGet(id) {
    const ent = _cache.get(id);
    if (!ent) return null;
    if (Date.now() - ent.ts > FETCH_TTL_MS) { _cache.delete(id); return null; }
    _cache.delete(id); _cache.set(id, ent); // bump LRU
    return ent.val;
}
function cacheSet(id, val) {
    if (_cache.size >= FETCH_CACHE_MAX) {
        const firstKey = _cache.keys().next().value;
        if (firstKey) _cache.delete(firstKey);
    }
    _cache.set(id, { ts: Date.now(), val });
}

const sha256 = (s) => crypto.createHash('sha256').update(String(s)).digest('hex');
const b64 = (s) => Buffer.from(String(s), 'utf8').toString('base64url');
const unb64 = (s) => Buffer.from(String(s), 'base64url').toString('utf8');

function encodeIdFromPath(repoPath) { return `lukhas-path:${b64(repoPath)}`; }
function tryDecodePathId(id) {
    if (!id?.startsWith('lukhas-path:')) return null;
    try { return unb64(id.slice('lukhas-path:'.length)); } catch { return null; }
}

// Light text normalization utilities
function stripMarkdown(md) {
    return String(md)
        .replace(/```[\s\S]*?```/g, '')
        .replace(/^#{1,6}\s+/gm, '')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
        .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1')
        .replace(/>\s?/g, '')
        .replace(/\*\*|__/g, '')
        .replace(/\*/g, '');
}

function stripHtml(html) {
    return String(html)
        .replace(/<script[\s\S]*?<\/script>/gi, '')
        .replace(/<style[\s\S]*?<\/style>/gi, '')
        .replace(/<\/?[^>]+>/g, '')
        .replace(/&nbsp;/g, ' ')
        .replace(/&amp;/g, '&')
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>');
}

function guessMimeByExt(p) {
    const ext = (p || '').toLowerCase();
    if (ext.endsWith('.md')) return 'text/markdown';
    if (ext.endsWith('.txt')) return 'text/plain';
    if (ext.endsWith('.html') || ext.endsWith('.htm')) return 'text/html';
    if (ext.endsWith('.json')) return 'application/json';
    return 'text/plain';
}

function normalizeText({ body, mimeType, titleHint }) {
    let text = body ?? '';
    if (mimeType === 'text/markdown') text = stripMarkdown(text);
    else if (mimeType === 'text/html') text = stripHtml(text);
    if (mimeType === 'application/json') {
        try { text = JSON.stringify(JSON.parse(text), null, 2); } catch { }
    }
    const title = titleHint || (text.split('\n').find(Boolean) ?? 'Document');
    return { text, title };
}

// Path safety utilities
function resolveSafeAbs(relPath) {
    if (!relPath || typeof relPath !== 'string') throw new Error('Invalid path');
    const norm = path.posix.normalize(relPath.replaceAll('\\', '/')).replace(/^\/+/, '');
    if (norm.includes('..')) throw new Error('Path traversal not allowed');
    const abs = path.resolve(REPO_ROOT, norm);
    if (!abs.startsWith(path.resolve(REPO_ROOT) + path.sep) && path.resolve(REPO_ROOT) !== abs) {
        throw new Error('Path escapes repository root');
    }
    return { abs, norm };
}

async function fileExists(absPath) {
    try { await fs.access(absPath); return true; } catch { return false; }
}

async function readFileUtf8(absPath) {
    return fs.readFile(absPath, 'utf8');
}

// Basic HTTP fetch with timeout + size cap
async function safeFetch(url, opts = {}) {
    const ac = new AbortController();
    const t = setTimeout(() => ac.abort(), REQ_TIMEOUT_MS);
    try {
        const res = await fetch(url, { ...opts, signal: ac.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const reader = res.body.getReader();
        const chunks = [];
        let size = 0;
        for (; ;) {
            const { value, done } = await reader.read();
            if (done) break;
            size += value.length;
            if (size > MAX_BYTES) throw new Error('Response too large');
            chunks.push(value);
        }
        return Buffer.concat(chunks).toString('utf8');
    } finally { clearTimeout(t); }
}

// === fetchById (repo paths, URLs, GitHub) ===
async function fetchById(id) {
    const cached = cacheGet(id);
    if (cached) return cached;

    const repoRel = tryDecodePathId(id);
    if (repoRel) {
        const abs = path.resolve(REPO_ROOT, repoRel);
        const body = await fs.readFile(abs, 'utf8');
        const mimeType = guessMimeByExt(repoRel);
        const { text, title } = normalizeText({ body, mimeType, titleHint: path.basename(repoRel) });
        const githubUrl = process.env.GITHUB_VIEW_BASE ? `${process.env.GITHUB_VIEW_BASE}/${repoRel}` : undefined;
        const out = {
            id, title, url: githubUrl, mimeType: 'text/plain', text,
            metadata: { source: 'lukhas-repo', path: repoRel, mimeType, sha256: sha256(text) }
        };
        cacheSet(id, out); return out;
    }

    if (/^https?:\/\//i.test(id)) {
        const body = await safeFetch(id);
        const mimeType = guessMimeByExt(id);
        const { text, title } = normalizeText({ body, mimeType, titleHint: new URL(id).pathname.split('/').pop() });
        const out = {
            id, title, url: id, mimeType: 'text/plain', text,
            metadata: { source: 'url', mimeType, sha256: sha256(text) }
        };
        cacheSet(id, out); return out;
    }

    if (id.startsWith('gh:')) {
        const m = /^gh:([^/]+)\/([^@]+)@([^:]+):(.+)$/.exec(id);
        if (!m) throw new Error('Invalid gh id format');
        const [, owner, repo, sha, ghPath] = m;
        const raw = `https://raw.githubusercontent.com/${owner}/${repo}/${sha}/${ghPath}`;
        const body = await safeFetch(raw);
        const mimeType = guessMimeByExt(ghPath);
        const { text, title } = normalizeText({ body, mimeType, titleHint: path.basename(ghPath) });
        const url = `https://github.com/${owner}/${repo}/blob/${sha}/${ghPath}`;
        const out = {
            id, title, url, mimeType: 'text/plain', text,
            metadata: { source: 'github', owner, repo, sha, path: ghPath, raw, sha256: sha256(text) }
        };
        cacheSet(id, out); return out;
    }

    const out = {
        id, title: id.slice(0, 64), url: undefined, mimeType: 'text/plain', text: id,
        metadata: { source: 'literal', sha256: sha256(id) }
    };
    cacheSet(id, out); return out;
}

// Minimal in-memory catalog used by lukhasSearch (replace with your index later)
const CATALOG = [
    {
        id: encodeIdFromPath('mcp-servers/lukhas-devtools-mcp/mcp-streamable.mjs'),
        title: 'MCP Streamable Server',
        snippet: 'Enhanced dual-transport MCP server with ops kit functionality...',
        url: process.env.GITHUB_VIEW_BASE
            ? `${process.env.GITHUB_VIEW_BASE}/mcp-servers/lukhas-devtools-mcp/mcp-streamable.mjs`
            : undefined
    },
    {
        id: encodeIdFromPath('README.md'),
        title: 'LUKHAS AI Platform',
        snippet: 'Consciousness-aware AI development platform with Trinity Framework...',
        url: process.env.GITHUB_VIEW_BASE
            ? `${process.env.GITHUB_VIEW_BASE}/README.md`
            : undefined
    }
];

async function lukhasSearch(query, limit = 5) {
    const q = String(query || '').toLowerCase();
    const hits = CATALOG.filter(
        x => x.title.toLowerCase().includes(q) || x.snippet.toLowerCase().includes(q)
    ).slice(0, limit);
    return hits; // each {id,title,snippet,url}
}

// MCP Tools definitions
const MCP_TOOLS = [
    {
        name: "search",
        description: "Search over LUKHΛS sources and return opaque IDs for follow-up fetch.",
        inputSchema: {
            type: "object",
            properties: {
                query: { type: "string" },
                limit: { type: "integer", minimum: 1, maximum: 50, default: 5 }
            },
            required: ["query"]
        }
    },
    {
        name: "fetch",
        description: "Fetch full record by ID returned from `search`.",
        inputSchema: {
            type: "object",
            properties: {
                id: { type: "string" },
                fields: {
                    type: "array",
                    items: { type: "string", enum: ["title", "url", "mimeType", "text", "metadata"] }
                }
            },
            required: ["id"]
        }
    },
    {
        name: "apply_patch",
        description: "Apply unified diff to a file under LUKHAS_REPO_ROOT with sha precondition.",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string" },
                patch: { type: "string" },
                expectSha256: { type: "string" },
                allowCreate: { type: "boolean", default: false }
            },
            required: ["path", "patch", "expectSha256"]
        }
    },
    {
        name: "list_dir",
        description: "List files in a directory (safe filters).",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string" },
                glob: { type: "string" },
                max: { type: "integer", minimum: 1, maximum: 200, default: 50 },
                includeDirs: { type: "boolean", default: false }
            },
            required: ["path"]
        }
    },
    {
        name: "find_files",
        description: "Find files by glob from repo root.",
        inputSchema: {
            type: "object",
            properties: {
                glob: { type: "string" },
                max: { type: "integer", minimum: 1, maximum: 500, default: 100 }
            },
            required: ["glob"]
        }
    },
    {
        name: "git_commit",
        description: "Create a git commit for changes (safe subset).",
        inputSchema: {
            type: "object",
            properties: {
                message: { type: "string" },
                add: { type: "array", items: { type: "string" } },
                signoff: { type: "boolean", default: false },
                stageAll: { type: "boolean", default: false }
            },
            required: ["message"]
        }
    }
];

// MCP Response helpers
function ok(id, result) {
    return { jsonrpc: "2.0", id, result };
}

function err(id, code, message) {
    return { jsonrpc: "2.0", id, error: { code, message } };
}

// Send CORS headers
function setCORSHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, HEAD, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');
}

// Parse JSON body
async function parseJSONBody(req) {
    return new Promise((resolve, reject) => {
        let data = '';
        req.on('data', chunk => { data += chunk; });
        req.on('end', () => {
            try {
                resolve(data ? JSON.parse(data) : {});
            } catch (e) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Handle JSON-RPC requests
async function handleJSONRPC(req, res) {
    try {
        const data = await parseJSONBody(req);
        const { jsonrpc, id, method, params } = data;

        if (jsonrpc !== "2.0") {
            setCORSHeaders(res);
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(err(id, -32600, "Invalid JSON-RPC version")));
            return;
        }

        let result;
        switch (method) {
            case "initialize":
                result = ok(id, {
                    protocolVersion: "2025-06-18",
                    capabilities: { tools: {} },
                    serverInfo: { name: "lukhas-devtools-mcp", version: "1.0.0" }
                });
                break;

            case "tools/list":
                result = ok(id, { tools: MCP_TOOLS });
                break;

            case "tools/call":
                const { name, arguments: args } = params;

                // search → { ids, hits }
                if (name === "search") {
                    const q = String(args?.query ?? "");
                    const limit = Math.max(1, Math.min(50, Number(args?.limit ?? 5)));
                    const hits = await lukhasSearch(q, limit);
                    const ids = hits.map(h => String(h.id));
                    result = ok(id, { content: [{ type: "text", text: JSON.stringify({ ids, hits }) }] });
                    break;
                }

                // fetch({id, fields?})
                if (name === "fetch") {
                    const recId = String(args?.id || "");
                    const doc = await fetchById(recId);
                    let payload = {
                        id: recId,
                        title: doc.title ?? recId,
                        url: doc.url ?? undefined,
                        mimeType: doc.mimeType ?? "text/plain",
                        text: doc.text ?? "",
                        metadata: doc.metadata ?? {}
                    };
                    const fields = Array.isArray(args?.fields) ? args.fields.map(String) : null;
                    if (fields && fields.length) {
                        const keep = new Set(['id', ...fields]);
                        payload = Object.fromEntries(Object.entries(payload).filter(([k]) => keep.has(k)));
                    }
                    result = ok(id, { content: [{ type: "text", text: JSON.stringify(payload) }] });
                    break;
                }

                // apply_patch (unified diff; single-file; sha precondition)
                if (name === "apply_patch") {
                    const rel = String(args?.path || "");
                    const patch = String(args?.patch || "");
                    const expectSha = String(args?.expectSha256 || "");
                    const allowCreate = Boolean(args?.allowCreate ?? false);
                    const { abs, norm } = resolveSafeAbs(rel);
                    const exists = await fileExists(abs);
                    if (!exists && !allowCreate) {
                        result = err(id, -32602, `Missing file: ${norm} (allowCreate=false)`);
                        break;
                    }

                    const original = exists ? await readFileUtf8(abs) : "";
                    const currentSha = sha256(original);
                    if (currentSha !== expectSha && exists) {
                        result = err(id, -32602, `Precondition failed: sha256=${currentSha}`);
                        break;
                    }

                    function applyUnified(baseText, diff) {
                        const lines = diff.replace(/\r\n/g, '\n').split('\n');
                        const hasHeaders = lines.some(l => l.startsWith('--- ')) && lines.some(l => l.startsWith('+++ '));
                        if (!hasHeaders) throw new Error('Invalid unified diff (---/+++ missing)');
                        let idx = lines.findIndex(l => l.startsWith('@@ '));
                        if (idx === -1) throw new Error('Invalid hunk header');
                        const base = baseText.replace(/\r\n/g, '\n').split('\n');
                        let out = [], basePtr = 0;
                        while (idx !== -1) {
                            const m = /^@@\s+-([0-9]+)(?:,([0-9]+))?\s+\+([0-9]+)(?:,([0-9]+))?\s+@@/.exec(lines[idx]);
                            if (!m) throw new Error('Invalid hunk header');
                            const aStart = parseInt(m[1], 10) - 1;
                            out.push(...base.slice(basePtr, aStart));
                            basePtr = aStart;
                            idx++;
                            while (idx < lines.length && !lines[idx].startsWith('@@ ')) {
                                const l = lines[idx];
                                if (l.startsWith('+')) out.push(l.slice(1));
                                else if (l.startsWith('-')) basePtr++;
                                else if (l.startsWith(' ') || l === '') out.push(base[basePtr++] ?? '');
                                idx++;
                            }
                        }
                        out.push(...base.slice(basePtr));
                        return out.join('\n');
                    }

                    let next;
                    try {
                        next = applyUnified(original, patch);
                    } catch (e) {
                        result = err(id, -32602, `Invalid patch: ${e.message}`);
                        break;
                    }

                    await fs.mkdir(path.dirname(abs), { recursive: true });
                    await fs.writeFile(abs, next, 'utf8');
                    const newSha = sha256(next);
                    result = ok(id, {
                        content: [{
                            type: "text", text: JSON.stringify({
                                path: norm, bytesWritten: Buffer.byteLength(next, 'utf8'),
                                previousSha256: exists ? currentSha : null, sha256: newSha, created: !exists
                            })
                        }]
                    });
                    break;
                }

                // list_dir
                if (name === "list_dir") {
                    const dirRel = String(args?.path || "");
                    const glob = args?.glob ? String(args.glob) : null;
                    const max = Math.max(1, Math.min(200, Number(args?.max ?? 50)));
                    const includeDirs = Boolean(args?.includeDirs ?? false);
                    const { abs: dirAbs, norm: dirNorm } = resolveSafeAbs(dirRel);

                    async function walkDir(absRoot, relRoot = "") {
                        const out = [];
                        const entries = await fs.readdir(absRoot, { withFileTypes: true });
                        for (const e of entries) {
                            const rel = path.posix.join(relRoot, e.name);
                            const abs = path.join(absRoot, e.name);
                            if (e.isDirectory()) {
                                out.push({ type: "dir", rel, abs });
                                const sub = await walkDir(abs, rel);
                                out.push(...sub);
                            } else if (e.isFile()) {
                                out.push({ type: "file", rel, abs });
                            }
                        }
                        return out;
                    }

                    function matchGlob(name, pattern) {
                        const esc = s => s.replace(/[-/\\^$+?.()|[\]{}]/g, '\\$&');
                        let rx = esc(pattern).replace(/\\\\*\\\\*/g, '.*').replace(/\\\\*/g, '[^/]*').replace(/\\\\?/g, '.');
                        return new RegExp(`^${rx}$`).test(name);
                    }

                    const entries = await walkDir(dirAbs);
                    let files = entries.filter(e => e.type === "file" || (includeDirs && e.type === "dir"));
                    if (glob) files = files.filter(e => matchGlob(e.rel, glob));
                    const items = files.slice(0, max).map(e => ({ type: e.type, path: path.posix.join(dirNorm, e.rel) }));
                    result = ok(id, { content: [{ type: "text", text: JSON.stringify({ items, truncated: files.length > max }) }] });
                    break;
                }

                // find_files
                if (name === "find_files") {
                    const findGlob = String(args?.glob || "");
                    const findMax = Math.max(1, Math.min(500, Number(args?.max ?? 100)));

                    async function walkDirForFind(absRoot, relRoot = "") {
                        const out = [];
                        const entries = await fs.readdir(absRoot, { withFileTypes: true });
                        for (const e of entries) {
                            const rel = path.posix.join(relRoot, e.name);
                            const abs = path.join(absRoot, e.name);
                            if (e.isDirectory()) {
                                const sub = await walkDirForFind(abs, rel);
                                out.push(...sub);
                            } else if (e.isFile()) {
                                out.push({ type: "file", rel, abs });
                            }
                        }
                        return out;
                    }

                    function matchGlobFind(name, pattern) {
                        const esc = s => s.replace(/[-/\\^$+?.()|[\]{}]/g, '\\$&');
                        let rx = esc(pattern).replace(/\\\\*\\\\*/g, '.*').replace(/\\\\*/g, '[^/]*').replace(/\\\\?/g, '.');
                        return new RegExp(`^${rx}$`).test(name);
                    }

                    const findEntries = await walkDirForFind(REPO_ROOT);
                    let findFiles = findEntries.filter(e => e.type === "file" && matchGlobFind(e.rel, findGlob));
                    const findItems = findFiles.slice(0, findMax).map(e => ({ path: e.rel }));
                    result = ok(id, { content: [{ type: "text", text: JSON.stringify({ items: findItems, truncated: findFiles.length > findMax }) }] });
                    break;
                }

                // git_commit (safe subset, optional stageAll)
                if (name === "git_commit") {
                    const commitMessage = String(args?.message || "").trim();
                    const addList = Array.isArray(args?.add) ? args.add.map(String) : [];
                    const signoff = Boolean(args?.signoff ?? false);
                    const stageAll = Boolean(args?.stageAll ?? false);
                    if (!commitMessage) {
                        result = err(id, -32602, "Commit message required");
                        break;
                    }

                    const ex = async (cmd, argv, cwd = REPO_ROOT) =>
                        (await import('child_process')).execFileSync(cmd, argv, { cwd, encoding: 'utf8' });

                    if (addList.length) {
                        const safe = [];
                        for (const rel of addList) safe.push(resolveSafeAbs(rel).norm);
                        ex('git', ['add', ...safe]);
                    } else if (stageAll) {
                        ex('git', ['add', '-A']);
                    }

                    const fullMsg = signoff ? `${commitMessage}\n\nSigned-off-by: MCP Bot <bot@lukhas.ai>` : commitMessage;
                    let out;
                    try {
                        out = ex('git', ['commit', '-m', fullMsg]);
                    } catch (e) {
                        const msg = String(e?.stdout || e?.stderr || e?.message || '').trim();
                        result = err(id, -32602, `git commit failed: ${msg || 'nothing to commit?'}`);
                        break;
                    }
                    const sha = ex('git', ['rev-parse', 'HEAD']).trim();
                    result = ok(id, { content: [{ type: "text", text: JSON.stringify({ commit: sha, message: commitMessage, staged: addList, stageAll }) }] });
                    break;
                }

                result = err(id, -32601, `Unknown tool: ${name}`);
                break;

            default:
                result = err(id, -32601, `Unknown method: ${method}`);
        }

        setCORSHeaders(res);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result, null, 2));

    } catch (error) {
        setCORSHeaders(res);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(err(null, -32603, error.message)));
    }
}

const server = createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const path = url.pathname;
    const method = req.method;

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        setCORSHeaders(res);
        res.writeHead(200);
        res.end();
        return;
    }

    try {
        // HEAD handlers for ultra-fast liveness checks
        if (method === 'HEAD') {
            setCORSHeaders(res);
            if (path === '/mcp' || path === '/sse') {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end();
                return;
            }
        }

        // SPLIT TRANSPORT: dedicated SSE discovery at /sse (emits endpoint event)
        if (path === '/sse' && method === 'GET') {
            setCORSHeaders(res);
            res.writeHead(200, {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            });
            const host = req.headers.host || `localhost:${PORT}`;
            const proto = req.headers['x-forwarded-proto'] || 'http';
            const base = `${proto}://${host}`;
            res.write(`event: endpoint\n`);
            res.write(`data: ${JSON.stringify({ method: 'POST', uri: `${base}/mcp` })}\n\n`);
            const keep = setInterval(() => res.write(': keep-alive\n\n'), 30000);
            req.on('close', () => clearInterval(keep));
            return;
        }

        // SINGLE ENDPOINT: /mcp handles both SSE (GET) and JSON-RPC (POST)
        if (path === '/mcp') {
            if (method === 'GET' && req.headers.accept?.includes('text/event-stream')) {
                setCORSHeaders(res);
                res.writeHead(200, {
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                });
                const host = req.headers.host || `localhost:${PORT}`;
                const proto = req.headers['x-forwarded-proto'] || 'http';
                const base = `${proto}://${host}`;
                res.write(`event: endpoint\n`);
                res.write(`data: ${JSON.stringify({ method: 'POST', uri: `${base}/mcp` })}\n\n`);
                const keep = setInterval(() => res.write(': keep-alive\n\n'), 30000);
                req.on('close', () => clearInterval(keep));
                return;
            }

            if (method === 'POST') {
                await handleJSONRPC(req, res);
                return;
            }
        }

        // Root endpoint
        if (path === '/' && method === 'GET') {
            setCORSHeaders(res);
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(`
<!DOCTYPE html>
<html>
<head><title>LUKHAS MCP Ops Kit</title></head>
<body>
<h1>🚀 LUKHAS MCP Ops Kit Server</h1>
<p><strong>Status:</strong> ✅ Operational</p>
<p><strong>Port:</strong> ${PORT}</p>
<p><strong>Endpoints:</strong></p>
<ul>
<li><code>GET /sse</code> - SSE endpoint discovery</li>
<li><code>GET/POST /mcp</code> - Dual transport (SSE + JSON-RPC)</li>
<li><code>HEAD /mcp, /sse</code> - Ultra-fast liveness checks</li>
</ul>
<p><strong>Tools:</strong> search, fetch, apply_patch, list_dir, find_files, git_commit</p>
<p><strong>Cache:</strong> LRU+TTL (${FETCH_CACHE_MAX} items, ${FETCH_TTL_MS}ms TTL)</p>
</body>
</html>
			`);
            return;
        }

        // Health check
        if (path === '/health' && method === 'GET') {
            setCORSHeaders(res);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'healthy',
                tools: MCP_TOOLS.length,
                cache: { size: _cache.size, max: FETCH_CACHE_MAX, ttl: FETCH_TTL_MS },
                repo: REPO_ROOT
            }));
            return;
        }

        // 404 for all other paths
        setCORSHeaders(res);
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Not found' }));

    } catch (error) {
        console.error('Server error:', error);
        setCORSHeaders(res);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Internal server error' }));
    }
});

server.listen(PORT, () => {
    console.log(`🚀 LUKHAS MCP Ops Kit Server running on port ${PORT}`);
    console.log(`📁 Repository root: ${REPO_ROOT}`);
    console.log(`🔗 Endpoints: http://localhost:${PORT}/mcp (dual), http://localhost:${PORT}/sse (split)`);
    console.log(`💾 Cache: ${FETCH_CACHE_MAX} items, ${FETCH_TTL_MS}ms TTL`);
    console.log(`🛠️  Tools: ${MCP_TOOLS.length} available`);
});
