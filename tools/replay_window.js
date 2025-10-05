#!/usr/bin/env node
/**
 * Counterfactual replay: decide promote/rollback over a time window using a policy.
 * Usage: node tools/replay_window.js --from ISO --to ISO --model matriz-v3 --policy configs/slo-prod.json --report replay.html
 */
import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';

function arg(name, def) { const i = process.argv.indexOf(`--${name}`); return i > 0 ? (process.argv[i + 1] || '') : def; }
const FROM = arg('from'); const TO = arg('to');
const MODEL = arg('model');
const POLICY_PATH = arg('policy', '');
const REPORT = arg('report', `replay-${Date.now()}.html`);
const DB_PATH = process.env.LUKHAS_MCP_DB || path.join(process.cwd(), '.mcp-state.db');

if (!FROM || !TO || !MODEL) { console.error('Missing --from/--to/--model'); process.exit(2); }
const policy = POLICY_PATH && fs.existsSync(POLICY_PATH) ? JSON.parse(fs.readFileSync(POLICY_PATH, 'utf8')) : { targets: { latency_p95_ms: 250, max_error_rate: 0.02, max_drift: 0.15 } };

const db = new Database(DB_PATH);
// Prefer canary_metrics if present; otherwise synthesize zeros (conservative block).
let rows = [];
try {
    rows = db.prepare(`SELECT * FROM canary_metrics WHERE ts BETWEEN ? AND ? AND (modelId = ? OR canary_id IN (SELECT canary_id FROM canaries WHERE modelId = ?)) ORDER BY ts ASC`).all(FROM, TO, MODEL, MODEL);
} catch { }
function avg(arr, k) { const v = arr.map(x => Number(x[k])).filter(Number.isFinite); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : NaN; }
const latency = avg(rows, 'latency_p95_ms');
const error = avg(rows, 'error_rate');
const drift = avg(rows, 'drift_score');
const obs = { latency_p95_ms: latency, error_rate: error, drift };
const thr = policy.targets || {};
const decision = (
    (Number.isFinite(latency) ? latency <= (thr.latency_p95_ms ?? Infinity) : false) &&
    (Number.isFinite(error) ? error <= (thr.max_error_rate ?? Infinity) : false) &&
    (Number.isFinite(drift) ? drift <= (thr.max_drift ?? Infinity) : true)
) ? 'PROMOTE' : 'ROLLBACK';

const html = `<!doctype html><meta charset="utf-8">
<title>Counterfactual Replay</title>
<style>body{font:14px system-ui;background:#0b0d12;color:#e8eef8;padding:16px} code{background:#111a2a;padding:2px 6px;border-radius:6px}</style>
<h1>Counterfactual Replay</h1>
<p><b>Window:</b> <code>${FROM}</code> → <code>${TO}</code></p>
<p><b>Model:</b> <code>${MODEL}</code></p>
<p><b>Decision:</b> <code style="color:${decision === 'PROMOTE' ? '#2ecc71' : '#e74c3c'}">${decision}</code></p>
<h3>Observed</h3><pre>${JSON.stringify(obs, null, 2)}</pre>
<h3>Thresholds</h3><pre>${JSON.stringify(thr, null, 2)}</pre>
<h3>Samples</h3><pre>${rows.slice(0, 50).map(r => JSON.stringify(r)).join('\n')}</pre>`;
fs.writeFileSync(REPORT, html);
console.log(JSON.stringify({ decision, observed: obs, thresholds: thr, report: REPORT }, null, 2));