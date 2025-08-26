# LUKHAS AI Tool Execution System 🛠️

> **Phase 2 Core Implementation**: Safe Web Scraping & Sandboxed Execution with Multi-AI Orchestration

A comprehensive, secure, and highly performant tool execution system designed for the LUKHAS AI ecosystem. This system provides safe web scraping, sandboxed code execution, multi-AI consensus, Guardian ethical validation, and enterprise-grade monitoring.

## 🏗️ Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Tool Orchestrator                        │
│  • Multi-AI Consensus  • Guardian Integration              │
│  • Performance Monitor • External Service Integration      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  Tool Executor                              │
│  • Safe Web Scraping  • Sandboxed Code Execution          │
│  • Rate Limiting      • Comprehensive Security             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Guardian System Integration                    │
│  • Ethical Validation  • Security Checks                  │
│  • Audit Logging      • Decision Learning                 │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **🔒 Security First**: Comprehensive input validation, sandboxed execution, rate limiting
- **🛡️ Guardian Integration**: Ethical validation and consent management
- **🌐 Safe Web Scraping**: Domain allowlisting, content filtering, size limits
- **🐳 Docker Sandboxing**: Isolated code execution with resource constraints
- **🤖 Multi-AI Orchestration**: Consensus mechanisms across OpenAI, Anthropic, Gemini
- **📊 Performance Monitoring**: Real-time metrics, alerting, optimization
- **🔌 External Services**: Gmail, Dropbox, Google Drive integration
- **✅ Comprehensive Testing**: 95%+ test coverage with integration tests

## 🚀 Quick Start

### Installation

```bash
# Install additional dependencies
pip install -r candidate/tools/requirements-tools.txt

# Ensure Docker is installed and running
docker --version
```

### Environment Configuration

```bash
# Required environment variables
export LUKHAS_ENABLE_BROWSER=true
export LUKHAS_ENABLE_CODE_EXEC=true
export LUKHAS_MAX_CONCURRENT_EXECUTIONS=10
export LUKHAS_MAX_CONTENT_SIZE=1048576  # 1MB

# Optional security configuration
export LUKHAS_RATE_LIMIT_REQUESTS=10
export LUKHAS_RATE_LIMIT_WINDOW=60
export LUKHAS_REQUEST_TIMEOUT=30
```

### Basic Usage

```python
from candidate.tools.tool_orchestrator import get_tool_orchestrator

# Initialize orchestrator
orchestrator = get_tool_orchestrator({
    "enable_consensus": True,
    "consensus_threshold": 0.7
})

# Execute tool with full orchestration
result = await orchestrator.execute_with_orchestration(
    tool_name="open_url",
    arguments='{"url": "https://httpbin.org/get"}',
    user_context={"lid": "user123", "credentials": {}}
)

print(f"Success: {result['success']}")
print(f"Guardian Approved: {result['guardian_validation']['approved']}")
print(f"Execution Time: {result['execution_time']:.2f}s")
```

## 🛠️ Tool Categories

### Web Scraping Tools
- **`open_url`**: Safe web scraping with security validation
- Domain allowlisting and content filtering
- Size limits and timeout protection
- BeautifulSoup-based content extraction

### Code Execution Tools
- **`exec_code`**: Sandboxed code execution (Python, JavaScript, Bash)
- Docker-based isolation with resource limits
- Security pattern detection and blocking
- Comprehensive output handling

### Knowledge & Scheduling
- **`retrieve_knowledge`**: Knowledge base queries
- **`schedule_task`**: Task scheduling with persistence

### External Services
- **Gmail**: `gmail_send`, `gmail_list`, `gmail_read`
- **Dropbox**: `dropbox_upload`, `dropbox_download`, `dropbox_list`
- **Google Drive**: `drive_upload`, `drive_download`, `drive_list`, `drive_share`

## 🔐 Security Architecture

### Multi-Layer Security

1. **Input Validation**
   - URL scheme and domain validation
   - Code pattern security scanning
   - Argument sanitization

2. **Sandboxed Execution**
   - Docker container isolation
   - Network access disabled
   - Read-only filesystem
   - Resource constraints (CPU, memory, time)

3. **Rate Limiting**
   - Per-user request limits
   - Configurable time windows
   - Graceful degradation

4. **Guardian Integration**
   - Ethical validation pipeline
   - Consent verification
   - Audit trail logging

### Security Configuration

```python
security_config = {
    "allowed_domains": ["github.com", "stackoverflow.com"],
    "blocked_patterns": ["javascript:", "data:", "file://"],
    "max_content_size": 1048576,  # 1MB
    "request_timeout": 30,
    "rate_limit_requests": 10,
    "rate_limit_window": 60
}
```

## 🤖 Multi-AI Orchestration

### Consensus Mechanism

The system supports consensus validation across multiple AI services:

```python
# AI Services Integration
ai_clients = {
    "openai": UnifiedOpenAIClient(),
    "anthropic": AnthropicWrapper(),
    "gemini": GeminiWrapper(),
    "perplexity": PerplexityWrapper()
}

# Consensus evaluation
consensus = await get_consensus(
    tool_name="open_url",
    arguments={"url": "https://example.com"},
    execution_result="scraped content..."
)

print(f"Consensus reached: {consensus['consensus_reached']}")
print(f"Overall score: {consensus['overall_score']:.2f}")
print(f"Participating services: {consensus['participating_services']}")
```

### Performance Targets

- **Tool Execution Latency**: <2000ms for most operations
- **Consensus Evaluation**: <30s for multi-AI validation
- **Guardian Validation**: <250ms ethical checks
- **API Response Time**: <100ms p95
- **Concurrent Executions**: 10+ parallel operations

## 📊 Performance Monitoring

### Real-time Metrics

```python
from candidate.tools.performance_monitor import get_performance_monitor

# Start monitoring
monitor = get_performance_monitor({
    "collection_interval": 1.0,
    "analysis_interval": 30
})

await monitor.start_monitoring()

# Get current status
status = monitor.get_current_status()
print(f"Health Score: {status['health_score']:.2f}")
print(f"Active Alerts: {status['active_alerts']}")

# Export performance report
report_path = await monitor.export_performance_report(time_range=3600)
```

### Monitored Metrics

- **System**: CPU, memory, disk I/O, network
- **Tool Execution**: Latency, throughput, error rates
- **Security**: Blocked requests, Guardian denials
- **External Services**: Authentication success, API response times

## 🧪 Testing

### Run Comprehensive Tests

```bash
# Run all tool execution tests
pytest tests/tools/test_tool_executor_comprehensive.py -v

# Run with coverage
pytest tests/tools/ --cov=candidate.tools --cov-report=html

# Run specific test categories
pytest tests/tools/ -m "security"
pytest tests/tools/ -m "performance"
pytest tests/tools/ -m "integration"
```

### Test Categories

- **Unit Tests**: Core functionality validation
- **Security Tests**: Vulnerability and penetration testing
- **Integration Tests**: End-to-end workflow validation
- **Performance Tests**: Load testing and optimization
- **Guardian Tests**: Ethical validation pipeline

## 📈 Performance Optimization

### Optimization Features

1. **Caching**: Result caching with TTL management
2. **Connection Pooling**: HTTP connection reuse
3. **Resource Limits**: Prevent resource exhaustion
4. **Async Execution**: Non-blocking operations
5. **Smart Retries**: Exponential backoff with circuit breaking

### Optimization Recommendations

The system automatically generates optimization recommendations:

```python
recommendations = optimizer.generate_recommendations(metrics)
for rec in recommendations:
    print(f"[{rec['priority'].upper()}] {rec['recommendation']}")
```

Example outputs:
- `[HIGH] Consider reducing concurrent operations or optimizing CPU-intensive tasks`
- `[MEDIUM] Implement memory management strategies, clear caches`
- `[HIGH] Investigate error causes, improve error handling`

## 🔧 Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LUKHAS_ENABLE_BROWSER` | `false` | Enable web scraping |
| `LUKHAS_ENABLE_CODE_EXEC` | `false` | Enable code execution |
| `LUKHAS_ENABLE_RETRIEVAL` | `true` | Enable knowledge retrieval |
| `LUKHAS_ENABLE_SCHEDULER` | `true` | Enable task scheduling |
| `LUKHAS_MAX_CONCURRENT_EXECUTIONS` | `10` | Max parallel executions |
| `LUKHAS_MAX_CONTENT_SIZE` | `1048576` | Max content size (bytes) |
| `LUKHAS_REQUEST_TIMEOUT` | `30` | Request timeout (seconds) |
| `LUKHAS_RATE_LIMIT_REQUESTS` | `10` | Rate limit requests |
| `LUKHAS_RATE_LIMIT_WINDOW` | `60` | Rate limit window (seconds) |

### Configuration Files

```python
# Tool executor configuration
tool_config = {
    "allowed_domains": ["example.com", "httpbin.org"],
    "max_content_size": 1048576,
    "request_timeout": 30
}

# Orchestrator configuration
orchestrator_config = {
    "enable_consensus": True,
    "consensus_threshold": 0.7,
    "max_execution_time": 300,
    "cache_ttl": 3600
}

# Performance monitoring configuration
monitor_config = {
    "collection_interval": 1.0,
    "analysis_interval": 30,
    "export_directory": "data/performance"
}
```

## 🚨 Error Handling

### Error Categories

1. **Security Violations**: Blocked by security policies
2. **Rate Limiting**: Request limits exceeded
3. **Resource Exhaustion**: System resource limits
4. **Guardian Denials**: Ethical validation failures
5. **Service Unavailability**: External service issues

### Error Response Format

```python
{
    "success": false,
    "error": "security_violation",
    "details": {
        "reason": "url_blocked",
        "blocked_domain": "malicious.com"
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "execution_id": "exec_abc123"
}
```

## 🔗 Integration Points

### Guardian System
- Pre-execution ethical validation
- Post-execution audit logging
- Decision learning and adaptation

### External Services
- OAuth2 authentication flows
- Capability token validation
- Service-specific adapters

### Multi-AI Services
- Consensus evaluation protocols
- Service health monitoring
- Failover mechanisms

## 📚 API Reference

### Core Classes

- **`ToolExecutor`**: Core tool execution engine
- **`ToolOrchestrator`**: Multi-AI orchestration layer
- **`ToolExecutorGuardian`**: Guardian integration
- **`ExternalServiceIntegration`**: External service adapters
- **`PerformanceMonitor`**: Performance monitoring system

### Key Methods

```python
# Execute with full orchestration
result = await orchestrator.execute_with_orchestration(tool_name, args, context)

# Validate with Guardian
validation = await guardian.validate_tool_execution(tool, args, context)

# Execute external service operation
service_result = await integration.execute_service_operation(op, args, context)

# Monitor performance
await monitor.start_monitoring()
```

## 🛣️ Roadmap

### Upcoming Features

- [ ] **Advanced Consensus**: Weighted voting, expertise domains
- [ ] **Enhanced Sandboxing**: GPU support, additional languages
- [ ] **AI-Powered Optimization**: ML-based performance tuning
- [ ] **Distributed Execution**: Multi-node tool execution
- [ ] **Advanced Security**: Zero-trust architecture, HSM integration

### Performance Targets

- [ ] Sub-100ms Guardian validation
- [ ] 99.9% uptime for critical tools
- [ ] Auto-scaling based on demand
- [ ] Real-time threat detection

## 🤝 Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r candidate/tools/requirements-tools.txt
pip install -r requirements-test.txt

# Run pre-commit hooks
pre-commit install

# Run tests
make test-tools
```

### Code Quality Standards

- **Test Coverage**: Minimum 85%, target 95%
- **Security**: All security patterns must be tested
- **Performance**: Sub-2s execution for standard operations
- **Documentation**: Comprehensive docstrings and examples

---

**Built with Trinity Framework principles: ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian**

*LUKHAS AI Tool Execution System - Enterprise-grade tool orchestration for safe, ethical, and performant AI operations.*