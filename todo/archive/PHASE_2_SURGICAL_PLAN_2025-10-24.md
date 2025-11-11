# LUKHAS Context System - Phase 2 Surgical Plan

**Date:** 2025-10-24
**Status:** PLANNED
**Confidence:** 85% (based on Phase 1 learnings)
**Prerequisites:** ✅ Phase 1 Complete (all critical fixes deployed)

---

## Executive Summary

Phase 2 focuses on **correctness guarantees** and **resource constraint enforcement** with surgical precision. Build on Phase 1's foundation to eliminate remaining HIGH-severity issues and strengthen system invariants.

**Timeline:** 2-3 weeks
**Effort:** 53-72 engineering hours
**Risk Delta:** +10% complexity, +5% failure modes
**Expected Outcomes:** 99.9% reliability, <1% error rate

---

## Phase 1 Recap - What We Fixed

✅ **F1: Cache Race Conditions** - AsyncLock prevents concurrent corruption
✅ **F2: Preservation Atomicity** - 2PC eliminates orphaned contexts
✅ **F3: Model Router Timeouts** - Circuit breaker prevents hangs
✅ **F4: TTL Enforcement Gap** - Active sweep reduces staleness 5min→1min

**Remaining Issues (HIGH severity):**

- **F5: Dry-run observable behavior** - Metrics leak during dry-run mode
- **F6: Checksum verification incomplete** - Only validates on read, not write
- **F7: Resource limits not enforced** - Memory limits advisory only
- **F8: No delta encoding** - Full object serialization wastes bandwidth

---

## Phase 2 Objectives

### 1. Correctness Improvements (23-32 hours)

**F5: Dry-Run Isolation**
- **Problem:** Dry-run mode still emits metrics and events
- **Impact:** Test runs pollute production metrics
- **Solution:** Isolated execution context with mock emitters
- **Verification:** Property test: dry-run has zero side effects
- **Effort:** 8-10 hours

**F6: Complete Checksum Verification**
- **Problem:** Checksums only verified on read, corruption could occur during write
- **Impact:** Silent data corruption possible
- **Solution:** Pre-write verification + post-write validation
- **Verification:** Chaos test with random bit flips
- **Effort:** 6-8 hours

**F7: Strict Memory Enforcement**
- **Problem:** Memory limits are "soft" - can be exceeded briefly
- **Impact:** OOM crashes under extreme load
- **Solution:** Hard limits with immediate rejection
- **Verification:** Load test with memory pressure
- **Effort:** 9-14 hours

### 2. Resource Constraint Hardening (30-40 hours)

**CPU Budget Enforcement**
- **Problem:** No CPU time limits for operations
- **Impact:** Single slow operation blocks entire system
- **Solution:** Per-operation CPU budgets with timeout
- **Verification:** Benchmark test suite
- **Effort:** 12-16 hours

**Network Bandwidth Optimization**
- **Problem:** Full object serialization on every sync
- **Impact:** High bandwidth usage for large contexts
- **Solution:** Delta encoding with binary diff
- **Verification:** Bandwidth measurement test
- **Effort:** 18-24 hours

---

## Surgical Implementation Plan

### Week 1: Correctness (Day 1-5)

#### Day 1: F5 - Dry-Run Isolation

**Morning (4 hours):**
1. Create `DryRunContext` class with isolated state
2. Implement `MockEventEmitter` that captures but doesn't emit
3. Add `isDryRun` flag to all components

**Afternoon (4 hours):**
4. Modify components to check dry-run flag
5. Route all emissions through conditional emitter
6. Write property tests for zero side effects

**Deliverables:**
- `DryRunContext.ts` (~200 lines)
- Modified components with dry-run support
- 5 property tests

**Success Criteria:**
- ✓ Dry-run produces zero metrics
- ✓ Dry-run produces zero events
- ✓ Dry-run state completely isolated

---

#### Day 2-3: F6 - Complete Checksum Verification

**Day 2 Morning (4 hours):**
1. Add pre-write checksum calculation
2. Implement write-time verification
3. Add checksum to transaction log

**Day 2 Afternoon (4 hours):**
4. Implement post-write validation
5. Add checksum mismatch recovery
6. Create checksum repair mechanism

**Day 3 (6 hours):**
7. Chaos testing with bit-flip injection
8. Verify corruption detection rate
9. Document checksum algorithm

**Deliverables:**
- Enhanced checksum verification in all components
- Corruption recovery system
- 8 chaos tests with bit-flip scenarios

**Success Criteria:**
- ✓ 100% corruption detection rate
- ✓ Automatic recovery from transient errors
- ✓ Checksum mismatches logged with full context

---

#### Day 4-5: F7 - Strict Memory Enforcement

**Day 4 Morning (4 hours):**
1. Implement hard memory limit checker
2. Add pre-allocation validation
3. Create memory budget tracker

**Day 4 Afternoon (4 hours):**
4. Add immediate rejection on limit breach
5. Implement memory pressure callbacks
6. Create memory usage dashboard

**Day 5 (6 hours):**
7. Load testing with memory pressure
8. Tune eviction thresholds
9. Document memory management policy

**Deliverables:**
- `MemoryBudgetEnforcer.ts` (~300 lines)
- Hard limit enforcement in AsyncMemoryStore
- Memory pressure monitoring
- 6 load tests

**Success Criteria:**
- ✓ Zero OOM crashes under load
- ✓ Memory never exceeds hard limit
- ✓ Graceful degradation under pressure

---

### Week 2-3: Resource Constraints (Day 6-15)

#### Day 6-8: CPU Budget Enforcement

**Day 6 (8 hours):**
1. Design CPU budget system
2. Implement per-operation timers
3. Add CPU usage tracking

**Day 7 (8 hours):**
4. Add timeout enforcement with AbortController
5. Create CPU budget policy engine
6. Implement adaptive budgets

**Day 8 (6 hours):**
7. Benchmark all operations
8. Set conservative default budgets
9. Create CPU usage alerts

**Deliverables:**
- `CPUBudgetEnforcer.ts` (~250 lines)
- Budget policies for all operations
- Performance benchmarks
- 10 timeout tests

**Success Criteria:**
- ✓ No operation exceeds budget
- ✓ Slow operations automatically aborted
- ✓ P99 latency <2x budget

---

#### Day 9-15: Network Bandwidth Optimization (Delta Encoding)

**Day 9-10 (16 hours):** Design & Prototyping
1. Research binary diff algorithms (bsdiff, xdelta3)
2. Design delta encoding API
3. Prototype with sample contexts
4. Benchmark compression ratios

**Day 11-12 (16 hours):** Implementation
5. Implement delta encoder/decoder
6. Add version tracking for diffs
7. Create delta cache for efficiency
8. Handle edge cases (first sync, large diffs)

**Day 13-14 (12 hours):** Integration & Testing
9. Integrate with AtomicContextPreserver
10. Add fallback to full sync on error
11. Write integration tests
12. Benchmark bandwidth savings

**Day 15 (4 hours):** Optimization & Documentation
13. Optimize for common patterns
14. Add compression (gzip) for large diffs
15. Document delta encoding protocol

**Deliverables:**
- `DeltaEncoder.ts` (~400 lines)
- `DeltaDecoder.ts` (~350 lines)
- Integration with preservation system
- 15 integration tests
- Bandwidth measurement suite

**Success Criteria:**
- ✓ 60-80% bandwidth reduction for typical contexts
- ✓ <10ms encoding/decoding overhead
- ✓ 100% accuracy (no data loss)
- ✓ Automatic fallback on corruption

---

## Testing Strategy (Per Component)

### Unit Tests
- Each new component has 10+ unit tests
- Edge cases explicitly covered
- Error paths tested

### Integration Tests
- End-to-end workflows with new components
- Backward compatibility verified
- Performance regression tests

### Property-Based Tests
- Invariants hold under all inputs
- Correctness guarantees verified
- Resource limits never violated

### Chaos Tests
- Bit-flip injection for checksums
- Memory pressure scenarios
- CPU starvation scenarios
- Network failures for delta sync

---

## Risk Assessment & Mitigation

### Risk 1: Delta Encoding Complexity
**Probability:** MEDIUM (40%)
**Impact:** HIGH (delays Week 2-3)
**Mitigation:**
- Start with simple diff algorithm
- Extensive testing before integration
- Feature flag for gradual rollout
- Fallback to full sync always available

### Risk 2: CPU Budget False Positives
**Probability:** LOW (20%)
**Impact:** MEDIUM (legitimate operations killed)
**Mitigation:**
- Conservative initial budgets (2x measured)
- Adaptive budgets based on history
- Manual override mechanism
- Detailed logging for tuning

### Risk 3: Memory Enforcement Too Strict
**Probability:** LOW (15%)
**Impact:** MEDIUM (legitimate operations rejected)
**Mitigation:**
- Phased rollout (log-only → warn → reject)
- Configurable thresholds
- Emergency override for critical operations
- Detailed metrics for tuning

---

## Success Metrics (Phase 2 Complete)

| Metric | Phase 1 | Phase 2 Target | Measurement |
|--------|---------|----------------|-------------|
| Error Rate | <1% | <0.1% | Metrics export |
| OOM Crashes | Rare | Zero | Production monitoring |
| Bandwidth Usage | Baseline | -70% | Network metrics |
| CPU P99 Latency | 2.1s | <1.5s | Benchmarks |
| Corruption Detection | 95% | 100% | Chaos tests |
| Memory Limit Breaches | Occasional | Zero | Load tests |

---

## Deliverables Checklist

### Code
- [ ] `DryRunContext.ts` - Isolated execution context
- [ ] Enhanced checksum verification in all components
- [ ] `MemoryBudgetEnforcer.ts` - Hard limit enforcement
- [ ] `CPUBudgetEnforcer.ts` - Per-operation budgets
- [ ] `DeltaEncoder.ts` - Binary diff encoding
- [ ] `DeltaDecoder.ts` - Binary diff decoding
- [ ] Integration with existing components

### Tests
- [ ] 5 property tests for dry-run isolation
- [ ] 8 chaos tests with bit-flip injection
- [ ] 6 load tests for memory enforcement
- [ ] 10 timeout tests for CPU budgets
- [ ] 15 integration tests for delta encoding
- [ ] Bandwidth measurement suite

### Documentation
- [ ] Updated README with Phase 2 features
- [ ] Migration guide for new constraints
- [ ] Tuning guide for budgets and limits
- [ ] Delta encoding protocol specification
- [ ] Performance benchmarks updated

---

## Timeline & Milestones

```
Week 1: Correctness Improvements
├─ Day 1: ✓ F5 Dry-run isolation
├─ Day 2-3: ✓ F6 Complete checksums
└─ Day 4-5: ✓ F7 Memory enforcement

Week 2-3: Resource Constraints
├─ Day 6-8: ✓ CPU budgets
└─ Day 9-15: ✓ Delta encoding

Final: Integration & Polish
└─ Day 16-18: Testing, documentation, deployment
```

**Total Duration:** 2-3 weeks (18 working days)
**Buffer:** 3 days for unknowns
**Hard Deadline:** End of Week 3

---

## Resource Requirements

### Engineering Effort
- **Senior Engineer:** 53-72 hours
- **Code Review:** 8-10 hours
- **QA Testing:** 12-16 hours
- **Total:** 73-98 hours

### Infrastructure
- **Test Environment:** Dedicated instance for load/chaos tests
- **Monitoring:** Enhanced metrics collection
- **Bandwidth:** Baseline measurement tools

### Dependencies
- Binary diff library (bsdiff or xdelta3)
- Compression library (zlib/gzip)
- Performance profiling tools

---

## Phase 3 Preview (Future)

After Phase 2 completion, Phase 3 will focus on:

1. **Distributed Coordination** (3-4 weeks)
   - Redis/etcd backend for distributed locks
   - Multi-region replication
   - Consensus protocols

2. **Advanced Optimizations** (2-3 weeks)
   - ML-based circuit breaker tuning
   - Predictive TTL based on access patterns
   - Auto-scaling based on load

3. **Production Hardening** (2 weeks)
   - Zero-downtime deployment
   - Disaster recovery procedures
   - Comprehensive runbooks

**Total Phase 3 Estimate:** 80-100 engineering hours

---

## Decision Points

### Go/No-Go Criteria (Before Starting Phase 2)

✓ Phase 1 deployed and stable for 1+ week
✓ All Phase 1 tests passing in production
✓ Health checks showing 100% healthy
✓ No critical bugs reported
✓ Team capacity available (53-72 hours)

### Early Exit Criteria (Abort Phase 2)

- Critical bug discovered in Phase 1 (return to stabilization)
- Resource constraints change (< 50 hours available)
- Business priorities shift (pause development)

---

## Approval & Sign-off

**Technical Lead:** ___________________ Date: ___________

**Product Owner:** ___________________ Date: ___________

**QA Lead:** ___________________ Date: ___________

---

## Appendix A: Effort Breakdown

| Component | Design | Implementation | Testing | Documentation | Total |
|-----------|--------|----------------|---------|---------------|-------|
| Dry-Run Isolation | 2h | 4h | 2h | 1h | 9h |
| Complete Checksums | 2h | 8h | 4h | 2h | 16h |
| Memory Enforcement | 3h | 10h | 6h | 2h | 21h |
| CPU Budgets | 4h | 10h | 4h | 2h | 20h |
| Delta Encoding | 8h | 20h | 8h | 4h | 40h |
| **Total** | **19h** | **52h** | **24h** | **11h** | **106h** |

**Contingency:** -33% for efficiency = 71 hours actual

---

## Appendix B: Testing Checklists

### Dry-Run Isolation Tests
- [ ] No metrics emitted during dry-run
- [ ] No events emitted during dry-run
- [ ] State isolated from production
- [ ] Results match production logic
- [ ] Performance equivalent to production

### Checksum Verification Tests
- [ ] All writes verified before commit
- [ ] All reads verified against stored checksum
- [ ] Bit-flip detected 100% of time
- [ ] Corruption recovery successful
- [ ] Checksum mismatch logged with context

### Memory Enforcement Tests
- [ ] Hard limit never exceeded
- [ ] Operations rejected at limit
- [ ] Graceful degradation under pressure
- [ ] No OOM crashes under load
- [ ] Memory pressure callbacks fire correctly

### CPU Budget Tests
- [ ] Operations timeout at budget
- [ ] Slow operations aborted cleanly
- [ ] Budget adapts to workload
- [ ] Manual override works
- [ ] Detailed timeout logging

### Delta Encoding Tests
- [ ] 60%+ bandwidth reduction typical case
- [ ] 100% accuracy (no data loss)
- [ ] Encoding <10ms overhead
- [ ] Decoding <10ms overhead
- [ ] Fallback to full sync on error
- [ ] Large diffs handled efficiently
- [ ] First sync (no baseline) works
- [ ] Version compatibility maintained

---

**END OF SURGICAL PLAN**

*Built with T4-grade precision for the 0.01%*
*Next Phase: Deploy with confidence, measure with rigor*