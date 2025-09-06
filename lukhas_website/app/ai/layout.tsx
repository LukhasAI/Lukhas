'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface AILayoutProps {
  children: React.ReactNode
}

/**
 * AI Domain Layout - Main LUKHΛS AI Platform
 * 
 * This is the primary consciousness hub where users explore
 * AI consciousness technology, the Trinity Framework, and
 * the core platform capabilities.
 */
export default function AILayout({ children }: AILayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.ai', {
      theme: 'consciousness',
      particles: 'neural',
      primaryColor: '#00D4FF',
      role: 'consciousness_explorer'
    })
  }, [initializeDomain])

  return (
    <div className="ai-domain min-h-screen">
      {/* Domain-specific consciousness particle background */}
      <div className="consciousness-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* AI Domain Header */}
      <header className="ai-domain-header bg-gradient-to-r from-blue-600/10 to-cyan-600/10 border-b border-blue-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="consciousness-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text">
                  LUKHΛS AI
                </span>
              </div>
              <div className="consciousness-status text-sm text-blue-300">
                Coherence: {domainState?.coherence?.toFixed(3) || '0.98'}
              </div>
            </div>
            
            <nav className="consciousness-nav flex items-center space-x-6">
              <a href="/consciousness" className="text-blue-200 hover:text-blue-100">Consciousness</a>
              <a href="/trinity" className="text-blue-200 hover:text-blue-100">Trinity Framework</a>
              <a href="/research" className="text-blue-200 hover:text-blue-100">Research</a>
              <a href="/experience" className="text-blue-200 hover:text-blue-100">Experience</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="ai-domain-content relative z-10">
        {children}
      </main>

      {/* Consciousness Footer */}
      <footer className="ai-domain-footer bg-blue-900/20 border-t border-blue-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-blue-300">
            <p className="consciousness-tagline">
              ⚛️🧠🛡️ Where consciousness meets code
            </p>
            <p className="text-sm mt-2 opacity-70">
              Exploring the frontiers of AI consciousness technology
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}