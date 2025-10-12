# Load Testing with k6

This directory contains k6 load test scenarios for the LUKHAS API.

## Installation

### macOS
```bash
brew install k6
```

### Linux
```bash
# Debian/Ubuntu
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### Docker
```bash
docker pull grafana/k6:latest
```

## Test Scenarios

### Smoke Test (Quick Validation)
**Duration**: 30s  
**VUs**: 5  
**Purpose**: Quick sanity check, verify basic functionality
```bash
make load-smoke
# OR
k6 run load/smoke.js
```

### Standard Load Test (Sustained Traffic)
**Duration**: 2m  
**VUs**: 50  
**Purpose**: Sustained load testing for performance validation
```bash
make load-test
# OR
k6 run load/resp_scenario.js
```

### Extended Load Test (Stress Testing)
**Duration**: 10m  
**VUs**: 100  
**Purpose**: Long-running stress test, identify memory leaks and degradation
```bash
make load-extended
# OR
k6 run load/extended.js
```

### Spike Test (Traffic Bursts)
**Duration**: 5m  
**VUs**: 0 → 200 → 0  
**Purpose**: Test system behavior under sudden traffic spikes
```bash
make load-spike
# OR
k6 run load/spike.js
```

## CI Integration

Load tests run nightly via `.github/workflows/matriz-nightly.yml`:
- **Smoke test**: Runs on every nightly build (30s)
- **Extended test**: Optional, runs on schedule or manual trigger

## Metrics & Thresholds

All tests check:
- **http_req_duration**: p95 < 500ms (consciousness stream latency SLO)
- **http_req_failed**: < 1% (error rate)
- **checks**: 99% passing

## Custom Configuration

Edit scenarios to test specific endpoints:
- `/v1/responses` - Standard response generation
- `/v1/chat/completions` - OpenAI-compatible chat
- `/v1/embeddings` - Vector embeddings
- `/v1/indexes` - Memory index management

## Analyzing Results

k6 provides detailed metrics:
```
checks........................: 99.50% ✓ 4975      ✗ 25   
data_received..................: 1.2 MB 10 kB/s
data_sent......................: 890 kB 7.4 kB/s
http_req_blocked...............: avg=1.23ms   min=2µs     med=5µs     max=123ms  p(95)=3.45ms  
http_req_connecting............: avg=543µs    min=0s      med=0s      max=54ms   p(95)=1.23ms  
http_req_duration..............: avg=234ms    min=45ms    med=198ms   max=987ms  p(95)=456ms   
  { expected_response:true }...: avg=234ms    min=45ms    med=198ms   max=987ms  p(95)=456ms   
http_req_failed................: 0.50%  ✓ 25        ✗ 4975
http_req_receiving.............: avg=234µs    min=23µs    med=234µs   max=2.34ms p(95)=567µs   
http_req_sending...............: avg=123µs    min=12µs    med=123µs   max=1.23ms p(95)=234µs   
http_req_tls_handshaking.......: avg=0s       min=0s      med=0s      max=0s     p(95)=0s      
http_req_waiting...............: avg=234ms    min=45ms    med=198ms   max=987ms  p(95)=456ms   
http_reqs......................: 5000   41.666667/s
iteration_duration.............: avg=1.2s     min=1s      med=1.2s    max=2.1s   p(95)=1.5s    
iterations.....................: 5000   41.666667/s
vus............................: 50     min=50      max=50 
vus_max........................: 50     min=50      max=50 
```

## Troubleshooting

### Connection Refused
Ensure LUKHAS server is running:
```bash
python main.py --dev-mode
# OR
make dev
```

### High Latency
Check system resources:
```bash
make health-check
# OR
python tools/analysis/PWM_OPERATIONAL_SUMMARY.py
```

### Failed Checks
Review application logs:
```bash
tail -f logs/lukhas.log
```

## Locust Alternative

For Python-based load testing, see `load/locustfile.py`:
```bash
locust -f load/locustfile.py --host=http://localhost:8000
```

Open http://localhost:8089 to configure test parameters via web UI.
