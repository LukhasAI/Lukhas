"""
Narrative Replay: explainability in plain language.
"""
def describe(trace: dict) -> str:
    return (f"Dream {trace.get('target')} chosen "
            f"(align={trace.get('reason','?')})")
