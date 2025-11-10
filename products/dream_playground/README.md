# Dream Engine Interactive Playground

AI-Powered Dream Processing with Quantum-Inspired Consciousness Analysis

## Features

- **Real-time Dream Processing** - Process dreams with <2s latency
- **Tier Comparison** - Visual comparison of Tier 1, 2, and 3 features
- **Emotional Analysis** - D3.js visualization of emotional states
- **Quantum Coherence** - Gauge showing quantum coherence levels
- **Symbolic Pattern Network** - Interactive graph of dream symbols

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+ with LUKHAS API running on `localhost:8000`

### Development

```bash
cd products/dream_playground/frontend
npm install
npm run dev
```

Open http://localhost:5173

### Production Build

```bash
npm run build
npm run preview
```

### Docker Deployment

```bash
docker build -t lukhas-dream-playground .
docker run -p 3000:3000 lukhas-dream-playground
```

## Architecture

```
┌─────────────────┐
│  React Frontend │ ← Vite + TypeScript
└────────┬────────┘
         │ HTTP/WebSocket
┌────────┴────────┐
│   API Proxy     │ ← FastAPI proxy
└────────┬────────┘
         │
┌────────┴────────┐
│  LUKHAS API     │ ← localhost:8000/dream/*
└─────────────────┘
```

## API Integration

### Endpoints Used

- `POST /dream/process` - Process a dream
- `GET /dream/tiers` - Get tier comparison
- `WS /dream/stream` - Real-time processing updates

## Tech Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS
- **Charts**: D3.js + Recharts
- **WebSocket**: Socket.io
- **API**: FastAPI proxy to LUKHAS endpoints

## Deployment

Deploy to `playground.lukhas.ai`:

```bash
# Build production bundle
npm run build

# Deploy to Vercel
vercel --prod

# Or deploy to Cloudflare Pages
wrangler pages publish dist
```

## Marketing Angles

- "AI-Powered Dream Engine — Creativity Meets Consciousness"
- "Process Dreams Like Never Before"
- "Quantum-Inspired Consciousness API"

## Success Metrics

- **Target**: 1000+ dreams processed in first week
- **Latency**: <2s p95
- **Uptime**: 99.9%+
