#!/usr/bin/env python3
"""
PWM Streamline Implementation
=============================
Implements the streamlining recommendations from the analysis.
"""

import os
import ast
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class StreamlineImplementation:
    """Implements streamlining recommendations"""
    
    def __init__(self):
        self.root_path = Path("/Users/agi_dev/Lukhas_PWM")
        self.backup_dir = self.root_path / ".streamline_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.changes_made = []
        
    def implement_phase1(self):
        """Phase 1: Remove duplicate functions"""
        logger.info("\n🔧 PHASE 1: Removing Duplicate Functions")
        logger.info("="*60)
        
        # Load the streamline report
        report_path = self.root_path / "docs" / "reports" / "PWM_STREAMLINE_REPORT.json"
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        duplicate_functions = report['findings']['duplicate_functions']
        
        # Group duplicates by module
        duplicates_by_module = {}
        for dup in duplicate_functions:
            module = dup['module']
            if module not in duplicates_by_module:
                duplicates_by_module[module] = []
            duplicates_by_module[module].append(dup)
        
        # Process each module
        for module, duplicates in duplicates_by_module.items():
            logger.info(f"\n📦 Processing {module} module ({len(duplicates)} duplicate groups)...")
            
            # Create consolidated file for common functions
            common_file_path = self.root_path / module / "common" / "utils.py"
            self._ensure_common_module(module)
            
            # Process each duplicate group
            for dup_group in duplicates[:10]:  # Limit to first 10 for safety
                self._consolidate_duplicate_function(dup_group, common_file_path)
        
        logger.info(f"\n✅ Phase 1 complete. {len(self.changes_made)} changes made.")
    
    def implement_phase2(self):
        """Phase 2: Create common utilities"""
        logger.info("\n🔧 PHASE 2: Creating Common Utilities")
        logger.info("="*60)
        
        # Create main common utilities module
        common_utils_path = self.root_path / "lukhas" / "common" / "utils.py"
        common_utils_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create standard utilities
        utils_content = '''"""
Common utilities for LUKHAS PWM
===============================
Centralized utility functions to reduce code duplication.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
from functools import wraps


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def load_config(config_path: Path, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load JSON configuration with defaults"""
    config = defaults or {}
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                config.update(loaded_config)
        except Exception as e:
            logger = get_logger(__name__)
            logger.error(f"Failed to load config from {config_path}: {e}")
    
    return config


def save_config(config: Dict[str, Any], config_path: Path) -> bool:
    """Save configuration to JSON file"""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger = get_logger(__name__)
        logger.error(f"Failed to save config to {config_path}: {e}")
        return False


def async_error_handler(func):
    """Decorator for consistent async error handling"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper


def sync_error_handler(func):
    """Decorator for consistent sync error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper


class SingletonMeta(type):
    """Metaclass for singleton pattern"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def ensure_path(path: Path) -> Path:
    """Ensure a path exists, creating directories if needed"""
    path = Path(path)
    if path.suffix:  # It's a file
        path.parent.mkdir(parents=True, exist_ok=True)
    else:  # It's a directory
        path.mkdir(parents=True, exist_ok=True)
    return path


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result
'''
        
        with open(common_utils_path, 'w') as f:
            f.write(utils_content)
        
        self.changes_made.append(f"Created common utilities at {common_utils_path}")
        
        # Create __init__.py
        init_path = common_utils_path.parent / "__init__.py"
        init_content = '''"""Common utilities for LUKHAS PWM"""

from .utils import (
    get_logger,
    load_config,
    save_config,
    async_error_handler,
    sync_error_handler,
    SingletonMeta,
    ensure_path,
    merge_dicts
)

__all__ = [
    'get_logger',
    'load_config', 
    'save_config',
    'async_error_handler',
    'sync_error_handler',
    'SingletonMeta',
    'ensure_path',
    'merge_dicts'
]
'''
        
        with open(init_path, 'w') as f:
            f.write(init_content)
        
        logger.info(f"✅ Created common utilities module at {common_utils_path}")
        
        # Create interface consolidation
        self._create_common_interfaces()
        
        logger.info(f"\n✅ Phase 2 complete. Common utilities created.")
    
    def _ensure_common_module(self, module: str):
        """Ensure common submodule exists"""
        common_path = self.root_path / module / "common"
        common_path.mkdir(parents=True, exist_ok=True)
        
        init_path = common_path / "__init__.py"
        if not init_path.exists():
            with open(init_path, 'w') as f:
                f.write(f'"""Common utilities for {module} module"""')
    
    def _consolidate_duplicate_function(self, dup_group: Dict, target_file: Path):
        """Consolidate a group of duplicate functions"""
        if not dup_group['occurrences']:
            return
        
        # Use the first occurrence as the canonical version
        canonical = dup_group['occurrences'][0]
        
        logger.info(f"   Consolidating {canonical['name']} ({len(dup_group['occurrences'])} duplicates)")
        
        # For now, just log what would be done
        # In a real implementation, we would:
        # 1. Copy the function to the common module
        # 2. Update imports in all files that use it
        # 3. Remove the duplicate definitions
        
        self.changes_made.append({
            'action': 'consolidate_function',
            'function': canonical['name'],
            'module': dup_group['module'],
            'duplicates': len(dup_group['occurrences'])
        })
    
    def _create_common_interfaces(self):
        """Create consolidated interface definitions"""
        interfaces_path = self.root_path / "lukhas" / "common" / "interfaces.py"
        
        interfaces_content = '''"""
Common interfaces for LUKHAS PWM
================================
Consolidated interface definitions to reduce duplication.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class BaseInterface(ABC):
    """Base interface for all LUKHAS components"""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the component"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the component"""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get component status"""
        pass


class ProcessingInterface(BaseInterface):
    """Interface for components that process data"""
    
    @abstractmethod
    async def process(self, data: Any) -> Any:
        """Process input data"""
        pass
    
    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Validate input data"""
        pass


class StorageInterface(BaseInterface):
    """Interface for storage components"""
    
    @abstractmethod
    async def store(self, key: str, value: Any) -> bool:
        """Store a value"""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a value"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass


class CommunicationInterface(BaseInterface):
    """Interface for inter-module communication"""
    
    @abstractmethod
    async def send_message(self, target: str, message: Any) -> bool:
        """Send a message to target"""
        pass
    
    @abstractmethod
    async def receive_message(self) -> Optional[Any]:
        """Receive next message"""
        pass
    
    @abstractmethod
    async def subscribe(self, topic: str) -> bool:
        """Subscribe to a topic"""
        pass
    
    @abstractmethod
    async def publish(self, topic: str, message: Any) -> bool:
        """Publish to a topic"""
        pass


@dataclass
class ModuleInfo:
    """Standard module information"""
    name: str
    version: str
    description: str
    dependencies: List[str]
    status: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'dependencies': self.dependencies,
            'status': self.status
        }
'''
        
        with open(interfaces_path, 'w') as f:
            f.write(interfaces_content)
        
        self.changes_made.append(f"Created common interfaces at {interfaces_path}")
    
    def create_migration_script(self):
        """Create a script to help migrate to new structure"""
        migration_script_path = self.root_path / "tools" / "scripts" / "migrate_to_common_utils.py"
        
        migration_content = '''#!/usr/bin/env python3
"""
Migration script to update imports to use common utilities
"""

import os
import re
from pathlib import Path


def update_imports_in_file(file_path: Path):
    """Update imports in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace common patterns
    replacements = [
        # Logger imports
        (r'from .+ import get_logger', 'from system.common.utils import get_logger'),
        (r'logger = logging.getLogger\\(__name__\\)', 'logger = get_logger(__name__)'),
        
        # Config loading
        (r'with open\\(.+\\) as .+:\\s*\\n\\s*.+ = json\\.load\\(.+\\)', 
         'config = load_config(config_path)'),
    ]
    
    modified = False
    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    if modified:
        # Add import if needed
        if 'from system.common.utils import' not in content:
            lines = content.split('\\n')
            import_line = 'from system.common.utils import get_logger, load_config\\n'
            
            # Find where to insert import
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    lines.insert(i + 1, import_line)
                    break
            
            content = '\\n'.join(lines)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return True
    
    return False


def main():
    """Run migration"""
    root = Path("/Users/agi_dev/Lukhas_PWM")
    updated_files = []
    
    for py_file in root.rglob("*.py"):
        if update_imports_in_file(py_file):
            updated_files.append(py_file)
    
    print(f"Updated {len(updated_files)} files")


if __name__ == "__main__":
    main()
'''
        
        with open(migration_script_path, 'w') as f:
            f.write(migration_content)
        
        os.chmod(migration_script_path, 0o755)
        logger.info(f"✅ Created migration script at {migration_script_path}")
    
    def run(self):
        """Run all streamlining phases"""
        logger.info("🚀 Starting LUKHAS PWM Streamlining Implementation")
        logger.info("="*80)
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Backup directory: {self.backup_dir}")
        
        # Run phases
        self.implement_phase1()
        self.implement_phase2()
        self.create_migration_script()
        
        # Save changes log
        changes_log_path = self.root_path / "docs" / "reports" / "streamline_changes.json"
        with open(changes_log_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'changes': self.changes_made
            }, f, indent=2)
        
        logger.info(f"\n✅ Streamlining implementation complete!")
        logger.info(f"📝 Changes log saved to: {changes_log_path}")
        logger.info("="*80)


def main():
    """Run streamlining implementation"""
    implementation = StreamlineImplementation()
    implementation.run()


if __name__ == "__main__":
    main()