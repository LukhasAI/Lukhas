import streamlit as st
import time
class ComplianceMonitor:
    def __init__(self):
        self.drift_score = 0.0  # Starts at 0 (fully compliant)
        self.drift_threshold = 0.3  # Example threshold for recalibration
        self.critical_threshold = 0.6  # Escalate to human oversight

    def evaluate_decision(self, decision_compliance):
        """
        decision_compliance: float between 0 (non-compliant) and 1 (fully compliant)
        """
        drift_increment = 1 - decision_compliance  # Higher non-compliance = more drift
        self.drift_score += drift_increment * 0.1  # Drift accumulates slowly

        # Log decision
        print(f"Decision compliance: {decision_compliance:.2f}, Drift increment: {drift_increment:.2f}")
        print(f"Updated drift score: {self.drift_score:.2f}")
        self.log_drift_event(decision_compliance, drift_increment)

        # Check thresholds
        if self.drift_score >= self.critical_threshold:
            self.escalate_to_human()
        elif self.drift_score >= self.drift_threshold:
            self.recalibrate()

    def recalibrate(self):
        print("⚠️ Drift threshold exceeded. Initiating self-recalibration...")
        # Example recalibration: reduce drift
        self.drift_score *= 0.5
        print(f"Drift score after recalibration: {self.drift_score:.2f}")

    def escalate_to_human(self):
        print("🚨 Critical drift detected! Escalating to human oversight.")

    def log_drift_event(self, decision_compliance, drift_increment):
        """
        Logs drift events to the compliance log file.
        """
        import json
        from datetime import datetime, timezone
        from pathlib import Path

        log_path = Path("../../logs/compliance/compliance_log_2025_04_28.json")
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_compliance": decision_compliance,
            "drift_increment": drift_increment,
            "cumulative_drift_score": self.drift_score,
        }

        # Append to log file
        if log_path.exists():
            with open(log_path, "r+") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []
                data.append(event)
                file.seek(0)
                json.dump(data, file, indent=4)
        else:
            with open(log_path, "w") as file:
                json.dump([event], file, indent=4)
