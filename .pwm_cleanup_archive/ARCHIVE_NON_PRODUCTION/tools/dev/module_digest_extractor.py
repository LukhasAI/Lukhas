import json
import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ΛTAG: digest_extraction

HEADER_MARKER_RE = re.compile(
    r"#\s*ΛHEADER_START(?P<body>.*?)#\s*ΛHEADER_END", re.DOTALL
)
FOOTER_MARKER_RE = re.compile(r"#\s*ΛFOOTER_START(?P<body>.*)", re.DOTALL)
TRIPLE_HEADER_RE = re.compile(r"\A[\"']{3}(?P<body>.*?)[\"']{3}", re.DOTALL)
TRIPLE_BLOCK_RE = re.compile(r"[\"']{3}(?P<body>.*?)[\"']{3}", re.DOTALL)

MODULE_RE = re.compile(r"Module:\s*(?P<name>[\w_\.]+)")
VERSION_RE = re.compile(r"Version:\s*(?P<version>[^|\n]+)")
TAGS_RE = re.compile(r"Symbolic Tags:\s*(?P<tags>.+)")
TRACE_FIELD_RE = re.compile(r"#\s*(Λ[A-Z_]+):\s*(.*)")


@dataclass
class ModuleDigest:
    name: str
    path: str
    version: Optional[str] = None
    tags: List[str] = None
    fields: Dict[str, str] = None

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class ModuleDigestExtractor:
    """Extract module metadata from core.common headers/footers."""

    def __init__(self, base_path: Optional[str] = None):
        repo_root = (
            Path(base_path) if base_path else Path(__file__).resolve().parents[2]
        )
        self.repo_root = repo_root
        self.lukhas_root = repo_root / "lukhas"
        self.digest_dir = self.lukhas_root / "tools" / "digest"
        self.modules: List[ModuleDigest] = []
        self.anomalies: List[str] = []

    def run(self, filter_tags: Optional[Iterable[str]] = None) -> None:
        self.digest_dir.mkdir(parents=True, exist_ok=True)
        for py_file in self.lukhas_root.rglob("*.py"):
            digest = self._process_file(py_file)
            if not digest:
                continue
            if filter_tags and not any(tag in digest.tags for tag in filter_tags):
                continue
            self.modules.append(digest)
        self._write_outputs()

    def _process_file(self, path: Path) -> Optional[ModuleDigest]:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning("Could not read %s: %s", path, exc)
            self.anomalies.append(f"unreadable: {path}")
            return None

        header = self._extract_block(text, HEADER_MARKER_RE)
        if not header:
            # fall back to triple-quoted header at beginning
            m = TRIPLE_HEADER_RE.match(text)
            if m and "LUKHAS" in m.group("body"):
                header = m.group("body")

        if not header:
            logger.debug("Missing header in %s", path)
            self.anomalies.append(f"no_header: {path}")
            return None

        footer = self._extract_block(text, FOOTER_MARKER_RE)
        if not footer:
            # search for triple-quoted block containing FOOTER
            for match in TRIPLE_BLOCK_RE.finditer(text):
                if "FOOTER" in match.group("body"):
                    footer = match.group("body")
                    break

        module_name = self._match_value(header, MODULE_RE) or path.stem
        version = self._match_value(header, VERSION_RE)
        tag_line = self._match_value(header, TAGS_RE)
        tags = self._parse_tags(tag_line)

        fields = {}
        for line in header.splitlines():
            tm = TRACE_FIELD_RE.match(line.strip())
            if tm:
                fields[tm.group(1)] = tm.group(2)

        digest = ModuleDigest(
            name=module_name,
            path=str(path.relative_to(self.repo_root)),
            version=version,
            tags=tags,
            fields=fields,
        )
        logger.debug("Extracted %s", digest)
        return digest

    def _extract_block(self, text: str, pattern: re.Pattern) -> Optional[str]:
        m = pattern.search(text)
        return m.group("body") if m else None

    def _match_value(self, text: str, pattern: re.Pattern) -> Optional[str]:
        m = pattern.search(text)
        return m.group(1).strip() if m else None

    def _parse_tags(self, tag_line: Optional[str]) -> List[str]:
        if not tag_line:
            return []
        tags = re.findall(r"#(\w+)", tag_line) + re.findall(r"{([^}]+)}", tag_line)
        return list({t.strip() for t in tags if t.strip()})

    def _write_outputs(self) -> None:
        json_path = self.digest_dir / "digest.json"
        md_path = self.digest_dir / "DIGEST_SUMMARY.md"

        data = [m.to_dict() for m in self.modules]
        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        lines = ["# Module Digest Summary", ""]
        for module in self.modules:
            lines.append(f"## {module.name}")
            lines.append(f"- Path: {module.path}")
            if module.version:
                lines.append(f"- Version: {module.version}")
            if module.tags:
                lines.append(f"- Tags: {', '.join(module.tags)}")
            if module.fields:
                lines.append("- Fields:")
                for k, v in module.fields.items():
                    lines.append(f"  - {k}: {v}")
            lines.append("")
        md_path.write_text("\n".join(lines), encoding="utf-8")

        if self.anomalies:
            logger.info("Anomalies detected: %s", self.anomalies)
