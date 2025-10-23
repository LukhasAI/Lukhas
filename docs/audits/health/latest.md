# LUKHAS System Health Audit (auto-generated)

**Version:** `audit-2025-10-22T210824Z-2-g5f432276a` | **Commit:** `5f432276`  
**Timestamp:** `2025-10-22T21:58:05Z`

## Summary

- **Ruff Total:** 4809 issues
- **Smoke Tests:** 0/0 passing (0.0%)
- **Unit Core Tests:** None
- **OpenAPI:** {'valid': True, 'paths': 12}

## Ruff Statistics

```
  1112  E402
   775  W293
   432  I001
   197  RUF100
   172  F841
   153  E712
   140  E722
   131  F541
   111  W292
    79  E702
    73  F821
    54  W291
    51  E701
    49  F401
    42  Q000
    38  E741
    17  F811
    13  F706
    11  F402
     9  F405
     8  E401
     6  F823
     5  F403
     4  E731
     3  E902
     2  E721
     2  F404
     2  F704
     1  B009
     1  SIM117
     1  F822
```

## Test Results

###  Smoke Tests

- **Status:** {'summary': 'ERROR tests/smoke/test_openai_facade.py\nERROR tests/smoke/test_rate_limit_headers.py\nERROR tests/smoke/test_rate_limiting.py\nERROR tests/smoke/test_responses.py\nERROR tests/smoke/test_responses_stream.py\nERROR tests/smoke/test_security_headers.py\nERROR tests/smoke/test_trace_header.py\nERROR tests/smoke/test_tracing.py\n!!!!!!!!!!!!!!!!!!! Interrupted: 23 errors during collection !!!!!!!!!!!!!!!!!!!'}

### Core Unit Tests

- **Status:** {}

## Compat Hits

[report_compat_hits] Total compat alias hits: 0
[report_compat_hits] ✅ PASS: 0 hits within limit 999999

## Guardian & Rate Limiter Status

⚪ **API not running** - Start API to get live Guardian/RL stats

---
*Generated: 2025-10-22T21:58:05Z*