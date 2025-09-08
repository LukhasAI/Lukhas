---
title: Openai Api Templates
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["api", "reference"]
facets:
  layer: ["orchestration"]
  domain: ["symbolic"]
  audience: ["dev"]
---

# OpenAI API Templates (v0.2 usage)
> Phrase in UI: **Built using OpenAI APIs**. No endorsement/partnership language.
3
## Text narration (streaming)
```bash
POST https://api.openai.com/v1/chat/completions
Authorization: Bearer $OPENAI_API_KEY
Content-Type: application/json

{
  "model": "gpt-4o-mini",
  "stream": true,
  "messages": [
    {"role":"system","content":"You write concise, cinematic-but-clear narration. No purple prose."},
    {"role":"user","content":"Seed: <user seed>. Current phase: <phase>. Awareness: <n> Coherence: <n>."}
  ]
}
```

## Image stills (snapshots)
```bash
POST https://api.openai.com/v1/images/generations
Authorization: Bearer $OPENAI_API_KEY
Content-Type: application/json

{
  "model": "gpt-image-1",
  "prompt": "Cloud theater, gentle volumetrics, minimal palette, focus at center. Web-safe composition.",
  "size": "1792x1024",
  "quality": "standard"
}
```

## Rate limiting & backoff
- Start 500ms → cap 30s; jitter ±15%.
- Queue non-blocking; render 2D baseline while awaiting responses.
