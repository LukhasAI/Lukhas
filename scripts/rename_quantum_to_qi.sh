#!/bin/bash

# Script to rename quantum files and classes to QI (quantum-inspired)

echo "🔄 Starting quantum → qi renaming process..."

# Files to rename (quantum → qi)
declare -a files_to_rename=(
    "candidate/bio/quantum.py:candidate/bio/qi.py"
    "candidate/core/symbolic_legacy/bio/mito_quantum_attention.py:candidate/core/symbolic_legacy/bio/mito_qi_attention.py"
    "candidate/core/symbolic_legacy/bio/mito_quantum_attention_adapter.py:candidate/core/symbolic_legacy/bio/mito_qi_attention_adapter.py"
    "candidate/core/symbolic_legacy/bio/quantum_attention.py:candidate/core/symbolic_legacy/bio/qi_attention.py"
    "candidate/core/bio_systems/quantum_inspired_layer.py:candidate/core/bio_systems/qi_layer.py"
    "candidate/core/bridges/consciousness_quantum_bridge.py:candidate/core/bridges/consciousness_qi_bridge.py"
    "candidate/core/bridges/quantum_memory_bridge.py:candidate/core/bridges/qi_memory_bridge.py"
    "candidate/core/adapters/quantum_service_adapter.py:candidate/core/adapters/qi_service_adapter.py"
    "candidate/core/orchestration/brain/attention/quantum_attention.py:candidate/core/orchestration/brain/attention/qi_attention.py"
    "candidate/core/orchestration/brain/quantum_annealed_consensus.py:candidate/core/orchestration/brain/qi_annealed_consensus.py"
    "candidate/core/orchestration/brain/quantum_neuro_symbolic_engine.py:candidate/core/orchestration/brain/qi_neuro_symbolic_engine.py"
    "candidate/memory/core/quantum_memory_manager.py:candidate/memory/core/qi_memory_manager.py"
    "candidate/memory/quantum_manager.py:candidate/memory/qi_manager.py"
    "candidate/memory/systems/quantum_memory_architecture.py:candidate/memory/systems/qi_memory_architecture.py"
    "candidate/bridge/voice/bio_core/voice/quantum_voice_enhancer.py:candidate/bridge/voice/bio_core/voice/qi_voice_enhancer.py"
    "candidate/bridge/voice/bio_core/oscillator/bio_quantum_engine.py:candidate/bridge/voice/bio_core/oscillator/bio_qi_engine.py"
    "candidate/bridge/voice/bio_core/oscillator/quantum_layer.py:candidate/bridge/voice/bio_core/oscillator/qi_layer.py"
    "candidate/consciousness/creativity/quantum_creative_types.py:candidate/consciousness/creativity/qi_creative_types.py"
    "candidate/consciousness/awareness/symbolic_quantum_attention.py:candidate/consciousness/awareness/symbolic_qi_attention.py"
    "candidate/consciousness/quantum_consciousness_integration.py:candidate/consciousness/qi_consciousness_integration.py"
    "candidate/consciousness/states/bio_quantum_engine.py:candidate/consciousness/states/bio_qi_engine.py"
    "candidate/consciousness/states/quantum_mesh_visualizer.py:candidate/consciousness/states/qi_mesh_visualizer.py"
    "candidate/consciousness/states/quantum_consciousness_hub.py:candidate/consciousness/states/qi_consciousness_hub.py"
    "candidate/consciousness/states/quantum_mesh_integrator.py:candidate/consciousness/states/qi_mesh_integrator.py"
    "candidate/consciousness/reflection/quantum_layer.py:candidate/consciousness/reflection/qi_layer.py"
    "candidate/consciousness/reflection/abas_quantum_specialist.py:candidate/consciousness/reflection/abas_qi_specialist.py"
)

# Process each file rename
for mapping in "${files_to_rename[@]}"; do
    IFS=':' read -r old_path new_path <<< "$mapping"
    if [ -f "$old_path" ]; then
        echo "📄 Renaming: $old_path → $new_path"
        git mv "$old_path" "$new_path" 2>/dev/null || mv "$old_path" "$new_path"
    fi
done

echo "✅ File renaming complete!"
echo ""
echo "📝 Now updating class names in Python files..."

# Update class names in all Python files
find . -name "*.py" -type f ! -path "./.git/*" ! -path "./__pycache__/*" -exec sed -i '' \
    -e 's/class QuantumInspired/class QI/g' \
    -e 's/class Quantum/class QI/g' \
    -e 's/QuantumProcessor/QIProcessor/g' \
    -e 's/QuantumEngine/QIEngine/g' \
    -e 's/QuantumManager/QIManager/g' \
    -e 's/QuantumBridge/QIBridge/g' \
    -e 's/QuantumAdapter/QIAdapter/g' \
    -e 's/QuantumAttention/QIAttention/g' \
    -e 's/QuantumMemory/QIMemory/g' \
    -e 's/QuantumCreative/QICreative/g' \
    -e 's/QuantumConsciousness/QIConsciousness/g' \
    -e 's/QuantumMesh/QIMesh/g' \
    -e 's/QuantumLayer/QILayer/g' \
    -e 's/from quantum/from qi/g' \
    -e 's/import quantum/import qi/g' \
    {} \;

echo "✅ Class name updates complete!"

# Update Lucas references
echo ""
echo "📝 Updating Lucas → Lukhas references..."

find . -name "*.py" -type f ! -path "./.git/*" ! -path "./__pycache__/*" -exec sed -i '' \
    -e 's/class LucasDASTEngine/class LukhasDASTEngine/g' \
    -e 's/class LucasDASTAPI/class LukhasDASTAPI/g' \
    -e 's/class TestLucasDASTIntegration/class TestLukhasDASTIntegration/g' \
    -e 's/class LucasVoiceSystem/class LukhasVoiceSystem/g' \
    -e 's/class BaseLucasModule/class BaseLukhasModule/g' \
    -e 's/class LucasPlugin/class LukhasPlugin/g' \
    -e 's/class LucasPluginManifest/class LukhasPluginManifest/g' \
    -e 's/class LucasGovernanceModule/class LukhasGovernanceModule/g' \
    -e 's/class LucasAGI/class LukhasAI/g' \
    -e 's/class LucasAnalyzeEngine/class LukhasAnalyzeEngine/g' \
    -e 's/class LucasSystemState/class LukhasSystemState/g' \
    -e 's/class BaseLucasPlugin/class BaseLukhasPlugin/g' \
    -e 's/class LucasLLM/class LukhasLLM/g' \
    -e 's/class LucasSymbolicValidator/class LukhasSymbolicValidator/g' \
    -e 's/class LucasBrainIntegration/class LukhasBrainIntegration/g' \
    -e 's/_LucasPrivateEthicsGuard/_LukhasPrivateEthicsGuard/g' \
    -e 's/LUCAS AGI/LUKHAS AI/g' \
    -e 's/Lucas/Lukhas/g' \
    {} \;

echo "✅ Lucas → Lukhas updates complete!"

echo ""
echo "🎯 Cleanup complete! Remember to:"
echo "  1. Review the changes with 'git status'"
echo "  2. Test the system to ensure nothing broke"
echo "  3. Commit the changes"