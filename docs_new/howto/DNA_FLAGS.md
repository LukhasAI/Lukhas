---
title: Dna Flags
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["howto"]
facets:
  layer: ["gateway"]
  domain: ["symbolic"]
  audience: ["dev"]
---

# DNA Migration Flags

- FLAG_DNA_DUAL_WRITE (default: false)
  - When true, new writes go to legacy + DNA.
- FLAG_DNA_READ_SHADOW (default: false)
  - When true, reads come from legacy, but DNA is also read and differences logged.
- FLAG_DNA_CUTOVER_READ_FROM (default: "legacy")  # values: legacy|dna
  - When set to dna, primary reads use DNA; legacy optionally used as fallback.
