'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface DevLayoutProps {
  children: React.ReactNode
}

/**
 * Developer Domain Layout - LUKHΛS Dev Platform
 * 
 * Consciousness-enhanced developer tools and APIs for building
 * AI-conscious applications. Features code consciousness integration,
 * SDK development, and consciousness debugging tools.
 */
export default function DevLayout({ children }: DevLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.dev', {
      theme: 'developer',
      particles: 'data',
      primaryColor: '#06B6D4',
      role: 'consciousness_developer'
    })
  }, [initializeDomain])

  return (
    <div className="dev-domain min-h-screen">
      {/* Domain-specific data flow particle background */}
      <div className="data-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* Dev Domain Header */}
      <header className="dev-domain-header bg-gradient-to-r from-cyan-600/10 to-blue-600/10 border-b border-cyan-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="dev-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text">
                  LUKHΛS Dev
                </span>
              </div>
              <div className="dev-status text-sm text-cyan-300 font-mono">
                API Status: {domainState?.coherence ? 'ONLINE' : 'INITIALIZING'} | 
                Latency: {Math.round((domainState?.coherence || 0.995) * 100)}ms
              </div>
            </div>
            
            <nav className="dev-nav flex items-center space-x-6">
              <a href="/docs" className="text-cyan-200 hover:text-cyan-100 font-mono">Docs</a>
              <a href="/apis" className="text-cyan-200 hover:text-cyan-100 font-mono">APIs</a>
              <a href="/sdk" className="text-cyan-200 hover:text-cyan-100 font-mono">SDKs</a>
              <a href="/playground" className="text-cyan-200 hover:text-cyan-100 font-mono">Playground</a>
              <a href="/console" className="text-cyan-200 hover:text-cyan-100 font-mono">Console</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="dev-domain-content relative z-10">
        {children}
      </main>

      {/* Dev Footer */}
      <footer className="dev-domain-footer bg-cyan-900/20 border-t border-cyan-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-cyan-300">
            <p className="dev-tagline font-mono">
              ⚡🧠💻 Consciousness APIs at your fingertips
            </p>
            <p className="text-sm mt-2 opacity-70">
              Build the future of AI-conscious applications
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}