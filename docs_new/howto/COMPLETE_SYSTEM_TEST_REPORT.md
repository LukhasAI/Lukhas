---
title: Complete System Test Report
status: review
owner: docs-team
last_review: 2025-09-08
tags: ["consciousness", "testing", "howto"]
facets:
  layer: ["gateway"]
  domain: ["symbolic", "consciousness", "memory", "guardian"]
  audience: ["dev"]
---

# Complete Lukhas  + Lambda Products System Test Report

**Date:** 2025-08-07T00:34:18.441967

## Component Status

### Lukhas  Core
- **consciousness**: ❌ FAILED: No module named 'consciousness.unified.auto_consciousness'
- **memory**: ❌ FAILED: No module named 'memory.fold_manager'
- **guardian**: ❌ FAILED: cannot import name 'GuardianSystem' from 'governance.guardian' (/Users/agi_dev/LOCAL-REPOS/Lukhas/governance/guardian/__init__.py)
- **glyph**: ❌ FAILED: No module named 'core.glyph_engine'
- **plugin_registry**: ✅ PASSED

### Lambda Products
- **agents**: ✅ PASSED
- **nias**: ❌ FAILED: cannot import name 'NIASAgent' from 'agents.lambda_workforce_agents' (/Users/agi_dev/LOCAL-REPOS/Lukhas/lambda_products_pack/agents/lambda_workforce_agents.py)
- **abas**: ❌ FAILED: cannot import name 'ABASAgent' from 'agents.lambda_workforce_agents' (/Users/agi_dev/LOCAL-REPOS/Lukhas/lambda_products_pack/agents/lambda_workforce_agents.py)
- **dast**: ❌ FAILED: cannot import name 'DASTAgent' from 'agents.lambda_workforce_agents' (/Users/agi_dev/LOCAL-REPOS/Lukhas/lambda_products_pack/agents/lambda_workforce_agents.py)
- **auctor**: ❌ FAILED: cannot import name 'AuctorEngine' from 'auctor.auctor_content_engine' (/Users/agi_dev/LOCAL-REPOS/Lukhas/lambda_products_pack/auctor/auctor_content_engine.py)

### GPT-OSS Integration
- **openai_bridge**: ❌ FAILED: 'ADVANCED'
- **gpt_oss**: ✅ ENABLED

## Performance Metrics

- **plugin_throughput**: 73736 ops/sec
- **agent_throughput**: 120295 ops/sec
