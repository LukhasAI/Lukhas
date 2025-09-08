#!/usr/bin/env python3
"""
LUKHAS Symbol Resolution Tool
Analyzes F821 violations and provides strategic resolution suggestions
"""
import json
from collections import defaultdict


class LUKHASSymbolResolver:
    """LUKHAS consciousness-aware symbol resolver"""

    def __init__(self, f821_report_path: str):
        self.f821_report_path = f821_report_path
        self.violations = []
        self.symbol_patterns = defaultdict(list)
        self.file_patterns = defaultdict(int)
        self.consciousness_tiers = {
            "TIER_1_CORE": ["candidate/consciousness", "candidate/memory", "lukhas/identity", "candidate/bio", "governance"],
            "TIER_2_INTEGRATION": ["orchestration/brain", "bridge", "api", "visualization"],
            "TIER_3_EXPERIMENTAL": ["candidate/core", "products/", "branding/", "tools/"]
        }

    def load_violations(self):
        """Load F821 violations from JSON report"""
        with open(self.f821_report_path) as f:
            data = json.load(f)
            self.violations = data.get("violations", [])
        print(f"Loaded {len(self.violations)} F821 violations")

    def analyze_patterns(self):
        """Analyze common patterns in F821 violations"""
        symbol_counts = defaultdict(int)
        file_counts = defaultdict(int)

        for violation in self.violations:
            filename = violation["filename"]
            message = violation["message"]

            # Extract symbol name from message
            if "Undefined name `" in message:
                symbol = message.split("Undefined name `")[1].split("`")[0]
                symbol_counts[symbol] += 1
                self.symbol_patterns[symbol].append(filename)

            # Count by directory
            dir_prefix = "/".join(filename.split("/")[:2])
            file_counts[dir_prefix] += 1

        self.symbol_counts = dict(sorted(symbol_counts.items(), key=lambda x: x[1], reverse=True))
        self.file_counts = dict(sorted(file_counts.items(), key=lambda x: x[1], reverse=True))

    def categorize_by_tier(self):
        """Categorize violations by consciousness system tiers"""
        tier_counts = defaultdict(int)
        tier_files = defaultdict(set)

        for violation in self.violations:
            filename = violation["filename"]

            # Determine tier
            tier = "TIER_3_EXPERIMENTAL"  # Default
            for tier_name, patterns in self.consciousness_tiers.items():
                if any(pattern in filename for pattern in patterns):
                    tier = tier_name
                    break

            tier_counts[tier] += 1
            tier_files[tier].add(filename)

        return tier_counts, tier_files

    def identify_common_fixes(self):
        """Identify common fix patterns for F821 violations"""
        fixes = []

        # Common typos
        typo_patterns = {
            "platfrom": "platform",
            "integeration": "integration",
            "consciousnes": "consciousness",
            "managment": "management",
            "procesing": "processing"
        }

        # Variables that might need definitions
        common_undefined = ["result", "platform", "integration", "fix_later"]

        for symbol, count in self.symbol_counts.items():
            if symbol in typo_patterns:
                fixes.append({
                    "type": "TYPO_FIX",
                    "symbol": symbol,
                    "correct": typo_patterns[symbol],
                    "count": count,
                    "files": self.symbol_patterns[symbol]
                })
            elif symbol in common_undefined:
                fixes.append({
                    "type": "MISSING_DEFINITION",
                    "symbol": symbol,
                    "count": count,
                    "files": self.symbol_patterns[symbol]
                })
            elif symbol.endswith("_later") or symbol.startswith("fix_"):
                fixes.append({
                    "type": "TODO_STUB",
                    "symbol": symbol,
                    "count": count,
                    "files": self.symbol_patterns[symbol]
                })

        return fixes

    def generate_resolution_report(self):
        """Generate comprehensive resolution report"""
        self.load_violations()
        self.analyze_patterns()
        tier_counts, tier_files = self.categorize_by_tier()
        fixes = self.identify_common_fixes()

        print("\n" + "="*80)
        print("LUKHAS SYMBOL RESOLUTION ANALYSIS")
        print("="*80)

        print(f"\nTOTAL F821 VIOLATIONS: {len(self.violations)}")

        print("\nVIOLATIONS BY CONSCIOUSNESS TIER:")
        for tier, count in tier_counts.items():
            print(f"  {tier}: {count} violations ({len(tier_files[tier])} files)")

        print("\nTOP 20 UNDEFINED SYMBOLS:")
        for symbol, count in list(self.symbol_counts.items())[:20]:
            print(f"  {symbol}: {count} occurrences")

        print("\nTOP AFFECTED DIRECTORIES:")
        for directory, count in list(self.file_counts.items())[:15]:
            print(f"  {directory}: {count} violations")

        print("\nRECOMMENDED FIXES:")
        for fix in fixes[:10]:
            print(f"  {fix['type']}: '{fix['symbol']}' ({fix['count']} occurrences)")
            if fix["type"] == "TYPO_FIX":
                print(f"    → Replace with: '{fix['correct']}'")

        return {
            "total_violations": len(self.violations),
            "tier_counts": tier_counts,
            "symbol_counts": self.symbol_counts,
            "file_counts": self.file_counts,
            "recommended_fixes": fixes
        }

if __name__ == "__main__":
    resolver = LUKHASSymbolResolver("/Users/agi_dev/LOCAL-REPOS/Lukhas/reports/idx_F821.json")
    report = resolver.generate_resolution_report()
