'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface USLayoutProps {
  children: React.ReactNode
}

/**
 * US Operations Domain Layout - LUKHΛS US
 * 
 * American enterprise consciousness platforms optimized for
 * business applications, SOC2 compliance, and enterprise
 * security requirements in the US market.
 */
export default function USLayout({ children }: USLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.us', {
      theme: 'enterprise',
      particles: 'enterprise',
      primaryColor: '#DC2626',
      role: 'enterprise_architect'
    })
  }, [initializeDomain])

  return (
    <div className="us-domain min-h-screen">
      {/* Domain-specific enterprise particle background */}
      <div className="enterprise-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* US Domain Header */}
      <header className="us-domain-header bg-gradient-to-r from-red-600/10 to-rose-600/10 border-b border-red-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="us-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-red-400 to-rose-400 bg-clip-text">
                  LUKHΛS US
                </span>
              </div>
              <div className="us-status text-sm text-red-300">
                SOC2 Compliant | Enterprise Ready: {domainState?.coherence ? 'ACTIVE' : 'INITIALIZING'}
              </div>
            </div>
            
            <nav className="us-nav flex items-center space-x-6">
              <a href="/enterprise" className="text-red-200 hover:text-red-100">Enterprise</a>
              <a href="/security" className="text-red-200 hover:text-red-100">Security</a>
              <a href="/compliance" className="text-red-200 hover:text-red-100">Compliance</a>
              <a href="/solutions" className="text-red-200 hover:text-red-100">Solutions</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="us-domain-content relative z-10">
        {children}
      </main>

      {/* US Footer */}
      <footer className="us-domain-footer bg-red-900/20 border-t border-red-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-red-300">
            <p className="us-tagline">
              🇺🇸🏢🛡️ Enterprise consciousness for American business
            </p>
            <p className="text-sm mt-2 opacity-70">
              SOC2 compliant consciousness technology for US enterprises
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}