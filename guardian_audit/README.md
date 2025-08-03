# 🛡️ Guardian Audit Submodule

**Purpose**: Complete audit trail and analysis tools for the LUKHAS Guardian System  
**Version**: Phase 5 - Guardian Integration  
**Classification**: Security & Compliance  

## 📁 Directory Structure

```
guardian_audit/
├── logs/           # Raw symbolic intervention logs
├── exports/        # Processed audit data and reports
├── visualizations/ # Glyph traceback and drift visualizations  
├── replay/         # Drift event replay tools
└── README.md       # This file
```

## 🎯 Core Functions

### 🔍 **Audit Logging**
- All Guardian interventions logged with symbolic context
- Timestamp, threat type, severity, and glyph sequences preserved
- Causal chain tracking for complex threat scenarios

### 📊 **Export Capabilities**
- JSON export from `sentinel.py` for external analysis
- CSV format for spreadsheet analysis
- GraphQL-ready structured data

### 🌀 **Visualization Tools**
- Glyph traceback visualization showing intervention chains
- Drift event timelines with symbolic state transitions
- Guardian response effectiveness metrics

### 🔄 **Replay System**
- Recreate historical drift events for analysis
- Test Guardian response under controlled conditions
- Validate intervention rule effectiveness

## 🚀 Quick Start

```bash
# Generate current audit export
python exports/generate_audit_export.py

# Visualize recent interventions
python visualizations/glyph_traceback.py --hours 24

# Replay a specific drift event
python replay/replay_drift.py --event-id drift_spike_20250804_013000
```

## 🧬 Symbolic Integration

All audit data preserves LUKHAS symbolic context:
- **🔐→🔓**: Authentication state changes
- **🌪️→🌀→🌿**: Drift stabilization sequences  
- **🚨→🔒→🛡️**: Emergency lockdown procedures
- **💎→🔮→🌫️**: Coherence degradation patterns

## 📋 Compliance Features

- **Retention**: 90-day audit log retention (configurable)
- **Integrity**: SHA3-512 hashing of all log entries
- **Privacy**: GDPR-compliant data handling
- **Access**: Role-based audit access controls

---

**Guardian System**: Autonomous protection through symbolic intelligence  
**Audit Trail**: Complete transparency for production trust