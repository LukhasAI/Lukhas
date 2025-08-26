# Development Dashboards

**LUKHAS AI Development and Monitoring Dashboards**

## 📊 **Dashboard Files (Moved from `/web/`)**

### **Available Dashboards**
- **`approver_ui.html`**: Approval workflow interface
- **`cockpit.html`**: System monitoring cockpit
- **`trace_drilldown.html`**: Trace analysis and audit visualization
- **`provenance-client.js`**: Provenance system client-side functionality

## 🎯 **Purpose**
These development dashboards provide:
- **System Monitoring**: Real-time system status and metrics
- **Audit Trails**: Trace analysis and provenance tracking
- **Approval Workflows**: Administrative and governance interfaces
- **Development Tools**: Debugging and analysis interfaces

## 🔧 **Usage**

### **Local Development**
```bash
# Serve dashboards locally
python -m http.server 8080 --directory tools/dashboards

# Access dashboards
open http://localhost:8080/cockpit.html
open http://localhost:8080/trace_drilldown.html
```

### **Integration with LUKHAS Systems**
- **Trace Drilldown**: Connects to provenance API for audit visualization
- **Cockpit**: System monitoring integration
- **Approver UI**: Governance workflow integration

## 📁 **Organization Change**
- **Previous Location**: `/web/` (root level)
- **New Location**: `/tools/dashboards/` (organized under development tools)
- **Reason**: Better categorization as development/monitoring tools

## 🔗 **Related Systems**
- **Provenance API**: `qi/provenance/receipts_api.py`
- **Audit System**: Guardian System monitoring
- **Governance**: Approval workflow integration

---

**Development Dashboards - Professional Monitoring and Debug Tools**

*Moved from root `/web/` to organized `/tools/dashboards/` location*

*Last updated: August 2024*
