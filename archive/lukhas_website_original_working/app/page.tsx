'use client'

import { Atom, Brain, Shield, Settings, Sparkles } from 'lucide-react'
import { TrinityFramework } from '@/components/sections/trinity-framework'
import { TrinityShowcase } from '@/components/trinity-showcase'
import Link from 'next/link'

export default function Home() {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <>
      <main className="min-h-screen relative">
        {/* Navigation handled by StateLayout */}

        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center">
          <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14">
            <div className="text-center max-w-prose mx-auto">
            <p className="text-sm uppercase tracking-[0.3em] text-blue-400 mb-8">
              Logical Unified Knowledge Hyper-Adaptive Superior Systems
            </p>
            <h1 className="text-6xl md:text-8xl font-thin tracking-[0.3em] mb-8 text-white">
              LUKHAS
            </h1>
            <p className="text-xl md:text-2xl text-white/70 mb-12">
              Building Consciousness You Can Trust
            </p>
            
            {/* Trinity Symbols */}
            <div className="flex justify-center space-x-12 mb-12">
              <div className="text-center">
                <div className="flex justify-center mb-2">
                  <Atom className="w-10 h-10 text-purple-400" />
                </div>
                <p className="text-xs uppercase tracking-wider text-white">Identity</p>
              </div>
              <div className="text-center">
                <div className="flex justify-center mb-2">
                  <Brain className="w-10 h-10 text-blue-400" />
                </div>
                <p className="text-xs uppercase tracking-wider text-white">Consciousness</p>
              </div>
              <div className="text-center">
                <div className="flex justify-center mb-2">
                  <Shield className="w-10 h-10 text-emerald-400" />
                </div>
                <p className="text-xs uppercase tracking-wider text-white">Guardian</p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/experience"
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition inline-block animate-pulse"
              >
                Try the Experience
              </Link>
              <a 
                href="http://localhost:3001"
                target="_blank"
                rel="noopener noreferrer"
                className="px-8 py-4 border border-white/20 rounded-lg hover:bg-white/10 transition inline-block"
              >
                <span aria-label="Explore Matriz">Explore MΛTRIZ</span>
              </a>
              <button 
                onClick={() => scrollToSection('products')}
                className="px-8 py-4 border border-white/20 rounded-lg hover:bg-white/10 transition"
              >
                View Products
              </button>
            </div>
            </div>
          </div>
        </section>

        {/* Trinity Framework Showcase - New Design */}
        <TrinityShowcase />
        
        {/* Trinity Framework Details */}
        <TrinityFramework />

        {/* PR0T3US Experience Section */}
        <section className="py-32 px-4 bg-gradient-to-b from-transparent to-blue-900/20">
          <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <p className="text-[11px] tracking-[0.18em] text-white/50 uppercase mb-4">
                  Voice-Reactive Visualization
                </p>
                <h2 className="text-4xl md:text-5xl font-thin mb-8 text-white">
                  PR0T3US Experience
                </h2>
                <p className="text-xl text-white/70 mb-6">
                  Transform your voice and consciousness into living, breathing geometric forms. 
                  Experience real-time AI-driven particle systems that respond to your emotions and thoughts.
                </p>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-start">
                    <span className="text-blue-400 mr-3">•</span>
                    <span className="text-white/80">Voice-controlled 3D morphing shapes</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-purple-400 mr-3">•</span>
                    <span className="text-white/80">Real-time consciousness visualization</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-400 mr-3">•</span>
                    <span className="text-white/80">AI-powered emotional expression</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-orange-400 mr-3">•</span>
                    <span className="text-white/80">Multi-provider AI integration</span>
                  </li>
                </ul>
                <Link 
                  href="/experience"
                  className="inline-block px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition"
                >
                  Launch PR0T3US →
                </Link>
              </div>
              <div className="relative">
                <div className="aspect-square bg-gradient-to-br from-purple-900/20 to-blue-900/20 rounded-2xl border border-white/10 flex items-center justify-center">
                  <div className="text-center">
                    <div className="inline-block p-8 bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-full mb-4">
                      <Sparkles className="w-16 h-16 text-blue-400" />
                    </div>
                    <p className="text-sm uppercase tracking-wider text-white/70">
                      Interactive Consciousness
                    </p>
                  </div>
                </div>
                <div className="absolute -top-4 -right-4 w-20 h-20 bg-purple-600/20 rounded-full blur-3xl" />
                <div className="absolute -bottom-4 -left-4 w-20 h-20 bg-blue-600/20 rounded-full blur-3xl" />
              </div>
            </div>
          </div>
        </section>

        {/* MATRIZ Section */}
        <section className="py-32 px-4 bg-gradient-to-b from-transparent to-purple-900/20">
          <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14 text-center">
            <p className="text-[11px] tracking-[0.18em] text-white/50 uppercase mb-4">
              <span aria-label="Powered by Matriz">Powered by MΛTRIZ</span>
            </p>
            <h2 className="text-4xl md:text-5xl font-thin mb-8 text-white">
              Cognitive Architecture Revolution
            </h2>
            <p className="text-xl text-white/70 mb-12 max-w-3xl mx-auto">
              Every thought becomes a traceable, governed, evolvable node in our consciousness-aware cognitive architecture
            </p>
            <a 
              href="http://localhost:3001" 
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition"
            >
              <span aria-label="Explore Matriz">Explore MΛTRIZ →</span>
            </a>
          </div>
        </section>

        {/* Products Grid */}
        <section id="products" className="py-32 px-4">
          <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14">
            <div className="text-center mb-20">
              <p className="text-[11px] tracking-[0.18em] text-white/50 uppercase mb-4">
                Lambda Products Suite
              </p>
              <h2 className="text-4xl md:text-5xl font-thin text-white">
                Enterprise-Ready AI Modules
              </h2>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { name: 'ΛLens', desc: 'Symbolic File Dashboard' },
                { name: 'WΛLLET', desc: 'Digital Identity Wallet' },
                { name: 'NIΛS', desc: 'Non-Intrusive Messaging' },
                { name: 'ΛBAS', desc: 'Attention Management' },
                { name: 'DΛST', desc: 'Context Intelligence' },
                { name: 'ΛTrace', desc: 'Quantum Metadata' },
              ].map((product, i) => (
                <div key={i} className="bg-white/5 backdrop-blur rounded-2xl p-8 border border-white/10 hover:bg-white/10 hover:shadow-[0_0_0_1px_rgba(255,255,255,.08)] transition cursor-pointer min-h-[152px]">
                  <h3 className="text-2xl font-light mb-2">{product.name}</h3>
                  <p className="text-white/70">{product.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Technology Stack */}
        <section id="technology" className="py-32 px-4 bg-gradient-to-b from-transparent to-blue-900/20">
          <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14">
            <div className="text-center mb-20">
              <p className="text-[11px] tracking-[0.18em] text-white/50 uppercase mb-4">
                Technology Stack
              </p>
              <h2 className="text-4xl md:text-5xl font-thin text-white">
                Quantum-Inspired & Bio-Adaptive
              </h2>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: Brain, name: 'Consciousness Layer', color: 'text-blue-400' },
                { icon: Atom, name: 'Identity Layer', color: 'text-purple-400' },
                { icon: Shield, name: 'Guardian Layer', color: 'text-emerald-400' },
                { icon: Settings, name: 'Infrastructure', color: 'text-white/70' }
              ].map((layer, i) => (
                <div key={i} className="bg-white/5 backdrop-blur rounded-xl p-6 border border-white/10 min-h-[152px] hover:shadow-[0_0_0_1px_rgba(255,255,255,.08)] transition-colors">
                  <div className="flex items-center space-x-3">
                    <layer.icon className={`w-6 h-6 md:w-7 md:h-7 ${layer.color}`} />
                    <p className="text-lg">{layer.name}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-12 grid md:grid-cols-3 gap-8 text-center">
              <div>
                <p className="text-4xl font-thin text-blue-400 mb-2">2.4M+</p>
                <p className="text-white/70">Operations/Second</p>
              </div>
              <div>
                <p className="text-4xl font-thin text-purple-400 mb-2">200+</p>
                <p className="text-white/70">Specialized Modules</p>
              </div>
              <div>
                <p className="text-4xl font-thin text-green-400 mb-2">25</p>
                <p className="text-white/70">AI Agents</p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section id="pricing" className="py-32 px-4">
          <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14">
            <div className="text-center mb-20">
              <p className="text-[11px] tracking-[0.18em] text-white/50 uppercase mb-4">
                Pricing
              </p>
              <h2 className="text-4xl md:text-5xl font-thin text-white">
                Choose Your Tier
              </h2>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {[
                { name: 'Starter', features: ['Single product access', 'Basic features', 'Community support'] },
                { name: 'Professional', features: ['Multiple products bundle', 'Advanced features', 'Priority support'], highlight: true },
                { name: 'Enterprise', features: ['All products access', 'Custom integration', 'Dedicated support'] }
              ].map((tier, i) => (
                <div key={i} className={`rounded-2xl p-8 border flex flex-col justify-between min-h-[380px] ${tier.highlight ? 'bg-gradient-to-b from-purple-900/20 to-blue-900/20 border-blue-500' : 'bg-white/5 border-white/10'} hover:shadow-[0_0_0_1px_rgba(255,255,255,.08)] transition`}>
                  <div>
                    <h3 className="text-2xl font-light mb-2">{tier.name}</h3>
                    <p className="text-3xl font-thin mb-6 text-blue-400">TBC</p>
                    <p className="text-sm text-white/70 mb-6">Pricing to be confirmed</p>
                    <ul className="space-y-3 mb-8">
                      {tier.features.map((feature, j) => (
                        <li key={j} className="text-white/80">✓ {feature}</li>
                      ))}
                    </ul>
                  </div>
                  <button className={`w-full py-3 rounded-lg transition ${tier.highlight ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:opacity-90' : 'border border-white/20 hover:bg-white/10'}`}>
                    Contact Sales
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer - Centered Design */}
        <footer className="mt-24 border-t border-white/10 bg-black/30">
          <div className="mx-auto w-full max-w-screen-2xl px-6 md:px-10 lg:px-14 py-10">
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="text-[11px] tracking-[0.18em] text-white/50 uppercase">LUKHΛS</div>
              <nav className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[12px] text-white/60">
                <a className="hover:text-white/80" href="/privacy">Privacy</a>
                <a className="hover:text-white/80" href="/terms">Terms</a>
                <a className="hover:text-white/80" href="/compliance">Compliance</a>
                <a className="hover:text-white/80" href="/docs">Docs</a>
              </nav>
              <div className="text-[11px] text-white/40">© {new Date().getFullYear()} LUKHΛS AI. Building Consciousness You Can Trust.</div>
            </div>
          </div>
        </footer>
      </main>

      {/* Login modal handled by StateLayout */}
    </>
  )
}