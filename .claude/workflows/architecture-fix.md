---
status: wip
type: documentation
---
# Constellation Framework Architecture Auto-Fix Workflow

## MATRIZ Pipeline Integration Auto-Fix
When detecting missing MATRIZ pipeline integration:

```python
# BEFORE (detected issue):
class ServiceAdapter:
    def __init__(self):
        pass

# AFTER (Claude Code auto-fix):
class ConstellationAwareServiceAdapter:
    """
    ⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum Constellation Framework service adaptation with MATRIZ pipeline integration
    🧠 Memory-Attention-Thought-Risk-Intent-Action processing
    🎓 Technical: T4/0.01% implementation with registry-based plugins
    """

    def __init__(self, λid: str, constellation_config: ConstellationConfig):
        self.λid = λid
        self.λ_trace = AuditTrace(λid)

        # Constellation Framework integration
        self.anchor_star = AnchorStarCoordinator(λid)  # ⚛️ Identity
        self.trail_star = TrailStarCoordinator(λid)   # ✦ Memory
        self.horizon_star = HorizonStarCoordinator(λid) # 🔬 Vision
        self.watch_star = WatchStarCoordinator(λid)   # 🛡️ Guardian

        # MATRIZ pipeline components
        self.matriz_processor = MatrizPipelineProcessor()
        self.registry_manager = RegistryBasedPluginManager()
        self.constellation_validator = ConstellationFramework()

    @constellation_aware
    async def process_with_matriz_pipeline(self, request: ConstellationRequest):
        """🧠 MATRIZ Memory-Attention-Thought-Risk-Intent-Action processing"""
        await self.λ_trace.start(f'matriz_processing_{request.context_id}')

        # MATRIZ Pipeline Stages
        memory_context = await self.trail_star.process_memory(request)      # M
        attention_focus = await self.horizon_star.process_attention(memory_context)  # A
        thought_analysis = await self.matriz_processor.process_thought(attention_focus)  # T
        risk_assessment = await self.watch_star.process_risk(thought_analysis)       # R
        intent_validation = await self.anchor_star.process_intent(risk_assessment)   # I
        action_execution = await self.matriz_processor.process_action(intent_validation)  # A

        # Constellation validation with T4/0.01% compliance
        if not await self.constellation_validator.validate_t4_compliance(action_execution):
            return self.constellation_error("T4/0.01% compliance validation failed")

        await self.λ_trace.complete(action_execution)
        return action_execution

    @registry_based_plugin
    async def communicate_with_constellation_agent(self, target_agent: str, message: ConstellationMessage):
        """⚛️ Identity · ✦ Memory · 🔬 Vision · 🌱 Bio · 🌙 Dream · ⚖️ Ethics · 🛡️ Guardian · ⚛️ Quantum Constellation-aware inter-agent communication with registry-based routing"""

        # Dynamic plugin registration for target agent
        agent_plugin = await self.registry_manager.get_agent_plugin(target_agent)

        # Constructor-aware instantiation
        communication_adapter = await agent_plugin.create_communication_adapter(
            source_constellation=self.get_constellation_context(),
            cognitive_alignment=True
        )

        # Send with full constellation context
        response = await communication_adapter.send(
            target=target_agent,
            message=message,
            constellation_stars={
                'anchor': self.anchor_star.get_state(),
                'trail': self.trail_star.get_state(),
                'horizon': self.horizon_star.get_state(),
                'watch': self.watch_star.get_state()
            },
            matriz_context=self.matriz_processor.get_context()
        )

        return response
```

## Constellation Framework Auto-Integration
Auto-add Constellation Framework star coordination to classes missing it.
