#!/usr/bin/env python3
"""
Simple navigation update for mkdocs.yml
"""

# Create a comprehensive but manageable navigation structure
nav_content = """nav:
  - Overview: index.md
  - Concepts:
      - Constellation Framework: concepts/constellation-framework.md
      - Identity & Authentication: concepts/identity-system.md
      - Memory & Persistence: concepts/memory-system.md
      - Ethics & Governance: concepts/ethics-governance.md
      - Quantum-Bio Processing: concepts/quantum-bio.md
      - Vocabularies:
          - LUKHAS Vocabulary: concepts/vocabularies/LUKHAS_VOCABULARY_PUBLIC.md
          - Constellation Framework: concepts/vocabularies/CONSTELLATION_FRAMEWORK.md
          - Two Stream Vocabulary: concepts/vocabularies/TWO_STREAM_VOCABULARY_COMPLETE.md
          - Lexicon System: concepts/vocabularies/LEXICON_SYSTEM_COMPLETE.md
      - Candidate Systems:
          - Quantum Bio Consciousness: concepts/candidate/quantum_bio_consciousness/README.md
          - Core Symbolic Legacy: concepts/candidate/core/symbolic_legacy/README.md
          - GLYPH Consciousness: concepts/candidate/core/symbolic_legacy/GLYPH_CONSCIOUSNESS_PROTOCOLS.md
      - Branding & Tone:
          - Tone Presets: concepts/tone/presets/poetic_grounded.prompt.md
          - Modulation System: concepts/modulation/README.md
  - How-to:
      - Quick Start: howto/quick-start.md
      - Development Setup: howto/development-setup.md
      - Testing Guide: howto/testing.md
      - Deployment: howto/deployment.md
      - Contribute Docs: howto/contribute-docs.md
      - Code of Conduct: howto/code-of-conduct.md
      - Contributing: howto/contributing.md
  - Reference:
      - API Overview: reference/index.md
      - Core Modules: reference/core.md
      - Lukhas Modules: reference/lukhas.md
      - Candidate Modules: reference/candidate.md
      - Configuration: reference/configuration.md
      - Claude Integration: reference/claude-integration.md
      - Candidate Systems:
          - Tools: reference/candidate/tools/README.md
          - Core Systems: reference/candidate/core/README.md
          - Bio Systems: reference/candidate/bio/README.md
  - Decisions:
      - ADRs Overview: decisions/index.md
      - "ADR-0001 Choose MkDocs": decisions/ADR-0001-choose-mkdocs.md
  - Runbooks:
      - On-call Guide: runbooks/oncall.md
      - Monitoring: runbooks/monitoring.md
      - Troubleshooting: runbooks/troubleshooting.md
      - Security: runbooks/security.md
  - Changelogs:
      - Release Notes: changelogs/app.md
      - Change Log: changelogs/changelog.md
  - Reports:
      - Migration Report: reports/docs_reorg.md
      - Analysis Reports:
          - Audit Reports: reports/audit/README.md
          - Business Reports: reports/business/README.md
"""


def update_mkdocs_navigation():
    """Update mkdocs.yml navigation section"""

    # Read original file
    with open("mkdocs.yml") as f:
        lines = f.readlines()

    # Find nav section and replace it
    new_lines = []
    skip_nav = False

    for line in lines:
        if line.startswith("nav:"):
            skip_nav = True
            # Add our new nav content
            new_lines.extend(nav_content.split("\n"))
            new_lines.append("\n")
            continue
        elif skip_nav and line.startswith("markdown_extensions:"):
            skip_nav = False

        if not skip_nav:
            new_lines.append(line)

    # Write updated file
    with open("mkdocs.yml", "w") as f:
        f.writelines(new_lines)

    print("✅ Updated mkdocs.yml navigation")


if __name__ == "__main__":
    update_mkdocs_navigation()
