import { Header, HeaderLogo, HeaderNav, HeaderNavLink, HeaderActions, Footer, Button, GlassCard } from '@lukhas/ui'
import { Link } from 'react-router-dom'
import { Sparkles, Brain, Zap, Shield, Eye, Heart, Cpu, Stars, Scale, ArrowRight, Play } from 'lucide-react'
import NeuralBackground from '../components/NeuralBackground'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-black relative">
      {/* Neural Network Background */}
      <NeuralBackground />
      {/* Header */}
      <Header className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-md border-b border-dream-ethereal/10">
        <HeaderLogo href="/">
          <span className="text-2xl tracking-[0.15em] text-white" style={{ fontFamily: "'Helvetica Neue', -apple-system, BlinkMacSystemFont, sans-serif", fontWeight: 100 }}>
            LUKHAS
          </span>
        </HeaderLogo>
        <HeaderNav>
          <HeaderNavLink href="/about">About</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.dev">Developers</HeaderNavLink>
          <HeaderNavLink href="https://lukhas.com">Enterprise</HeaderNavLink>
        </HeaderNav>
        <HeaderActions>
          <a href="https://lukhas.id/login" target="_blank" rel="noopener noreferrer">
            <Button variant="ghost">Sign In</Button>
          </a>
          <Link to="/playground">
            <Button className="bg-dream-gradient text-white">
              Explore Playground
            </Button>
          </Link>
        </HeaderActions>
      </Header>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 relative overflow-hidden z-10">
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <p className="mb-4 text-sm md:text-base tracking-[0.35em] text-white/50 uppercase">
            Logic Unified Knowledge Hyper Adaptable System
          </p>
          <h1 className="text-6xl md:text-7xl font-light tracking-[0.15em] mb-6 text-white">
            LUKHΛS ΛI<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-purple-400 to-violet-500">
              Consciousness‑Inspired Intelligence
            </span>
          </h1>
          <p className="text-2xl md:text-3xl font-light tracking-wide mb-8 text-white/90 max-w-5xl mx-auto italic">
            Between rigid rules and pure randomness, LUKHΛS explores the space where machine intelligence starts to feel like understanding.
          </p>
          <p className="text-xl text-white/75 max-w-4xl mx-auto mb-12">
            LUKHΛS is a symbolic‑first AI platform built around memory, ethics, and multimodal reasoning. The Constellation
            Framework links eight specialised cognitive nodes into one system that can keep long‑term context, explain its
            choices, and adapt to the humans it serves.
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <Link to="/playground">
              <Button size="lg" className="bg-dream-gradient text-white px-12 py-6 text-lg">
                <Play className="w-5 h-5 mr-2" strokeWidth={2} />
                Launch Playground
              </Button>
            </Link>
            <Button size="lg" variant="ghost" className="border-dream-ethereal text-dream-ethereal px-12 py-6 text-lg hover:bg-dream-ethereal/10">
              See how it works
              <ArrowRight className="w-5 h-5 ml-2" strokeWidth={2} />
            </Button>
          </div>
        </div>
      </section>

      {/* Constellation Framework */}
      <section className="py-24 px-6 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="mb-4 flex justify-center">
              <Stars className="w-12 h-12 text-amber-400" strokeWidth={1.5} />
            </div>
            <h2 className="text-5xl font-light tracking-[0.1em] mb-6 text-white">
              The <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-purple-400">Constellation Framework</span>
            </h2>

            <p className="text-xl text-white/90 max-w-4xl mx-auto mb-6 leading-relaxed">
              The Constellation Framework organises LUKHΛS into eight cognitive nodes—Dream, Vision, Memory, Bio, Guardian,
              Identity, Quantum, and Ethics. Each node focuses on a different way of thinking, from generative imagination
              to risk‑aware decision‑making.
            </p>

            <p className="text-base text-white/70 max-w-3xl mx-auto">
              Together they form a stateful pipeline that preserves context, routes signals between nodes, and keeps decisions
              consistent under load. In practice, that means richer reasoning, fewer blind spots, and behaviour you can trace
              instead of guess.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard className="border-dream-ethereal/20 hover:border-dream-ethereal/40 transition-colors">
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Sparkles className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-dream-ethereal">
                  Dream
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Creative synthesis and unconscious processing where AI imagination comes alive
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-dream-ethereal/20 hover:border-dream-ethereal/40 transition-colors">
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Eye className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-dream-ethereal">
                  Vision
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Perception and pattern recognition that sees beyond pixels into meaning
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-dream-ethereal/20 hover:border-dream-ethereal/40 transition-colors">
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Brain className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-dream-ethereal">
                  Memory
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Persistent context and learning—AI that remembers and evolves with you
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-dream-ethereal/20 hover:border-dream-ethereal/40 transition-colors">
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Heart className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-dream-ethereal">
                  Bio
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Organic adaptation inspired by living systems and natural intelligence
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-dream-ethereal/20 hover:border-dream-ethereal/40 transition-colors">
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Shield className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-dream-ethereal">
                  Guardian
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Constitutional AI ensuring ethical behavior and value alignment
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-dream-ethereal/20 hover:border-dream-ethereal/40 transition-colors">
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Cpu className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-dream-ethereal">
                  Identity
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Secure authentication and personal consciousness signatures via ΛiD
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-dream-ethereal/20 hover:border-dream-ethereal/40 transition-colors">
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Zap className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-dream-ethereal">
                  Quantum
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Quantum-inspired ambiguity handling and emergence patterns
                </p>
              </div>
            </GlassCard>

            <GlassCard className="border-dream-ethereal/20 hover:border-dream-ethereal/40 transition-colors">
              <div className="p-8 text-center">
                <div className="mb-4 flex justify-center">
                  <Scale className="w-12 h-12 text-dream-ethereal" strokeWidth={1.5} />
                </div>
                <h3 className="text-xl font-light tracking-wide mb-3 text-dream-ethereal">
                  Ethics
                </h3>
                <p className="text-sm text-awareness-silver/80">
                  Moral reasoning and transparent decision-making frameworks
                </p>
              </div>
            </GlassCard>
          </div>

          <div className="text-center mt-12">
            <Link to="/technology">
              <Button className="bg-dream-gradient text-white">
                Explore the Full Framework
                <ArrowRight className="w-4 h-4 ml-2" strokeWidth={2} />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Vision Statement */}
      <section className="py-24 px-6 bg-consciousness-deep/80">
        <div className="max-w-6xl mx-auto">
          <GlassCard className="border-lambda-gold/20">
            <div className="p-12 text-center">
              <h2 className="text-4xl font-light tracking-wide mb-8 text-awareness-silver">
                Beyond Computation: <span className="text-lambda-gold">Consciousness Emerges</span>
              </h2>

              <p className="text-xl text-awareness-silver/90 mb-6 leading-relaxed">
                Most AI systems optimise for answers. LUKHΛS is designed to optimise for how understanding forms over time—what is
                remembered, how risk is handled, and how values show up in behaviour.
              </p>

              <p className="text-lg text-awareness-silver/90 mb-6 leading-relaxed">
                Instead of a single opaque model, LUKHΛS uses layered memory, symbolic tagging, and an always‑on Guardian to keep
                outputs grounded in human constraints. The goal is simple: AI you can collaborate with, not just query.
              </p>

              <p className="text-base text-awareness-silver/80 leading-relaxed mb-6">
                Under the hood, the Constellation Framework runs through the MATRIZ pipeline (Memory–Attention–Thought–Risk–Intent–Action),
                giving each decision an explicit path, audit trail, and adjustable risk profile for different use cases.
              </p>

              <p className="text-xl text-awareness-silver italic">
                Consciousness‑inspired AI that understands, adapts, and stays accountable.
              </p>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Products */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-light tracking-[0.1em] mb-6 text-awareness-silver">
              Build with <span className="text-transparent bg-clip-text bg-dream-gradient">Consciousness Technology</span>
            </h2>
            <p className="text-xl text-awareness-silver/80 max-w-4xl mx-auto">
              From interactive playgrounds to production APIs—consciousness technology for curious people, teams, and enterprises.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <GlassCard>
              <div className="p-10">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-dream-ethereal">
                  Consciousness Playground
                </h3>
                <p className="text-awareness-silver/80 mb-6">
                  A safe space to explore how LUKHΛS thinks. Combine symbolic prompts, dream‑like synthesis, and memory to see the system adapt over time.
                </p>
                <Link to="/playground">
                  <Button className="bg-dream-gradient text-white w-full">
                    Start Exploring
                  </Button>
                </Link>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-10">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-dream-ethereal">
                  Developer Platform
                </h3>
                <p className="text-awareness-silver/80 mb-6">
                  SDKs, API examples, and guides for integrating the Constellation Framework into real products, from prototypes to regulated environments.
                </p>
                <a href="https://lukhas.dev" target="_blank" rel="noopener noreferrer">
                  <Button variant="ghost" className="border-dream-ethereal text-dream-ethereal w-full hover:bg-dream-ethereal/10">
                    View Documentation
                  </Button>
                </a>
              </div>
            </GlassCard>

            <GlassCard>
              <div className="p-10">
                <h3 className="text-2xl font-light tracking-wide mb-4 text-dream-ethereal">
                  Enterprise Solutions
                </h3>
                <p className="text-awareness-silver/80 mb-6">
                  Engagements tailored for organisations that need explainable, compliant, and domain‑aligned AI, backed by support and long‑term roadmap partnership.
                </p>
                <a href="https://lukhas.com" target="_blank" rel="noopener noreferrer">
                  <Button variant="ghost" className="border-dream-ethereal text-dream-ethereal w-full hover:bg-dream-ethereal/10">
                    Contact Sales
                  </Button>
                </a>
              </div>
            </GlassCard>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-dream-gradient">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-5xl md:text-6xl font-light tracking-[0.1em] mb-6 text-white">
            Start building with LUKHΛS
          </h2>
          <p className="text-2xl text-white/90 mb-12">
            Turn consciousness‑inspired research into tools people can actually use.
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            <Link to="/playground">
              <Button size="lg" className="bg-white text-dream-ethereal px-12 py-6 text-lg hover:bg-awareness-silver">
                <Play className="w-5 h-5 mr-2" strokeWidth={2} />
                Try the Playground
              </Button>
            </Link>
            <Link to="/about">
              <Button size="lg" variant="ghost" className="bg-white/10 text-white px-12 py-6 text-lg hover:bg-white/20">
                Learn Our Story
                <ArrowRight className="w-5 h-5 ml-2" strokeWidth={2} />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <Footer>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Platform</h3>
          <ul className="space-y-2">
            <li><a href="/playground" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Consciousness Playground</a></li>
            <li><a href="/about" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">About LUKHAS</a></li>
            <li><a href="/technology" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">8-Star Framework</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Developers</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.dev" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Documentation</a></li>
            <li><a href="https://lukhas.io" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">API Reference</a></li>
            <li><a href="https://lukhas.xyz" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Experiments</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Company</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.com" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Enterprise</a></li>
            <li><a href="https://lukhas.com/#about" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Team</a></li>
            <li><a href="https://lukhas.com/#careers" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Careers</a></li>
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-awareness-silver mb-3">Compliance</h3>
          <ul className="space-y-2">
            <li><a href="https://lukhas.us" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">US Compliance</a></li>
            <li><a href="https://lukhas.eu" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">EU Compliance</a></li>
            <li><a href="/privacy" className="text-sm text-awareness-silver/70 hover:text-dream-ethereal transition-colors">Privacy Policy</a></li>
          </ul>
        </div>
      </Footer>
    </div>
  )
}
