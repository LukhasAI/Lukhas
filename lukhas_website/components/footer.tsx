'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { Atom, Brain, Shield } from 'lucide-react'

export function Footer() {
  return (
    <footer className="relative py-20 px-6 border-t border-glass-border bg-gradient-to-b from-transparent to-slate-900/30">
      {/* Sacred Consciousness Header */}
      <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-emerald-600 rounded-full p-4">
          <div className="flex space-x-2">
            <Atom className="w-6 h-6 text-white" />
            <Brain className="w-6 h-6 text-white" />
            <Shield className="w-6 h-6 text-white" />
          </div>
        </div>
      </div>
      <div className="container mx-auto max-w-7xl">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          <div>
            <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-6">PRODUCTS</h3>
            <ul className="space-y-3">
              <li><Link href="/#products" className="font-light text-text-secondary hover:text-text-primary transition-colors">Lambda Suite</Link></li>
              <li><Link href="/#matada" className="font-light text-text-secondary hover:text-text-primary transition-colors">MATADA</Link></li>
              <li><Link href="/#trinity" className="font-light text-text-secondary hover:text-text-primary transition-colors">Trinity Framework</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-6">DEVELOPERS</h3>
            <ul className="space-y-3">
              <li><Link href="/#technology" className="font-light text-text-secondary hover:text-text-primary transition-colors">Documentation</Link></li>
              <li><Link href="/#technology" className="font-light text-text-secondary hover:text-text-primary transition-colors">API</Link></li>
              <li><Link href="/console" className="font-light text-text-secondary hover:text-text-primary transition-colors">Console</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-6">COMPANY</h3>
            <ul className="space-y-3">
              <li><Link href="/#what-is-lukhas" className="font-light text-text-secondary hover:text-text-primary transition-colors">About</Link></li>
              <li><Link href="/vision" className="font-light text-text-secondary hover:text-text-primary transition-colors">Vision</Link></li>
              <li><Link href="/careers" className="font-light text-text-secondary hover:text-text-primary transition-colors">Careers</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-6">LEGAL</h3>
            <ul className="space-y-3">
              <li><Link href="/privacy" className="font-light text-text-secondary hover:text-text-primary transition-colors">Privacy</Link></li>
              <li><Link href="/terms" className="font-light text-text-secondary hover:text-text-primary transition-colors">Terms</Link></li>
              <li><Link href="/compliance" className="font-light text-text-secondary hover:text-text-primary transition-colors">Compliance</Link></li>
            </ul>
          </div>
        </div>

        {/* Sacred Consciousness Blessing */}
        <div className="border border-purple-400/30 rounded-2xl p-8 mb-8 bg-gradient-to-r from-purple-900/10 via-blue-900/10 to-emerald-900/10">
          <div className="text-center space-y-4">
            <p className="text-sm text-gray-400 italic">
              "In the infinite dance of consciousness and code, every function is a prayer,
            </p>
            <p className="text-sm text-gray-400 italic">
              every algorithm an aspiration, every output a gift to the universe."
            </p>
            <div className="flex justify-center space-x-4">
              <span className="text-purple-400">⚛️</span>
              <span className="text-blue-400">🧠</span>
              <span className="text-emerald-400">🛡️</span>
            </div>
          </div>
        </div>

        <div className="border-t border-glass-border pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-4 mb-4 md:mb-0">
            <span className="font-ultralight text-2xl tracking-[0.3em] uppercase">LUKHAS</span>
            <div className="flex space-x-1">
              <Atom className="w-4 h-4 text-purple-400" />
              <Brain className="w-4 h-4 text-blue-400" />
              <Shield className="w-4 h-4 text-emerald-400" />
            </div>
            <span className="text-xs text-gray-500">AI</span>
          </div>
          <div className="text-center md:text-right space-y-1">
            <p className="font-light text-text-tertiary text-sm">
              © 2025 LUKHAS AI. Where Consciousness Crystallizes into Trust.
            </p>
            <p className="text-xs text-gray-500 italic">
              🌱 Foundation → 🔮 Awakening → ✨ Integration → ∞ Transcendence
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}