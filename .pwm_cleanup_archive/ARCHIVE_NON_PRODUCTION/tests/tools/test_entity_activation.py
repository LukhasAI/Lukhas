from pathlib import Path

from tools.entity_activation.entity_activator import EntityActivator


def test_entity_activation_generates_file(tmp_path: Path):
    # create sample module
    sample_dir = tmp_path / "sample"
    sample_dir.mkdir()
    module_file = sample_dir / "demo.py"
    module_file.write_text(
        """\nclass DemoClass:\n    pass\n\ndef helper():\n    return 1\n"""
    )

    activator = EntityActivator(str(tmp_path))
    activator.activate_system("sample", "sample")

    activation_file = tmp_path / "sample_entity_activation.py"
    assert activation_file.exists()
    content = activation_file.read_text()
    assert "DemoClass" in content
