#!/usr/bin/env python3
"""
Import Connectivity Fixer
========================
Fixes import issues post-modularization.
"""

from pathlib import Path

# Import mappings discovered during analysis
IMPORT_MAPPINGS = {
    "memory.glyph_memory_integration": "core.glyph.glyph_memory_integration",
    "core.symbolic.glyphs": "core.glyph.glyphs",
    "core.symbolic.glyphs.glyph": "core.common.glyph",
    "memory.core_memory.memory_fold": "memory.folds.memory_fold",
    "memory.unified_memory_manager": "consciousness.reflection.unified_memory_manager",
    "core.symbolic_boot": "core.symbolic.symbolic_boot",
    "core.hub_registry": "core.integration.hub_registry",
    "memory.memory_hub": "consciousness.reflection.memory_hub",
    "core.bio_symbolic": "core.symbolic_legacy.bio.bio_symbolic",
    "memory.core_memory.memoria": "core.memoria",
    "core.symbolic.drift.drift_score": "consciousness.dream.oneiric.oneiric_core.analysis.drift_score",
    "core.docututor.symbolic_knowledge_core.knowledge_graph": (
        "tools.documentation.symbolic_knowledge_core.knowledge_graph"
    ),  # ΛTAG: mapping_wrap
    "core.adaptive_systems.crista_optimizer.crista_optimizer": "core.symbolic_legacy.bio.crista_optimizer",
    "core.service_discovery": "core.integration.service_discovery",
    "core.docututor.memory_evolution.voice_synthesis": "tools.documentation.memory_evolution.voice_synthesis",
    "consciousness.consciousness_hub": "consciousness.reflection.consciousness_hub",
    "consciousness.systems.awareness_engine": "consciousness.awareness.awareness_engine",
    "core.interfaces.ui.multimodal.image_generator": "core.common.interfaces.ui.multimodal.image_generator",
    "core.interfaces.ui.adaptive.adaptive_interface_generator": (
        "core.common.interfaces.ui.adaptive.adaptive_interface_generator"
    ),  # ΛTAG: mapping_wrap
    "core.cognitive.node": "memory.node",
    "core.engine.neuro_symbolic_engine": "core.orchestration.brain.neuro_symbolic.neuro_symbolic_engine",
    "core.config.settings": "core.orchestration.brain.config.settings",
    "core.config": "core.common.config",
    "consciousness.core_consciousness.awareness_engine": "consciousness.awareness.awareness_engine",
    "consciousness.core_consciousness.dream_engine.__init__": "qi_attention.__init__",
    "core.qi_identity_manager": (
        "._cleanup_archive.BACKUP_BEFORE_CONSOLIDATION_20250801_002312.core.qi_identity_manager"
    ),  # ΛTAG: mapping_wrap
    "memory.fold_engine": "memory.folds.fold_engine",
}


def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single file"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply import mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            # Handle various import patterns
            patterns = [
                (f"from {old_import} import", f"from {new_import} import"),
                (f"import {old_import}", f"import {new_import}"),
            ]

            for old_pattern, new_pattern in patterns:
                content = content.replace(old_pattern, new_pattern)

        # Save if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return False


def main():
    """Fix imports across the codebase"""
    # ΛTAG: path_resolution
    root = Path(__file__).resolve().parents[2]
    fixed_count = 0

    print("🔧 Fixing imports post-modularization...")

    for py_file in root.rglob("*.py"):
        if "archive" in str(py_file) or "__pycache__" in str(py_file):
            continue

        if fix_imports_in_file(py_file):
            print(f"   Fixed: {py_file.relative_to(root)}")
            fixed_count += 1

    print(f"\n✅ Fixed {fixed_count} files")


if __name__ == "__main__":
    main()
