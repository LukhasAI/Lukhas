# LUKHAS TypeScript SDK Examples

**OpenAI-Compatible TypeScript Client for LUKHAS AI**

This directory contains production-ready TypeScript examples for integrating with the LUKHAS API using modern TypeScript patterns, type safety, and best practices.

## 📦 Quick Start

```bash
npm install
npm run example:basic
npm run example:streaming
npm run example:search
```

## 🎯 Examples

### 1. Basic Response Generation (`basic-client.ts`)
- Create responses with `client.createResponse()`
- Handle authentication and tracing
- Type-safe request/response handling
- Error handling with OpenAI-compatible format

### 2. Streaming SSE (`streaming-client.ts`)
- Server-Sent Events (SSE) streaming
- Real-time token streaming
- Automatic trace ID extraction
- Connection management

### 3. Index Search (`search-client.ts`)
- Vector search with `client.searchIndex()`
- Semantic similarity search
- Result filtering and ranking
- Pagination support

### 4. Dreams API (`dreams-client.ts`)
- Scenario simulation with `client.createDream()`
- Multi-path exploration
- Consciousness-aware processing

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
