# Headers Comparison Report
**Date**: 2025-10-16T04:55:25.497800Z
**Endpoint**: /v1/chat/completions

## Rate-Limit Headers Parity

### ❌ `x-ratelimit-limit`
- **Lukhas**: `MISSING`
- **OpenAI**: `MISSING`
- **Present in Both**: False

### ❌ `x-ratelimit-remaining`
- **Lukhas**: `MISSING`
- **OpenAI**: `MISSING`
- **Present in Both**: False

### ❌ `x-ratelimit-reset`
- **Lukhas**: `MISSING`
- **OpenAI**: `MISSING`
- **Present in Both**: False

### ✅ `x-ratelimit-limit-requests`
- **Lukhas**: `40`
- **OpenAI**: `10000`
- **Present in Both**: True

### ✅ `x-ratelimit-remaining-requests`
- **Lukhas**: `39`
- **OpenAI**: `9999`
- **Present in Both**: True

### ✅ `x-ratelimit-reset-requests`
- **Lukhas**: `0.049`
- **OpenAI**: `8.64s`
- **Present in Both**: True

### ❌ `x-trace-id`
- **Lukhas**: `a2e508123b0b47169f99779fb96deb94`
- **OpenAI**: `MISSING`
- **Present in Both**: False

### ❌ `x-service-version`
- **Lukhas**: `dev`
- **OpenAI**: `MISSING`
- **Present in Both**: False

