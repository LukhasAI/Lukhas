INFO:ΛTRACE.bridge.llm_wrappers:Successfully imported UnifiedOpenAIClient
INFO:ΛTRACE.bridge.llm_wrappers:OpenAIModulatedService available
WARNING:root:Core voice systems not available (cannot import name 'GuardianValidator' from 'candidate.governance.guardian' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/governance/guardian/__init__.py)), using compatibility layer
INFO:lukhas.governance.auth_guardian_integration:Authentication Guardian initialized with drift threshold: 0.15
INFO:lukhas.governance.auth_integration_system:LUKHAS Authentication Integration System initialized: f8d585c6-7039-4765-bd20-c55f9c392942
INFO:identity:✅ Enhanced identity components loaded
INFO:identity:✅ Enhanced identity module loaded: 7/7 components ready
INFO:candidate.governance.identity.import_bridge:Identity import bridge installed
INFO:candidate.governance.identity:Identity namespace bridge initialized successfully
INFO:lukhas.qi:QI module loaded in DRY-RUN mode (set QI_ACTIVE=true to enable)
INFO:lukhas.emotion:✅ LUKHAS emotion system loaded successfully
INFO:lukhas.emotion:✅ Emotion module loaded: 7/7 components ready
INFO:lukhas.core.colonies:Imported BaseColony from candidate.core.colonies.base_colony
INFO:lukhas.core.colonies:Successfully imported real implementations from lukhas.core
/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/colonies/governance_colony.py:21: UserWarning: Could not import lukhas.governance ethics components: No module named 'lukhas.governance.policy'
  from ethics import EthicsEngine, SafetyChecker
INFO:candidate.core.colonies:Aliased GovernanceColony -> GovernanceColonyEnhanced from .governance_colony
INFO:memory:✅ Core LUKHAS memory system loaded
INFO:memory:✅ Enhanced memory components loaded
INFO:memory:✅ Enhanced memory module loaded: 8/8 components ready
INFO:bio:Bio Core systems loaded successfully
INFO:candidate.bio.core:bio core module initialized. Available components: ['BioEngine']
INFO:lukhas.accepted.bio:lukhas.accepted.bio: using candidate.bio implementations
INFO:lukhas.accepted.bio.symbolic:lukhas.accepted.bio.symbolic -> candidate.bio.symbolic
INFO:bio:Bio Symbolic systems loaded successfully
INFO:bio:Bio Awareness systems loaded successfully
INFO:bio:Bio Systems initialized: 3/3 subsystems operational
WARNING:candidate.core.colonies:Could not import CreativityColony: No module named 'bio.bio_utilities'
WARNING:candidate.core.colonies:Could not import TensorColonyOps: cannot import name 'TensorColonyOps' from 'candidate.core.colonies.tensor_colony_ops' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/colonies/tensor_colony_ops.py)
INFO:ΛTRACE.ethics_swarm_colony:ΛETHICS: Swarm Colony with simulation and drift correction loaded. Revolutionary ethical intelligence available.
WARNING:candidate.core.colonies:Could not import SymbolicReasoningColony: cannot import name 'Tag' from 'lukhas.core.symbolism.tags' (/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/core/symbolism/tags.py)
INFO:candidate.core.colonies:colonies module initialized. Available components: ['BaseColony', 'ColonyConsensus', 'ConsensusMethod', 'ConsensusProposal', 'EnhancedReasoningColony', 'EthicsSwarmColony', 'GovernanceColony', 'GovernanceColonyEnhanced', 'MemoryColony', 'MemoryColonyEnhanced', 'OracleColony', 'ReasoningColony', 'SimAgent', 'SupervisorAgent', 'SwarmNetwork', 'SwarmSignalNetwork', 'TemporalColony', 'VoteType']
WARNING:candidate.core.symbolism:Could not import Archiver: cannot import name 'Archiver' from 'candidate.core.symbolism.archiver' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/symbolism/archiver.py)
INFO:candidate.core.symbolism:symbolism module initialized. Available components: ['MethylationModel']
=== MEMORY MODULE STATUS CHECK ===

lukhas/memory:
✅ Loaded environment from: /Users/agi_dev/Library/Mobile Documents/com~apple~CloudDocs/Prototype/Lukhas-ecosystem/ABot/LukhasBot/.env
 LUKHAS AI Governance Module loaded: Phase 7 - Registry Updates and Policy Integration
< Trinity Framework: Identity-Consciousness-Guardian
 Phase 7 ID Integration: Available
  ✗ MemoryModule import failed: cannot import name 'MemoryModule' from 'lukhas.memory' (/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/memory/__init__.py)
  ✗ FoldSystem import failed: cannot import name 'FoldSystem' from 'lukhas.memory' (/Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/memory/__init__.py)
  ✗ FoldManager import failed: No module named 'lukhas.memory.fold_manager'

candidate/memory:
ℹ️ 2025-09-07 19:05:38  candidate.memory.integrity - INFO - integrity module initialized. Available components: ['CollapseHash']
ℹ️ 2025-09-07 19:05:38  candidate.memory.protection - INFO - protection module initialized. Available components: ['SymbolicQuarantineSanctum']
ℹ️ 2025-09-07 19:05:38  candidate.memory.scaffold - INFO - scaffold module initialized. Available components: ['AtomicMemoryScaffold']
ℹ️ 2025-09-07 19:05:38  candidate.memory.systems - INFO - Memory systems module initialized. Available components: ['CoreMemoryComponent', 'MemoryOrchestrator', 'MemorySystem']
INFO:hybrid_memory_fold:Re-exported VectorStorageLayer from candidate implementation
WARNING:candidate.memory.fold_system:Failed to import memory fold components: No module named 'memory_fold_system'
Warning: Memory components not available: No module named 'candidate.memory.consolidation.consolidation_orchestrator'
ℹ️ 2025-09-07 19:05:38  candidate.memory.core - INFO - core module initialized. Available components: ['ColonyMemoryValidator', 'HybridMemoryFold', 'UnifiedMemoryOrchestrator', 'create_hybrid_memory_fold']
  ✗ MemoryModule import failed: cannot import name 'MemoryModule' from 'candidate.memory' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/memory/__init__.py)
  ✗ ConsciousnessMemory import failed: No module named 'candidate.memory.consciousness_memory'

candidate/aka_qualia (Wave C):
  ✗ SqlMemory import failed: No module named 'candidate.aka_qualia.memory_client'
  ✗ NoopMemory import failed: No module named 'candidate.aka_qualia.memory_client'
