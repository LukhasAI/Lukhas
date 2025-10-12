import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = { vus: 50, duration: '2m' };

export default function () {
  const url = 'http://localhost:8000/v1/responses';
  const payload = JSON.stringify({ input: 'ping', tools: [] });
  const res = http.post(url, payload, { headers: { 'Content-Type': 'application/json' }});
  check(res, { '200': (r) => r.status === 200 });
  sleep(0.2);
}
