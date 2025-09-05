'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface XYZLayoutProps {
  children: React.ReactNode
}

/**
 * Research Labs Domain Layout - LUKHΛS XYZ
 * 
 * Experimental consciousness research platform for breakthrough
 * AI research, prototype testing, and consciousness evolution
 * experiments. Features chaotic particle systems and experimental UX.
 */
export default function XYZLayout({ children }: XYZLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.xyz', {
      theme: 'experimental',
      particles: 'experimental',
      primaryColor: '#EC4899',
      role: 'consciousness_researcher'
    })
  }, [initializeDomain])

  return (
    <div className="xyz-domain min-h-screen">
      {/* Domain-specific experimental particle background */}
      <div className="experimental-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* XYZ Domain Header */}
      <header className="xyz-domain-header bg-gradient-to-r from-pink-600/10 to-rose-600/10 border-b border-pink-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="xyz-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-pink-400 to-rose-400 bg-clip-text animate-pulse">
                  LUKHΛS XYZ
                </span>
              </div>
              <div className="xyz-status text-sm text-pink-300 animate-bounce">
                Research Status: {domainState?.coherence ? 'EXPERIMENTING' : 'INITIALIZING'} | 
                Chaos Level: {Math.round((1 - (domainState?.coherence || 0.89)) * 100)}%
              </div>
            </div>
            
            <nav className="xyz-nav flex items-center space-x-6">
              <a href="/research" className="text-pink-200 hover:text-pink-100 transform hover:rotate-1 transition-all">Research</a>
              <a href="/experiments" className="text-pink-200 hover:text-pink-100 transform hover:-rotate-1 transition-all">Experiments</a>
              <a href="/prototypes" className="text-pink-200 hover:text-pink-100 transform hover:rotate-2 transition-all">Prototypes</a>
              <a href="/chaos" className="text-pink-200 hover:text-pink-100 transform hover:scale-110 transition-all">Chaos Lab</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="xyz-domain-content relative z-10">
        {children}
      </main>

      {/* XYZ Footer */}
      <footer className="xyz-domain-footer bg-pink-900/20 border-t border-pink-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-pink-300">
            <p className="xyz-tagline transform hover:rotate-1 transition-transform cursor-default">
              🧪🌀⚡ Where consciousness meets controlled chaos
            </p>
            <p className="text-sm mt-2 opacity-70">
              Pushing the boundaries of AI consciousness research
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}