// adapters/sloMonitor.prom.js
// Prometheus-backed SLO sampling. No wire changes.
import http from "http";
import https from "https";
import { URL } from "url";

/**
 * ENV:
 *  PROM_URL: base URL, e.g. https://prometheus.example.com
 *  PROM_BEARER: optional bearer token
 *  PROM_QUERY_LAT: promql with $__window and $__gate variables
 *  PROM_QUERY_ERR: promql with $__window and $__gate variables (return error_rate in 0..1)
 *
 * Defaults assume 'model_latency_ms{gate="<gate>"}' and 'model_errors_total' series exist.
 */
const PROM_URL = process.env.PROM_URL || "http://localhost:9090";
const PROM_BEARER = process.env.PROM_BEARER || "";

const Q_LAT =
    process.env.PROM_QUERY_LAT ||
    `histogram_quantile(0.95, sum(rate(model_latency_bucket{gate="$__gate"}[$__window])) by (le))`;
const Q_ERR =
    process.env.PROM_QUERY_ERR ||
    `sum(rate(model_errors_total{gate="$__gate"}[$__window])) / clamp_min(sum(rate(model_requests_total{gate="$__gate"}[$__window])), 1)`;

function httpGetJson(url, headers = {}) {
    return new Promise((resolve, reject) => {
        const u = new URL(url);
        const lib = u.protocol === "https:" ? https : http;
        const req = lib.get(
            {
                hostname: u.hostname,
                port: u.port || (u.protocol === "https:" ? 443 : 80),
                path: u.pathname + u.search,
                headers: { ...(PROM_BEARER ? { Authorization: `Bearer ${PROM_BEARER}` } : {}), ...headers },
            },
            (res) => {
                let body = "";
                res.on("data", (c) => (body += c));
                res.on("end", () => {
                    try {
                        const j = JSON.parse(body);
                        if (j.status !== "success") return reject(new Error(`Prom status=${j.status}`));
                        resolve(j.data);
                    } catch (e) {
                        reject(e);
                    }
                });
            }
        );
        req.on("error", reject);
    });
}

async function instantQuery(query) {
    const url = `${PROM_URL}/api/v1/query?query=${encodeURIComponent(query)}`;
    const data = await httpGetJson(url);
    const v = data?.result?.[0]?.value?.[1];
    return v != null ? Number(v) : NaN;
}

export const sloMonitor = {
    /**
     * Sample p95 latency (ms) and error rate (0..1) for gate in the last windowSeconds.
     */
    async sample({ modelId, gate, windowSeconds }) {
        const window = `${Math.max(30, windowSeconds)}s`;
        const latQ = Q_LAT.replaceAll("$__window", window).replaceAll("$__gate", gate);
        const errQ = Q_ERR.replaceAll("$__window", window).replaceAll("$__gate", gate);
        const [lat, err] = await Promise.all([instantQuery(latQ), instantQuery(errQ)]);
        // If Prom misses, return NaNs to force conservative decisions upstream
        return {
            latency_p95_ms: Number.isFinite(lat) ? lat : 9999,
            error_rate: Number.isFinite(err) ? err : 1,
            source: "prometheus",
            window,
            gate,
            modelId,
        };
    },
};