#!/usr/bin/env python3
"""
Documentation Migration Script for LUKHAS Repository Reorganization
=================================================================

Migrate 1000+ docs from scattered structure to clean MkDocs categories:
- concepts/: Architecture, consciousness, MΛTRIZ theory
- howto/: Development workflows, deployment, guides  
- reference/: API docs, configuration, schemas
- decisions/: ADRs, architectural decisions
- runbooks/: Operations, troubleshooting, oncall
- changelogs/: Version history, release notes

Add YAML front-matter to all files using controlled vocabulary.
"""
import os
import re
import shutil
import time
from pathlib import Path
from typing import Dict, List, Tuple


CONTROLLED_VOCABULARY = {
    "status": ["draft", "review", "stable", "deprecated"],
    "layer": ["gateway", "orchestration", "integration", "storage", "ui"],
    "domain": ["symbolic", "identity", "ethics", "time", "async", "metrics", 
               "consciousness", "memory", "quantum", "bio", "guardian"],
    "audience": ["dev", "ops", "researcher", "product"],
    "tags": ["overview", "consciousness", "platform", "architecture", "api", 
             "testing", "deployment", "security", "performance", "monitoring", 
             "troubleshooting", "howto", "concept", "reference", "adr", 
             "runbook", "changelog"]
}


def categorize_doc(file_path: Path) -> Tuple[str, Dict[str, any]]:
    """
    Categorize document and generate front-matter.
    
    Returns:
        Tuple of (category, front_matter_dict)
    """
    content = file_path.read_text(errors='ignore')
    filename = file_path.name.lower()
    path_str = str(file_path).lower()
    
    # Determine category based on path and content
    category = "concepts"  # default
    
    if any(keyword in path_str for keyword in ['howto', 'guide', 'tutorial', 'setup', 'development']):
        category = "howto"
    elif any(keyword in path_str for keyword in ['reference', 'api', 'config', 'schema']):
        category = "reference"
    elif any(keyword in path_str for keyword in ['adr', 'decision', 'architecture']):
        category = "decisions"  
    elif any(keyword in path_str for keyword in ['runbook', 'operation', 'troubleshoot', 'monitor', 'oncall']):
        category = "runbooks"
    elif any(keyword in path_str for keyword in ['changelog', 'release', 'version']):
        category = "changelogs"
    elif any(keyword in path_str for keyword in ['architecture', 'consciousness', 'concept', 'theory']):
        category = "concepts"
        
    # Generate front-matter
    title = filename.replace('.md', '').replace('_', ' ').replace('-', ' ').title()
    
    # Determine tags based on content and path
    tags = []
    if 'consciousness' in content.lower() or 'consciousness' in path_str:
        tags.append('consciousness')
    if 'api' in content.lower() or 'api' in path_str:
        tags.append('api')
    if 'architecture' in content.lower() or 'architecture' in path_str:
        tags.append('architecture')
    if 'test' in content.lower() or 'test' in path_str:
        tags.append('testing')
    if 'security' in content.lower() or 'security' in path_str:
        tags.append('security')
    if 'monitor' in content.lower() or 'monitor' in path_str:
        tags.append('monitoring')
        
    if category == "concepts":
        tags.append('concept')
    elif category == "howto":
        tags.append('howto')
    elif category == "reference":
        tags.append('reference')
    elif category == "decisions":
        tags.append('adr')
    elif category == "runbooks":
        tags.append('runbook')
    elif category == "changelogs":
        tags.append('changelog')
    
    # Determine facets
    facets = {
        "layer": ["gateway"] if category in ["concepts", "howto"] else ["orchestration"],
        "domain": ["symbolic"],
        "audience": ["dev"]
    }
    
    if 'consciousness' in content.lower() or 'consciousness' in path_str:
        facets["domain"].append("consciousness")
    if 'identity' in content.lower() or 'identity' in path_str:
        facets["domain"].append("identity")
    if 'memory' in content.lower() or 'memory' in path_str:
        facets["domain"].append("memory")
    if 'quantum' in content.lower() or 'quantum' in path_str:
        facets["domain"].append("quantum")
    if 'bio' in content.lower() or 'bio' in path_str:
        facets["domain"].append("bio")
    if 'guardian' in content.lower() or 'guardian' in path_str:
        facets["domain"].append("guardian")
        
    if category in ["runbooks", "operations"]:
        facets["audience"].append("ops")
    if 'research' in content.lower() or 'research' in path_str:
        facets["audience"].append("researcher")
        
    front_matter = {
        "title": title,
        "status": "review",  # Conservative default
        "owner": "docs-team",
        "last_review": time.strftime("%Y-%m-%d"),
        "tags": tags[:5],  # Limit to 5 tags
        "facets": facets
    }
    
    return category, front_matter


def add_front_matter(content: str, front_matter: Dict) -> str:
    """Add YAML front-matter to content if not already present."""
    
    if content.startswith('---'):
        return content  # Already has front-matter
        
    yaml_header = "---\n"
    yaml_header += f"title: {front_matter['title']}\n"
    yaml_header += f"status: {front_matter['status']}\n"
    yaml_header += f"owner: {front_matter['owner']}\n"
    yaml_header += f"last_review: {front_matter['last_review']}\n"
    
    if front_matter['tags']:
        tags_str = '[' + ', '.join(f'"{tag}"' for tag in front_matter['tags']) + ']'
        yaml_header += f"tags: {tags_str}\n"
    
    yaml_header += "facets:\n"
    for facet_key, facet_values in front_matter['facets'].items():
        values_str = '[' + ', '.join(f'"{val}"' for val in facet_values) + ']'
        yaml_header += f"  {facet_key}: {values_str}\n"
    
    yaml_header += "---\n\n"
    
    return yaml_header + content


def migrate_docs(source_dir: Path, target_dir: Path) -> Dict[str, List[str]]:
    """
    Migrate all docs from source_dir to target_dir with categorization.
    
    Returns migration report.
    """
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)
    
    # Find all markdown files
    md_files = list(source_dir.rglob("*.md"))
    
    migration_report = {
        "concepts": [],
        "howto": [],
        "reference": [],
        "decisions": [],
        "runbooks": [],
        "changelogs": [],
        "errors": []
    }
    
    print(f"Found {len(md_files)} markdown files to migrate")
    
    for md_file in md_files:
        try:
            # Skip if already in target directory or if it's a special file
            if str(target_dir) in str(md_file) or md_file.name in ['README.md']:
                continue
                
            # Read content
            content = md_file.read_text(errors='ignore')
            
            # Categorize and get front-matter
            category, front_matter = categorize_doc(md_file)
            
            # Create target path
            rel_path = md_file.relative_to(source_dir)
            target_path = target_dir / category / rel_path.name
            
            # Ensure unique filename
            counter = 1
            original_target = target_path
            while target_path.exists():
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = original_target.parent / f"{stem}_{counter}{suffix}"
                counter += 1
            
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add front-matter and write
            updated_content = add_front_matter(content, front_matter)
            target_path.write_text(updated_content)
            
            migration_entry = f"{md_file} -> {target_path}"
            migration_report[category].append(migration_entry)
            
            print(f"✅ {category}: {md_file.name}")
            
        except Exception as e:
            error_msg = f"❌ {md_file}: {str(e)}"
            migration_report["errors"].append(error_msg)
            print(error_msg)
    
    return migration_report


if __name__ == "__main__":
    source = Path("docs")
    target = Path("docs_new")
    
    print("🚀 Starting LUKHAS documentation migration...")
    print(f"Source: {source}")
    print(f"Target: {target}")
    print()
    
    # Migrate docs
    report = migrate_docs(source, target)
    
    # Print summary
    print("\n📊 Migration Summary:")
    print("=" * 50)
    for category, files in report.items():
        if category != "errors":
            print(f"{category.upper()}: {len(files)} files")
    
    if report["errors"]:
        print(f"\n❌ ERRORS: {len(report['errors'])} files failed")
        for error in report["errors"][:5]:  # Show first 5 errors
            print(f"   {error}")
    
    total_migrated = sum(len(files) for cat, files in report.items() if cat != "errors")
    print(f"\n✅ Migration complete: {total_migrated} files migrated with front-matter")