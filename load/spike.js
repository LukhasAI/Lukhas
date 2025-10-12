/**
 * k6 Spike Test - Sudden Traffic Burst Testing
 * 
 * Purpose: Test system behavior under sudden traffic spikes
 * Duration: 5 minutes
 * VUs: 0 → 200 → 0 (rapid scaling)
 * 
 * Usage:
 *   k6 run load/spike.js
 *   make load-spike
 */

import http from 'k6/http';
import { sleep, check, group } from 'k6';
import { Rate, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const spikeErrors = new Counter('spike_phase_errors');

// Spike test configuration
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Baseline: 10 VUs
    { duration: '1m', target: 200 },   // SPIKE: Rapid ramp to 200 VUs
    { duration: '2m', target: 200 },   // SUSTAIN: Hold 200 VUs for 2 minutes
    { duration: '1m', target: 10 },    // RECOVERY: Drop back to 10 VUs
    { duration: '30s', target: 0 },    // COOLDOWN: Ramp down to 0
  ],
  thresholds: {
    // More lenient thresholds for spike test
    'http_req_duration': ['p(95)<1000', 'p(99)<2000'], // Allow higher latency during spike
    'http_req_failed': ['rate<0.05'],                   // Allow up to 5% errors during spike
    'checks': ['rate>0.90'],                            // 90% checks pass
  },
};

const BASE_URL = __ENV.K6_BASE_URL || 'http://localhost:8000';

export default function () {
  const vuId = __VU;
  const iterationId = __ITER;

  // Determine current phase based on execution time
  const executionTime = Date.now();

  group('Spike Load - Mixed Requests', function () {
    // Simple health check (10% of requests)
    if (Math.random() < 0.1) {
      const healthRes = http.get(`${BASE_URL}/health`);
      const healthCheck = check(healthRes, {
        'health check OK': (r) => r.status === 200,
      });
      if (!healthCheck) {
        errorRate.add(1);
        spikeErrors.add(1);
      }
    }
    // Standard response generation (60% of requests)
    else if (Math.random() < 0.7) {
      const payload = JSON.stringify({
        input: `Spike test message ${vuId}-${iterationId}`,
        tools: [],
        stream: false,
      });

      const params = {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${__ENV.API_KEY || 'test-key'}`,
        },
        timeout: '10s', // Longer timeout for spike conditions
      };

      const res = http.post(`${BASE_URL}/v1/responses`, payload, params);
      const passed = check(res, {
        'response status acceptable': (r) => [200, 201, 429, 503].includes(r.status), // Accept rate limiting
        'response not timeout': (r) => r.status !== 0,
      });

      if (!passed) {
        errorRate.add(1);
        if (res.status === 503 || res.status === 429) {
          // Expected during spike - don't count as spike errors
          console.log(`VU ${vuId}: Rate limited or service unavailable (expected during spike)`);
        } else {
          spikeErrors.add(1);
        }
      }
    }
    // Chat completions (30% of requests)
    else {
      const payload = JSON.stringify({
        model: 'lukhas-consciousness-v1',
        messages: [
          { role: 'user', content: 'Quick test during spike' }
        ],
        max_tokens: 50,
      });

      const params = {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${__ENV.API_KEY || 'test-key'}`,
        },
        timeout: '10s',
      };

      const res = http.post(`${BASE_URL}/v1/chat/completions`, payload, params);
      const passed = check(res, {
        'chat status acceptable': (r) => [200, 429, 503].includes(r.status),
      });

      if (!passed) {
        errorRate.add(1);
        spikeErrors.add(1);
      }
    }
  });

  // Minimal sleep during spike (0.05-0.15s)
  sleep(Math.random() * 0.1 + 0.05);
}

export function setup() {
  console.log('═'.repeat(70));
  console.log('                      SPIKE TEST INITIATED                           ');
  console.log('═'.repeat(70));
  console.log(`Target: ${BASE_URL}`);
  console.log(`Duration: 5 minutes`);
  console.log(`Spike Pattern: 10 → 200 → 200 → 10 → 0 VUs`);
  console.log('');
  console.log('Phase 1 (0:00-0:30):   Baseline (10 VUs)');
  console.log('Phase 2 (0:30-1:30):   SPIKE! (10→200 VUs)');
  console.log('Phase 3 (1:30-3:30):   Sustain (200 VUs)');
  console.log('Phase 4 (3:30-4:30):   Recovery (200→10 VUs)');
  console.log('Phase 5 (4:30-5:00):   Cooldown (10→0 VUs)');
  console.log('═'.repeat(70));

  // Pre-flight check
  const health = http.get(`${BASE_URL}/health`);
  if (health.status !== 200) {
    console.error(`⚠️  WARNING: Health check failed (${health.status}). Proceeding anyway...`);
  } else {
    console.log('✓ Pre-flight health check passed');
  }

  return {
    startTime: new Date().toISOString(),
    baseUrl: BASE_URL,
  };
}

export function teardown(data) {
  console.log('═'.repeat(70));
  console.log('                    SPIKE TEST COMPLETED                            ');
  console.log('═'.repeat(70));
  console.log(`Started:   ${data.startTime}`);
  console.log(`Completed: ${new Date().toISOString()}`);
  console.log(`Target:    ${data.baseUrl}`);
  console.log('');
  console.log('Key Observations:');
  console.log('  - Check metrics for spike phase performance degradation');
  console.log('  - Review error rates during 200 VU sustain period');
  console.log('  - Verify system recovery after spike');
  console.log('  - Look for memory leaks or resource exhaustion');
  console.log('═'.repeat(70));
}
