#!/usr/bin/env python3
"""
🔍 lukhas Keyword Extractor
📦 Purpose: Extract domain-specific keywords from system codebase and documentation
🎯 Goal: Build comprehensive thematic classification for modularization
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path


class KeywordExtractor:
    def __init__(self, workspace_root="/Users/A_G_I/CodexGPT_Lukhas"):
        self.workspace_root = Path(workspace_root)
        self.keywords = defaultdict(set)
        self.domain_patterns = {
            "bio": re.compile(
                r"\b(bio|neural|neuro|brain|cognitive|awareness|consciousness|cell|gene|protein|organism|evolution|adaptation|biosignature|qi.*bio|biometric|neural.*network|cortex|synapse|dendrite|axon|neurotransmitter)\b",
                re.IGNORECASE,
            ),
            "memory": re.compile(
                r"\b(memory|memorization|recall|remember|episodic|semantic|working.*memory|cache|storage|persist|trace|rem|hippocampus|encoding|retrieval|consolidation|forgetting|memorize)\b",
                re.IGNORECASE,
            ),
            "dream": re.compile(
                r"\b(dream|dreaming|unconscious|subconscious|simulation|imagine|imagination|fantasy|vision|hallucination|lucid|nightmare|rem.*sleep|oneiric)\b",
                re.IGNORECASE,
            ),
            "voice": re.compile(
                r"\b(voice|speech|audio|sound|tts|text.*to.*speech|whisper|eleven.*labs|phoneme|prosody|intonation|utterance|vocal|articulation|pronunciation)\b",
                re.IGNORECASE,
            ),
            "quantum": re.compile(
                r"\b(quantum|qubit|superposition|entanglement|collapse|wave.*function|decoherence|qi.*field|qi.*state|qi.*mechanics|qi.*computing|qi.*awareness)\b",
                re.IGNORECASE,
            ),
            "symbolic": re.compile(
                r"\b(symbolic|symbol|logic|reasoning|planning|inference|eval|evaluation|lambda|predicate|proposition|theorem|proof|axiom|semantic|syntax|ontology)\b",
                re.IGNORECASE,
            ),
            "emotional": re.compile(
                r"\b(emotion|emotional|feeling|mood|sentiment|affect|empathy|compassion|joy|sadness|anger|fear|surprise|disgust|arousal|valence|resonance)\b",
                re.IGNORECASE,
            ),
            "governance": re.compile(
                r"\b(governance|policy|rule|regulation|compliance|ethics|ethical|moral|accountability|responsibility|audit|monitor|oversight|guideline)\b",
                re.IGNORECASE,
            ),
            "identity": re.compile(
                r"\b(identity|self|persona|personality|character|trait|profile|signature|authentication|authorization|credential|token|fingerprint)\b",
                re.IGNORECASE,
            ),
            "orchestrator": re.compile(
                r"\b(orchestrat|coordination|coordinate|manage|control|dispatch|schedule|workflow|pipeline|routing|director|conductor|maestro)\b",
                re.IGNORECASE,
            ),
            "interface": re.compile(
                r"\b(interface|api|adapter|connector|bridge|gateway|endpoint|protocol|websocket|http|rest|graphql|rpc|middleware)\b",
                re.IGNORECASE,
            ),
            "learning": re.compile(
                r"\b(learn|learning|train|training|adapt|adaptation|evolve|evolution|optimize|optimization|gradient|backprop|meta.*learning|transfer.*learning)\b",
                re.IGNORECASE,
            ),
            "security": re.compile(
                r"\b(security|secure|encrypt|decrypt|hash|cipher|ssl|tls|certificate|key|private|public|signature|authentication|authorization)\b",
                re.IGNORECASE,
            ),
            "web": re.compile(
                r"\b(web|html|css|javascript|react|vue|angular|dom|browser|http|https|url|uri|endpoint|server|client|frontend|backend)\b",
                re.IGNORECASE,
            ),
            "data": re.compile(
                r"\b(data|dataset|database|sql|nosql|json|xml|csv|pandas|numpy|tensor|matrix|vector|array|structure|schema)\b",
                re.IGNORECASE,
            ),
            "network": re.compile(
                r"\b(network|neural.*network|graph|node|edge|connection|topology|layer|neuron|activation|weight|bias|convolution)\b",
                re.IGNORECASE,
            ),
        }

        # File extensions to scan
        self.code_extensions = {".py", ".md", ".txt", ".json", ".yaml", ".yml"}

        # Directories to exclude
        self.exclude_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "node_modules",
            ".pytest_cache",
            "htmlcov",
            ".DS_Store",
            "lukhas.egg-info",
        }

    def extract_from_file(self, file_path):
        """Extract keywords from a single file"""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()

            file_keywords = defaultdict(set)
            for domain, pattern in self.domain_patterns.items():
                matches = pattern.findall(content)
                if matches:
                    file_keywords[domain].update(matches)

            return file_keywords
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
            return defaultdict(set)

    def scan_workspace(self):
        """Scan the entire workspace for domain keywords"""
        print(f"🔍 Scanning workspace: {self.workspace_root}")

        total_files = 0
        processed_files = 0

        for root, dirs, files in os.walk(self.workspace_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.code_extensions:
                    total_files += 1

                    file_keywords = self.extract_from_file(file_path)
                    if file_keywords:
                        processed_files += 1
                        for domain, kws in file_keywords.items():
                            self.keywords[domain].update(kws)

        print(f"📊 Processed {processed_files}/{total_files} files")
        return self.keywords

    def generate_enhanced_domains(self):
        """Generate enhanced domain configuration for core_mapper"""
        enhanced_domains = {}

        for domain, keyword_set in self.keywords.items():
            # Convert to sorted list and clean up
            keywords = sorted(keyword_set)
            # Remove very short or generic words
            filtered_keywords = [
                kw for kw in keywords if len(kw) > 2 and kw not in {"the", "and", "for", "with", "from"}
            ]
            enhanced_domains[domain] = filtered_keywords[:20]  # Top 20 keywords per domain

        return enhanced_domains

    def save_results(self, output_file="keyword_analysis.json"):
        """Save extracted keywords to JSON file"""
        results = {
            "domains": {domain: sorted(kws) for domain, kws in self.keywords.items()},
            "enhanced_domains": self.generate_enhanced_domains(),
            "statistics": {
                "total_domains": len(self.keywords),
                "total_unique_keywords": sum(len(kws) for kws in self.keywords.values()),
            },
        }

        output_path = self.workspace_root / output_file
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)

        print(f"💾 Results saved to: {output_path}")
        return results

    def print_summary(self):
        """Print a summary of extracted keywords"""
        print("\n🎯 lukhas Domain Keywords Summary")
        print("=" * 50)

        for domain in sorted(self.keywords.keys()):
            keywords = sorted(self.keywords[domain])
            print(f"\n📁 {domain.upper()} ({len(keywords)} keywords):")
            print(f"   {', '.join(keywords[:10])}")
            if len(keywords) > 10:
                print(f"   ... and {len(keywords) - 10} more")


if __name__ == "__main__":
    print("🚀 Starting lukhas Keyword Extraction...")

    extractor = lukhasKeywordExtractor()  # noqa: F821  # TODO: lukhasKeywordExtractor
    keywords = extractor.scan_workspace()
    extractor.print_summary()
    results = extractor.save_results()

    print(f"\n✅ Extraction complete! Found {len(keywords)} domains")
    print("🔧 Use these results to enhance core_mapper.py")

# Λ Systems 2025 www.lukhas.ai
