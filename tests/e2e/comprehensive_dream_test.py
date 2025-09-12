#!/usr/bin/env python3
"""
Comprehensive Dream Components Testing
====================================
Testing all LUKHAS dream consciousness modules including emotion learning
and parallel reality systems for ethics and self-learning
"""

import importlib
import importlib.util
import sys
from pathlib import Path


def test_dream_component(module_path):
    """Test a single dream component module"""
    try:
        # Convert path to module name
        module_name = str(module_path).replace("/", ".").replace(".py", "")

        # Special handling for different module structures
        if module_name.startswith("."):
            module_name = module_name[1:]

        # Try importing the module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            return False, f"Could not create spec for {module_path}"

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return True, f"Successfully imported {module_name}"

    except Exception as e:
        return False, f"Failed to import {module_path}: {e!s}"


def main():
    """Test all dream components"""
    print("🌙 LUKHAS Dream Components Comprehensive Testing")
    print("Including Dream Emotion Learning & Parallel Reality Systems")
    print("=" * 70)

    # COMPREHENSIVE dream modules to test - including emotion learning and parallel reality
    dream_modules = [
        # Core dream orchestration
        "core/orchestration/brain/unified_integration/adapters/dream_adapter.py",
        "core/orchestration/brain/consciousness/dream_sequence.py",
        "core/orchestration/brain/consciousness/dream_state.py",
        "core/orchestration/brain/unified_integration/dream_memory_bridge.py",
        "core/orchestration/brain/unified_integration/dream_orchestration.py",
        "core/orchestration/integration/consciousness_dream.py",
        # CRITICAL: Dream emotion learning systems
        "candidate/consciousness/dream/core/dream_emotion_bridge.py",
        # CRITICAL: Parallel reality systems for ethics and self-learning
        "candidate/consciousness/dream/parallel_reality_simulator.py",
        "candidate/consciousness/dream/parallel_reality_safety.py",
        # Additional dream consciousness modules
        "candidate/consciousness/dream/core/dream_state_manager.py",
        "candidate/consciousness/dream/core/dream_sequence_coordinator.py",
        "candidate/consciousness/dream/core/dream_memory_integration.py",
        "candidate/consciousness/dream/lucid_dreaming.py",
        "candidate/consciousness/dream/dream_analytics.py",
        "candidate/consciousness/dream/dream_visualization.py",
        "candidate/consciousness/dream/integration/dream_consciousness_bridge.py",
        "candidate/consciousness/dream/integration/dream_memory_fusion.py",
        "candidate/consciousness/dream/integration/dream_orchestration_hub.py",
        "candidate/consciousness/dream/symbolic/dream_symbolism.py",
        "candidate/consciousness/dream/symbolic/dream_interpretation.py",
        "candidate/consciousness/dream/symbolic/archetypal_patterns.py",
    ]

    results = []
    successful = 0

    for module in dream_modules:
        module_path = Path(module)
        if module_path.exists():
            success, message = test_dream_component(module_path)
            results.append((module, success, message))
            if success:
                successful += 1

            # Special indicators for critical systems
            if "emotion" in module and success:
                print(f"🧠✅ {message} (EMOTION LEARNING)")
            elif "parallel_reality" in module and success:
                print(f"🌌✅ {message} (PARALLEL REALITY ETHICS)")
            elif success:
                print(f"✅ {message}")
            else:
                if "emotion" in module:
                    print(f"🧠❌ {message} (CRITICAL: EMOTION LEARNING)")
                elif "parallel_reality" in module:
                    print(f"🌌❌ {message} (CRITICAL: PARALLEL REALITY)")
                else:
                    print(f"❌ {message}")
        else:
            results.append((module, False, f"Module not found: {module}"))
            if "emotion" in module:
                print(f"🧠❌ Module not found: {module} (CRITICAL: EMOTION LEARNING)")
            elif "parallel_reality" in module:
                print(f"�❌ Module not found: {module} (CRITICAL: PARALLEL REALITY)")
            else:
                print(f"❌ Module not found: {module}")

    print("\n" + "=" * 70)
    print(f"Dream Testing Results: {successful}/{len(dream_modules)} modules working")
    print(f"Success Rate: {(successful/len(dream_modules)*100):.1f}%")

    # Critical system analysis
    emotion_modules = [m for m in dream_modules if "emotion" in m]
    parallel_modules = [m for m in dream_modules if "parallel_reality" in m]

    emotion_success = sum(1 for module, success, _ in results if "emotion" in module and success)
    parallel_success = sum(1 for module, success, _ in results if "parallel_reality" in module and success)

    print(f"\n🧠 Dream Emotion Learning: {emotion_success}/{len(emotion_modules)} modules working")
    print(f"🌌 Parallel Reality Ethics: {parallel_success}/{len(parallel_modules)} modules working")

    if successful < len(dream_modules):
        print("\n⚠️ Dream consciousness system requires attention!")
        print("Failed modules:")
        for module, success, message in results:
            if not success:
                if "emotion" in module:
                    print(f"  🧠 CRITICAL - {module}: {message}")
                elif "parallel_reality" in module:
                    print(f"  🌌 CRITICAL - {module}: {message}")
                else:
                    print(f"  - {module}: {message}")


if __name__ == "__main__":
    main()


def test_dream_components():
    """Test all dream-related components in the LUKHAS ecosystem"""

    print("🌙 COMPREHENSIVE DREAM COMPONENT TESTING 🌙")
    print("=" * 60)

    # Manually specify dream component paths from our search results
    dream_components = [
        # Core AGI dream systems (the 6 I already tested)
        "symbolic/vocabularies/dream_vocabulary.py",
        "hooks/gpt_dream_reflection.py",
        "agi_core/reasoning/dream_integration.py",
        "agi_core/learning/dream_guided_learner.py",
        "agi_core/tools/dream_guided_tools.py",
        "agi_core/memory/dream_memory.py",
        # Products ecosystem
        "products/communication/nias/dream_orchestrator_enhanced.py",
        "products/communication/nias/dream_generator.py",
        "products/communication/nias/dream_recorder.py",
        "products/communication/nias/core/dream_recorder.py",
        "products/communication/nias/dream_commerce_orchestrator.py",
        "products/experience/voice/bridge/dream_voice_pipeline.py",
        # Candidate systems
        "candidate/orchestration/dream_orchestrator.py",
        "candidate/governance/ethics/dream_generator.py",
        "candidate/governance/identity/core/colonies/dream_verification_colony.py",
        "candidate/governance/identity/core/auth/dream_auth.py",
        "candidate/emotion/dreamseed_upgrade.py",
        "candidate/qi/engines/dream/dream_adapter.py",
        "candidate/qi/engines/dream/dream_seed.py",
        "candidate/consciousness/dream_bridge.py",
        # Deployment & Infrastructure
        "deployment/platforms/dream_commerce/dream_commerce/dream_api.py",
        # Branding & Vocabularies
        "branding/vocabularies/dream_vocabulary.py",
    ]

    # Filter to existing files only
    existing_components = []
    for component in dream_components:
        if Path(component).exists():
            existing_components.append(component)
        else:
            print(f"⚠️  File not found: {component}")

    print(f"Found {len(existing_components)} dream components to test")
    print()

    successful = []
    failed = []

    for i, file_path in enumerate(existing_components, 1):
        print(f"{i:3d}. Testing: {file_path}")

        try:
            # Convert file path to module name
            module_path = str(file_path).replace("/", ".").replace(".py", "")

            # Try to import
            spec = importlib.util.spec_from_file_location(module_path, file_path)
            if spec is None:
                print(f"     ❌ Could not create spec for {module_path}")
                failed.append((str(file_path), "No spec"))
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_path] = module
            spec.loader.exec_module(module)

            # Check for main classes/functions
            classes = [
                name for name in dir(module) if not name.startswith("_") and hasattr(getattr(module, name), "__class__")
            ]
            functions = [name for name in dir(module) if callable(getattr(module, name)) and not name.startswith("_")]

            print(f"     ✅ SUCCESS - Classes: {len(classes)}, Functions: {len(functions)}")
            successful.append(str(file_path))

        except Exception as e:
            error_msg = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
            print(f"     ❌ FAILED - {error_msg}")
            failed.append((str(file_path), error_msg))

    print()
    print("=" * 60)
    print("🏆 COMPREHENSIVE DREAM TESTING RESULTS")
    print("=" * 60)
    print(
        f"✅ Successful: {len(successful)}/{len(existing_components)} ({len(successful)/len(existing_components)*100:.1f}%)"
    )
    print(f"❌ Failed: {len(failed)}/{len(existing_components)} ({len(failed)/len(existing_components)*100:.1f}%)")
    print()

    if failed:
        print("🚨 FAILED COMPONENTS:")
        for i, (file_path, error) in enumerate(failed, 1):
            print(f"{i:2d}. {file_path}")
            print(f"    Error: {error}")
        print()

    if successful:
        print("✅ SUCCESSFUL COMPONENTS:")
        for i, file_path in enumerate(successful, 1):
            print(f"{i:2d}. {file_path}")

    return len(successful), len(failed), failed


if __name__ == "__main__":
    successful_count, failed_count, failed_details = test_dream_components()

    if failed_count > 0:
        print(f"\n🎯 Next step: Fix {failed_count} failed dream components")
        sys.exit(1)
    else:
        print(f"\n🎉 ALL {successful_count} dream components are working perfectly!")
        sys.exit(0)
