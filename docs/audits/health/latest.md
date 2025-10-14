# LUKHAS System Health Audit (auto-generated)

**Version:** `v0.9.0-rc-24-g8844e266b` | **Commit:** `8844e266`  
**Timestamp:** `2025-10-14T22:26:27Z`

## Summary

- **Ruff Total:** 5970 issues
- **Smoke Tests:** 70/74 passing (94.6%)
- **Unit Core Tests:** {'summary': '\nERROR tests/unit/bridge/adapters/test_gmail_adapter.py\nERROR tests/unit/bridge/adapters/test_oauth_manager.py\nERROR tests/unit/bridge/adapters/test_oauth_manager_advanced.py\nERROR tests/unit/bridge/api_gateway/test_unified_api_gateway.py\n!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!\n========================= 5 skipped, 5 errors in 0.56s ========================='}
- **OpenAPI:** {'valid': True, 'paths': 12}

## Ruff Statistics

```
  1782  W293
  1320  E402
   347  F841
   290  I001
   253  RUF100
   153  E712
   140  E722
   117  F541
   111  W292
    79  E702
    53  W291
    50  E701
    38  E741
    38  F401
    21  F821
    18  F811
    11  F402
    10  F706
     8  F405
     6  E401
     6  F403
     6  F823
     4  E731
     2  E721
     2  E902
     2  F404
     1  F822
```

## Test Results

###  Smoke Tests

- **Status:** 70/74 passing (94.6%)
- **Passed:** 70
- **Failed:** 4

### Core Unit Tests

```

ERROR tests/unit/bridge/adapters/test_gmail_adapter.py
ERROR tests/unit/bridge/adapters/test_oauth_manager.py
ERROR tests/unit/bridge/adapters/test_oauth_manager_advanced.py
ERROR tests/unit/bridge/api_gateway/test_unified_api_gateway.py
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 5 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
========================= 5 skipped, 5 errors in 0.56s =========================
```

## Compat Hits

[report_compat_hits] Total compat alias hits: 0
[report_compat_hits] ✅ PASS: 0 hits within limit 999999

## Guardian & Rate Limiter Status

⚪ **API not running** - Start API to get live Guardian/RL stats

---
*Generated: 2025-10-14T22:26:27Z*