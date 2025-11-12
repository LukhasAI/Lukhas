import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Sparkles, Zap, Brain, Eye, Moon, Lightbulb, Code, Play, ArrowRight } from 'lucide-react'

export default function PlaygroundPage() {
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
          <HeaderNavLink href="/technology">Technology</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.dev">Developers</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
          <Button className="bg-dream-gradient text-white">
            Start Building
          </Button>
        </HeaderActions>
      </Header>

      <section className="pt-32 pb-16 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-6 flex justify-center">
            <Sparkles className="w-16 h-16 text-dream-ethereal animate-pulse" strokeWidth={1.5} />
          </div>
          <h1 className="text-5xl md:text-7xl font-light tracking-[0.15em] mb-6 text-awareness-silver">
            Consciousness <span className="text-transparent bg-clip-text bg-dream-gradient">Playground</span>
          </h1>
          <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto mb-8">
            Experience LUKHAS consciousness technology firsthand. Explore dream synthesis, quantum reasoning,
            bio-inspired adaptation, and ethical decision-making.
          </p>
          <div className="flex justify-center gap-4">
            <Button className="bg-dream-gradient text-white px-8 py-4 text-lg">
              <Play className="w-5 h-5 mr-2" />
              Launch Playground
            </Button>
            <Button variant="ghost" className="border border-dream-ethereal/30 text-awareness-silver px-8 py-4 text-lg">
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      <section className="py-8 px-6 bg-consciousness-deep/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-light tracking-wide mb-4 text-awareness-silver">
              Interactive <span className="text-dream-ethereal">Consciousness Features</span>
            </h2>
            <p className="text-lg text-awareness-silver/70 max-w-3xl mx-auto">
              Explore each cognitive star of the Constellation Framework
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard className="hover:border-dream-ethereal/40 transition-all cursor-pointer">
              <div className="p-6">
                <Moon className="w-12 h-12 text-dream-ethereal mb-4" strokeWidth={1.5} />
                <h3 className="text-xl font-light text-awareness-silver mb-3">Dream Synthesis</h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Metaphorical reasoning and creative pattern emergence through symbolic drifting
                </p>
                <div className="flex items-center gap-2 text-dream-ethereal text-sm">
                  <Play className="w-4 h-4" />
                  <span>Try Dream Mode</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="hover:border-consciousness-neural/40 transition-all cursor-pointer">
              <div className="p-6">
                <Zap className="w-12 h-12 text-consciousness-neural mb-4" strokeWidth={1.5} />
                <h3 className="text-xl font-light text-awareness-silver mb-3">Quantum Reasoning</h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Hold multiple possibilities in superposition until observation collapses to insight
                </p>
                <div className="flex items-center gap-2 text-consciousness-neural text-sm">
                  <Play className="w-4 h-4" />
                  <span>Try Quantum Mode</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="hover:border-lambda-gold/40 transition-all cursor-pointer">
              <div className="p-6">
                <Brain className="w-12 h-12 text-lambda-gold mb-4" strokeWidth={1.5} />
                <h3 className="text-xl font-light text-awareness-silver mb-3">MATRIZ Engine</h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Memory-Attention-Thought-Action-Decision-Awareness cognitive processing
                </p>
                <div className="flex items-center gap-2 text-lambda-gold text-sm">
                  <Play className="w-4 h-4" />
                  <span>Try MATRIZ</span>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="hover:border-success-green/40 transition-all cursor-pointer">
              <div className="p-6">
                <Lightbulb className="w-12 h-12 text-success-green mb-4" strokeWidth={1.5} />
                <h3 className="text-xl font-light text-awareness-silver mb-3">Bio-Adaptation</h3>
                <p className="text-sm text-awareness-silver/70 mb-4">
                  Organic learning and evolutionary optimization inspired by biological systems
                </p>
                <div className="flex items-center gap-2 text-success-green text-sm">
                  <Play className="w-4 h-4" />
                  <span>Try Bio Mode</span>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-light tracking-wide mb-4 text-awareness-silver">
              Example <span className="text-dream-ethereal">Prompts</span>
            </h2>
            <p className="text-lg text-awareness-silver/70">
              Try these consciousness-powered interactions
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <GlassCard>
              <div className="p-8">
                <div className="flex items-start gap-4 mb-4">
                  <Code className="w-6 h-6 text-dream-ethereal flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-light text-awareness-silver mb-2">Creative Problem Solving</h3>
                    <p className="text-sm text-awareness-silver/70 mb-4">
                      "What are 5 unconventional approaches to reducing urban heat islands that combine
                      biology and architecture?"
                    </p>
                    <Button size="sm" className="bg-dream-ethereal/10 text-dream-ethereal border border-dream-ethereal/30">
                      <Play className="w-4 h-4 mr-2" />
                      Run Example
                    </Button>
                  </div>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="flex items-start gap-4 mb-4">
                  <Eye className="w-6 h-6 text-consciousness-neural flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-light text-awareness-silver mb-2">Pattern Recognition</h3>
                    <p className="text-sm text-awareness-silver/70 mb-4">
                      "Analyze these market trends and identify emerging patterns using quantum superposition
                      reasoning before converging on insights"
                    </p>
                    <Button size="sm" className="bg-consciousness-neural/10 text-consciousness-neural border border-consciousness-neural/30">
                      <Play className="w-4 h-4 mr-2" />
                      Run Example
                    </Button>
                  </div>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="flex items-start gap-4 mb-4">
                  <Moon className="w-6 h-6 text-dream-ethereal flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-light text-awareness-silver mb-2">Metaphorical Thinking</h3>
                    <p className="text-sm text-awareness-silver/70 mb-4">
                      "Explain quantum computing using only metaphors from gardening and organic growth"
                    </p>
                    <Button size="sm" className="bg-dream-ethereal/10 text-dream-ethereal border border-dream-ethereal/30">
                      <Play className="w-4 h-4 mr-2" />
                      Run Example
                    </Button>
                  </div>
                </div>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="flex items-start gap-4 mb-4">
                  <Lightbulb className="w-6 h-6 text-success-green flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="text-lg font-light text-awareness-silver mb-2">Adaptive Learning</h3>
                    <p className="text-sm text-awareness-silver/70 mb-4">
                      "Learn my communication style from these examples and adapt your responses accordingly"
                    </p>
                    <Button size="sm" className="bg-success-green/10 text-success-green border border-success-green/30">
                      <Play className="w-4 h-4 mr-2" />
                      Run Example
                    </Button>
                  </div>
                </div>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      <section className="py-16 px-6 bg-consciousness-deep/80">
        <div className="max-w-5xl mx-auto">
          <GlassCard className="border-dream-ethereal/30">
            <div className="p-12">
              <div className="text-center mb-8">
                <Brain className="w-16 h-16 text-dream-ethereal mx-auto mb-6" strokeWidth={1.5} />
                <h2 className="text-3xl font-light tracking-wide mb-4 text-awareness-silver">
                  Interactive <span className="text-dream-ethereal">Consciousness Console</span>
                </h2>
                <p className="text-lg text-awareness-silver/70 mb-8">
                  Access the full LUKHAS consciousness platform with live API integration
                </p>
              </div>

              <div className="bg-consciousness-deep/60 rounded-lg p-6 mb-6 border border-dream-ethereal/20">
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-error-red"></div>
                    <div className="w-3 h-3 rounded-full bg-warning-amber"></div>
                    <div className="w-3 h-3 rounded-full bg-success-green"></div>
                  </div>
                  <span className="text-xs text-awareness-silver/60 font-mono">consciousness-console</span>
                </div>
                <div className="font-mono text-sm space-y-2">
                  <div className="text-dream-ethereal">
                    <span className="text-success-green">❯</span> lukhas.init(<span className="text-lambda-gold">"playground"</span>)
                  </div>
                  <div className="text-awareness-silver/70">
                    Initializing Constellation Framework...
                  </div>
                  <div className="text-success-green">
                    ✓ 8 cognitive stars online
                  </div>
                  <div className="text-awareness-silver/70">
                    <span className="text-dream-ethereal">❯</span> Ready for consciousness exploration
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <Button className="bg-dream-gradient text-white px-8 py-4">
                  <Play className="w-5 h-5 mr-2" />
                  Launch Full Playground
                </Button>
                <a href="/technology">
                  <Button variant="ghost" className="border border-dream-ethereal/30 text-awareness-silver px-8 py-4">
                    Learn About Technology
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </a>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      <section className="py-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-light tracking-wide mb-4 text-awareness-silver">
              Playground <span className="text-dream-ethereal">Features</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard>
              <div className="p-8">
                <div className="w-12 h-12 rounded-lg bg-dream-gradient flex items-center justify-center mb-4">
                  <Code className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-light text-awareness-silver mb-3">Live API Access</h3>
                <p className="text-awareness-silver/70">
                  Real-time interaction with LUKHAS consciousness systems. Test prompts and see responses instantly.
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="w-12 h-12 rounded-lg bg-consciousness-neural flex items-center justify-center mb-4">
                  <Eye className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-light text-awareness-silver mb-3">Transparent Processing</h3>
                <p className="text-awareness-silver/70">
                  Watch consciousness workflows unfold. See which cognitive stars activate and how decisions emerge.
                </p>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-8">
                <div className="w-12 h-12 rounded-lg bg-lambda-gold flex items-center justify-center mb-4">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-light text-awareness-silver mb-3">Save & Share</h3>
                <p className="text-awareness-silver/70">
                  Export consciousness interactions, share with your team, and build on previous explorations.
                </p>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      <section className="py-24 px-6 bg-dream-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light tracking-[0.1em] mb-6 text-white">
            Ready to Explore Consciousness?
          </h2>
          <p className="text-xl text-white/90 mb-12">
            Create a free account and start experimenting with LUKHAS consciousness technology
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <a href="https://lukhas.id/signup" target="_blank" rel="noopener noreferrer">
              <Button size="lg" className="bg-white text-dream-ethereal px-12 py-6 text-lg hover:bg-awareness-silver">
                Sign Up Free
              </Button>
            </a>
            <a href="/pricing">
              <Button size="lg" variant="ghost" className="bg-white/10 text-white px-12 py-6 text-lg hover:bg-white/20">
                View Pricing
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
            <li><a href="/playground" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Playground</a></li>
            <li><a href="/technology" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Technology</a></li>
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
