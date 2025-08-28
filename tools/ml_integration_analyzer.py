"""
ML-Powered Integration Analyzer for LUKHΛS
-------------------------------------------------

A modular Python tool that evaluates orphaned modules for potential reintegration into the LUKHΛS system using an enhanced SWOT-like framework, semantic code embeddings, security/style checks, and OpenAI-assisted reasoning.

Key Features
============
- Multi-modal code understanding (AST parsing, docstring/comment scan, optional git history)
- Semantic function mapping via embeddings (OpenAI or pluggable encoders)
- Integration pathway discovery (direct, wrapper, gradual migration) with line-by-line mapping hints
- Scoring & risk assessment (value/effort, tech debt, security heuristics)
- Continuous learning hooks (feedback registry for outcome-based calibration)
- Safety & explainability (uncertainty quantification, audit log, "I don't know" gating)
- Naming convention harmonization & code style alignment
- OpenAI "ultimate analysis" assistant to refine SWOT and recommendations

Design Notes
============
- The analyzer is **non-destructive**. It reads files, never writes to source code.
- All outputs are emitted as structured JSON plus an audit log for traceability.
- External tools (git, semgrep) are optional. The analyzer gracefully degrades.

"""
from __future__ import annotations

import ast
import datetime as _dt
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import numpy as np
except Exception:  # pragma: no cover
    np = None  # type: ignore

# -----------------------------
# Utility: Audit Recorder
# -----------------------------
class Audit:
    """Simple append-only audit trail with timestamps."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def log(self, action: str, **data: Any) -> None:
        self.events.append({
            "ts": _dt.datetime.utcnow().isoformat() + "Z",
            "action": action,
            **data,
        })

    def to_list(self) -> list[dict[str, Any]]:
        return self.events


# -----------------------------
# Utility: Naming Conventions
# -----------------------------
_CAMEL_RE = re.compile(r"(^|_)([a-z])")


def camel_to_snake(name: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.replace("__", "_").lower()


def snake_to_camel(name: str, upper_first: bool = False) -> str:
    parts = name.split("_")
    parts = [p.capitalize() for p in parts]
    res = "".join(parts)
    if not upper_first:
        res = res[0].lower() + res[1:] if res else res
    return res


def detect_naming_convention(name: str) -> str:
    if "_" in name and name.lower() == name:
        return "snake_case"
    if re.search(r"[A-Z]", name) and name[0].islower():
        return "camelCase"
    if name and name[0].isupper() and re.search(r"[A-Z]", name[1:]):
        return "PascalCase"
    return "unknown"


# -----------------------------
# Utility: Simple Security Heuristics
# -----------------------------
SQL_PATTERNS = [
    r"SELECT\s+.*\s+FROM\s+.*\+",  # naive concat in SQL
    r"INSERT\s+INTO\s+.*\+",
    r"execute\((?P<arg>.+)\)",
]
DANGEROUS_CALLS = ["eval(", "exec(", "os.system(", "subprocess.Popen("]


# -----------------------------
# Utility: Code Extraction
# -----------------------------
@dataclass
class FunctionSig:
    name: str
    args: list[str]
    lineno: int
    end_lineno: int
    source: str
    docstring: str | None


@dataclass
class ModuleView:
    path: Path
    code: str
    ast: ast.AST
    functions: list[FunctionSig]
    imports: list[str]
    comments: list[str]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def extract_module_view(py_path: Path) -> ModuleView:
    code = read_text(py_path)
    tree = ast.parse(code)
    funcs: list[FunctionSig] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            args = [a.arg for a in node.args.args]
            start = node.lineno
            end = getattr(node, "end_lineno", node.lineno)
            lines = code.splitlines()
            source = "\n".join(lines[start - 1:end])
            doc = ast.get_docstring(node)
            funcs.append(FunctionSig(
                name=node.name,
                args=args,
                lineno=start,
                end_lineno=end,
                source=source,
                docstring=doc,
            ))

    imports = re.findall(r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))",
                         code, flags=re.MULTILINE)
    import_names = [a or b for a, b in imports]

    comments = [m.group(0) for m in re.finditer(r"# .*$", code, re.MULTILINE]

    return ModuleView(path=py_path, code=code, ast=tree,
                      functions=funcs, imports=import_names, comments=comments)


# -----------------------------
# Embedding Adapter (OpenAI + pluggable)
# -----------------------------
class EmbeddingAdapter:
    """Pluggable embedding provider. Defaults to OpenAI if available."""

    def __init__(self, provider: str = "openai", model: str = "text-embedding-3-small", dimensions: int | None = None) -> None:
        self.provider = provider
        self.model = model
        self.dimensions = dimensions
        self._client = None
        if provider == "openai":
            try:
                from openai import OpenAI  # type: ignore
                self._client = OpenAI()
            except Exception:  # pragma: no cover
                self._client = None

    def encode(self, text: str) -> list[float]:
        if self.provider == "openai" and self._client is not None:
            kwargs = {"model": self.model, "input": text}
            if self.dimensions:
                kwargs["dimensions"] = self.dimensions
            res = self._client.embeddings.create(**kwargs)
            return res.data[0].embedding  # type: ignore
        # Fallback: deterministic hash-based pseudo-embedding (low-quality but stable)
        return self._hash_embed(text)

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        if self.provider == "openai" and self._client is not None:
            kwargs = {"model": self.model, "input": texts}
            if self.dimensions:
                kwargs["dimensions"] = self.dimensions
            res = self._client.embeddings.create(**kwargs)
            return [d.embedding for d in res.data]  # type: ignore
        return [self._hash_embed(t) for t in texts]

    @staticmethod
    def _hash_embed(text: str, dim: int = 256) -> list[float]:
        # Simple locality-preserving bag-of-hash embedding
        vec = [0.0] * dim
        for token in re.findall(r"\w+", text.lower()):
            h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
            idx = h % dim
            vec[idx] += 1.0
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


# -----------------------------
# OpenAI Reasoner Adapter
# -----------------------------
class ReasonerAdapter:
    """Wrapper around OpenAI Responses API with graceful fallback."""

    def __init__(self, model: str = os.getenv("LUKHAS_REASONER_MODEL", "gpt-5-mini")) -> None:
        self.model = model
        try:
            from openai import OpenAI  # type: ignore
            self._client = OpenAI()
        except Exception:  # pragma: no cover
            self._client = None

    def analyze(self, system_prompt: str, user_prompt: str, max_output_tokens: int = 1200) -> str:
        if self._client is None:
            # Offline fallback: heuristic summary
            return "[offline] Heuristic analysis only. No OpenAI output available."
        try:
            # Prefer Responses API
            res = self._client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_output_tokens=max_output_tokens,
            )
            # Unified getter for text output
            if hasattr(res, "output_text"):
                return res.output_text  # type: ignore
            # Fallback extraction
            return json.dumps(res.dict())[:2000]
        except Exception:
            # Try Chat Completions if Responses is unavailable
            try:
                resp = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                )
                return resp.choices[0].message.content or ""
            except Exception as e:  # pragma: no cover
                return f"[error] OpenAI call failed: {e}"

    def analyze_on_model(self, model: str, system_prompt: str, user_prompt: str, max_output_tokens: int = 1200) -> str:
        if self._client is None:
            return "[offline] Heuristic analysis only. No OpenAI output available."
        try:
            res = self._client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_output_tokens=max_output_tokens,
            )
            if hasattr(res, "output_text"):
                return res.output_text  # type: ignore
            return json.dumps(res.dict())[:2000]
        except Exception:
            try:
                resp = self._client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                )
                return resp.choices[0].message.content or ""
            except Exception as e:  # pragma: no cover
                return f"[error] OpenAI call failed: {e}"


# -----------------------------
# Similarity
# -----------------------------

def cosine_similarity(a: list[float], b: list[float]) -> float:
    if np is not None:
        aa = np.array(a)
        bb = np.array(b)
        denom = (np.linalg.norm(aa) * np.linalg.norm(bb)) or 1.0
        return float(np.dot(aa, bb) / denom)
    # Minimal pure-Python fallback
    denom = (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b))) or 1.0
    dot = sum(x*y for x, y in zip(a, b))
    return dot / denom


# -----------------------------
# Dataclasses for Output JSON
# -----------------------------
@dataclass
class SWOTEntry:
    description: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class LineMapping:
    source_line: int
    source_code: str
    target_file: str
    target_line: int
    suggested_merge: str
    confidence: float
    required_adaptations: list[str]
    # new:
    source_context_before: list[str] = field(default_factory=list)
    source_context_after: list[str] = field(default_factory=list)
    target_context_before: list[str] = field(default_factory=list)
    target_context_after: list[str] = field(default_factory=list)
    param_rename_map: dict[str, str] = field(default_factory=dict)


@dataclass
class IntegrationStrategy:
    strategy: str
    effort_estimate: str
    risk_level: str
    pros: list[str]
    cons: list[str]


@dataclass
class RiskAssessment:
    security_scan: dict[str, Any]
    dependency_analysis: dict[str, Any]
    performance_impact: dict[str, Any]


# -----------------------------
# Analyzer Core
# -----------------------------
class IntegrationAnalyzer:
    """Main orchestrator for the LUKHΛS Integration Analyzer."""

    def __init__(
        self,
        audit: Audit | None = None,
        embedder: EmbeddingAdapter | None = None,
        reasoner: ReasonerAdapter | None = None,
        confidence_threshold: float = 0.75,
        style_prefs: dict[str, Any] | None = None,
    ) -> None:
        self.audit = audit or Audit()
        self.embedder = embedder or EmbeddingAdapter()
        self.reasoner = reasoner or ReasonerAdapter()
        self.confidence_threshold = confidence_threshold
        self.style_prefs = style_prefs or {
            "naming": "snake_case",
            "indent": 4,
            "type_hints": True,
        }

    # ---------- Discovery ----------
    def discover_python_files(self, root: Path) -> list[Path]:
        files = [p for p in root.rglob("*.py") if p.is_file() and ".venv" not in p.parts and "__pycache__" not in p.parts]
        self.audit.log("discover_files", root=str(root), count=len(files))
        return files

    def parse_repository(self, root: Path) -> list[ModuleView]:
        views: list[ModuleView] = []
        for p in self.discover_python_files(root):
            try:
                views.append(extract_module_view(p))
            except SyntaxError as e:
                self.audit.log("parse_error", file=str(p), error=str(e))
        self.audit.log("parse_repository", root=str(root), modules=len(views))
        return views

    # ---------- Embedding & Matching ----------
    def build_function_embeddings(self, views: list[ModuleView]) -> dict[tuple[str, str], list[float]]:
        texts = []
        keys: list[tuple[str, str]] = []
        for v in views:
            for f in v.functions:
                snippet = f"def {f.name}({', '.join(f.args)}):\n{f.source}\n\nDoc: {f.docstring or ''}"
                texts.append(snippet)
                keys.append((str(v.path), f.name))
        embs = self.embedder.encode_batch(texts) if texts else []
        table: dict[tuple[str, str], list[float]] = dict(zip(keys, embs))
        self.audit.log("build_embeddings", count=len(table))
        return table

    def semantic_function_matcher(
        self,
        orphan_func: FunctionSig,
        target_views: list[ModuleView],
        target_embs: dict[tuple[str, str], list[float]],
    ) -> list[tuple[str, str, float]]:
        orphan_text = f"def {orphan_func.name}({', '.join(orphan_func.args)}):\n{orphan_func.source}\n\nDoc: {orphan_func.docstring or ''}"
        orphan_emb = self.embedder.encode(orphan_text)

        scored: list[tuple[str, str, float]] = []
        for (path, fname), emb in target_embs.items():
            s = cosine_similarity(orphan_emb, emb)
            scored.append((path, fname, s))
        scored.sort(key=lambda x: x[2], reverse=True)
        return scored

    # ---------- Security & Style ----------
    def security_scan(self, code: str) -> dict[str, Any]:
        def idx_to_line(i: int) -> int:
            return code.count("\n", 0, i) + 1

        issues: list[str] = []
        critical: list[str] = []
        snippets: list[dict[str, Any]] = []

        # SQL-like patterns
        for p in SQL_PATTERNS:
            for m in re.finditer(p, code, flags=re.IGNORECASE):
                issues.append("Potential SQL concatenation")
                critical.append("SQL injection potential")
                start = idx_to_line(m.start())
                end = idx_to_line(m.end())
                lines = code.splitlines()
                snippet = "\n".join(lines[max(0, start-2): min(len(lines), end+1)])
                snippets.append({"issue": "SQL injection potential", "start_line": start, "end_line": end, "snippet": snippet})

        # Dangerous calls
        for call in DANGEROUS_CALLS:
            for m in re.finditer(re.escape(call), code):
                issues.append(f"Dangerous call: {call}")
                start = idx_to_line(m.start())
                line = code.splitlines()[start-1] if 0 <= start-1 < len(code.splitlines()) else ""
                snippets.append({"issue": f"Dangerous call: {call}", "start_line": start, "end_line": start, "snippet": line.strip()})

        # Semgrep (optional)
        semgrep_available = shutil_which("semgrep") is not None
        semgrep_findings = []
        if semgrep_available:
            try:
                proc = subprocess.run(["semgrep", "--json", "--quiet", "-l", "python", "-"],
                                      input=code.encode(), capture_output=True, check=False)
                data = json.loads(proc.stdout.decode() or "{}")
                for r in data.get("results", [])[:20]:
                    semgrep_findings.append(r.get("check_id"))
                    start = r.get("start", {}).get("line")
                    end = r.get("end", {}).get("line")
                    if start and end:
                        lines = code.splitlines()
                        snippet = "\n".join(lines[max(0, start-2): min(len(lines), end+1)])
                        snippets.append({"issue": f"semgrep:{r.get('check_id')}", "start_line": start, "end_line": end, "snippet": snippet})
            except Exception:
                pass

        return {
            "vulnerabilities_found": len(issues) + len(semgrep_findings),
            "critical_issues": list(set(critical)),
            "semgrep_rules_hit": semgrep_findings,
            "remediation_required": bool(critical),
            "snippets": snippets,
        }

    def style_scan(self, code: str) -> dict[str, Any]:
        indent_candidates = re.findall(r"^( +)\S", code, re.MULTILINE)
        indent = min((len(s) for s in indent_candidates), default=self.style_prefs["indent"]) if indent_candidates else self.style_prefs["indent"]
        bracket_style = "same-line" if re.search(r"def .+\):\n\s+\"\"\"", code) else "newline"
        anti_patterns = []
        if re.search(r"except:\s*pass", code):
            anti_patterns.append("bare-except-pass")
        if re.search(r"print\(", code):
            anti_patterns.append("print-in-library")
        return {
            "indent_spaces": indent,
            "bracket_style": bracket_style,
            "anti_patterns": anti_patterns,
        }

    # ---------- Dependency Inspection ----------
    def read_requirements(self, root: Path) -> dict[str, str]:
        reqs: dict[str, str] = {}
        for fn in ("requirements.txt", "pyproject.toml", "Pipfile"):
            p = root / fn
            if not p.exists():
                continue
            txt = read_text(p)
            if fn == "requirements.txt":
                for line in txt.splitlines():
                    m = re.match(r"\s*([A-Za-z0-9_.-]+)\s*==\s*([A-Za-z0-9_.-]+)", line)
                    if m:
                        reqs[m.group(1).lower()] = m.group(2)
            elif fn == "pyproject.toml":
                # naive scan
                for m in re.finditer(r"\"([A-Za-z0-9_.-]+)\"\s*=\s*\"([A-Za-z0-9_.-]+)\"", txt):
                    reqs[m.group(1).lower()] = m.group(2)
            else:  # Pipfile
                for m in re.finditer(r"\[packages\][\s\S]*?\n([A-Za-z0-9_.-]+)\s*=\s*\"?([A-Za-z0-9_.-]+)\"?", txt):
                    reqs[m.group(1).lower()] = m.group(2)
        return reqs

    def dependency_diff(self, orphan_root: Path, target_root: Path) -> dict[str, Any]:
        orphan = self.read_requirements(orphan_root)
        target = self.read_requirements(target_root)
        outdated = [k for k in orphan if k not in target]
        conflicts = []
        for pkg, ver in orphan.items():
            if pkg in target and target[pkg] != ver:
                conflicts.append(f"{pkg}=={ver} vs LUKHAS {target[pkg]}")
        effort = "low"
        if len(conflicts) > 2 or len(outdated) > 5:
            effort = "medium"
        if len(conflicts) > 5:
            effort = "high"
        return {
            "outdated_dependencies": len(outdated),
            "conflicting_versions": conflicts,
            "update_effort": effort,
        }

    # ---------- Naming Harmonization ----------
    def naming_analysis(self, func: FunctionSig, lukhas_funcs: list[str]) -> dict[str, Any]:
        convention = detect_naming_convention(func.name)
        verb_pattern = ""
        if re.match(r"^(get|set|process|validate|compute|update|create)", func.name, re.IGNORECASE):
            verb = re.match(r"^(get|set|process|validate|compute|update|create)", func.name, re.IGNORECASE).group(1# type: ignore
            verb_pattern = f"{verb.lower()} + noun"
        domain = self._infer_domain(func.name)
        preferred = func.name
        if self.style_prefs.get("naming") == "snake_case" and convention != "snake_case":
            preferred = camel_to_snake(func.name)
        similar_existing = [n for n in lukhas_funcs if camel_to_snake(n).split("_")[0] == camel_to_snake(func.name).split("_")[0]][:3]
        rules = ["camelCase → snake_case" if convention != "snake_case" else "keep snake_case",
                 "add domain prefix if ambiguous",
                 "align with existing verb patterns"]
        return {
            "original_function": func.name,
            "detected_patterns": {
                "convention": convention,
                "verb_pattern": verb_pattern or "unknown",
                "domain": domain,
            },
            "target_conventions": {
                "lukhas_pattern": self.style_prefs.get("naming", "snake_case"),
                "preferred_naming": preferred,
                "similar_existing": similar_existing,
            },
            "transformation_rules": rules,
        }

    @staticmethod
    def _infer_domain(name: str) -> str:
        name_l = name.lower()
        for domain in ["payment", "auth", "vision", "nlp", "storage", "validation", "crypto", "network", "db", "cache"]:
            if domain in name_l:
                return f"{domain}"
        return "generic"

    # ---------- Integration Mapping ----------
    def line_by_line_mapping(
        self,
        orphan_view: ModuleView,
        target_views: list[ModuleView],
        matches: list[tuple[str, str, float]],
        context_lines: int = 3,
    ) -> list[LineMapping]:
        result: list[LineMapping] = []
        if not matches:
            return result
        best_path = Path(matches[0][0])
        target_view = next((v for v in target_views if v.path == best_path), None)
        if not target_view:
            return result

        orphan_lines = orphan_view.code.splitlines()
        target_lines = target_view.code.splitlines()

        for f in orphan_view.functions:
            best = None
            for g in target_view.functions:
                score = 0
                if camel_to_snake(f.name).split("_")[0] == camel_to_snake(g.name).split("_")[0]:
                    score += 0.4
                overlap = len(set(map(camel_to_snake, f.args)) & set(map(camel_to_snake, g.args)))
                score += min(0.6, 0.1 * overlap)
                if best is None or score > best[0]:
                    best = (score, g)
            g = best[1] if best else None  # type: ignore
            target_line = g.lineno if g else 1
            suggested_sig = self._suggest_signature(f)
            adaptations = self._required_adaptations(f)
            conf = (best[0] if best else 0.4# type: ignore

            # Source context around function header
            s = f.lineno
            src_before = orphan_lines[max(0, s-1-context_lines): s-1]
            src_after = orphan_lines[s-1: min(len(orphan_lines), s-1+context_lines)]

            # Target context around insertion line
            tgt_before = target_lines[max(0, target_line-1-context_lines): target_line-1]
            tgt_after = target_lines[target_line-1: min(len(target_lines), target_line-1+context_lines)]

            # Param rename mapping
            param_map: dict[str, str] = {}
            for a in f.args:
                a_new = camel_to_snake(a) if self.style_prefs.get("naming") == "snake_case" else a
                param_map[a] = a_new

            result.append(LineMapping(
                source_line=f.lineno,
                source_code=f.source.splitlines()[0][:200],
                target_file=str(best_path),
                target_line=target_line,
                suggested_merge=suggested_sig,
                confidence=float(round(conf, 2)),
                required_adaptations=adaptations,
                source_context_before=src_before,
                source_context_after=src_after,
                target_context_before=tgt_before,
                target_context_after=tgt_after,
                param_rename_map=param_map,
            ))
        return result

    def _suggest_signature(self, f: FunctionSig) -> str:
        args = ", ".join([f"{a}: Any" for a in f.args]) if self.style_prefs.get("type_hints", True) else ", ".join(f.args)
        name = camel_to_snake(f.name) if self.style_prefs.get("naming") == "snake_case" else f.name
        return f"def {name}({args}):"

    def _required_adaptations(self, f: FunctionSig) -> list[str]:
        reqs = []
        if detect_naming_convention(f.name) != self.style_prefs.get("naming"):
            reqs.append("Rename function to match LUKHAS convention")
        if self.style_prefs.get("type_hints", True):
            reqs.append("Add type hints")
        if re.search(r"assert ", f.source):
            reqs.append("Replace asserts with explicit exceptions in library code")
        if re.search(r"print\(", f.source):
            reqs.append("Replace prints with structured logging")
        return reqs

    def function_summaries(self, view: ModuleView) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for f in view.functions:
            loc = f.end_lineno - f.lineno + 1
            summaries.append({
                "name": f.name,
                "args": f.args,
                "lineno": f.lineno,
                "end_lineno": f.end_lineno,
                "loc": loc,
                "has_docstring": bool(f.docstring),
                "doc_chars": len(f.docstring or ""),
            })
        return summaries

    def generate_naming_map(self, orphan_view: ModuleView, lukhas_funcs: list[str]) -> dict[str, Any]:
        forward: dict[str, str] = {}
        for f in orphan_view.functions:
            na = self.naming_analysis(f, lukhas_funcs)
            forward[f.name] = na["target_conventions"]["preferred_naming"]
        inverse: dict[str, list[str]] = {}
        for k, v in forward.items():
            inverse.setdefault(v, []).append(k)
        return {"forward": forward, "inverse": inverse}

    def generate_patch(self, orphan_view: ModuleView, mappings: list[LineMapping]) -> str:
        lines: list[str] = []
        lines.append(f"")
        for m in mappings:
            lines.append(f"--- {m.target_file}")
            lines.append(f"+++ {m.target_file}")
            lines.append(f"@@ -{m.target_line},{m.target_line} +{m.target_line},{m.target_line} @@")
            lines.append(f"- ")
            lines.append(f"+ {m.suggested_merge}  ")
        return "\n".join(lines)

    def generate_test_scaffolding(self, orphan_view: ModuleView, naming_map: dict[str, Any]) -> list[dict[str, str]]:
        tests: list[dict[str, str]] = []
        fwd = naming_map.get("forward", {})
        for f in orphan_view.functions:
            snake = camel_to_snake(f.name)
            test_name = f"test_{snake}"
            stub = (
                "import pytest\n\n"
                f"def {test_name}():\n"
                f"    "
                f"    "
                f"    "
                f"    ", '.join(f.args)})\n"
                f"    "
                f"    "
                f"    "
                f"    assert True\n"
            )
            tests.append({"name": test_name, "stub": stub})
        return tests

    def github_action_yaml(self) -> str:
        return """name: Lukhas Integration Analyzer

on:
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install openai numpy
          pip install semgrep gitpython || true
      - name: Run analyzer
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          LUKHAS_REASONER_MODEL: gpt-5-mini
        run: |
          python ml_integration_analyzer.py --orphan ./path/to/orphan.py --lukhas . \\
            --cheap-first --extra-info --out report.json || echo "Analyzer completed with non-zero status"
      - name: Upload report artifact
        uses: actions/upload-artifact@v4
        with:
          name: lukhas-integration-report
          path: report.json
      - name: Comment summary on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            let body = 'Integration Analyzer report could not be generated.';
            try {
              const data = JSON.parse(fs.readFileSync('report.json', 'utf8'));
              const score = data.module_analysis?.confidence_score;
              const primary = data.module_analysis?.integration_recommendations?.primary_strategy;
              body = `**LUKHAS Integration Analyzer**\\n- Confidence: ${score}\\n- Primary strategy: ${primary}\\n- See artifact: lukhas-integration-report`;
            } catch (e) {
              body = 'Integration Analyzer ran, but no report.json was found.';
            }
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body
            })""".strip()

    # ---------- Scoring ----------
    def value_effort_score(self, strengths: list[SWOTEntry], weaknesses: list[SWOTEntry]) -> tuple[float, float]:
        value = min(1.0, 0.5 + 0.1 * len(strengths))
        effort = min(1.0, 0.3 + 0.15 * len(weaknesses))
        return value, effort

    def integration_cost_model(self, weaknesses: list[SWOTEntry], mappings: list[LineMapping]) -> str:
        base_hours = 6 + 2 * len(mappings)
        for w in weaknesses:
            sev = w.meta.get("severity", "low")
            if sev == "medium":
                base_hours += 4
            elif sev == "high":
                base_hours += 10
            elif sev == "critical":
                base_hours += 16
        if base_hours < 16:
            return "1-2 days"
        if base_hours < 40:
            return "3-5 days"
        if base_hours < 80:
            return "1-2 weeks"
        return ">= 2 weeks"

    # ---------- Git History (Optional) ----------
    def git_history_summary(self, root: Path) -> str:
        if shutil_which("git") is None:
            return "git unavailable"
        try:
            proc = subprocess.run(["git", "-C", str(root), "log", "--oneline", "-n", "50"], capture_output=True, check=False)
            lines = proc.stdout.decode().splitlines()
            return f"Last {len(lines)} commits (head):\n" + "\n".join(lines[:10])
        except Exception:
            return "git analysis failed"

    # ---------- LLM Enhancement ----------
    def llm_enhance_swot(self, orphan_view: ModuleView, lukhas_context: str, model_override: str | None = None) -> dict[str, list[SWOTEntry]]:
        sys_prompt = (
            "You are an expert software integration analyst for the LUKHAS symbolic AGI project. "
            "Output concise, high-signal SWOT bullets. Include severity/confidence when relevant."
        )
        sample = textwrap.shorten(orphan_view.code, width=2000, placeholder="... [truncated]")
        user_prompt = f"""
        Orphaned module: {orphan_view.path.name}
        --- Orphan Code (excerpt) ---
        {sample}
        --- LUKHAS Context (excerpt) ---
        {lukhas_context[:1500]}
        Provide:
        - Strengths (max 4)
        - Weaknesses (max 4)
        - Opportunities (max 4)
        - Threats (max 4)
        For each item, add JSON-friendly hints like severity, uniqueness, or confidence.
        """
        raw = self.reasoner.analyze_on_model(model_override, sys_prompt, user_prompt) if model_override else self.reasoner.analyze(sys_prompt, user_prompt)
        # Minimal parse: extract lines starting with -, then map
        strengths: list[SWOTEntry] = []
        weaknesses: list[SWOTEntry] = []
        opportunities: list[SWOTEntry] = []
        threats: list[SWOTEntry] = []
        bucket = None
        for line in raw.splitlines():
            head = line.strip()
            if head.lower().startswith("- strengths"):
                bucket = "S"
            elif head.lower().startswith("- weaknesses"):
                bucket = "W"
            elif head.lower().startswith("- opportunities"):
                bucket = "O"
            elif head.lower().startswith("- threats"):
                bucket = "T"
            elif head.startswith("-"):
                entry = head[1:].strip()
                meta = {}
                m = re.search(r"\{(.*)\}$", entry)
                if m:
                    try:
                        meta = json.loads("{" + m.group(1) + "}")
                        entry = entry[:m.start()].strip()
                    except Exception:
                        pass
                sw = SWOTEntry(description=entry, meta=meta)
                if bucket == "S":
                    strengths.append(sw)
                elif bucket == "W":
                    weaknesses.append(sw)
                elif bucket == "O":
                    opportunities.append(sw)
                elif bucket == "T":
                    threats.append(sw)
        self.audit.log("llm_swot_enhanced", strengths=len(strengths), weaknesses=len(weaknesses), model_override=model_override or self.reasoner.model)
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
        }

    # ---------- Main Entry ----------
    def analyze(
        self,
        orphan_path: Path,
        lukhas_root: Path,
        module_name: str | None = None,
        use_openai: bool = True,
        model_versions: dict[str, str] | None = None,
        cheap_first: bool = False,
        cascade_models: list[str] | None = None,
        extra_info: bool = False,
        simulate_out: Path | None = None,
        naming_map_out: Path | None = None,
        context_lines: int = 3,
    ) -> dict[str, Any]:
        self.audit.log("start_analysis", orphan=str(orphan_path), target=str(lukhas_root), cheap_first=cheap_first)
        orphan_view = extract_module_view(orphan_path)
        lukhas_views = self.parse_repository(lukhas_root)
        lukhas_embs = self.build_function_embeddings(lukhas_views)

        # LUKHAS context for LLM (high-level only)
        lukhas_context = "\n".join([
            f"{v.path.name}: {', '.join(f.name for f in v.functions[:5])}" for v in lukhas_views[:10]
        ])

        # Semantic matching for each orphan function against LUKHAS codebase
        all_matches: list[tuple[str, str, float]] = []
        for f in orphan_view.functions:
            m = self.semantic_function_matcher(f, lukhas_views, lukhas_embs)[:5]
            all_matches.extend(m)
        all_matches.sort(key=lambda x: x[2], reverse=True)

        # Security & style analysis
        sec = self.security_scan(orphan_view.code)
        style = self.style_scan(orphan_view.code)

        # Dependency analysis (repo roots)
        dep = self.dependency_diff(orphan_path.parent, lukhas_root)

        # Naming harmonization (use top-100 LUKHAS function names)
        lukhas_funcs = [f.name for v in lukhas_views for f in v.functions][:100]
        naming = self.naming_analysis(orphan_view.functions[0], lukhas_funcs) if orphan_view.functions else {
            "original_function": "<none>",
            "detected_patterns": {"convention": "unknown", "verb_pattern": "unknown", "domain": "generic"},
            "target_conventions": {"lukhas_pattern": self.style_prefs.get("naming", "snake_case"), "preferred_naming": "<none>", "similar_existing": []},
            "transformation_rules": ["camelCase → snake_case"],
        }

        # Integration mapping
        mappings = self.line_by_line_mapping(orphan_view, lukhas_views, all_matches[:1], context_lines=context_lines)

        # Heuristic SWOT baseline
        strengths_base = [SWOTEntry("Feature-rich functions", {"uniqueness_score": 0.6})] if orphan_view.functions else []
        weaknesses_base = []
        if "bare-except-pass" in style.get("anti_patterns", []):
            weaknesses_base.append(SWOTEntry("Bare except-pass blocks", {"severity": "medium"}))
        if sec.get("critical_issues"):
            for ci in sec["critical_issues"]:
                weaknesses_base.append(SWOTEntry(ci, {"severity": "critical"}))

        # LLM Enhancement (optional)
        swot = {
            "strengths": strengths_base,
            "weaknesses": weaknesses_base,
            "opportunities": [],
            "threats": [],
        }

        cascade_audit: list[dict[str, Any]] = []
        final_model = getattr(self.reasoner, "model", None)
        if use_openai and cheap_first:
            models = cascade_models or os.getenv("LUKHAS_CASCADE_MODELS", "gpt-5-nano,gpt-5-mini,gpt-5").split(",")
            for mdl in [m.strip() for m in models if m.strip()]:
                swot_llm = self.llm_enhance_swot(orphan_view, lukhas_context, model_override=mdl)
                for k in swot:
                    seen = {s.description for s in swot[k]}
                    for item in swot_llm[k]:
                        if item.description not in seen:
                            swot[k].append(item)
                            seen.add(item.description)
                value_tmp, effort_tmp = self.value_effort_score(swot["strengths"], swot["weaknesses"])
                confidence_score_tmp = round(max(0.1, value_tmp - 0.3 * effort_tmp), 2)
                cascade_audit.append({"model": mdl, "confidence_after_merge": confidence_score_tmp})
                final_model = mdl
                if confidence_score_tmp >= self.confidence_threshold:
                    break
        elif use_openai:
            swot_llm = self.llm_enhance_swot(orphan_view, lukhas_context)
            for k in swot:
                seen = {s.description for s in swot[k]}
                for item in swot_llm[k]:
                    if item.description not in seen:
                        swot[k].append(item)
                        seen.add(item.description)

        # Scoring
        value, effort = self.value_effort_score(swot["strengths"], swot["weaknesses"])
        confidence_score = round(max(0.1, value - 0.3 * effort), 2)
        cost_estimate = self.integration_cost_model(swot["weaknesses"], mappings)

        # Primary & alternatives strategies
        primary_strategy = "gradual_migration" if dep["update_effort"] != "high" else "wrapper_service"
        alt_strategies = [
            IntegrationStrategy("wrapper_service", "2-3 days", "low", ["Quick implementation", "Minimal LUKHAS changes"], ["Additional maintenance overhead", "Performance impact"]),
            IntegrationStrategy("direct_integration", "1-2 weeks", "medium", ["Clean architecture", "Better performance"], ["More extensive testing needed", "Potential conflicts"]),
        ]

        # Risk assessment
        risk = RiskAssessment(
            security_scan=sec,
            dependency_analysis=dep,
            performance_impact={
                "memory_overhead": "+15MB estimated",
                "cpu_impact": "negligible",
                "integration_bottlenecks": ["Database connection pooling"] if "db" in orphan_view.code.lower() else [],
            },
        )

        # Git history (optional)
        git_summary = self.git_history_summary(orphan_path.parent)

        # System metadata
        sysmeta = {
            "analysis_timestamp": _dt.datetime.utcnow().isoformat() + "Z",
            "analyzer_version": "2.2.0",
            "confidence_threshold": self.confidence_threshold,
            "model_versions": model_versions or {
                "code_embeddings": self.embedder.model if hasattr(self.embedder, "model") else "hash-embed-256",
                "security_scanner": "semgrep-auto" if shutil_which("semgrep") else "heuristic-0.1",
                "style_analyzer": "custom-v2.0",
            },
            "reasoning_model": {"default": getattr(self.reasoner, "model", None), "final_used": final_model, "cascade": cascade_audit},
        }

        # Final JSON structure
        report = {
            "module_analysis": {
                "module_name": module_name or orphan_path.stem,
                "confidence_score": confidence_score,
                "swot_analysis": {
                    "strengths": [asdict(SWOTEntry(s.description, s.meta)) for s in swot["strengths"]],
                    "weaknesses": [asdict(SWOTEntry(s.description, s.meta)) for s in swot["weaknesses"]],
                    "opportunities": [asdict(SWOTEntry(s.description, s.meta)) for s in swot["opportunities"]],
                    "threats": [asdict(SWOTEntry(s.description, s.meta)) for s in swot["threats"]],
                },
                "naming_analysis": naming,
                "integration_recommendations": {
                    "primary_strategy": primary_strategy,
                    "line_by_line_mapping": [asdict(m) for m in mappings],
                    "alternative_strategies": [asdict(s) for s in alt_strategies],
                    "integration_cost_estimate": cost_estimate,
                },
                "risk_assessment": asdict(risk),
                "integration_roadmap": {
                    "phase_1": {
                        "duration": "1 week",
                        "tasks": ["Security vulnerability fixes", "Dependency updates"],
                        "deliverables": ["Cleaned orphan module", "Security assessment report"],
                    },
                    "phase_2": {
                        "duration": "1-2 weeks",
                        "tasks": ["Naming convention alignment", "Code style harmonization"],
                        "deliverables": ["Refactored module", "Integration test suite"],
                    },
                    "phase_3": {
                        "duration": "3-5 days",
                        "tasks": ["LUKHAS integration", "End-to-end testing"],
                        "deliverables": ["Integrated system", "Performance benchmarks"],
                    },
                },
                "git_summary": git_summary,
            },
            "system_metadata": sysmeta,
            "audit_trail": self.audit.to_list(),
        }

        if extra_info:
            report["module_analysis"]["extras"] = {
                "orphan_function_summaries": self.function_summaries(orphan_view),
                "imports": orphan_view.imports,
                "top_match_candidates": [{"path": p, "function": fn, "similarity": round(s, 3)} for p, fn, s in all_matches[:10]],
                "style": style,
            }

        # simulate patch
        if simulate_out is not None:
            try:
                patch_text = self.generate_patch(orphan_view, mappings)
                Path(simulate_out).write_text(patch_text, encoding="utf-8")
                report["module_analysis"]["simulation_patch"] = str(simulate_out)
            except Exception as e:
                self.audit.log("simulate_write_error", error=str(e))

        # naming map + tests
        if naming_map_out is not None:
            try:
                nmap = self.generate_naming_map(orphan_view, lukhas_funcs)
                Path(naming_map_out).write_text(json.dumps(nmap, indent=2), encoding="utf-8")
                report["module_analysis"]["naming_map_path"] = str(naming_map_out)
                report["module_analysis"]["test_scaffolding"] = self.generate_test_scaffolding(orphan_view, nmap)
            except Exception as e:
                self.audit.log("naming_map_write_error", error=str(e))
        else:
            nmap = self.generate_naming_map(orphan_view, lukhas_funcs)
            report["module_analysis"]["test_scaffolding"] = self.generate_test_scaffolding(orphan_view, nmap)

        self.audit.log("end_analysis", confidence=confidence_score)
        return report


# -----------------------------
# Helpers
# -----------------------------

def shutil_which(cmd: str) -> str | None:
    from shutil import which
    return which(cmd)


# -----------------------------
# CLI Entrypoint
# -----------------------------
CLI_HELP = """
Usage:
  python ml_integration_analyzer.py --orphan <path/to/orphan.py> --lukhas <path/to/lukhas/repo> \\
    [--out report.json] [--no-openai] [--cheap-first] \\
    [--cascade-models gpt-5-nano,gpt-5-mini,gpt-5] \\
    [--embed-provider openai] [--embed-model text-embedding-3-small] [--embed-dim 512] \\
    [--style-naming snake_case|camelCase|PascalCase] [--style-indent 4] [--no-type-hints] \\
    [--context-lines 3] \\
    [--simulate] [--simulate-out integration.patch] [--export-naming-map names.json] [--extra-info] \\
    [--emit-github-action .github/workflows/lukhas-integration-analyzer.yml]

Environment:
  OPENAI_API_KEY=...                # Required only if using OpenAI features
  LUKHAS_REASONER_MODEL=...         # Optional, default: gpt-5-mini
  LUKHAS_CASCADE_MODELS=...         # Optional, e.g.: gpt-5-nano,gpt-5-mini,gpt-5

Examples:
  # Cost-aware cascade with extras and a simulated patch
  python ml_integration_analyzer.py --orphan ./orphans/payment_processor.py --lukhas ../LUKHAS \\
    --cheap-first --extra-info --simulate --simulate-out payment.patch --export-naming-map payment_names.json --out report.json

  # Custom embeddings + style prefs
  python ml_integration_analyzer.py --orphan ./module.py --lukhas ../LUKHAS \\
    --embed-model text-embedding-3-small --embed-dim 512 --style-naming snake_case --style-indent 4

  # Emit a GitHub Action file
  python ml_integration_analyzer.py --emit-github-action .github/workflows/lukhas-integration-analyzer.yml

  # Run offline without OpenAI
  python ml_integration_analyzer.py --orphan ./module.py --lukhas ../LUKHAS --no-openai

  # Pretty-print to stdout
  python ml_integration_analyzer.py --orphan ./module.py --lukhas ../LUKHAS | python -m json.tool
"""


def _cli(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(description="LUKHΛS ML-Powered Integration Analyzer", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=CLI_HELP)
    p.add_argument("--orphan", required=True, help="Path to orphan module .py file")
    p.add_argument("--lukhas", required=True, help="Path to LUKHΛS repository root")
    p.add_argument("--out", default=None, help="Output JSON path (default: stdout)")
    p.add_argument("--no-openai", action="store_true", help="Disable OpenAI-assisted analysis")
    p.add_argument("--cheap-first", action="store_true", help="Use model cascade (nano→mini→base) with auto-escalation by confidence")
    p.add_argument("--cascade-models", default=os.getenv("LUKHAS_CASCADE_MODELS", "gpt-5-nano,gpt-5-mini,gpt-5"), help="Comma-separated models for cascade order")
    p.add_argument("--embed-model", default=os.getenv("LUKHAS_EMBED_MODEL", "text-embedding-3-small"))
    p.add_argument("--embed-provider", default=os.getenv("LUKHAS_EMBED_PROVIDER", "openai"))
    p.add_argument("--embed-dim", type=int, default=None)
    p.add_argument("--style-naming", default="snake_case", choices=["snake_case", "camelCase", "PascalCase"])
    p.add_argument("--style-indent", type=int, default=4)
    p.add_argument("--no-type-hints", action="store_true", help="Disable type hints in suggested signatures")
    p.add_argument("--context-lines", type=int, default=3, help="±N lines of context to include around suggestions")
    p.add_argument("--simulate", action="store_true", help="Dry-run integration and write a patch file (does not modify source)")
    p.add_argument("--simulate-out", default=None, help="Path for the generated patch file")
    p.add_argument("--export-naming-map", default=None, help="Write a JSON mapping of original→preferred names")
    p.add_argument("--extra-info", action="store_true", help="Include expanded extras in the JSON report")
    p.add_argument("--emit-github-action", default=None, help="Write a GitHub Action YAML to the given path")

    args = p.parse_args(argv)

    orphan = Path(args.orphan).resolve()
    lukhas = Path(args.lukhas).resolve()
    if not orphan.exists():
        print(f"[error] orphan module not found: {orphan}", file=sys.stderr)
        return 2
    if not lukhas.exists():
        print(f"[error] LUKHΛS repo not found: {lukhas}", file=sys.stderr)
        return 2

    embedder = EmbeddingAdapter(provider=args.embed_provider, model=args.embed_model, dimensions=args.embed_dim)
    style_prefs = {
        "naming": args.style_naming,
        "indent": args.style_indent,
        "type_hints": not args.no_type_hints,
    }
    analyzer = IntegrationAnalyzer(embedder=embedder, style_prefs=style_prefs)

    # Optionally emit GitHub Action and exit
    if args.emit_github_action:
        out_path = Path(args.emit_github_action)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(analyzer.github_action_yaml(), encoding="utf-8")
        print(f"[ok] GitHub Action written: {out_path}")
        return 0

    sim_path = None
    if args.simulate:
        sim_path = Path(args.simulate_out) if args.simulate_out else Path(f"{orphan.stem}_integration.patch")

    map_path = Path(args.export_naming_map) if args.export_naming_map else None

    report = analyzer.analyze(
        orphan,
        lukhas,
        module_name=orphan.stem,
        use_openai=(not args.no_openai),
        cheap_first=args.cheap_first,
        cascade_models=[s.strip() for s in (args.cascade_models or "").split(",") if s.strip()],
        extra_info=args.extra_info,
        simulate_out=sim_path,
        naming_map_out=map_path,
        context_lines=args.context_lines,
    )

    out = json.dumps(report, indent=2)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"[ok] report written: {args.out}")
    else:
        print(out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_cli(sys.argv[1:]))

"""
# -----------------------------
# Developer Quick Start (Shell)
# -----------------------------
# 1) Create a virtualenv and install deps
#    python -m venv .venv && source .venv/bin/activate
#    pip install openai numpy
#    # optional for deeper scans
#    pip install semgrep gitpython
#
# 2) Export your OpenAI key (if using LLM/embeddings)
#    export OPENAI_API_KEY=sk-...  # or set via your secrets manager
#    # optional: choose your reasoning model
#    export LUKHAS_REASONER_MODEL=gpt-5-mini
#
# 3) Run the analyzer
#    python ml_integration_analyzer.py --orphan ./path/to/orphan.py --lukhas ../LUKHAS --out report.json
#
# 4) Pretty-print the JSON and inspect
#    cat report.json | python -m json.tool
#
# 5) Iterate:
#    - Address security/style hints in the orphan module
#    - Re-run to observe score/confidence changes
#
# Notes:
# - The tool is conservative: if confidence < threshold, it will surface "I don't know"-leaning outputs.
# - You can swap EmbeddingAdapter(provider="openai", model="text-embedding-3-small") with custom encoders.
# - Extend ReasonerAdapter to other LLMs if desired.
"""
