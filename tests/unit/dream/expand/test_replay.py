from lukhas.consciousness.dream.expand import replay


def test_describe_formats_trace():
    trace = {"target": "dream_123", "reason": "high_alignment"}
    result = replay.describe(trace)
    assert "dream_123" in result
    assert "high_alignment" in result

def test_describe_handles_missing_fields():
    trace = {"target": "dream_456"}
    result = replay.describe(trace)
    assert "dream_456" in result
    assert "?" in result  # default reason
