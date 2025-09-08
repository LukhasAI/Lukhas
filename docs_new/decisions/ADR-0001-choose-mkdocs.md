---
title: ADR-0001 Choose MkDocs for docs-as-code
date: 2025-09-01
status: accepted
tags: [adr, docs]
---

## Context
We need a lightweight, versioned, searchable doc system.

## Decision
Use MkDocs + mkdocs-material + mkdocstrings.

## Consequences
- Easy local preview.
- CI-friendly.
- Markdown everywhere.