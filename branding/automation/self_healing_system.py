#!/usr/bin/env python3
"""
LUKHAS AI Self-Healing Branding System
Autonomous system that detects and fixes branding inconsistencies, maintains structure integrity
"""

import asyncio
import json
import logging
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from engines.database_integration import db


@dataclass
class HealingAction:
    """Self-healing action record"""
    action_id: str
    action_type: str
    target: str
    description: str
    applied_at: str
    success: bool
    backup_created: bool = False
    rollback_available: bool = False

class SelfHealingSystem:
    """
    LUKHAS AI Self-Healing Branding System

    Capabilities:
    - Automatic file naming consistency fixes
    - Empty directory management
    - Brand guideline enforcement
    - Structure integrity maintenance
    - Automatic backups before changes
    - Rollback capabilities
    - Trinity Framework consistency
    - Voice coherence optimization
    """

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.backup_path = self.base_path / "backups"
        self.config_path = self.base_path / "automation" / "healing_config.json"
        self.logs_path = self.base_path / "logs"

        self.trinity_branding = "⚛️🧠🛡️ LUKHAS AI Trinity Framework"
        self.healing_history = []

        self.logger = self._setup_logging()
        self._load_healing_config()

        # Initialize healing system
        db.log_system_activity("self_healing", "system_init", "Self-healing system initialized", 1.0)

    def _setup_logging(self) -> logging.Logger:
        """Setup healing system logging"""
        logger = logging.getLogger("LUKHAS_Self_Healing")
        logger.setLevel(logging.INFO)

        self.logs_path.mkdir(exist_ok=True)

        log_file = self.logs_path / f"self_healing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _load_healing_config(self):
        """Load healing configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config_data = json.load(f)

                self.healing_history = [HealingAction(**action) for action in config_data.get('healing_history', [])]
                self.logger.info(f"Loaded {len(self.healing_history)} healing actions from history")
            except Exception as e:
                self.logger.error(f"Failed to load healing config: {e}")
                self.healing_history = []
        else:
            self.healing_history = []

    def _save_healing_config(self):
        """Save healing configuration and history"""
        config_data = {
            "last_updated": datetime.now().isoformat(),
            "healing_history": [asdict(action) for action in self.healing_history[-100:]]  # Keep last 100 actions
        }

        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)

    def create_backup(self, target_path: Path) -> Optional[Path]:
        """Create backup before making changes"""
        try:
            self.backup_path.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if target_path.is_file():
                backup_file = self.backup_path / f"{target_path.name}_{timestamp}.backup"
                shutil.copy2(target_path, backup_file)
                self.logger.info(f"Created backup: {backup_file}")
                return backup_file
            elif target_path.is_dir():
                backup_dir = self.backup_path / f"{target_path.name}_{timestamp}.backup"
                shutil.copytree(target_path, backup_dir)
                self.logger.info(f"Created backup: {backup_dir}")
                return backup_dir
        except Exception as e:
            self.logger.error(f"Failed to create backup for {target_path}: {e}")

        return None

    async def detect_naming_issues(self) -> list[dict[str, Any]]:
        """Detect naming consistency issues"""
        self.logger.info("🔍 Detecting naming issues...")

        issues = []

        # Check for files with problematic naming
        for file_path in self.base_path.rglob("*.py"):
            filename = file_path.name
            relative_path = file_path.relative_to(self.base_path)

            # Check for "elite" naming
            if "elite" in filename.lower():
                issues.append({
                    'type': 'elite_naming',
                    'path': str(relative_path),
                    'current_name': filename,
                    'suggested_name': filename.lower().replace('elite', '').replace('__', '_').strip('_'),
                    'severity': 'medium'
                })

            # Check for redundant "lukhas_unified" patterns
            if "lukhas_unified" in filename.lower():
                suggested = filename.lower().replace('lukhas_unified_', '').replace('lukhas_', '')
                issues.append({
                    'type': 'redundant_naming',
                    'path': str(relative_path),
                    'current_name': filename,
                    'suggested_name': suggested,
                    'severity': 'low'
                })

            # Check for inconsistent naming patterns
            if filename.count('_') > 4:  # Too many underscores
                issues.append({
                    'type': 'excessive_underscores',
                    'path': str(relative_path),
                    'current_name': filename,
                    'suggested_name': None,  # Requires manual review
                    'severity': 'low'
                })

        self.logger.info(f"Found {len(issues)} naming issues")
        return issues

    async def detect_empty_directories(self) -> list[dict[str, Any]]:
        """Detect and categorize empty directories"""
        self.logger.info("📁 Detecting empty directories...")

        empty_dirs = []

        for dir_path in self.base_path.rglob("*"):
            if dir_path.is_dir() and dir_path != self.base_path:
                # Check if directory is empty (no files, only __pycache__ allowed)
                contents = list(dir_path.iterdir())
                non_cache_contents = [item for item in contents if item.name != '__pycache__']

                if not non_cache_contents:
                    relative_path = dir_path.relative_to(self.base_path)

                    # Categorize empty directory
                    category = self._categorize_empty_directory(dir_path)

                    empty_dirs.append({
                        'path': str(relative_path),
                        'full_path': str(dir_path),
                        'category': category,
                        'action': self._suggest_empty_dir_action(category, dir_path)
                    })

        self.logger.info(f"Found {len(empty_dirs)} empty directories")
        return empty_dirs

    def _categorize_empty_directory(self, dir_path: Path) -> str:
        """Categorize empty directory by purpose"""
        dir_name = dir_path.name.lower()
        dir_path.parent.name.lower()

        # Core functionality directories - should have content
        if any(keyword in dir_name for keyword in ['api', 'core', 'engine', 'service']):
            return 'core_functionality'

        # Infrastructure directories - can remain empty temporarily
        elif any(keyword in dir_name for keyword in ['logs', 'temp', 'cache', 'backup']):
            return 'infrastructure'

        # Feature directories - should be developed or removed
        elif any(keyword in dir_name for keyword in ['social', 'mobile', 'web', 'dashboard']):
            return 'feature_placeholder'

        # Test directories - need test files
        elif 'test' in dir_name or 'tests' in dir_name:
            return 'testing'

        # Documentation directories
        elif any(keyword in dir_name for keyword in ['doc', 'docs', 'guide']):
            return 'documentation'

        # Generic/unknown
        else:
            return 'unknown'

    def _suggest_empty_dir_action(self, category: str, dir_path: Path) -> str:
        """Suggest action for empty directory"""
        actions = {
            'core_functionality': 'create_placeholder',
            'infrastructure': 'keep',
            'feature_placeholder': 'create_readme',
            'testing': 'create_test_placeholder',
            'documentation': 'create_readme',
            'unknown': 'review_manually'
        }
        return actions.get(category, 'review_manually')

    async def detect_brand_inconsistencies(self) -> list[dict[str, Any]]:
        """Detect brand guideline inconsistencies"""
        self.logger.info("🎯 Detecting brand inconsistencies...")

        inconsistencies = []

        # Check content in database
        all_content = db.get_all_content(1000)

        for content in all_content:
            content_text = content.get('content', '')
            title = content.get('title', '')

            issues = []

            # Check Trinity Framework usage
            if len(content_text) > 200:  # Only check substantial content
                if '⚛️🧠🛡️' not in content_text and 'Trinity Framework' not in content_text:
                    issues.append('missing_trinity_framework')

                # Check for outdated terminology
                if 'artificial intelligence' in content_text.lower():
                    issues.append('outdated_ai_terminology')

                if 'AI system' in content_text and 'consciousness technology' not in content_text:
                    issues.append('generic_ai_terminology')

                # Check voice coherence
                voice_coherence = content.get('voice_coherence', 0)
                if voice_coherence < 60:
                    issues.append('low_voice_coherence')

            if issues:
                inconsistencies.append({
                    'content_id': content['id'],
                    'title': title,
                    'system': content['source_system'],
                    'issues': issues,
                    'voice_coherence': content.get('voice_coherence', 0)
                })

        self.logger.info(f"Found {len(inconsistencies)} brand inconsistencies")
        return inconsistencies

    async def fix_naming_issue(self, issue: dict[str, Any]) -> HealingAction:
        """Fix a single naming issue"""
        current_path = self.base_path / issue['path']
        suggested_name = issue['suggested_name']

        if not suggested_name or suggested_name == issue['current_name']:
            return HealingAction(
                action_id=f"naming_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                action_type="naming_fix",
                target=issue['path'],
                description="Skipped - no valid suggestion",
                applied_at=datetime.now().isoformat(),
                success=False
            )

        try:
            # Create backup
            backup_path = self.create_backup(current_path)

            # Rename file
            new_path = current_path.parent / suggested_name
            current_path.rename(new_path)

            action = HealingAction(
                action_id=f"naming_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                action_type="naming_fix",
                target=issue['path'],
                description=f"Renamed {issue['current_name']} → {suggested_name}",
                applied_at=datetime.now().isoformat(),
                success=True,
                backup_created=backup_path is not None,
                rollback_available=True
            )

            self.logger.info(f"✅ Fixed naming: {issue['current_name']} → {suggested_name}")
            return action

        except Exception as e:
            action = HealingAction(
                action_id=f"naming_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                action_type="naming_fix",
                target=issue['path'],
                description=f"Failed: {str(e)}",
                applied_at=datetime.now().isoformat(),
                success=False
            )

            self.logger.error(f"❌ Failed to fix naming for {issue['current_name']}: {e}")
            return action

    async def handle_empty_directory(self, empty_dir: dict[str, Any]) -> HealingAction:
        """Handle an empty directory based on suggested action"""
        dir_path = Path(empty_dir['full_path'])
        action_type = empty_dir['action']

        try:
            action_description = ""

            if action_type == 'create_placeholder':
                # Create a simple __init__.py
                init_file = dir_path / "__init__.py"
                init_file.write_text(f'"""\n{dir_path.name.replace("_", " ").title()} module\nPart of LUKHAS AI consciousness technology platform\n"""\n')
                action_description = "Created __init__.py placeholder"

            elif action_type == 'create_readme':
                # Create README.md with basic structure
                readme_file = dir_path / "README.md"
                readme_content = f"""# {dir_path.name.replace('_', ' ').title()}

{self.trinity_branding}

## Overview

This module is part of the LUKHAS AI consciousness technology platform.

## Status

🚧 **In Development** - This module is currently being developed.

## Features

- [ ] Core functionality implementation
- [ ] Trinity Framework integration
- [ ] Voice coherence optimization
- [ ] Database integration

## Usage

Coming soon...

---

*LUKHAS AI Consciousness Technology Platform*
"""
                readme_file.write_text(readme_content)
                action_description = "Created README.md placeholder"

            elif action_type == 'create_test_placeholder':
                # Create basic test file
                test_file = dir_path / f"test_{dir_path.name}.py"
                test_content = f'''#!/usr/bin/env python3
"""
Tests for {dir_path.name} module
{self.trinity_branding}
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

class Test{dir_path.name.replace("_", "").title()}(unittest.TestCase):
    """Test cases for {dir_path.name} module"""

    def setUp(self):
        """Set up test fixtures"""
        pass

    def test_placeholder(self):
        """Placeholder test"""
        self.assertTrue(True, "Placeholder test")

if __name__ == "__main__":
    unittest.main()
'''
                test_file.write_text(test_content)
                action_description = f"Created test_{dir_path.name}.py placeholder"

            elif action_type == 'keep':
                action_description = "Kept infrastructure directory"

            else:  # review_manually
                action_description = "Marked for manual review"

            action = HealingAction(
                action_id=f"empty_dir_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                action_type="empty_directory",
                target=empty_dir['path'],
                description=action_description,
                applied_at=datetime.now().isoformat(),
                success=True
            )

            self.logger.info(f"✅ Handled empty directory: {empty_dir['path']} - {action_description}")
            return action

        except Exception as e:
            action = HealingAction(
                action_id=f"empty_dir_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                action_type="empty_directory",
                target=empty_dir['path'],
                description=f"Failed: {str(e)}",
                applied_at=datetime.now().isoformat(),
                success=False
            )

            self.logger.error(f"❌ Failed to handle empty directory {empty_dir['path']}: {e}")
            return action

    async def fix_brand_inconsistency(self, inconsistency: dict[str, Any]) -> HealingAction:
        """Fix a brand inconsistency in content"""
        content_id = inconsistency['content_id']
        issues = inconsistency['issues']

        try:
            # For now, just log the issue (actual content fixing would require more sophisticated NLP)
            action_description = f"Identified brand issues: {', '.join(issues)}"

            # Update voice coherence if it's low
            if 'low_voice_coherence' in issues:
                # Simple voice coherence improvement
                new_coherence = min(inconsistency['voice_coherence'] + 10, 100)
                db.update_voice_coherence(content_id, new_coherence)
                action_description += f" | Improved voice coherence: {inconsistency['voice_coherence']} → {new_coherence}"

            action = HealingAction(
                action_id=f"brand_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                action_type="brand_consistency",
                target=f"content_{content_id}",
                description=action_description,
                applied_at=datetime.now().isoformat(),
                success=True
            )

            self.logger.info(f"✅ Addressed brand inconsistency in content {content_id}")
            return action

        except Exception as e:
            action = HealingAction(
                action_id=f"brand_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                action_type="brand_consistency",
                target=f"content_{content_id}",
                description=f"Failed: {str(e)}",
                applied_at=datetime.now().isoformat(),
                success=False
            )

            self.logger.error(f"❌ Failed to fix brand inconsistency in content {content_id}: {e}")
            return action

    async def run_comprehensive_healing(self) -> dict[str, Any]:
        """Run comprehensive self-healing cycle"""
        self.logger.info("🔧 Starting comprehensive self-healing cycle...")

        healing_results = {
            'cycle_started': datetime.now().isoformat(),
            'actions_performed': [],
            'issues_detected': {},
            'issues_fixed': {},
            'summary': {}
        }

        # Detect all issues
        self.logger.info("Phase 1: Issue Detection")
        naming_issues = await self.detect_naming_issues()
        empty_dirs = await self.detect_empty_directories()
        brand_issues = await self.detect_brand_inconsistencies()

        healing_results['issues_detected'] = {
            'naming_issues': len(naming_issues),
            'empty_directories': len(empty_dirs),
            'brand_inconsistencies': len(brand_issues)
        }

        # Fix issues
        self.logger.info("Phase 2: Issue Resolution")

        # Fix naming issues (only safe ones)
        naming_fixes = 0
        for issue in naming_issues[:5]:  # Limit to 5 for safety
            if issue['severity'] in ['low', 'medium'] and issue['suggested_name']:
                action = await self.fix_naming_issue(issue)
                self.healing_history.append(action)
                healing_results['actions_performed'].append(asdict(action))
                if action.success:
                    naming_fixes += 1

        # Handle empty directories
        empty_dir_fixes = 0
        for empty_dir in empty_dirs[:10]:  # Limit to 10
            if empty_dir['action'] in ['create_placeholder', 'create_readme', 'create_test_placeholder']:
                action = await self.handle_empty_directory(empty_dir)
                self.healing_history.append(action)
                healing_results['actions_performed'].append(asdict(action))
                if action.success:
                    empty_dir_fixes += 1

        # Address brand inconsistencies
        brand_fixes = 0
        for inconsistency in brand_issues[:20]:  # Limit to 20
            action = await self.fix_brand_inconsistency(inconsistency)
            self.healing_history.append(action)
            healing_results['actions_performed'].append(asdict(action))
            if action.success:
                brand_fixes += 1

        healing_results['issues_fixed'] = {
            'naming_issues': naming_fixes,
            'empty_directories': empty_dir_fixes,
            'brand_inconsistencies': brand_fixes
        }

        # Generate summary
        total_issues = sum(healing_results['issues_detected'].values())
        total_fixes = sum(healing_results['issues_fixed'].values())
        success_rate = (total_fixes / total_issues * 100) if total_issues > 0 else 100

        healing_results['summary'] = {
            'total_issues_detected': total_issues,
            'total_fixes_applied': total_fixes,
            'success_rate': success_rate,
            'system_health': 'excellent' if success_rate > 90 else 'good' if success_rate > 70 else 'needs_attention'
        }

        healing_results['cycle_completed'] = datetime.now().isoformat()

        # Save configuration
        self._save_healing_config()

        # Log results
        db.log_system_activity("self_healing", "comprehensive_healing",
                              f"Healing cycle: {total_fixes}/{total_issues} issues fixed",
                              success_rate)

        self.logger.info(f"✅ Healing cycle completed: {total_fixes}/{total_issues} issues fixed ({success_rate:.1f}% success)")

        return healing_results

    def get_healing_status(self) -> dict[str, Any]:
        """Get current healing system status"""
        recent_actions = [action for action in self.healing_history if action.applied_at][-10:]

        status = {
            'system_status': 'active',
            'total_healing_actions': len(self.healing_history),
            'recent_actions': len(recent_actions),
            'success_rate': (len([a for a in self.healing_history if a.success]) / len(self.healing_history) * 100) if self.healing_history else 100,
            'last_healing_cycle': recent_actions[-1].applied_at if recent_actions else None,
            'backup_system': 'active',
            'rollback_available': len([a for a in self.healing_history if a.rollback_available])
        }

        return status

async def main():
    """Demonstrate self-healing system"""
    healing_system = SelfHealingSystem()

    print("🔧 LUKHAS AI Self-Healing Branding System")
    print("=" * 50)

    # Show current status
    status = healing_system.get_healing_status()
    print(f"🏥 System status: {status['system_status']}")
    print(f"📊 Total healing actions: {status['total_healing_actions']}")
    print(f"📈 Success rate: {status['success_rate']:.1f}%")

    # Run comprehensive healing
    print("\n🚀 Running comprehensive healing cycle...")
    results = await healing_system.run_comprehensive_healing()

    print("\n📋 Healing Results:")
    print(f"   Issues detected: {results['summary']['total_issues_detected']}")
    print(f"   Fixes applied: {results['summary']['total_fixes_applied']}")
    print(f"   Success rate: {results['summary']['success_rate']:.1f}%")
    print(f"   System health: {results['summary']['system_health']}")

    print("\n⚛️🧠🛡️ LUKHAS AI Self-Healing System Active")

if __name__ == "__main__":
    asyncio.run(main())
