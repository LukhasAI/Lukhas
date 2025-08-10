"""Render visual drift maps for symbolic entropy."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

# ΛTAG: diagnostics, entropy_radar


def load_brief_metrics(base_dir: str = "lukhas") -> dict[str, dict[str, float]]:
    """Load symbolic entropy and collapse deltas from .brief.yaml files."""
    metrics: dict[str, dict[str, float]] = {}
    for yaml_path in Path(base_dir).rglob("*.brief.yaml"):
        try:
            data = yaml.safe_load(yaml_path.read_text()) or {}
        except Exception:
            continue
        symbolic = data.get("symbolic", {})
        module = data.get("module", {}).get("name", yaml_path.stem)
        entropy = float(symbolic.get("entropy", 0.0))
        delta = float(symbolic.get("collapse_delta", 0.0))
        metrics[module] = {"entropy": entropy, "collapse_delta": delta}
    return metrics


def render_entropy_radar(
    module: str, values: dict[str, float], output_dir: Path
) -> Path:
    """Render a radar chart for the provided module metrics."""
    labels = list(values.keys())
    if not labels:
        raise ValueError("No metrics provided")
    stats = [values[label] for label in labels]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw={"polar": True})
    ax.plot(angles, stats, "o-", linewidth=2)
    ax.fill(angles, stats, alpha=0.25)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_title(f"Λ {module} Drift Map")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{module}_entropy.svg"
    plt.tight_layout()
    plt.savefig(out_path, format="svg")
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Entropy Drift Radar")
    parser.add_argument(
        "--drift-only",
        action="store_true",
        help="Only render modules with non-zero collapse delta",
    )
    args = parser.parse_args()

    metrics = load_brief_metrics()
    output_dir = Path("lukhas/diagnostics/plots")

    for module, vals in metrics.items():
        if args.drift_only and vals.get("collapse_delta", 0.0) == 0.0:
            continue
        render_entropy_radar(module, vals, output_dir)


if __name__ == "__main__":
    main()
