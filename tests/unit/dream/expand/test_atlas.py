from consciousness.dream.expand import atlas


def test_log_creates_entry():
    result = atlas.log("test_run", {"name": "test"}, 0.5, 0.3)
    assert result["run_id"] == "test_run"
    assert result["drift"] == 0.5
    assert result["entropy"] == 0.3
    assert "ts" in result


def test_export_html_creates_file():
    atlas.export_html("/tmp/test_atlas.html")
    with open("/tmp/test_atlas.html") as f:
        content = f.read()
    assert "Drift Atlas" in content
