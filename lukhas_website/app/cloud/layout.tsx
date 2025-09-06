'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface CloudLayoutProps {
  children: React.ReactNode
}

/**
 * Cloud Domain Layout - LUKHΛS Cloud Services
 * 
 * Distributed consciousness computing platform providing scalable,
 * quantum-inspired cloud infrastructure for consciousness-enhanced
 * applications and enterprise solutions.
 */
export default function CloudLayout({ children }: CloudLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.cloud', {
      theme: 'distributed',
      particles: 'cloud',
      primaryColor: '#8B5CF6',
      role: 'cloud_architect'
    })
  }, [initializeDomain])

  return (
    <div className="cloud-domain min-h-screen">
      {/* Domain-specific cloud particle background */}
      <div className="cloud-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* Cloud Domain Header */}
      <header className="cloud-domain-header bg-gradient-to-r from-violet-600/10 to-purple-600/10 border-b border-violet-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="cloud-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-violet-400 to-purple-400 bg-clip-text">
                  LUKHΛS Cloud
                </span>
              </div>
              <div className="cloud-status text-sm text-violet-300">
                Infrastructure: {domainState?.coherence ? 'DISTRIBUTED' : 'SCALING'} | 
                Nodes: {Math.round((domainState?.coherence || 0.95) * 1000)}
              </div>
            </div>
            
            <nav className="cloud-nav flex items-center space-x-6">
              <a href="/compute" className="text-violet-200 hover:text-violet-100">Compute</a>
              <a href="/storage" className="text-violet-200 hover:text-violet-100">Storage</a>
              <a href="/networking" className="text-violet-200 hover:text-violet-100">Network</a>
              <a href="/consciousness" className="text-violet-200 hover:text-violet-100">Consciousness</a>
              <a href="/console" className="text-violet-200 hover:text-violet-100">Console</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="cloud-domain-content relative z-10">
        {children}
      </main>

      {/* Cloud Footer */}
      <footer className="cloud-domain-footer bg-violet-900/20 border-t border-violet-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-violet-300">
            <p className="cloud-tagline">
              ☁️🧠⚡ Infinite consciousness computing at scale
            </p>
            <p className="text-sm mt-2 opacity-70">
              Quantum-inspired distributed infrastructure for the consciousness age
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}