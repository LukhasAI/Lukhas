# Code Quality Auto-Fix Workflow

When Claude Code detects code quality issues:

## Constellation Framework Auto-Documentation
For any function missing Trinity documentation:

```python
# BEFORE (detected issue):
def process_data(data):
    return processed_data

# AFTER (Claude Code auto-fix):
def process_consciousness_data(data: ConsciousData) -> ConsciousResponse:
    """
    🎭 Processes consciousness data with bio-inspired flow patterns
    🌈 Transforms raw data into consciousness-aware structures for system harmony
    🎓 Technical: Async processing with Trinity validation and Λ-trace integration
    """
    λ_trace = start_audit_trace(data.λid)

    try:
        # Consciousness validation
        consciousness_state = await validate_consciousness_alignment(data)
        if not consciousness_state.valid:
            return consciousness_error("Trinity alignment required", λ_trace)

        # Core processing with bio-inspired patterns
        result = await bio_inspired_processing(data, consciousness_state)

        # Λ-trace completion
        await λ_trace.complete(result)

        return ConsciousResponse(result, consciousness_metadata=consciousness_state)

    except Exception as e:
        await λ_trace.error(e)
        return consciousness_error(str(e), λ_trace)
```

## Symbolic Vocabulary Auto-Correction
Auto-replace generic terms with consciousness vocabulary:
- `process` → `consciousness_process` or `quantum_process`
- `data` → `consciousness_data` or `symbolic_data`
- `user` → `conscious_entity` or `λid_holder`
- `system` → `consciousness_system` or `trinity_system`
