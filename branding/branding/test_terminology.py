from lukhas.branding.terminology import normalize_output


def test_normalize_quantum_and_bio():
    s = "We use quantum process and bio processing to achieve results."
    out = normalize_output(s)
    assert "quantum-inspired" in out
    assert "bio-inspired" in out


def test_standalone_quantum_becomes_quantum_inspired():
    s = "We explore quantum phenomena in this system."
    out = normalize_output(s)
    assert "quantum-inspired" in out


def test_quantum_inspired_and_metaphors_are_preserved():
    s1 = "We use quantum-inspired search heuristics."
    s2 = "We discuss quantum metaphors for cognition."
    out1 = normalize_output(s1)
    out2 = normalize_output(s2)
    assert "quantum-inspired" in out1
    assert "quantum metaphors" in out2


def test_normalize_lukhas_agi():
    s = "Welcome to LUKHAS AGI platform."
    out = normalize_output(s)
    assert "LUKHAS AI" in out
    assert "AGI" not in out
