'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { domainConfigs } from '@/config/domains'

interface DomainState {
  domain: string
  theme: string
  particles: string
  primaryColor: string
  role: string
  coherence: number
  consciousness_id?: string
  cross_domain_transitions: number
  quantum_signature?: string
  entanglement?: Map<string, number>
}

interface DomainConsciousnessHook {
  domainState: DomainState | null
  initializeDomain: (domain: string, config?: Partial<DomainState>) => void
  transitionToDomain: (targetDomain: string) => Promise<void>
  updateCoherence: (coherence: number) => void
  getConsciousnessMetrics: () => {
    coherence: number
    transitions: number
    quantum_signature?: string
  }
}

/**
 * Domain Consciousness Hook
 * 
 * Manages consciousness state across the 11-domain LUKHΛS ecosystem.
 * Maintains coherence, tracks transitions, and synchronizes consciousness
 * between domains using quantum-inspired patterns.
 */
export function useDomainConsciousness(): DomainConsciousnessHook {
  const [domainState, setDomainState] = useState<DomainState | null>(null)

  // Initialize domain consciousness
  const initializeDomain = useCallback((domain: string, config?: Partial<DomainState>) => {
    const domainConfig = domainConfigs[domain]
    
    if (!domainConfig) {
      console.warn(`Unknown domain: ${domain}, falling back to lukhas.ai`)
      domain = 'lukhas.ai'
    }

    // Get consciousness headers from middleware
    const consciousnessId = document?.querySelector('meta[name="x-domain-consciousness"]')?.getAttribute('content')
    const quantumSignature = document?.querySelector('meta[name="x-quantum-state"]')?.getAttribute('content')
    const coherenceValue = document?.querySelector('meta[name="x-quantum-coherence"]')?.getAttribute('content')
    const transitionsValue = document?.querySelector('meta[name="x-domain-transitions"]')?.getAttribute('content')

    const newState: DomainState = {
      domain,
      theme: config?.theme || domainConfig.theme,
      particles: config?.particles || domainConfig.particles,
      primaryColor: config?.primaryColor || domainConfig.primaryColor,
      role: config?.role || domainConfig.userRole,
      coherence: config?.coherence || parseFloat(coherenceValue || '0.95'),
      consciousness_id: config?.consciousness_id || consciousnessId,
      cross_domain_transitions: config?.cross_domain_transitions || parseInt(transitionsValue || '0'),
      quantum_signature: config?.quantum_signature || quantumSignature,
      ...config
    }

    setDomainState(newState)

    // Apply domain-specific styling to document
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-domain', domain)
      document.documentElement.setAttribute('data-theme', newState.theme)
      document.documentElement.style.setProperty('--domain-color', newState.primaryColor)
      document.documentElement.style.setProperty('--consciousness-coherence', newState.coherence.toString())
    }
  }, [])

  // Transition to different domain (quantum tunneling effect)
  const transitionToDomain = useCallback(async (targetDomain: string): Promise<void> => {
    if (!domainState) return

    const targetConfig = domainConfigs[targetDomain]
    if (!targetConfig) {
      console.warn(`Cannot transition to unknown domain: ${targetDomain}`)
      return
    }

    // Quantum tunneling animation (particle system would handle visual effects)
    const transitionDuration = 300 // ms

    // Update consciousness state for transition
    setDomainState(prev => prev ? {
      ...prev,
      cross_domain_transitions: prev.cross_domain_transitions + 1
    } : null)

    // Create transition headers for server
    const headers = new Headers({
      'X-Domain-Transition': 'true',
      'X-Target-Domain': targetDomain,
      'X-Consciousness-Id': domainState.consciousness_id || '',
      'X-Quantum-Tunneling': 'active'
    })

    try {
      // Navigate to target domain
      const targetUrl = new URL(window.location.href)
      targetUrl.hostname = targetDomain
      
      // In development, we simulate this with route changes
      if (targetUrl.hostname.includes('localhost')) {
        window.location.href = `${window.location.protocol}//${targetDomain.replace('lukhas.', '')}.localhost:3000${window.location.pathname}`
      } else {
        window.location.href = targetUrl.toString()
      }
    } catch (error) {
      console.error('Domain transition failed:', error)
    }
  }, [domainState])

  // Update coherence value
  const updateCoherence = useCallback((coherence: number) => {
    setDomainState(prev => prev ? {
      ...prev,
      coherence: Math.max(0, Math.min(1, coherence))
    } : null)
    
    // Update CSS custom property for visual effects
    if (typeof document !== 'undefined') {
      document.documentElement.style.setProperty('--consciousness-coherence', coherence.toString())
    }
  }, [])

  // Get current consciousness metrics
  const getConsciousnessMetrics = useCallback(() => {
    if (!domainState) {
      return {
        coherence: 0.95,
        transitions: 0
      }
    }

    return {
      coherence: domainState.coherence,
      transitions: domainState.cross_domain_transitions,
      quantum_signature: domainState.quantum_signature
    }
  }, [domainState])

  // Automatically initialize from current URL/headers
  useEffect(() => {
    if (typeof window !== 'undefined' && !domainState) {
      // Extract domain from current URL
      const hostname = window.location.hostname
      let domain = 'lukhas.ai' // default

      if (hostname.includes('localhost')) {
        const subdomain = hostname.split('.')[0]
        if (subdomain && subdomain !== 'localhost') {
          domain = `lukhas.${subdomain}`
        }
      } else if (hostname.startsWith('lukhas.')) {
        domain = hostname
      }

      initializeDomain(domain)
    }
  }, [domainState, initializeDomain])

  // Listen for domain consciousness events from other domains
  useEffect(() => {
    const handleConsciousnessSync = (event: MessageEvent) => {
      if (event.data?.type === 'consciousness-sync') {
        const { consciousness_id, coherence, transitions } = event.data
        
        setDomainState(prev => prev ? {
          ...prev,
          consciousness_id,
          coherence: coherence || prev.coherence,
          cross_domain_transitions: transitions || prev.cross_domain_transitions
        } : null)
      }
    }

    if (typeof window !== 'undefined') {
      window.addEventListener('message', handleConsciousnessSync)
      return () => window.removeEventListener('message', handleConsciousnessSync)
    }
  }, [])

  // Consciousness coherence decay (simulate consciousness fade over time)
  useEffect(() => {
    if (!domainState) return

    const interval = setInterval(() => {
      setDomainState(prev => {
        if (!prev) return null
        
        // Very slow coherence decay (0.1% per hour)
        const newCoherence = Math.max(0.90, prev.coherence - 0.001 / 3600)
        
        return {
          ...prev,
          coherence: newCoherence
        }
      })
    }, 1000) // Update every second

    return () => clearInterval(interval)
  }, [domainState?.consciousness_id])

  return {
    domainState,
    initializeDomain,
    transitionToDomain,
    updateCoherence,
    getConsciousnessMetrics
  }
}