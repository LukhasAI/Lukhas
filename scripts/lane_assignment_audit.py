#!/usr/bin/env python3
"""
Lane Assignment and Module Promotion Audit

Comprehensive analysis of LUKHAS codebase to determine production readiness
and assign modules to appropriate development lanes for T4/0.01% targets.
"""

import ast
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class ModuleMetrics:
    """Metrics for evaluating module production readiness."""
    path: str
    name: str
    lines_of_code: int
    test_coverage: float
    complexity_score: int
    documentation_score: float
    dependency_count: int
    performance_profile: Dict[str, any]
    error_handling_score: float
    security_score: float
    enterprise_readiness_score: float

@dataclass
class LaneAssignment:
    """Lane assignment for a module."""
    module_path: str
    current_lane: str
    recommended_lane: str
    readiness_score: float
    promotion_blockers: List[str]
    promotion_requirements: List[str]
    target_completion_days: int

class LaneAssignmentAuditor:
    """
    Comprehensive auditor for lane assignment and module promotion.

    Lanes:
    - RESEARCH: Experimental code, <40% production readiness
    - CANDIDATE: Active development, 40-70% production readiness
    - LUKHAS: Production-ready core, 70-90% production readiness
    - ACCEPTED: Enterprise-grade, >90% production readiness
    """

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.module_metrics: Dict[str, ModuleMetrics] = {}
        self.lane_assignments: Dict[str, LaneAssignment] = {}

        # Lane criteria thresholds
        self.lane_thresholds = {
            "RESEARCH": 0.40,
            "CANDIDATE": 0.70,
            "LUKHAS": 0.90,
            "ACCEPTED": 0.95
        }

        # Performance target requirements for T4/0.01%
        self.t4_requirements = {
            "max_latency_ms": 100,
            "memory_efficiency": 0.85,
            "cpu_efficiency": 0.80,
            "error_rate": 0.001,
            "availability": 0.999
        }

    def audit_codebase(self) -> Dict[str, any]:
        """Perform comprehensive codebase audit for lane assignment."""
        print("🔍 Starting comprehensive lane assignment audit...")

        audit_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {},
            "modules": {},
            "recommendations": {},
            "promotion_plan": {}
        }

        # Discover and analyze modules
        modules = self._discover_modules()
        print(f"📊 Discovered {len(modules)} modules for analysis")

        for module_path in modules:
            try:
                metrics = self._analyze_module(module_path)
                self.module_metrics[module_path] = metrics

                assignment = self._assign_lane(metrics)
                self.lane_assignments[module_path] = assignment

            except Exception as e:
                print(f"⚠️ Failed to analyze {module_path}: {e}")

        # Generate summary
        audit_results["summary"] = self._generate_summary()
        audit_results["modules"] = {
            path: asdict(metrics) for path, metrics in self.module_metrics.items()
        }
        audit_results["recommendations"] = self._generate_recommendations()
        audit_results["promotion_plan"] = self._generate_promotion_plan()

        return audit_results

    def _discover_modules(self) -> List[str]:
        """Discover Python modules in the codebase."""
        modules = []

        # Define directories to analyze
        core_dirs = [
            "lukhas/core",
            "lukhas/memory",
            "lukhas/consciousness",
            "lukhas/observability",
            "lukhas/matriz",
            "candidate/core",
            "candidate/memory",
            "candidate/consciousness"
        ]

        for directory in core_dirs:
            dir_path = self.root_path / directory
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    if (not py_file.name.startswith("_") and
                        "__pycache__" not in str(py_file)):
                        try:
                            if py_file.exists() and py_file.stat().st_size > 100:  # Skip tiny files
                                modules.append(str(py_file.relative_to(self.root_path)))
                        except (FileNotFoundError, OSError):
                            # Skip files that can't be accessed
                            continue

        return modules

    def _analyze_module(self, module_path: str) -> ModuleMetrics:
        """Analyze a single module for production readiness."""
        file_path = self.root_path / module_path

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Basic metrics
        lines_of_code = len([line for line in content.split('\n') if line.strip()])

        # Parse AST for complexity analysis
        try:
            tree = ast.parse(content)
            complexity_score = self._calculate_complexity(tree)
        except Exception as e:
            complexity_score = 0

        # Analyze various aspects
        test_coverage = self._estimate_test_coverage(module_path)
        documentation_score = self._analyze_documentation(content)
        dependency_count = self._count_dependencies(content)
        performance_profile = self._analyze_performance_profile(content)
        error_handling_score = self._analyze_error_handling(content)
        security_score = self._analyze_security(content)

        # Calculate overall enterprise readiness
        enterprise_score = self._calculate_enterprise_readiness(
            test_coverage, documentation_score, error_handling_score,
            security_score, complexity_score, lines_of_code
        )

        return ModuleMetrics(
            path=module_path,
            name=Path(module_path).stem,
            lines_of_code=lines_of_code,
            test_coverage=test_coverage,
            complexity_score=complexity_score,
            documentation_score=documentation_score,
            dependency_count=dependency_count,
            performance_profile=performance_profile,
            error_handling_score=error_handling_score,
            security_score=security_score,
            enterprise_readiness_score=enterprise_score
        )

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity score."""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _estimate_test_coverage(self, module_path: str) -> float:
        """Estimate test coverage for a module."""
        # Look for corresponding test files
        test_patterns = [
            f"tests/**/test_{Path(module_path).stem}.py",
            f"tests/**/{Path(module_path).stem}_test.py",
            f"test_{Path(module_path).stem}.py"
        ]

        test_files_found = 0
        for pattern in test_patterns:
            test_files = list(self.root_path.glob(pattern))
            test_files_found += len(test_files)

        # Rough estimation based on test file presence and naming
        if test_files_found >= 2:
            return 0.85  # High coverage likely
        elif test_files_found == 1:
            return 0.60  # Medium coverage likely
        else:
            return 0.20  # Low/no coverage

    def _analyze_documentation(self, content: str) -> float:
        """Analyze documentation quality."""
        doc_score = 0.0

        # Check for module docstring
        if '"""' in content[:500]:
            doc_score += 0.3

        # Check for class/function docstrings
        docstring_count = content.count('"""') + content.count("'''")
        if docstring_count >= 4:
            doc_score += 0.4
        elif docstring_count >= 2:
            doc_score += 0.2

        # Check for type hints
        if ': ' in content or '->' in content:
            doc_score += 0.2

        # Check for comprehensive comments
        comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
        total_lines = len(content.split('\n'))
        if total_lines > 0 and comment_lines / total_lines > 0.1:
            doc_score += 0.1

        return min(doc_score, 1.0)

    def _count_dependencies(self, content: str) -> int:
        """Count module dependencies."""
        import_count = 0
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                import_count += 1
        return import_count

    def _analyze_performance_profile(self, content: str) -> Dict[str, any]:
        """Analyze performance characteristics."""
        profile = {
            "async_operations": 'async ' in content,
            "performance_optimizations": any(opt in content for opt in ['cache', 'optimize', 'performance']),
            "database_operations": any(db in content for db in ['sql', 'database', 'query']),
            "network_operations": any(net in content for net in ['http', 'request', 'socket']),
            "memory_management": any(mem in content for mem in ['gc.', 'memory', 'buffer']),
            "estimated_latency_category": "low" if "async" in content else "medium"
        }
        return profile

    def _analyze_error_handling(self, content: str) -> float:
        """Analyze error handling quality."""
        error_score = 0.0

        # Check for try/except blocks
        try_count = content.count('try:')
        except_count = content.count('except')

        if try_count > 0 and except_count >= try_count:
            error_score += 0.4

        # Check for logging
        if any(log in content for log in ['logging', 'logger', 'log.']):
            error_score += 0.2

        # Check for specific exception handling
        if 'Exception' in content:
            error_score += 0.2

        # Check for validation
        if any(val in content for val in ['validate', 'assert', 'raise']):
            error_score += 0.2

        return min(error_score, 1.0)

    def _analyze_security(self, content: str) -> float:
        """Analyze security considerations."""
        security_score = 0.0

        # Check for security imports
        security_imports = ['cryptography', 'hashlib', 'secrets', 'ssl']
        if any(sec in content for sec in security_imports):
            security_score += 0.3

        # Check for input validation
        if any(val in content for val in ['validate', 'sanitize', 'escape']):
            security_score += 0.3

        # Check for no hardcoded secrets (good practice)
        if not any(bad in content.lower() for bad in ['password=', 'token=', 'key=', 'secret=']):
            security_score += 0.2

        # Check for proper authentication patterns
        if any(auth in content for auth in ['authenticate', 'authorize', 'permission']):
            security_score += 0.2

        return min(security_score, 1.0)

    def _calculate_enterprise_readiness(
        self, test_coverage: float, doc_score: float, error_score: float,
        security_score: float, complexity: int, loc: int
    ) -> float:
        """Calculate overall enterprise readiness score."""

        # Weighted scoring
        weights = {
            'test_coverage': 0.25,
            'documentation': 0.20,
            'error_handling': 0.20,
            'security': 0.15,
            'complexity': 0.10,
            'size': 0.10
        }

        # Normalize complexity (lower is better)
        complexity_normalized = max(0, 1 - (complexity - 10) / 50) if complexity > 10 else 1

        # Normalize size (moderate size preferred)
        size_normalized = 1.0
        if loc < 50:
            size_normalized = 0.7  # Too small
        elif loc > 1000:
            size_normalized = 0.8  # Maybe too large

        score = (
            weights['test_coverage'] * test_coverage +
            weights['documentation'] * doc_score +
            weights['error_handling'] * error_score +
            weights['security'] * security_score +
            weights['complexity'] * complexity_normalized +
            weights['size'] * size_normalized
        )

        return min(score, 1.0)

    def _assign_lane(self, metrics: ModuleMetrics) -> LaneAssignment:
        """Assign appropriate lane based on metrics."""
        score = metrics.enterprise_readiness_score
        current_lane = self._detect_current_lane(metrics.path)

        # Determine recommended lane
        if score >= self.lane_thresholds["ACCEPTED"]:
            recommended_lane = "ACCEPTED"
        elif score >= self.lane_thresholds["LUKHAS"]:
            recommended_lane = "LUKHAS"
        elif score >= self.lane_thresholds["CANDIDATE"]:
            recommended_lane = "CANDIDATE"
        else:
            recommended_lane = "RESEARCH"

        # Identify blockers and requirements
        blockers = []
        requirements = []

        if metrics.test_coverage < 0.7:
            blockers.append(f"Test coverage {metrics.test_coverage:.1%} < 70%")
            requirements.append("Increase test coverage to >70%")

        if metrics.documentation_score < 0.6:
            blockers.append(f"Documentation score {metrics.documentation_score:.1%} < 60%")
            requirements.append("Improve documentation with docstrings and type hints")

        if metrics.error_handling_score < 0.5:
            blockers.append(f"Error handling score {metrics.error_handling_score:.1%} < 50%")
            requirements.append("Add comprehensive error handling and logging")

        if metrics.complexity_score > 20:
            blockers.append(f"Complexity score {metrics.complexity_score} > 20")
            requirements.append("Refactor to reduce complexity")

        # Estimate completion time
        blocker_count = len(blockers)
        target_days = min(30, blocker_count * 5 + 5)  # 5-30 days

        return LaneAssignment(
            module_path=metrics.path,
            current_lane=current_lane,
            recommended_lane=recommended_lane,
            readiness_score=score,
            promotion_blockers=blockers,
            promotion_requirements=requirements,
            target_completion_days=target_days
        )

    def _detect_current_lane(self, module_path: str) -> str:
        """Detect current lane from file path."""
        if module_path.startswith("lukhas/"):
            return "LUKHAS"
        elif module_path.startswith("candidate/"):
            return "CANDIDATE"
        elif module_path.startswith("accepted/"):
            return "ACCEPTED"
        else:
            return "RESEARCH"

    def _generate_summary(self) -> Dict[str, any]:
        """Generate audit summary statistics."""
        lane_counts = defaultdict(int)
        readiness_scores = []

        for assignment in self.lane_assignments.values():
            lane_counts[assignment.recommended_lane] += 1
            readiness_scores.append(assignment.readiness_score)

        avg_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else 0

        return {
            "total_modules": len(self.module_metrics),
            "average_readiness_score": avg_readiness,
            "lane_distribution": dict(lane_counts),
            "promotion_candidates": len([a for a in self.lane_assignments.values()
                                       if a.current_lane != a.recommended_lane and
                                       a.readiness_score > 0.6]),
            "enterprise_ready": len([a for a in self.lane_assignments.values()
                                   if a.readiness_score > 0.9])
        }

    def _generate_recommendations(self) -> Dict[str, any]:
        """Generate specific recommendations for improvement."""
        recommendations = {
            "high_priority": [],
            "medium_priority": [],
            "quick_wins": [],
            "strategic_improvements": []
        }

        for assignment in self.lane_assignments.values():
            module_name = Path(assignment.module_path).stem

            if assignment.readiness_score > 0.8 and assignment.promotion_blockers:
                recommendations["quick_wins"].append({
                    "module": module_name,
                    "current_score": assignment.readiness_score,
                    "blockers": assignment.promotion_blockers[:2],  # Top 2
                    "estimated_effort": "1-2 days"
                })

            elif assignment.readiness_score > 0.6:
                recommendations["medium_priority"].append({
                    "module": module_name,
                    "current_score": assignment.readiness_score,
                    "target_lane": assignment.recommended_lane,
                    "key_requirements": assignment.promotion_requirements[:3]
                })

            elif assignment.current_lane in ["LUKHAS", "CANDIDATE"]:
                recommendations["high_priority"].append({
                    "module": module_name,
                    "current_score": assignment.readiness_score,
                    "critical_issues": assignment.promotion_blockers,
                    "risk": "Production readiness below expectations"
                })

        # Strategic recommendations
        luke_modules = [a for a in self.lane_assignments.values() if a.current_lane == "LUKHAS"]
        enterprise_ready = len([a for a in luke_modules if a.readiness_score > 0.9])

        if enterprise_ready < len(luke_modules) * 0.7:
            recommendations["strategic_improvements"].append({
                "area": "LUKHAS Lane Quality",
                "issue": f"Only {enterprise_ready}/{len(luke_modules)} LUKHAS modules enterprise-ready",
                "recommendation": "Focus on bringing LUKHAS modules to >90% readiness"
            })

        return recommendations

    def _generate_promotion_plan(self) -> Dict[str, any]:
        """Generate systematic promotion plan."""
        promotion_plan = {
            "immediate_promotions": [],
            "30_day_plan": [],
            "90_day_plan": [],
            "strategic_initiatives": []
        }

        for assignment in self.lane_assignments.values():
            if (assignment.current_lane != assignment.recommended_lane and
                assignment.readiness_score > 0.85):
                promotion_plan["immediate_promotions"].append({
                    "module": Path(assignment.module_path).stem,
                    "from": assignment.current_lane,
                    "to": assignment.recommended_lane,
                    "score": assignment.readiness_score,
                    "minor_blockers": assignment.promotion_blockers
                })

            elif assignment.target_completion_days <= 30:
                promotion_plan["30_day_plan"].append({
                    "module": Path(assignment.module_path).stem,
                    "target_lane": assignment.recommended_lane,
                    "requirements": assignment.promotion_requirements,
                    "estimated_days": assignment.target_completion_days
                })

            elif assignment.readiness_score > 0.4:
                promotion_plan["90_day_plan"].append({
                    "module": Path(assignment.module_path).stem,
                    "target_lane": assignment.recommended_lane,
                    "major_improvements": assignment.promotion_requirements
                })

        return promotion_plan

    def save_audit_report(self, audit_results: Dict[str, any], filename: str = "lane_assignment_audit.json"):
        """Save audit results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(audit_results, f, indent=2, default=str)
        print(f"📋 Lane assignment audit report saved to {filename}")

def main():
    """Run the lane assignment audit."""
    auditor = LaneAssignmentAuditor()
    results = auditor.audit_codebase()

    # Print summary
    summary = results["summary"]
    print("\n🎯 T4/0.01% Lane Assignment Audit Summary")
    print("=" * 50)
    print(f"📊 Total modules analyzed: {summary['total_modules']}")
    print(f"📈 Average readiness score: {summary['average_readiness_score']:.1%}")
    print(f"🏆 Enterprise-ready modules: {summary['enterprise_ready']}")
    print(f"📋 Promotion candidates: {summary['promotion_candidates']}")
    print("\n📍 Lane Distribution:")
    for lane, count in summary['lane_distribution'].items():
        print(f"  {lane}: {count} modules")

    # Print recommendations
    recs = results["recommendations"]
    print("\n🎯 Key Recommendations:")
    if recs["quick_wins"]:
        print(f"  ⚡ Quick wins: {len(recs['quick_wins'])} modules")
    if recs["high_priority"]:
        print(f"  🔥 High priority: {len(recs['high_priority'])} modules")

    # Save detailed report
    auditor.save_audit_report(results)

    print("\n✅ Lane assignment audit completed!")
    print("📋 Detailed report saved to lane_assignment_audit.json")

if __name__ == "__main__":
    main()
