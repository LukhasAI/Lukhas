import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// A custom trend metric to track response times
const responseTimeTrend = new Trend('response_time');

export const options = {
  scenarios: {
    // Scenario 1: Sustained load
    sustained_load: {
      executor: 'constant-vus',
      vus: 20,
      duration: '5m',
      tags: { test_type: 'sustained_load' },
    },
    // Scenario 2: Spike load
    spike_load: {
      executor: 'ramping-vus',
      startTime: '5m', // Start after the sustained load test
      startVUs: 0,
      stages: [
        { duration: '10s', target: 100 }, // Ramp up to 100 VUs in 10s
        { duration: '30s', target: 100 }, // Stay at 100 VUs for 30s
        { duration: '10s', target: 0 },   // Ramp down to 0 VUs
      ],
      gracefulRampDown: '5s',
      tags: { test_type: 'spike_load' },
    },
  },
  thresholds: {
    'http_req_failed': ['rate<0.01'], // http errors should be less than 1%
    'http_req_duration': ['p(95)<500'], // 95% of requests should be below 500ms
  },
};

export default function () {
  const res = http.get('http://localhost:8000/feedback/health');

  // Check if the request was successful
  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  // Add response time to our custom trend metric
  responseTimeTrend.add(res.timings.duration);

  // Wait for 1 second before the next request
  sleep(1);
}
