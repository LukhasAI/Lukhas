lukhas -> /Users/agi_dev/LOCAL-REPOS/Lukhas/lukhas/__init__.py
matriz -> /Users/agi_dev/LOCAL-REPOS/Lukhas/matriz/__init__.py
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports -v
Usage: lint-imports [OPTIONS]
Try 'lint-imports --help' for help.

Error: No such option: -v
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports --verbose
=============
Import Linter
=============

Verbose mode.
Building import graph (cache directory is .import_linter_cache)...
Used cache meta file .import_linter_cache/lukhas.meta.json.
Used cache data file .import_linter_cache/d81b79999ed617163375e03528da3b15227e8393.data.json.
Wrote data cache file .import_linter_cache/d81b79999ed617163375e03528da3b15227e8393.data.json.
Wrote meta cache file .import_linter_cache/lukhas.meta.json.
Built graph in 0.007s.

---------
Contracts
---------

Analyzed 133 files, 180 dependencies.
-------------------------------------


Contracts: 0 kept, 0 broken.
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports --verbose
=============
Import Linter
=============

Verbose mode.
Building import graph (cache directory is .import_linter_cache)...
Could not find package 'l' in your Python path.
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports --verbose
=============
Import Linter
=============

Verbose mode.
Building import graph (cache directory is .import_linter_cache)...
Used cache meta file .import_linter_cache/lukhas.meta.json.
Used cache data file .import_linter_cache/d81b79999ed617163375e03528da3b15227e8393.data.json.
Wrote data cache file .import_linter_cache/d81b79999ed617163375e03528da3b15227e8393.data.json.
Wrote meta cache file .import_linter_cache/lukhas.meta.json.
Built graph in 0.005s.

---------
Contracts
---------

Analyzed 133 files, 180 dependencies.
-------------------------------------


Contracts: 0 kept, 0 broken.
agi_dev@g Lukhas % cd /Users/agi_dev/LOCAL-REPOS/Lukhas && PYTHONPATH=. python3 
-c "
cmdand dquote> import lukhas
cmdand dquote> print('✅ lukhas found')
cmdand dquote> try:
cmdand dquote>     import lukhas.core
cmdand dquote>     print('✅ lukhas.core found')
cmdand dquote> except:
cmdand dquote>     print('❌ lukhas.core NOT found')
cmdand dquote> try:
cmdand dquote>     import matriz
cmdand dquote>     print('✅ matriz found')
cmdand dquote> except:
cmdand dquote>     print('❌ matriz NOT found')
cmdand dquote> try:
cmdand dquote>     import candidate
cmdand dquote>     print('❌ candidate should be forbidden but is accessible')
cmdand dquote> except:
cmdand dquote>     print('✅ candidate correctly not accessible')
cmdand dquote> "
INFO:lukhas.governance.auth_guardian_integration:Authentication Guardian initialized with drift threshold: 0.15
INFO:lukhas.governance.auth_integration_system:LUKHAS Authentication Integration System initialized: 56e096e8-5c71-42a3-b981-6e96505f5bcc
 LUKHAS AI Governance Module loaded: Phase 7 - Registry Updates and Policy Integration
< Constellation Framework: Identity-Consciousness-Guardian
 Phase 7 ID Integration: Available
INFO:identity:✅ Enhanced identity components loaded
INFO:identity:✅ Enhanced identity module loaded: 7/7 components ready
INFO:lukhas.governance.identity:Real identity module already exists - not overriding
INFO:lukhas.governance.identity:Real identity module already loaded - not overriding
INFO:lukhas.governance.identity:Identity namespace bridge initialized successfully
INFO:candidate.governance.identity.import_bridge:Identity import bridge installed
INFO:candidate.governance.identity:Identity namespace bridge initialized successfully
INFO:ΛTRACE.bridge.llm_wrappers:Successfully imported UnifiedOpenAIClient
INFO:ΛTRACE.bridge.llm_wrappers:Successfully imported UnifiedOpenAIClient
INFO:ΛTRACE.bridge.llm_wrappers:OpenAIModulatedService available
/Users/agi_dev/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
✅ Loaded environment from: /Users/agi_dev/LOCAL-REPOS/Lukhas/.env
WARNING:root:Core voice systems not available (cannot import name 'GuardianValidator' from 'candidate.governance.guardian' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/governance/guardian/__init__.py)), using compatibility layer
INFO:auth.service:⚠️ Using fallback mock implementations
INFO:auth.service:Info: Wallet authentication not available
INFO:auth.service:Authentication service initialized with fallback implementations
INFO:lukhas.core.colonies:Imported BaseColony from candidate.core.colonies.base_colony
INFO:lukhas.core.colonies:Successfully imported real implementations from lukhas.core
WARNING:candidate.core.colonies:Could not import MemoryColony: No module named 'lukhas.core.swarm'
/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/colonies/governance_colony.py:19: UserWarning: Could not import lukhas.governance ethics components: No module named 'lukhas.governance.bridge'
  from ethics import EthicsEngine, SafetyChecker
INFO:candidate.core.colonies:Aliased GovernanceColony -> GovernanceColonyEnhanced from .governance_colony
INFO:memory:✅ Core LUKHAS memory system loaded
INFO:memory:✅ Enhanced memory components loaded
INFO:memory:✅ Enhanced memory module loaded: 8/8 components ready
WARNING:candidate.core.colonies:Could not import CreativityColony: No module named 'lukhas.accepted.bio.utils'; 'lukhas.accepted.bio' is not a package
WARNING:candidate.core.colonies:Could not import TensorColonyOps: cannot import name 'TensorColonyOps' from 'candidate.core.colonies.tensor_colony_ops' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/colonies/tensor_colony_ops.py)
INFO:ΛTRACE.ethics_swarm_colony:ΛETHICS: Swarm Colony with simulation and drift correction loaded. Revolutionary ethical intelligence available.
WARNING:candidate.core.colonies:Could not import SymbolicReasoningColony: cannot import name 'SymbolicVocabulary' from 'symbolic.vocabularies' (/Users/agi_dev/LOCAL-REPOS/Lukhas/symbolic/vocabularies/__init__.py)
INFO:candidate.core.colonies:colonies module initialized. Available components: ['BaseColony', 'ColonyConsensus', 'ConsensusMethod', 'ConsensusProposal', 'EnhancedReasoningColony', 'EthicsSwarmColony', 'GovernanceColony', 'GovernanceColonyEnhanced', 'OracleColony', 'ReasoningColony', 'SimAgent', 'SupervisorAgent', 'SwarmNetwork', 'SwarmSignalNetwork', 'TemporalColony', 'VoteType']
WARNING:candidate.core.symbolism:Could not import Archiver: cannot import name 'Archiver' from 'candidate.core.symbolism.archiver' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/symbolism/archiver.py)
INFO:candidate.core.symbolism:symbolism module initialized. Available components: ['MethylationModel']
ℹ️ 2025-09-10 19:22:41  candidate.memory.integrity - INFO - integrity module initialized. Available components: ['CollapseHash']
ℹ️ 2025-09-10 19:22:41  candidate.memory.protection - INFO - protection module initialized. Available components: ['SymbolicQuarantineSanctum']
ℹ️ 2025-09-10 19:22:41  candidate.memory.scaffold - INFO - scaffold module initialized. Available components: ['AtomicMemoryScaffold']
ℹ️ 2025-09-10 19:22:41  candidate.memory.systems - INFO - Memory systems module initialized. Available components: ['CoreMemoryComponent', 'MemoryOrchestrator', 'MemorySystem']
Warning: Memory components not available: No module named 'lukhas_pb2'
WARNING:candidate.memory.fold_system:Failed to import memory fold components: No module named 'hybrid_memory_fold'
ℹ️ 2025-09-10 19:22:41  candidate.memory.core - INFO - core module initialized. Available components: ['ColonyMemoryValidator', 'HybridMemoryFold', 'UnifiedMemoryOrchestrator', 'create_hybrid_memory_fold']
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: Initializing 'core.advanced.brain.awareness' package.
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: Core awareness components imported.
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: 'core.advanced.brain.awareness' package initialized. Exposed symbols in __all__: ['BioSymbolicAwarenessAdapter', 'LucasAwarenessProtocol', 'SymbolicTraceLogger']
INFO:ΛTRACE.consciousness.core_consciousness.awareness_engine:ΛTRACE: Initializing awareness_engine module.
i 2025-09-10 19:22:41  lukhas.governance.security.access_control - INFO - 🛡️ Production Permission Manager initialized
🛡️ Sync Access Control Engine initialized
i 2025-09-10 19:22:41  lukhas.governance.ethics.constitutional_ai - INFO - 🛡️ Production Constitutional AI Framework initialized
i 2025-09-10 19:22:41  lukhas.governance.ethics.constitutional_ai - INFO - 🛡️ Production Safety Monitor initialized
✅ Identity Connector: Using real production implementations
Info: Integration hub not available, using standalone mode
✅ Identity Connector initialized: production implementation
🛡️ Constitutional AI Safety: ACTIVE
⚛️ Tiered Access Control T1-T5: ACTIVE
📋 Full Audit Compliance: ACTIVE
⚠️ Extreme performance optimizations not available - falling back to standard implementation
Warning: Could not initialize identity components: TierValidator() takes no arguments
INFO:candidate.core.module_registry:ModuleRegistry initialized - Tier enforcement: True
INFO:candidate.bio.core:bio core module initialized. Available components: ['BioEngine']
INFO:lukhas.qi:QI module loaded in DRY-RUN mode (set QI_ACTIVE=true to enable)
INFO:lukhas.emotion:✅ LUKHAS emotion system loaded successfully
INFO:lukhas.emotion:✅ Emotion module loaded: 7/7 components ready
✅ lukhas found
✅ lukhas.core found
✅ matriz found
❌ candidate should be forbidden but is accessible
agi_dev@g Lukhas % rm -rf .import_linter_cache
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 133 files, 180 dependencies.
-------------------------------------


Contracts: 0 kept, 0 broken.
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 133 files, 180 dependencies.
-------------------------------------


Contracts: 0 kept, 0 broken.
agi_dev@g Lukhas % grep -r "import lukhas" matriz/ || echo "No lukhas imports fo
und in matriz"
No lukhas imports found in matriz
agi_dev@g Lukhas % grep -r "import candidate\|from candidate" lukhas/ | head -5
lukhas/core/colonies/__init__.py:# Try to prefer real implementations from candidate lane first
lukhas/core/colonies/__init__.py:logger.debug("Attempting to import colony implementations from candidate lane")
lukhas/core/colonies/__init__.py:# Stable lane does not import candidate colonies dynamically.
lukhas/core/core_wrapper.py:            # from candidate modules loaded at runtime
lukhas/core/policy/MODULE_MANIFEST.json:  "notes": "Interfaces-only in accepted; heavy logic promoted from candidate later."
agi_dev@g Lukhas % grep -r "^from candidate\|^import candidate" lukhas/ | head -
10
agi_dev@g Lukhas % grep -rn "from candidate\|import candidate" lukhas/ | grep -v
 "#" | head -5
lukhas/core/colonies/__init__.py:42:logger.debug("Attempting to import colony implementations from candidate lane")
lukhas/core/policy/MODULE_MANIFEST.json:9:  "notes": "Interfaces-only in accepted; heavy logic promoted from candidate later."
lukhas/identity/auth_service.py:42:    """Dynamically import candidate components if available"""
lukhas/identity/passkey/MODULE_MANIFEST.json:10:    "No static imports from candidate/",
lukhas/orchestration/context/MODULE_MANIFEST.json:10:    "No static imports from candidate/",
agi_dev@g Lukhas % find lukhas/ -name "*.py" -exec grep -l "from candidate\|impo
rt candidate" {} \;
lukhas/core/colonies/__init__.py
lukhas/core/core_wrapper.py
lukhas/identity/auth_service.py
lukhas/governance/guardian/guardian_impl.py
agi_dev@g Lukhas % grep -n "from candidate\|import candidate" lukhas/core/coloni
es/__init__.py
41:# Try to prefer real implementations from candidate lane first
42:logger.debug("Attempting to import colony implementations from candidate lane")
94:# Stable lane does not import candidate colonies dynamically.
agi_dev@g Lukhas % grep -A5 -B5 "_try_import.*candidate" lukhas/core/colonies/__
init__.py

# Try to prefer real implementations from candidate lane first
logger.debug("Attempting to import colony implementations from candidate lane")


def _try_import(name: str, candidate_module: str, item_name: str):
    try:
        mod = importlib.import_module(candidate_module)
        if hasattr(mod, item_name):
            logger.info(f"Imported {item_name} from {candidate_module}")
            return getattr(mod, item_name)
--
    votes: dict[str, Any]
    participation_rate: float
    dissent_reasons: list[str] = field(default_factory=list)


BaseColony = _try_import("BaseColony", "candidate.core.colonies.base_colony", "BaseColony")

if BaseColony is None:
    logger.warning("Using BaseColony stub (no cross-lane imports)")

    class BaseColony(ABC):
agi_dev@g Lukhas % grep -A3 -B3 "from candidate\|import candidate" lukhas/govern
ance/guardian/guardian_impl.py

Note: This is a placeholder implementation that would be loaded when the
feature flag is active. The real implementation would integrate with the
full Guardian System v1.0.0 from candidate/governance/guardian/.
"""

from __future__ import annotations
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 133 files, 180 dependencies.
-------------------------------------


Contracts: 0 kept, 0 broken.
agi_dev@g Lukhas % rm test_import_violation.py
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 134 files, 180 dependencies.
-------------------------------------


Contracts: 0 kept, 0 broken.
agi_dev@g Lukhas % find . -name "core.py" | grep candidate
./candidate/bio/core.py
./candidate/core/orchestration/core.py
./candidate/core/orchestration/brain/abstract_reasoning/core.py
./candidate/core/orchestration/brain/emotional/core.py
./candidate/core/orchestration/brain/orchestration/core.py
./candidate/memory/systems/core.py
./candidate/consciousness/reflection/core.py
./candidate/governance/guardian/core.py
./candidate/aka_qualia/core.py
agi_dev@g Lukhas % ls -la candidate/core/
total 3360
drwxr-x---@ 193 agi_dev  staff   6176 Sep 10 15:20 .
drwxr-x---@  39 agi_dev  staff   1248 Sep 10 15:20 ..
-rw-r-----@   1 agi_dev  staff  20484 Sep  8 08:21 .DS_Store
-rw-r-----@   1 agi_dev  staff  13749 Aug 26 16:58 AGENT_COORDINATION.md
-rw-r-----@   1 agi_dev  staff   1926 Aug 26 16:58 AGI_Core_System.md
-rw-r-----@   1 agi_dev  staff   7443 Aug 26 16:58 API_INDEX.md
-rw-r-----@   1 agi_dev  staff  51607 Aug 26 16:58 API_MISMATCH_REPORT.md
-rw-r-----@   1 agi_dev  staff  18358 Aug 26 16:58 API_REFERENCE.md
-rw-r-----@   1 agi_dev  staff  10417 Aug 22 02:29 AUTOMATIC_TESTING_GUIDE.md
-rw-r-----@   1 agi_dev  staff   6292 Aug 22 02:29 DEPLOYMENT_STATUS.md
-rw-r-----@   1 agi_dev  staff  18285 Aug 26 16:58 FAULT_TOLERANCE_ARCHITECTURE.md
-rw-r-----@   1 agi_dev  staff  17480 Aug 22 02:29 GOLDEN_FEATURES_AUDIT.md
-rw-r-----@   1 agi_dev  staff  12497 Aug 26 16:58 IMPLEMENTATION_SUMMARY.md
-rw-r-----@   1 agi_dev  staff   1991 Aug 22 02:29 INTERNAL_USE_README.md
-rw-r-----@   1 agi_dev  staff   1510 Aug 26 16:58 LAYER.md
-rw-r-----@   1 agi_dev  staff  12353 Aug 26 16:58 MAILBOX_ARCHITECTURE.md
-rw-r-----@   1 agi_dev  staff   5701 Aug 22 02:29 MISSION_ACCOMPLISHED_REPORT.md
-rw-r-----@   1 agi_dev  staff   1811 Aug 26 16:58 MODULE_MANIFEST.json
-rw-r-----@   1 agi_dev  staff  10902 Aug 26 16:58 QUICK_START_FAULT_TOLERANCE.md
-rw-r-----@   1 agi_dev  staff   3272 Aug 22 02:29 QUICK_START_GUIDE.md
-rw-r-----@   1 agi_dev  staff    426 Aug 26 16:58 README.md
-rw-r-----@   1 agi_dev  staff    538 Aug 22 02:29 README_INDEX.md
-rw-r--r--@   1 agi_dev  staff  15585 Sep  5 22:24 README_MATRIZ_CONSCIOUSNESS_INTEGRATION.md
-rw-r--r--@   1 agi_dev  staff  12204 Sep  5 22:24 README_MATRIZ_CONSCIOUSNESS_SYSTEM.md
-rw-r-----@   1 agi_dev  staff  14902 Aug 22 02:29 README_core_drift.md
-rw-r-----@   1 agi_dev  staff  26269 Aug 22 02:29 README_core_trace.md
-rw-r-----@   1 agi_dev  staff   6424 Aug 26 16:58 SYSTEM_HEALTH_REPORT.md
-rw-r--r--@   1 agi_dev  staff   1013 Sep 10 15:20 __init__.py
-rw-r--r--@   1 agi_dev  staff   1669 Sep 10 15:20 actor_model.py
-rw-r--r--@   1 agi_dev  staff   5038 Sep 10 15:20 actor_supervision_integration.py
-rw-r--r--@   1 agi_dev  staff   2296 Sep 10 15:20 actor_system.py
drwxr-x---@   6 agi_dev  staff    192 Sep 10 15:20 adapters
-rw-r--r--@   1 agi_dev  staff  15463 Sep 10 15:20 adaptive_ux_engine.py
drwxr-x---@  10 agi_dev  staff    320 Sep 10 15:20 agi
drwxr-xr-x@   6 agi_dev  staff    192 Sep 10 15:20 agi_preparedness
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 ai
drwxr-x---@   8 agi_dev  staff    256 Sep  8 22:24 api
-rw-r--r--@   1 agi_dev  staff  18285 Sep 10 13:52 api_diff_analyzer.py
-rw-r-----@   1 agi_dev  staff  38953 Aug 26 16:58 api_fixes.json
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 architectures
drwxr-x---@   8 agi_dev  staff    256 Sep 10 15:20 audit
drwxr-x---@   9 agi_dev  staff    288 Sep 10 15:20 base
-rw-r--r--@   1 agi_dev  staff  27944 Sep 10 15:20 bio_symbolic_processor.py
drwxr-x---@   4 agi_dev  staff    128 Sep  2 04:19 bio_systems
-rw-r--r--@   1 agi_dev  staff  14576 Sep 10 13:52 bootstrap.py
-rw-r--r--@   1 agi_dev  staff   9408 Sep 10 15:20 bot.py
drwxr-x---@  11 agi_dev  staff    352 Sep 10 15:20 bridges
drwxr-x---@   7 agi_dev  staff    224 Sep 10 15:20 business
-rw-r--r--@   1 agi_dev  staff   1912 Sep 10 15:20 cluster_sharding.py
-rw-r--r--@   1 agi_dev  staff   4039 Sep 10 15:20 collaboration.py
drwxr-x---@   8 agi_dev  staff    256 Sep 10 15:20 collective
drwxr-x---@  20 agi_dev  staff    640 Sep 10 15:20 colonies
drwxr-x---@   9 agi_dev  staff    288 Sep 10 15:20 common
-rw-r--r--@   1 agi_dev  staff   3056 Sep 10 15:20 common.py
drwxr-xr-x@   7 agi_dev  staff    224 Sep 10 15:20 compliance
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 config
-rw-r-----@   1 agi_dev  staff    477 Aug 26 16:58 config.json
drwxr-x---@  12 agi_dev  staff    384 Sep 10 15:20 consciousness
drwxr-xr-x@   4 agi_dev  staff    128 Sep 10 15:20 consciousness_ascension
-rw-r--r--@   1 agi_dev  staff  33389 Sep 10 19:02 consciousness_data_flow.py
-rw-r--r--@   1 agi_dev  staff  37099 Sep 10 13:52 consciousness_network_monitor.py
-rw-r--r--@   1 agi_dev  staff  31070 Sep 10 15:20 consciousness_signal_router.py
-rw-r--r--@   1 agi_dev  staff   1332 Sep 10 15:20 consistency_manager.py
-rw-r--r--@   1 agi_dev  staff  35435 Sep 10 13:52 constellation_alignment_system.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 container
-rw-r--r--@   1 agi_dev  staff   1749 Sep 10 15:20 coordination.py
-rw-r--r--@   1 agi_dev  staff  27419 Sep 10 15:20 core_hub.py
-rw-r--r--@   1 agi_dev  staff   2821 Sep 10 15:20 core_system.py
-rw-r--r--@   1 agi_dev  staff   5575 Sep 10 15:20 core_utilities.py
drwxr-x---@   4 agi_dev  staff    128 Sep  2 04:19 db
-rw-r--r--@   1 agi_dev  staff   7986 Sep 10 19:02 decorators.py
-rw-r--r--@   1 agi_dev  staff  25297 Sep 10 15:20 distributed_tracing.py
-rw-r--r--@   1 agi_dev  staff  22495 Sep 10 15:20 efficient_communication.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 endocrine
-rw-r--r--@   1 agi_dev  staff  29412 Sep 10 19:02 energy_consumption_analysis.py
drwxr-x---@   8 agi_dev  staff    256 Sep 10 15:20 engines
-rw-r--r--@   1 agi_dev  staff  24397 Sep 10 13:52 enhanced_matriz_adapter.py
-rw-r--r--@   1 agi_dev  staff   7110 Sep 10 19:02 enhanced_swarm.py
-rw-r--r--@   1 agi_dev  staff    101 Sep 10 15:20 errors.py
drwxr-x---@   5 agi_dev  staff    160 Sep 10 15:20 ethics
-rw-r--r--@   1 agi_dev  staff  14361 Sep 10 19:02 event_bus.py
-rw-r--r--@   1 agi_dev  staff  20168 Sep 10 15:20 event_sourcing.py
drwxr-x---@   5 agi_dev  staff    160 Sep 10 15:20 events
drwxr-x---@   5 agi_dev  staff    160 Sep 10 15:20 examples
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 explainability
-rw-r--r--@   1 agi_dev  staff  10233 Sep 10 15:20 fallback_services.py
-rw-r--r--@   1 agi_dev  staff   2451 Sep 10 15:20 fault_tolerance.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 flow
-rw-r--r--@   1 agi_dev  staff    124 Sep 10 13:52 framework_integration.py
drwxr-x---@  19 agi_dev  staff    608 Sep 10 15:20 glyph
-rw-r--r--@   1 agi_dev  staff    424 Sep 10 15:20 glyph.py
drwxr-x---@  11 agi_dev  staff    352 Sep 10 15:20 governance
-rw-r-----@   1 agi_dev  staff   2552 Aug 26 16:58 hello.md
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 helpers
drwxr-x---@   5 agi_dev  staff    160 Sep 10 15:20 hub_services
-rw-r--r--@   1 agi_dev  staff  31093 Sep 10 19:02 id.py
drwxr-x---@  22 agi_dev  staff    704 Sep 10 15:20 identity
-rw-r--r--@   1 agi_dev  staff  14920 Sep 10 15:20 identity_aware_base.py
-rw-r--r--@   1 agi_dev  staff  29875 Sep 10 15:20 identity_aware_base_colony.py
-rw-r--r--@   1 agi_dev  staff  13543 Sep 10 15:20 identity_integration.py
-rw-r--r--@   1 agi_dev  staff  32893 Sep 10 15:20 image_processing_pipeline.py
drwxr-x---@   7 agi_dev  staff    224 Sep 10 15:20 infrastructure
-rw-r--r--@   1 agi_dev  staff   7683 Sep 10 15:20 integrated_system.py
drwxr-x---@  29 agi_dev  staff    928 Sep 10 15:20 integration
-rw-r--r--@   1 agi_dev  staff  18904 Sep 10 15:20 integration_hub.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 integrations
-rw-r--r--@   1 agi_dev  staff  41302 Sep 10 19:02 integrator.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 interaction
drwxr-x---@  42 agi_dev  staff   1344 Sep 10 15:20 interfaces
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 introspection
drwxr-xr-x@   3 agi_dev  staff     96 Sep 10 15:20 log_system
drwxr-xr-x@   4 agi_dev  staff    128 Sep 10 15:20 logging
-rw-r--r--@   1 agi_dev  staff  25214 Sep 10 15:20 mailbox.py
-rw-r--r--@   1 agi_dev  staff   5999 Sep 10 15:20 matriz_adapter.py
-rw-r--r--@   1 agi_dev  staff  22881 Sep 10 15:20 matriz_consciousness_integration.py
-rw-r--r--@   1 agi_dev  staff  20494 Sep 10 13:52 matriz_consciousness_signals.py
-rw-r--r--@   1 agi_dev  staff  28272 Sep 10 15:20 matriz_integrated_demonstration.py
-rw-r--r--@   1 agi_dev  staff  25083 Sep 10 15:20 matriz_signal_emitters.py
-rw-r--r--@   1 agi_dev  staff    253 Sep 10 15:20 memory_core.py
drwxr-x---@   9 agi_dev  staff    288 Sep 10 15:20 meta_learning
-rw-r--r--@   1 agi_dev  staff    957 Sep 10 15:20 minimal_actor.py
-rw-r--r--@   1 agi_dev  staff  16301 Sep 10 15:20 module_manager.py
-rw-r--r--@   1 agi_dev  staff  20120 Sep 10 15:20 module_registry.py
drwxr-x---@   5 agi_dev  staff    160 Sep 10 15:20 modules
drwxr-x---@   7 agi_dev  staff    224 Sep 10 15:20 monitoring
drwxr-xr-x@   4 agi_dev  staff    128 Sep 10 15:20 multiverse_creative
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 net
drwxr-x---@   7 agi_dev  staff    224 Sep 10 15:20 neural
drwxr-x---@   7 agi_dev  staff    224 Sep 10 15:20 neural_architectures
-rw-r--r--@   1 agi_dev  staff   1824 Sep 10 15:20 neural_bridge.py
-rw-r--r--@   1 agi_dev  staff   1422 Sep 10 15:20 neuroplastic_connector.py
-rwxr-xr-x@   1 agi_dev  staff  32167 Sep  9 12:23 notion_sync.py
drwxr-x---@  10 agi_dev  staff    320 Sep 10 15:20 observability
-rw-r--r--@   1 agi_dev  staff  22806 Sep 10 15:20 observability_steering.py
-rw-r--r--@   1 agi_dev  staff   1967 Sep 10 15:20 observatory.py
-rw-r--r--@   1 agi_dev  staff  34493 Sep 10 19:02 oracle_nervous_system.py
drwxr-x---@  37 agi_dev  staff   1184 Sep 10 15:20 orchestration
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 output
-rw-r--r--@   1 agi_dev  staff  24354 Sep 10 15:20 p2p_communication.py
-rw-r--r--@   1 agi_dev  staff   3095 Sep 10 15:20 p2p_fabric.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 performance
drwxr-x---@   8 agi_dev  staff    256 Sep 10 15:20 personality
drwxr-xr-x@   4 agi_dev  staff    128 Sep 10 15:20 planetary_consciousness
-rw-r--r--@   1 agi_dev  staff   2878 Sep 10 15:20 plugin_registry.py
drwxr-xr-x@   5 agi_dev  staff    160 Sep 10 15:20 qi_biometrics
drwxr-xr-x@   5 agi_dev  staff    160 Sep 10 15:20 qi_empathy
drwxr-xr-x@   5 agi_dev  staff    160 Sep 10 15:20 qi_financial
-rw-r--r--@   1 agi_dev  staff    629 Sep 10 15:20 quantized_cycle_manager.py
-rw-r--r--@   1 agi_dev  staff  13691 Sep 10 15:20 quantized_thought_cycles.py
drwxr-xr-x@   4 agi_dev  staff    128 Sep 10 15:20 quantum_biometrics
drwxr-xr-x@   4 agi_dev  staff    128 Sep 10 15:20 quantum_empathy
drwxr-xr-x@   4 agi_dev  staff    128 Sep 10 15:20 quantum_financial
-rw-r--r--@   1 agi_dev  staff    513 Sep 10 15:20 quorum_override.py
drwxr-xr-x@   5 agi_dev  staff    160 Sep 10 15:20 reality_synthesis
drwxr-x---@   7 agi_dev  staff    224 Sep 10 15:20 rem
-rw-r-----@   1 agi_dev  staff   1670 Aug 22 02:29 requirements.txt
-rw-r--r--@   1 agi_dev  staff   1405 Sep 10 15:20 resource_efficiency.py
-rw-r--r--@   1 agi_dev  staff  40513 Sep 10 15:20 resource_efficiency_analyzer.py
-rw-r--r--@   1 agi_dev  staff  26039 Sep 10 15:20 resource_optimization_integration.py
-rw-r--r--@   1 agi_dev  staff   1055 Sep 10 15:20 resource_scheduler.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 router
drwxr-x---@   7 agi_dev  staff    224 Sep 10 15:20 safety
drwxr-x---@  15 agi_dev  staff    480 Sep 10 15:20 security
drwxr-x---@   6 agi_dev  staff    192 Sep 10 15:20 services
-rw-r--r--@   1 agi_dev  staff   2675 Sep 10 15:20 settings.py
-rw-r--r--@   1 agi_dev  staff    899 Sep 10 15:20 specialized_colonies.py
drwxr-x---@   6 agi_dev  staff    192 Sep 10 15:20 spine
-rw-r--r--@   1 agi_dev  staff   2712 Sep 10 15:20 state_management.py
-rw-r--r--@   1 agi_dev  staff  20301 Sep 10 19:02 supervision.py
-rw-r--r--@   1 agi_dev  staff  12248 Sep 10 19:02 swarm.py
-rw-r--r--@   1 agi_dev  staff   2686 Sep 10 15:20 swarm_visualizer.py
drwxr-x---@  74 agi_dev  staff   2368 Sep 10 16:09 symbolic
-rw-r--r--@   1 agi_dev  staff   2297 Sep 10 15:20 symbolic_arbitration.py
drwxr-x---@   5 agi_dev  staff    160 Sep 10 15:20 symbolic_bridge
drwxr-xr-x@  19 agi_dev  staff    608 Sep 10 15:20 symbolic_core
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 symbolic_diagnostics
drwxr-x---@  19 agi_dev  staff    608 Sep 10 15:20 symbolic_legacy
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 symbolic_reasoning
drwxr-x---@   6 agi_dev  staff    192 Sep 10 15:20 symbolism
-rw-r--r--@   1 agi_dev  staff  14098 Sep 10 15:20 system_init.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 tagging
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 tags
-rw-r--r--@   1 agi_dev  staff  10512 Sep 10 15:20 targeted_api_fixes.py
-rw-r--r--@   1 agi_dev  staff  15810 Sep 10 15:20 task_manager.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 telemetry
-rw-r--r--@   1 agi_dev  staff  10043 Sep 10 15:20 telemetry.py
-rw-r--r--@   1 agi_dev  staff  25740 Sep 10 13:52 tier_aware_colony_proxy.py
-rw-r--r--@   1 agi_dev  staff  14826 Sep 10 15:20 tier_unification_adapter.py
drwxr-x---@   6 agi_dev  staff    192 Sep 10 15:20 unified
drwxr-x---@   5 agi_dev  staff    160 Sep 10 15:20 user_interface_manager
drwxr-x---@  10 agi_dev  staff    320 Sep 10 15:20 utils
-rw-r--r--@   1 agi_dev  staff   6251 Sep 10 15:20 validation_script_fixes.py
drwxr-x---@   4 agi_dev  staff    128 Sep 10 15:20 verifold
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 134 files, 180 dependencies.
-------------------------------------


Contracts: 0 kept, 0 broken.
agi_dev@g Lukhas % .venv/bin/lint-imports --help
Usage: lint-imports [OPTIONS]

  Check that a project adheres to a set of contracts.

Options:
  --config TEXT     The config file to use.
  --contract TEXT   Limit the check to the supplied contract identifier. May
                    be passed multiple times.
  --cache-dir TEXT  The directory to use for caching.
  --no-cache        Disable caching.
  --debug           Run in debug mode.
  --show-timings    Show times taken to build the graph and to check each
                    contract.
  --verbose         Noisily output progress as we go along.
  --help            Show this message and exit.
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports --debug --verbose
=============
Import Linter
=============

Verbose mode.
Building import graph (cache directory is .import_linter_cache)...
Used cache meta file .import_linter_cache/lukhas.meta.json.
Used cache data file .import_linter_cache/d81b79999ed617163375e03528da3b15227e8393.data.json.
Wrote data cache file .import_linter_cache/d81b79999ed617163375e03528da3b15227e8393.data.json.
Wrote meta cache file .import_linter_cache/lukhas.meta.json.
Built graph in 0.005s.

---------
Contracts
---------

Analyzed 134 files, 180 dependencies.
-------------------------------------


Contracts: 0 kept, 0 broken.
agi_dev@g Lukhas % rm -rf .import_linter_cache
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports --debug --verbose
=============
Import Linter
=============

Verbose mode.
Building import graph (cache directory is .import_linter_cache)...
No cache file: .import_linter_cache/lukhas.meta.json.
No cache file: .import_linter_cache/d81b79999ed617163375e03528da3b15227e8393.data.json.
Wrote data cache file .import_linter_cache/d81b79999ed617163375e03528da3b15227e8393.data.json.
Wrote meta cache file .import_linter_cache/lukhas.meta.json.
Built graph in 0.011s.
Checking Test simple forbidden import...
Traceback (most recent call last):
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/bin/lint-imports", line 7, in <module>
    sys.exit(lint_imports_command())
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/click/core.py", line 1164, in __call__
    return self.main(*args, **kwargs)
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/click/core.py", line 1085, in main
    rv = self.invoke(ctx)
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/click/core.py", line 1446, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/click/core.py", line 791, in invoke
    return __callback(*args, **kwargs)
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/importlinter/cli.py", line 52, in lint_imports_command
    exit_code = lint_imports(
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/importlinter/cli.py", line 99, in lint_imports
    passed = use_cases.lint_imports(
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/importlinter/application/use_cases.py", line 57, in lint_imports
    raise e
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/importlinter/application/use_cases.py", line 54, in lint_imports
    report = create_report(user_options, limit_to_contracts, cache_dir, show_timings, verbose)
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/importlinter/application/use_cases.py", line 123, in create_report
    return _build_report(
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/importlinter/application/use_cases.py", line 202, in _build_report
    check = contract.check(copy_of_graph, verbose=verbose)
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/importlinter/contracts/forbidden.py", line 74, in check
    self._check_external_forbidden_modules(forbidden_modules)
  File "/Users/agi_dev/LOCAL-REPOS/Lukhas/.venv/lib/python3.9/site-packages/importlinter/contracts/forbidden.py", line 187, in _check_external_forbidden_modules
    raise ValueError(
ValueError: The top level configuration must have include_external_packages=True when there are external forbidden modules.
agi_dev@g Lukhas % rm -rf .import_linter_cache && PYTHONPATH=. .venv/bin/lint-im
ports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 188 files, 730 dependencies.
-------------------------------------

Test simple forbidden import BROKEN

Contracts: 0 kept, 1 broken.


----------------
Broken contracts
----------------

Test simple forbidden import
----------------------------

lukhas.test_import_violation is not allowed to import candidate:

-   lukhas.test_import_violation -> candidate (l.4)


agi_dev@g Lukhas % rm lukhas/test_import_violation.py
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 186 files, 729 dependencies.
-------------------------------------

Production must not import candidate KEPT
Nothing may import quarantine KEPT
Nothing may import archive KEPT

Contracts: 3 kept, 0 broken.
agi_dev@g Lukhas % cd /Users/agi_dev/LOCAL-REPOS/Lukhas && echo "<0001f9ea> Fina
l Import Sanity Check:"
python3 -c "import lukhas, matriz; print('✅ lukhas & matriz importable')"
echo "🔧 Final Import-Linter Check:"
PYTHONPATH=. .venv/bin/lint-imports
echo "🎯 Final Traces Router Test:"
PYTHONPATH=. python3 -c "import matriz.traces_router as t; print('✅ matriz.traces_router accessible')"
🧪 Final Import Sanity Check:
agi_dev@g Lukhas % python3 -c "import lukhas, matriz; print('✅ lukhas & matriz 
importable')"
INFO:lukhas.governance.auth_guardian_integration:Authentication Guardian initialized with drift threshold: 0.15
INFO:lukhas.governance.auth_integration_system:LUKHAS Authentication Integration System initialized: 73efaa58-5cc3-4c24-a6f2-256eb6b28c36
 LUKHAS AI Governance Module loaded: Phase 7 - Registry Updates and Policy Integration
< Constellation Framework: Identity-Consciousness-Guardian
 Phase 7 ID Integration: Available
INFO:identity:✅ Enhanced identity components loaded
INFO:identity:✅ Enhanced identity module loaded: 7/7 components ready
INFO:lukhas.governance.identity:Real identity module already exists - not overriding
INFO:lukhas.governance.identity:Real identity module already loaded - not overriding
INFO:lukhas.governance.identity:Identity namespace bridge initialized successfully
INFO:candidate.governance.identity.import_bridge:Identity import bridge installed
INFO:candidate.governance.identity:Identity namespace bridge initialized successfully
INFO:ΛTRACE.bridge.llm_wrappers:Successfully imported UnifiedOpenAIClient
INFO:ΛTRACE.bridge.llm_wrappers:Successfully imported UnifiedOpenAIClient
INFO:ΛTRACE.bridge.llm_wrappers:OpenAIModulatedService available
/Users/agi_dev/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
✅ Loaded environment from: /Users/agi_dev/LOCAL-REPOS/Lukhas/.env
WARNING:root:Core voice systems not available (cannot import name 'GuardianValidator' from 'candidate.governance.guardian' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/governance/guardian/__init__.py)), using compatibility layer
INFO:auth.service:⚠️ Using fallback mock implementations
INFO:auth.service:Info: Wallet authentication not available
INFO:auth.service:Authentication service initialized with fallback implementations
INFO:lukhas.core.colonies:Imported BaseColony from candidate.core.colonies.base_colony
INFO:lukhas.core.colonies:Successfully imported real implementations from lukhas.core
WARNING:candidate.core.colonies:Could not import MemoryColony: No module named 'lukhas.core.swarm'
/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/colonies/governance_colony.py:19: UserWarning: Could not import lukhas.governance ethics components: No module named 'lukhas.governance.bridge'
  from ethics import EthicsEngine, SafetyChecker
INFO:candidate.core.colonies:Aliased GovernanceColony -> GovernanceColonyEnhanced from .governance_colony
INFO:memory:✅ Core LUKHAS memory system loaded
INFO:memory:✅ Enhanced memory components loaded
INFO:memory:✅ Enhanced memory module loaded: 8/8 components ready
WARNING:candidate.core.colonies:Could not import CreativityColony: No module named 'lukhas.accepted.bio.utils'; 'lukhas.accepted.bio' is not a package
WARNING:candidate.core.colonies:Could not import TensorColonyOps: cannot import name 'TensorColonyOps' from 'candidate.core.colonies.tensor_colony_ops' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/colonies/tensor_colony_ops.py)
INFO:ΛTRACE.ethics_swarm_colony:ΛETHICS: Swarm Colony with simulation and drift correction loaded. Revolutionary ethical intelligence available.
WARNING:candidate.core.colonies:Could not import SymbolicReasoningColony: cannot import name 'SymbolicVocabulary' from 'symbolic.vocabularies' (/Users/agi_dev/LOCAL-REPOS/Lukhas/symbolic/vocabularies/__init__.py)
INFO:candidate.core.colonies:colonies module initialized. Available components: ['BaseColony', 'ColonyConsensus', 'ConsensusMethod', 'ConsensusProposal', 'EnhancedReasoningColony', 'EthicsSwarmColony', 'GovernanceColony', 'GovernanceColonyEnhanced', 'OracleColony', 'ReasoningColony', 'SimAgent', 'SupervisorAgent', 'SwarmNetwork', 'SwarmSignalNetwork', 'TemporalColony', 'VoteType']
WARNING:candidate.core.symbolism:Could not import Archiver: cannot import name 'Archiver' from 'candidate.core.symbolism.archiver' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/symbolism/archiver.py)
INFO:candidate.core.symbolism:symbolism module initialized. Available components: ['MethylationModel']
ℹ️ 2025-09-10 19:26:18  candidate.memory.integrity - INFO - integrity module initialized. Available components: ['CollapseHash']
ℹ️ 2025-09-10 19:26:18  candidate.memory.protection - INFO - protection module initialized. Available components: ['SymbolicQuarantineSanctum']
ℹ️ 2025-09-10 19:26:18  candidate.memory.scaffold - INFO - scaffold module initialized. Available components: ['AtomicMemoryScaffold']
ℹ️ 2025-09-10 19:26:18  candidate.memory.systems - INFO - Memory systems module initialized. Available components: ['CoreMemoryComponent', 'MemoryOrchestrator', 'MemorySystem']
Warning: Memory components not available: No module named 'lukhas_pb2'
WARNING:candidate.memory.fold_system:Failed to import memory fold components: No module named 'hybrid_memory_fold'
ℹ️ 2025-09-10 19:26:18  candidate.memory.core - INFO - core module initialized. Available components: ['ColonyMemoryValidator', 'HybridMemoryFold', 'UnifiedMemoryOrchestrator', 'create_hybrid_memory_fold']
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: Initializing 'core.advanced.brain.awareness' package.
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: Core awareness components imported.
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: 'core.advanced.brain.awareness' package initialized. Exposed symbols in __all__: ['BioSymbolicAwarenessAdapter', 'LucasAwarenessProtocol', 'SymbolicTraceLogger']
INFO:ΛTRACE.consciousness.core_consciousness.awareness_engine:ΛTRACE: Initializing awareness_engine module.
i 2025-09-10 19:26:18  lukhas.governance.security.access_control - INFO - 🛡️ Production Permission Manager initialized
🛡️ Sync Access Control Engine initialized
i 2025-09-10 19:26:18  lukhas.governance.ethics.constitutional_ai - INFO - 🛡️ Production Constitutional AI Framework initialized
i 2025-09-10 19:26:18  lukhas.governance.ethics.constitutional_ai - INFO - 🛡️ Production Safety Monitor initialized
✅ Identity Connector: Using real production implementations
Info: Integration hub not available, using standalone mode
✅ Identity Connector initialized: production implementation
🛡️ Constitutional AI Safety: ACTIVE
⚛️ Tiered Access Control T1-T5: ACTIVE
📋 Full Audit Compliance: ACTIVE
⚠️ Extreme performance optimizations not available - falling back to standard implementation
Warning: Could not initialize identity components: TierValidator() takes no arguments
INFO:candidate.core.module_registry:ModuleRegistry initialized - Tier enforcement: True
INFO:candidate.bio.core:bio core module initialized. Available components: ['BioEngine']
INFO:lukhas.qi:QI module loaded in DRY-RUN mode (set QI_ACTIVE=true to enable)
INFO:lukhas.emotion:✅ LUKHAS emotion system loaded successfully
INFO:lukhas.emotion:✅ Emotion module loaded: 7/7 components ready
✅ lukhas & matriz importable
agi_dev@g Lukhas % echo "🔧 Final Import-Linter Check:"
🔧 Final Import-Linter Check:
agi_dev@g Lukhas % PYTHONPATH=. .venv/bin/lint-imports
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 186 files, 729 dependencies.
-------------------------------------

Production must not import candidate KEPT
Nothing may import quarantine KEPT
Nothing may import archive KEPT

Contracts: 3 kept, 0 broken.
agi_dev@g Lukhas % echo "🎯 Final Traces Router Test:"
🎯 Final Traces Router Test:
agi_dev@g Lukhas % PYTHONPATH=. python3 -c "import matriz.traces_router as t; pr
int('✅ matriz.traces_router accessible')"
✅ matriz.traces_router accessible
agi_dev@g Lukhas % cd /Users/agi_dev/LOCAL-REPOS/Lukhas && PYTHONPATH=. python3 
-c "
cmdand dquote> print('<0001f9ea> Final Import Sanity Check:')
cmdand dquote> import lukhas, matriz
cmdand dquote> print('✅ lukhas & matriz importable')
cmdand dquote> import matriz.traces_router as t
cmdand dquote> print('✅ matriz.traces_router accessible')
cmdand dquote> print('✅ All imports working with PYTHONPATH=.')
cmdand dquote> "
🧪 Final Import Sanity Check:
INFO:lukhas.governance.auth_guardian_integration:Authentication Guardian initialized with drift threshold: 0.15
INFO:lukhas.governance.auth_integration_system:LUKHAS Authentication Integration System initialized: 8f9b728b-a6f0-4b7b-a84d-84591f138fff
 LUKHAS AI Governance Module loaded: Phase 7 - Registry Updates and Policy Integration
< Constellation Framework: Identity-Consciousness-Guardian
 Phase 7 ID Integration: Available
INFO:identity:✅ Enhanced identity components loaded
INFO:identity:✅ Enhanced identity module loaded: 7/7 components ready
INFO:lukhas.governance.identity:Real identity module already exists - not overriding
INFO:lukhas.governance.identity:Real identity module already loaded - not overriding
INFO:lukhas.governance.identity:Identity namespace bridge initialized successfully
INFO:candidate.governance.identity.import_bridge:Identity import bridge installed
INFO:candidate.governance.identity:Identity namespace bridge initialized successfully
INFO:ΛTRACE.bridge.llm_wrappers:Successfully imported UnifiedOpenAIClient
INFO:ΛTRACE.bridge.llm_wrappers:Successfully imported UnifiedOpenAIClient
INFO:ΛTRACE.bridge.llm_wrappers:OpenAIModulatedService available
/Users/agi_dev/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
✅ Loaded environment from: /Users/agi_dev/LOCAL-REPOS/Lukhas/.env
WARNING:root:Core voice systems not available (cannot import name 'GuardianValidator' from 'candidate.governance.guardian' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/governance/guardian/__init__.py)), using compatibility layer
INFO:auth.service:⚠️ Using fallback mock implementations
INFO:auth.service:Info: Wallet authentication not available
INFO:auth.service:Authentication service initialized with fallback implementations
INFO:lukhas.core.colonies:Imported BaseColony from candidate.core.colonies.base_colony
INFO:lukhas.core.colonies:Successfully imported real implementations from lukhas.core
WARNING:candidate.core.colonies:Could not import MemoryColony: No module named 'lukhas.core.swarm'
/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/colonies/governance_colony.py:19: UserWarning: Could not import lukhas.governance ethics components: No module named 'lukhas.governance.bridge'
  from ethics import EthicsEngine, SafetyChecker
INFO:candidate.core.colonies:Aliased GovernanceColony -> GovernanceColonyEnhanced from .governance_colony
INFO:memory:✅ Core LUKHAS memory system loaded
INFO:memory:✅ Enhanced memory components loaded
INFO:memory:✅ Enhanced memory module loaded: 8/8 components ready
WARNING:candidate.core.colonies:Could not import CreativityColony: No module named 'lukhas.accepted.bio.utils'; 'lukhas.accepted.bio' is not a package
WARNING:candidate.core.colonies:Could not import TensorColonyOps: cannot import name 'TensorColonyOps' from 'candidate.core.colonies.tensor_colony_ops' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/colonies/tensor_colony_ops.py)
INFO:ΛTRACE.ethics_swarm_colony:ΛETHICS: Swarm Colony with simulation and drift correction loaded. Revolutionary ethical intelligence available.
WARNING:candidate.core.colonies:Could not import SymbolicReasoningColony: cannot import name 'SymbolicVocabulary' from 'symbolic.vocabularies' (/Users/agi_dev/LOCAL-REPOS/Lukhas/symbolic/vocabularies/__init__.py)
INFO:candidate.core.colonies:colonies module initialized. Available components: ['BaseColony', 'ColonyConsensus', 'ConsensusMethod', 'ConsensusProposal', 'EnhancedReasoningColony', 'EthicsSwarmColony', 'GovernanceColony', 'GovernanceColonyEnhanced', 'OracleColony', 'ReasoningColony', 'SimAgent', 'SupervisorAgent', 'SwarmNetwork', 'SwarmSignalNetwork', 'TemporalColony', 'VoteType']
WARNING:candidate.core.symbolism:Could not import Archiver: cannot import name 'Archiver' from 'candidate.core.symbolism.archiver' (/Users/agi_dev/LOCAL-REPOS/Lukhas/candidate/core/symbolism/archiver.py)
INFO:candidate.core.symbolism:symbolism module initialized. Available components: ['MethylationModel']
ℹ️ 2025-09-10 19:26:22  candidate.memory.integrity - INFO - integrity module initialized. Available components: ['CollapseHash']
ℹ️ 2025-09-10 19:26:22  candidate.memory.protection - INFO - protection module initialized. Available components: ['SymbolicQuarantineSanctum']
ℹ️ 2025-09-10 19:26:22  candidate.memory.scaffold - INFO - scaffold module initialized. Available components: ['AtomicMemoryScaffold']
ℹ️ 2025-09-10 19:26:22  candidate.memory.systems - INFO - Memory systems module initialized. Available components: ['CoreMemoryComponent', 'MemoryOrchestrator', 'MemorySystem']
Warning: Memory components not available: No module named 'lukhas_pb2'
WARNING:candidate.memory.fold_system:Failed to import memory fold components: No module named 'hybrid_memory_fold'
ℹ️ 2025-09-10 19:26:22  candidate.memory.core - INFO - core module initialized. Available components: ['ColonyMemoryValidator', 'HybridMemoryFold', 'UnifiedMemoryOrchestrator', 'create_hybrid_memory_fold']
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: Initializing 'core.advanced.brain.awareness' package.
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: Core awareness components imported.
INFO:ΛTRACE.core.advanced.brain.awareness:ΛTRACE: 'core.advanced.brain.awareness' package initialized. Exposed symbols in __all__: ['BioSymbolicAwarenessAdapter', 'LucasAwarenessProtocol', 'SymbolicTraceLogger']
INFO:ΛTRACE.consciousness.core_consciousness.awareness_engine:ΛTRACE: Initializing awareness_engine module.
i 2025-09-10 19:26:22  lukhas.governance.security.access_control - INFO - 🛡️ Production Permission Manager initialized
🛡️ Sync Access Control Engine initialized
i 2025-09-10 19:26:22  lukhas.governance.ethics.constitutional_ai - INFO - 🛡️ Production Constitutional AI Framework initialized
i 2025-09-10 19:26:22  lukhas.governance.ethics.constitutional_ai - INFO - 🛡️ Production Safety Monitor initialized
✅ Identity Connector: Using real production implementations
Info: Integration hub not available, using standalone mode
✅ Identity Connector initialized: production implementation
🛡️ Constitutional AI Safety: ACTIVE
⚛️ Tiered Access Control T1-T5: ACTIVE
📋 Full Audit Compliance: ACTIVE
⚠️ Extreme performance optimizations not available - falling back to standard implementation
Warning: Could not initialize identity components: TierValidator() takes no arguments
INFO:candidate.core.module_registry:ModuleRegistry initialized - Tier enforcement: True
INFO:candidate.bio.core:bio core module initialized. Available components: ['BioEngine']
INFO:lukhas.qi:QI module loaded in DRY-RUN mode (set QI_ACTIVE=true to enable)
INFO:lukhas.emotion:✅ LUKHAS emotion system loaded successfully
INFO:lukhas.emotion:✅ Emotion module loaded: 7/7 components ready
✅ lukhas & matriz importable
✅ matriz.traces_router accessible
✅ All imports working with PYTHONPATH=.
agi_dev@g Lukhas % echo "🔧 Final Import-Linter Validation:" && PYTHONPATH=. .ve
nv/bin/lint-imports
🔧 Final Import-Linter Validation:
=============
Import Linter
=============

---------
Contracts
---------

Analyzed 186 files, 729 dependencies.
-------------------------------------

Production must not import candidate KEPT
Nothing may import quarantine KEPT
Nothing may import archive KEPT

Contracts: 3 kept, 0 broken.
agi_dev@g Lukhas % 