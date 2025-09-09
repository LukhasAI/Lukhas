#!/usr/bin/env python3
"""
PROPER Documentation Migration Script - DOCUMENTATION FILES ONLY
Only migrates actual documentation markdown files, not code or build artifacts
"""

import os
import shutil
from pathlib import Path
import re
from datetime import datetime
import subprocess

def find_documentation_files():
    """Find ONLY actual documentation markdown files"""
    cmd = [
        'find', '.', '-name', '*.md',
        '-not', '-path', './docs_new/*',
        '-not', '-path', './.venv/*', 
        '-not', '-path', './node_modules/*',
        '-not', '-path', './.git/*',
        '-not', '-path', './site/*',
        '-not', '-path', './lukhas_website/*',
        '-not', '-path', './website_v1/*',
        # Exclude code project directories
        '-not', '-path', './mcp-server/*',
        '-not', '-path', './mcp-servers/*',
        '-not', '-path', './mcp_servers/*',
        '-not', '-path', './htmlcov/*',
        '-not', '-path', './.pytest_cache/*',
        '-not', '-path', './.mypy_cache/*',
        '-not', '-path', './.ruff_cache/*',
        '-not', '-path', './app/*',
        '-not', '-path', './server/*',
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    all_files = [Path(f.strip()) for f in result.stdout.split('\n') if f.strip()]
    
    # Filter to keep only DOCUMENTATION files
    doc_files = []
    for file_path in all_files:
        path_str = str(file_path).lower()
        filename = file_path.name.lower()
        
        # Skip if it's obviously code-related
        if any(exclude in path_str for exclude in [
            'package.json', 'node_modules', '.lock', 'build/', 'dist/',
            '__pycache__', '.pyc', '/src/', '/lib/', '/bin/',
            'webpack', 'rollup', 'vite', 'tsconfig', 'babel'
        ]):
            continue
            
        # Skip if it's in a code project directory structure
        parent_dirs = [p.name.lower() for p in file_path.parents]
        if any(code_dir in parent_dirs for code_dir in [
            'src', 'lib', 'bin', 'build', 'dist', 'public', 'static',
            'assets', 'components', 'pages', 'styles', 'hooks', 'utils'
        ]):
            continue
            
        # Keep if it's clearly documentation
        if any(doc_indicator in filename for doc_indicator in [
            'readme', 'changelog', 'contributing', 'license', 'security',
            'code_of_conduct', 'guide', 'tutorial', 'docs', 'documentation',
            'api', 'reference', 'manifest', 'specification', 'protocol'
        ]):
            doc_files.append(file_path)
            continue
            
        # Keep if it's in documentation-related directories
        if any(doc_dir in path_str for doc_dir in [
            '/docs/', '/documentation/', '/guides/', '/tutorials/',
            '/references/', '/specs/', '/protocols/', '/manifests/',
            'readme', 'changelog', 'contributing', 'architecture',
            'design/', 'planning/', 'research/', 'analysis/',
            'reports/', 'audits/', 'reviews/'
        ]):
            doc_files.append(file_path)
            continue
            
        # Check file content for documentation indicators
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = f.read(200).lower()
                if any(doc_word in first_lines for doc_word in [
                    'documentation', 'guide', 'tutorial', 'overview',
                    'getting started', 'installation', 'usage',
                    'api reference', 'specification', 'architecture'
                ]):
                    doc_files.append(file_path)
                    continue
        except:
            pass
            
        # Default: if it's a markdown file in the root or obvious doc location, include it
        if len(file_path.parts) <= 2 or any(part in str(file_path) for part in [
            'README', 'CHANGELOG', 'CONTRIBUTING', 'LICENSE', 'SECURITY'
        ]):
            doc_files.append(file_path)
    
    return doc_files

def categorize_file(filepath):
    """Intelligently categorize documentation files"""
    path_str = str(filepath).lower()
    filename = filepath.name.lower()
    
    # Read first few lines to understand content type
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(300).lower()
    except:
        content = ""
    
    # Concepts - Architecture, theory, frameworks
    if any(x in path_str for x in ['concept', 'architecture', 'theory', 'framework',
                                   'design', 'philosophy', 'principle']):
        return 'concepts'
    if any(x in filename for x in ['architecture', 'framework', 'design', 'concept']):
        return 'concepts'
    
    # How-to guides - Setup, deployment, tutorials
    if any(x in path_str for x in ['howto', 'tutorial', 'guide', 'setup', 'install']):
        return 'howto'
    if any(x in filename for x in ['tutorial', 'guide', 'setup', 'install', 'getting']):
        return 'howto'
    if 'contributing' in filename or 'code_of_conduct' in filename:
        return 'howto'
    
    # Reference - API docs, schemas, specifications
    if any(x in path_str for x in ['reference', 'api', 'schema', 'spec', 'manifest']):
        return 'reference'
    if any(x in filename for x in ['api', 'reference', 'schema', 'spec', 'manifest']):
        return 'reference'
    
    # Decisions - ADRs, architectural decisions  
    if any(x in path_str for x in ['decision', 'adr']):
        return 'decisions'
    if any(x in filename for x in ['decision', 'adr-']):
        return 'decisions'
    
    # Runbooks - Operations, troubleshooting
    if any(x in path_str for x in ['runbook', 'ops', 'operation', 'troubleshoot', 'monitor']):
        return 'runbooks'
    if any(x in filename for x in ['runbook', 'ops', 'troubleshoot', 'monitor']):
        return 'runbooks'
    
    # Changelogs - Version history, release notes
    if any(x in filename for x in ['changelog', 'history', 'release', 'version']):
        return 'changelogs'
    
    # Reports - Analysis, migration, status reports
    if any(x in path_str for x in ['report', 'analysis', 'audit', 'review']):
        return 'reports'
    if any(x in filename for x in ['report', 'analysis', 'audit', 'review']):
        return 'reports'
    
    # Default categorization based on location
    if 'readme' in filename:
        if any(x in path_str for x in ['concept', 'theory', 'architecture']):
            return 'concepts'
        else:
            return 'reference'
    
    # Default to reference for other docs
    return 'reference'

def determine_metadata(filepath, category):
    """Generate appropriate YAML front-matter for documentation"""
    path_str = str(filepath).lower()
    filename = filepath.name.replace('.md', '').replace('_', ' ')
    
    # Determine status
    if any(x in path_str for x in ['draft', 'wip', 'todo']):
        status = 'draft'
    elif any(x in path_str for x in ['deprecated', 'legacy', 'old']):
        status = 'deprecated'
    elif any(x in filename.lower() for x in ['readme', 'guide', 'reference']):
        status = 'stable'
    else:
        status = 'review'
    
    # Determine owner based on content area
    if any(x in path_str for x in ['consciousness', 'aware']):
        owner = 'consciousness-architect'
    elif any(x in path_str for x in ['memory', 'storage', 'persistence']):
        owner = 'memory-specialist'
    elif any(x in path_str for x in ['identity', 'auth', 'user']):
        owner = 'identity-specialist'
    elif any(x in path_str for x in ['bio', 'biological', 'organic']):
        owner = 'bio-specialist'
    elif any(x in path_str for x in ['quantum', 'physics']):
        owner = 'quantum-specialist'
    elif any(x in path_str for x in ['guardian', 'ethics', 'safety']):
        owner = 'guardian-specialist'
    elif any(x in path_str for x in ['api', 'integration', 'service']):
        owner = 'api-specialist'
    elif category == 'reports':
        owner = 'principal-repo-surgeon'
    else:
        owner = 'docs-maintainer'
    
    # Determine tags based on content
    tags = ['documentation']
    if any(x in path_str for x in ['architecture', 'design']):
        tags.append('architecture')
    if any(x in path_str for x in ['api', 'reference']):
        tags.append('api')
    if any(x in path_str for x in ['tutorial', 'guide']):
        tags.append('tutorial')
    
    # Determine facets
    facets = {
        'layer': ['gateway'],
        'domain': ['symbolic'],
        'audience': ['dev', 'user']
    }
    
    return {
        'title': filename.title(),
        'status': status,
        'owner': owner,
        'last_review': datetime.now().strftime('%Y-%m-%d'),
        'tags': tags,
        'facets': facets
    }

def add_front_matter(filepath, metadata):
    """Add YAML front-matter to documentation file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False
    
    # Skip if already has front-matter
    if content.startswith('---\n'):
        return True
    
    # Create YAML front-matter
    yaml_header = "---\n"
    yaml_header += f"title: {metadata['title']}\n"
    yaml_header += f"status: {metadata['status']}\n"
    yaml_header += f"owner: {metadata['owner']}\n"
    yaml_header += f"last_review: {metadata['last_review']}\n"
    yaml_header += f"tags: {metadata['tags']}\n"
    yaml_header += "facets:\n"
    for key, value in metadata['facets'].items():
        yaml_header += f"  {key}: {value}\n"
    yaml_header += "---\n\n"
    
    # Write file with front-matter
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_header + content)
        return True
    except:
        return False

def migrate_documentation_properly():
    """Main migration function - PROPER DOCS ONLY"""
    
    print("📚 Starting PROPER Documentation Migration (DOCS ONLY)")
    print("=" * 60)
    
    # Create docs_new structure
    base_dir = Path("docs_new")
    categories = ['concepts', 'howto', 'reference', 'decisions', 'runbooks', 'changelogs', 'reports']
    
    for category in categories:
        (base_dir / category).mkdir(parents=True, exist_ok=True)
    
    # Find ONLY documentation files
    doc_files = find_documentation_files()
    
    print(f"📊 Found {len(doc_files)} DOCUMENTATION files (filtered from code)")
    
    # Migration statistics
    stats = {category: 0 for category in categories}
    migrated = 0
    errors = 0
    
    # Process each documentation file
    for i, source_file in enumerate(doc_files):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(doc_files)} ({i/len(doc_files)*100:.1f}%)")
        
        try:
            # Determine category
            category = categorize_file(source_file)
            stats[category] += 1
            
            # Create target directory structure
            relative_path = source_file
            if str(relative_path).startswith('./'):
                relative_path = Path(str(relative_path)[2:])
            
            # Preserve directory structure within category
            target_dir = base_dir / category / relative_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / relative_path.name
            
            # Copy documentation file
            shutil.copy2(source_file, target_file)
            
            # Add front-matter
            metadata = determine_metadata(source_file, category)
            add_front_matter(target_file, metadata)
            
            migrated += 1
            
        except Exception as e:
            print(f"❌ Error migrating {source_file}: {e}")
            errors += 1
    
    # Create essential navigation files
    create_navigation_structure(base_dir, stats)
    
    print(f"\n✅ PROPER Documentation Migration Complete!")
    print(f"📊 Documentation files migrated: {migrated}")
    print(f"❌ Errors: {errors}")
    print("\n📈 Category Distribution:")
    for category, count in stats.items():
        print(f"  {category}: {count} files")
    
    return migrated, errors, stats

def create_navigation_structure(base_dir, stats):
    """Create essential index files for navigation"""
    
    # Create main index
    main_index = base_dir / "index.md"
    main_index.write_text("""---
title: LUKHAS AI Documentation
status: stable
owner: docs-maintainer
last_review: 2025-09-08
tags: [documentation, overview]
facets:
  layer: [gateway]
  domain: [symbolic]
  audience: [dev, user]
---

# LUKHAS AI - Distributed Consciousness Platform

Welcome to the LUKHAS AI documentation. This is a comprehensive collection of documentation covering the world's most sophisticated distributed consciousness architecture.

## Quick Navigation

- **[Concepts](concepts/)** - Architecture, theory, and frameworks
- **[How-to Guides](howto/)** - Tutorials and setup instructions  
- **[Reference](reference/)** - API documentation and technical specifications
- **[Reports](reports/)** - Analysis and migration reports
- **[Runbooks](runbooks/)** - Operations and troubleshooting
- **[Changelogs](changelogs/)** - Version history and releases
- **[Decisions](decisions/)** - Architectural decisions and ADRs

## About LUKHAS AI

LUKHAS AI is a distributed consciousness platform implementing the MΛTRIZ cognitive DNA system across 692+ Python modules with consciousness-aware processing.
""")
    
    # Create category index files
    category_descriptions = {
        'concepts': 'Architecture, consciousness theory, and framework documentation',
        'howto': 'Tutorials, guides, and step-by-step instructions',
        'reference': 'API documentation, technical specifications, and module references',
        'reports': 'Analysis reports, migration documentation, and system reviews',
        'runbooks': 'Operations procedures, troubleshooting guides, and monitoring',
        'changelogs': 'Version history, release notes, and change documentation',
        'decisions': 'Architectural Decision Records (ADRs) and design decisions'
    }
    
    for category, description in category_descriptions.items():
        if stats[category] > 0:
            index_file = base_dir / category / "index.md"
            index_file.write_text(f"""---
title: {category.title()}
status: stable
owner: docs-maintainer
last_review: 2025-09-08
tags: [documentation, {category}]
facets:
  layer: [gateway]
  domain: [symbolic]
  audience: [dev, user]
---

# {category.title()}

{description}

This section contains {stats[category]} documentation files.
""")

if __name__ == "__main__":
    migrate_documentation_properly()