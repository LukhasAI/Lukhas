# Lane Debt Analyzer Skill

Lane-aware technical debt analysis and prioritization based on promotion readiness, architectural impact, and constellation alignment.

## Reasoning

1. 2,414 TODOs/FIXMEs across 999 files with no intelligent prioritization - developers waste time on low-impact debt.
2. Some debt blocks candidate→lukhas promotion (import violations, missing tests) while other debt can be deferred.
3. No visibility into which TODOs must be resolved for lane promotion vs. which are low-priority refactorings.
4. Current systems treat all debt equally - need lane-aware classification considering promotion, test coverage, guardian alignment.
5. Debt trends unknown - is technical debt growing or shrinking per lane? Which lanes are accumulating debt fastest?

## Actions

### Core Analyzer System

```python
#!/usr/bin/env python3
"""
Lane Debt Analyzer - Promotion-Ready Technical Debt Intelligence

Lane-aware debt prioritization:
- Blocker vs. important vs. defer classification
- Promotion-readiness scoring
- Lane-specific debt reports
- Trend analysis
- Integration with lane promotion orchestrator
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Set
from collections import defaultdict
import json

@dataclass
class DebtItem:
    file_path: str
    line_number: int
    lane: str
    debt_type: str  # 'TODO', 'FIXME', 'HACK', 'XXX', 'BUG'
    content: str
    priority: str = 'defer'  # 'blocker', 'important', 'defer'
    blocks_promotion: bool = False
    impact_score: float = 0.0

@dataclass
class LaneDebtReport:
    lane: str
    total_debt: int
    blockers: int
    important: int
    deferred: int
    top_blockers: List[DebtItem] = field(default_factory=list)
    trend: str = 'stable'  # 'increasing', 'decreasing', 'stable'

class LaneDebtAnalyzer:
    DEBT_PATTERNS = {
        'TODO': r'#\s*TODO[:\s]+(.+)',
        'FIXME': r'#\s*FIXME[:\s]+(.+)',
        'HACK': r'#\s*HACK[:\s]+(.+)',
        'XXX': r'#\s*XXX[:\s]+(.+)',
        'BUG': r'#\s*BUG[:\s]+(.+)'
    }

    PROMOTION_BLOCKERS = [
        r'import.*from\s+lukhas',  # candidate importing lukhas (lane violation)
        r'TODO.*before.*promotion',
        r'FIXME.*circular',
        r'TODO.*test\s+coverage',
        r'FIXME.*performance'
    ]

    def __init__(self):
        self.debt_items: List[DebtItem] = []
        self.lane_reports: Dict[str, LaneDebtReport] = {}

    def scan_technical_debt(self, paths: List[str] = None) -> List[DebtItem]:
        """Find all TODOs, FIXMEs, HACKs with context"""
        if paths is None:
            paths = ['candidate/', 'core/', 'lukhas/', 'matriz/']

        self.debt_items = []

        for path_str in paths:
            path = Path(path_str)
            if not path.exists():
                continue

            for py_file in path.rglob('*.py'):
                # Skip test files, __pycache__, etc.
                if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                    continue

                self._scan_file(py_file)

        return self.debt_items

    def _scan_file(self, file_path: Path):
        """Scan single file for debt markers"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception:
            return

        lane = self._detect_lane(file_path)

        for line_num, line in enumerate(lines, 1):
            for debt_type, pattern in self.DEBT_PATTERNS.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    content = match.group(1).strip()

                    debt_item = DebtItem(
                        file_path=str(file_path),
                        line_number=line_num,
                        lane=lane,
                        debt_type=debt_type,
                        content=content
                    )

                    # Classify
                    self._classify_debt(debt_item)

                    self.debt_items.append(debt_item)

    def _detect_lane(self, file_path: Path) -> str:
        """Detect which lane file belongs to"""
        parts = file_path.parts
        for lane in ['candidate', 'core', 'lukhas', 'products', 'matriz']:
            if lane in parts:
                return lane
        return 'other'

    def _classify_debt(self, debt: DebtItem):
        """Classify debt urgency and impact"""
        content_lower = debt.content.lower()

        # Check if blocks promotion
        for blocker_pattern in self.PROMOTION_BLOCKERS:
            if re.search(blocker_pattern, debt.content, re.IGNORECASE):
                debt.blocks_promotion = True
                debt.priority = 'blocker'
                debt.impact_score = 10.0
                return

        # Important debt indicators
        important_keywords = ['security', 'guardian', 'ethics', 'performance', 'memory leak']
        if any(kw in content_lower for kw in important_keywords):
            debt.priority = 'important'
            debt.impact_score = 5.0
            return

        # Critical debt types
        if debt.debt_type in ['FIXME', 'BUG']:
            debt.priority = 'important'
            debt.impact_score = 4.0
            return

        # Default: defer
        debt.priority = 'defer'
        debt.impact_score = 1.0

    def generate_lane_debt_report(self, lane: str) -> LaneDebtReport:
        """Show debt blocking promotion with prioritization"""
        lane_debt = [d for d in self.debt_items if d.lane == lane]

        report = LaneDebtReport(
            lane=lane,
            total_debt=len(lane_debt),
            blockers=sum(1 for d in lane_debt if d.priority == 'blocker'),
            important=sum(1 for d in lane_debt if d.priority == 'important'),
            deferred=sum(1 for d in lane_debt if d.priority == 'defer')
        )

        # Top blockers
        blockers = [d for d in lane_debt if d.priority == 'blocker']
        blockers.sort(key=lambda x: x.impact_score, reverse=True)
        report.top_blockers = blockers[:10]

        self.lane_reports[lane] = report
        return report

    def track_debt_trends(self, historical_data: Dict) -> Dict[str, str]:
        """Detect if debt is increasing or decreasing per lane"""
        trends = {}

        for lane in ['candidate', 'core', 'lukhas']:
            current = len([d for d in self.debt_items if d.lane == lane])
            previous = historical_data.get(lane, {}).get('total_debt', current)

            if current > previous * 1.1:
                trends[lane] = 'increasing'
            elif current < previous * 0.9:
                trends[lane] = 'decreasing'
            else:
                trends[lane] = 'stable'

        return trends

    def integrate_with_promotion_orchestrator(self, module_path: str) -> Dict:
        """Auto-flag blocking debt when promotion requested"""
        module_debt = [
            d for d in self.debt_items
            if module_path in d.file_path and d.blocks_promotion
        ]

        if module_debt:
            return {
                'promotion_blocked': True,
                'blocking_debt_count': len(module_debt),
                'blockers': [
                    {
                        'file': d.file_path,
                        'line': d.line_number,
                        'content': d.content
                    }
                    for d in module_debt
                ]
            }

        return {'promotion_blocked': False}

    def export_report(self, output_format='json'):
        """Export comprehensive debt analysis"""
        report = {
            'total_debt': len(self.debt_items),
            'by_lane': {},
            'by_priority': defaultdict(int),
            'blocking_promotion': []
        }

        for debt in self.debt_items:
            report['by_priority'][debt.priority] += 1

            if debt.blocks_promotion:
                report['blocking_promotion'].append({
                    'file': debt.file_path,
                    'line': debt.line_number,
                    'content': debt.content,
                    'lane': debt.lane
                })

        for lane in ['candidate', 'core', 'lukhas']:
            lane_report = self.generate_lane_debt_report(lane)
            report['by_lane'][lane] = {
                'total': lane_report.total_debt,
                'blockers': lane_report.blockers,
                'important': lane_report.important,
                'deferred': lane_report.deferred
            }

        return json.dumps(report, indent=2)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Lane Debt Analyzer')
    parser.add_argument('--scan', nargs='+', default=['candidate/', 'core/', 'lukhas/'],
                       help='Paths to scan')
    parser.add_argument('--lane', help='Generate report for specific lane')
    parser.add_argument('--export', action='store_true', help='Export JSON report')
    args = parser.parse_args()

    analyzer = LaneDebtAnalyzer()

    print("🔍 Scanning technical debt...")
    analyzer.scan_technical_debt(args.scan)

    if args.lane:
        print(f"\n📊 Lane Report: {args.lane}")
        report = analyzer.generate_lane_debt_report(args.lane)
        print(f"Total debt: {report.total_debt}")
        print(f"Blockers: {report.blockers}")
        print(f"Important: {report.important}")
        print(f"Deferred: {report.deferred}")

        if report.top_blockers:
            print("\n⚠️  Top Blockers:")
            for blocker in report.top_blockers[:5]:
                print(f"  {blocker.file_path}:{blocker.line_number}")
                print(f"    {blocker.content}")

    if args.export:
        print(analyzer.export_report())
```

### Makefile Integration

```makefile
debt-analyze:
	@python3 tools/lane_debt_analyzer.py --scan candidate/ core/ lukhas/

debt-report-candidate:
	@python3 tools/lane_debt_analyzer.py --scan candidate/ --lane candidate

debt-export:
	@python3 tools/lane_debt_analyzer.py --scan candidate/ core/ lukhas/ --export > debt_report.json

debt-blockers:
	@python3 tools/lane_debt_analyzer.py --scan candidate/ --lane candidate | grep -A 20 "Top Blockers"
```

### Integration with Lane Promotion

```python
# In lane_promotion_orchestrator.py
from lane_debt_analyzer import LaneDebtAnalyzer

def check_promotion_blockers(module_path: str):
    analyzer = LaneDebtAnalyzer()
    analyzer.scan_technical_debt(['candidate/'])

    result = analyzer.integrate_with_promotion_orchestrator(module_path)

    if result['promotion_blocked']:
        raise ValueError(
            f"Promotion blocked by {result['blocking_debt_count']} debt items. "
            "Fix blockers before promoting."
        )
```

## Context References

- `/candidate/claude.me`
- `/lukhas/claude.me`
- `/MODULE_INDEX.md`
