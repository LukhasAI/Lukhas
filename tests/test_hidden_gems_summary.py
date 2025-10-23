import json
from pathlib import Path

import pytest

from scripts.hidden_gems_summary import (
    HiddenGem,
    ManifestFormatError,
    build_summary_payload,
    extract_hidden_gems,
    format_summary,
    load_manifest,
    main,
    render_summary,
    summarize_by_lane,
)


def test_load_manifest_requires_module_list(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"modules": {}}))

    with pytest.raises(ManifestFormatError):
        load_manifest(manifest_path)


def test_extract_hidden_gems_filters_by_score_and_complexity() -> None:
    manifest_payload = {
        "modules": [
            {
                "module": "labs.module_a",
                "score": 71.2,
                "complexity": "low",
                "effort_hours": 3,
                "target_location": "core/module_a.py",
            },
            {
                "module": "labs.module_b",
                "score": 69.0,
                "complexity": "low",
                "effort_hours": 5,
                "target_location": "matriz/module_b.py",
            },
            {
                "module": "labs.module_c",
                "score": 90.0,
                "complexity": "medium",
                "effort_hours": 2,
                "target_location": "serve/module_c.py",
            },
        ]
    }

    gems = extract_hidden_gems(manifest_payload)

    assert [gem.module for gem in gems] == ["labs.module_a"]
    assert gems[0].lane == "core"


def test_summarize_and_format_summary_output() -> None:
    gems = [
        HiddenGem(
            module="labs.module_a",
            score=95.0,
            complexity="low",
            effort_hours=4.5,
            target_location="core/module_a.py",
        ),
        HiddenGem(
            module="labs.module_b",
            score=90.0,
            complexity="low",
            effort_hours=2.0,
            target_location="matriz/module_b.py",
        ),
    ]

    summary = summarize_by_lane(gems)
    assert summary["core"]["count"] == 1
    assert summary["matriz"]["effort"] == pytest.approx(2.0)

    rendered = format_summary(gems, top_n=2)

    assert "Hidden Gems Integration Summary" in rendered
    assert "core: 1 modules" in rendered
    assert "matriz: 1 modules" in rendered
    assert "labs.module_a" in rendered
    assert "labs.module_b" in rendered


def test_build_summary_payload_sorted_lanes() -> None:
    gems = [
        HiddenGem(
            module="labs.module_a",
            score=95.0,
            complexity="low",
            effort_hours=4.5,
            target_location="core/module_a.py",
        ),
        HiddenGem(
            module="labs.module_b",
            score=90.0,
            complexity="low",
            effort_hours=2.0,
            target_location="matriz/module_b.py",
        ),
    ]

    payload = build_summary_payload(gems, top_n=1)

    assert payload["total_modules"] == 2
    assert payload["total_effort_hours"] == pytest.approx(6.5)
    assert payload["lanes"][0]["lane"] == "core"
    assert payload["lanes"][1]["lane"] == "matriz"
    assert payload["top_modules"][0]["module"] == "labs.module_a"


def test_render_summary_json_format() -> None:
    gems = [
        HiddenGem(
            module="labs.module_a",
            score=95.0,
            complexity="low",
            effort_hours=4.5,
            target_location="core/module_a.py",
        )
    ]

    rendered = render_summary(gems, top_n=1, output_format="json")
    payload = json.loads(rendered)

    assert payload["total_modules"] == 1
    assert payload["top_modules"][0]["module"] == "labs.module_a"


def test_main_writes_output_file(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest_payload = {
        "modules": [
            {
                "module": "labs.module_a",
                "score": 80.0,
                "complexity": "low",
                "effort_hours": 2.5,
                "target_location": "core/module_a.py",
            }
        ]
    }
    manifest_path.write_text(json.dumps(manifest_payload))

    output_path = tmp_path / "summary.json"
    exit_code = main(
        [
            "--manifest",
            str(manifest_path),
            "--format",
            "json",
            "--top",
            "1",
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    written_payload = json.loads(output_path.read_text())
    assert written_payload["total_modules"] == 1
    assert written_payload["lanes"][0]["lane"] == "core"
