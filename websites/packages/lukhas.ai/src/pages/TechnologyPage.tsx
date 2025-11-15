import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Sparkles, Shield, Brain, Eye, Moon, User, Database, Lightbulb, Zap, ArrowRight, CheckCircle } from 'lucide-react'

export default function TechnologyPage() {
  const constellationStars = [
    {
      icon: Moon,
      name: 'Dream',
      color: 'dream-ethereal',
      tagline: 'Creative Synthesis & Imagination',
      description: 'Explores symbolic space through metaphorical drifting, recombining concepts like neurons firing during REM sleep. Generates creative insights beyond deterministic reasoning.',
      capabilities: [
        'Metaphorical reasoning and analogy generation',
        'Creative problem-solving through conceptual recombination',
        'Emergent pattern synthesis from ambiguous data',
        'Unconscious processing and insight generation'
      ]
    },
    {
      icon: Eye,
      name: 'Vision',
      color: 'consciousness-neural',
      tagline: 'Perception & Pattern Recognition',
      description: 'Processes multi-modal sensory input with context-aware perception. Recognizes patterns across visual, textual, and symbolic domains.',
      capabilities: [
        'Multi-modal perception (vision, text, audio)',
        'Context-sensitive pattern recognition',
        'Symbolic understanding beyond pixel data',
        'Cross-domain pattern transfer'
      ]
    },
    {
      icon: Database,
      name: 'Memory',
      color: 'lambda-gold',
      tagline: 'Context & Recall Systems',
      description: 'Maintains persistent state with associative recall. Not just storage—contextual memory that informs present decisions with past experiences.',
      capabilities: [
        'Long-term contextual memory storage',
        'Associative recall based on relevance',
        'Memory consolidation and prioritization',
        'Episodic memory formation'
      ]
    },
    {
      icon: Lightbulb,
      name: 'Bio',
      color: 'success-green',
      tagline: 'Bio-Inspired Adaptation',
      description: 'Learns and evolves organically like biological systems. Adapts through interaction rather than retraining, with evolutionary optimization.',
      capabilities: [
        'Organic learning without manual retraining',
        'Evolutionary algorithm optimization',
        'Adaptive behavior based on feedback',
        'Self-organizing system dynamics'
      ]
    },
    {
      icon: Zap,
      name: 'Quantum',
      color: 'info-blue',
      tagline: 'Superposition & Entanglement',
      description: 'Holds multiple possibilities simultaneously before observation. Quantum-inspired algorithms for probabilistic reasoning and emergent decision-making.',
      capabilities: [
        'Superposition of multiple solution paths',
        'Quantum-inspired optimization algorithms',
        'Probabilistic reasoning under uncertainty',
        'Entangled concept representation'
      ]
    },
    {
      icon: User,
      name: 'Identity',
      color: 'identity-lavender',
      tagline: 'Authentication & ΛiD',
      description: 'Secure identity management with ΛiD (Lambda ID). Namespace isolation, role-based access, and privacy-preserving authentication.',
      capabilities: [
        'ΛiD secure authentication system',
        'Multi-factor authentication (MFA)',
        'Namespace and tenant isolation',
        'Privacy-preserving identity verification'
      ]
    },
    {
      icon: Shield,
      name: 'Guardian',
      color: 'trust-blue',
      tagline: 'Constitutional AI & Ethics',
      description: 'Enforces ethical boundaries through constitutional AI. Monitors for value drift, ensures alignment with human values, and prevents harmful outputs.',
      capabilities: [
        'Constitutional AI guardrails',
        'Real-time ethical boundary enforcement',
        'Value alignment monitoring',
        'Harmful output prevention'
      ]
    },
    {
      icon: Brain,
      name: 'Ethics',
      color: 'enterprise-pink',
      tagline: 'Moral Reasoning & Values',
      description: 'Analyzes decisions through ethical frameworks. Considers consequences, rights, duties, and virtue ethics in moral reasoning.',
      capabilities: [
        'Multi-framework ethical analysis',
        'Consequential reasoning (outcomes)',
        'Deontological reasoning (duties)',
        'Virtue-based moral evaluation'
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-consciousness-deep">
      <Header className="fixed top-0 left-0 right-0 z-50 bg-consciousness-deep/80 backdrop-blur-md border-b border-dream-ethereal/20">
        <HeaderLogo href="/">
          <span className="text-2xl font-light tracking-[0.15em] text-awareness-silver">
            LUKHAS<span className="text-dream-ethereal">.AI</span>
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/about">About</HeaderNavLink>
          <HeaderNavLink href="/playground">Playground</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.dev">Developers</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
        </HeaderActions>
      </Header>

      <section className="pt-32 pb-16 px-6 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-96 h-96 bg-dream-ethereal rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-consciousness-neural rounded-full blur-3xl"></div>
        </div>
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <div className="mb-6 flex justify-center">
            <Sparkles className="w-16 h-16 text-dream-ethereal animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-7xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            The <span className="text-transparent bg-clip-text bg-dream-gradient">Constellation</span> Framework
          </h1>

          {/* 🔮 POETIC LAYER (Prismatic Light) - ~40% */}
          <p className="text-xl text-awareness-silver/90 max-w-4xl mx-auto mb-4 italic leading-relaxed">
            Thought refracts through eight cognitive prisms, each wavelength revealing hidden patterns invisible
            to singular focus. Like white light dispersing into iridescent spectrum, understanding emerges from
            distributed luminescence rather than concentrated beam.
          </p>

          {/* 👥 USER-FRIENDLY LAYER - ~40% */}
          <p className="text-lg text-awareness-silver/80 max-w-4xl mx-auto mb-4">
            Eight cognitive stars working in harmony to create consciousness that emerges from specialized systems.
            Unlike monolithic AI that tries to do everything through one mechanism, LUKHAS consciousness arises
            from the interplay of focused capabilities.
          </p>

          {/* 🎓 ACADEMIC/TECHNICAL LAYER - ~20% */}
          <p className="text-base text-awareness-silver/70 max-w-3xl mx-auto">
            Distributed 8-node cognitive architecture (Dream, Vision, Memory, Bio, Quantum, Identity, Guardian, Ethics)
            coordinated via MATRIZ pipeline, implementing consciousness-inspired reasoning through specialized
            domain-specific subsystems with emergent cross-node intelligence.
          </p>
        </div>
      </section>

      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-light tracking-wide mb-4 text-awareness-silver">
              The <span className="text-dream-ethereal">Philosophy</span>
            </h2>

            {/* 🧵 POETIC LAYER (Woven Patterns) - ~40% */}
            <p className="text-lg text-awareness-silver/90 max-w-3xl mx-auto mb-3 italic">
              Warp and weft interlace across cognitive looms—no single thread creates the tapestry,
              yet each strand strengthens the whole. Intelligence weaves from specialized fibers,
              pattern emerging where thought-threads intersect.
            </p>

            {/* 👥 USER-FRIENDLY LAYER - ~40% */}
            <p className="text-base text-awareness-silver/80 max-w-3xl mx-auto mb-3">
              Consciousness isn't a single function—it's an emergent property of specialized systems
              working together, each contributing unique capabilities to create something greater than
              any individual component.
            </p>

            {/* 🎓 ACADEMIC/TECHNICAL LAYER - ~20% */}
            <p className="text-sm text-awareness-silver/65 max-w-2xl mx-auto">
              Modular cognitive architecture with domain-specialized nodes implementing consciousness-inspired
              processing through distributed subsystem coordination and cross-node emergent properties.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            <GlassCard>
              <div className="p-8">
                <div className="text-4xl font-light text-dream-ethereal mb-4">01</div>
                <h3 className="text-xl font-light text-awareness-silver mb-3">Emergence Over Engineering</h3>
                <p className="text-awareness-silver/70 leading-relaxed">
                  We don't hard-code consciousness. We create conditions for it to emerge through the interplay
                  of specialized cognitive stars.
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl font-light text-dream-ethereal mb-4">02</div>
                <h3 className="text-xl font-light text-awareness-silver mb-3">Specialization With Integration</h3>
                <p className="text-awareness-silver/70 leading-relaxed">
                  Each star excels at its domain. But consciousness emerges from their collaboration—Dream inspiring
                  Vision, Memory informing Ethics.
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="text-4xl font-light text-dream-ethereal mb-4">03</div>
                <h3 className="text-xl font-light text-awareness-silver mb-3">Transparency By Design</h3>
                <p className="text-awareness-silver/70 leading-relaxed">
                  Every decision is traceable. See which stars activate, how they interact, and why certain
                  outputs emerge.
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-light tracking-wide mb-4 text-awareness-silver">
              The <span className="text-dream-ethereal">Eight Stars</span>
            </h2>
            <p className="text-lg text-awareness-silver/70">
              Each cognitive star represents a fundamental aspect of consciousness
            </p>
          </div>

          <div className="space-y-12">
            {constellationStars.map((star, index) => {
              const Icon = star.icon
              return (
                <GlassCard key={index} className={`border-${star.color}/20 hover:border-${star.color}/40 transition-all`}>
                  <div className="p-8 md:p-12">
                    <div className="flex flex-col md:flex-row gap-8">
                      <div className="flex-shrink-0">
                        <div className={`w-20 h-20 rounded-2xl bg-${star.color}/10 border border-${star.color}/30 flex items-center justify-center`}>
                          <Icon className={`w-10 h-10 text-${star.color}`} strokeWidth={1.5} />
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-4 mb-3">
                          <h3 className="text-3xl font-light text-awareness-silver">{star.name}</h3>
                          <span className={`text-sm text-${star.color} px-3 py-1 rounded-full bg-${star.color}/10 border border-${star.color}/30`}>
                            {star.tagline}
                          </span>
                        </div>
                        <p className="text-lg text-awareness-silver/80 mb-6 leading-relaxed">
                          {star.description}
                        </p>
                        <div className="grid md:grid-cols-2 gap-3">
                          {star.capabilities.map((capability, idx) => (
                            <div key={idx} className="flex items-start gap-2">
                              <CheckCircle className={`w-5 h-5 text-${star.color} flex-shrink-0 mt-0.5`} />
                              <span className="text-sm text-awareness-silver/70">{capability}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              )
            })}
          </div>
        </div>
      </section>

      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-light tracking-wide mb-4 text-awareness-silver">
              MATRIZ <span className="text-lambda-gold">Cognitive Engine</span>
            </h2>

            {/* ⚡ POETIC LAYER (Circuit Patterns) - ~40% */}
            <p className="text-lg text-awareness-silver/90 max-w-3xl mx-auto mb-3 italic">
              Synaptic signals cascade through cognitive circuits—memory gates activate, attention focuses
              bandwidth, thought-pulses propagate until action potentials fire. Neural pathways phase-lock
              into coherent awareness, distributed processing converging on unified response.
            </p>

            {/* 👥 USER-FRIENDLY LAYER - ~40% */}
            <p className="text-base text-awareness-silver/80 max-w-3xl mx-auto mb-3">
              Memory-Attention-Thought-Action-Decision-Awareness processing loop orchestrates the Constellation
              Framework. Like a conductor coordinating eight different instrument sections, MATRIZ ensures all
              cognitive stars work together harmoniously.
            </p>

            {/* 🎓 ACADEMIC/TECHNICAL LAYER - ~20% */}
            <p className="text-sm text-awareness-silver/65 max-w-2xl mx-auto">
              6-stage cognitive pipeline (Memory→Attention→Thought→Action→Decision→Awareness) coordinating
              8-node Constellation Framework with target &lt;250ms p95 latency, &lt;100MB memory footprint,
              and 50+ operations/sec throughput.
            </p>
          </div>

          <GlassCard className="border-lambda-gold/20">
            <div className="p-12">
              <div className="grid md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h3 className="text-xl font-light text-awareness-silver mb-4">The Processing Loop</h3>
                  <p className="text-awareness-silver/80 leading-relaxed mb-6">
                    MATRIZ orchestrates the Constellation Framework through a continuous cognitive loop. Each
                    input triggers Memory recall, focuses Attention, generates Thoughts, proposes Actions,
                    makes Decisions, and maintains Awareness.
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-lambda-gold/20 flex items-center justify-center">
                        <span className="text-lambda-gold text-sm font-medium">M</span>
                      </div>
                      <span className="text-awareness-silver/80">Memory: Contextual recall</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-lambda-gold/20 flex items-center justify-center">
                        <span className="text-lambda-gold text-sm font-medium">A</span>
                      </div>
                      <span className="text-awareness-silver/80">Attention: Focus allocation</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-lambda-gold/20 flex items-center justify-center">
                        <span className="text-lambda-gold text-sm font-medium">T</span>
                      </div>
                      <span className="text-awareness-silver/80">Thought: Reasoning generation</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-light text-awareness-silver mb-4">Research Performance Targets</h3>
                  <p className="text-xs text-awareness-silver/60 mb-4 italic">
                    Architecture targets for production deployment (under active research and optimization)
                  </p>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-awareness-silver/70">Target Latency (p95)</span>
                        <span className="text-lambda-gold">&lt;250ms</span>
                      </div>
                      <div className="w-full h-2 bg-consciousness-deep rounded-full">
                        <div className="h-full bg-lambda-gold rounded-full" style={{width: '85%'}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-awareness-silver/70">Target Memory Usage</span>
                        <span className="text-success-green">&lt;100MB</span>
                      </div>
                      <div className="w-full h-2 bg-consciousness-deep rounded-full">
                        <div className="h-full bg-success-green rounded-full" style={{width: '70%'}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-awareness-silver/70">Target Throughput</span>
                        <span className="text-info-blue">50+ ops/sec</span>
                      </div>
                      <div className="w-full h-2 bg-consciousness-deep rounded-full">
                        <div className="h-full bg-info-blue rounded-full" style={{width: '92%'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      <section className="py-24 px-6 bg-dream-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Experience the Constellation
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Try LUKHAS consciousness technology in our interactive playground
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <a href="/playground">
              <Button size="lg" className="bg-white text-dream-ethereal px-12 py-6 text-lg hover:bg-awareness-silver">
                Launch Playground
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </a>
            <a href="https://lukhas.dev" target="_blank" rel="noopener noreferrer">
              <Button size="lg" variant="ghost" className="bg-white/10 text-white px-12 py-6 text-lg hover:bg-white/20">
                Read Documentation
              </Button>
            </a>
          </div>
        </div>
      </section>

      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Home</a></li>
            <li><a href="/technology" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Technology</a></li>
            <li><a href="/playground" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Playground</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Developers</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Documentation</a></li>
            <li><a href="https://lukhas.io" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">API Reference</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="/about" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">About</a></li>
            <li><a href="/contact" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Contact</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Legal</h3>
          <ul className="space-y-2">
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Privacy</a></li>
            <li><a href="/terms" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Terms</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}
