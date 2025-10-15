# LUKHAS Python SDK Examples

**OpenAI-Compatible Python Client for LUKHAS AI**

Production-ready Python examples for integrating with the LUKHAS API using modern Python patterns, type hints, and async support.

## 📦 Quick Start

```bash
pip install -r requirements.txt
python src/basic_client.py
python src/streaming_client.py
python src/search_client.py
python src/dreams_client.py
```

## 🎯 Examples

### 1. Basic Response Generation (`basic_client.py`)
- Synchronous and async response creation
- Type-safe requests with Pydantic models
- Automatic trace ID extraction
- OpenAI-compatible error handling

### 2. Streaming SSE (`streaming_client.py`)
- Server-Sent Events streaming
- Real-time token processing
- Async/await patterns
- Connection management with httpx

### 3. Index Search (`search_client.py`)
- Vector similarity search
- Semantic query processing
- Result filtering and ranking
- Pagination support

### 4. Dreams API (`dreams_client.py`)
- Scenario simulation
- Multi-path exploration
- Consciousness-aware processing
- Path ranking and insights

## 🔧 Configuration

Set environment variables:

```bash
export LUKHAS_API_KEY="sk-lukhas-your-key-here"
export LUKHAS_BASE_URL="https://api.lukhas.ai"  # or http://localhost:8000
```

Or create `.env` file:

```
LUKHAS_API_KEY=sk-lukhas-your-key-here
LUKHAS_BASE_URL=http://localhost:8000
```

## 📚 API Reference

See [LUKHAS API Documentation](../../../docs/api/README.md) for complete API reference.

## 🚀 Usage

All examples support both sync and async patterns:

```python
# Synchronous
from lukhas_client import LukhasClient

client = LukhasClient(api_key="sk-lukhas-...")
response = client.create_response(prompt="Hello", max_tokens=100)

# Asynchronous
import asyncio
from lukhas_client import AsyncLukhasClient

async def main():
    client = AsyncLukhasClient(api_key="sk-lukhas-...")
    response = await client.create_response(prompt="Hello", max_tokens=100)

asyncio.run(main())
```
