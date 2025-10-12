/**
 * k6 Extended Load Test - Sustained Stress Testing
 * 
 * Purpose: Long-running load test to identify memory leaks, performance degradation
 * Duration: 10 minutes
 * VUs: 100 concurrent users (ramping)
 * 
 * Usage:
 *   k6 run load/extended.js
 *   make load-extended
 */

import { check, group, sleep } from 'k6';
import http from 'k6/http';
import { Counter, Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const responseTime = new Trend('custom_response_time');
const requestCounter = new Counter('total_requests');

// Test configuration with ramping stages
export const options = {
    stages: [
        { duration: '1m', target: 20 },   // Ramp up to 20 VUs over 1 minute
        { duration: '3m', target: 50 },   // Ramp up to 50 VUs over 3 minutes
        { duration: '4m', target: 100 },  // Ramp up to 100 VUs over 4 minutes
        { duration: '2m', target: 0 },    // Ramp down to 0 VUs over 2 minutes
    ],
    thresholds: {
        'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95th percentile < 500ms, 99th < 1s
        'http_req_failed': ['rate<0.01'],                  // Less than 1% error rate
        'checks': ['rate>0.95'],                           // 95% of checks pass (more lenient for stress test)
        'custom_response_time': ['p(95)<500'],             // Custom metric threshold
    },
};

// Base URL
const BASE_URL = __ENV.K6_BASE_URL || 'http://localhost:8000';

// Test data variants
const testInputs = [
    'Analyze this consciousness pattern',
    'Generate a symbolic representation',
    'Process this quantum state',
    'What is the meaning of consciousness?',
    'Explain the MATRIZ cognitive architecture',
    'How does bio-inspired processing work?',
];

const models = [
    'lukhas-consciousness-v1',
    'lukhas-vision-v1',
    'lukhas-quantum-v1',
];

export default function () {
    const input = testInputs[Math.floor(Math.random() * testInputs.length)];
    const model = models[Math.floor(Math.random() * models.length)];

    group('Mixed Workload', function () {
        // 70% regular responses
        if (Math.random() < 0.7) {
            const payload = JSON.stringify({
                input: input,
                tools: [],
                stream: false,
            });

            const params = {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${__ENV.API_KEY || 'test-key'}`,
                },
            };

            const start = Date.now();
            const res = http.post(`${BASE_URL}/v1/responses`, payload, params);
            const duration = Date.now() - start;

            responseTime.add(duration);
            requestCounter.add(1);

            const passed = check(res, {
                'status is 200 or 201': (r) => [200, 201].includes(r.status),
                'response has id': (r) => {
                    try {
                        return JSON.parse(r.body).id !== undefined;
                    } catch {
                        return false;
                    }
                },
                'response time acceptable': (r) => r.timings.duration < 1000,
            });
            errorRate.add(!passed);
        }
        // 30% chat completions
        else {
            const payload = JSON.stringify({
                model: model,
                messages: [
                    { role: 'system', content: 'You are a consciousness-aware AI assistant.' },
                    { role: 'user', content: input }
                ],
                max_tokens: 100,
                temperature: 0.7,
            });

            const params = {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${__ENV.API_KEY || 'test-key'}`,
                },
            };

            const start = Date.now();
            const res = http.post(`${BASE_URL}/v1/chat/completions`, payload, params);
            const duration = Date.now() - start;

            responseTime.add(duration);
            requestCounter.add(1);

            const passed = check(res, {
                'chat status is 200': (r) => r.status === 200,
                'chat has choices': (r) => {
                    try {
                        const body = JSON.parse(r.body);
                        return body.choices && body.choices.length > 0;
                    } catch {
                        return false;
                    }
                },
            });
            errorRate.add(!passed);
        }
    });

    // Variable sleep time (0.1-0.3s) to simulate realistic traffic patterns
    sleep(Math.random() * 0.2 + 0.1);
}

export function setup() {
    console.log('='.repeat(60));
    console.log('Starting Extended Load Test');
    console.log('='.repeat(60));
    console.log(`Target: ${BASE_URL}`);
    console.log(`Duration: 10 minutes`);
    console.log(`Max VUs: 100`);
    console.log(`Ramping Strategy: 20 → 50 → 100 → 0`);
    console.log('='.repeat(60));

    // Warm-up request
    const warmup = http.get(`${BASE_URL}/health`);
    if (warmup.status !== 200) {
        console.error(`WARNING: Health check returned ${warmup.status}`);
    }

    return {
        startTime: new Date().toISOString(),
        baseUrl: BASE_URL,
    };
}

export function teardown(data) {
    console.log('='.repeat(60));
    console.log('Extended Load Test Completed');
    console.log('='.repeat(60));
    console.log(`Started: ${data.startTime}`);
    console.log(`Completed: ${new Date().toISOString()}`);
    console.log(`Target: ${data.baseUrl}`);
    console.log('='.repeat(60));
}

/**
 * Handle summary for custom reporting
 */
export function handleSummary(data) {
    return {
        'stdout': textSummary(data, { indent: ' ', enableColors: true }),
        'load/results/extended-summary.json': JSON.stringify(data, null, 2),
    };
}

function textSummary(data, options) {
    // Simplified summary generation
    const indent = options.indent || '';
    const enableColors = options.enableColors || false;

    let summary = `\n${indent}Extended Load Test Summary:\n`;
    summary += `${indent}  Total Requests: ${data.metrics.total_requests?.values?.count || 0}\n`;
    summary += `${indent}  Failed Requests: ${data.metrics.http_req_failed?.values?.rate || 0}%\n`;
    summary += `${indent}  Avg Response Time: ${data.metrics.http_req_duration?.values?.avg || 0}ms\n`;
    summary += `${indent}  p95 Response Time: ${data.metrics.http_req_duration?.values['p(95)'] || 0}ms\n`;
    summary += `${indent}  p99 Response Time: ${data.metrics.http_req_duration?.values['p(99)'] || 0}ms\n`;

    return summary;
}
