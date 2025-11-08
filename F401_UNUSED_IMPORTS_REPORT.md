# F401 Unused Imports Report

**Generated**: 2025-11-08  
**Total Errors**: 781  
**Excluded**: Lukhas-auto-1046 submodule

## Summary by Category

| Category | Count | Recommendation |
|----------|-------|----------------|
| functions | 754 | ✅ LIKELY SAFE - But check for side effects first |
| classes | 13 | ⚠️ REVIEW - May be used for type hints or side effects |
| test_utilities | 11 | ⚠️ REVIEW - May be pytest fixtures or used by conftest |
| logging | 3 | ✅ SAFE TO REMOVE - Unused logger imports |

## Top 20 Most Common Unused Imports

| Import Name | Occurrences | Category |
|------------|-------------|----------|
| `unknown` | 302 | functions |
| `typing.Tuple` | 16 | functions |
| `typing.List` | 7 | functions |
| `cryptography.hazmat.primitives.hashes` | 5 | functions |
| `adapters` | 4 | functions |
| `core_ΛBot.SubscriptionTier` | 4 | functions |
| `collections` | 4 | functions |
| `branding_bridge.normalize_output_text` | 3 | functions |
| `branding_bridge.validate_output` | 3 | functions |
| `cryptography.hazmat.primitives.serialization` | 3 | functions |
| `cryptography.hazmat.primitives.asymmetric.padding` | 3 | functions |
| `cryptography.hazmat.primitives.asymmetric.rsa` | 3 | functions |
| `opentelemetry.semconv.trace.SpanAttributes` | 3 | functions |
| `TODO` | 2 | classes |
| `CLAUDE_ARMY` | 2 | classes |
| `SYSTEM_CLAUDE_AUDIT` | 2 | classes |
| `agent` | 2 | functions |
| `agents` | 2 | functions |
| `agents_external` | 2 | functions |
| `ai_orchestration` | 2 | functions |


## Sample Files by Category


### Classes (13 files)

- `/Users/agi_dev/LOCAL-REPOS/Lukhas/TODO/tests/test_TODO_integration.py:18` - `TODO`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/TODO/tests/test_TODO_unit.py:18` - `TODO`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_cli.py:457` - `ΛiD.identity_manager.Identitymanager`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_abot_cli.py:466` - `ΛiD.trauma_lock.TraumaLockSystem`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/branding/engines/lukhas_content_platform/bots/lambda_bot_enterprise_multi_brain_symphony_lambda_bot.py:36` - `MultiBrainSymphony.BrainRegion`
- ... and 8 more

### Functions (754 files)

- `/Users/agi_dev/LOCAL-REPOS/Lukhas/adapters/tests/test_adapters_integration.py:18` - `adapters`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/adapters/tests/test_adapters_unit.py:18` - `adapters`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/agent/tests/test_agent_integration.py:18` - `agent`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/agent/tests/test_agent_unit.py:18` - `agent`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/agents/tests/test_agents_integration.py:18` - `agents`
- ... and 749 more

### Logging (3 files)

- `/Users/agi_dev/LOCAL-REPOS/Lukhas/tools/extreme_performance_validator.py:45` - `governance.identity.auth_backend.extreme_performance_audit_logger.run_audit_benchmark_extreme`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/trace_logs/tests/test_trace_logs_integration.py:18` - `trace_logs`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/trace_logs/tests/test_trace_logs_unit.py:18` - `trace_logs`

### Test Utilities (11 files)

- `/Users/agi_dev/LOCAL-REPOS/Lukhas/bridge/api/test_orchestration_system.py:30` - `pytest`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas_website/lukhas/api/identity.py:34` - `..identity.biometrics.BiometricAttestation`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas_website/lukhas/observability/prometheus_metrics.py:24` - `prometheus_client.CONTENT_TYPE_LATEST`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/pytest_asyncio_stub_DISABLED/tests/test_pytest_asyncio_integration.py:18` - `pytest_asyncio`
- `/Users/agi_dev/LOCAL-REPOS/Lukhas/pytest_asyncio_stub_DISABLED/tests/test_pytest_asyncio_unit.py:18` - `pytest_asyncio`
- ... and 6 more


## Recommendations for GPT-5 Review

1. **Start with logging & type_checking categories** - These are safest to remove (16 files)
2. **Review functions category carefully** - Largest group (754), check for side-effect imports
3. **Be cautious with classes** - May be used in type hints or have side effects
4. **Manually review star_imports** - These may be intentional re-exports

## Next Steps

```bash
# Remove safe categories (logging, type_checking)
# Run tests after each batch removal to ensure no breakage
make test

# For functions category, use script to check actual usage:
python3 tools/check_import_usage.py <import_name>
```

