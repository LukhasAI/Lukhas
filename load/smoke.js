/**
 * k6 Smoke Test - Quick Sanity Check
 * 
 * Purpose: Verify basic API functionality with minimal load
 * Duration: 30 seconds
 * VUs: 5 concurrent users
 * 
 * Usage:
 *   k6 run load/smoke.js
 *   make load-smoke
 */

import http from 'k6/http';
import { sleep, check, group } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  vus: 5,
  duration: '30s',
  thresholds: {
    'http_req_duration': ['p(95)<500'], // 95% of requests should complete within 500ms (consciousness stream SLO)
    'http_req_failed': ['rate<0.01'],   // Less than 1% error rate
    'checks': ['rate>0.99'],            // 99% of checks should pass
  },
};

// Base URL - override with K6_BASE_URL environment variable
const BASE_URL = __ENV.K6_BASE_URL || 'http://localhost:8000';

export default function () {
  group('Health Check', function () {
    const healthRes = http.get(`${BASE_URL}/health`);
    const healthCheck = check(healthRes, {
      'health endpoint returns 200': (r) => r.status === 200,
      'health response has status field': (r) => JSON.parse(r.body).status !== undefined,
    });
    errorRate.add(!healthCheck);
  });

  group('Response Generation', function () {
    const payload = JSON.stringify({
      input: 'test consciousness stream',
      tools: [],
    });

    const params = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${__ENV.API_KEY || 'test-key'}`,
      },
    };

    const respRes = http.post(`${BASE_URL}/v1/responses`, payload, params);
    const respCheck = check(respRes, {
      'response endpoint returns 200 or 201': (r) => [200, 201].includes(r.status),
      'response has required fields': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.id && body.created;
        } catch {
          return false;
        }
      },
      'response time < 500ms': (r) => r.timings.duration < 500,
    });
    errorRate.add(!respCheck);
  });

  group('OpenAI Chat Completion', function () {
    const payload = JSON.stringify({
      model: 'lukhas-consciousness-v1',
      messages: [
        { role: 'user', content: 'Hello, test message' }
      ],
      max_tokens: 50,
    });

    const params = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${__ENV.API_KEY || 'test-key'}`,
      },
    };

    const chatRes = http.post(`${BASE_URL}/v1/chat/completions`, payload, params);
    const chatCheck = check(chatRes, {
      'chat endpoint returns 200': (r) => r.status === 200,
      'chat response has choices': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.choices && body.choices.length > 0;
        } catch {
          return false;
        }
      },
    });
    errorRate.add(!chatCheck);
  });

  // Sleep between iterations (0.5s = ~2 req/s per VU)
  sleep(0.5);
}

/**
 * Setup function - runs once before test
 */
export function setup() {
  console.log(`Starting smoke test against ${BASE_URL}`);
  console.log(`VUs: ${options.vus}, Duration: ${options.duration}`);
  return { startTime: new Date().toISOString() };
}

/**
 * Teardown function - runs once after test
 */
export function teardown(data) {
  console.log(`Smoke test completed. Started at: ${data.startTime}`);
}
