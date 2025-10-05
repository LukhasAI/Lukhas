---
module: {{module_fqn}}
type: api
title: {{module_title}} API Reference
status: {{status}}
---

> Source of truth: `module.manifest.json` → `apis` section.

### APIs
{{#each apis}}
#### {{name}}
- Module: `{{module_path}}`
- Import verified: {{import_verified}}
- Docs ≥80 chars: {{doc_ok}}
{{/each}}
