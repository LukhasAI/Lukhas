# Context Sync Headers (Schema v2.0.0)

## 1. ROOT: claude.me + lukhas_context.md
```
> Context Sync Header (Schema v2.0.0)
Lane: production
Lane root: lukhas
Canonical imports: lukhas.*
Cognitive components (global): 692
Flags: ENFORCE_ETHICS_DSL, LUKHAS_LANE, LUKHAS_ADVANCED_TAGS
Legacy core alias: enabled (warn/disable via env) — use lukhas.core.*
```

## 2. LUKHAS: lukhas/claude.me + lukhas/lukhas_context.md
```
> Context Sync Header (Schema v2.0.0)
Lane: production
Lane root: lukhas
Canonical imports: lukhas.*
Cognitive components (global): 692
Flags: ENFORCE_ETHICS_DSL, LUKHAS_LANE, LUKHAS_ADVANCED_TAGS
Legacy core alias: enabled (warn/disable via env) — use lukhas.core.*
```

## 3. CANDIDATE: candidate/claude.me + candidate/lukhas_context.md
```
> Context Sync Header (Schema v2.0.0)
Lane: development
Lane root: candidate
Canonical imports: lukhas.* (candidate only in dev)
Cognitive components (global): 692
Flags: ENFORCE_ETHICS_DSL, LUKHAS_LANE, LUKHAS_ADVANCED_TAGS
Legacy core alias: enabled (warn/disable via env) — use lukhas.core.*
```

## 4. CANDIDATE/CORE: candidate/core/claude.me + candidate/core/lukhas_context.md
```
> Context Sync Header (Schema v2.0.0)
Lane: integration
Lane root: candidate/core
Canonical imports: lukhas.* (candidate/core only in integration)
Cognitive components (global): 692
Flags: ENFORCE_ETHICS_DSL, LUKHAS_LANE, LUKHAS_ADVANCED_TAGS
Legacy core alias: enabled (warn/disable via env) — use lukhas.core.*
```