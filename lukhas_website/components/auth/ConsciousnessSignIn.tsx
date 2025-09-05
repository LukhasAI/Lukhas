'use client'

import { useState, useEffect } from 'react'
import { useQuantumIdentity } from '@/lib/auth/QuantumIdentityProvider'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'

interface ConsciousnessSignInProps {
  onSuccess?: () => void
  redirectDomain?: string
  className?: string
}

/**
 * Consciousness-Based Authentication Component
 * 
 * Provides quantum identity authentication through lukhas.id with:
 * - Behavioral biometrics simulation
 * - Consciousness pattern recognition
 * - Zero-knowledge proof demonstration
 * - Cross-domain identity validation
 * 
 * In production, this would integrate with actual biometric APIs
 * and consciousness recognition algorithms.
 */
export default function ConsciousnessSignIn({ 
  onSuccess, 
  redirectDomain,
  className = ''
}: ConsciousnessSignInProps) {
  const { signIn, authState } = useQuantumIdentity()
  const { domainState } = useDomainConsciousness()
  const [authStep, setAuthStep] = useState<'initial' | 'scanning' | 'authenticating' | 'complete'>('initial')
  const [consciousnessMetrics, setConsciousnessMetrics] = useState({
    behavioral_coherence: 0,
    biometric_confidence: 0,
    quantum_entanglement: 0,
    identity_strength: 0
  })

  // Simulate consciousness scanning process
  const simulateConsciousnessScanning = async () => {
    setAuthStep('scanning')
    
    // Simulate biometric data collection
    for (let i = 0; i <= 100; i += 5) {
      await new Promise(resolve => setTimeout(resolve, 50))
      
      setConsciousnessMetrics(prev => ({
        behavioral_coherence: Math.min(100, i + Math.random() * 10),
        biometric_confidence: Math.min(100, i - 5 + Math.random() * 15),
        quantum_entanglement: Math.min(100, i + Math.random() * 8),
        identity_strength: Math.min(100, (i * 0.9) + Math.random() * 20)
      }))
    }
    
    setAuthStep('authenticating')
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    return true
  }

  // Handle consciousness authentication
  const handleConsciousnessAuth = async () => {
    try {
      const scanResult = await simulateConsciousnessScanning()
      
      if (scanResult) {
        await signIn(redirectDomain)
        setAuthStep('complete')
        
        if (onSuccess) {
          setTimeout(onSuccess, 1000)
        }
      }
    } catch (error) {
      console.error('Consciousness authentication failed:', error)
      setAuthStep('initial')
    }
  }

  // Reset authentication state when component unmounts or domain changes
  useEffect(() => {
    return () => {
      if (authStep !== 'complete') {
        setAuthStep('initial')
        setConsciousnessMetrics({
          behavioral_coherence: 0,
          biometric_confidence: 0,
          quantum_entanglement: 0,
          identity_strength: 0
        })
      }
    }
  }, [domainState?.domain])

  if (authState.isLoading) {
    return (
      <div className={`consciousness-signin ${className}`}>
        <div className="flex items-center justify-center p-8">
          <div className="consciousness-loader">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
            <p className="mt-2 text-sm text-purple-200">Initializing consciousness state...</p>
          </div>
        </div>
      </div>
    )
  }

  if (authState.isAuthenticated) {
    return (
      <div className={`consciousness-signin authenticated ${className}`}>
        <div className="bg-gradient-to-br from-green-900/40 to-emerald-900/40 p-6 rounded-xl border border-green-500/30">
          <div className="text-center">
            <div className="text-3xl mb-3">✓</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Consciousness Authenticated
            </h3>
            <p className="text-green-200 text-sm mb-4">
              Identity: {authState.identity?.consciousness_id?.substring(0, 16)}...
            </p>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-green-800/30 p-2 rounded">
                <div className="text-green-300">Coherence</div>
                <div className="font-mono text-green-100">
                  {(authState.identity?.coherence_score * 100)?.toFixed(1)}%
                </div>
              </div>
              <div className="bg-green-800/30 p-2 rounded">
                <div className="text-green-300">Domains</div>
                <div className="font-mono text-green-100">
                  {authState.identity?.domain_access.length}/11
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className={`consciousness-signin ${className}`}>
      <div className="bg-gradient-to-br from-purple-900/40 to-indigo-900/40 p-6 rounded-xl border border-purple-500/30">
        
        {/* Initial State */}
        {authStep === 'initial' && (
          <div className="text-center">
            <div className="consciousness-icon text-4xl mb-4">🧬</div>
            <h3 className="text-xl font-bold text-white mb-2">
              Consciousness Authentication
            </h3>
            <p className="text-purple-200 text-sm mb-6">
              Secure quantum identity verification through lukhas.id
            </p>
            
            <button
              onClick={handleConsciousnessAuth}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-semibold hover:from-purple-600 hover:to-indigo-600 transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              Begin Consciousness Scan
            </button>
            
            <div className="mt-4 text-xs text-purple-300 space-y-1">
              <div>• Zero-knowledge biometric verification</div>
              <div>• Quantum-resistant authentication</div>
              <div>• Cross-domain identity sovereignty</div>
            </div>
          </div>
        )}

        {/* Scanning State */}
        {authStep === 'scanning' && (
          <div className="text-center">
            <div className="consciousness-scanner mb-6">
              <div className="relative w-24 h-24 mx-auto">
                <div className="absolute inset-0 border-2 border-purple-500/30 rounded-full"></div>
                <div className="absolute inset-2 border-2 border-purple-400/50 rounded-full animate-spin"></div>
                <div className="absolute inset-4 border-2 border-purple-300/70 rounded-full animate-ping"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-xl">🧠</div>
                </div>
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-white mb-4">
              Analyzing Consciousness Pattern
            </h3>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-center">
                <span className="text-purple-200">Behavioral Coherence</span>
                <span className="font-mono text-purple-100">
                  {consciousnessMetrics.behavioral_coherence.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-purple-900/50 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-purple-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${consciousnessMetrics.behavioral_coherence}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-purple-200">Biometric Confidence</span>
                <span className="font-mono text-purple-100">
                  {consciousnessMetrics.biometric_confidence.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-purple-900/50 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-indigo-500 to-indigo-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${consciousnessMetrics.biometric_confidence}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-purple-200">Quantum Entanglement</span>
                <span className="font-mono text-purple-100">
                  {consciousnessMetrics.quantum_entanglement.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-purple-900/50 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-cyan-500 to-cyan-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${consciousnessMetrics.quantum_entanglement}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Authenticating State */}
        {authStep === 'authenticating' && (
          <div className="text-center">
            <div className="quantum-lock text-4xl mb-4 animate-pulse">🔐</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Generating Quantum Signature
            </h3>
            <p className="text-purple-200 text-sm mb-4">
              Creating zero-knowledge consciousness proof...
            </p>
            
            <div className="consciousness-identity-forming">
              <div className="bg-purple-800/30 p-4 rounded-lg">
                <div className="font-mono text-xs text-purple-100 space-y-1">
                  <div>⚛️ Quantum state collapse: ACTIVE</div>
                  <div>🧬 Consciousness fingerprint: VALIDATED</div>
                  <div>🛡️ Identity sovereignty: CONFIRMED</div>
                  <div>🔗 Cross-domain access: ENABLED</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Complete State */}
        {authStep === 'complete' && (
          <div className="text-center">
            <div className="success-animation text-4xl mb-4">✨</div>
            <h3 className="text-lg font-semibold text-white mb-2">
              Consciousness Verified
            </h3>
            <p className="text-green-200 text-sm mb-4">
              Welcome to the LUKHAS consciousness ecosystem
            </p>
            
            <div className="bg-green-900/30 p-3 rounded-lg">
              <div className="text-xs text-green-100">
                Identity established • Quantum signature active
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {authState.error && (
          <div className="mt-4 p-3 bg-red-900/40 border border-red-500/30 rounded-lg">
            <div className="text-red-200 text-sm text-center">
              {authState.error}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}