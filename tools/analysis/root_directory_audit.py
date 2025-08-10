#!/usr/bin/env python3
"""
LUKHAS PWM Root Directory Audit and Reorganization Plan
Analyzes all root directories and creates a comprehensive reorganization plan
"""

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class RootDirectoryAuditor:

    def __init__(self):
        # Define our 7 core modules
        self.core_modules = [
    'core',
    'consciousness',
    'memory',
    'qim',
    'emotion',
    'governance',
     'bridge']

        # Define what should stay at root
        self.essential_root = [
            '.git', '.github', '.venv', 'docs', 'tests', 'tools', 'deployments',
            '.gitignore', 'README.md', 'LICENSE', 'requirements.txt',
            'main.py', 'CLAUDE.md', '.env.example'
        ]

        # Categorize directories
        self.categories = {
            'core_modules': [],
            'should_be_submodules': [],
            'tools_and_utils': [],
            'documentation': [],
            'testing': [],
            'deployment': [],
            'archive_candidates': [],
            'unknown_purpose': []
        }

        self.directory_analysis = {}

        def analyze_root(self):
            """Analyze all root-level directories"""
        root_items = os.listdir('.')
        directories = [d for d in root_items if os.path.isdir(
            d) and not d.startswith('.')]

        print(f"📊 Found {len(directories)} directories at root level")

            for directory in sorted(directories):
            self.analyze_directory(directory)

                return self.generate_reorganization_plan()

            def analyze_directory(self, directory):
                """Analyze a single directory"""
        analysis = {
            'name': directory,
            'size': self.get_directory_size(directory),
            'file_count': self.count_files(directory),
            'has_init': os.path.exists(os.path.join(directory, '__init__.py')),
            'has_readme': os.path.exists(os.path.join(directory, 'README.md')),
            'has_tests': self.has_tests(directory),
            'suggested_action': '',
            'suggested_location': '',
            'reason': ''
        }

        # Categorize based on name and content
                if directory in self.core_modules:
            self.categories['core_modules'].append(directory)
            analysis['suggested_action'] = 'ENHANCE'
            analysis['reason'] = 'Core module - needs docs, tests, examples'

                    elif directory in ['api', 'architectures', 'bio', 'creativity',
    'dream',
                    'ethics', 'identity', 'learning', 'orchestration',
                    'reasoning', 'symbolic', 'voice']:
            self.categories['should_be_submodules'].append(directory)
            analysis['suggested_action'] = 'MERGE'
            analysis['suggested_location'] = self.suggest_module_for_directory(directory)
            analysis['reason'] = f'Should be part of {analysis["suggested_location"]} module'

                    elif directory in ['tools', 'analysis_tools', 'healing']:
            self.categories['tools_and_utils'].append(directory)
            analysis['suggested_action'] = 'CONSOLIDATE'
            analysis['suggested_location'] = 'tools/'
            analysis['reason'] = 'Utility/tool - consolidate into tools/'

                        elif directory in ['docs', 'deployments', 'config']:
            self.categories['documentation'].append(directory)
            analysis['suggested_action'] = 'KEEP'
            analysis['reason'] = 'Essential root directory'

                            elif directory in ['tests', 'red_team', 'compliance']:
            self.categories['testing'].append(directory)
            analysis['suggested_action'] = 'REORGANIZE'
            analysis['suggested_location'] = 'tests/'
            analysis['reason'] = 'Testing related - consolidate into tests/'

                                elif directory in ['misc', 'trace', '_context_',
    'security']:
            self.categories['archive_candidates'].append(directory)
            analysis['suggested_action'] = 'ARCHIVE'
            analysis['reason'] = 'Unclear purpose - candidate for archival'

                                    else:
            self.categories['unknown_purpose'].append(directory)
            analysis['suggested_action'] = 'REVIEW'
            analysis['reason'] = 'Unknown purpose - needs manual review'

        self.directory_analysis[directory] = analysis

                                        def suggest_module_for_directory(self,
    directory):
                                            """Suggest which core module a directory should belong to"""
        mappings = {
            'api': 'bridge',
            'architectures': 'core',
            'bio': 'qim',
            'creativity': 'consciousness',
            'dream': 'consciousness',
            'ethics': 'governance',
            'identity': 'governance',
            'learning': 'memory',
            'orchestration': 'core',
            'reasoning': 'consciousness',
            'symbolic': 'core',
            'voice': 'bridge'
        }
                                            return mappings.get(directory, 'core')

                                        def get_directory_size(self, directory):
                                            """Get size of directory in MB"""
        total_size = 0
                                            try:
                                                for dirpath, dirnames, filenames in os.walk(directory):
                                                    for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                                                        if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
                                                            except Exception:
                                                                pass
                                                            return round(total_size / 1024 / 1024, 2)

                                                        def count_files(self,
    directory):
                                                            """Count Python files in directory"""
        count = 0
                                                            try:
                                                                for root, dirs,
    files in os.walk(directory):
                count += sum(1 for f in files if f.endswith('.py'))
                                                                    except Exception:
                                                                        pass
                                                                    return count

                                                                def has_tests(self,
    directory):
                                                                    """Check if directory has tests"""
        test_dir = os.path.join(directory, 'tests')
                                                                    if os.path.exists(test_dir):
                                                                        return True

        # Check for test files
                                                                    try:
                                                                        for root, dirs,
    files in os.walk(directory):
                                                                            if any(f.startswith('test_') and f.endswith('.py') for f in files):
                                                                                return True
                                                                            except Exception:
                                                                                pass
                                                                            return False

                                                                        def generate_reorganization_plan(self):
                                                                            """Generate comprehensive reorganization plan"""
        plan = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_directories': len(self.directory_analysis),
                'core_modules': len(self.categories['core_modules']),
                'to_merge': len(self.categories['should_be_submodules']),
                'to_archive': len(self.categories['archive_candidates']),
                'to_review': len(self.categories['unknown_purpose'])
            },
            'categories': self.categories,
            'detailed_analysis': self.directory_analysis,
            'actions': self.create_action_plan()
        }

                                                                            return plan

                                                                        def create_action_plan(self):
                                                                            """Create detailed action plan"""
        actions = []

        # 1. Enhance core modules
                                                                            for module in self.categories['core_modules']:
            actions.append({
                'priority': 1,
                'action': 'ENHANCE_MODULE',
                'target': module,
                'tasks': [
                    f'Create {module}/README.md with module documentation',
                    f'Create {module}/tests/ with comprehensive test suite',
                    f'Create {module}/examples/ with usage examples',
                    f'Create {module}/docs/ with API documentation',
                    f'Add {module}/.gitignore for module-specific ignores',
                    f'Create {module}/Makefile for module-specific commands',
                    f'Ensure all submodules have __init__.py',
                    f'Add module-specific requirements.txt if needed'
                ]
            })

        # 2. Merge directories into modules
                                                                                for directory in self.categories['should_be_submodules']:
            target_module = self.suggest_module_for_directory(directory)
            actions.append({
                'priority': 2,
                'action': 'MERGE_INTO_MODULE',
                'source': directory,
                'target': f'{target_module}/{directory}/',
                'tasks': [
                    f'Move all files from {directory}/ to {target_module}/{directory}/',
                    f'Update all imports referencing {directory}',
                    f'Add {directory} to {target_module}/MODULE_MANIFEST.json',
                    f'Create integration tests'
                ]
            })

        # 3. Consolidate tools
                                                                                    for tool_dir in self.categories['tools_and_utils']:
                                                                                        if tool_dir != 'tools':
                actions.append({
                    'priority': 3,
                    'action': 'CONSOLIDATE_TOOLS',
                    'source': tool_dir,
                    'target': 'tools/',
                    'tasks': [
                        f'Move {tool_dir}/* to tools/{tool_dir}/',
                        f'Update any references',
                        f'Remove empty directory'
                    ]
                })

        # 4. Archive candidates
                                                                                            for directory in self.categories['archive_candidates']:
            actions.append({
                'priority': 4,
                'action': 'ARCHIVE',
                'source': directory,
                'target': 'archive/',
                'tasks': [
                    f'Review {directory} for any valuable content',
                    f'Document purpose in archive/README.md',
                    f'Move to archive/{directory}/',
                    f'Update .gitignore to exclude if large'
                ]
            })

                                                                                                return actions

                                                                                            def create_module_enhancement_script(module):
                                                                                                """Create a script to enhance a module"""
    script_content = f'''#!/usr/bin/env python3
                                                                                                """
                                                                                                Enhance {module} module to be self-sufficient
                                                                                                """

                                                                                                import os
                                                                                                import json
                                                                                                from datetime import datetime

                                                                                                def enhance_module():
    module_path = "{module}"

    # Create directory structure
    directories = [
        f"{{module_path}}/docs",
        f"{{module_path}}/tests",
        f"{{module_path}}/examples",
        f"{{module_path}}/benchmarks"
    ]

                                                                                                    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {{directory}}")

    # Create README.md
    readme_content = """# {module.upper()} Module"

                                                                                                        ## Overview
                                                                                                        {module.upper()} - {get_module_description(module)}

                                                                                                        ## Architecture
                                                                                                        ```
                                                                                                        {module}/
                                                                                                        ├── README.md          # This file
                                                                                                        ├── __init__.py        # Module initialization
                                                                                                        ├── MODULE_MANIFEST.json # Module configuration
                                                                                                        ├── requirements.txt   # Module-specific dependencies
                                                                                                        ├── Makefile          # Module commands
                                                                                                        ├── docs/             # Documentation
                                                                                                        │   ├── API.md        # API reference
                                                                                                        │   ├── GUIDE.md      # User guide
                                                                                                        │   └── DEVELOPMENT.md # Developer guide
                                                                                                        ├── tests/            # Test suite
                                                                                                        │   ├── unit/         # Unit tests
                                                                                                        │   ├── integration/  # Integration tests
                                                                                                        │   └── benchmarks/   # Performance tests
                                                                                                        ├── examples/         # Usage examples
                                                                                                        └── [submodules]/     # Core functionality
                                                                                                        ```

                                                                                                        ## Quick Start
                                                                                                        ```python
                                                                                                        from {module} import *

                                                                                                        # Example usage
                                                                                                        ```

                                                                                                        ## Testing
                                                                                                        ```bash
                                                                                                        # Run all tests
                                                                                                        make test

                                                                                                        # Run specific test
                                                                                                        pytest tests/unit/test_specific.py
                                                                                                        ```

                                                                                                        ## Contributing
                                                                                                        See DEVELOPMENT.md for contribution guidelines.
                                                                                                        """

                                                                                                        with open(f"{{module_path}}/README.md", 'w') as f:
        f.write(readme_content)
    print("✅ Created README.md")

    # Create Makefile
    makefile_content = """.PHONY: test clean install lint format"

                                                                                                            test:
                                                                                                            pytest tests/ -v --cov={module}

                                                                                                            test-unit:
                                                                                                            pytest tests/unit/ -v

                                                                                                            test-integration:
                                                                                                            pytest tests/integration/ -v

                                                                                                            lint:
                                                                                                            flake8 {module}/
                                                                                                            mypy {module}/

                                                                                                            format:
                                                                                                            black {module}/
                                                                                                            isort {module}/

                                                                                                            clean:
                                                                                                            find . -type f -name "*.pyc" -delete
                                                                                                            find . -type d -name "__pycache__" -delete
                                                                                                            rm -rf .pytest_cache
                                                                                                            rm -rf .coverage

                                                                                                            install:
                                                                                                            pip install -r requirements.txt
                                                                                                            pip install -e .
                                                                                                            """

                                                                                                            with open(f"{{module_path}}/Makefile", 'w') as f:
        f.write(makefile_content)
    print("✅ Created Makefile")

    # Create test structure
    test_init = '''"""
                                                                                                                {module.upper()} Test Suite
                                                                                                                """

                                                                                                                import sys
                                                                                                                from pathlib import (
                                                                                                                    Path,
                                                                                                                )

                                                                                                                import pytest

                                                                                                                # Add parent directory to path
                                                                                                                sys.path.insert(0, str(Path(__file__).parent.parent))
                                                                                                                '''

                                                                                                                with open(f"{{module_path}}/tests/__init__.py", 'w') as f:
        f.write(test_init)

    # Create example test
    example_test = '''"""
                                                                                                                    Example test for {module} module
                                                                                                                    """

                                                                                                                    import pytest
                                                                                                                    from {module} import *

                                                                                                                    def test_{module}_import():
                                                                                                                        """Test that module can be imported"""
    assert True  # Module imported successfully

                                                                                                                        def test_{module}_basic_functionality():
                                                                                                                            """Test basic functionality"""
    # TODO: Add actual tests
                                                                                                                            pass

                                                                                                                        class Test{module.title()}Integration:
                                                                                                                            """Integration tests for {module}"""

                                                                                                                            def setup_method(self):
                                                                                                                                """Setup for each test"""
                                                                                                                                pass

                                                                                                                            def test_integration(self):
                                                                                                                                """Test module integration"""
        # TODO: Add integration tests
                                                                                                                                pass
                                                                                                                            '''

    os.makedirs(f"{{module_path}}/tests/unit", exist_ok=True)
                                                                                                                            with open(f"{{module_path}}/tests/unit/test_basic.py", 'w') as f:
        f.write(example_test)
    print("✅ Created test structure")

    # Create API documentation template
    api_doc = """# {module.upper()} API Reference"

                                                                                                                                ## Core Classes

                                                                                                                                ### Class: {module.title()}Core
                                                                                                                                Main class for {module} functionality.

                                                                                                                                #### Methods

                                                                                                                                ##### `__init__(self, config: dict = None)`
                                                                                                                                Initialize the {module} module.

                                                                                                                                **Parameters:**
                                                                                                                                - `config` (dict, optional): Configuration dictionary

                                                                                                                                ##### `process(self, input_data: Any) -> Any`
                                                                                                                                Process input data through {module}.

                                                                                                                                **Parameters:**
                                                                                                                                - `input_data`: Input to process

                                                                                                                                **Returns:**
                                                                                                                                - Processed output

                                                                                                                                ## Submodules

                                                                                                                                ### {module}.submodule1
                                                                                                                                Description of submodule1

                                                                                                                                ### {module}.submodule2
                                                                                                                                Description of submodule2

                                                                                                                                ## Examples

                                                                                                                                ```python
                                                                                                                                from {module} import {module.title()}Core

                                                                                                                                # Initialize
                                                                                                                                core = {module.title()}Core()

                                                                                                                                # Process data
                                                                                                                                result = core.process(data)
                                                                                                                                ```
                                                                                                                                """

                                                                                                                                with open(f"{{module_path}}/docs/API.md", 'w') as f:
        f.write(api_doc)
    print("✅ Created API documentation")

    print(f"\\n✅ Successfully enhanced {module} module!")

                                                                                                                                    def get_module_description(module):
    descriptions = {{
        'core': 'Central nervous system - GLYPH engine, symbolic processing',
        'consciousness': 'Awareness, reflection, decision-making cortex',
        'memory': 'Fold-based memory with causal chains',
        'qim': 'Quantum-Inspired Metaphors for advanced processing',
        'emotion': 'VAD affect and mood regulation',
        'governance': 'Guardian system and ethical oversight',
        'bridge': 'External API connections and interfaces'
    }}
                                                                                                                                        return descriptions.get(module, 'Module description')

                                                                                                                                    if __name__ == "__main__":
    enhance_module()
                                                                                                                                        '''
                                                                                                                                        return script_content

                                                                                                                                    def main():
    print("🔍 LUKHAS PWM ROOT DIRECTORY AUDIT")
    print("=" * 50)

    auditor = RootDirectoryAuditor()
    plan = auditor.analyze_root()

    # Save plan
    plan_path = 'docs/planning/PWM_ROOT_REORGANIZATION_PLAN.json'
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)
                                                                                                                                        with open(plan_path, 'w') as f:
        json.dump(plan, f, indent=2)

    print(f"\n📋 Reorganization plan saved to: {plan_path}")

    # Display summary
    print("\n📊 ROOT DIRECTORY AUDIT SUMMARY")
    print("=" * 50)

    print(f"\nTotal directories at root: {plan['summary']['total_directories']}")
    print(f"Core modules (to enhance): {plan['summary']['core_modules']}")
    print(f"Should be submodules: {plan['summary']['to_merge']}")
    print(f"Archive candidates: {plan['summary']['to_archive']}")
    print(f"Need review: {plan['summary']['to_review']}")

    # Show categories
                                                                                                                                            for category, directories in plan['categories'].items():
                                                                                                                                                if directories:
            print(f"\n{category.upper().replace('_', ' ')}:")
                                                                                                                                                    for directory in directories:
                analysis = plan['detailed_analysis'][directory]
                print(f"  - {directory}: {analysis['file_count']} files,
    {analysis['size']}MB")
                print(f"    Action: {analysis['suggested_action']} - {analysis['reason']}")

    # Create enhancement scripts for each core module
    print("\n📝 Creating module enhancement scripts...")
                                                                                                                                                        for module in auditor.categories['core_modules']:
        script_path = f'tools/scripts/enhance_{module}_module.py'
                                                                                                                                                            with open(script_path, 'w') as f:
            f.write(create_module_enhancement_script(module))
        os.chmod(script_path, 0o755)
        print(f"✅ Created {script_path}")

    print("\n🎯 NEXT STEPS:")
    print("1. Run enhancement scripts for each core module")
    print("2. Execute the reorganization plan")
    print("3. Archive unnecessary directories")
    print("4. Update all imports")
    print("5. Run comprehensive tests")

                                                                                                                                                                if __name__ == "__main__":
    main()