// mcp-servers/lukhas-devtools-mcp/persistence/sqlite.js
import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';

export function openDB(dbPath, { wal = true } = {}) {
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const db = new Database(dbPath, { fileMustExist: false });
    if (wal) db.pragma('journal_mode = WAL');
    db.pragma('foreign_keys = ON');

    db.exec(`
    CREATE TABLE IF NOT EXISTS jobs (
      job_id TEXT PRIMARY KEY,
      task_id TEXT NOT NULL,
      config_id TEXT NOT NULL,
      status TEXT NOT NULL,
      started_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      result_json TEXT
    );
    CREATE TABLE IF NOT EXISTS models (
      model_id TEXT PRIMARY KEY,
      promoted INTEGER NOT NULL DEFAULT 0,
      promoted_at TEXT
    );
    CREATE TABLE IF NOT EXISTS model_gates (
      model_id TEXT NOT NULL,
      gate TEXT NOT NULL,
      PRIMARY KEY (model_id, gate),
      FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS audits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      ts TEXT NOT NULL,
      actor TEXT,
      action TEXT NOT NULL,
      payload_json TEXT
    );
    CREATE TABLE IF NOT EXISTS canaries (
      canary_id TEXT PRIMARY KEY,
      model_id TEXT NOT NULL,
      from_gate TEXT NOT NULL,
      to_gate   TEXT NOT NULL,
      status    TEXT NOT NULL,           -- PENDING|RUNNING|PROMOTED|ROLLED_BACK|FAILED
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      policy_json TEXT NOT NULL          -- {windowSeconds, targets:{latency_p95_ms, max_error_rate}}
    );
    CREATE TABLE IF NOT EXISTS canary_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        canary_id TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        latency_p95_ms REAL,
        error_rate REAL,
        gate TEXT,
        source TEXT DEFAULT 'sloMonitor',
        raw_data TEXT
    );

    CREATE TABLE IF NOT EXISTS audits_narrative (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT NOT NULL,
        entity_id TEXT,
        entity_type TEXT,
        message TEXT NOT NULL,
        operator TEXT,
        context TEXT
    );
  `);

    return db;
}

export function createStores(db) {
    // JOBS
    const upsertJob = db.prepare(`
    INSERT INTO jobs(job_id, task_id, config_id, status, started_at, updated_at, result_json)
    VALUES (@job_id, @task_id, @config_id, @status, @started_at, @updated_at, @result_json)
    ON CONFLICT(job_id) DO UPDATE SET
      status=excluded.status,
      updated_at=excluded.updated_at,
      result_json=excluded.result_json;
  `);
    const getJob = db.prepare(`SELECT * FROM jobs WHERE job_id = ?`);
    const sweepJobs = db.prepare(`DELETE FROM jobs WHERE strftime('%s', updated_at) < ?`);

    // MODELS + GATES
    const upsertModel = db.prepare(`
    INSERT INTO models(model_id, promoted, promoted_at)
    VALUES (@model_id, @promoted, @promoted_at)
    ON CONFLICT(model_id) DO UPDATE SET
      promoted=excluded.promoted,
      promoted_at=excluded.promoted_at;
  `);
    const addGate = db.prepare(`INSERT OR IGNORE INTO model_gates(model_id, gate) VALUES (?, ?)`);
    const listGates = db.prepare(`SELECT gate FROM model_gates WHERE model_id = ? ORDER BY gate`);
    const getModel = db.prepare(`SELECT * FROM models WHERE model_id = ?`);

    // AUDIT
    const insertAudit = db.prepare(`
    INSERT INTO audits(ts, actor, action, payload_json) VALUES(?, ?, ?, ?)
  `);
    const insertNarrative = db.prepare(`
    INSERT INTO audits_narrative(event_type, entity_id, entity_type, message, operator, context)
    VALUES (?, ?, ?, ?, ?, ?)
  `);

    // CANARIES
    const upsertCanary = db.prepare(`
    INSERT INTO canaries(canary_id, model_id, from_gate, to_gate, status, created_at, updated_at, policy_json)
    VALUES (@canary_id, @model_id, @from_gate, @to_gate, @status, @created_at, @updated_at, @policy_json)
    ON CONFLICT(canary_id) DO UPDATE SET
      status=excluded.status,
      updated_at=excluded.updated_at,
      policy_json=excluded.policy_json;
  `);
    const getCanary = db.prepare(`SELECT * FROM canaries WHERE canary_id = ?`);
    const addMetric = db.prepare(`
    INSERT INTO canary_metrics(canary_id, created_at, latency_p95_ms, error_rate, gate, source, raw_data) 
    VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
  `);

    return {
        job: {
            upsert: (j) => upsertJob.run(j),
            get: (id) => getJob.get(id),
            sweepOlderThanUnix: (unix) => sweepJobs.run(unix).changes,
            insertNarrative: (eventType, entityId, message, operator = 'system', context = null) => {
                return insertNarrative.run(eventType, entityId, 'job', message, operator, context ? JSON.stringify(context) : null);
            }
        },
        model: {
            upsert: (m) => upsertModel.run(m),
            addGate: (modelId, gate) => addGate.run(modelId, gate),
            gates: (modelId) => listGates.all(modelId).map(r => r.gate),
            get: (id) => getModel.get(id)
        },
        audit: {
            write: (ts, actor, action, payload) => insertAudit.run(ts, actor, action, JSON.stringify(payload ?? {})),
            narrative: (eventType, entityId, entityType, message, operator = 'system', context = null) => {
                return insertNarrative.run(eventType, entityId, entityType, message, operator, context ? JSON.stringify(context) : null);
            }
        },
        canary: {
            upsert: (c) => upsertCanary.run(c),
            get: (id) => getCanary.get(id),
            addMetric: (canaryId, metrics) => {
                return addMetric.run(
                    canaryId,
                    metrics.latency_p95_ms,
                    metrics.error_rate,
                    metrics.gate || 'unknown',
                    metrics.source || 'sloMonitor',
                    JSON.stringify(metrics)
                );
            },
            insertNarrative: (eventType, entityId, message, operator = 'system', context = null) => {
                return insertNarrative.run(eventType, entityId, 'canary', message, operator, context ? JSON.stringify(context) : null);
            }
        }
    };
}