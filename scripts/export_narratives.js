#!/usr/bin/env node
/**
 * Evidence pack exporter.
 * Usage: node scripts/export_narratives.js --from 30d --to now --out ops-evidence.zip
 */
import Database from 'better-sqlite3';
import { execSync } from 'child_process';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

function arg(name, def) { const i = process.argv.indexOf(`--${name}`); return i > 0 ? (process.argv[i + 1] || '') : def; }
const FROM = arg('from', '30d');
const TO = arg('to', new Date().toISOString());
const OUT = arg('out', `ops-evidence-${Date.now()}.zip`);
const DB_PATH = process.env.LUKHAS_MCP_DB || path.join(process.cwd(), '.mcp-state.db');

const db = new Database(DB_PATH);
const tmp = fs.mkdtempSync(path.join(process.cwd(), '.evidence-'));
const w = (p, d) => fs.writeFileSync(path.join(tmp, p), d);
const sha256 = (buf) => crypto.createHash('sha256').update(buf).digest('hex');

function relToISO(rel) {
    if (/^\d+d$/.test(rel)) { const days = Number(rel.slice(0, -1)); return new Date(Date.now() - days * 86400000).toISOString(); }
    return rel;
}
function toCSV(rows) {
    if (!rows?.length) return ""; const cols = Object.keys(rows[0]);
    const esc = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
    return [cols.join(','), ...rows.map(r => cols.map(c => esc(r[c])).join(','))].join('\n');
}

const meta = {
    generated_at: new Date().toISOString(),
    from: FROM, to: TO,
    policy: (() => { try { const c = db.prepare('SELECT policy_json FROM canaries ORDER BY created_at DESC LIMIT 1').get(); return c?.policy_json ? JSON.parse(c.policy_json) : null; } catch { return null; } })(),
    prom: { url: process.env.PROM_URL || null, q_lat: process.env.PROM_Q_LAT || null, q_err: process.env.PROM_Q_ERR || null },
};
w('meta.json', JSON.stringify(meta, null, 2));

try {
    const audits = db.prepare('SELECT * FROM audits WHERE ts BETWEEN ? AND ? ORDER BY ts ASC').all(relToISO(FROM), relToISO(TO));
    w('audits.json', JSON.stringify(audits, null, 2));
    w('audits.csv', toCSV(audits));
} catch { }
try {
    const narr = db.prepare('SELECT * FROM audits_narrative WHERE ts BETWEEN ? AND ? ORDER BY ts ASC').all(relToISO(FROM), relToISO(TO));
    const txt = narr.map(n => `[${n.ts}] ${n.type || 'event'} ${n.message || ''}`).join('\n');
    w('narrative.txt', txt);
} catch {
    w('narrative.txt', 'No audits_narrative table; consider upgrading.');
}
const hashes = [];
for (const f of ['meta.json', 'audits.json', 'audits.csv', 'narrative.txt']) {
    const p = path.join(tmp, f); if (fs.existsSync(p)) hashes.push(`${f}  ${sha256(fs.readFileSync(p))}   sha256`);
}
w('hashes.txt', hashes.join('\n'));
execSync(`cd "${tmp}" && zip -qr "${OUT}" .`);
fs.copyFileSync(path.join(tmp, OUT), path.join(process.cwd(), OUT));
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`Wrote ${OUT}`);