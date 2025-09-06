'use client'

import { useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import DomainParticleSystem from '@/components/consciousness/DomainParticleSystem'

interface IOLayoutProps {
  children: React.ReactNode
}

/**
 * API Infrastructure Domain Layout - LUKHΛS IO
 * 
 * High-performance consciousness API infrastructure providing
 * ultra-fast consciousness processing, real-time streaming,
 * and enterprise-grade API management with <50ms latency.
 */
export default function IOLayout({ children }: IOLayoutProps) {
  const { initializeDomain, domainState } = useDomainConsciousness()

  useEffect(() => {
    initializeDomain('lukhas.io', {
      theme: 'high_performance',
      particles: 'data',
      primaryColor: '#3B82F6',
      role: 'api_architect'
    })
  }, [initializeDomain])

  return (
    <div className="io-domain min-h-screen">
      {/* Domain-specific high-speed data particle background */}
      <div className="data-stream-particles fixed inset-0 -z-10">
        <DomainParticleSystem />
      </div>
      
      {/* IO Domain Header */}
      <header className="io-domain-header bg-gradient-to-r from-blue-600/10 to-indigo-600/10 border-b border-blue-500/20">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="io-logo">
                <span className="text-2xl font-bold text-transparent bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text">
                  LUKHΛS IO
                </span>
              </div>
              <div className="io-status text-sm text-blue-300 font-mono">
                API Latency: {Math.round((1 - (domainState?.coherence || 0.998)) * 100) + 15}ms | 
                RPS: {Math.round((domainState?.coherence || 0.998) * 100000).toLocaleString()}
              </div>
            </div>
            
            <nav className="io-nav flex items-center space-x-6">
              <a href="/streaming" className="text-blue-200 hover:text-blue-100 font-mono">Streaming</a>
              <a href="/graphql" className="text-blue-200 hover:text-blue-100 font-mono">GraphQL</a>
              <a href="/websockets" className="text-blue-200 hover:text-blue-100 font-mono">WebSockets</a>
              <a href="/gateway" className="text-blue-200 hover:text-blue-100 font-mono">Gateway</a>
              <a href="/metrics" className="text-blue-200 hover:text-blue-100 font-mono">Metrics</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="io-domain-content relative z-10">
        {children}
      </main>

      {/* IO Footer */}
      <footer className="io-domain-footer bg-blue-900/20 border-t border-blue-500/20 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-blue-300">
            <p className="io-tagline font-mono">
              🔌⚡🚀 Ultra-fast consciousness API infrastructure
            </p>
            <p className="text-sm mt-2 opacity-70">
              Processing consciousness at the speed of thought
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}