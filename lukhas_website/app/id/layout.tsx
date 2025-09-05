'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface IDLayoutProps {
  children: React.ReactNode
}

/**
 * Identity Domain Layout - LUKHΛS ΛiD System
 * 
 * The quantum-secure digital identity platform providing
 * consciousness-based authentication and identity sovereignty.
 */
export default function IDLayout({ children }: IDLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.id', {
      theme: 'identity',
      particles: 'biometric',
      primaryColor: '#7C3AED',
      role: 'identity_sovereign'
    })
  }, [initializeDomain])

  return (
    <div className="id-domain min-h-screen">
      {/* Domain-specific biometric particle background */}
      <div className="biometric-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* Identity Domain Header */}
      <header className="id-domain-header bg-gradient-to-r from-purple-600/10 to-indigo-600/10 border-b border-purple-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="identity-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text">
                  LUKHΛS ΛiD
                </span>
              </div>
              <div className="identity-status text-sm text-purple-300">
                Security: Quantum-Resistant
              </div>
            </div>
            
            <nav className="identity-nav flex items-center space-x-6">
              <a href="/auth" className="text-purple-200 hover:text-purple-100">Authenticate</a>
              <a href="/dashboard" className="text-purple-200 hover:text-purple-100">Dashboard</a>
              <a href="/security" className="text-purple-200 hover:text-purple-100">Security</a>
              <a href="/privacy" className="text-purple-200 hover:text-purple-100">Privacy</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="id-domain-content relative z-10">
        {children}
      </main>

      {/* Identity Footer */}
      <footer className="id-domain-footer bg-purple-900/20 border-t border-purple-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-purple-300">
            <p className="identity-tagline">
              🛡️ Your consciousness signature - Unique, secure, sovereign
            </p>
            <p className="text-sm mt-2 opacity-70">
              Zero-knowledge identity with quantum-resistant security
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}