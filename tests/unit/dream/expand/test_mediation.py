from consciousness.dream.expand import mediation


def test_mediate_creates_compromise():
    a = {"confidence": 0.8, "joy": 0.6}
    b = {"confidence": 0.2, "joy": 0.4}
    target = {"confidence": 0.5, "joy": 0.5}

    result = mediation.mediate(a, b, target)

    assert "compromise" in result
    assert "trace" in result
    assert result["compromise"]["confidence"] == 0.5
    assert result["compromise"]["joy"] == 0.5


def test_mediate_handles_missing_keys():
    a = {"confidence": 0.8}
    b = {"joy": 0.4}
    target = {}

    result = mediation.mediate(a, b, target)

    assert result["compromise"]["confidence"] == 0.4
    assert result["compromise"]["joy"] == 0.2
