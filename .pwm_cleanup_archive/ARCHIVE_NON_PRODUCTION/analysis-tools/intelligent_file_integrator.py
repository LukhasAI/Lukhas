#!/usr/bin/env python3
"""
Intelligent File Integration System for LUKHAS AGI

This system analyzes isolated files and matches them with the working system
using semantic analysis, pattern matching, and confidence scoring.

Author: LUKHAS Integration Team
Created: 2024-07-31
"""

import argparse
import ast
import difflib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class CodeSignature:
    """Represents the semantic signature of a code element"""

    name: str
    type: str  # 'class', 'function', 'method'
    parameters: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    imports: Set[str] = field(default_factory=set)
    calls: Set[str] = field(default_factory=set)
    domain: Optional[str] = None  # 'voice', 'memory', 'quantum', etc.
    file_path: str = ""
    line_number: int = 0


@dataclass
class IntegrationMatch:
    """Represents a potential integration match"""

    isolated_file: str
    target_file: str
    isolated_signature: CodeSignature
    target_signature: CodeSignature
    confidence_score: float
    match_reasons: Dict[str, float] = field(default_factory=dict)
    integration_actions: List[str] = field(default_factory=list)


class CodeAnalyzer(ast.NodeVisitor):
    """Extracts semantic signatures from Python AST"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.signatures: List[CodeSignature] = []
        self.current_class = None
        self.imports: Set[str] = set()
        self.domain = self._infer_domain(file_path)

    def _infer_domain(self, file_path: str) -> Optional[str]:
        """Infer domain from file path"""
        path_lower = file_path.lower()
        domains = {
            "voice": ["voice", "audio", "speech", "vocal"],
            "memory": ["memory", "mem", "recall", "storage"],
            "quantum": ["quantum", "quant", "superposition"],
            "consciousness": ["consciousness", "aware", "conscious"],
            "emotion": ["emotion", "feel", "mood", "affect"],
            "identity": ["identity", "auth", "user", "persona"],
            "reasoning": ["reasoning", "logic", "inference"],
            "ethics": ["ethics", "moral", "policy"],
            "learning": ["learning", "learn", "train"],
            "creativity": ["creativity", "creative", "dream", "imagine"],
            "bio": ["bio", "biological", "organic"],
            "orchestration": ["orchestration", "orchestr", "coordinate"],
        }

        for domain, keywords in domains.items():
            if any(keyword in path_lower for keyword in keywords):
                return domain
        return None

    def visit_Import(self, node):
        """Extract import statements"""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Extract from-import statements"""
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Extract class definitions"""
        signature = CodeSignature(
            name=node.name,
            type="class",
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node),
            domain=self.domain,
            file_path=self.file_path,
            line_number=node.lineno,
            imports=self.imports.copy(),
        )

        # Extract base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                signature.parameters.append(f"base:{base.id}")

        self.signatures.append(signature)

        # Visit methods within class
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node):
        """Extract function/method definitions"""
        signature = CodeSignature(
            name=node.name,
            type="method" if self.current_class else "function",
            parameters=[arg.arg for arg in node.args.args],
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            docstring=ast.get_docstring(node),
            domain=self.domain,
            file_path=self.file_path,
            line_number=node.lineno,
            imports=self.imports.copy(),
        )

        # Extract return type annotation if available
        if node.returns:
            signature.returns = (
                ast.unparse(node.returns)
                if hasattr(ast, "unparse")
                else str(node.returns)
            )

        # Extract function calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                signature.calls.add(child.func.id)

        self.signatures.append(signature)
        self.generic_visit(node)

    def _get_decorator_name(self, decorator):
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id if isinstance(decorator.value, ast.Name) else '?'}.{decorator.attr}"
        return str(decorator)


class BrandingNormalizer:
    """Normalizes old branding to new branding"""

    BRANDING_MAP = {
        "lucas": "lukhas",
        "Lucas": "LUKHAS",
        "LUCAS": "LUKHAS",
        "LucAS": "LUKHAS",
        "Lucλs": "LUKHAS",
        "LUCΛS": "LUKHAS",
    }

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Normalize branding in text"""
        result = text
        for old, new in cls.BRANDING_MAP.items():
            result = result.replace(old, new)
        return result

    @classmethod
    def normalize_path(cls, path: str) -> str:
        """Normalize branding in file paths"""
        return cls.normalize_text(path)


class SemanticMatcher:
    """Matches code elements using semantic analysis"""

    def __init__(self):
        self.domain_weights = {
            "same_domain": 0.3,
            "name_similarity": 0.25,
            "signature_match": 0.2,
            "import_overlap": 0.15,
            "structural_match": 0.1,
        }

    def calculate_match_score(
        self, sig1: CodeSignature, sig2: CodeSignature
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate overall match score between two signatures"""
        scores = {}

        # Domain matching
        if sig1.domain and sig2.domain:
            scores["domain"] = 1.0 if sig1.domain == sig2.domain else 0.3
        else:
            scores["domain"] = 0.5

        # Name similarity (with normalization)
        name1 = BrandingNormalizer.normalize_text(sig1.name.lower())
        name2 = BrandingNormalizer.normalize_text(sig2.name.lower())
        scores["name"] = difflib.SequenceMatcher(None, name1, name2).ratio()

        # Also check for semantic name similarity
        if self._are_names_semantically_similar(name1, name2):
            scores["name"] = max(scores["name"], 0.8)

        # Type matching
        scores["type"] = 1.0 if sig1.type == sig2.type else 0.0

        # Parameter similarity
        if sig1.type in ["function", "method"] and sig2.type in ["function", "method"]:
            param_score = self._compare_parameters(sig1.parameters, sig2.parameters)
            scores["parameters"] = param_score
        else:
            scores["parameters"] = 0.5

        # Import overlap
        if sig1.imports and sig2.imports:
            normalized_imports1 = {
                BrandingNormalizer.normalize_text(imp) for imp in sig1.imports
            }
            normalized_imports2 = {
                BrandingNormalizer.normalize_text(imp) for imp in sig2.imports
            }

            overlap = len(normalized_imports1 & normalized_imports2)
            total = len(normalized_imports1 | normalized_imports2)
            scores["imports"] = overlap / total if total > 0 else 0.0
        else:
            scores["imports"] = 0.5

        # Docstring similarity
        if sig1.docstring and sig2.docstring:
            doc1 = BrandingNormalizer.normalize_text(sig1.docstring.lower())
            doc2 = BrandingNormalizer.normalize_text(sig2.docstring.lower())
            scores["docstring"] = difflib.SequenceMatcher(None, doc1, doc2).ratio()
        else:
            scores["docstring"] = 0.5

        # Calculate weighted score
        weights = {
            "domain": 0.3,
            "name": 0.25,
            "type": 0.15,
            "parameters": 0.15,
            "imports": 0.1,
            "docstring": 0.05,
        }

        total_score = sum(
            scores.get(key, 0) * weight for key, weight in weights.items()
        )

        return total_score, scores

    def _are_names_semantically_similar(self, name1: str, name2: str) -> bool:
        """Check if names are semantically similar"""
        # Common patterns
        patterns = [
            ("manager", "orchestrator"),
            ("engine", "processor"),
            ("handler", "manager"),
            ("adapter", "integrator"),
            ("factory", "creator"),
            ("builder", "constructor"),
            ("validator", "checker"),
            ("analyzer", "inspector"),
            ("hub", "center"),
            ("core", "main"),
        ]

        for p1, p2 in patterns:
            if (p1 in name1 and p2 in name2) or (p2 in name1 and p1 in name2):
                return True

        return False

    def _compare_parameters(self, params1: List[str], params2: List[str]) -> float:
        """Compare parameter lists"""
        if len(params1) == 0 and len(params2) == 0:
            return 1.0
        if len(params1) == 0 or len(params2) == 0:
            return 0.0

        # Consider order and names
        if params1 == params2:
            return 1.0

        # Check if same length
        if len(params1) == len(params2):
            return 0.7

        # Partial match based on length difference
        length_diff = abs(len(params1) - len(params2))
        max_length = max(len(params1), len(params2))

        return max(0.0, 1.0 - (length_diff / max_length))


class IntelligentFileIntegrator:
    """Main integration system"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.matcher = SemanticMatcher()
        self.working_signatures: List[CodeSignature] = []
        self.isolated_signatures: List[CodeSignature] = []
        self.integration_matches: List[IntegrationMatch] = []

        # From connectivity analysis
        self.connected_files: Set[str] = set()
        self.isolated_files: Set[str] = set()

    def load_connectivity_data(self, connectivity_file: str):
        """Load connectivity analysis results"""
        with open(connectivity_file) as f:
            data = json.load(f)

        # Extract connected and isolated files
        for file_path, info in data.get("file_analysis", {}).items():
            if info.get("total_connections", 0) > 0:
                self.connected_files.add(file_path)
            else:
                self.isolated_files.add(file_path)

    def analyze_files(self):
        """Analyze all Python files in the repository"""
        print("🔍 Analyzing connected files...")
        self._analyze_file_set(self.connected_files, self.working_signatures)

        print("🔍 Analyzing isolated files...")
        self._analyze_file_set(self.isolated_files, self.isolated_signatures)

        print(f"✅ Found {len(self.working_signatures)} signatures in connected files")
        print(f"✅ Found {len(self.isolated_signatures)} signatures in isolated files")

    def _analyze_file_set(
        self, file_set: Set[str], signature_list: List[CodeSignature]
    ):
        """Analyze a set of files and extract signatures"""
        for file_path in file_set:
            if file_path.endswith(".py"):
                full_path = self.repo_path / file_path
                if full_path.exists():
                    try:
                        with open(full_path, encoding="utf-8") as f:
                            content = f.read()

                        tree = ast.parse(content)
                        analyzer = CodeAnalyzer(file_path)
                        analyzer.visit(tree)
                        signature_list.extend(analyzer.signatures)
                    except Exception as e:
                        print(f"⚠️  Error analyzing {file_path}: {e}")

    def find_integration_matches(self, min_confidence: float = 0.6):
        """Find potential integration matches"""
        print("\n🧮 Finding integration matches...")

        total_comparisons = len(self.isolated_signatures) * len(self.working_signatures)
        comparisons_done = 0

        for isolated_sig in self.isolated_signatures:
            best_matches = []

            for working_sig in self.working_signatures:
                comparisons_done += 1
                if comparisons_done % 10000 == 0:
                    progress = (comparisons_done / total_comparisons) * 100
                    print(f"  Progress: {progress:.1f}%")

                score, reasons = self.matcher.calculate_match_score(
                    isolated_sig, working_sig
                )

                if score >= min_confidence:
                    match = IntegrationMatch(
                        isolated_file=isolated_sig.file_path,
                        target_file=working_sig.file_path,
                        isolated_signature=isolated_sig,
                        target_signature=working_sig,
                        confidence_score=score,
                        match_reasons=reasons,
                        integration_actions=self._generate_integration_actions(
                            isolated_sig, working_sig, score
                        ),
                    )
                    best_matches.append(match)

            # Keep only top matches for each isolated signature
            best_matches.sort(key=lambda m: m.confidence_score, reverse=True)
            self.integration_matches.extend(best_matches[:3])  # Top 3 matches

    def _generate_integration_actions(
        self, isolated_sig: CodeSignature, target_sig: CodeSignature, score: float
    ) -> List[str]:
        """Generate specific integration actions"""
        actions = []

        # High confidence - direct integration
        if score >= 0.85:
            if isolated_sig.type == "class" and target_sig.type == "class":
                actions.append(
                    f"Merge class {isolated_sig.name} into {target_sig.name}"
                )
                actions.append("Consolidate duplicate methods")
                actions.append("Merge class attributes")
            elif isolated_sig.type in ["function", "method"]:
                actions.append(
                    f"Move {isolated_sig.type} {isolated_sig.name} to {target_sig.file_path}"
                )
                actions.append("Update function signature if needed")

        # Always needed
        actions.append("Update import statements: lucas/Lucas -> lukhas/LUKHAS")
        actions.append("Update any string references to old branding")

        # Domain-specific actions
        if isolated_sig.domain == target_sig.domain:
            actions.append(f"Integrate with {isolated_sig.domain} system architecture")

        return actions

    def generate_integration_report(self, output_file: str = "integration_plan.json"):
        """Generate detailed integration report"""
        print("\n📊 Generating integration report...")

        # Group matches by confidence level
        high_confidence = [
            m for m in self.integration_matches if m.confidence_score >= 0.85
        ]
        medium_confidence = [
            m for m in self.integration_matches if 0.7 <= m.confidence_score < 0.85
        ]
        low_confidence = [
            m for m in self.integration_matches if 0.6 <= m.confidence_score < 0.7
        ]

        # Group by domain
        domain_groups = defaultdict(list)
        for match in self.integration_matches:
            domain = match.isolated_signature.domain or "unknown"
            domain_groups[domain].append(match)

        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_isolated_files": len(self.isolated_files),
                "total_connected_files": len(self.connected_files),
                "total_matches_found": len(self.integration_matches),
                "isolated_signatures_analyzed": len(self.isolated_signatures),
                "working_signatures_analyzed": len(self.working_signatures),
            },
            "confidence_summary": {
                "high_confidence_matches": len(high_confidence),
                "medium_confidence_matches": len(medium_confidence),
                "low_confidence_matches": len(low_confidence),
            },
            "domain_summary": {
                domain: len(matches) for domain, matches in domain_groups.items()
            },
            "high_confidence_integrations": self._format_matches(
                high_confidence[:20]
            ),  # Top 20
            "medium_confidence_suggestions": self._format_matches(
                medium_confidence[:20]
            ),
            "branding_updates_needed": self._find_branding_updates(),
        }

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        # Also generate human-readable summary
        self._print_summary(report)

        return report

    def _format_matches(self, matches: List[IntegrationMatch]) -> List[Dict]:
        """Format matches for report"""
        formatted = []

        for match in matches:
            formatted.append(
                {
                    "isolated_file": match.isolated_file,
                    "target_file": match.target_file,
                    "isolated_element": {
                        "name": match.isolated_signature.name,
                        "type": match.isolated_signature.type,
                        "line": match.isolated_signature.line_number,
                    },
                    "target_element": {
                        "name": match.target_signature.name,
                        "type": match.target_signature.type,
                        "line": match.target_signature.line_number,
                    },
                    "confidence_score": round(match.confidence_score, 3),
                    "match_reasons": {
                        k: round(v, 3) for k, v in match.match_reasons.items()
                    },
                    "integration_actions": match.integration_actions,
                }
            )

        return formatted

    def _find_branding_updates(self) -> List[Dict]:
        """Find files that need branding updates"""
        updates = []

        for file_path in self.isolated_files:
            if any(brand in file_path.lower() for brand in ["lucas", "lucλs"]):
                updates.append(
                    {
                        "file": file_path,
                        "suggested_path": BrandingNormalizer.normalize_path(file_path),
                    }
                )

        return updates[:50]  # Top 50

    def _print_summary(self, report: Dict):
        """Print human-readable summary"""
        print("\n" + "=" * 70)
        print("🎯 INTEGRATION ANALYSIS SUMMARY")
        print("=" * 70)

        meta = report["metadata"]
        print("\n📊 Files Analyzed:")
        print(f"  - Connected files: {meta['total_connected_files']:,}")
        print(f"  - Isolated files: {meta['total_isolated_files']:,}")
        print(
            f"  - Code signatures found: {meta['isolated_signatures_analyzed']:,} (isolated)"
        )
        print(
            f"  - Code signatures found: {meta['working_signatures_analyzed']:,} (working)"
        )

        conf = report["confidence_summary"]
        print("\n🎯 Integration Matches Found:")
        print(f"  - High confidence (≥85%): {conf['high_confidence_matches']}")
        print(f"  - Medium confidence (70-84%): {conf['medium_confidence_matches']}")
        print(f"  - Low confidence (60-69%): {conf['low_confidence_matches']}")

        print("\n🏷️  Domain Distribution:")
        for domain, count in sorted(
            report["domain_summary"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  - {domain}: {count} matches")

        print(
            f"\n🔄 Branding Updates Needed: {len(report['branding_updates_needed'])} files"
        )

        if report["high_confidence_integrations"]:
            print("\n✨ Top High-Confidence Integration Opportunities:")
            for i, match in enumerate(report["high_confidence_integrations"][:5], 1):
                print(
                    f"\n  {i}. {match['isolated_element']['name']} → {match['target_element']['name']}"
                )
                print(f"     Score: {match['confidence_score']:.1%}")
                print(f"     From: {match['isolated_file']}")
                print(f"     To: {match['target_file']}")


def main():
    parser = argparse.ArgumentParser(
        description="Intelligent file integration system for LUKHAS AGI"
    )
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument("connectivity_file", help="Path to connectivity analysis JSON")
    parser.add_argument(
        "-o",
        "--output",
        default="integration_plan.json",
        help="Output file for integration plan",
    )
    parser.add_argument(
        "-c",
        "--min-confidence",
        type=float,
        default=0.6,
        help="Minimum confidence score for matches (0-1)",
    )

    args = parser.parse_args()

    print("🚀 Starting Intelligent File Integration Analysis")
    print(f"📁 Repository: {args.repo_path}")
    print(f"📊 Using connectivity data: {args.connectivity_file}")

    integrator = IntelligentFileIntegrator(args.repo_path)

    # Load connectivity data
    integrator.load_connectivity_data(args.connectivity_file)

    # Analyze files
    integrator.analyze_files()

    # Find matches
    integrator.find_integration_matches(args.min_confidence)

    # Generate report
    integrator.generate_integration_report(args.output)

    print(f"\n✅ Integration plan saved to: {args.output}")
    print("\n🎉 Analysis complete!")


if __name__ == "__main__":
    main()
