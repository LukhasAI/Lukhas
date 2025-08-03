# Import Migration Guide

After the directory reorganization, update imports as follows:

## Module Moves

### From root to core module:
```python
# OLD
from architectures import something
from orchestration import something
from symbolic import something

# NEW
from core.architectures import something
from core.orchestration import something
from core.symbolic_legacy import something
```

### From root to consciousness module:
```python
# OLD
from creativity import something
from dream import something
from reasoning import something

# NEW
from consciousness.creativity import something
from consciousness.dream import something
from consciousness.reasoning import something
```

### From root to other modules:
```python
# OLD
from api import something
from bio import something
from ethics import something
from identity import something
from learning import something
from voice import something

# NEW
from bridge.api_legacy import something
from qim.bio_legacy import something
from governance.ethics_legacy import something
from governance.identity import something
from memory.learning import something
from bridge.voice import something
```

## Archived Directories

The following directories have been archived and should not be imported:
- health_reports
- misc
- quarantine
- security
- trace
- _context_

## Tools Consolidation

```python
# OLD
from analysis_tools import something
from healing import something

# NEW
from tools.legacy_analysis import something
from tools.healing import something
```

## Automated Import Update

Run this command to find all files needing import updates:
```bash
grep -r "from \(api\|architectures\|bio\|creativity\|dream\|ethics\|identity\|learning\|orchestration\|reasoning\|symbolic\|voice\) import" . --include="*.py"
```
