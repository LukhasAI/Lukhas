"""Utility for summarizing Hidden Gems integration manifest entries."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

# ΛTAG: hidden_gems_summary

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST_PATH = _REPO_ROOT / "docs" / "audits" / "integration_manifest.json"


class ManifestFormatError(ValueError):
    """Raised when the integration manifest does not match the expected schema."""


@dataclass(frozen=True)
class HiddenGem:
    """Normalized representation of a manifest entry ready for reporting."""

    module: str
    score: float
    complexity: str
    effort_hours: float
    target_location: str

    # ΛTAG: hidden_gem_lane
    @property
    def lane(self) -> str:
        """Return the top-level directory for the target location (e.g., core/matriz)."""

        target_path = Path(self.target_location)
        return target_path.parts[0] if target_path.parts else "unknown"

    # ΛTAG: hidden_gem_factory
    @classmethod
    def from_manifest_entry(cls, entry: Mapping[str, Any]) -> HiddenGem:
        """Create a ``HiddenGem`` from a manifest entry, validating required fields."""

        required_fields = ("module", "score", "complexity", "effort_hours", "target_location")
        missing = [field for field in required_fields if field not in entry]
        if missing:
            raise ManifestFormatError(f"Manifest entry missing required fields: {', '.join(missing)}")

        try:
            score = float(entry["score"])
            effort_hours = float(entry["effort_hours"])
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive check
            raise ManifestFormatError("Score and effort_hours must be numeric") from exc

        return cls(
            module=str(entry["module"]),
            score=score,
            complexity=str(entry["complexity"]),
            effort_hours=effort_hours,
            target_location=str(entry["target_location"]),
        )


def load_manifest(manifest_path: Path) -> Mapping[str, Any]:
    """Load the integration manifest JSON file and validate its structure."""

    try:
        payload = json.loads(manifest_path.read_text())
    except FileNotFoundError as exc:
        raise ManifestFormatError(f"Manifest not found at {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestFormatError(f"Manifest JSON invalid: {exc}") from exc

    modules = payload.get("modules")
    if not isinstance(modules, list):
        raise ManifestFormatError("Manifest must contain a 'modules' list")

    return payload


def extract_hidden_gems(
    manifest_payload: Mapping[str, Any], *, min_score: float = 70.0, complexity: str = "low"
) -> List[HiddenGem]:
    """Return manifest entries meeting the hidden gem criteria."""

    modules: Iterable[Mapping[str, Any]] = manifest_payload.get("modules", [])
    gems: List[HiddenGem] = []
    for entry in modules:
        if entry.get("complexity") != complexity:
            continue
        try:
            score = float(entry.get("score", 0.0))
        except (TypeError, ValueError):
            continue
        if score < min_score:
            continue
        gem = HiddenGem.from_manifest_entry(entry)
        gems.append(gem)
    return gems


def summarize_by_lane(gems: Sequence[HiddenGem]) -> Dict[str, Dict[str, float]]:
    """Aggregate hidden gem counts and effort by lane."""

    summary: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "effort": 0.0})
    for gem in gems:
        lane_stats = summary[gem.lane]
        lane_stats["count"] += 1
        lane_stats["effort"] += gem.effort_hours
    return summary


def format_summary(gems: Sequence[HiddenGem], *, top_n: int = 5) -> str:
    """Create a human-readable summary for the filtered hidden gems."""

    if not gems:
        return "No hidden gems match the provided filters."

    lane_summary = summarize_by_lane(gems)
    total_effort = sum(gem.effort_hours for gem in gems)
    total_modules = len(gems)

    lines = [
        "Hidden Gems Integration Summary",
        "--------------------------------",
        f"Total modules: {total_modules}",
        f"Total effort hours: {total_effort:.1f}",
        "",
        "By lane:",
    ]

    for lane, stats in sorted(lane_summary.items()):
        lines.append(
            f"- {lane}: {int(stats['count'])} modules · {stats['effort']:.1f} effort hours"
        )

    lines.append("")
    lines.append(f"Top {min(top_n, total_modules)} modules by score:")

    top_modules = sorted(gems, key=lambda gem: gem.score, reverse=True)[:top_n]
    for gem in top_modules:
        lines.append(
            f"- {gem.score:.1f} · {gem.module} → {gem.target_location} ({gem.effort_hours:.1f}h)"
        )

    return "\n".join(lines)


def _resolve_manifest_path(path_argument: Optional[Path]) -> Path:
    """Resolve the manifest path argument, falling back to the default location."""

    manifest_path = path_argument or DEFAULT_MANIFEST_PATH
    if not manifest_path.exists():
        raise ManifestFormatError(f"Manifest not found at {manifest_path}")
    return manifest_path


def _build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Summarize low-complexity high-score modules from the Hidden Gems integration manifest"
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to the integration manifest JSON (defaults to repository manifest)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=70.0,
        help="Minimum module score required to qualify as a hidden gem",
    )
    parser.add_argument(
        "--complexity",
        choices=["low", "medium", "high"],
        default="low",
        help="Complexity level to include in the summary",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top modules by score to display",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for the CLI utility."""

    parser = _build_parser()
    args = parser.parse_args(argv)

    manifest_path = _resolve_manifest_path(args.manifest)

    try:
        # ΛTAG: hidden_gems_cli_validation
        manifest_payload = load_manifest(manifest_path)
        gems = extract_hidden_gems(
            manifest_payload, min_score=args.min_score, complexity=args.complexity
        )
        summary = format_summary(gems, top_n=args.top)
    except ManifestFormatError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
