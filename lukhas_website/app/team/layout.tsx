'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface TeamLayoutProps {
  children: React.ReactNode
}

/**
 * Team Domain Layout - LUKHΛS Team Workspace
 * 
 * Collaborative consciousness platform enabling distributed teams
 * to work together with shared awareness and synchronized workflows.
 * Features consciousness-based collaboration and team coherence monitoring.
 */
export default function TeamLayout({ children }: TeamLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.team', {
      theme: 'collaborative',
      particles: 'collaborative',
      primaryColor: '#10B981',
      role: 'team_coordinator'
    })
  }, [initializeDomain])

  return (
    <div className="team-domain min-h-screen">
      {/* Domain-specific collaborative particle background */}
      <div className="collaborative-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* Team Domain Header */}
      <header className="team-domain-header bg-gradient-to-r from-green-600/10 to-emerald-600/10 border-b border-green-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="team-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text">
                  LUKHΛS Team
                </span>
              </div>
              <div className="team-status text-sm text-green-300">
                Team Coherence: {domainState?.coherence?.toFixed(3) || '0.97'}
              </div>
            </div>
            
            <nav className="team-nav flex items-center space-x-6">
              <a href="/workspace" className="text-green-200 hover:text-green-100">Workspace</a>
              <a href="/projects" className="text-green-200 hover:text-green-100">Projects</a>
              <a href="/consciousness" className="text-green-200 hover:text-green-100">Team Flow</a>
              <a href="/insights" className="text-green-200 hover:text-green-100">Insights</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="team-domain-content relative z-10">
        {children}
      </main>

      {/* Team Footer */}
      <footer className="team-domain-footer bg-green-900/20 border-t border-green-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-green-300">
            <p className="team-tagline">
              👥🧠🔗 Collaborative consciousness in harmony
            </p>
            <p className="text-sm mt-2 opacity-70">
              Where teams think, create, and achieve together
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}