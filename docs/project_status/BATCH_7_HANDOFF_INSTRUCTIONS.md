---
status: wip
type: documentation
owner: unknown
module: project_status
redirect: false
moved_to: null
---

# BATCH 7 Agent Handoff Instructions
**Agent Assignment**: Configuration & Logging Systems
**Priority**: 🟠 MEDIUM - Infrastructure
**Status**: 75% Complete - **Final Sprint Required**
**Generated**: August 25, 2025

## 🎯 **MISSION: Complete BATCH 7 Configuration & Logging Infrastructure**

You're taking over a **75% complete** batch that has substantial infrastructure already built. Your job is to **finish the remaining 25%** and integrate everything properly.

---

## 📊 **Current Status: What's Already Done**

### ✅ **COMPLETED - Don't Recreate These**
1. **ΛTRACE Functionality** ✅ - Working in `candidate/core/glyph/api_manager.py`
2. **Monitoring Infrastructure** ✅ - Complete system in `candidate/monitoring/`
3. **Configuration Loading** ✅ - `candidate/monitoring/config_loader.py`
4. **Metrics Collection** ✅ - `candidate/monitoring/adaptive_metrics_collector.py`
5. **Structured Logging** ✅ - Implemented in multiple files

### 🔍 **Evidence of Existing Work**
```bash
# Verify these exist (they do):
ls -la candidate/monitoring/  # 20+ monitoring files
grep -r "ΛTRACE" candidate/core/glyph/api_manager.py  # ΛTRACE working
find candidate/ -name "*config*" -name "*.py"  # Config files exist
```

---

## 🎯 **YOUR TASKS: Complete These 6 Items**

### **Task 1: Create Missing File Structure** ⭐ **HIGH PRIORITY**
The original BATCH 7 spec requires specific file names. Create these files that redirect to existing functionality:

```python
# candidate/config/configuration_manager.py
"""
Configuration Manager - BATCH 7 Completion
Redirects to existing config functionality
"""
from candidate.monitoring.config_loader import ConfigLoader
from pathlib import Path

class ConfigurationManager:
    """Unified configuration management for LUKHAS"""

    def __init__(self):
        self.config_loader = ConfigLoader()
        self.config_path = Path("candidate/config")
        self.config_path.mkdir(exist_ok=True)

    def load_dynamic_config(self, config_name: str):
        """Load configuration dynamically"""
        return self.config_loader.load_config(config_name)

    def reload_config(self):
        """Reload all configurations"""
        return self.config_loader.reload()

    def get_config(self, key: str, default=None):
        """Get configuration value"""
        return self.config_loader.get(key, default)

# Usage example
if __name__ == "__main__":
    config_manager = ConfigurationManager()
    print("✅ Configuration Manager working")
```

### **Task 2: Create Settings Validator** ⭐ **MEDIUM PRIORITY**
```python
# candidate/config/settings_validator.py
"""
Settings Validator - BATCH 7 Completion
"""
import os
import json
from typing import Dict, Any, List
from pathlib import Path

class SettingsValidator:
    """Validate LUKHAS configuration settings"""

    def __init__(self):
        self.validation_rules = {
            "api_keys": self._validate_api_keys,
            "paths": self._validate_paths,
            "thresholds": self._validate_thresholds,
            "features": self._validate_features
        }

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate configuration and return errors"""
        errors = {}

        for section, validator in self.validation_rules.items():
            if section in config:
                section_errors = validator(config[section])
                if section_errors:
                    errors[section] = section_errors

        return errors

    def _validate_api_keys(self, keys: Dict) -> List[str]:
        """Validate API keys configuration"""
        errors = []
        required_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]

        for key in required_keys:
            if key not in keys or not keys[key]:
                errors.append(f"Missing required API key: {key}")

        return errors

    def _validate_paths(self, paths: Dict) -> List[str]:
        """Validate file paths"""
        errors = []
        for name, path in paths.items():
            if not Path(path).exists():
                errors.append(f"Path does not exist: {name} -> {path}")
        return errors

    def _validate_thresholds(self, thresholds: Dict) -> List[str]:
        """Validate threshold values"""
        errors = []
        for name, value in thresholds.items():
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"Invalid threshold: {name} = {value}")
        return errors

    def _validate_features(self, features: Dict) -> List[str]:
        """Validate feature flags"""
        errors = []
        for name, enabled in features.items():
            if not isinstance(enabled, bool):
                errors.append(f"Feature flag must be boolean: {name} = {enabled}")
        return errors

# Usage example
if __name__ == "__main__":
    validator = SettingsValidator()
    test_config = {
        "api_keys": {"OPENAI_API_KEY": "test"},
        "thresholds": {"drift_threshold": 0.15}
    }
    errors = validator.validate_config(test_config)
    print(f"Validation errors: {errors}")
```

### **Task 3: Create Environment Manager** ⭐ **MEDIUM PRIORITY**
```python
# candidate/config/environment_manager.py
"""
Environment Manager - BATCH 7 Completion
"""
import os
from enum import Enum
from typing import Dict, Any
from pathlib import Path

class Environment(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class EnvironmentManager:
    """Manage environment-specific configurations"""

    def __init__(self):
        self.current_env = self._detect_environment()
        self.config_dir = Path("candidate/config/environments")
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _detect_environment(self) -> Environment:
        """Detect current environment"""
        env_name = os.getenv("LUKHAS_ENV", "development").lower()
        try:
            return Environment(env_name)
        except ValueError:
            return Environment.DEVELOPMENT

    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        config_file = self.config_dir / f"{self.current_env.value}.json"

        if config_file.exists():
            import json
            with open(config_file, 'r') as f:
                return json.load(f)

        # Default configurations
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for current environment"""
        base_config = {
            "logging_level": "INFO",
            "debug_mode": False,
            "features": {
                "ai_analysis": True,
                "matrix_instrumentation": True
            }
        }

        if self.current_env == Environment.DEVELOPMENT:
            base_config.update({
                "logging_level": "DEBUG",
                "debug_mode": True,
                "features": {"ai_analysis": True}
            })
        elif self.current_env == Environment.PRODUCTION:
            base_config.update({
                "logging_level": "WARNING",
                "debug_mode": False,
                "features": {"performance_monitoring": True}
            })

        return base_config

    def set_environment(self, env: Environment):
        """Set current environment"""
        self.current_env = env
        os.environ["LUKHAS_ENV"] = env.value

# Usage example
if __name__ == "__main__":
    env_manager = EnvironmentManager()
    config = env_manager.get_environment_config()
    print(f"Environment: {env_manager.current_env}")
    print(f"Config: {config}")
```

### **Task 4: Create Structured Logger Integration** ⭐ **HIGH PRIORITY**
```python
# candidate/logging/structured_logger.py
"""
Structured Logger - BATCH 7 Completion
Integrates with existing monitoring infrastructure
"""
import structlog
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    """Unified structured logging for LUKHAS"""

    def __init__(self, component: str = "lukhas"):
        self.component = component
        self.setup_structlog()
        self.logger = structlog.get_logger(component)

        # Integration with existing monitoring
        self._integrate_with_monitoring()

    def setup_structlog(self):
        """Configure structlog"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def _integrate_with_monitoring(self):
        """Integrate with existing monitoring system"""
        try:
            from candidate.monitoring.adaptive_metrics_collector import MetricsCollector
            self.metrics = MetricsCollector()
        except ImportError:
            self.metrics = None

    def log_event(self, level: str, message: str, **kwargs):
        """Log structured event"""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": self.component,
            "message": message,
            **kwargs
        }

        # Send to metrics if available
        if self.metrics:
            self.metrics.record_event(event_data)

        # Log structured message
        getattr(self.logger, level.lower())(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log_event("INFO", message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log_event("ERROR", message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log_event("WARNING", message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log_event("DEBUG", message, **kwargs)

# Global logger instance
lukhas_logger = StructuredLogger("lukhas")

# Usage example
if __name__ == "__main__":
    logger = StructuredLogger("test")
    logger.info("BATCH 7 structured logging working",
                component="batch_7",
                task="completion_test")
```

### **Task 5: Create Log Aggregator** ⭐ **MEDIUM PRIORITY**
```python
# candidate/logging/log_aggregator.py
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
```

### **Task 6: Integration Test** ⭐ **HIGH PRIORITY**
```python
# candidate/logging/integration_test.py
"""
BATCH 7 Integration Test - Verify Everything Works Together
"""
def test_batch_7_completion():
    """Test all BATCH 7 components work together"""

    print("🧪 BATCH 7 Integration Test Starting...")

    # Test 1: Configuration Manager
    try:
        from candidate.config.configuration_manager import ConfigurationManager
        config_manager = ConfigurationManager()
        print("✅ Configuration Manager: Working")
    except Exception as e:
        print(f"❌ Configuration Manager: {e}")

    # Test 2: Settings Validator
    try:
        from candidate.config.settings_validator import SettingsValidator
        validator = SettingsValidator()
        print("✅ Settings Validator: Working")
    except Exception as e:
        print(f"❌ Settings Validator: {e}")

    # Test 3: Environment Manager
    try:
        from candidate.config.environment_manager import EnvironmentManager
        env_manager = EnvironmentManager()
        print(f"✅ Environment Manager: Working ({env_manager.current_env})")
    except Exception as e:
        print(f"❌ Environment Manager: {e}")

    # Test 4: Structured Logger
    try:
        from candidate.logging.structured_logger import StructuredLogger
        logger = StructuredLogger("test")
        logger.info("BATCH 7 test log", batch=7, status="testing")
        print("✅ Structured Logger: Working")
    except Exception as e:
        print(f"❌ Structured Logger: {e}")

    # Test 5: Log Aggregator
    try:
        from candidate.logging.log_aggregator import LogAggregator
        aggregator = LogAggregator()
        report = aggregator.generate_report(1)
        print("✅ Log Aggregator: Working")
    except Exception as e:
        print(f"❌ Log Aggregator: {e}")

    # Test 6: ΛTRACE functionality (existing)
    try:
        import candidate.core.glyph.api_manager
        print("✅ ΛTRACE System: Working (existing)")
    except Exception as e:
        print(f"❌ ΛTRACE System: {e}")

    # Test 7: Monitoring Integration (existing)
    try:
        from candidate.monitoring.adaptive_metrics_collector import MetricsCollector
        metrics = MetricsCollector()
        print("✅ Monitoring System: Working (existing)")
    except Exception as e:
        print(f"❌ Monitoring System: {e}")

    print("🎉 BATCH 7 Integration Test Complete!")

if __name__ == "__main__":
    test_batch_7_completion()
```

---

## 🚀 **Execution Plan for New Agent**

### **Step 1: Create Directory Structure** (2 minutes)
```bash
mkdir -p candidate/config
mkdir -p candidate/logging
```

### **Step 2: Create the 5 Required Files** (15 minutes)
Copy the code above for each file:
1. `candidate/config/configuration_manager.py`
2. `candidate/config/settings_validator.py`
3. `candidate/config/environment_manager.py`
4. `candidate/logging/structured_logger.py`
5. `candidate/logging/log_aggregator.py`

### **Step 3: Run Integration Test** (5 minutes)
```bash
cd candidate/logging
python integration_test.py
```

### **Step 4: Fix Any Issues** (8 minutes)
- Address import errors
- Fix missing dependencies
- Ensure all tests pass

### **Step 5: Create Completion Report** (5 minutes)
Document what you completed and test results.

---

## ✅ **Success Criteria**

**BATCH 7 is COMPLETE when:**
1. ✅ All 5 new files created and working
2. ✅ Integration test passes (all ✅, no ❌)
3. ✅ Existing monitoring system still works
4. ✅ ΛTRACE functionality preserved
5. ✅ No import errors in the codebase

---

## 🆘 **If You Get Stuck**

### **Common Issues & Solutions:**

1. **Import Errors**:
   ```bash
   # Fix with:
   export PYTHONPATH=/Users/agi_dev/LOCAL-REPOS/Lukhas:$PYTHONPATH
   ```

2. **Missing Dependencies**:
   ```bash
   pip install structlog
   ```

3. **File Permissions**:
   ```bash
   chmod +x candidate/logging/integration_test.py
   ```

### **Get Help:**
- Look at existing files in `candidate/monitoring/` for patterns
- Check `candidate/core/glyph/api_manager.py` for ΛTRACE examples
- All the hard work is done - you're just creating the final interfaces!

---

## 🎯 **Estimated Time: 35 minutes total**

**This is achievable!** The infrastructure exists, you're just creating the final integration layer. Focus on creating working code that connects to existing systems.

**Good luck! 🚀**
