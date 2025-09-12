#!/usr/bin/env python3
"""
🔧 Enhanced Surgical F-String Repair Tool

Fixes the specific f-string corruption patterns found in our files.
"""
import re
import os

def fix_html_in_fstring(content):
    """Fix HTML/CSS content that's accidentally inside f-strings"""
    
    # Pattern 1: CSS styles with double braces that should be single braces
    # This happens when CSS is inside an f-string but the braces should be literal
    
    # Fix CSS style blocks in f-strings
    css_fixes = [
        (r'body \{\{ font-family:', 'body { font-family:'),
        (r'margin: 0; padding: 20px; \}', 'margin: 0; padding: 20px; }'),
        (r'#network \{\{ height:', '#network { height:'),
        (r'border: 1px solid #ccc; \}', 'border: 1px solid #ccc; }'),
        (r'\.controls \{\{ margin:', '.controls { margin:'),
        (r'margin: 20px 0; \}', 'margin: 20px 0; }'),
        (r'\.legend \{\{ margin:', '.legend { margin:'),
        (r'display: flex; gap: 20px; \}', 'display: flex; gap: 20px; }'),
        (r'\.legend-item \{\{ display:', '.legend-item { display:'),
        (r'align-items: center; gap: 5px; \}', 'align-items: center; gap: 5px; }'),
        (r'\.color-box \{\{ width:', '.color-box { width:'),
        (r'border: 1px solid #333; \}', 'border: 1px solid #333; }'),
        (r'\.stats \{\{ background:', '.stats { background:'),
        (r'border-radius: 5px; margin: 20px 0; \}', 'border-radius: 5px; margin: 20px 0; }'),
    ]
    
    for pattern, replacement in css_fixes:
        content = re.sub(pattern, replacement, content)
    
    # Fix JavaScript object literals in f-strings
    js_fixes = [
        (r'const data = \{\{ nodes: nodes, edges: edges \};', 'const data = { nodes: nodes, edges: edges };'),
        (r'stabilization: \{\{ iterations: 100 \}', 'stabilization: { iterations: 100 }'),
        (r'widthConstraint: \{\{ minimum: 100, maximum: 200 \},', 'widthConstraint: { minimum: 100, maximum: 200 },'),
        (r'heightConstraint: \{\{ minimum: 50 \}', 'heightConstraint: { minimum: 50 }'),
        (r'smooth: \{\{ type: \'dynamic\' \},', 'smooth: { type: \'dynamic\' },'),
        (r'arrows: \{\{ to: \{\{ scaleFactor: 0\.5 \} \}', 'arrows: { to: { scaleFactor: 0.5 } }'),
        (r'network\.setOptions\(\{\{ physics: \{\{ enabled: physicsEnabled \} \}\);', 'network.setOptions({ physics: { enabled: physicsEnabled } });'),
    ]
    
    for pattern, replacement in js_fixes:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_python_fstring_issues(content):
    """Fix Python f-string bracket issues"""
    
    # Fix common Python f-string patterns
    python_fixes = [
        # Fix dictionary literals in f-strings
        (r"f\"Using \{\{module_name\.upper\(\)\} module\"", 'f"Using {module_name.upper()} module"'),
        (r"exec\(f\"from \{module_name\} import \{\{submodule\}\"\)", 'exec(f"from {module_name} import {submodule}")'),
        (r"print\(f\"\{\{module_name\.upper\(\)\}\} Neuroplastic Demo\"\)", 'print(f"{module_name.upper()} Neuroplastic Demo")'),
        (r"print\(f\"Initial hormone levels: \{\{self\.hormone_levels\}\"\)", 'print(f"Initial hormone levels: {self.hormone_levels}")'),
        (r"print\(f\"Stress hormone levels: \{\{self\.hormone_levels\}\"\)", 'print(f"Stress hormone levels: {self.hormone_levels}")'),
        (r"return \{\{\'colony\': self\.colony_id, \'signal\': signal\}", "return {'colony': self.colony_id, 'signal': signal}"),
        (r"signal = \{\{\'type\': \'update\', \'data\': changes\}", "signal = {'type': 'update', 'data': changes}"),
        (r"print\(f\"Module version: \{\{manifest\[\'version\'\]\}\"\)", 'print(f"Module version: {manifest[\'version\']}")'),
        (r"print\(f\"Submodules: \{\{list\(manifest\[\'submodules\'\]\.keys\(\)\}\"\)", 'print(f"Submodules: {list(manifest[\'submodules\'].keys())}")'),
    ]
    
    for pattern, replacement in python_fixes:
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_indentation_issues(content):
    """Fix remaining indentation issues"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix common indentation problems
        if line.strip().startswith('def ') and not line.startswith('    def ') and not line.startswith('def '):
            # Function definition should be properly indented
            if i > 0 and lines[i-1].strip().startswith('class '):
                fixed_lines.append('    ' + line.strip())
            else:
                fixed_lines.append(line)
        elif line.strip().startswith('"""') and line.strip().endswith('"""') and len(line.strip()) > 6:
            # Single-line docstring should be properly indented
            if i > 0 and (lines[i-1].strip().startswith('def ') or lines[i-1].strip().startswith('class ')):
                fixed_lines.append('        ' + line.strip())
            else:
                fixed_lines.append(line)
        elif line.strip() and not line.startswith(' ') and not line.startswith('\t') and not line.strip().startswith('#'):
            # Lines that should be indented but aren't
            if i > 0 and (lines[i-1].strip().endswith(':') or 'if ' in lines[i-1] or 'for ' in lines[i-1] or 'with ' in lines[i-1]):
                fixed_lines.append('    ' + line.strip())
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def surgical_repair_file(filepath):
    """Apply surgical repairs to a specific file"""
    try:
        print(f"🔧 Repairing: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes in order
        content = fix_html_in_fstring(content)
        content = fix_python_fstring_issues(content)
        content = fix_indentation_issues(content)
        
        # Only write if we made changes
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed: {filepath}")
            return True
        else:
            print(f"  ℹ️  No changes needed: {filepath}")
            return False
    
    except Exception as e:
        print(f"  ❌ Error repairing {filepath}: {e}")
        return False

def main():
    """Repair the specific files with f-string corruption"""
    
    files_to_repair = [
        'tools/module_dependency_visualizer.py',
        'tools/scripts/enhance_all_modules.py',
        'candidate/core/safety/predictive_harm_prevention.py',
        'candidate/bridge/adapters/api_documentation_generator.py',
        'products/communication/nias/vendor_portal_backup.py'
    ]
    
    print("🔧 Enhanced Surgical F-String Repair")
    print("=" * 50)
    
    repaired_count = 0
    for filepath in files_to_repair:
        if os.path.exists(filepath):
            if surgical_repair_file(filepath):
                repaired_count += 1
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print(f"\n✅ Repaired {repaired_count} files")
    
    # Test if files can be parsed now
    print("\n🧪 Testing syntax parsing...")
    import ast
    
    for filepath in files_to_repair:
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                ast.parse(content)
                print(f"  ✅ {filepath} - syntax OK")
            except Exception as e:
                print(f"  ❌ {filepath} - {e}")

if __name__ == "__main__":
    main()