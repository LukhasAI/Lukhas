"""
Log Aggregator - BATCH 7 Completion
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Iterator
from collections import defaultdict

class LogAggregator:
    """Aggregate and analyze logs from multiple sources"""

    def __init__(self, log_directory: str = "logs"):
        self.log_dir = Path(log_directory)
        self.log_dir.mkdir(exist_ok=True)

        # Integration with existing systems
        self._setup_integrations()

    def _setup_integrations(self):
        """Setup integrations with existing monitoring"""
        try:
            from candidate.monitoring.real_data_collector import DataCollector
            self.data_collector = DataCollector()
        except ImportError:
            self.data_collector = None

    def collect_logs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Collect logs from last N hours"""
        logs = []
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Collect from log files
        for log_file in self.log_dir.glob("*.jsonl"):
            logs.extend(self._read_log_file(log_file, cutoff))

        # Collect from monitoring system
        if self.data_collector:
            logs.extend(self._collect_monitoring_logs(cutoff))

        return sorted(logs, key=lambda x: x.get('timestamp', ''))

    def _read_log_file(self, log_file: Path, cutoff: datetime) -> List[Dict]:
        """Read structured log file"""
        logs = []
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        if self._is_recent_log(log_entry, cutoff):
                            logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass
        return logs

    def _is_recent_log(self, log_entry: Dict, cutoff: datetime) -> bool:
        """Check if log entry is recent enough"""
        timestamp_str = log_entry.get('timestamp', '')
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return timestamp >= cutoff
        except (ValueError, TypeError):
            return True  # Include if we can't parse timestamp

    def _collect_monitoring_logs(self, cutoff: datetime) -> List[Dict]:
        """Collect logs from monitoring system"""
        if not self.data_collector:
            return []

        # This would integrate with existing monitoring
        return []

    def aggregate_by_component(self, logs: List[Dict]) -> Dict[str, List[Dict]]:
        """Aggregate logs by component"""
        aggregated = defaultdict(list)
        for log in logs:
            component = log.get('component', 'unknown')
            aggregated[component].append(log)
        return dict(aggregated)

    def get_error_summary(self, logs: List[Dict]) -> Dict[str, int]:
        """Get summary of errors"""
        error_counts = defaultdict(int)
        for log in logs:
            if log.get('level', '').upper() in ['ERROR', 'CRITICAL']:
                error_type = log.get('message', 'unknown_error')
                error_counts[error_type] += 1
        return dict(error_counts)

    def generate_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate aggregated log report"""
        logs = self.collect_logs(hours)

        return {
            "period": f"Last {hours} hours",
            "total_logs": len(logs),
            "by_component": {k: len(v) for k, v in self.aggregate_by_component(logs).items()},
            "error_summary": self.get_error_summary(logs),
            "generated_at": datetime.utcnow().isoformat()
        }

# Usage example
if __name__ == "__main__":
    aggregator = LogAggregator()
    report = aggregator.generate_report(24)
    print(f"Log report: {json.dumps(report, indent=2)}")
