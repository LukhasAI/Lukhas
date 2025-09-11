#!/usr/bin/env python3
"""
FIXED Complete Documentation Migration Script for LUKHAS Repository
Migrates ALL 8,968+ markdown files to organized docs_new/ structure
"""

import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def find_all_markdown_files():
    """Use subprocess to get the exact same files as bash find command"""
    cmd = [
        "find",
        ".",
        "-name",
        "*.md",
        "-not",
        "-path",
        "./docs_new/*",
        "-not",
        "-path",
        "./.venv/*",
        "-not",
        "-path",
        "./node_modules/*",
        "-not",
        "-path",
        "./.git/*",
        "-not",
        "-path",
        "./site/*",
        "-not",
        "-path",
        "./lukhas_website/*",
        "-not",
        "-path",
        "./website_v1/*",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    files = [Path(f.strip()) for f in result.stdout.split("\n") if f.strip()]
    return files


def categorize_file(filepath):
    """Intelligently categorize files based on path and content"""
    path_str = str(filepath).lower()
    filename = filepath.name.lower()

    # Read first few lines to understand content type
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read(500).lower()
    except:
        content = ""

    # Concepts - Architecture, theory, frameworks
    if any(
        x in path_str
        for x in [
            "constellation",
            "framework",
            "architecture",
            "theory",
            "consciousness",
            "quantum",
            "bio",
            "matrix",
            "matriz",
        ]
    ):
        return "concepts"
    if any(x in filename for x in ["architecture", "framework", "constellation", "theory"]):
        return "concepts"
    if any(x in content for x in ["architecture", "framework", "constellation", "theory"]):
        return "concepts"

    # How-to guides - Setup, deployment, tutorials
    if any(x in path_str for x in ["setup", "install", "deploy", "tutorial", "guide", "howto"]):
        return "howto"
    if any(x in filename for x in ["setup", "install", "deploy", "tutorial", "guide", "quick"]):
        return "howto"
    if "readme" in filename and any(x in content for x in ["setup", "install", "getting started"]):
        return "howto"

    # Reference - API docs, schemas, specifications
    if any(x in path_str for x in ["api", "schema", "spec", "reference", "manifest"]):
        return "reference"
    if any(x in filename for x in ["api", "schema", "spec", "reference", "manifest"]):
        return "reference"
    if "module_manifest" in filename or "api_reference" in filename:
        return "reference"

    # Decisions - ADRs, architectural decisions
    if any(x in path_str for x in ["decision", "adr", "choice"]):
        return "decisions"
    if any(x in filename for x in ["decision", "adr-", "choice"]):
        return "decisions"

    # Runbooks - Operations, troubleshooting, monitoring
    if any(x in path_str for x in ["runbook", "ops", "monitor", "troubleshoot", "oncall"]):
        return "runbooks"
    if any(x in filename for x in ["runbook", "ops", "monitor", "troubleshoot", "oncall"]):
        return "runbooks"

    # Changelogs - Version history, release notes
    if any(x in filename for x in ["changelog", "history", "release", "version"]):
        return "changelogs"

    # Reports - Analysis, migration, status reports
    if any(x in path_str for x in ["report", "analysis", "migration", "audit"]):
        return "reports"
    if any(x in filename for x in ["report", "analysis", "migration", "audit"]):
        return "reports"

    # Default to reference for unknown files
    return "reference"


def determine_metadata(filepath, category):
    """Generate appropriate YAML front-matter"""
    path_str = str(filepath).lower()
    filename = filepath.name

    # Determine status
    if "candidate" in path_str:
        status = "draft"
    elif any(x in path_str for x in ["deprecated", "legacy", "old"]):
        status = "deprecated"
    elif "lukhas" in path_str or category in ["concepts", "reference"]:
        status = "stable"
    else:
        status = "review"

    # Determine owner based on path
    if "consciousness" in path_str:
        owner = "consciousness-architect"
    elif "memory" in path_str:
        owner = "memory-specialist"
    elif "identity" in path_str:
        owner = "identity-specialist"
    elif "bio" in path_str:
        owner = "bio-specialist"
    elif "quantum" in path_str:
        owner = "quantum-specialist"
    elif "guardian" in path_str or "ethics" in path_str:
        owner = "guardian-specialist"
    elif "api" in path_str:
        owner = "api-specialist"
    elif "test" in path_str:
        owner = "testing-specialist"
    elif category == "reports":
        owner = "principal-repo-surgeon"
    else:
        owner = "core-dev"

    # Determine tags
    tags = []
    if "consciousness" in path_str:
        tags.append("consciousness")
    if "memory" in path_str:
        tags.append("memory")
    if "identity" in path_str:
        tags.append("identity")
    if "api" in path_str:
        tags.append("api")
    if "test" in path_str:
        tags.append("testing")
    if not tags:
        tags.append("architecture")

    # Determine facets
    facets = {}
    if "candidate" in path_str:
        facets["layer"] = ["candidate"]
    elif "lukhas" in path_str:
        facets["layer"] = ["core"]
    else:
        facets["layer"] = ["gateway"]

    if "consciousness" in path_str:
        facets["domain"] = ["consciousness"]
    elif "memory" in path_str:
        facets["domain"] = ["memory"]
    elif "bio" in path_str:
        facets["domain"] = ["bio"]
    elif "quantum" in path_str:
        facets["domain"] = ["quantum"]
    else:
        facets["domain"] = ["symbolic"]

    facets["audience"] = ["dev"]

    return {
        "title": filename.replace(".md", "").replace("_", " ").title(),
        "status": status,
        "owner": owner,
        "last_review": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "tags": tags,
        "facets": facets,
    }


def add_front_matter(filepath, metadata):
    """Add YAML front-matter to markdown file"""
    try:
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except:
        return False

    # Check if already has front-matter
    if content.startswith("---\n"):
        return True

    # Create YAML front-matter
    yaml_header = "---\n"
    yaml_header += f"title: {metadata['title']}\n"
    yaml_header += f"status: {metadata['status']}\n"
    yaml_header += f"owner: {metadata['owner']}\n"
    yaml_header += f"last_review: {metadata['last_review']}\n"
    yaml_header += f"tags: {metadata['tags']}\n"
    yaml_header += "facets:\n"
    for key, value in metadata["facets"].items():
        yaml_header += f"  {key}: {value}\n"
    yaml_header += "---\n\n"

    # Write file with front-matter
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(yaml_header + content)
        return True
    except:
        return False


def migrate_documentation():
    """Main migration function - FIXED VERSION"""

    print("🚀 Starting FIXED Complete Documentation Migration")
    print("=" * 60)

    # Create docs_new structure if it doesn't exist
    base_dir = Path("docs_new")
    categories = ["concepts", "howto", "reference", "decisions", "runbooks", "changelogs", "reports"]

    for category in categories:
        (base_dir / category).mkdir(parents=True, exist_ok=True)

    # Use the FIXED file finding method
    md_files = find_all_markdown_files()

    print(f"📊 Found {len(md_files)} markdown files to migrate (FIXED COUNT)")

    # Migration statistics
    stats = {category: 0 for category in categories}
    migrated = 0
    errors = 0

    # Process each file
    for i, source_file in enumerate(md_files):
        if i % 500 == 0:
            print(f"Progress: {i}/{len(md_files)} ({i/len(md_files)*100:.1f}%)")

        try:
            # Determine category
            category = categorize_file(source_file)
            stats[category] += 1

            # Create target directory structure
            relative_path = source_file
            if str(relative_path).startswith("./"):
                relative_path = Path(str(relative_path)[2:])

            target_dir = base_dir / category / relative_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / relative_path.name

            # Copy file
            shutil.copy2(source_file, target_file)

            # Add front-matter
            metadata = determine_metadata(source_file, category)
            add_front_matter(target_file, metadata)

            migrated += 1

        except Exception as e:
            print(f"❌ Error migrating {source_file}: {e}")
            errors += 1

    print("\n✅ FIXED Migration Complete!")
    print(f"📊 Files migrated: {migrated}")
    print(f"❌ Errors: {errors}")
    print("\n📈 Category Distribution:")
    for category, count in stats.items():
        print(f"  {category}: {count} files")

    return migrated, errors, stats


if __name__ == "__main__":
    migrate_documentation()
