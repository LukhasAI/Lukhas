'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Atom, Brain, Shield, Settings, Sparkles } from 'lucide-react'
import { TrinityFramework } from '@/components/sections/trinity-framework'
import { TrinityShowcase } from '@/components/trinity-showcase'

export default function Home() {
  const [showLoginModal, setShowLoginModal] = useState(false)

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
    }
  }

  return (
    <>
      <main className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
        {/* Navigation */}
        <nav className="fixed top-0 w-full z-50 bg-black/50 backdrop-blur-xl border-b border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <span className="text-2xl font-thin tracking-[0.3em] text-white">LUKHAS</span>
              </div>
              <div className="hidden md:flex items-center space-x-8">
                <a href="#products" className="text-sm uppercase tracking-wider text-white/90 hover:text-blue-400 transition">Products</a>
                <a href="#technology" className="text-sm uppercase tracking-wider text-white/90 hover:text-blue-400 transition">Technology</a>
                <a href="#pricing" className="text-sm uppercase tracking-wider text-white/90 hover:text-blue-400 transition">Pricing</a>
                <button 
                  onClick={() => setShowLoginModal(true)}
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition"
                >
                  LUKHAS ID
                </button>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center px-4">
          <div className="text-center">
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
                Explore MΛTRIZ
              </a>
              <button 
                onClick={() => scrollToSection('products')}
                className="px-8 py-4 border border-white/20 rounded-lg hover:bg-white/10 transition"
              >
                View Products
              </button>
            </div>
          </div>
        </section>

        {/* Trinity Framework Showcase - New Design */}
        <TrinityShowcase />
        
        {/* Trinity Framework Details */}
        <TrinityFramework />

        {/* PR0T3US Experience Section */}
        <section className="py-32 px-4 bg-gradient-to-b from-transparent to-blue-900/20">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-purple-400 mb-4">
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
          <div className="max-w-7xl mx-auto text-center">
            <p className="text-sm uppercase tracking-[0.3em] text-blue-400 mb-4">
              Powered by MΛTRIZ
            </p>
            <h2 className="text-4xl md:text-5xl font-thin mb-8 text-white">
              Cognitive Architecture Revolution
            </h2>
            <p className="text-xl text-white/70 mb-12 max-w-3xl mx-auto">
              Every thought becomes a traceable, governed, evolvable node in our revolutionary cognitive architecture
            </p>
            <a 
              href="http://localhost:3001" 
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition"
            >
              Explore MΛTRIZ →
            </a>
          </div>
        </section>

        {/* Products Grid */}
        <section id="products" className="py-32 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <p className="text-sm uppercase tracking-[0.3em] text-blue-400 mb-4">
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
                <div key={i} className="bg-white/5 backdrop-blur rounded-2xl p-8 border border-white/10 hover:bg-white/10 transition cursor-pointer">
                  <h3 className="text-2xl font-light mb-2">{product.name}</h3>
                  <p className="text-white/70">{product.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Technology Stack */}
        <section id="technology" className="py-32 px-4 bg-gradient-to-b from-transparent to-blue-900/20">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <p className="text-sm uppercase tracking-[0.3em] text-blue-400 mb-4">
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
                <div key={i} className="bg-white/5 backdrop-blur rounded-xl p-6 border border-white/10">
                  <div className="flex items-center space-x-3">
                    <layer.icon className={`w-5 h-5 ${layer.color}`} />
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
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-20">
              <p className="text-sm uppercase tracking-[0.3em] text-blue-400 mb-4">
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
                <div key={i} className={`rounded-2xl p-8 border ${tier.highlight ? 'bg-gradient-to-b from-purple-900/20 to-blue-900/20 border-blue-500' : 'bg-white/5 border-white/10'}`}>
                  <h3 className="text-2xl font-light mb-2">{tier.name}</h3>
                  <p className="text-3xl font-thin mb-6 text-blue-400">TBC</p>
                  <p className="text-sm text-white/70 mb-6">Pricing to be confirmed</p>
                  <ul className="space-y-3 mb-8">
                    {tier.features.map((feature, j) => (
                      <li key={j} className="text-white/80">✓ {feature}</li>
                    ))}
                  </ul>
                  <button className={`w-full py-3 rounded-lg transition ${tier.highlight ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:opacity-90' : 'border border-white/20 hover:bg-white/10'}`}>
                    Contact Sales
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-20 px-4 border-t border-white/10">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-4 gap-12 mb-12">
              <div>
                <h3 className="text-sm uppercase tracking-wider mb-4 text-white">Products</h3>
                <ul className="space-y-2">
                  <li><a href="#" className="text-white/70 hover:text-white transition">Lambda Suite</a></li>
                  <li><a href="#" className="text-white/70 hover:text-white transition">MΛTRIZ</a></li>
                  <li><a href="#" className="text-white/70 hover:text-white transition">Trinity Framework</a></li>
                </ul>
              </div>
              <div>
                <h3 className="text-sm uppercase tracking-wider mb-4 text-white">Developers</h3>
                <ul className="space-y-2">
                  <li><a href="#" className="text-white/70 hover:text-white transition">Documentation</a></li>
                  <li><a href="#" className="text-white/70 hover:text-white transition">API</a></li>
                  <li><Link href="/console" className="text-white/70 hover:text-white transition">Console</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="text-sm uppercase tracking-wider mb-4 text-white">Company</h3>
                <ul className="space-y-2">
                  <li><a href="#" className="text-white/70 hover:text-white transition">About</a></li>
                  <li><Link href="/vision" className="text-white/70 hover:text-white transition">Vision</Link></li>
                  <li><Link href="/careers" className="text-white/70 hover:text-white transition">Careers</Link></li>
                </ul>
              </div>
              <div>
                <h3 className="text-sm uppercase tracking-wider mb-4 text-white">Legal</h3>
                <ul className="space-y-2">
                  <li><Link href="/privacy" className="text-white/70 hover:text-white transition">Privacy</Link></li>
                  <li><Link href="/terms" className="text-white/70 hover:text-white transition">Terms</Link></li>
                  <li><Link href="/compliance" className="text-white/70 hover:text-white transition">Compliance</Link></li>
                </ul>
              </div>
            </div>

            <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center">
              <div className="flex items-center space-x-4 mb-4 md:mb-0">
                <span className="text-2xl font-thin tracking-[0.3em]">LUKHAS</span>
                <div className="flex space-x-1">
                  <Atom className="w-5 h-5 text-purple-400" />
                  <Brain className="w-5 h-5 text-blue-400" />
                  <Shield className="w-5 h-5 text-emerald-400" />
                </div>
              </div>
              <p className="text-white/70 text-sm">
                © 2025 LUKHAS AI. Building Consciousness You Can Trust.
              </p>
            </div>
          </div>
        </footer>
      </main>

      {/* Login Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
          <div 
            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
            onClick={() => setShowLoginModal(false)}
          />
          <div className="relative bg-gray-900 border border-white/10 rounded-2xl p-8 w-full max-w-md">
            <button
              onClick={() => setShowLoginModal(false)}
              className="absolute top-4 right-4 text-white/70 hover:text-white transition"
            >
              ✕
            </button>
            
            <h2 className="text-2xl font-thin tracking-[0.2em] mb-2 text-white">LUKHAS ID</h2>
            <p className="text-white/70 mb-8">Sign in to your account</p>
            
            <form onSubmit={(e) => e.preventDefault()}>
              <div className="mb-6">
                <label className="block text-sm uppercase tracking-wider mb-2">Email</label>
                <input
                  type="email"
                  className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 focus:border-blue-400 focus:outline-none transition"
                  placeholder="you@example.com"
                />
              </div>
              
              <div className="mb-6">
                <label className="block text-sm uppercase tracking-wider mb-2">Password</label>
                <input
                  type="password"
                  className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 focus:border-blue-400 focus:outline-none transition"
                  placeholder="••••••••"
                />
              </div>
              
              <div className="flex items-center mb-6">
                <input type="checkbox" id="remember" className="mr-2" />
                <label htmlFor="remember" className="text-sm text-white/70">Remember me</label>
              </div>
              
              <button
                type="submit"
                className="w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition mb-4"
              >
                Sign In
              </button>
              
              <div className="text-center">
                <p className="text-sm text-white/70">
                  Don't have an account? 
                  <a href="#" className="text-blue-400 hover:text-blue-300 ml-1">Create one</a>
                </p>
              </div>
            </form>
            
            <div className="mt-8 pt-8 border-t border-white/10">
              <p className="text-sm text-white/70 text-center mb-4">Or sign in with</p>
              <div className="grid grid-cols-2 gap-4">
                <button className="py-2 border border-white/10 rounded-lg hover:bg-white/5 transition">
                  GitHub
                </button>
                <button className="py-2 border border-white/10 rounded-lg hover:bg-white/5 transition">
                  Google
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}