---
status: wip
type: documentation
owner: unknown
module: development
redirect: false
moved_to: null
---

# DNA Migration Flags

- FLAG_DNA_DUAL_WRITE (default: false)
  - When true, new writes go to legacy + DNA.
- FLAG_DNA_READ_SHADOW (default: false)
  - When true, reads come from legacy, but DNA is also read and differences logged.
- FLAG_DNA_CUTOVER_READ_FROM (default: "legacy")  # values: legacy|dna
  - When set to dna, primary reads use DNA; legacy optionally used as fallback.
