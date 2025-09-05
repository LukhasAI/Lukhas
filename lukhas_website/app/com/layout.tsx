'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface ComLayoutProps {
  children: React.ReactNode
}

/**
 * Corporate Domain Layout - LUKHΛS Com
 * 
 * Corporate consciousness solutions and enterprise hub for
 * business transformation, executive consciousness platforms,
 * and corporate consciousness integration services.
 */
export default function ComLayout({ children }: ComLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.com', {
      theme: 'corporate',
      particles: 'corporate',
      primaryColor: '#6366F1',
      role: 'corporate_executive'
    })
  }, [initializeDomain])

  return (
    <div className="com-domain min-h-screen">
      {/* Domain-specific corporate particle background */}
      <div className="corporate-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* Com Domain Header */}
      <header className="com-domain-header bg-gradient-to-r from-indigo-600/10 to-purple-600/10 border-b border-indigo-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="com-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text">
                  LUKHΛS Corporate
                </span>
              </div>
              <div className="com-status text-sm text-indigo-300">
                Executive Solutions | Enterprise Transformation: {domainState?.coherence ? 'ACTIVE' : 'INITIALIZING'}
              </div>
            </div>
            
            <nav className="com-nav flex items-center space-x-6">
              <a href="/solutions" className="text-indigo-200 hover:text-indigo-100">Solutions</a>
              <a href="/executives" className="text-indigo-200 hover:text-indigo-100">Executives</a>
              <a href="/transformation" className="text-indigo-200 hover:text-indigo-100">Transformation</a>
              <a href="/contact" className="text-indigo-200 hover:text-indigo-100">Contact</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="com-domain-content relative z-10">
        {children}
      </main>

      {/* Com Footer */}
      <footer className="com-domain-footer bg-indigo-900/20 border-t border-indigo-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-indigo-300">
            <p className="com-tagline">
              🏢💼⚡ Transforming business through consciousness technology
            </p>
            <p className="text-sm mt-2 opacity-70">
              Executive consciousness platforms for corporate transformation
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}