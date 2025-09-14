# Jules-05 — Bio optimizer corrective actions

**Priority**: CRITICAL
**File**: `candidate/qi/bio/bio_optimizer.py`
**Line**: 631

## Goal
Map failed targets → concrete corrective actions; implement as strategy table + dispatcher.

## Requirements
- Strategy table mapping target types to actions
- Dispatcher function
- At least 3 target types with unit coverage

## Steps
1. **Analyze failure cases** around line 631 in `bio_optimizer.py`
2. **Identify target types** (examples):
   - `metabolic_drift`: Metabolic parameter deviation
   - `sensor_loss`: Sensor connectivity/data loss
   - `parameter_instability`: Parameter oscillation/instability
3. **Define strategy table**:
   ```python
   CORRECTIVE_STRATEGIES = {
       'metabolic_drift': [reset_metabolic_baseline, adjust_sensitivity],
       'sensor_loss': [switch_backup_sensor, interpolate_missing_data],
       'parameter_instability': [apply_smoothing_filter, reduce_gain]
   }
   ```
4. **Implement dispatcher**:
   ```python
   def handle_failed_target(target_type: str, context: dict) -> List[str]:
       """Apply corrective actions for failed optimization target."""
   ```
5. **Add action functions** as small, testable callables
6. **Write unit tests** for each target type and dispatcher logic

## Commands
```bash
# Test bio optimizer corrections
python -c "from candidate.qi.bio.bio_optimizer import handle_failed_target; print(handle_failed_target('metabolic_drift', {}))"
pytest -q tests/ -k bio_optimizer
```

## Acceptance Criteria
- [x] Strategy table implemented for 3+ target types ✅ COMPLETED
- [x] Dispatcher function handles target routing ✅ COMPLETED
- [x] Unit tests cover all target types ✅ COMPLETED (5 test cases)
- [x] Actions are idempotent and testable ✅ COMPLETED
- [x] Clear error handling for unknown targets ✅ COMPLETED

## ✅ STATUS: COMPLETED (2025-09-14)
**Completed By**: Claude Code
**PR**: #225 (auto-merge enabled)
**Result**: Full implementation with comprehensive test coverage

## Implementation Notes
- Keep actions small and focused
- Mock external systems in tests
- Add logging for corrective actions taken
- Consider action ordering/dependencies
- Document expected context parameters
