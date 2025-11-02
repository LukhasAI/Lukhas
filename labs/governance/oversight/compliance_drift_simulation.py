import pandas as pd
from lucas_governance.compliance_drift_monitor import ComplianceMonitor

# Initialize the compliance monitor with jurisdiction context

# TAG:governance
# TAG:oversight
# TAG:neuroplastic
# TAG:colony


monitor = ComplianceMonitor(subsystem="ethics_engine", location="EU")

# Simulate compliance scores over time (0 = full drift, 1 = full compliance)
compliance_scores = [1.0, 0.98, 0.92, 0.87, 0.75, 0.68, 0.5, 0.3]

results = []
for score in compliance_scores:
    status = monitor.evaluate_decision(score)
results.append({"score": score, "status": status})

# Display results

df = pd.DataFrame(results)
df
