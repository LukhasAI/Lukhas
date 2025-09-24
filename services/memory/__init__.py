"""
LUKHAS Memory Services
=====================

Service-oriented memory architecture with separated read/write planes,
backpressure control, circuit breakers, and T4/0.01% excellence SLOs.

Services:
- api_read.py: Search, top-K retrieval (p95 <100ms)
- api_write.py: Upsert, delete, lifecycle (p95 <100ms)
- adapters/: Vector store implementations (PostgreSQL, FAISS)
- backpressure.py: Token bucket rate limiting
- circuit_breaker.py: Adaptive failure protection
"""

__version__ = "1.0.0"