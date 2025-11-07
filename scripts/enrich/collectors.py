"""
T4/0.01% Semantic Extractors with Multi-Evidence Requirements
==============================================================

All extractors return Signal objects with full provenance chains.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from enrich.review_queue import ReviewQueue


@dataclass
class Signal:
    """Extracted signal with full T4/0.01% provenance"""
    value: Any
    provenance: list[str]
    confidence: str  # "high" | "medium" | "low"
    reasons: list[str]
    extracted_at: str
    sha: str | None = None

    def to_prov(self) -> Dict:
        """Convert to _provenance schema format"""
        out = {
            "sources": self.provenance,
            "confidence": self.confidence,
            "extracted_at": self.extracted_at
        }
        if self.sha:
            out["sha"] = self.sha
        if self.reasons:
            out["reasons"] = self.reasons
        return out


def _now() -> str:
    """ISO 8601 timestamp with timezone"""
    return datetime.now(timezone.utc).isoformat()


class Vocab:
    """Controlled vocabulary manager with synonym mapping"""

    def __init__(self, root: Path):
        self.root = root
        self.features = self._load_features()
        self.tags_allowed = self._load_tags()
        self.synonym_map = self._build_synonym_map()

    def _load_features(self) -> Dict:
        path = self.root / "vocab" / "features.json"
        if not path.exists():
            return {}
        return json.loads(path.read_text())

    def _load_tags(self) -> set:
        path = self.root / "vocab" / "tags.json"
        if not path.exists():
            return set()
        data = json.loads(path.read_text())
        return set(data.get("allowed", []))

    def _build_synonym_map(self) -> dict[str, str]:
        """Build mapping from synonyms to canonical keys"""
        mapping = {}
        for canonical, meta in self.features.items():
            # Map canonical to itself
            mapping[canonical.lower()] = canonical
            # Map all synonyms to canonical
            for syn in meta.get("synonyms", []):
                mapping[syn.lower().strip()] = canonical
        return mapping

    def map_feature(self, text: str) -> str | None:
        """Map raw text to canonical feature key"""
        normalized = text.lower().strip()
        return self.synonym_map.get(normalized)

    def is_tag_allowed(self, tag: str) -> bool:
        """Check if tag is in allowed list"""
        return tag in self.tags_allowed


class ClaudeExtractor:
    """Extract semantics from claude.me files with min-evidence requirements"""

    def __init__(self, vocab: Vocab, repo_root: Path):
        self.vocab = vocab
        self.repo_root = repo_root
        self.queue = ReviewQueue(repo_root)

    def _read(self, path: Path) -> str | None:
        """Safe read with error handling"""
        if not path.exists():
            return None
        try:
            return path.read_text(errors="ignore")
        except Exception:
            return None

    def flush_queue(self):
        """Persist review queue to disk"""
        self.queue.save()

    def features(self, claude_me: Path, module_name: str = "") -> Signal:
        """
        Extract features with multi-pattern validation.
        Requires min-evidence: 2+ patterns OR 5+ from single pattern.
        Unmapped phrases are added to review queue for promotion.
        """
        txt = self._read(claude_me)
        if not txt:
            return Signal(
                value=[],
                provenance=[],
                confidence="low",
                reasons=["file_not_found"],
                extracted_at=_now()
            )

        sha = hashlib.sha256(txt.encode()).hexdigest()

        def add_unmapped(raw_text: str, source: str):
            """Add unmapped phrase to review queue"""
            # Strip markdown formatting
            raw = re.sub(r'[*_`~]', '', raw_text).strip()
            if raw and self.vocab.map_feature(raw) is None:
                self.queue.add(raw, module_name or claude_me.parent.name, source)

        # Pattern 1: Bullet lists with **Feature**:
        bullets = set()
        bullet_pattern = re.compile(r'^[\s]*[-•*]\s*(.+)$', re.MULTILINE)
        for match in bullet_pattern.finditer(txt):
            raw = match.group(1).split(':')[0].strip()
            canonical = self.vocab.map_feature(raw)
            if canonical:
                bullets.add(canonical)
            else:
                add_unmapped(raw, "claude.me:bullets")

        # Pattern 2: Section headers (## or ###)
        headers = set()
        header_pattern = re.compile(r'^(?:##|###)\s+(.+)$', re.MULTILINE)
        for match in header_pattern.finditer(txt):
            raw = match.group(1).strip()
            canonical = self.vocab.map_feature(raw)
            if canonical:
                headers.add(canonical)
            else:
                add_unmapped(raw, "claude.me:headers")

        # Min-evidence calculation
        both_patterns = len(bullets & headers)

        if both_patterns >= 2:
            confidence = "high"
            reasons = [f"multi_match:{both_patterns}"]
        elif len(bullets) >= 5:
            confidence = "medium"
            reasons = [f"bullets:{len(bullets)}"]
        elif len(headers) >= 5:
            confidence = "medium"
            reasons = [f"headers:{len(headers)}"]
        else:
            confidence = "low"
            reasons = ["weak_evidence"]

        # Combine and deduplicate, max 15
        all_features = sorted(bullets | headers)[:15]

        return Signal(
            value=all_features,
            provenance=["claude.me:bullets", "claude.me:headers"],
            confidence=confidence,
            reasons=reasons,
            extracted_at=_now(),
            sha=sha
        )

    def components_count(self, claude_me: Path) -> int:
        """
        Count components (H3 headings under Components section).
        Crude but stable heuristic.
        """
        txt = self._read(claude_me)
        if not txt:
            return 0

        # Find Components section (H2) and count H3s within it
        comp_section = re.search(
            r'^##\s+.*[Cc]omponents.*?(?=^##\s+|\Z)',
            txt,
            flags=re.MULTILINE | re.DOTALL
        )

        if comp_section:
            block = comp_section.group(0)
            count = len(re.findall(r'^###\s+', block, re.MULTILINE))
            return count

        # Fallback: count all H3s (less accurate)
        return len(re.findall(r'^###\s+', txt, re.MULTILINE))

    def description(
        self,
        claude_me: Path,
        features: list[str],
        components_count: int
    ) -> Signal:
        """
        Generate rich description with guardrails:
        - 120-360 chars
        - Must reference ≥1 canonical feature
        - Must include component count
        - No emojis
        """
        txt = self._read(claude_me)
        if not txt:
            return Signal(
                value=None,
                provenance=[],
                confidence="low",
                reasons=["file_not_found"],
                extracted_at=_now()
            )

        # Extract title (H1)
        title_match = re.search(r'^#\s+(.+)$', txt, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ""

        # Extract subtitle (italic line after title)
        subtitle_match = re.search(r'^\*(.+?)\*$', txt, re.MULTILINE)
        subtitle = subtitle_match.group(1).strip() if subtitle_match else ""

        # Find first substantial paragraph
        paragraphs = [
            p.strip() for p in txt.split('\n\n')
            if len(p.strip()) > 80 and not p.strip().startswith('#')
        ]
        first_para = paragraphs[0] if paragraphs else ""

        # Build description parts
        parts = []
        if title:
            parts.append(title)
        if subtitle:
            parts.append(subtitle)
        if first_para:
            # Take first sentence
            first_sentence = first_para.split('.')[0] + '.'
            parts.append(first_sentence)

        # Add required feature + component reference
        if features:
            feature_sample = ', '.join(features[:3])
            parts.append(
                f"Implements {feature_sample} with {components_count} integrated components"
            )

        description = ' '.join(parts)

        # Trim to bounds
        if len(description) > 360:
            description = description[:357] + "..."

        # Validate guardrails
        if len(description) < 120:
            confidence = "low"
            reasons = [f"too_short:{len(description)}"]
        elif not features:
            confidence = "low"
            reasons = ["no_features_contradiction"]
        elif any(ord(c) > 127 for c in description):
            confidence = "low"
            reasons = ["contains_non_ascii_possibly_emoji"]
        else:
            confidence = "high"
            reasons = ["length_ok", "features_present", f"components:{components_count}"]

        return Signal(
            value=description if len(description) >= 120 else None,
            provenance=["claude.me:title+subtitle+para"],
            confidence=confidence,
            reasons=reasons,
            extracted_at=_now()
        )


class InitExtractor:
    """Extract API surface from __init__.py files"""

    def apis(self, module_dir: Path) -> Signal:
        """
        Extract exported APIs from __init__.py.
        Returns metadata dict with doc_ok checks (≥80 chars).
        """
        init_path = module_dir / "__init__.py"
        if not init_path.exists():
            return Signal(
                value={},
                provenance=[],
                confidence="low",
                reasons=["no_init_file"],
                extracted_at=_now()
            )

        try:
            tree = ast.parse(init_path.read_text())
        except SyntaxError as e:
            return Signal(
                value={},
                provenance=[],
                confidence="low",
                reasons=[f"syntax_error:{e}"],
                extracted_at=_now()
            )

        # Extract __all__ exports
        exports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (isinstance(target, ast.Name) and target.id == '__all__') and isinstance(node.value, (ast.List, ast.Tuple)):
                        for elem in node.value.elts:
                            if isinstance(elem, (ast.Str, ast.Constant)):
                                val = getattr(elem, "s", None) or getattr(elem, "value", None)
                                if val:
                                    exports.add(val)

        # Fallback: public class/function defs
        if not exports:
            for node in tree.body:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and (not node.name.startswith('_')):
                    exports.add(node.name)

        # Build API metadata
        apis = {}
        for name in sorted(exports):
            # Check docstring length
            doc_ok = False
            try:
                node = next(
                    n for n in ast.walk(tree)
                    if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name == name
                )
                docstring = ast.get_docstring(node) or ""
                doc_ok = len(docstring) >= 80
            except StopIteration:
                pass

            apis[name] = {
                "description": "Auto-detected API; fill in description ≥ 40 chars.",
                "module": f"{module_dir.name}.{name}",  # Will be refined by caller
                "capabilities": [],
                "doc_ok": doc_ok,
                "import_verified": False  # Set by ImportVerifier
            }

        confidence = "high" if apis else "low"
        reasons = ["exports_detected" if apis else "no_exports"]

        return Signal(
            value=apis,
            provenance=["ast:__init__.py"],
            confidence=confidence,
            reasons=reasons,
            extracted_at=_now()
        )


class ImportVerifier:
    """
    Verify API imports without executing code.
    Uses AST-only checks to confirm symbols exist.
    """

    def verify(
        self,
        pkg_root: Path,
        module_dir: Path,
        apis: dict[str, Dict]
    ) -> Signal:
        """
        Verify each API is importable by checking:
        1. File/module exists
        2. Symbol present in AST

        No actual imports to avoid side effects.
        """
        provenance = []
        verified = {}

        for name, meta in apis.items():
            module_spec = meta.get("module", f"{module_dir.name}.{name}")

            # Resolve file path
            # module_spec like "consciousness.api" -> consciousness/api.py or consciousness/api/__init__.py
            mod_path = pkg_root / module_spec.replace(".", "/")
            candidates = [
                mod_path.with_suffix(".py"),
                mod_path / "__init__.py"
            ]

            src_file = None
            for candidate in candidates:
                if candidate.exists():
                    src_file = candidate
                    break

            import_ok = False
            if src_file:
                try:
                    tree = ast.parse(src_file.read_text())
                    # Check if symbol exists in AST
                    import_ok = any(
                        isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name
                        for node in ast.walk(tree)
                    )
                except SyntaxError:
                    import_ok = False

            # Update metadata
            updated_meta = dict(meta)
            updated_meta["import_verified"] = import_ok
            verified[name] = updated_meta

            prov_entry = f"importcheck:{src_file.relative_to(pkg_root) if src_file else 'missing'}"
            provenance.append(prov_entry)

        # Confidence based on verification results
        all_verified = all(v.get("import_verified") for v in verified.values())

        if all_verified and verified:
            confidence = "high"
            reasons = ["all_symbols_verified"]
        elif verified:
            confidence = "medium"
            verified_count = sum(1 for v in verified.values() if v.get("import_verified"))
            reasons = [f"partial_verification:{verified_count}/{len(verified)}"]
        else:
            confidence = "low"
            reasons = ["no_apis"]

        return Signal(
            value=verified,
            provenance=provenance,
            confidence=confidence,
            reasons=reasons,
            extracted_at=_now()
        )
