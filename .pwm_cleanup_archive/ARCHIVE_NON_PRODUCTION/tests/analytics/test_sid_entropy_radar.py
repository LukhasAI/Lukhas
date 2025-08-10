from diagnostics.entropy_radar import collect_sid_hashes, shannon_entropy


def test_collect_sid_hashes(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("sid_hash = 'abcdef'\nother = 1")
    result = collect_sid_hashes(str(tmp_path))
    assert "sample" in result
    assert result["sample"] == ["abcdef"]


def test_shannon_entropy():
    values = ["a", "a", "b", "b", "b"]
    ent = shannon_entropy(values)
    assert round(ent, 3) > 0
