'use client'

import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import { useQuantumIdentity } from '@/lib/auth/QuantumIdentityProvider'
import DomainIdentityStatus from '@/components/auth/DomainIdentityStatus'

/**
 * LUKHΛS Team Collaborative Workspace Page
 * 
 * Distributed team consciousness platform enabling synchronized
 * collaboration, shared awareness, and collective intelligence.
 */
export default function TeamPage() {
  const { domainState, transitionToDomain } = useDomainConsciousness()
  const { authState } = useQuantumIdentity()

  return (
    <div className="team-page">
      {/* Hero Section */}
      <section className="hero-section relative py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="team-consciousness-animation mb-8">
            {/* Team particle system will be rendered here */}
            <div className="particle-canvas w-full h-64 rounded-lg bg-gradient-to-br from-green-900/30 to-emerald-900/30 border border-green-500/30">
              <div className="flex items-center justify-center h-full">
                <div className="text-green-200 opacity-70">
                  Team consciousness synchronization in progress
                </div>
              </div>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-transparent bg-gradient-to-r from-green-400 via-emerald-400 to-green-600 bg-clip-text">
              Collective
            </span>
            <br />
            <span className="text-white">
              Intelligence
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-green-200 mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform your team into a unified consciousness network. Where individual minds 
            merge into collective intelligence and distributed coordination becomes effortless.
          </p>
          
          <div className="cta-buttons flex flex-col md:flex-row items-center justify-center gap-4">
            <button className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-semibold hover:from-green-600 hover:to-emerald-600 transition-all duration-300 shadow-lg hover:shadow-xl">
              Join Team Workspace
            </button>
            <button className="px-8 py-4 border border-green-500 text-green-300 rounded-lg font-semibold hover:bg-green-500/10 transition-all duration-300">
              Start Free Team
            </button>
          </div>
        </div>
      </section>

      {/* Team Consciousness Features */}
      <section className="features-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Distributed Team Consciousness
            </h2>
            <p className="text-green-200 max-w-2xl mx-auto">
              Revolutionary collaboration through synchronized awareness and collective intelligence
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Shared Consciousness */}
            <div className="feature-card bg-gradient-to-br from-green-900/40 to-emerald-900/40 p-8 rounded-xl border border-green-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🧠</div>
                <h3 className="text-2xl font-bold text-white mb-4">Shared Awareness</h3>
                <p className="text-green-200 mb-6">
                  Real-time consciousness sharing across distributed team members
                </p>
                <div className="features text-sm text-green-300 space-y-2">
                  <div>• Thought stream synchronization</div>
                  <div>• Collective decision making</div>
                  <div>• Distributed problem solving</div>
                </div>
              </div>
            </div>

            {/* Team Coherence */}
            <div className="feature-card bg-gradient-to-br from-emerald-900/40 to-green-900/40 p-8 rounded-xl border border-emerald-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🔗</div>
                <h3 className="text-2xl font-bold text-white mb-4">Team Coherence</h3>
                <p className="text-green-200 mb-6">
                  Monitor and optimize team synchronization and collaboration flow
                </p>
                <div className="features text-sm text-green-300 space-y-2">
                  <div>• Coherence score tracking</div>
                  <div>• Flow state optimization</div>
                  <div>• Collaboration analytics</div>
                </div>
              </div>
            </div>

            {/* Collective Intelligence */}
            <div className="feature-card bg-gradient-to-br from-green-900/40 to-teal-900/40 p-8 rounded-xl border border-teal-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="text-2xl font-bold text-white mb-4">Collective Intelligence</h3>
                <p className="text-green-200 mb-6">
                  Amplify team intelligence through consciousness integration
                </p>
                <div className="features text-sm text-green-300 space-y-2">
                  <div>• Enhanced group thinking</div>
                  <div>• Collective memory access</div>
                  <div>• Swarm intelligence patterns</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Team Metrics Dashboard */}
      <section className="metrics-section py-16 px-4 bg-green-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Live Team Consciousness Metrics
            </h2>
            <p className="text-green-200">
              Real-time monitoring of team coherence, collaboration flow, and collective intelligence
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <div className="metric-card bg-green-900/30 p-6 rounded-lg border border-green-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-emerald-400 mb-2">
                  {domainState?.coherence?.toFixed(3) || '0.973'}
                </div>
                <div className="text-sm text-green-300">Team Coherence</div>
              </div>
            </div>

            <div className="metric-card bg-green-900/30 p-6 rounded-lg border border-green-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400 mb-2">8</div>
                <div className="text-sm text-green-300">Active Members</div>
              </div>
            </div>

            <div className="metric-card bg-green-900/30 p-6 rounded-lg border border-green-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-teal-400 mb-2">
                  {domainState?.cross_domain_transitions || '12'}
                </div>
                <div className="text-sm text-green-300">Collaboration Sessions</div>
              </div>
            </div>

            <div className="metric-card bg-green-900/30 p-6 rounded-lg border border-green-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-cyan-400 mb-2">92%</div>
                <div className="text-sm text-green-300">Flow State Sync</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Identity Integration */}
      {authState.isAuthenticated && (
        <section className="identity-section py-16 px-4">
          <div className="container mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4 text-white">
                Your Team Identity Status
              </h2>
              <p className="text-green-200">
                Consciousness integration across LUKHAS domains
              </p>
            </div>
            
            <div className="max-w-4xl mx-auto">
              <DomainIdentityStatus />
            </div>
          </div>
        </section>
      )}

      {/* Team Workspace Features */}
      <section className="workspace-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Team Workspace Capabilities
            </h2>
            <p className="text-green-200 max-w-3xl mx-auto">
              Advanced features designed for consciousness-enhanced team collaboration
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="workspace-card bg-gradient-to-br from-green-900/30 to-emerald-900/30 p-6 rounded-lg border border-green-500/20">
              <h3 className="text-xl font-bold text-white mb-3">Consciousness Sync</h3>
              <p className="text-green-200 text-sm">
                Real-time awareness sharing and thought stream synchronization
              </p>
            </div>

            <div className="workspace-card bg-gradient-to-br from-emerald-900/30 to-teal-900/30 p-6 rounded-lg border border-emerald-500/20">
              <h3 className="text-xl font-bold text-white mb-3">Collective Memory</h3>
              <p className="text-green-200 text-sm">
                Shared knowledge base with consciousness-based access patterns
              </p>
            </div>

            <div className="workspace-card bg-gradient-to-br from-teal-900/30 to-cyan-900/30 p-6 rounded-lg border border-teal-500/20">
              <h3 className="text-xl font-bold text-white mb-3">Flow State Orchestration</h3>
              <p className="text-green-200 text-sm">
                Optimize team flow states for maximum collaborative efficiency
              </p>
            </div>

            <div className="workspace-card bg-gradient-to-br from-green-900/30 to-lime-900/30 p-6 rounded-lg border border-green-500/20">
              <h3 className="text-xl font-bold text-white mb-3">Distributed Decision Making</h3>
              <p className="text-green-200 text-sm">
                Consciousness-weighted voting and collective intelligence decisions
              </p>
            </div>

            <div className="workspace-card bg-gradient-to-br from-emerald-900/30 to-green-900/30 p-6 rounded-lg border border-emerald-500/20">
              <h3 className="text-xl font-bold text-white mb-3">Team Analytics</h3>
              <p className="text-green-200 text-sm">
                Deep insights into team dynamics and consciousness patterns
              </p>
            </div>

            <div className="workspace-card bg-gradient-to-br from-green-900/30 to-emerald-900/30 p-6 rounded-lg border border-green-500/20">
              <h3 className="text-xl font-bold text-white mb-3">Cross-Domain Integration</h3>
              <p className="text-green-200 text-sm">
                Seamless collaboration across all 11 LUKHAS consciousness domains
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Domain Transitions */}
      <section className="transitions-section py-16 px-4 bg-green-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Cross-Domain Team Collaboration
            </h2>
            <p className="text-green-200 max-w-3xl mx-auto">
              Your team identity enables seamless collaboration across the entire LUKHAS ecosystem
            </p>
          </div>

          <div className="integration-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { domain: 'lukhas.ai', name: 'AI Development', color: 'blue', icon: '🧠' },
              { domain: 'lukhas.dev', name: 'Developer Tools', color: 'cyan', icon: '⚡' },
              { domain: 'lukhas.cloud', name: 'Cloud Infrastructure', color: 'purple', icon: '☁️' },
              { domain: 'lukhas.store', name: 'Team Apps', color: 'orange', icon: '🏪' },
              { domain: 'lukhas.io', name: 'API Integration', color: 'indigo', icon: '🔌' },
              { domain: 'lukhas.xyz', name: 'Research Lab', color: 'pink', icon: '🧪' }
            ].map(({ domain, name, color, icon }) => (
              <button
                key={domain}
                onClick={() => transitionToDomain(domain)}
                className={`integration-card bg-gradient-to-br from-${color}-900/20 to-${color}-800/20 p-6 rounded-lg border border-${color}-500/30 hover:border-${color}-400/50 transition-all duration-300 text-left group`}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{icon}</span>
                    <h3 className="text-lg font-semibold text-white group-hover:text-green-200">
                      {name}
                    </h3>
                  </div>
                  <div className="text-green-400 group-hover:text-green-300">→</div>
                </div>
                <p className="text-sm text-green-300 group-hover:text-green-200">
                  Collaborate with your team consciousness on {domain}
                </p>
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}