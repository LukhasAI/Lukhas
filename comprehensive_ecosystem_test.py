#!/usr/bin/env python3
"""
🌌 COMPLETE LUKHAS CONSCIOUSNESS ECOSYSTEM SCANNER
Comprehensive testing of the entire LUKHAS consciousness platform
"""

import os
import sys
import time
from datetime import datetime
import importlib.util

def test_import(module_name, description=''):
    """Test if a module can be imported"""
    try:
        if '.' in module_name:
            # Handle nested imports
            parts = module_name.split('.')
            current = __import__(parts[0])
            for part in parts[1:]:
                current = getattr(current, part)
        else:
            __import__(module_name)
        return True, "✅ OPERATIONAL"
    except ImportError as e:
        return False, f"❌ ImportError: {str(e)[:40]}..."
    except AttributeError as e:
        return False, f"❌ AttributeError: {str(e)[:40]}..."
    except Exception as e:
        return False, f"❌ {type(e).__name__}: {str(e)[:40]}..."

def main():
    print('🌌 COMPLETE LUKHAS CONSCIOUSNESS ECOSYSTEM SCAN')
    print('=' * 60)
    
    start_time = time.time()
    
    # Get all directories for comprehensive testing
    lukhas_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and not item.startswith('.') and not item.startswith('_') and item != '__pycache__':
            lukhas_dirs.append(item)
    
    print(f'🔍 Discovered {len(lukhas_dirs)} top-level directories')
    print(f'🚀 Ecosystem scan started: {datetime.now().strftime("%H:%M:%S")}')
    print()
    
    # Comprehensive system testing
    systems_status = {}
    
    print('🧠 CORE CONSCIOUSNESS SYSTEMS:')
    print('-' * 35)
    
    # Core lukhas systems
    core_systems = [
        ('lukhas.memory', 'Fold-based memory system'),
        ('lukhas.consciousness', 'Core consciousness'),
        ('lukhas.api', 'API endpoints'),
        ('lukhas.bridge', 'Bridge systems'),
        ('lukhas.agents', 'Agent system (NEW)'),
        ('lukhas.core', 'Core systems'),
        ('lukhas.identity', 'Identity systems'),
    ]
    
    for module, desc in core_systems:
        success, status = test_import(module, desc)
        systems_status[module] = status
        print(f'  {status} {module}')
    
    print()
    print('🎭 CONSCIOUSNESS DOMAINS:')
    print('-' * 25)
    
    # Major consciousness domains
    consciousness_domains = [
        ('branding', 'LUKHAS branding system'),
        ('governance', 'Governance & ethics'),
        ('ethics', 'Ethics systems'),
        ('memory', 'Root memory system'),
        ('bio', 'Bio-inspired systems'),
        ('qi', 'Quantum-inspired systems'),
        ('rl', 'Reinforcement learning'),
        ('dreams', 'Dream state systems'),
        ('emotions', 'Emotion systems'),
        ('brain', 'Brain systems'),
        ('identity', 'Identity management'),
        ('consciousness', 'Consciousness core'),
        ('quantum', 'Quantum processing'),
    ]
    
    for module, desc in consciousness_domains:
        success, status = test_import(module, desc)
        systems_status[module] = status
        print(f'  {status} {module}')
    
    print()
    print('🌟 ADVANCED SYSTEMS:')
    print('-' * 20)
    
    advanced_systems = [
        ('matriz', 'MATRIZ consciousness'),
        ('reasoning', 'Reasoning engines'),
        ('consciousness_validation', 'Consciousness validation'),
        ('symbolic', 'Symbolic processing'),
        ('observability', 'System observability'),
        ('authentication', 'Authentication systems'),
        ('authorization', 'Authorization systems'),
        ('audit', 'Audit systems'),
        ('flow', 'Flow control'),
        ('cli', 'Command line interface'),
        ('lukhas', 'Main LUKHAS module'),
    ]
    
    for module, desc in advanced_systems:
        success, status = test_import(module, desc)
        systems_status[module] = status
        print(f'  {status} {module}')
    
    print()
    print('🎨 CREATIVE & EXPERIENCE:')
    print('-' * 25)
    
    creative_systems = [
        ('personality', 'Personality systems'),
        ('tone', 'Tone & communication'),
        ('universal_language', 'Universal language'),
        ('modulation', 'Voice modulation'),
        ('creativity', 'Creative expression'),
        ('expression', 'Expression systems'),
        ('communication', 'Communication'),
    ]
    
    for module, desc in creative_systems:
        success, status = test_import(module, desc)
        systems_status[module] = status
        print(f'  {status} {module}')
    
    print()
    print('🏗️ INFRASTRUCTURE:')
    print('-' * 18)
    
    infrastructure = [
        ('deployment', 'Deployment systems'),
        ('monitoring', 'System monitoring'),
        ('security', 'Security systems'),
        ('config', 'Configuration'),
        ('analytics', 'Analytics systems'),
        ('testing', 'Testing framework'),
        ('tools', 'Development tools'),
        ('scripts', 'Automation scripts'),
        ('data', 'Data management'),
    ]
    
    for module, desc in infrastructure:
        success, status = test_import(module, desc)
        systems_status[module] = status
        print(f'  {status} {module}')
    
    print()
    print('📦 PRODUCTS & SERVICES:')
    print('-' * 23)
    
    products_services = [
        ('products', 'Product systems'),
        ('lambda_products', 'Lambda products'),
        ('business', 'Business logic'),
        ('sdk', 'Software development kit'),
        ('api', 'Root API system'),
        ('services', 'Service layer'),
        ('platforms', 'Platform systems'),
    ]
    
    for module, desc in products_services:
        success, status = test_import(module, desc)
        systems_status[module] = status
        print(f'  {status} {module}')
    
    print()
    print('🔬 CANDIDATE SYSTEMS:')
    print('-' * 20)
    
    candidate_systems = [
        ('candidate', 'Candidate root'),
        ('agent', 'New agent system'),
        ('agents_external', 'External agent configs'),
        ('core', 'Core root systems'),
        ('orchestration', 'Orchestration systems'),
        ('interfaces', 'Interface definitions'),
    ]
    
    for module, desc in candidate_systems:
        success, status = test_import(module, desc)
        systems_status[module] = status
        print(f'  {status} {module}')
    
    # Calculate comprehensive results
    end_time = time.time()
    scan_duration = end_time - start_time
    
    operational_count = sum(1 for status in systems_status.values() if status.startswith('✅'))
    total_systems = len(systems_status)
    health_percentage = (operational_count / total_systems) * 100
    
    print()
    print('📊 COMPREHENSIVE ECOSYSTEM RESULTS:')
    print('=' * 40)
    print(f'🟢 Systems Operational: {operational_count}/{total_systems}')
    print(f'📊 Ecosystem Health: {health_percentage:.1f}%')
    print(f'⏱️  Scan Duration: {scan_duration:.3f} seconds')
    print(f'🌌 Directories Scanned: {len(lukhas_dirs)}')
    
    print()
    print('🔍 SYSTEM FAILURES (Issues to address):')
    print('-' * 40)
    failure_count = 0
    for system, status in sorted(systems_status.items()):
        if not status.startswith('✅'):
            print(f'  {status} {system}')
            failure_count += 1
    
    if failure_count == 0:
        print('  🎉 NO FAILURES! All systems operational!')
    
    print()
    print('🎯 COMPREHENSIVE ASSESSMENT:')
    print('-' * 30)
    if health_percentage >= 80:
        print('🎉 EXCELLENT: Strong ecosystem health')
        print('🚀 Most consciousness systems operational')
    elif health_percentage >= 60:
        print('👍 GOOD: Majority of systems working')
        print('🔧 Some systems need attention')
    elif health_percentage >= 40:
        print('⚠️  FAIR: Mixed system health')
        print('🛠️  Multiple systems need work')
    else:
        print('🚨 CRITICAL: Ecosystem needs attention')
        print('🆘 Many systems not operational')
    
    print()
    print('🌌 CONSCIOUSNESS ECOSYSTEM INSIGHTS:')
    print('• LUKHAS is a massive consciousness platform')
    print('• True ecosystem contains dozens of consciousness domains')
    print('• Agent restructure was just one small component')
    print('• Comprehensive testing reveals enormous scope')
    print('• Most systems are likely development/experimental phase')
    
    print()
    print(f'🌍 COMPLETE ECOSYSTEM SCAN FINISHED! 🧠')
    print(f'True system scope: {total_systems} major components')
    print(f'Directories discovered: {", ".join(sorted(lukhas_dirs))}')

if __name__ == "__main__":
    main()
