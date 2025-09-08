---
title: Symbolic Mesh Router
status: draft
owner: core-arch
last_review: 2025-09-01
tags: [architecture, routing, eqnox]
facets:
  layer: [orchestration]
  domain: [symbolic, identity]
  audience: [dev, researcher]
---

Diagram (Mermaid):

```mermaid
flowchart LR
  A[Module A] -- glyph --> R[Mesh Router]
  R -- attract/repel --> B[Module B]
```