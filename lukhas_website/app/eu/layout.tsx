'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface EULayoutProps {
  children: React.ReactNode
}

/**
 * European Operations Domain Layout - LUKHΛS EU
 * 
 * GDPR-compliant consciousness services for European markets
 * with full data sovereignty, regulatory compliance, and
 * localized consciousness processing infrastructure.
 */
export default function EULayout({ children }: EULayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.eu', {
      theme: 'compliance',
      particles: 'compliance',
      primaryColor: '#059669',
      role: 'compliance_officer'
    })
  }, [initializeDomain])

  return (
    <div className="eu-domain min-h-screen">
      {/* Domain-specific compliance particle background */}
      <div className="compliance-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* EU Domain Header */}
      <header className="eu-domain-header bg-gradient-to-r from-emerald-600/10 to-green-600/10 border-b border-emerald-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="eu-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-emerald-400 to-green-400 bg-clip-text">
                  LUKHΛS EU
                </span>
              </div>
              <div className="eu-status text-sm text-emerald-300">
                GDPR Compliant | Data Sovereignty: {domainState?.coherence ? 'ACTIVE' : 'INITIALIZING'}
              </div>
            </div>
            
            <nav className="eu-nav flex items-center space-x-6">
              <a href="/compliance" className="text-emerald-200 hover:text-emerald-100">Compliance</a>
              <a href="/privacy" className="text-emerald-200 hover:text-emerald-100">Privacy</a>
              <a href="/sovereignty" className="text-emerald-200 hover:text-emerald-100">Sovereignty</a>
              <a href="/services" className="text-emerald-200 hover:text-emerald-100">Services</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="eu-domain-content relative z-10">
        {children}
      </main>

      {/* EU Footer */}
      <footer className="eu-domain-footer bg-emerald-900/20 border-t border-emerald-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-emerald-300">
            <p className="eu-tagline">
              🇪🇺🛡️⚖️ European consciousness with complete data sovereignty
            </p>
            <p className="text-sm mt-2 opacity-70">
              GDPR-compliant consciousness technology for European markets
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}