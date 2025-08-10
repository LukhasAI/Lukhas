#!/usr/bin/env python3
"""
Automatic Daily Benchmark Organizer
Organizes test results into dated folders automatically
"""

import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DailyBenchmarkOrganizer:
    """Automatically organize benchmark results by date"""

    def __init__(self, benchmarks_root: str = None):
        self.benchmarks_root = Path(benchmarks_root or os.getcwd())
        self.daily_archive = self.benchmarks_root / "daily_archives"

        # Categories to organize
        self.categories = [
            "safety",
            "performance",
            "actor_systems",
            "memory",
            "ethics",
            "integration",
            "creativity",
            "quantum",
            "orchestration",
            "voice",
            "reasoning",
            "emotion",
            "symbolic",
            "dashboard",
            "learning",
            "perception",
            "api",
            "security",
            "bridge",
            "config",
        ]

        # File patterns that indicate test results
        self.test_patterns = [
            "*_test_*.json",
            "*_benchmark_*.json",
            "*_results_*.json",
            "*_analysis_*.json",
            "*test*.json",
            "*benchmark*.json",
        ]

        # File patterns for test scripts
        self.script_patterns = [
            "*_test_*.py",
            "*_benchmark_*.py",
            "test_*.py",
            "benchmark_*.py",
        ]

        logger.info(f"Initialized organizer for: {self.benchmarks_root}")

    def create_daily_structure(self, date: str = None) -> Path:
        """Create daily directory structure"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        daily_dir = self.daily_archive / date
        daily_dir.mkdir(parents=True, exist_ok=True)

        # Create category subdirectories
        for category in self.categories:
            category_dir = daily_dir / category
            category_dir.mkdir(exist_ok=True)

            # Create results and scripts subdirectories
            (category_dir / "results").mkdir(exist_ok=True)
            (category_dir / "scripts").mkdir(exist_ok=True)
            (category_dir / "metadata").mkdir(exist_ok=True)

        logger.info(f"Created daily structure for: {date}")
        return daily_dir

    def detect_test_files(self, directory: Path) -> Dict[str, List[Path]]:
        """Detect test files that need organization"""
        detected_files = {"results": [], "scripts": [], "metadata": []}

        # Find test result files
        for pattern in self.test_patterns:
            detected_files["results"].extend(directory.glob(pattern))

        # Find test script files
        for pattern in self.script_patterns:
            detected_files["scripts"].extend(directory.glob(pattern))

        # Find metadata files
        for file in directory.glob("*metadata*.json"):
            detected_files["metadata"].append(file)

        return detected_files

    def extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract date from filename patterns like 'test_20250729_064441'"""
        import re

        # Pattern for YYYYMMDD_HHMMSS
        pattern1 = r"(\d{8}_\d{6})"
        match1 = re.search(pattern1, filename)
        if match1:
            date_str = match1.group(1)[:8]  # Get YYYYMMDD part
            try:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Pattern for YYYY-MM-DD
        pattern2 = r"(\d{4}-\d{2}-\d{2})"
        match2 = re.search(pattern2, filename)
        if match2:
            return match2.group(1)

        return None

    def categorize_file(self, file_path: Path) -> str:
        """Determine which category a file belongs to"""
        filename = file_path.name.lower()

        # Direct category matches
        category_keywords = {
            "safety": ["safety", "security", "safeguard", "protection"],
            "performance": [
                "performance",
                "benchmark",
                "throughput",
                "latency",
                "quantized",
            ],
            "actor_systems": ["actor", "swarm", "colony"],
            "memory": ["memory", "fold", "storage"],
            "ethics": ["ethics", "ethical", "compliance", "moral"],
            "integration": [
                "integration",
                "coherence",
                "consciousness",
                "symbolic_reasoning",
            ],
            "creativity": ["creativity", "dream", "creative"],
            "quantum": ["quantum", "identity"],
            "orchestration": ["orchestration", "workflow", "coordination"],
            "voice": ["voice", "speech", "audio"],
            "reasoning": ["reasoning", "logic", "inference"],
            "emotion": ["emotion", "sentiment", "mood"],
            "symbolic": ["symbolic", "symbol", "vocabulary"],
            "dashboard": ["dashboard", "ui", "interface"],
            "learning": ["learning", "adaptive", "meta"],
            "perception": ["perception", "sensor", "visual"],
            "api": ["api", "endpoint", "service"],
            "security": ["security", "auth", "encryption"],
            "bridge": ["bridge", "integration", "adapter"],
            "config": ["config", "settings", "configuration"],
        }

        for category, keywords in category_keywords.items():
            if any(keyword in filename for keyword in keywords):
                return category

        # Check parent directory
        parent_name = file_path.parent.name.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in parent_name for keyword in keywords):
                return category

        # Default to integration for unknown files
        return "integration"

    def organize_file(self, file_path: Path, daily_dir: Path, file_type: str) -> bool:
        """Organize a single file into the daily structure"""
        try:
            category = self.categorize_file(file_path)

            # Determine destination directory
            dest_dir = daily_dir / category / file_type
            dest_path = dest_dir / file_path.name

            # Avoid overwriting existing files
            counter = 1
            original_dest = dest_path
            while dest_path.exists():
                stem = original_dest.stem
                suffix = original_dest.suffix
                dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            # Copy (don't move) the file to preserve originals
            shutil.copy2(file_path, dest_path)

            logger.info(f"Organized {file_path.name} -> {category}/{file_type}/")
            return True

        except Exception as e:
            logger.error(f"Failed to organize {file_path}: {e}")
            return False

    def generate_daily_summary(self, daily_dir: Path) -> Dict[str, any]:
        """Generate summary of the day's test results"""
        summary = {
            "date": daily_dir.name,
            "timestamp": datetime.now().isoformat(),
            "categories": {},
            "totals": {"results": 0, "scripts": 0, "metadata": 0},
        }

        for category in self.categories:
            category_dir = daily_dir / category
            if not category_dir.exists():
                continue

            category_summary = {
                "results": len(list((category_dir / "results").glob("*"))),
                "scripts": len(list((category_dir / "scripts").glob("*"))),
                "metadata": len(list((category_dir / "metadata").glob("*"))),
            }

            summary["categories"][category] = category_summary

            # Add to totals
            for key in ["results", "scripts", "metadata"]:
                summary["totals"][key] += category_summary[key]

        # Save summary
        summary_path = daily_dir / "daily_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Generated daily summary: {summary['totals']}")
        return summary

    def cleanup_old_archives(self, days_to_keep: int = 30):
        """Clean up archives older than specified days"""
        if not self.daily_archive.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        for daily_dir in self.daily_archive.iterdir():
            if daily_dir.is_dir():
                try:
                    dir_date = datetime.strptime(daily_dir.name, "%Y-%m-%d")
                    if dir_date < cutoff_date:
                        shutil.rmtree(daily_dir)
                        logger.info(f"Cleaned up old archive: {daily_dir.name}")
                except ValueError:
                    # Skip directories that don't match date format
                    continue

    def organize_today(self, source_categories: List[str] = None) -> Dict[str, any]:
        """Organize today's test results"""
        today = datetime.now().strftime("%Y-%m-%d")
        daily_dir = self.create_daily_structure(today)

        organized_count = 0
        failed_count = 0

        # Default to all categories if none specified
        if source_categories is None:
            source_categories = self.categories

        for category in source_categories:
            category_path = self.benchmarks_root / category
            if not category_path.exists():
                continue

            # Detect files in category
            detected_files = self.detect_test_files(category_path)

            # Organize each type of file
            for file_type, files in detected_files.items():
                for file_path in files:
                    # Check if file was created today (or has today's date in name)
                    file_date = self.extract_date_from_filename(file_path.name)
                    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

                    # Organize if file is from today or has today's date
                    if (
                        file_date == today
                        or file_modified.strftime("%Y-%m-%d") == today
                    ):

                        if self.organize_file(file_path, daily_dir, file_type):
                            organized_count += 1
                        else:
                            failed_count += 1

        # Generate summary
        summary = self.generate_daily_summary(daily_dir)
        summary["organization_stats"] = {
            "organized": organized_count,
            "failed": failed_count,
        }

        # Cleanup old archives
        self.cleanup_old_archives()

        return summary

    def create_benchmark_script_template(self, system_name: str) -> str:
        """Create a template benchmark script for a new system"""
        template = f'''#!/usr/bin/env python3
"""
{system_name.title()} System Benchmark
Generated automatically by Daily Benchmark Organizer
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_{system_name}_performance():
    """Test {system_name} system performance"""
    results = {{
        "test_id": f"{system_name}_performance_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}",
        "timestamp": datetime.now().isoformat(),
        "system": "{system_name}",
        "test_type": "performance",
        "results": {{}}
    }}

    print(f"🧪 Testing {system_name.title()} System Performance")
    print("=" * 60)

    # TODO: Implement actual {system_name} performance tests
    # Example metrics to measure:
    # - Throughput (operations/second)
    # - Latency (response time)
    # - Resource usage (CPU/memory)
    # - Error rates

    # Placeholder test
    start_time = time.time()

    # TODO: Add actual system tests here
    test_operations = 100
    for i in range(test_operations):
        # Simulate {system_name} operation
        await asyncio.sleep(0.001)  # 1ms simulated operation

    duration = time.time() - start_time
    throughput = test_operations / duration

    results["results"] = {{
        "throughput_ops_per_sec": round(throughput, 2),
        "total_operations": test_operations,
        "duration_seconds": round(duration, 3),
        "average_latency_ms": round((duration / test_operations) * 1000, 3)
    }}

    print(f"✅ Throughput: {{throughput:.1f}} ops/second")
    print(f"✅ Average Latency: {{(duration/test_operations)*1000:.1f}}ms")

    return results


async def test_{system_name}_accuracy():
    """Test {system_name} system accuracy"""
    results = {{
        "test_id": f"{system_name}_accuracy_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}",
        "timestamp": datetime.now().isoformat(),
        "system": "{system_name}",
        "test_type": "accuracy",
        "results": {{}}
    }}

    print(f"\\n🎯 Testing {system_name.title()} System Accuracy")
    print("-" * 60)

    # TODO: Implement accuracy tests
    # Example metrics:
    # - Correctness percentage
    # - False positive/negative rates
    # - Precision/recall scores

    # Placeholder accuracy test
    test_cases = 50
    correct_results = 48  # TODO: Replace with actual testing

    accuracy = correct_results / test_cases

    results["results"] = {{
        "accuracy": accuracy,
        "correct_results": correct_results,
        "total_test_cases": test_cases,
        "error_rate": 1 - accuracy
    }}

    print(f"✅ Accuracy: {{accuracy:.1%}}")
    print(f"✅ Correct: {{correct_results}}/{{test_cases}}")

    return results


async def main():
    """Run all {system_name} benchmarks"""
    print(f"🚀 {system_name.upper()} SYSTEM BENCHMARK SUITE")
    print("=" * 80)

    all_results = {{
        "benchmark_suite": f"{system_name}_comprehensive",
        "timestamp": datetime.now().isoformat(),
        "tests": {{}}
    }}

    try:
        # Run performance tests
        perf_results = await test_{system_name}_performance()
        all_results["tests"]["performance"] = perf_results

        # Run accuracy tests
        acc_results = await test_{system_name}_accuracy()
        all_results["tests"]["accuracy"] = acc_results

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"{system_name}_benchmark_results_{{timestamp}}.json"

        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\\n📊 BENCHMARK SUMMARY")
        print("=" * 80)
        print(f"✅ Performance Test: {{perf_results['results']['throughput_ops_per_sec']}} ops/sec")
        print(f"✅ Accuracy Test: {{acc_results['results']['accuracy']:.1%}}")
        print(f"📁 Results saved: {{results_file}}")
        print(f"\\n🎉 {system_name.title()} benchmark completed!")

    except Exception as e:
        print(f"\\n❌ Benchmark failed: {{e}}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
'''
        return template


def main():
    """Command-line interface for the organizer"""
    import argparse

    parser = argparse.ArgumentParser(description="Daily Benchmark Organizer")
    parser.add_argument(
        "--organize", action="store_true", help="Organize today's benchmarks"
    )
    parser.add_argument(
        "--create-template", type=str, help="Create benchmark template for system"
    )
    parser.add_argument(
        "--cleanup", type=int, default=30, help="Days of archives to keep (default: 30)"
    )
    parser.add_argument("--root", type=str, help="Benchmarks root directory")

    args = parser.parse_args()

    organizer = DailyBenchmarkOrganizer(args.root)

    if args.organize:
        summary = organizer.organize_today()
        print("📊 Daily organization complete:")
        print(f"   Organized: {summary['organization_stats']['organized']} files")
        print(f"   Failed: {summary['organization_stats']['failed']} files")
        print(f"   Total results: {summary['totals']['results']}")

    elif args.create_template:
        template = organizer.create_benchmark_script_template(args.create_template)
        filename = f"benchmark_{args.create_template}.py"
        with open(filename, "w") as f:
            f.write(template)
        print(f"📝 Created benchmark template: {filename}")

    else:
        print("Use --organize to organize today's benchmarks")
        print("Use --create-template <system> to create a benchmark template")


if __name__ == "__main__":
    main()
