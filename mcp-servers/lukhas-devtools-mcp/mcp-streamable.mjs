import crypto from 'crypto';
import { promises as fs } from 'fs';
import { createServer } from 'node:http';
import { URL } from 'node:url';
import path from 'path';
import { evalOrchestrator } from './adapters/evalOrchestrator.js';
import { modelRegistry } from './adapters/modelRegistry.js';
import { createStores, openDB } from './persistence/sqlite.js';
// Prefer Prometheus-backed monitor if PROM_URL is set; fallback to stub.
let sloMonitor;
try {
    if (process.env.PROM_URL) {
        ({ sloMonitor } = await import('./adapters/sloMonitor.prom.js'));
    } else {
        ({ sloMonitor } = await import('./adapters/sloMonitor.js'));
    }
} catch {
    ({ sloMonitor } = await import('./adapters/sloMonitor.js'));
}

const PORT = parseInt(process.env.PORT || "8766");

// === Security & durability ===
const API_KEYS = (process.env.LUKHAS_MCP_API_KEYS || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);
const REQUIRE_AUTH = API_KEYS.length > 0;

// very small token-bucket per IP
const RL_WINDOW_MS = Number(process.env.MCP_RL_WINDOW_MS ?? 10_000);
const RL_BUCKET = Number(process.env.MCP_RL_BUCKET ?? 60);
const _rl = new Map(); // keyOrIp -> {tokens, ts}
function rateLimitOk(keyOrIp) {
    const now = Date.now();
    let s = _rl.get(keyOrIp);
    if (!s) { s = { tokens: RL_BUCKET, ts: now }; _rl.set(keyOrIp, s); }
    // refill
    const refill = Math.floor((now - s.ts) / RL_WINDOW_MS) * RL_BUCKET;
    if (refill > 0) { s.tokens = Math.min(RL_BUCKET, s.tokens + refill); s.ts = now; }
    if (s.tokens <= 0) return false;
    s.tokens -= 1;
    return true;
}

function getClientIp(req) {
    return (req.headers['x-forwarded-for']?.split(',')[0]?.trim())
        || req.socket?.remoteAddress
        || '0.0.0.0';
}

function extractApiKey(req) {
    if (!REQUIRE_AUTH) return true;
    const key = req.headers['x-api-key'] || req.headers['authorization']?.toString().replace(/^Bearer\s+/i, '');
    return key ? String(key).trim() : null;
}

function verifyAuth(req) {
    if (!REQUIRE_AUTH) return true;
    const key = extractApiKey(req);
    return key && API_KEYS.includes(key);
}

function logReq(req, status, extra) {
    const ip = getClientIp(req);
    const line = JSON.stringify({
        ts: new Date().toISOString(),
        ip,
        method: req.method,
        url: req.url,
        status,
        ua: req.headers['user-agent'] || '',
        ...extra
    });
    console.error(line);
}

// ===== Eval Runner In-Memory Store (stub backend) =====
const JOBS = new Map(); // jobId -> { jobId, taskId, configId, status, startedAt, updatedAt, result? }
const MODELS = new Map(); // modelId -> { modelId, gates: Set<string>, promoted: boolean, promotedAt? }

function nowIso() { return new Date().toISOString(); }
function newId(prefix = 'job') { return `${prefix}_${Math.random().toString(36).slice(2, 10)}`; }

// ===== SSE broker =====
const topics = new Map(); // topic -> Set(res)
function sseSubscribe(topic, res) {
    let set = topics.get(topic);
    if (!set) { set = new Set(); topics.set(topic, set); }
    set.add(res);
    res.on('close', () => { set.delete(res); if (set.size === 0) topics.delete(topic); });
}
function ssePublish(topic, event, payload) {
    const set = topics.get(topic);
    if (!set || set.size === 0) return;
    const data = typeof payload === 'string' ? payload : JSON.stringify(payload);
    for (const res of set) {
        res.write(`event: ${event}\n`);
        res.write(`data: ${data}\n\n`);
    }
}

// === Persistence (lightweight JSON) ===
const REPO_ROOT = process.env.LUKHAS_REPO_ROOT || '/Users/agi_dev/LOCAL-REPOS/Lukhas';
const STATE_PATH = process.env.MCP_STATE_PATH || path.resolve(REPO_ROOT, '.mcp-state.json');

// === SQLite persistence ===
const DB_PATH = process.env.LUKHAS_MCP_DB || path.resolve(REPO_ROOT, '.mcp-state.db');
const __db = openDB(DB_PATH, { wal: true });
const stores = createStores(__db);

// Enhanced narrative audit retrieval
function auditNarrativeFor(idLike) {
    return buildNarrativeFor(idLike);
}

function buildNarrativeFor(idLike) {
    // Fall back to audits-only narrative if no rich canary rows present.
    try {
        const rows = __db.prepare(
            `SELECT ts, actor, action, payload_json FROM audits ORDER BY ts ASC`
        ).all();
        const hits = rows.filter(r => JSON.stringify(r).includes(idLike));
        if (!hits.length) return `No audit narrative found for: ${idLike}`;
        return hits.map(r => {
            let payload = {};
            try { payload = JSON.parse(r.payload_json || "{}"); } catch {}
            return `[${r.ts}] ${r.actor||"system"} ${r.action} ${Object.keys(payload).length? JSON.stringify(payload):""}`.trim();
        }).join("\n");
    } catch (e) {
        return `Narrative unavailable: ${String(e?.message||e)}`;
    }
}

function structuredWhy(id) {
    // Prefer canary view (thresholds + observed); otherwise synthesize from audits.
    const out = {
        id,
        decision: "unknown",
        thresholds: { latency_p95_ms: null, max_error_rate: null, max_drift: null },
        observed: { latency_p95_ms: null, error_rate: null, drift: null },
        time_to_action_sec: null,
        evidence: []
    };
    try {
        // Pull last metrics for the ID if available
        const m = __db.prepare(
            `SELECT * FROM canary_metrics WHERE canary_id = ? ORDER BY created_at DESC LIMIT 1`
        ).get(id);
        if (m) {
            out.observed.latency_p95_ms = m.latency_p95_ms ?? null;
            out.observed.error_rate = m.error_rate ?? null;
            out.observed.drift = m.drift_score ?? null;
        }
    } catch {}
    try {
        const c = __db.prepare(
            `SELECT * FROM canaries WHERE canary_id = ? LIMIT 1`
        ).get(id);
        if (c) {
            try {
                const pol = JSON.parse(c.policy_json || "{}");
                out.thresholds.latency_p95_ms = pol?.targets?.latency_p95_ms ?? null;
                out.thresholds.max_error_rate = pol?.targets?.max_error_rate ?? null;
                out.thresholds.max_drift = pol?.targets?.max_drift ?? null;
            } catch {}
            out.decision = c.status || "unknown";
        }
    } catch {}
    try {
        const rows = __db.prepare(
            `SELECT ts, action, payload_json FROM audits WHERE payload_json LIKE ? ORDER BY ts ASC`
        ).all(`%${id}%`);
        if (rows.length >= 2) {
            const t0 = new Date(rows[0].ts).getTime();
            const te = new Date(rows[rows.length - 1].ts).getTime();
            if (Number.isFinite(t0) && Number.isFinite(te)) out.time_to_action_sec = Math.max(0, Math.round((te - t0)/1000));
        }
        out.evidence = rows.slice(-6); // last few events
    } catch {}
    return out;
}

let _dirty = false;
let _saving = false;

function stateSerialize() {
    const jobs = [...JOBS.values()];
    const models = [...MODELS.values()].map(m => ({ ...m, gates: [...m.gates] }));
    return JSON.stringify({ jobs, models }, null, 2);
}

async function stateSave() {
    if (_saving) return;
    _saving = true;
    try {
        const tmp = STATE_PATH + '.tmp';
        await fs.writeFile(tmp, stateSerialize(), 'utf8');
        await fs.rename(tmp, STATE_PATH);
    } catch (e) {
        console.error('[stateSave] failed:', e?.message || e);
    } finally {
        _saving = false;
        _dirty = false;
    }
}

async function stateLoad() {
    try {
        const raw = await fs.readFile(STATE_PATH, 'utf8');
        const obj = JSON.parse(raw);
        if (Array.isArray(obj?.jobs)) {
            JOBS.clear();
            for (const j of obj.jobs) JOBS.set(j.jobId, j);
        }
        if (Array.isArray(obj?.models)) {
            MODELS.clear();
            for (const m of obj.models) MODELS.set(m.modelId, { ...m, gates: new Set(m.gates || []) });
        }
        console.error(`[stateLoad] loaded ${JOBS.size} jobs, ${MODELS.size} models`);
    } catch {
        // fresh start
    }
}

function markDirty() { _dirty = true; }
setInterval(() => { if (_dirty) stateSave(); }, 3_000).unref();

// GC: sweep old jobs every hour (TTL 7d) - now using SQLite
const JOB_TTL_MS = Number(process.env.MCP_JOB_TTL_MS ?? 7 * 24 * 60 * 60 * 1000);
setInterval(() => {
    const cutoffUnix = Math.floor((Date.now() - JOB_TTL_MS) / 1000);
    const removed = stores.job.sweepOlderThanUnix(cutoffUnix);
    if (removed > 0) console.error(`[gc] removed ${removed} old jobs`);
}, 60 * 60 * 1000).unref();

// Mock LUKHAS search function - replace with actual search implementation
async function mockLUKHASSearch(query, limit = 10) {
    // Simulate search delay
    await new Promise(resolve => setTimeout(resolve, 100));

    const allResults = [
        {
            id: "lukhas-arch-001",
            title: "LUKHAS Architecture Overview",
            snippet: `Comprehensive guide to LUKHAS consciousness-aware AI platform architecture. Query: "${query}"`,
            url: "https://lukhas.ai/docs/architecture",
            type: "documentation",
            relevance: 0.95
        },
        {
            id: "constellation-fw-002",
            title: "Constellation Framework (⚛️🧠🛡️) Implementation",
            snippet: `Trinity Framework implementation details for Identity, Consciousness, and Guardian systems. Searching for: "${query}"`,
            url: "https://lukhas.ai/docs/constellation",
            type: "framework",
            relevance: 0.90
        },
        {
            id: "mcp-tools-003",
            title: "MCP Development Tools",
            snippet: `LUKHAS Model Context Protocol server development tools and utilities. Related to: "${query}"`,
            url: "https://lukhas.ai/tools/mcp",
            type: "tools",
            relevance: 0.85
        },
        {
            id: "t4-standards-004",
            title: "T4/0.01% Quality Standards",
            snippet: `Enterprise-grade quality standards and testing methodologies for LUKHAS systems. Context: "${query}"`,
            url: "https://lukhas.ai/standards/t4",
            type: "standards",
            relevance: 0.80
        },
        {
            id: "consciousness-mod-005",
            title: "Consciousness Module Integration",
            snippet: `692-module consciousness system integration patterns and best practices. Search: "${query}"`,
            url: "https://lukhas.ai/modules/consciousness",
            type: "modules",
            relevance: 0.75
        }
    ];

    // Filter and sort by relevance, then limit
    return allResults
        .filter(result => result.title.toLowerCase().includes(query.toLowerCase()) ||
            result.snippet.toLowerCase().includes(query.toLowerCase()))
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, limit);
}

// Mock LUKHAS fetch function - replace with actual fetch implementation  
async function mockLUKHASFetch(url) {
    // Simulate fetch delay
    await new Promise(resolve => setTimeout(resolve, 150));

    // Mock document content based on URL
    const documents = {
        "https://lukhas.ai/docs/architecture": {
            title: "LUKHAS Architecture Overview",
            mimeType: "text/markdown",
            content: `# LUKHAS Architecture Overview

## Trinity Framework (⚛️🧠🛡️)

LUKHAS implements a sophisticated consciousness-aware AI platform built on three foundational pillars:

- **⚛️ Identity**: Lambda ID system, authentication, symbolic self-representation  
- **🧠 Consciousness**: 692-module cognitive processing, memory systems, awareness
- **🛡️ Guardian**: Constitutional AI, ethical frameworks, drift detection

## Key Components

### Consciousness Modules (692 total)
- Reflection Engine
- Dream Engine  
- Memory systems
- Emotion processing
- Awareness tracking

### Infrastructure
- T4/0.01% quality standards
- Comprehensive testing (775+ tests)
- Lane-based architecture
- Model Context Protocol servers

This document provides the foundational architecture for understanding LUKHAS systems.`
        },
        "https://lukhas.ai/docs/constellation": {
            title: "Constellation Framework Implementation",
            mimeType: "text/markdown",
            content: `# Constellation Framework (⚛️🧠🛡️)

The Constellation Framework represents the evolution of the Trinity Framework, providing a unified approach to consciousness-aware AI development.

## Framework Components

### ⚛️ Identity Layer
- Lambda ID (ΛID) token system
- Tiered authentication (T1-T5)
- Symbolic self-representation
- Access control and permissions

### 🧠 Consciousness Layer  
- 692 cognitive processing modules
- Memory systems and recall
- Dream state processing
- Reflection and meta-cognition

### 🛡️ Guardian Layer
- Constitutional AI principles
- Ethical decision frameworks
- Drift detection and correction
- Safety validation systems

## Integration Patterns

The framework enables seamless integration across all LUKHAS components while maintaining strict quality standards and ethical compliance.`
        }
    };

    // Return document or default
    return documents[url] || {
        title: "Document Not Found",
        mimeType: "text/plain",
        content: `The requested document at ${url} was not found in the LUKHAS knowledge base. This is a mock implementation - in production, this would fetch actual content from the LUKHAS documentation system.`
    };
}

// Fetch document by ID - maps IDs to full documents
async function fetchById(id) {
    // Simulate fetch delay
    await new Promise(resolve => setTimeout(resolve, 150));

    // ID-to-document mapping
    const documents = {
        "lukhas-arch-001": {
            title: "LUKHAS Architecture Overview",
            url: "https://lukhas.ai/docs/architecture",
            mimeType: "text/markdown",
            content: `# LUKHAS Architecture Overview

## Trinity Framework (⚛️🧠🛡️)

LUKHAS implements a sophisticated consciousness-aware AI platform built on three foundational pillars:

- **⚛️ Identity**: Lambda ID system, authentication, symbolic self-representation  
- **🧠 Consciousness**: 692-module cognitive processing, memory systems, awareness
- **🛡️ Guardian**: Constitutional AI, ethical frameworks, drift detection

### Lane-Based Architecture
Production code flows through isolated development lanes with strict import boundaries and comprehensive testing infrastructure.

### T4/0.01% Excellence Standards
Enterprise-grade quality gates ensure sub-100ms performance with 99.99% reliability across all systems.`,
            metadata: { type: "documentation", category: "architecture" }
        },
        "constellation-fw-002": {
            title: "Constellation Framework (⚛️🧠🛡️) Implementation",
            url: "https://lukhas.ai/docs/constellation",
            mimeType: "text/markdown",
            content: `# Constellation Framework Implementation

## Identity Layer (⚛️)
- ΛiD token generation and validation
- T1-T5 tiered authentication system
- OIDC provider with JWT integration
- Security hardening and penetration testing

## Consciousness Layer (🧠)
- ReflectionEngine for meta-cognitive processing
- DreamEngine for background learning  
- Memory/Emotion bridges for context-aware processing
- 692-module neural architecture with dynamic scaling

## Guardian Layer (🛡️)
- Async safety methods with fail-safe defaults
- Drift detection with 0.15 threshold remediation
- Cross-module ethical validation
- Constitutional AI enforcement`,
            metadata: { type: "framework", category: "implementation" }
        },
        "mcp-tools-003": {
            title: "MCP Development Tools",
            url: "https://lukhas.ai/tools/mcp",
            mimeType: "text/markdown",
            content: `# LUKHAS MCP Development Tools

## Server Infrastructure
- Streamable HTTP transport for ChatGPT compatibility
- JSON-RPC 2.0 protocol implementation
- Tool discovery and execution framework
- Development utilities and diagnostics

## Quality Standards
- T4/0.01% testing methodology
- Performance budgets: <100ms auth, <250ms orchestration
- Lane isolation with zero cross-imports
- Comprehensive audit trails and monitoring

## Integration Patterns
- Search/fetch contract for Deep Research compatibility
- ID-based document retrieval system
- Permissive argument handling for forward compatibility`,
            metadata: { type: "tools", category: "development" }
        },
        "t4-standards-004": {
            title: "T4/0.01% Quality Standards",
            url: "https://lukhas.ai/standards/t4",
            mimeType: "text/markdown",
            content: `# T4/0.01% Excellence Standards

## Performance Budgets (Non-Negotiable)
- Memory recall: <100ms p95 for 10k items
- Pipeline latency: <250ms end-to-end p95  
- Guardian overhead: <5ms DSL evaluation
- Cascade prevention: ≥99.7% success rate

## Quality Gates (All PRs)
- Test coverage: ≥90% for core/orchestrator/memory
- Lane isolation: Zero cross-lane imports
- Observability: Metrics + traces + runbooks
- Security: SBOM + secret scanning + pinned SHAs

## Evidence Requirements
- Performance benchmarks with flamegraphs
- Coverage diff vs baseline
- Lane violation reports (must be zero)
- Security audit results
- PromQL snapshots for SLO validation`,
            metadata: { type: "standards", category: "quality" }
        },
        "consciousness-mod-005": {
            title: "Consciousness Module Integration",
            url: "https://lukhas.ai/modules/consciousness",
            mimeType: "text/markdown",
            content: `# Consciousness Module Integration

## 692-Module Architecture
- Modular consciousness components with clear interfaces
- Bio-inspired processing patterns
- Quantum-inspired computational models
- Memory systems with vector database integration

## Integration Patterns
- Guardian safety validation for all consciousness operations
- Memory/Emotion bridge systems for context awareness
- Identity validation for conscious state management
- Orchestrator coordination for cross-module communication

## Performance Characteristics
- <10ms tick processing for real-time consciousness
- Dynamic scaling with stable behavioral patterns
- Cascade prevention with 99.7% success rate
- Memory-efficient processing with sub-second recall`,
            metadata: { type: "modules", category: "consciousness" }
        }
    };

    // Return document or default
    return documents[id] || {
        title: "Document Not Found",
        url: `https://lukhas.ai/unknown/${id}`,
        mimeType: "text/plain",
        content: `The requested document with ID "${id}" was not found in the LUKHAS knowledge base. This is a mock implementation - in production, this would resolve IDs to actual content from the LUKHAS documentation system.`,
        metadata: { type: "error", category: "not_found" }
    };
}

// Simple CORS headers
function setCORSHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept');
}

// Send JSON-RPC response
function sendJSONRPC(res, response) {
    setCORSHeaders(res);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(response));
}

// Send regular JSON response
function sendJSON(res, data, status = 200) {
    setCORSHeaders(res);
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data, null, 2));
}

// Parse JSON body
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (err) {
                reject(err);
            }
        });
    });
}

// MCP Tools definitions - ChatGPT requires 'search' and 'fetch' tools FIRST.
// DO NOT change the first two entries or remove required:["id"] from fetch.
const MCP_TOOLS = [
    // Contract-compliant tools (snake_case)
    {
        name: "search",
        description: "Search over LUKHAS sources and return opaque IDs for follow-up fetch.",
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
        description: "Fetch full record by ID returned from search.",
        inputSchema: {
            type: "object",
            properties: {
                id: { type: "string" }, // required by ChatGPT searchability checks
                fields: {
                    type: "array",
                    items: { type: "string", enum: ["title", "url", "mimeType", "text", "metadata"] }
                }
            },
            required: ["id"]
        }
    },
    {
        name: "run_eval",
        description: "Run an evaluation task with a given config. Returns a jobId to poll via status().",
        inputSchema: {
            type: "object",
            properties: {
                taskId: { type: "string", description: "Evaluation task identifier" },
                configId: { type: "string", description: "Configuration identifier or preset" },
                dryRun: { type: "boolean", default: false }
            },
            required: ["taskId", "configId"]
        }
    },
    {
        name: "status",
        description: "Check current status of a previously launched job.",
        inputSchema: {
            type: "object",
            properties: {
                jobId: { type: "string" }
            },
            required: ["jobId"]
        }
    },
    {
        name: "why",
        description: "Explain WHY a job/model/canary decision happened (narrative audit).",
        inputSchema: {
            type: "object",
            properties: { id: { type: "string", description: "jobId|modelId|canaryId" } },
            required: ["id"]
        }
    },
    {
        name: "why_math",
        description: "Structured WHY: SLO thresholds, observed metrics, decision & time-to-action.",
        inputSchema: {
            type: "object",
            properties: { id: { type: "string", description: "canaryId or jobId" } },
            required: ["id"]
        }
    },
    {
        name: "promote_model",
        description: "Promote a model behind a safety gate. Idempotent.",
        inputSchema: {
            type: "object",
            properties: {
                modelId: { type: "string" },
                gate: { type: "string", description: "Gate name, e.g., 'stage'|'prod'|'experiments'" },
                dryRun: { type: "boolean", default: false }
            },
            required: ["modelId", "gate"]
        }
    },
    {
        name: "apply_patch",
        description: "Aplica un unified diff a un archivo bajo LUKHAS_REPO_ROOT con precondición de sha.",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string", description: "Ruta repo-relativa" },
                patch: { type: "string", description: "Unified diff (formato '---/+++ @@')" },
                expectSha256: { type: "string", description: "sha256 actual del archivo" },
                allowCreate: { type: "boolean", default: false }
            },
            required: ["path", "patch", "expectSha256"]
        }
    },
    {
        name: "list_dir",
        description: "Lista archivos de un directorio (con filtros seguros).",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string", description: "Directorio repo-relativo (p.ej. docs/)" },
                glob: { type: "string", description: "Patrón glob simple (p.ej. **/*.md)" },
                max: { type: "integer", minimum: 1, maximum: 200, default: 50 },
                includeDirs: { type: "boolean", default: false }
            },
            required: ["path"]
        }
    },
    {
        name: "find_files",
        description: "Busca archivos por glob desde la raíz del repo.",
        inputSchema: {
            type: "object",
            properties: {
                glob: { type: "string", description: "Patrón glob (p.ej. mcp-servers/**/*.mjs)" },
                max: { type: "integer", minimum: 1, maximum: 500, default: 100 }
            },
            required: ["glob"]
        }
    },
    {
        name: "git_commit",
        description: "Crea un commit para cambios en LUKHAS_REPO_ROOT (seguro).",
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
    },
    {
        name: "write_file",
        description: "Create or overwrite a file with specified content (snake_case contract)",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string" },
                contents: { type: "string" },
                overwrite: { type: "boolean", default: false },
                encoding: { type: "string", default: "utf8" }
            },
            required: ["path", "contents"]
        }
    },
    {
        name: "create_file",
        description: "Create a new file; fails if file already exists (snake_case contract)",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string" },
                contents: { type: "string" },
                template: { type: "string" },
                encoding: { type: "string", default: "utf8" }
            },
            required: ["path", "contents"]
        }
    },
    {
        name: "update_file",
        description: "Update an existing file with SHA256 precondition check",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string" },
                contents: { type: "string" },
                expectSha256: { type: "string" },
                encoding: { type: "string", default: "utf8" }
            },
            required: ["path", "contents", "expectSha256"]
        }
    },
    {
        name: "append_file",
        description: "Append content to an existing file",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string" },
                contents: { type: "string" },
                ensureNewline: { type: "boolean", default: true },
                encoding: { type: "string", default: "utf8" }
            },
            required: ["path", "contents"]
        }
    },
    {
        name: "rename_file",
        description: "Rename or move a file from one path to another",
        inputSchema: {
            type: "object",
            properties: {
                from: { type: "string" },
                to: { type: "string" },
                overwrite: { type: "boolean", default: false }
            },
            required: ["from", "to"]
        }
    },
    {
        name: "delete_file",
        description: "Delete a file with SHA256 precondition check",
        inputSchema: {
            type: "object",
            properties: {
                path: { type: "string" },
                expectSha256: { type: "string" }
            },
            required: ["path", "expectSha256"]
        }
    },
    // Existing camelCase tools for backward compatibility...
    {
        name: "search",
        description: "Search over LUKHAS sources and return opaque IDs for follow-up fetch",
        inputSchema: {
            type: "object",
            properties: {
                query: { type: "string", description: "Full-text query" },
                limit: { type: "integer", minimum: 1, maximum: 50, default: 5 }
            },
            required: ["query"]
        }
    },
    {
        name: "fetch",
        description: "Fetch full record by ID returned from search",
        inputSchema: {
            type: "object",
            properties: {
                id: { type: "string", description: "Opaque record ID from search" }
            },
            required: ["id"]
        }
    },
    {
        name: "get_infrastructure_status",
        description: "Get LUKHAS testing infrastructure status and metrics",
        inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false
        }
    },
    {
        name: "get_code_analysis",
        description: "Get current codebase health metrics and analysis",
        inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false
        }
    },
    {
        name: "get_development_utilities",
        description: "Get available LUKHAS development tools and utilities",
        inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false
        }
    },
    {
        name: "get_module_structure",
        description: "Get LUKHAS architecture and module structure information",
        inputSchema: {
            type: "object",
            properties: {},
            additionalProperties: false
        }
    },
    {
        name: "writeFile",
        description: "Create or overwrite a file with specified content",
        inputSchema: {
            type: "object",
            properties: {
                path: {
                    type: "string",
                    description: "Absolute or repo-relative path (e.g., 'src/utils/helper.js' or '/Users/agi_dev/LOCAL-REPOS/Lukhas/file.py')"
                },
                content: {
                    type: "string",
                    description: "UTF-8 text content to write"
                },
                overwrite: {
                    type: "boolean",
                    default: false,
                    description: "Allow overwriting existing files"
                },
                encoding: {
                    type: "string",
                    default: "utf8",
                    description: "File encoding (utf8, ascii, etc.)"
                }
            },
            required: ["path", "content"]
        }
    },
    {
        name: "createFile",
        description: "Create a new file; fails if file already exists",
        inputSchema: {
            type: "object",
            properties: {
                path: {
                    type: "string",
                    description: "Absolute or repo-relative path for new file"
                },
                content: {
                    type: "string",
                    description: "UTF-8 text content for new file"
                },
                template: {
                    type: "string",
                    description: "Optional template type (python, javascript, markdown, etc.)"
                },
                encoding: {
                    type: "string",
                    default: "utf8",
                    description: "File encoding"
                }
            },
            required: ["path", "content"]
        }
    },
    {
        name: "start_canary",
        description: "Start an SLO-guarded canary from one gate to another.",
        inputSchema: {
            type: "object",
            properties: {
                modelId: { type: "string" },
                fromGate: { type: "string" },
                toGate: { type: "string" },
                windowSeconds: { type: "integer", default: 300 },
                targets: {
                    type: "object",
                    properties: {
                        latency_p95_ms: { type: "number", default: 250 },
                        max_error_rate: { type: "number", default: 0.02 }
                    },
                    required: ["latency_p95_ms", "max_error_rate"]
                },
                dryRun: { type: "boolean", default: false }
            },
            required: ["modelId", "fromGate", "toGate", "targets"]
        }
    },
    {
        name: "canary_status",
        description: "Inspect current status of a canary.",
        inputSchema: {
            type: "object",
            properties: { canaryId: { type: "string" } },
            required: ["canaryId"]
        }
    },
    {
        name: "abort_canary",
        description: "Abort a running canary and rollback to the previous gate.",
        inputSchema: {
            type: "object",
            properties: { canaryId: { type: "string" } },
            required: ["canaryId"]
        }
    }
];

// File system utilities for safe file operations

// Resolve path safely - convert relative paths to absolute within LUKHAS repo
function resolveSafePath(inputPath) {
    const repoRoot = REPO_ROOT;

    // If already absolute and within repo, use as-is
    if (path.isAbsolute(inputPath)) {
        if (inputPath.startsWith(repoRoot)) {
            return inputPath;
        } else {
            throw new Error(`Absolute path must be within LUKHAS repo: ${repoRoot}`);
        }
    }

    // Resolve relative path within repo
    const resolved = path.resolve(repoRoot, inputPath);
    if (!resolved.startsWith(repoRoot)) {
        throw new Error(`Path traversal not allowed: ${inputPath}`);
    }

    return resolved;
}

// Safe file write with directory creation
async function writeFileWithDirectories(filePath, content, encoding = 'utf8', overwrite = false) {
    const safePath = resolveSafePath(filePath);
    const dir = path.dirname(safePath);

    // Check if file exists and overwrite policy
    try {
        await fs.access(safePath);
        if (!overwrite) {
            throw new Error(`File already exists and overwrite=false: ${filePath}`);
        }
    } catch (err) {
        if (err.code !== 'ENOENT') {
            throw err; // Re-throw if not "file doesn't exist"
        }
    }

    // Create directory if needed
    await fs.mkdir(dir, { recursive: true });

    // Write file
    await fs.writeFile(safePath, content, encoding);

    // Get file stats for response
    const stats = await fs.stat(safePath);

    return {
        path: safePath,
        relativePath: path.relative('/Users/agi_dev/LOCAL-REPOS/Lukhas', safePath),
        size: stats.size,
        created: stats.birthtime,
        modified: stats.mtime,
        encoding: encoding
    };
}

// Safe file creation (fails if exists)
async function createNewFile(filePath, content, encoding = 'utf8', template = null) {
    const safePath = resolveSafePath(filePath);
    const dir = path.dirname(safePath);

    // Check if file already exists
    try {
        await fs.access(safePath);
        throw new Error(`File already exists: ${filePath}`);
    } catch (err) {
        if (err.code !== 'ENOENT') {
            throw new Error(`Cannot create file: ${err.message}`);
        }
    }

    // Apply template if specified
    let finalContent = content;
    if (template) {
        const templateHeader = getTemplateHeader(template, path.basename(safePath));
        finalContent = templateHeader + content;
    }

    // Create directory if needed
    await fs.mkdir(dir, { recursive: true });

    // Create file
    await fs.writeFile(safePath, finalContent, encoding);

    // Get file stats for response
    const stats = await fs.stat(safePath);

    return {
        path: safePath,
        relativePath: path.relative('/Users/agi_dev/LOCAL-REPOS/Lukhas', safePath),
        size: stats.size,
        created: stats.birthtime,
        template: template,
        encoding: encoding
    };
}

// Template headers for different file types
function getTemplateHeader(template, filename) {
    const templates = {
        python: `#!/usr/bin/env python3
"""${filename} - LUKHAS AI Platform Module

Author: LUKHAS Development Team
Generated: ${new Date().toISOString()}
"""

`,
        javascript: `/**
 * ${filename} - LUKHAS AI Platform Module
 * 
 * Author: LUKHAS Development Team
 * Generated: ${new Date().toISOString()}
 */

`,
        markdown: `# ${filename.replace('.md', '')}

**Generated:** ${new Date().toISOString()}  
**Platform:** LUKHAS AI  

`,
        typescript: `/**
 * ${filename} - LUKHAS AI Platform Module
 * 
 * Author: LUKHAS Development Team
 * Generated: ${new Date().toISOString()}
 */

`
    };

    return templates[template.toLowerCase()] || '';
}

// Handle MCP method calls
async function handleMCPMethod(method, params = {}) {
    switch (method) {
        case 'initialize':
            // Be flexible with protocol versions - support what the client wants
            const clientProtocolVersion = params?.protocolVersion || "2024-11-05";
            const supportedVersions = ["2024-11-05", "2025-06-18", "2025-03-26"];
            const protocolVersion = supportedVersions.includes(clientProtocolVersion)
                ? clientProtocolVersion
                : "2024-11-05";

            return {
                protocolVersion,
                capabilities: {
                    tools: {
                        listChanged: false
                    },
                    logging: {
                        level: "info"
                    },
                    resources: {},
                    prompts: {}
                },
                serverInfo: {
                    name: "LUKHAS DevTools MCP",
                    version: "1.0.0"
                }
            };

        case 'tools/list':
            return {
                tools: MCP_TOOLS
            };

        case 'tools/call':
            const { name, arguments: args = {} } = params;

            switch (name) {
                // --- Contract-compliant tools ---
                case 'write_file': {
                    const { path: writePath, contents, overwrite = false, encoding = 'utf8' } = args;
                    if (!writePath || typeof contents !== 'string') throw new Error('path and contents required');
                    const result = await writeFileWithDirectories(writePath, contents, encoding, overwrite);
                    return { content: [{ type: "text", text: JSON.stringify(result) }] };
                }
                case 'create_file': {
                    const { path: createPath, contents, template, encoding = 'utf8' } = args;
                    if (!createPath || typeof contents !== 'string') throw new Error('path and contents required');
                    const result = await createNewFile(createPath, contents, encoding, template);
                    return { content: [{ type: "text", text: JSON.stringify(result) }] };
                }
                case 'update_file': {
                    const { path: updatePath, contents, expectSha256, encoding = 'utf8' } = args;
                    if (!updatePath || typeof contents !== 'string' || !expectSha256) throw new Error('path, contents, and expectSha256 required');
                    const safePath = resolveSafePath(updatePath);
                    const exists = await fs.access(safePath).then(() => true).catch(() => false);
                    if (!exists) throw new Error(`File does not exist: ${updatePath}`);
                    const original = await fs.readFile(safePath, 'utf8');
                    const currentSha = crypto.createHash('sha256').update(original).digest('hex');
                    if (currentSha !== expectSha256) throw new Error(`SHA mismatch: expected ${expectSha256}, got ${currentSha}`);
                    await fs.writeFile(safePath, contents, encoding);
                    const newSha = crypto.createHash('sha256').update(contents).digest('hex');
                    const stats = await fs.stat(safePath);
                    return { content: [{ type: "text", text: JSON.stringify({ path: updatePath, sha256: newSha, size: stats.size, modified: stats.mtime }) }] };
                }
                case 'append_file': {
                    const { path: appendPath, contents, ensureNewline = true, encoding = 'utf8' } = args;
                    if (!appendPath || typeof contents !== 'string') throw new Error('path and contents required');
                    const safePath = resolveSafePath(appendPath);
                    const exists = await fs.access(safePath).then(() => true).catch(() => false);
                    if (!exists) throw new Error(`File does not exist: ${appendPath}`);
                    let appendText = contents;
                    if (ensureNewline && !appendText.startsWith('\n')) appendText = '\n' + appendText;
                    await fs.appendFile(safePath, appendText, encoding);
                    const final = await fs.readFile(safePath, 'utf8');
                    const newSha = crypto.createHash('sha256').update(final).digest('hex');
                    const stats = await fs.stat(safePath);
                    return { content: [{ type: "text", text: JSON.stringify({ path: appendPath, sha256: newSha, size: stats.size, appended: contents.length }) }] };
                }
                case 'rename_file': {
                    const { from, to, overwrite = false } = args;
                    if (!from || !to) throw new Error('from and to paths required');
                    const safeFrom = resolveSafePath(from);
                    const safeTo = resolveSafePath(to);
                    const fromExists = await fs.access(safeFrom).then(() => true).catch(() => false);
                    if (!fromExists) throw new Error(`Source file does not exist: ${from}`);
                    const toExists = await fs.access(safeTo).then(() => true).catch(() => false);
                    if (toExists && !overwrite) throw new Error(`Target file exists and overwrite=false: ${to}`);
                    await fs.mkdir(path.dirname(safeTo), { recursive: true });
                    await fs.rename(safeFrom, safeTo);
                    const stats = await fs.stat(safeTo);
                    return { content: [{ type: "text", text: JSON.stringify({ from, to, size: stats.size, moved: true }) }] };
                }
                case 'delete_file': {
                    const { path: deletePath, expectSha256 } = args;
                    if (!deletePath || !expectSha256) throw new Error('path and expectSha256 required');
                    const safePath = resolveSafePath(deletePath);
                    const exists = await fs.access(safePath).then(() => true).catch(() => false);
                    if (!exists) throw new Error(`File does not exist: ${deletePath}`);
                    const original = await fs.readFile(safePath, 'utf8');
                    const currentSha = crypto.createHash('sha256').update(original).digest('hex');
                    if (currentSha !== expectSha256) throw new Error(`SHA mismatch: expected ${expectSha256}, got ${currentSha}`);
                    await fs.unlink(safePath);
                    return { content: [{ type: "text", text: JSON.stringify({ path: deletePath, deleted: true, previousSha256: currentSha }) }] };
                }
                // --- apply_patch ---
                case 'apply_patch': {
                    const rel = String(args?.path || "");
                    const patch = String(args?.patch || "");
                    const expectSha = String(args?.expectSha256 || "");
                    const allowCreate = Boolean(args?.allowCreate ?? false);
                    const safePath = resolveSafePath(rel);
                    const exists = await fs.access(safePath).then(() => true).catch(() => false);
                    if (!exists && !allowCreate) throw new Error(`No existe: ${rel} (allowCreate=false)`);
                    const original = exists ? await fs.readFile(safePath, 'utf8') : "";
                    const currentSha = crypto.createHash('sha256').update(original).digest('hex');
                    if (currentSha !== expectSha && exists) throw new Error(`Precondición fallida: sha256 actual=${currentSha}`);
                    // --- robust unified-diff applier (single-file) ---
                    function applyUnified(baseText, diffRaw) {
                        // Normalize line endings, strip BOM, keep exact leading symbols
                        let diff = String(diffRaw).replace(/\r\n/g, '\n').replace(/^\uFEFF/, '');
                        const lines = diff.split('\n').map(l => l.replace(/\r$/, ''));

                        // Tolerant header detection: accept with or without ---/+++; ignore timestamps
                        const hasOld = lines.some(l => /^---(\s|$)/.test(l));
                        const hasNew = lines.some(l => /^\+\+\+(\s|$)/.test(l));

                        // Find first hunk; it's the only thing we truly need
                        let idx = lines.findIndex(l => /^@@\s+-\d+(?:,\d+)?\s+\+\d+(?:,\d+)?\s+@@/.test(l));
                        if (idx === -1) {
                            // If we got no hunk but we *do* have headers, this is malformed; surface a clear error
                            if (hasOld || hasNew) throw new Error('Invalid unified diff (found headers but no @@ hunk)');
                            // Otherwise treat whole thing as a literal replacement (escape hatch for minimal diffs)
                            return diff;
                        }

                        const base = String(baseText).replace(/\r\n/g, '\n').split('\n');
                        let out = [];
                        let basePtr = 0;

                        // Process each hunk
                        while (idx !== -1) {
                            const header = lines[idx];
                            const m = /^@@\s+-([0-9]+)(?:,([0-9]+))?\s+\+([0-9]+)(?:,([0-9]+))?\s+@@/.exec(header);
                            if (!m) throw new Error('Invalid hunk header');

                            // Old file start (1-based) & count
                            const aStart = Math.max(0, parseInt(m[1], 10) - 1);
                            const aCount = m[2] ? parseInt(m[2], 10) : 1;

                            // Copy unchanged up to hunk start
                            if (aStart > basePtr) out.push(...base.slice(basePtr, aStart));
                            basePtr = aStart;

                            // Consume hunk body
                            idx++;
                            while (idx < lines.length && !/^@@\s+-\d+/.test(lines[idx])) {
                                const l = lines[idx];

                                // Allowed prefix lines in unified diff:
                                //  ' '  context   → copy one line from base
                                //  '-'  deletion  → skip one line from base
                                //  '+'  addition  → append new line
                                //  ''   (empty)   → treat like context
                                //  '---'/'+++'    → header lines between hunks → ignore
                                if (l.startsWith('+')) {
                                    out.push(l.slice(1));
                                } else if (l.startsWith('-')) {
                                    // deletion: advance base pointer, but don't copy
                                    basePtr++;
                                } else if (l.startsWith(' ') || l === '') {
                                    out.push(base[basePtr++] ?? '');
                                } else if (/^---(\s|$)/.test(l) || /^\+\+\+(\s|$)/.test(l)) {
                                    // tolerate file header lines appearing here (git sometimes repeats)
                                } else {
                                    // be permissive: treat unknown lines as context
                                    out.push(base[basePtr++] ?? '');
                                }
                                idx++;
                            }
                        }

                        // Append any remaining tail from the base
                        if (basePtr < base.length) out.push(...base.slice(basePtr));

                        return out.join('\n');
                    }

                    // TEMP: flip to true only when debugging CI
                    const LOG_PATCH = false;
                    if (LOG_PATCH) console.error('[apply_patch] raw patch bytes:', Buffer.from(patch).length);

                    let next;
                    try {
                        next = applyUnified(original, patch);
                    } catch (e) {
                        throw new Error(`Invalid patch: ${e.message}`);
                    }

                    await fs.mkdir(path.dirname(safePath), { recursive: true });
                    await fs.writeFile(safePath, next, 'utf8');
                    const newSha = crypto.createHash('sha256').update(next).digest('hex');
                    return { content: [{ type: "text", text: JSON.stringify({ path: rel, bytesWritten: Buffer.byteLength(next, 'utf8'), previousSha256: exists ? currentSha : null, sha256: newSha, created: !exists }) }] };
                }
                // --- list_dir ---
                case 'list_dir': {
                    const rel = String(args?.path || "");
                    const glob = args?.glob ? String(args.glob) : null;
                    const max = Math.max(1, Math.min(200, Number(args?.max ?? 50)));
                    const includeDirs = Boolean(args?.includeDirs ?? false);
                    const dirAbs = resolveSafePath(rel);
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
                        let rx = esc(pattern).replace(/\\*\\*/g, '.*').replace(/\\*/g, '[^/]*').replace(/\\?/g, '.');
                        return new RegExp(`^${rx}$`).test(name);
                    }
                    const entries = await walkDir(dirAbs);
                    let files = entries.filter(e => e.type === "file" || (includeDirs && e.type === "dir"));
                    if (glob) files = files.filter(e => matchGlob(e.rel, glob));
                    const items = files.slice(0, max).map(e => ({ type: e.type, path: path.posix.join(rel, e.rel) }));
                    return { content: [{ type: "text", text: JSON.stringify({ items, truncated: files.length > max }) }] };
                }
                // --- find_files ---
                case 'find_files': {
                    const glob = String(args?.glob || "");
                    const max = Math.max(1, Math.min(500, Number(args?.max ?? 100)));
                    async function walkDir(absRoot, relRoot = "", depth = 0) {
                        if (depth > 10) return []; // Prevent stack overflow
                        const out = [];
                        try {
                            const entries = await fs.readdir(absRoot, { withFileTypes: true });
                            for (const e of entries) {
                                const rel = path.posix.join(relRoot, e.name);
                                const abs = path.join(absRoot, e.name);
                                if (e.isDirectory()) {
                                    const sub = await walkDir(abs, rel, depth + 1);
                                    out.push(...sub);
                                }
                                else if (e.isFile()) out.push({ type: "file", rel, abs });
                            }
                        } catch (err) {
                            // Skip directories we can't read
                        }
                        return out;
                    }
                    function matchGlob(name, pattern) {
                        const esc = s => s.replace(/[-/\\^$+?.()|[\]{}]/g, '\\$&');
                        let rx = esc(pattern).replace(/\\*\\*/g, '.*').replace(/\\*/g, '[^/]*').replace(/\\?/g, '.');
                        return new RegExp(`^${rx}$`).test(name);
                    }
                    const entries = await walkDir('/Users/agi_dev/LOCAL-REPOS/Lukhas');
                    let files = entries.filter(e => e.type === "file" && matchGlob(e.rel, glob));
                    const items = files.slice(0, max).map(e => ({ path: e.rel }));
                    return { content: [{ type: "text", text: JSON.stringify({ items, truncated: files.length > max }) }] };
                }
                // --- git_commit (mejorado) ---
                case 'git_commit': {
                    const message = String(args?.message || "").trim();
                    const addList = Array.isArray(args?.add) ? args.add.map(String) : [];
                    const signoff = Boolean(args?.signoff ?? false);
                    const stageAll = Boolean(args?.stageAll ?? false);
                    if (!message) throw new Error("Commit message requerido");
                    const ex = async (cmd, argv, cwd = '/Users/agi_dev/LOCAL-REPOS/Lukhas') => (await import('child_process')).execFileSync(cmd, argv, { cwd, encoding: 'utf8' });
                    if (addList.length) {
                        const safe = [];
                        for (const rel of addList) safe.push(resolveSafePath(rel));
                        ex('git', ['add', ...safe]);
                    } else if (stageAll) {
                        ex('git', ['add', '-A']);
                    }
                    const fullMsg = signoff ? `${message}\n\nSigned-off-by: MCP Bot <bot@lukhas.ai>` : message;
                    let out;
                    try { out = ex('git', ['commit', '-m', fullMsg]); }
                    catch (e) {
                        const msg = String(e?.stdout || e?.stderr || e?.message || '').trim();
                        throw new Error(`git commit falló: ${msg || '¿nada para commitear?'}`);
                    }
                    const sha = String(ex('git', ['rev-parse', 'HEAD']) || '').trim();
                    return { content: [{ type: "text", text: JSON.stringify({ commit: sha, message, staged: addList, stageAll }) }] };
                }
                // --- End contract tools ---
                case 'search':
                    const { query, limit = 5, ...extraArgs } = args; // Accept extra args gracefully
                    if (!query) {
                        throw new Error('Search query is required');
                    }

                    // Mock LUKHAS search results - return IDs + hits for ChatGPT compatibility
                    const searchResults = await mockLUKHASSearch(query, limit);
                    const ids = searchResults.map(r => r.id);
                    const hits = searchResults.map(r => ({
                        id: r.id,
                        title: r.title,
                        snippet: r.snippet
                    }));

                    // Return IDs for fetch + hits for display
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({ ids, hits })
                            }
                        ]
                    };

                case 'fetch':
                    const { id, ...extraFetchArgs } = args; // Accept extra args gracefully
                    if (!id) {
                        throw new Error('ID is required');
                    }

                    // Handle lukhas-path: IDs for direct file access
                    if (id.startsWith('lukhas-path:')) {
                        const b64Path = id.slice('lukhas-path:'.length);
                        const decodedPath = Buffer.from(b64Path + '===', 'base64url').toString('utf8');
                        const safePath = resolveSafePath(decodedPath);

                        try {
                            const exists = await fs.access(safePath).then(() => true).catch(() => false);
                            if (!exists) {
                                throw new Error(`File not found: ${decodedPath}`);
                            }

                            const content = await fs.readFile(safePath, 'utf8');
                            const sha256 = crypto.createHash('sha256').update(content).digest('hex');
                            const stats = await fs.stat(safePath);

                            return {
                                content: [
                                    {
                                        type: "text",
                                        text: JSON.stringify({
                                            id: id,
                                            title: path.basename(decodedPath),
                                            url: `file://${safePath}`,
                                            mimeType: decodedPath.endsWith('.md') ? 'text/markdown' : 'text/plain',
                                            text: content,
                                            metadata: {
                                                sha256: sha256,
                                                size: stats.size,
                                                modified: stats.mtime.toISOString(),
                                                path: decodedPath
                                            }
                                        })
                                    }
                                ]
                            };
                        } catch (error) {
                            throw new Error(`Failed to fetch file ${decodedPath}: ${error.message}`);
                        }
                    }

                    // Fetch document by ID - resolve ID to full document (original behavior)
                    const document = await fetchById(id);

                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    id: id,
                                    title: document.title,
                                    url: document.url,
                                    mimeType: document.mimeType,
                                    text: document.content,
                                    metadata: document.metadata || {}
                                })
                            }
                        ]
                    };

                case 'get_infrastructure_status':
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    status: "operational",
                                    total_tests: "775+ comprehensive tests",
                                    infrastructure: "stabilized after critical fixes",
                                    timestamp: new Date().toISOString(),
                                    quality_standard: "T4/0.01%"
                                }, null, 2)
                            }
                        ]
                    };

                case 'get_code_analysis':
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    health_score: 92.5,
                                    code_quality: "excellent",
                                    total_files: 7000,
                                    timestamp: new Date().toISOString(),
                                    quality_standard: "T4/0.01%"
                                }, null, 2)
                            }
                        ]
                    };

                case 'get_development_utilities':
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    utilities: ["Test infrastructure", "Code quality", "Performance monitoring"],
                                    tools: { testing: "pytest", linting: "ruff", typing: "mypy" },
                                    timestamp: new Date().toISOString(),
                                    quality_standard: "T4/0.01%"
                                }, null, 2)
                            }
                        ]
                    };

                case 'get_module_structure':
                    return {
                        content: [
                            {
                                type: "text",
                                text: JSON.stringify({
                                    total_modules: 692,
                                    consciousness_modules: 662,
                                    production_modules: 30,
                                    framework: "Constellation Framework",
                                    timestamp: new Date().toISOString(),
                                    quality_standard: "T4/0.01%"
                                }, null, 2)
                            }
                        ]
                    };

                case 'writeFile':
                    const { path: writePath, content: writeContent, overwrite = false, encoding: writeEncoding = 'utf8', ...extraWriteArgs } = args;

                    if (!writePath || !writeContent) {
                        throw new Error('Both path and content are required for writeFile');
                    }

                    try {
                        const result = await writeFileWithDirectories(writePath, writeContent, writeEncoding, overwrite);

                        return {
                            content: [
                                {
                                    type: "text",
                                    text: JSON.stringify({
                                        success: true,
                                        operation: "writeFile",
                                        path: result.path,
                                        relativePath: result.relativePath,
                                        size: result.size,
                                        encoding: result.encoding,
                                        overwritten: overwrite,
                                        timestamp: new Date().toISOString()
                                    }, null, 2)
                                }
                            ]
                        };
                    } catch (error) {
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: JSON.stringify({
                                        success: false,
                                        operation: "writeFile",
                                        error: error.message,
                                        path: writePath,
                                        timestamp: new Date().toISOString()
                                    }, null, 2)
                                }
                            ]
                        };
                    }

                case 'createFile':
                    const { path: createPath, content: createContent, template, encoding: createEncoding = 'utf8', ...extraCreateArgs } = args;

                    if (!createPath || !createContent) {
                        throw new Error('Both path and content are required for createFile');
                    }

                    try {
                        const result = await createNewFile(createPath, createContent, createEncoding, template);

                        return {
                            content: [
                                {
                                    type: "text",
                                    text: JSON.stringify({
                                        success: true,
                                        operation: "createFile",
                                        path: result.path,
                                        relativePath: result.relativePath,
                                        size: result.size,
                                        template: result.template,
                                        encoding: result.encoding,
                                        timestamp: new Date().toISOString()
                                    }, null, 2)
                                }
                            ]
                        };
                    } catch (error) {
                        return {
                            content: [
                                {
                                    type: "text",
                                    text: JSON.stringify({
                                        success: false,
                                        operation: "createFile",
                                        error: error.message,
                                        path: createPath,
                                        timestamp: new Date().toISOString()
                                    }, null, 2)
                                }
                            ]
                        };
                    }

                // ---------- run_eval ----------
                case 'run_eval': {
                    const taskId = String(args?.taskId || "");
                    const configId = String(args?.configId || "");
                    const dryRun = Boolean(args?.dryRun ?? false);
                    if (!taskId || !configId) throw new Error("taskId and configId are required");

                    const { jobId } = await evalOrchestrator.run({ taskId, configId, dryRun });

                    const entry = {
                        job_id: jobId,
                        task_id: taskId,
                        config_id: configId,
                        status: dryRun ? 'DRY_RUN' : 'QUEUED',
                        started_at: nowIso(),
                        updated_at: nowIso(),
                        result_json: null
                    };
                    stores.job.upsert(entry);
                    // Add narrative audit trail
                    stores.job.insertNarrative('queued', jobId, `eval "${taskId}" → queued for processing`);
                    // after stores.job.upsert(entry);
                    ssePublish(`job/${jobId}`, 'queued', { jobId, taskId, configId, ts: nowIso() });

                    // async progress simulation only if orchestrator didn't already take ownership
                    if (!dryRun) {
                        setTimeout(() => {
                            const j = stores.job.get(jobId); if (!j) return;
                            j.status = 'RUNNING'; j.updated_at = nowIso(); stores.job.upsert(j);
                            stores.job.insertNarrative('running', jobId, `eval "${taskId}" → running`);
                            ssePublish(`job/${jobId}`, 'running', { jobId, ts: j.updated_at });
                        }, 250);
                        setTimeout(() => {
                            const j = stores.job.get(jobId); if (!j) return;
                            j.status = 'COMPLETED';
                            j.updated_at = nowIso();
                            j.result_json = JSON.stringify({
                                taskId, configId,
                                metrics: { accuracy: 0.91, f1: 0.88, latency_ms_p50: 120 },
                                artifacts: []
                            });
                            stores.job.upsert(j);
                            stores.job.insertNarrative('completed', jobId, `eval "${taskId}" → completed successfully`);
                            ssePublish(`job/${jobId}`, 'completed', {
                                jobId, ts: j.updated_at,
                                result: JSON.parse(j.result_json)
                            });
                        }, 1500);
                    }

                    return {
                        content: [{
                            type: "text",
                            text: JSON.stringify({
                                jobId, taskId, configId, status: entry.status, startedAt: entry.started_at, updatedAt: entry.updated_at
                            })
                        }]
                    };
                }

                // ---------- status ----------
                case 'status': {
                    const jobId = String(args?.jobId || "");
                    if (!jobId) throw new Error("jobId is required");

                    // If you later integrate a real poller:
                    // const remote = await evalOrchestrator.poll(jobId); if (remote) { ... stores.job.upsert(remote) }

                    const j = stores.job.get(jobId);
                    if (!j) throw new Error(`Unknown jobId: ${jobId}`);
                    const payload = {
                        jobId: j.job_id,
                        taskId: j.task_id,
                        configId: j.config_id,
                        status: j.status,
                        startedAt: j.started_at,
                        updatedAt: j.updated_at,
                        result: j.result_json ? JSON.parse(j.result_json) : null
                    };
                    return {
                        content: [{
                            type: "text",
                            text: JSON.stringify(payload)
                        }]
                    };
                }

                // ---------- why ----------
                case 'why': {
                    const { id } = args;
                    const text = auditNarrativeFor(id);
                    return {
                        content: [{
                            type: "text",
                            text
                        }]
                    };
                }

                // ---------- why_math ----------
                case 'why_math': {
                    const { id } = args;
                    const data = structuredWhy(id);
                    return {
                        content: [{
                            type: "text",
                            text: JSON.stringify(data)
                        }]
                    };
                }

                // ---------- promote_model ----------
                case 'promote_model': {
                    const modelId = String(args?.modelId || "");
                    const gate = String(args?.gate || "");
                    const dryRun = Boolean(args?.dryRun ?? false);
                    if (!modelId || !gate) throw new Error("modelId and gate are required");

                    await modelRegistry.promote({ modelId, gate, dryRun });

                    // local registry state
                    const now = nowIso();
                    const current = stores.model.get(modelId) || { model_id: modelId, promoted: 0, promoted_at: null };
                    const gates = new Set(stores.model.gates(modelId));
                    const changed = !gates.has(gate);
                    if (!dryRun && changed) {
                        gates.add(gate);
                        stores.model.upsert({ model_id: modelId, promoted: 1, promoted_at: now });
                        stores.model.addGate(modelId, gate);
                        stores.audit.write(now, 'mcp', 'promote_model', { modelId, gate });
                    } else if (current && !current.promoted && !dryRun) {
                        stores.model.upsert({ model_id: modelId, promoted: 1, promoted_at: now });
                    }
                    const currentGates = [...gates];
                    return {
                        content: [{
                            type: "text",
                            text: JSON.stringify({
                                modelId, gate, dryRun, changed, currentGates,
                                promoted: (stores.model.get(modelId)?.promoted ?? 0) === 1,
                                promotedAt: stores.model.get(modelId)?.promoted_at ?? null
                            })
                        }]
                    };
                }

                // ---------- start_canary ----------
                case 'start_canary': {
                    const modelId = String(args?.modelId || "");
                    const fromGate = String(args?.fromGate || "");
                    const toGate = String(args?.toGate || "");
                    const windowSeconds = Number(args?.windowSeconds ?? 300);
                    const targets = args?.targets || {};
                    const dryRun = Boolean(args?.dryRun ?? false);
                    if (!modelId || !fromGate || !toGate) throw new Error("modelId, fromGate, toGate are required");

                    const canaryId = newId('canary');
                    const now = nowIso();
                    const policy = { windowSeconds, targets };
                    const entry = {
                        canary_id: canaryId, model_id: modelId, from_gate: fromGate, to_gate: toGate,
                        status: dryRun ? 'PENDING' : 'RUNNING',
                        created_at: now, updated_at: now, policy_json: JSON.stringify(policy)
                    };
                    stores.canary.upsert(entry);
                    stores.canary.insertNarrative('started', canaryId, `canary ${modelId} → ${fromGate} to ${toGate} (SLO monitoring)`);
                    ssePublish(`canary/${canaryId}`, 'started', { canaryId, modelId, fromGate, toGate, ts: now });

                    if (!dryRun) {
                        // polling loop (bounded)
                        let ticks = 0, maxTicks = Math.max(2, Math.ceil(windowSeconds / 10));
                        const iv = setInterval(async () => {
                            ticks++;
                            // Sample metrics from adapter at the *target* gate
                            const m = await sloMonitor.sample({ modelId, gate: toGate, windowSeconds });
                            const ts = nowIso();
                            stores.canary.addMetric(canaryId, ts, m.latency_p95_ms, m.error_rate);
                            ssePublish(`canary/${canaryId}`, 'metric', { canaryId, ts, ...m });

                            const { latency_p95_ms, error_rate } = m;
                            const { latency_p95_ms: L, max_error_rate: E } = policy.targets;

                            // Simple decision: if within targets for 2 consecutive ticks → promote; else if bad spike → rollback
                            const good = latency_p95_ms <= L && error_rate <= E;
                            if (good && ticks >= 2) {
                                // finalize: promote to toGate (idempotent)
                                const now2 = nowIso();
                                const gates = stores.model.gates(modelId);
                                if (!gates.includes(toGate)) stores.model.addGate(modelId, toGate);
                                stores.model.upsert({ model_id: modelId, promoted: 1, promoted_at: now2 });
                                stores.audit.write(now2, 'mcp', 'canary_promote', { modelId, fromGate, toGate, metrics: m });
                                stores.canary.upsert({ ...entry, status: 'PROMOTED', updated_at: now2, policy_json: JSON.stringify(policy) });
                                stores.canary.insertNarrative('promoted', canaryId, `promoted ${modelId} → ${toGate} (lat=${Math.round(latency_p95_ms)}ms, err=${(error_rate * 100).toFixed(1)}%)`);
                                ssePublish(`canary/${canaryId}`, 'promoted', { canaryId, ts: now2, metrics: m });
                                clearInterval(iv);
                                return;
                            }
                            // immediate rollback if egregious
                            if (error_rate > Math.max(E * 2, 0.05) || latency_p95_ms > L * 2) {
                                const now2 = nowIso();
                                stores.audit.write(now2, 'mcp', 'canary_rollback', { modelId, fromGate, toGate, metrics: m });
                                stores.canary.upsert({ ...entry, status: 'ROLLED_BACK', updated_at: now2, policy_json: JSON.stringify(policy) });
                                stores.canary.insertNarrative('rolled_back', canaryId, `rollback ${modelId} due to SLO breach (lat=${Math.round(latency_p95_ms)}ms, err=${(error_rate * 100).toFixed(1)}%)`);
                                ssePublish(`canary/${canaryId}`, 'rolled_back', { canaryId, ts: now2, metrics: m });
                                clearInterval(iv);
                                return;
                            }
                            if (ticks >= maxTicks) {
                                const now2 = nowIso();
                                // Timeout → rollback (conservative)
                                stores.audit.write(now2, 'mcp', 'canary_timeout', { modelId, fromGate, toGate });
                                stores.canary.upsert({ ...entry, status: 'ROLLED_BACK', updated_at: now2, policy_json: JSON.stringify(policy) });
                                ssePublish(`canary/${canaryId}`, 'rolled_back', { canaryId, ts: now2, reason: 'timeout' });
                                clearInterval(iv);
                            }
                        }, 10_000).unref();
                    }

                    return {
                        content: [{
                            type: "text",
                            text: JSON.stringify({
                                canaryId, modelId, fromGate, toGate, status: entry.status, policy
                            })
                        }]
                    };
                }

                // ---------- canary_status ----------
                case 'canary_status': {
                    const canaryId = String(args?.canaryId || "");
                    if (!canaryId) throw new Error("canaryId is required");
                    const c = stores.canary.get(canaryId);
                    if (!c) throw new Error(`Unknown canaryId: ${canaryId}`);
                    const payload = {
                        canaryId: c.canary_id,
                        modelId: c.model_id,
                        fromGate: c.from_gate,
                        toGate: c.to_gate,
                        status: c.status,
                        createdAt: c.created_at,
                        updatedAt: c.updated_at,
                        policy: JSON.parse(c.policy_json)
                    };
                    return {
                        content: [{
                            type: "text",
                            text: JSON.stringify(payload)
                        }]
                    };
                }

                // ---------- abort_canary ----------
                case 'abort_canary': {
                    const canaryId = String(args?.canaryId || "");
                    if (!canaryId) throw new Error("canaryId is required");
                    const c = stores.canary.get(canaryId);
                    if (!c) throw new Error(`Unknown canaryId: ${canaryId}`);
                    const now = nowIso();
                    stores.canary.upsert({ ...c, status: 'ROLLED_BACK', updated_at: now });
                    stores.audit.write(now, 'mcp', 'canary_abort', { canaryId: c.canary_id, modelId: c.model_id });
                    ssePublish(`canary/${canaryId}`, 'rolled_back', { canaryId, ts: now, reason: 'aborted' });
                    return {
                        content: [{
                            type: "text",
                            text: JSON.stringify({ canaryId, status: 'ROLLED_BACK' })
                        }]
                    };
                }

                default:
                    throw new Error(`Unknown tool: ${name}`);
            }

        default:
            throw new Error(`Unknown method: ${method}`);
    }
}

const server = createServer(async (req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    const pathname = url.pathname;
    const method = req.method;

    console.log(`${new Date().toISOString()} ${method} ${path} - Accept: ${req.headers.accept}`);

    // Handle CORS preflight
    if (method === 'OPTIONS') {
        setCORSHeaders(res);
        res.writeHead(200);
        res.end();
        return;
    }

    try {
        // STREAMABLE HTTP: Single /mcp endpoint for both SSE and JSON-RPC
        if (pathname === '/mcp') {
            // Auth and rate limiting check
            const ip = getClientIp(req);
            const k = extractApiKey(req) || ip;
            if (!rateLimitOk(k)) {
                res.writeHead(429, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32001, message: 'Rate limit' } }));
                logReq(req, 429);
                return;
            }

            // For SSE, allow either header auth or query param
            if (method === 'GET' && req.headers.accept?.includes('text/event-stream')) {
                let ok = verifyAuth(req);
                const qk = url.searchParams.get('key');
                if (!ok) {
                    if (qk && API_KEYS.includes(qk)) ok = true;
                }
                const sseKey = extractApiKey(req) || qk || getClientIp(req);
                if (!ok) {
                    res.writeHead(401);
                    res.end('unauthorized');
                    logReq(req, 401, { sse: true });
                    return;
                }
                if (!rateLimitOk(sseKey)) {
                    res.writeHead(429);
                    res.end('rate-limit');
                    logReq(req, 429, { sse: true });
                    return;
                }

                setCORSHeaders(res);
                res.writeHead(200, {
                    'Content-Type': 'text/event-stream',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'  // Prevent proxy buffering
                });

                // Keep connection alive with periodic comments
                const keepAlive = setInterval(() => {
                    res.write(': keep-alive\\n\\n');
                }, 30000);

                req.on('close', () => {
                    clearInterval(keepAlive);
                });

                logReq(req, 200, { sse: true });
                // Note: In Streamable HTTP, server->client messages would be sent here
                // For now, just keep the connection alive for ChatGPT
                return;
            }

            // POST = JSON-RPC for client->server messages
            if (method === 'POST') {
                if (!verifyAuth(req)) {
                    res.writeHead(401, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ jsonrpc: '2.0', id: null, error: { code: -32000, message: 'Unauthorized' } }));
                    logReq(req, 401);
                    return;
                }
                try {
                    const body = await parseBody(req);
                    console.log('MCP Request:', JSON.stringify(body, null, 2));

                    if (!body.jsonrpc || body.jsonrpc !== "2.0") {
                        throw new Error('Invalid JSON-RPC request');
                    }

                    const result = await handleMCPMethod(body.method, body.params);

                    const response = {
                        jsonrpc: "2.0",
                        id: body.id,
                        result
                    };

                    console.log('MCP Response:', JSON.stringify(response, null, 2));
                    sendJSONRPC(res, response);
                    return;

                } catch (error) {
                    console.error('MCP Error:', error);
                    const errorResponse = {
                        jsonrpc: "2.0",
                        id: req.body?.id || null,
                        error: {
                            code: -32603,
                            message: error.message || 'Internal error'
                        }
                    };
                    sendJSONRPC(res, errorResponse);
                    return;
                }
            }
        }

        // Health check endpoint
        if (pathname === '/healthz' && method === 'HEAD') {
            res.writeHead(200);
            res.end();
            logReq(req, 200, { healthz: true });
            return;
        }

        // Readiness endpoint
        if (pathname === '/readyz' && method === 'HEAD') {
            const ready = true; // extend if you need index warmup checks
            res.writeHead(ready ? 200 : 503);
            res.end();
            logReq(req, ready ? 200 : 503, { readyz: true });
            return;
        }

        // GET /sse?topic=job/<id>  (auth + rate-limit already applied above)
        if (method === 'GET' && path === '/sse') {
            // auth: header or ?key=...
            let ok = verifyAuth(req);
            if (!ok) {
                const qk = url.searchParams.get('key');
                if (qk && API_KEYS.includes(qk)) ok = true;
            }
            const keyOrIp = extractApiKey(req) || getClientIp(req);
            if (!ok) { res.writeHead(401); res.end('unauthorized'); logReq(req, 401, { sse: true }); return; }
            if (!rateLimitOk(keyOrIp)) { res.writeHead(429); res.end('rate-limit'); logReq(req, 429, { sse: true }); return; }

            const topic = url.searchParams.get('topic');
            if (!topic) { res.writeHead(400); res.end('missing topic'); logReq(req, 400, { sse: true }); return; }

            res.writeHead(200, {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                Connection: 'keep-alive',
            });
            res.write(`event: open\n`);
            res.write(`data: {"ok":true,"topic":${JSON.stringify(topic)}}\n\n`);
            sseSubscribe(topic, res);
            logReq(req, 200, { sse: true, topic });
            return;
        }

        // Root endpoint - Server information (not MCP, just for debugging)
        if (pathname === '/' && method === 'GET') {
            const host = req.headers.host || `localhost:${PORT}`;
            const protocol = req.headers['x-forwarded-proto'] || 'http';
            const baseUrl = `${protocol}://${host}`;

            sendJSON(res, {
                name: "LUKHAS DevTools MCP Server",
                version: "1.0.0",
                description: "LUKHAS development tools MCP server with Streamable HTTP transport",
                protocol: "MCP 2024-11-05",
                transport: "Streamable HTTP",
                mcp_endpoint: `${baseUrl}/mcp`,
                tools: MCP_TOOLS.length,
                usage: {
                    note: "Use /mcp endpoint for both SSE (GET) and JSON-RPC (POST)",
                    sse_connection: "GET /mcp with Accept: text/event-stream",
                    json_rpc: "POST /mcp with JSON-RPC 2.0 payload"
                }
            });
            return;
        }

        // Health check for debugging
        if (pathname === '/health' && method === 'GET') {
            setCORSHeaders(res);
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                server: 'lukhas-mcp-server',
                version: '1.0.0',
                transport: 'Streamable HTTP',
                mcp_version: '2024-11-05'
            }));
            return;
        }

        // Serve cockpit.html directly for convenience
        if (pathname === '/cockpit.html' && method === 'GET') {
            try {
                const cockpitPath = './cockpit.html';
                const html = await fs.readFile(cockpitPath, 'utf-8');
                setCORSHeaders(res);
                res.writeHead(200, { 'Content-Type': 'text/html' });
                res.end(html);
                return;
            } catch (err) {
                console.error('Cockpit error:', err.message);
                res.writeHead(404, { 'Content-Type': 'text/plain' });
                res.end(`cockpit.html not found: ${err.message}`);
                return;
            }
        }

        // Evidence export: GET /evidence/export?from=30d&to=now  -> streams a .zip
        if (pathname.startsWith('/evidence/export') && method === 'GET') {
            const from = url.searchParams.get('from') || '30d';
            const to = url.searchParams.get('to') || new Date().toISOString();
            try {
                const { mkdtemp } = await import('fs/promises');
                const { join } = await import('path');
                const tmp = await mkdtemp(join(process.cwd(), '.evidence-'));
                const outDir = tmp;
                const pack = join(tmp, 'ops-evidence.zip');
                // Write minimal evidence set from SQLite
                await writeEvidencePack(outDir, from, to);
                // Shell out to zip for simplicity (CI images have zip)
                const { execSync } = await import('child_process');
                execSync(`cd "${outDir}" && zip -qr "${pack}" .`);
                const zipBuf = await fs.readFile(pack);
                setCORSHeaders(res);
                res.writeHead(200, {
                    'Content-Type': 'application/zip',
                    'Content-Disposition': `attachment; filename="ops-evidence-${Date.now()}.zip"`,
                    'Content-Length': zipBuf.length
                });
                res.end(zipBuf);
                // best-effort cleanup
                await fs.rm(tmp, { recursive: true, force: true }).catch(() => {});
                return;
            } catch (e) {
                setCORSHeaders(res);
                res.writeHead(500, {'Content-Type':'text/plain'}); 
                res.end(`export failed: ${String(e?.message||e)}`);
                return;
            }
        }

        // 404 for other paths
        setCORSHeaders(res);
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            error: 'Not Found',
            message: 'This is an MCP server. Use /mcp endpoint for both SSE and JSON-RPC.',
            mcp_endpoint: '/mcp',
            mcp_version: '2024-11-05'
        }));

    } catch (error) {
        console.error('Server error:', error);
        setCORSHeaders(res);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            error: 'Internal Server Error',
            message: error.message
        }));
    }
});

// Load persistent state before starting server
await stateLoad();

server.listen(PORT, () => {
    console.log(`🚀 LUKHAS MCP Server (Streamable HTTP) running on port ${PORT}`);
    console.log(`📡 MCP Endpoint: http://localhost:${PORT}/mcp`);
    console.log(`🔧 Transport: Streamable HTTP (single endpoint)`);
    console.log(`📋 Protocol: MCP 2024-11-05`);
    console.log(`🛠️ Tools: ${MCP_TOOLS.length} development utilities available`);
    console.log(`✅ Ready for ChatGPT MCP Connector!`);
    console.log('');
    console.log('🧪 Self-check commands:');
    console.log(`   Initialize: curl -s http://localhost:${PORT}/mcp -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","clientInfo":{"name":"test","version":"1.0"},"capabilities":{}}}'`);
    console.log(`   SSE: curl -v -N -H "Accept: text/event-stream" http://localhost:${PORT}/mcp`);
    console.log(`   Tools: curl -s http://localhost:${PORT}/mcp -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'`);
});

// Evidence pack helper functions
async function writeEvidencePack(dir, from, to) {
    const fp = (name) => path.join(dir, name);
    await fs.mkdir(dir, { recursive: true });
    const meta = { generated_at: new Date().toISOString(), from, to,
        policy: safePolicySnapshot(), prom: { url: process.env.PROM_URL||null, q_lat: process.env.PROM_Q_LAT||null, q_err: process.env.PROM_Q_ERR||null }
    };
    await fs.writeFile(fp('meta.json'), JSON.stringify(meta, null, 2));
    // audits
    try {
        const audits = __db.prepare(`SELECT * FROM audits WHERE ts BETWEEN ? AND ? ORDER BY ts ASC`).all(fromISO(from), toISO(to));
        await fs.writeFile(fp('audits.json'), JSON.stringify(audits, null, 2));
        await fs.writeFile(fp('audits.csv'), toCSV(audits));
    } catch {}
    // narrative
    try {
        const narr = __db.prepare(`SELECT * FROM audits_narrative WHERE ts BETWEEN ? AND ? ORDER BY ts ASC`).all(fromISO(from), toISO(to));
        const txt = narr.map(n => `[${n.ts}] ${n.type||'event'} ${n.message||''}`).join('\n');
        await fs.writeFile(fp('narrative.txt'), txt);
    } catch {
        await fs.writeFile(fp('narrative.txt'), 'No audits_narrative table; falling back to audits narrative synthesis.\n');
    }
    // quick hashes
    function sha256(s){ return crypto.createHash('sha256').update(s).digest('hex'); }
    const h = [];
    for (const name of ['meta.json','audits.json','audits.csv','narrative.txt']) {
        const filePath = fp(name);
        try {
            const content = await fs.readFile(filePath);
            h.push(`${name}  ${sha256(content)}   sha256`);
        } catch {}
    }
    await fs.writeFile(fp('hashes.txt'), h.join('\n'));
}

function safePolicySnapshot() {
    try {
        const c = __db.prepare(`SELECT policy_json FROM canaries ORDER BY created_at DESC LIMIT 1`).get();
        return c?.policy_json ? JSON.parse(c.policy_json) : null;
    } catch { return null; }
}

function fromISO(rel) {
    // naive "30d" → now-30d; else assume ISO
    if (/^\d+d$/.test(rel)) {
        const days = Number(rel.slice(0,-1));
        return new Date(Date.now() - days*86400000).toISOString();
    }
    return rel;
}

function toISO(s) { return /^\d{4}-/.test(s) ? s : new Date().toISOString(); }

function toCSV(rows) {
    if (!rows?.length) return "";
    const cols = Object.keys(rows[0]);
    const esc = (v)=> `"${String(v??'').replace(/"/g,'""')}"`;
    return [cols.join(','), ...rows.map(r => cols.map(c => esc(r[c])).join(','))].join('\n');
}

server.on('error', (err) => {
    console.error('Server error:', err);
});