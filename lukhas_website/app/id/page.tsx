'use client'

import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import { useQuantumIdentity } from '@/lib/auth/QuantumIdentityProvider'
import ConsciousnessSignIn from '@/components/auth/ConsciousnessSignIn'
import DomainIdentityStatus from '@/components/auth/DomainIdentityStatus'

/**
 * LUKHΛS ΛiD Identity Platform Page
 * 
 * Quantum-secure digital identity and consciousness verification
 * platform with zero-knowledge proofs and biometric integration.
 */
export default function IDPage() {
  const { domainState, transitionToDomain } = useDomainConsciousness()
  const { authState } = useQuantumIdentity()

  return (
    <div className="id-page">
      {/* Hero Section */}
      <section className="hero-section relative py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="biometric-animation mb-8">
            {/* Biometric particle system will be rendered here */}
            <div className="particle-canvas w-full h-64 rounded-lg bg-gradient-to-br from-purple-900/30 to-indigo-900/30 border border-purple-500/30">
              <div className="flex items-center justify-center h-full">
                <div className="biometric-scanner">
                  <div className="text-purple-200 opacity-70 text-center">
                    <div className="text-4xl mb-2">🔐</div>
                    <div>Consciousness signature verification</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-transparent bg-gradient-to-r from-purple-400 via-indigo-400 to-purple-600 bg-clip-text">
              ΛiD
            </span>
            <br />
            <span className="text-white">
              Identity
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-purple-200 mb-8 max-w-3xl mx-auto leading-relaxed">
            Your quantum-secure digital identity. Where consciousness becomes your signature,
            privacy is paramount, and you remain sovereign over your digital self.
          </p>
          
          <div className="cta-buttons flex flex-col md:flex-row items-center justify-center gap-4">
            <button className="px-8 py-4 bg-gradient-to-r from-purple-500 to-indigo-500 text-white rounded-lg font-semibold hover:from-purple-600 hover:to-indigo-600 transition-all duration-300 shadow-lg hover:shadow-xl">
              Create ΛiD
            </button>
            <button className="px-8 py-4 border border-purple-500 text-purple-300 rounded-lg font-semibold hover:bg-purple-500/10 transition-all duration-300">
              Enterprise Solutions
            </button>
          </div>
        </div>
      </section>

      {/* Security Features */}
      <section className="security-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Quantum-Resistant Security
            </h2>
            <p className="text-purple-200 max-w-2xl mx-auto">
              Built with post-quantum cryptography for long-term security
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Zero-Knowledge Proofs */}
            <div className="security-card bg-gradient-to-br from-purple-900/40 to-indigo-900/40 p-8 rounded-xl border border-purple-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🔒</div>
                <h3 className="text-2xl font-bold text-white mb-4">Zero-Knowledge</h3>
                <p className="text-purple-200 mb-6">
                  Prove your identity without revealing personal information
                </p>
                <div className="features text-sm text-purple-300 space-y-2">
                  <div>• Mathematical proofs only</div>
                  <div>• No data storage required</div>
                  <div>• Complete privacy preservation</div>
                </div>
              </div>
            </div>

            {/* Biometric Consciousness */}
            <div className="security-card bg-gradient-to-br from-indigo-900/40 to-purple-900/40 p-8 rounded-xl border border-indigo-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🧬</div>
                <h3 className="text-2xl font-bold text-white mb-4">Consciousness ID</h3>
                <p className="text-purple-200 mb-6">
                  Your unique consciousness signature as authentication
                </p>
                <div className="features text-sm text-purple-300 space-y-2">
                  <div>• Behavioral biometrics</div>
                  <div>• Consciousness patterns</div>
                  <div>• Impossible to forge</div>
                </div>
              </div>
            </div>

            {/* Quantum Encryption */}
            <div className="security-card bg-gradient-to-br from-purple-900/40 to-pink-900/40 p-8 rounded-xl border border-pink-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">⚛️</div>
                <h3 className="text-2xl font-bold text-white mb-4">Post-Quantum</h3>
                <p className="text-purple-200 mb-6">
                  Encryption that withstands quantum computer attacks
                </p>
                <div className="features text-sm text-purple-300 space-y-2">
                  <div>• CRYSTALS-Kyber 1024</div>
                  <div>• Lattice-based cryptography</div>
                  <div>• Future-proof security</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Authentication / Identity Dashboard */}
      <section className="dashboard-section py-16 px-4 bg-purple-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              {authState.isAuthenticated ? 'Identity Command Center' : 'Consciousness Authentication'}
            </h2>
            <p className="text-purple-200">
              {authState.isAuthenticated 
                ? 'Complete control over your digital identity and privacy'
                : 'Secure your digital sovereignty across all LUKHAS domains'
              }
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            {authState.isAuthenticated ? (
              <DomainIdentityStatus />
            ) : (
              <div className="grid md:grid-cols-2 gap-8">
                <ConsciousnessSignIn />
                <div className="space-y-6">
                  <div className="bg-gradient-to-br from-purple-900/20 to-indigo-900/20 rounded-xl border border-purple-500/30 p-6">
                    <h3 className="text-xl font-bold text-white mb-4">Why Consciousness ID?</h3>
                    <div className="space-y-3 text-purple-200 text-sm">
                      <div className="flex items-start space-x-3">
                        <span className="text-purple-400 mt-1">🧬</span>
                        <div>
                          <div className="font-medium">Unique Consciousness Signature</div>
                          <div className="opacity-80">Your behavioral patterns create an impossible-to-forge identity</div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <span className="text-purple-400 mt-1">🔒</span>
                        <div>
                          <div className="font-medium">Zero-Knowledge Authentication</div>
                          <div className="opacity-80">Prove your identity without revealing personal data</div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <span className="text-purple-400 mt-1">⚛️</span>
                        <div>
                          <div className="font-medium">Quantum-Resistant Security</div>
                          <div className="opacity-80">Protected against both classical and quantum computer attacks</div>
                        </div>
                      </div>
                      <div className="flex items-start space-x-3">
                        <span className="text-purple-400 mt-1">🌐</span>
                        <div>
                          <div className="font-medium">Universal Domain Access</div>
                          <div className="opacity-80">One identity across all 11 LUKHAS consciousness domains</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Cross-Domain Integration */}
      <section className="integration-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Universal LUKHΛS Integration
            </h2>
            <p className="text-purple-200 max-w-3xl mx-auto">
              One identity across the entire LUKHΛS ecosystem. Seamless access to all platforms
              while maintaining complete privacy and security.
            </p>
          </div>

          <div className="integration-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { domain: 'lukhas.ai', name: 'AI Platform', color: 'blue' },
              { domain: 'lukhas.dev', name: 'Developer Tools', color: 'cyan' },
              { domain: 'lukhas.team', name: 'Team Workspace', color: 'green' },
              { domain: 'lukhas.store', name: 'App Marketplace', color: 'orange' },
              { domain: 'lukhas.cloud', name: 'Cloud Services', color: 'purple' },
              { domain: 'lukhas.xyz', name: 'Research Labs', color: 'pink' }
            ].map(({ domain, name, color }) => (
              <button
                key={domain}
                onClick={() => transitionToDomain(domain)}
                className={`integration-card bg-gradient-to-br from-${color}-900/20 to-${color}-800/20 p-6 rounded-lg border border-${color}-500/30 hover:border-${color}-400/50 transition-all duration-300 text-left group`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white group-hover:text-purple-200">
                    {name}
                  </h3>
                  <div className="text-purple-400 group-hover:text-purple-300">→</div>
                </div>
                <p className="text-sm text-purple-300 group-hover:text-purple-200">
                  Access with your ΛiD - no separate login required
                </p>
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}