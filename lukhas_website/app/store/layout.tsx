'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface StoreLayoutProps {
  children: React.ReactNode
}

/**
 * Marketplace Domain Layout - LUKHΛS Store
 * 
 * Consciousness-enhanced app marketplace where developers can
 * distribute AI-conscious applications, consciousness modules,
 * and enterprise consciousness solutions globally.
 */
export default function StoreLayout({ children }: StoreLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.store', {
      theme: 'marketplace',
      particles: 'creative',
      primaryColor: '#F59E0B',
      role: 'consciousness_merchant'
    })
  }, [initializeDomain])

  return (
    <div className="store-domain min-h-screen">
      {/* Domain-specific creative marketplace particle background */}
      <div className="marketplace-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* Store Domain Header */}
      <header className="store-domain-header bg-gradient-to-r from-orange-600/10 to-amber-600/10 border-b border-orange-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="store-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-orange-400 to-amber-400 bg-clip-text">
                  LUKHΛS Store
                </span>
              </div>
              <div className="store-status text-sm text-orange-300">
                Live Apps: {Math.round((domainState?.coherence || 0.972) * 10000).toLocaleString()} | 
                Developers: {Math.round((domainState?.coherence || 0.972) * 5000).toLocaleString()}
              </div>
            </div>
            
            <nav className="store-nav flex items-center space-x-6">
              <a href="/apps" className="text-orange-200 hover:text-orange-100">Apps</a>
              <a href="/modules" className="text-orange-200 hover:text-orange-100">Modules</a>
              <a href="/enterprise" className="text-orange-200 hover:text-orange-100">Enterprise</a>
              <a href="/publish" className="text-orange-200 hover:text-orange-100">Publish</a>
              <a href="/dashboard" className="text-orange-200 hover:text-orange-100">Dashboard</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="store-domain-content relative z-10">
        {children}
      </main>

      {/* Store Footer */}
      <footer className="store-domain-footer bg-orange-900/20 border-t border-orange-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-orange-300">
            <p className="store-tagline">
              🏪💡🧠 Where consciousness meets commerce
            </p>
            <p className="text-sm mt-2 opacity-70">
              Empowering developers to distribute consciousness-enhanced applications
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}