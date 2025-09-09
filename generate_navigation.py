#!/usr/bin/env python3
"""
Generate comprehensive MkDocs navigation from migrated documentation
"""

import os
from pathlib import Path
import yaml

def generate_navigation():
    """Generate nav structure from docs_new content"""
    
    base_dir = Path("docs_new")
    nav_structure = []
    
    # Overview
    nav_structure.append({"Overview": "index.md"})
    
    # Concepts - organized by major areas
    concepts_nav = []
    concepts_dir = base_dir / "concepts"
    
    # Key framework docs first
    key_concepts = [
        ("Constellation Framework", "constellation-framework.md"),
        ("Identity & Authentication", "identity-system.md"),
        ("Memory & Persistence", "memory-system.md"),
        ("Ethics & Governance", "ethics-governance.md"),
        ("Quantum-Bio Processing", "quantum-bio.md"),
    ]
    
    for title, file in key_concepts:
        if (concepts_dir / file).exists():
            concepts_nav.append({title: f"concepts/{file}"})
    
    # Add major concept areas
    concept_areas = {}
    if concepts_dir.exists():
        for item in sorted(concepts_dir.iterdir()):
            if item.is_dir():
                area_name = item.name.replace('_', ' ').title()
                concept_areas[area_name] = []
                
                # Add files in this area
                for md_file in sorted(item.rglob("*.md")):
                    rel_path = md_file.relative_to(base_dir)
                    file_title = md_file.stem.replace('_', ' ').replace('README', area_name)
                    concept_areas[area_name].append({file_title: str(rel_path)})
    
    # Add organized concept areas to nav
    for area, files in concept_areas.items():
        if files:
            concepts_nav.append({area: files[:10]})  # Limit to top 10 per area for readability
    
    nav_structure.append({"Concepts": concepts_nav})
    
    # How-to guides
    howto_nav = []
    howto_dir = base_dir / "howto"
    
    # Essential howto docs first
    essential_howto = [
        ("Quick Start", "quick-start.md"),
        ("Development Setup", "development-setup.md"),
        ("Testing Guide", "testing.md"),
        ("Deployment", "deployment.md"),
        ("Contribute Docs", "contribute-docs.md"),
    ]
    
    for title, file in essential_howto:
        if (howto_dir / file).exists():
            howto_nav.append({title: f"howto/{file}"})
    
    # Add other howto content
    if howto_dir.exists():
        for md_file in sorted(howto_dir.rglob("*.md")):
            rel_path = md_file.relative_to(base_dir)
            file_title = md_file.stem.replace('_', ' ').title()
            if not any(file_title.lower() in item.get(list(item.keys())[0], '').lower() 
                      for item in howto_nav if isinstance(item, dict)):
                howto_nav.append({file_title: str(rel_path)})
    
    nav_structure.append({"How-to": howto_nav[:20]})  # Limit for readability
    
    # Reference
    reference_nav = []
    reference_dir = base_dir / "reference"
    
    # Essential reference docs
    essential_ref = [
        ("API Overview", "index.md"),
        ("Core Modules", "core.md"),
        ("Lukhas Modules", "lukhas.md"),
        ("Candidate Modules", "candidate.md"),
        ("Configuration", "configuration.md"),
        ("Claude Integration", "claude-integration.md"),
    ]
    
    for title, file in essential_ref:
        if (reference_dir / file).exists():
            reference_nav.append({title: f"reference/{file}"})
    
    # Add other reference content organized by area
    ref_areas = {}
    if reference_dir.exists():
        for item in sorted(reference_dir.iterdir()):
            if item.is_dir():
                area_name = item.name.replace('_', ' ').title()
                ref_areas[area_name] = []
                
                for md_file in sorted(item.rglob("*.md")):
                    rel_path = md_file.relative_to(base_dir)
                    file_title = md_file.stem.replace('_', ' ').title()
                    ref_areas[area_name].append({file_title: str(rel_path)})
    
    # Add organized reference areas
    for area, files in ref_areas.items():
        if files:
            reference_nav.append({area: files[:15]})  # Limit per area
    
    nav_structure.append({"Reference": reference_nav})
    
    # Decisions
    decisions_nav = []
    decisions_dir = base_dir / "decisions"
    
    decisions_nav.append({"ADRs Overview": "decisions/index.md"})
    
    if decisions_dir.exists():
        for md_file in sorted(decisions_dir.rglob("*.md")):
            if md_file.name != "index.md":
                rel_path = md_file.relative_to(base_dir)
                file_title = md_file.stem.replace('_', ' ').title()
                decisions_nav.append({file_title: str(rel_path)})
    
    nav_structure.append({"Decisions": decisions_nav})
    
    # Runbooks
    runbooks_nav = []
    runbooks_dir = base_dir / "runbooks"
    
    # Essential runbooks
    essential_runbooks = [
        ("On-call Guide", "oncall.md"),
        ("Monitoring", "monitoring.md"),
        ("Troubleshooting", "troubleshooting.md"),
        ("Security", "security.md"),
    ]
    
    for title, file in essential_runbooks:
        if (runbooks_dir / file).exists():
            runbooks_nav.append({title: f"runbooks/{file}"})
    
    if runbooks_dir.exists():
        for md_file in sorted(runbooks_dir.rglob("*.md")):
            rel_path = md_file.relative_to(base_dir)
            file_title = md_file.stem.replace('_', ' ').title()
            if not any(file_title.lower() in item.get(list(item.keys())[0], '').lower() 
                      for item in runbooks_nav if isinstance(item, dict)):
                runbooks_nav.append({file_title: str(rel_path)})
    
    nav_structure.append({"Runbooks": runbooks_nav})
    
    # Changelogs
    changelogs_nav = []
    changelogs_dir = base_dir / "changelogs"
    
    changelogs_nav.extend([
        {"Release Notes": "changelogs/app.md"},
        {"Change Log": "changelogs/changelog.md"},
    ])
    
    if changelogs_dir.exists():
        for md_file in sorted(changelogs_dir.rglob("*.md")):
            rel_path = md_file.relative_to(base_dir)
            file_title = md_file.stem.replace('_', ' ').title()
            if not any(file_title.lower() in item.get(list(item.keys())[0], '').lower() 
                      for item in changelogs_nav if isinstance(item, dict)):
                changelogs_nav.append({file_title: str(rel_path)})
    
    nav_structure.append({"Changelogs": changelogs_nav})
    
    # Reports
    reports_nav = []
    reports_dir = base_dir / "reports"
    
    reports_nav.append({"Migration Report": "reports/docs_reorg.md"})
    
    if reports_dir.exists():
        for md_file in sorted(reports_dir.rglob("*.md")):
            if md_file.name != "docs_reorg.md":
                rel_path = md_file.relative_to(base_dir)
                file_title = md_file.stem.replace('_', ' ').title()
                reports_nav.append({file_title: str(rel_path)})
    
    nav_structure.append({"Reports": reports_nav})
    
    return nav_structure

def update_mkdocs_config():
    """Update mkdocs.yml with new navigation"""
    
    # Read current config - handle custom YAML tags
    import yaml
    from yaml import SafeLoader
    
    class CustomLoader(SafeLoader):
        pass
    
    def unknown_constructor(loader, node):
        return None
    
    CustomLoader.add_constructor(None, unknown_constructor)
    
    with open("mkdocs.yml", 'r') as f:
        content = f.read()
        # Replace the problematic line to avoid parsing issues
        content = content.replace('!!python/name:pymdownx.superfences.fence_code_format', '"pymdownx.superfences.fence_code_format"')
        config = yaml.load(content, Loader=CustomLoader)
    
    # Generate new navigation
    new_nav = generate_navigation()
    config['nav'] = new_nav
    
    # Write updated config - restore the format manually
    with open("mkdocs.yml", 'w') as f:
        # Write everything except nav manually to preserve format
        f.write(f"site_name: {config['site_name']}\n")
        f.write(f"site_url: {config['site_url']}\n")  
        f.write(f"site_description: {config['site_description']}\n\n")
        f.write(f"docs_dir: {config['docs_dir']}\n\n")
        
        # Write theme section
        f.write("theme:\n")
        f.write(f"  name: {config['theme']['name']}\n")
        f.write("  features:\n")
        for feature in config['theme']['features']:
            f.write(f"    - {feature}\n")
        f.write("  palette:\n")
        for palette in config['theme']['palette']:
            f.write(f"    - scheme: {palette['scheme']}\n")
            f.write(f"      primary: {palette['primary']}\n")
            f.write(f"      accent: {palette['accent']}\n")
            f.write("      toggle:\n")
            f.write(f"        icon: {palette['toggle']['icon']}\n")
            f.write(f"        name: {palette['toggle']['name']}\n")
        
        f.write("\nplugins:\n")
        f.write("  - search:\n")
        f.write("      lang: en\n")
        f.write("  - mkdocstrings:\n")
        f.write("      handlers:\n")
        f.write("        python:\n")
        f.write("          options:\n")
        f.write("            docstring_style: google\n")
        f.write("            show_source: false\n")
        f.write("            show_root_heading: true\n")
        f.write("            show_category_heading: true\n")
        f.write("            members_order: source\n")
        f.write("            filters: [\"!^_\"]\n\n")
        
        # Write navigation
        f.write("nav:\n")
        for item in new_nav:
            yaml.dump([item], f, default_flow_style=False, indent=2)
        
        # Write markdown extensions
        f.write("\nmarkdown_extensions:\n")
        f.write("  - pymdownx.highlight:\n")
        f.write("      anchor_linenums: true\n")
        f.write("  - pymdownx.inlinehilite\n")
        f.write("  - pymdownx.snippets\n")
        f.write("  - pymdownx.superfences:\n")
        f.write("      custom_fences:\n")
        f.write("        - name: mermaid\n")
        f.write("          class: mermaid\n")
        f.write("          format: !!python/name:pymdownx.superfences.fence_code_format\n")
        f.write("  - admonition\n")
        f.write("  - pymdownx.details\n")
        f.write("  - attr_list\n")
        f.write("  - md_in_html\n")
        f.write("  - tables\n")
        f.write("  - toc:\n")
        f.write("      permalink: true\n")
    
    print("✅ Updated mkdocs.yml with comprehensive navigation")
    print(f"📊 Navigation includes {len(new_nav)} main sections")
    
    # Count total entries
    total_entries = 0
    for section in new_nav:
        if isinstance(section, dict):
            for key, value in section.items():
                if isinstance(value, list):
                    total_entries += len(value)
                else:
                    total_entries += 1
    
    print(f"📖 Total navigation entries: {total_entries}")

if __name__ == "__main__":
    update_mkdocs_config()