#!/usr/bin/env python3
"""
Module Inventory: Compare /lukhas/ vs /lukhas_website/lukhas/

This script analyzes the two lukhas directories to identify:
1. Modules unique to production /lukhas/
2. Modules unique to website /lukhas_website/lukhas/
3. Overlapping modules (potential duplicates)
4. File size comparisons for overlaps
5. Import analysis for divergence detection

Reference: docs/audit/LUKHAS_WEBSITE_DIRECTORY_AUDIT_2025-11-12.md
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict


class DirectoryComparator:
    """Compare two directory structures for module inventory."""

    def __init__(self, prod_path: Path, website_path: Path):
        self.prod_path = prod_path
        self.website_path = website_path
        self.prod_modules: Dict[str, Path] = {}
        self.website_modules: Dict[str, Path] = {}

    def scan_directory(self, base_path: Path) -> Dict[str, Path]:
        """Scan directory and return module name -> path mapping."""
        modules = {}
        if not base_path.exists():
            print(f"Warning: {base_path} does not exist", file=sys.stderr)
            return modules

        for item in base_path.iterdir():
            if item.name.startswith(".") or item.name == "__pycache__":
                continue
            if item.is_dir():
                modules[item.name] = item
        return modules

    def get_file_stats(self, path: Path) -> Dict[str, int]:
        """Get statistics for a directory."""
        py_files = list(path.rglob("*.py"))
        total_size = sum(f.stat().st_size for f in py_files if f.is_file())
        return {
            "py_files": len(py_files),
            "total_size": total_size,
            "total_size_kb": total_size // 1024,
        }

    def compare(self) -> Dict:
        """Run comparison and return results."""
        print("Scanning production /lukhas/...")
        self.prod_modules = self.scan_directory(self.prod_path)

        print("Scanning website /lukhas_website/lukhas/...")
        self.website_modules = self.scan_directory(self.website_path)

        prod_only = set(self.prod_modules.keys()) - set(self.website_modules.keys())
        website_only = set(self.website_modules.keys()) - set(self.prod_modules.keys())
        overlapping = set(self.prod_modules.keys()) & set(self.website_modules.keys())

        results = {
            "summary": {
                "prod_total_modules": len(self.prod_modules),
                "website_total_modules": len(self.website_modules),
                "prod_only_count": len(prod_only),
                "website_only_count": len(website_only),
                "overlapping_count": len(overlapping),
            },
            "prod_only": sorted(prod_only),
            "website_only": sorted(website_only),
            "overlapping": [],
        }

        # Analyze overlapping modules
        print("\nAnalyzing overlapping modules...")
        for module_name in sorted(overlapping):
            prod_path = self.prod_modules[module_name]
            website_path = self.website_modules[module_name]

            prod_stats = self.get_file_stats(prod_path)
            website_stats = self.get_file_stats(website_path)

            size_diff_pct = (
                0
                if prod_stats["total_size"] == 0
                else (
                    (website_stats["total_size"] - prod_stats["total_size"])
                    / prod_stats["total_size"]
                    * 100
                )
            )

            overlap_info = {
                "module": module_name,
                "prod": prod_stats,
                "website": website_stats,
                "size_diff_pct": round(size_diff_pct, 1),
                "verdict": self._categorize_overlap(prod_stats, website_stats, size_diff_pct),
            }
            results["overlapping"].append(overlap_info)

        return results

    def _categorize_overlap(
        self, prod_stats: Dict, website_stats: Dict, size_diff_pct: float
    ) -> str:
        """Categorize the type of overlap."""
        if abs(size_diff_pct) < 10:
            return "POTENTIAL_DUPLICATE"
        elif website_stats["total_size"] > prod_stats["total_size"]:
            return "WEBSITE_EXTENSION"
        elif website_stats["total_size"] < prod_stats["total_size"]:
            return "WEBSITE_SUBSET"
        else:
            return "UNKNOWN"


def format_size(bytes_size: int) -> str:
    """Format bytes into human-readable size."""
    for unit in ["B", "KB", "MB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} GB"


def print_report(results: Dict):
    """Print formatted report to console."""
    print("\n" + "=" * 80)
    print("MODULE INVENTORY: /lukhas/ vs /lukhas_website/lukhas/")
    print("=" * 80)

    summary = results["summary"]
    print("\n📊 SUMMARY:")
    print(f"  Production /lukhas/: {summary['prod_total_modules']} modules")
    print(f"  Website /lukhas_website/lukhas/: {summary['website_total_modules']} modules")
    print(f"  Production-only: {summary['prod_only_count']} modules")
    print(f"  Website-only: {summary['website_only_count']} modules")
    print(f"  Overlapping: {summary['overlapping_count']} modules")

    # Production-only modules
    if results["prod_only"]:
        print(f"\n✅ PRODUCTION-ONLY MODULES ({len(results['prod_only'])}):")
        print("  These exist in /lukhas/ but not in /lukhas_website/lukhas/")
        for module in results["prod_only"]:
            print(f"  - {module}")

    # Website-only modules
    if results["website_only"]:
        print(f"\n🌐 WEBSITE-ONLY MODULES ({len(results['website_only'])}):")
        print("  These exist in /lukhas_website/lukhas/ but not in /lukhas/")
        for module in results["website_only"][:20]:  # Show first 20
            print(f"  - {module}")
        if len(results["website_only"]) > 20:
            print(f"  ... and {len(results['website_only']) - 20} more")

    # Overlapping modules
    if results["overlapping"]:
        print(f"\n🔄 OVERLAPPING MODULES ({len(results['overlapping'])}):")
        print("  These exist in both directories - potential duplicates or extensions")
        print()

        # Group by verdict
        by_verdict = defaultdict(list)
        for item in results["overlapping"]:
            by_verdict[item["verdict"]].append(item)

        for verdict, items in sorted(by_verdict.items()):
            print(f"  {verdict} ({len(items)} modules):")
            for item in sorted(items, key=lambda x: abs(x["size_diff_pct"]), reverse=True):
                prod_size = format_size(item["prod"]["total_size"])
                web_size = format_size(item["website"]["total_size"])
                diff = item["size_diff_pct"]
                sign = "+" if diff > 0 else ""
                print(
                    f"    - {item['module']:25} | Prod: {prod_size:>10} | "
                    f"Website: {web_size:>10} | Diff: {sign}{diff:>6.1f}%"
                )
            print()

    print("=" * 80)
    print(
        "\n💡 RECOMMENDATIONS:\n"
        "  - POTENTIAL_DUPLICATE: Review for true duplication, consider consolidation\n"
        "  - WEBSITE_EXTENSION: Website extends production module (expected)\n"
        "  - WEBSITE_SUBSET: Website has partial implementation (may need sync)\n"
    )
    print("=" * 80)


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent
    prod_path = repo_root / "lukhas"
    website_path = repo_root / "lukhas_website" / "lukhas"

    print(f"Repository root: {repo_root}")
    print(f"Production path: {prod_path}")
    print(f"Website path: {website_path}")

    comparator = DirectoryComparator(prod_path, website_path)
    results = comparator.compare()

    # Print human-readable report
    print_report(results)

    # Save JSON report
    output_file = repo_root / "docs" / "audit" / "lukhas_directory_comparison.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Full report saved to: {output_file}")

    # Exit with warning code if potential duplicates found
    duplicates = [
        item for item in results["overlapping"] if item["verdict"] == "POTENTIAL_DUPLICATE"
    ]
    if duplicates:
        print(
            f"\n⚠️  WARNING: {len(duplicates)} potential duplicate modules detected!\n"
            "    Review these modules for unnecessary duplication."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
