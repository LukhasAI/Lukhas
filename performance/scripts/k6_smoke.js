import http from 'k6/http';
import { check, sleep, group } from 'k6';

export const options = {
  scenarios: {
    smoke: {
      executor: 'constant-vus',
      vus: 10,
      duration: '45s',
    },
    spike: {
      executor: 'ramping-arrival-rate',
      startRate: 5,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 100,
      stages: [
        { target: 50, duration: '30s' },
        { target: 5, duration: '15s' },
      ],
      startTime: '45s',
    },
  },
  thresholds: {
    'http_req_duration{endpoint:health}': ['p(95)<120'],
    'http_req_duration{endpoint:tools}':  ['p(95)<200'],
    'http_req_duration{endpoint:openapi}':['p(95)<350'],
    'http_req_failed': ['rate<0.01'],
  },
  summaryTrendStats: ['avg','p(90)','p(95)','p(99)','min','max'],
};

const BASE = __ENV.BASE_URL || 'http://127.0.0.1:8000';

export default function () {
  group('read-only endpoints', () => {
    const r1 = http.get(`${BASE}/feedback/health`, { tags: { endpoint: 'health' } });
    check(r1, { '200 health': (r) => r.status === 200 });

    const r2 = http.get(`${BASE}/tools/registry`, { tags: { endpoint: 'tools' } });
    check(r2, { '200 tools': (r) => r.status === 200 });

    const r3 = http.get(`${BASE}/openapi.json`, { tags: { endpoint: 'openapi' } });
    check(r3, { '200 openapi': (r) => r.status === 200 });
  });
  sleep(Math.random() * 0.5 + 0.1);
}

// Write JSON summary to disk for CI artifacts/dashboards
export function handleSummary(data) {
  const path = __ENV.SUMMARY_JSON || 'out/k6_summary.json';
  return {
    [path]: JSON.stringify(data, null, 2),
    stdout: `\nk6 summary written to ${path}\n`,
  };
}
