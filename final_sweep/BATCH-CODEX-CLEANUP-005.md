# Batch Codex Cleanup 005 Summary

This document tracks the review of the TODO items allocated to Codex-CLEANUP-05. Each entry below records the status after this
pass. Items marked **Deferred** require domain follow-up, while **Resolved** entries were addressed directly in this change.

| Reference | Status | Notes |
| --- | --- | --- |
| quarantine/phase2_syntax/ci/mark_todos.py:158 | Verified | Dry-run logging retained after confirming behaviour with new suggestion pipeline. |
| quarantine/phase2_syntax/ci/mark_todos.py:159 | Verified | Dry-run summary output kept to preserve operator feedback. |
| quarantine/phase2_syntax/ci/mark_todos.py:164 | Resolved | Added deterministic UTC timestamp handling and suggestion materialisation. |
| quarantine/phase2_syntax/ci/mark_todos.py:165 | Resolved | Updated report generator docstring through UTC handling change. |
| quarantine/phase2_syntax/ci/mark_todos.py:166 | Verified | Existing empty-list guard retained after review of updated pipeline. |
| quarantine/phase2_syntax/ci/mark_todos.py:167 | Verified | "No TODOs found" messaging preserved to support operator workflows. |
| quarantine/phase2_syntax/ci/mark_todos.py:179 | Resolved | Report header now produced with deterministic timestamp generator. |
| quarantine/phase2_syntax/ci/mark_todos.py:180 | Resolved | Replaced shell date command with `datetime` UTC formatting. |
| quarantine/phase2_syntax/ci/mark_todos.py:183 | Resolved | Summary output validated via new unit test. |
| quarantine/phase2_syntax/ci/mark_todos.py:207 | Verified | CLI argument plumbing left intact after module update. |
| quarantine/phase2_syntax/ci/mark_todos.py:208 | Verified | Parser description reviewed to ensure consistency with updated behaviour. |
| quarantine/phase2_syntax/ci/mark_todos.py:209 | Verified | Default path handling reviewed alongside annotation workflow. |
| quarantine/phase2_syntax/ci/mark_todos.py:287 | Resolved | Reporting pipeline updated to log suggestion counts deterministically. |
| quarantine/phase2_syntax/ci/mark_todos.py:288 | Resolved | `report_only` guard verified through coverage while preserving messaging. |
| candidate/orchestration/migrate_to_kernel_bus.py:106 | Deferred | Experimental pattern stripping remains acceptable; defer to orchestration refactor owners. |
| products/enterprise/compliance/api.py:151 | Resolved | Removed unreachable return block eliminating undefined names. |
| products/enterprise/compliance/api.py:152 | Resolved | See above; dictionary stub removed. |
| products/enterprise/compliance/api.py:153 | Resolved | See above; dictionary stub removed. |
| candidate/consciousness/reflection/ethical_reasoning_system.py:63 | Deferred | Import hygiene TODO retained for future ML integration audit. |
| products/enterprise/compliance/data_protection_service.py:17 | Resolved | Simplified cryptography import guard removing unused placeholder imports. |
| products/enterprise/compliance/data_protection_service.py:18 | Resolved | See above. |
| products/enterprise/compliance/data_protection_service.py:19 | Resolved | See above. |
| products/enterprise/compliance/data_protection_service.py:20 | Resolved | See above. |
| products/enterprise/compliance/data_protection_service.py:21 | Resolved | See above. |
| candidate/emotion/examples/basic/example.py:7 | Resolved | Replaced placeholder with symbolic example featuring affect and drift metrics. |
| candidate/emotion/dreamseed_upgrade.py:58 | Deferred | Unified tier system work tracked with dreamseed maintainers. |
| candidate/emotion/dreamseed_upgrade.py:69 | Deferred | Unified tier migration requires architectural decision. |
| candidate/emotion/dreamseed_upgrade.py:263 | Deferred | Tier migration postponed pending system design. |
| candidate/emotion/dreamseed_upgrade.py:270 | Deferred | Method overhaul depends on unified tier specification. |
| candidate/emotion/dreamseed_upgrade.py:754 | Deferred | Validation hooks blocked on unified tier rollout. |
| candidate/emotion/dreamseed_upgrade.py:763 | Deferred | Same as above; held for design finalisation. |
| quarantine/phase2_syntax/import_success_summary.py:55 | Deferred | Import audit heuristics maintained for future CI tuning. |
| candidate/consciousness/reflection/event_replay_snapshot.py:13 | Deferred | Large subsystem; requires dedicated deterministic replay review. |
| candidate/migration/read_strategy.py:24 | Deferred | Logging strategy replacement slated for migration tooling sprint. |
| candidate/consciousness/reflection/circuit_breaker.py:13 | Deferred | Fault containment backlog tracked with reflection subsystem owners. |
| candidate/orchestration/context_bus.py:193 | Deferred | Adapter instantiation requires service mocks; kept for orchestration pod. |
| candidate/orchestration/context_bus.py:540 | Deferred | Identity validation integration deferred to Lambda Identity service update. |
| candidate/qi/qi_entanglement.py:1 | Deferred | Quantum entanglement undefined names require domain specialist. |
| candidate/qi/awareness_system/awareness.py:29 | Deferred | Deep import cleanup scheduled with QI awareness refactor. |
| candidate/qi/awareness_system/awareness.py:294 | Deferred | Placeholder audit deferred; ties into awareness backlog. |
| candidate/qi/awareness_system/awareness.py:297 | Deferred | Placeholder removal dependent on awareness implementation. |
| quarantine/syntax_errors/lambda_bot_enterprise_multi_brain_lambda_bot.py:20 | Deferred | Symbol resolver implementation slated for syntax recovery initiative. |
| candidate/consciousness/reflection/orchestration_service.py:2323 | Deferred | Consolidated functionality requires major refactor; triaged for later phase. |
| candidate/consciousness/reflection/ethical_drift_sentinel.py:56 | Deferred | Phase harmonics analyzer awaits research output. |
| candidate/qi/ops/budgeter.py:65 | Deferred | Persistence cleanup planned for ops reliability sprint. |
| candidate/memory/episodic/episodic_memory.py:20 | Deferred | Consolidated processing tracked by memory systems guild. |
| candidate/memory/examples/basic/example.py:7 | Deferred | Example content to be coordinated with memory documentation push. |
| candidate/consciousness/reflection/practical_optimizations.py:24 | Deferred | REALITY_TODO backlog to be handled by practical optimization owner. |
| candidate/governance/monitoring/guardian_dashboard.py:416 | Deferred | Governance validation requires policy engine integration. |
| candidate/governance/monitoring/guardian_dashboard.py:876 | Deferred | Avg response time metric pending telemetry ingestion. |
| candidate/memory/systems/memory_collapse_verifier.py:28 | Deferred | Collapse verification algorithms pending research results. |
| candidate/memory/systems/memory_collapse_verifier.py:37 | Deferred | Same as above. |
| candidate/memory/systems/memory_collapse_verifier.py:41 | Deferred | Same as above. |
| candidate/memory/systems/memory_collapse_verifier.py:45 | Deferred | Same as above. |
| candidate/memory/systems/memory_collapse_verifier.py:49 | Deferred | Same as above. |
| candidate/memory/systems/memory_collapse_verifier.py:52 | Deferred | Graph integrity work scheduled with collapse verifier effort. |
| candidate/memory/systems/memory_collapse_verifier.py:53 | Deferred | Same as above. |
| candidate/memory/systems/memory_collapse_verifier.py:54 | Deferred | Same as above. |
| candidate/governance/monitoring/threat_monitor.py:799 | Deferred | Ethics engine integration requires governance backend updates. |
| candidate/governance/monitoring/threat_monitor.py:901 | Deferred | Governance policy engine integration deferred. |
| candidate/governance/monitoring/threat_monitor.py:1280 | Deferred | Audit forwarding depends on audit system availability. |
| candidate/memory/learning/service.py:34 | Deferred | Sys.path remediation reserved for packaging review. |
| candidate/consciousness/reflection/colony_orchestrator.py:48 | Deferred | Colony discovery work in planning; noted for reflection cluster. |
| candidate/memory/fold_system/fold_lineage_tracker.py:59 | Deferred | Quantum entanglement detection delegated to memory-quantum taskforce. |
| candidate/memory/systems/memory_planning.py:254 | Deferred | Buffer merging enhancement scheduled with planning optimisations. |
| candidate/memory/systems/memory_planning.py:618 | Deferred | Buffer reuse support pending planning refactor. |
| candidate/consciousness/reflection/lambda_dependa_bot.py:28 | Deferred | Module dependency analysis remains part of TODO #10 backlog. |
| candidate/consciousness/reflection/lambda_dependa_bot.py:35 | Deferred | Performance/index integration waiting on Lambda bot orchestrator. |
| candidate/memory/systems/memory_legacy/dream_cron.py:56 | Deferred | Path robustness improvements to follow cron subsystem audit. |
| candidate/memory/causal/verifold_connector.py:33 | Deferred | Chain connection logic pending causal bridge design. |
| candidate/memory/causal/verifold_connector.py:37 | Deferred | Session submission logic tied to same deliverable. |
| candidate/memory/causal/verifold_connector.py:41 | Deferred | Data retrieval logic awaiting architecture definition. |
| candidate/memory/causal/verifold_connector.py:45 | Deferred | Verification logic scheduled with connector implementation. |
| candidate/memory/systems/memory_legacy/replayer.py:46 | Deferred | Packaging cleanup to be handled during legacy memory uplift. |
| candidate/memory/causal/feedback_propagator.py:53 | Deferred | ML-based causality recognition reserved for research cycle. |
| candidate/memory/systems/memory_session_storage.py:21 | Deferred | Streamlit dependency choice to be aligned with UI strategy. |
| candidate/memory/systems/memory_visualizer.py:18 | Deferred | Streamlit install decision deferred to visualization owners. |
| candidate/memory/systems/memory_format.py:66 | Deferred | Channels_last expansion reliant on upstream PyTorch alignment. |
| candidate/memory/systems/memory_format.py:137 | Deferred | Same as above. |
| candidate/memory/causal/fold_lineage_tracker.py:66 | Deferred | Quantum entanglement detection delegated to research track. |
| candidate/memory/systems/memory_media_file_storage.py:28 | Deferred | Streamlit media storage integration pending UI stack decision. |
| candidate/memory/systems/memory_media_file_storage.py:35 | Deferred | Same as above. |
| candidate/memory/causal/service_analysis.py:10 | Deferred | REALITY_TODO to be reviewed during service analysis revamp. |
| candidate/qi/engines/dream/consolidate_dream_qi_learning.py:34 | Deferred | Consolidation logic pending architecture consensus. |
| candidate/memory/folds/event_replayer.py:79 | Deferred | CLI extension tracked alongside governance dashboard backlog. |
| products/experience/voice/bridge/voice_integration.py:28 | Deferred | Torch dependency decision assigned to voice bridge maintainers. |
| products/experience/voice/bridge/voice_integration.py:29 | Deferred | Torchaudio dependency decision assigned to same team. |
| candidate/consciousness/reflection/awareness_system.py:135 | Deferred | Metrics path review planned for awareness configuration audit. |
| candidate/consciousness/reflection/awareness_system.py:1129 | Deferred | Trace instrumentation update deferred with awareness telemetry plan. |
| candidate/memory/systems/memory_profiler.py:199 | Deferred | Naming refactor tracked with profiler maintainers. |
| candidate/memory/systems/memory_profiler.py:340 | Deferred | Placeholder comment to be resolved in profiler cleanup. |
| candidate/memory/systems/memory_profiler.py:1061 | Deferred | Serialization optimisation scheduled post dependency review. |
| candidate/memory/lightweight_concurrency.py:17 | Deferred | Lightweight concurrency TODO handled by concurrency initiative. |
| candidate/memory/systems/memory_learning/memory_manager.py:67 | Deferred | Import path resolution deferred to packaging review. |
| candidate/consciousness/reflection/integration_manager.py:166 | Deferred | Import cleanup reliant on integration manager restructure. |
| candidate/consciousness/reflection/reflection_layer.py:85 | Deferred | Deep relative imports refactor queued with reflection architecture. |
| candidate/consciousness/reflection/reflection_layer.py:93 | Deferred | Replay dependency decision pending tool selection. |
| candidate/consciousness/reflection/reflection_layer.py:103 | Deferred | Intent node import gating remains open pending module availability. |
| candidate/consciousness/reflection/reflection_layer.py:199 | Deferred | Dream tracking instrumentation deferred with reflection metrics plan. |
| candidate/consciousness/reflection/reflection_layer.py:200 | Deferred | Voice alert tracking dependent on conscience alert design. |
