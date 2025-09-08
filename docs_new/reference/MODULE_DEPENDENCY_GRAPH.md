---
title: Module Dependency Graph
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["consciousness", "api", "monitoring", "reference"]
facets:
  layer: ["orchestration"]
  domain: ["symbolic", "consciousness", "identity", "memory", "quantum"]
  audience: ["dev"]
---

# 🔗 LUKHAS Module Dependency Graph

## Core Dependencies

```mermaid
graph TD
    %% Core module - everything depends on it
    core["core/<br/>Foundation"]

    %% First tier - depend only on core
    config["config/<br/>Settings"]
    trace["trace/<br/>Monitoring"]

    %% Second tier - basic services
    memory["memory/<br/>Storage"]
    emotion["emotion/<br/>Affect"]
    ethics["ethics/<br/>Governance"]

    %% Third tier - complex services
    reasoning["reasoning/<br/>Logic"]
    learning["learning/<br/>Adaptation"]
    identity["identity/<br/>Auth"]

    %% Fourth tier - integrative services
    consciousness["consciousness/<br/>Awareness"]
    creativity["creativity/<br/>Expression"]
    quantum["quantum/<br/>Advanced"]

    %% Fifth tier - coordination
    orchestration["orchestration/<br/>Coordination"]
    bridge["bridge/<br/>External APIs"]

    %% Dependencies
    core --> config
    core --> trace
    core --> memory
    core --> emotion
    core --> ethics

    memory --> reasoning
    emotion --> reasoning
    core --> reasoning

    memory --> learning
    core --> learning

    core --> identity
    quantum --> identity

    core --> consciousness
    emotion --> consciousness
    quantum --> consciousness

    emotion --> creativity
    quantum --> creativity
    core --> creativity

    core --> quantum

    core --> orchestration
    reasoning --> orchestration
    consciousness --> orchestration

    core --> bridge
    memory --> bridge
    reasoning --> bridge
```

## Module Interaction Patterns

### 🎯 Hub Modules (Many Dependencies)
1. **core/** - Universal dependency
2. **memory/** - Data persistence hub
3. **emotion/** - Affect processing hub

### 🌐 Bridge Modules (Integration)
1. **bridge/** - External system integration
2. **orchestration/** - Internal coordination
3. **consciousness/** - High-level integration

### 🔒 Leaf Modules (Fewer Dependencies)
1. **trace/** - Monitoring only
2. **config/** - Configuration only
3. **narrative/** - Story generation

### 🔄 Circular Dependencies to Avoid
- consciousness ↔ reasoning
- emotion ↔ memory
- learning ↔ reasoning

## Module Criticality Matrix

| Module | Criticality | Dependencies | Dependents | Risk |
|--------|------------|--------------|------------|------|
| core | 🔴 Critical | 0 | All | Very High |
| memory | 🔴 Critical | 1 | 5+ | High |
| ethics | 🔴 Critical | 1 | 3+ | High |
| bridge | 🟠 Important | 3 | External | High |
| orchestration | 🟠 Important | 3 | Coordination | Medium |
| reasoning | 🟠 Important | 3 | 2+ | Medium |
| emotion | 🟠 Important | 1 | 3+ | Medium |
| consciousness | 🟡 Experimental | 3 | 1 | Medium |
| quantum | 🟡 Experimental | 1 | 3 | Low |
| creativity | 🟢 Optional | 3 | 0 | Low |
| trace | 🟢 Optional | 1 | 0 | Low |

## Startup Order

Based on dependencies, modules should initialize in this order:

1. **Phase 1**: Core Infrastructure
   - config/
   - core/
   - trace/

2. **Phase 2**: Basic Services
   - memory/
   - emotion/
   - ethics/

3. **Phase 3**: Advanced Services
   - reasoning/
   - learning/
   - identity/
   - quantum/

4. **Phase 4**: Integration
   - consciousness/
   - creativity/
   - bridge/

5. **Phase 5**: Coordination
   - orchestration/

## Communication Patterns

### Direct Module Communication
- memory → reasoning (facts)
- emotion → creativity (inspiration)
- ethics → reasoning (constraints)
- consciousness → orchestration (decisions)

### Event-Based Communication
- All modules → trace (logging)
- All modules → orchestration (events)
- bridge → All modules (external events)

### Shared State
- config/ (read-only by all)
- memory/ (read/write by authorized)
- identity/ (user context)
