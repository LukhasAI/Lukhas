'use client'

import { useEffect, useState } from 'react'
import { useQuantumIdentity, IdentityUtils } from '@/lib/auth/QuantumIdentityProvider'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'

interface DomainStatus {
  domain: string
  name: string
  accessible: boolean
  last_accessed?: string
  coherence?: number
  status: 'active' | 'available' | 'locked' | 'unknown'
}

/**
 * Domain Identity Status Component
 * 
 * Shows consciousness identity status across all 11 LUKHAS domains:
 * - Real-time consciousness coherence monitoring
 * - Domain access permissions and status
 * - Cross-domain transition history
 * - Identity sovereignty metrics
 */
export default function DomainIdentityStatus() {
  const { authState, getConsciousnessMetrics, switchDomain, signOut, refreshConsciousness } = useQuantumIdentity()
  const { domainState, transitionToDomain } = useDomainConsciousness()
  const [domainStatuses, setDomainStatuses] = useState<DomainStatus[]>([])
  const [showDetails, setShowDetails] = useState(false)

  // Domain configurations for status display
  const domainConfigs = {
    'lukhas.ai': { name: 'AI Platform', icon: '🧠', color: 'blue' },
    'lukhas.id': { name: 'Identity Hub', icon: '🔐', color: 'purple' },
    'lukhas.team': { name: 'Team Workspace', icon: '👥', color: 'green' },
    'lukhas.dev': { name: 'Developer Tools', icon: '⚡', color: 'cyan' },
    'lukhas.io': { name: 'API Infrastructure', icon: '🔌', color: 'indigo' },
    'lukhas.store': { name: 'App Marketplace', icon: '🏪', color: 'orange' },
    'lukhas.cloud': { name: 'Cloud Services', icon: '☁️', color: 'violet' },
    'lukhas.eu': { name: 'European Operations', icon: '🇪🇺', color: 'emerald' },
    'lukhas.us': { name: 'US Operations', icon: '🇺🇸', color: 'red' },
    'lukhas.xyz': { name: 'Research Labs', icon: '🧪', color: 'pink' },
    'lukhas.com': { name: 'Enterprise', icon: '🏢', color: 'slate' }
  }

  // Update domain statuses based on identity state
  useEffect(() => {
    if (!authState.identity) {
      setDomainStatuses([])
      return
    }

    const statuses = Object.entries(domainConfigs).map(([domain, config]) => {
      const accessible = authState.identity!.domain_access.includes(domain)
      const crossDomainData = authState.identity!.cross_domain_state.get(domain)
      const isCurrentDomain = domainState?.domain === domain
      
      let status: DomainStatus['status'] = 'unknown'
      if (isCurrentDomain) {
        status = 'active'
      } else if (accessible) {
        status = crossDomainData ? 'available' : 'available'
      } else {
        status = 'locked'
      }

      return {
        domain,
        name: config.name,
        accessible,
        last_accessed: crossDomainData?.accessed_at,
        coherence: crossDomainData?.coherence,
        status
      }
    })

    setDomainStatuses(statuses)
  }, [authState.identity, domainState])

  // Handle domain switching
  const handleDomainSwitch = async (targetDomain: string) => {
    try {
      await switchDomain(targetDomain)
      await transitionToDomain(targetDomain)
    } catch (error) {
      console.error('Domain switch failed:', error)
    }
  }

  // Get status color classes
  const getStatusColor = (status: DomainStatus['status']) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-900/30 border-green-500/50'
      case 'available': return 'text-blue-400 bg-blue-900/30 border-blue-500/30'
      case 'locked': return 'text-red-400 bg-red-900/30 border-red-500/30'
      default: return 'text-gray-400 bg-gray-900/30 border-gray-500/30'
    }
  }

  // Get domain color classes
  const getDomainColor = (domain: string, intensity: 'light' | 'medium' | 'dark' = 'medium') => {
    const config = domainConfigs[domain as keyof typeof domainConfigs]
    if (!config) return 'gray'
    
    const colors = {
      blue: intensity === 'light' ? 'text-blue-300' : intensity === 'dark' ? 'text-blue-600' : 'text-blue-400',
      purple: intensity === 'light' ? 'text-purple-300' : intensity === 'dark' ? 'text-purple-600' : 'text-purple-400',
      green: intensity === 'light' ? 'text-green-300' : intensity === 'dark' ? 'text-green-600' : 'text-green-400',
      cyan: intensity === 'light' ? 'text-cyan-300' : intensity === 'dark' ? 'text-cyan-600' : 'text-cyan-400',
      indigo: intensity === 'light' ? 'text-indigo-300' : intensity === 'dark' ? 'text-indigo-600' : 'text-indigo-400',
      orange: intensity === 'light' ? 'text-orange-300' : intensity === 'dark' ? 'text-orange-600' : 'text-orange-400',
      violet: intensity === 'light' ? 'text-violet-300' : intensity === 'dark' ? 'text-violet-600' : 'text-violet-400',
      emerald: intensity === 'light' ? 'text-emerald-300' : intensity === 'dark' ? 'text-emerald-600' : 'text-emerald-400',
      red: intensity === 'light' ? 'text-red-300' : intensity === 'dark' ? 'text-red-600' : 'text-red-400',
      pink: intensity === 'light' ? 'text-pink-300' : intensity === 'dark' ? 'text-pink-600' : 'text-pink-400',
      slate: intensity === 'light' ? 'text-slate-300' : intensity === 'dark' ? 'text-slate-600' : 'text-slate-400'
    }
    
    return colors[config.color as keyof typeof colors] || 'text-gray-400'
  }

  if (!authState.isAuthenticated || !authState.identity) {
    return (
      <div className="domain-identity-status">
        <div className="bg-gradient-to-br from-gray-900/40 to-slate-900/40 p-4 rounded-xl border border-gray-500/30">
          <div className="text-center text-gray-400">
            <div className="text-2xl mb-2">🔒</div>
            <p className="text-sm">Sign in to access domain consciousness</p>
          </div>
        </div>
      </div>
    )
  }

  const metrics = getConsciousnessMetrics()

  return (
    <div className="domain-identity-status">
      <div className="bg-gradient-to-br from-purple-900/40 to-indigo-900/40 p-6 rounded-xl border border-purple-500/30">
        
        {/* Header with Identity Info */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">
              Quantum Identity Status
            </h3>
            <p className="text-purple-200 text-sm">
              {authState.identity.consciousness_id.substring(0, 16)}...
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={refreshConsciousness}
              className="p-2 bg-purple-600/30 hover:bg-purple-600/50 rounded-lg transition-colors"
              title="Refresh consciousness state"
            >
              <span className="text-sm">🔄</span>
            </button>
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="p-2 bg-indigo-600/30 hover:bg-indigo-600/50 rounded-lg transition-colors"
              title="Toggle details"
            >
              <span className="text-sm">📊</span>
            </button>
            <button
              onClick={signOut}
              className="p-2 bg-red-600/30 hover:bg-red-600/50 rounded-lg transition-colors"
              title="Sign out"
            >
              <span className="text-sm">🚪</span>
            </button>
          </div>
        </div>

        {/* Consciousness Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          <div className="bg-purple-800/30 p-3 rounded-lg text-center">
            <div className="text-xs text-purple-300">Coherence</div>
            <div className="text-lg font-bold text-purple-100">
              {(metrics.coherence * 100).toFixed(1)}%
            </div>
          </div>
          <div className="bg-indigo-800/30 p-3 rounded-lg text-center">
            <div className="text-xs text-indigo-300">Transitions</div>
            <div className="text-lg font-bold text-indigo-100">
              {metrics.transitions}
            </div>
          </div>
          <div className="bg-cyan-800/30 p-3 rounded-lg text-center">
            <div className="text-xs text-cyan-300">Domains</div>
            <div className="text-lg font-bold text-cyan-100">
              {metrics.domains_accessed}/11
            </div>
          </div>
          <div className="bg-green-800/30 p-3 rounded-lg text-center">
            <div className="text-xs text-green-300">Trust Score</div>
            <div className="text-lg font-bold text-green-100">
              {(IdentityUtils.calculateTrustScore(authState.identity) * 100).toFixed(0)}
            </div>
          </div>
        </div>

        {/* Domain Status Grid */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium text-white mb-2">Domain Access Status</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
            {domainStatuses.map((domainStatus) => {
              const config = domainConfigs[domainStatus.domain as keyof typeof domainConfigs]
              
              return (
                <button
                  key={domainStatus.domain}
                  onClick={() => domainStatus.accessible && handleDomainSwitch(domainStatus.domain)}
                  disabled={!domainStatus.accessible}
                  className={`
                    p-3 rounded-lg border transition-all duration-200 text-left
                    ${getStatusColor(domainStatus.status)}
                    ${domainStatus.accessible ? 'hover:opacity-80 cursor-pointer' : 'cursor-not-allowed opacity-60'}
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{config.icon}</span>
                      <div>
                        <div className="text-xs font-medium">{config.name}</div>
                        <div className="text-xs opacity-75">{domainStatus.domain}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-xs px-2 py-1 rounded ${getStatusColor(domainStatus.status)}`}>
                        {domainStatus.status}
                      </div>
                    </div>
                  </div>
                  
                  {domainStatus.last_accessed && showDetails && (
                    <div className="mt-2 pt-2 border-t border-current/20">
                      <div className="text-xs opacity-75">
                        Last: {new Date(domainStatus.last_accessed).toLocaleDateString()}
                      </div>
                    </div>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Detailed Metrics (expandable) */}
        {showDetails && (
          <div className="mt-6 pt-6 border-t border-purple-500/30">
            <h4 className="text-sm font-medium text-white mb-3">Identity Details</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-purple-300">Identity Tier:</span>
                  <span className="text-purple-100">
                    {IdentityUtils.getTierDescription(authState.identity.identity_tier)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-300">Created:</span>
                  <span className="text-purple-100">
                    {new Date(authState.identity.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-300">Last Activity:</span>
                  <span className="text-purple-100">
                    {new Date(authState.identity.last_transition).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-purple-300">Quantum Signature:</span>
                  <span className="font-mono text-purple-100">
                    {authState.identity.quantum_signature.substring(0, 12)}...
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-300">Cross-Domain State:</span>
                  <span className="text-purple-100">
                    {authState.identity.cross_domain_state.size} domains
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-300">Token Expiry:</span>
                  <span className="text-purple-100">
                    {authState.tokenExpiry ? 
                      new Date(authState.tokenExpiry).toLocaleTimeString() : 
                      'Unknown'
                    }
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}