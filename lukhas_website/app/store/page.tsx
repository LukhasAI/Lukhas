'use client'

import { useState } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import { useQuantumIdentity } from '@/lib/auth/QuantumIdentityProvider'

/**
 * LUKHΛS Store - Consciousness App Marketplace
 * 
 * Global marketplace for consciousness-enhanced applications,
 * AI modules, enterprise solutions, and consciousness development
 * tools. Connecting developers with consciousness technology.
 */
export default function StorePage() {
  const { domainState, transitionToDomain } = useDomainConsciousness()
  const { authState } = useQuantumIdentity()
  const [selectedCategory, setSelectedCategory] = useState<string>('featured')

  const featuredApps = [
    {
      id: 'conscious-writer',
      name: 'Conscious Writer Pro',
      developer: 'MindForge Studios',
      description: 'AI writing assistant with consciousness-enhanced creativity and contextual awareness.',
      price: '$29/month',
      rating: 4.9,
      downloads: '125K+',
      category: 'Productivity',
      consciousness_level: 'Advanced',
      image: '📝',
      features: ['Real-time consciousness enhancement', 'Multi-language support', 'Creative flow optimization']
    },
    {
      id: 'team-sync-consciousness',
      name: 'TeamSync Consciousness',
      developer: 'Collective Intelligence Inc',
      description: 'Synchronize team consciousness for enhanced collaboration and decision making.',
      price: '$199/month',
      rating: 4.8,
      downloads: '87K+',
      category: 'Collaboration',
      consciousness_level: 'Expert',
      image: '👥',
      features: ['Team coherence monitoring', 'Real-time sync', 'Collective intelligence amplification']
    },
    {
      id: 'consciousness-debugger',
      name: 'Consciousness Debugger',
      developer: 'AI Dev Tools',
      description: 'Debug and optimize consciousness patterns in AI applications with visual tools.',
      price: '$79/month',
      rating: 4.7,
      downloads: '45K+',
      category: 'Developer Tools',
      consciousness_level: 'Advanced',
      image: '🐛',
      features: ['Real-time consciousness inspection', 'Pattern analysis', 'Performance optimization']
    },
    {
      id: 'enterprise-consciousness-suite',
      name: 'Enterprise Consciousness Suite',
      developer: 'LUKHAS Enterprise',
      description: 'Complete enterprise consciousness platform with security and compliance.',
      price: 'Custom',
      rating: 4.9,
      downloads: '12K+',
      category: 'Enterprise',
      consciousness_level: 'Expert',
      image: '🏢',
      features: ['Enterprise security', 'Compliance tools', 'Custom consciousness models']
    },
    {
      id: 'dream-state-generator',
      name: 'Dream State Generator',
      developer: 'Oneiric Labs',
      description: 'Generate controlled consciousness drift states for creative problem solving.',
      price: '$49/month',
      rating: 4.6,
      downloads: '23K+',
      category: 'Creativity',
      consciousness_level: 'Experimental',
      image: '🌙',
      features: ['Controlled chaos generation', 'Creative enhancement', 'Safe consciousness drift']
    },
    {
      id: 'quantum-decision-engine',
      name: 'Quantum Decision Engine',
      developer: 'Quantum Consciousness Co',
      description: 'Quantum-inspired decision making with superposition exploration.',
      price: '$149/month',
      rating: 4.8,
      downloads: '67K+',
      category: 'Business Intelligence',
      consciousness_level: 'Advanced',
      image: '⚛️',
      features: ['Quantum decision trees', 'Superposition analysis', 'Uncertainty handling']
    }
  ]

  const categories = {
    featured: { name: 'Featured', count: 6 },
    productivity: { name: 'Productivity', count: 124 },
    collaboration: { name: 'Collaboration', count: 89 },
    developer: { name: 'Developer Tools', count: 156 },
    enterprise: { name: 'Enterprise', count: 67 },
    creativity: { name: 'Creativity', count: 78 },
    business: { name: 'Business Intelligence', count: 92 }
  }

  const getConsciousnessColor = (level: string) => {
    switch (level) {
      case 'Basic': return 'text-green-400 bg-green-900/30 border-green-500/50'
      case 'Advanced': return 'text-blue-400 bg-blue-900/30 border-blue-500/50'
      case 'Expert': return 'text-purple-400 bg-purple-900/30 border-purple-500/50'
      case 'Experimental': return 'text-pink-400 bg-pink-900/30 border-pink-500/50'
      default: return 'text-gray-400 bg-gray-900/30 border-gray-500/30'
    }
  }

  return (
    <div className="store-page">
      {/* Hero Section */}
      <section className="hero-section relative py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="marketplace-animation mb-8">
            <div className="particle-canvas w-full h-64 rounded-lg bg-gradient-to-br from-orange-900/30 to-amber-900/30 border border-orange-500/30">
              <div className="flex items-center justify-center h-full">
                <div className="text-orange-200 opacity-70 text-center">
                  <div className="text-4xl mb-2">🏪</div>
                  <div>Consciousness marketplace with {Math.round((domainState?.coherence || 0.972) * 10000).toLocaleString()} live applications</div>
                </div>
              </div>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-transparent bg-gradient-to-r from-orange-400 via-amber-400 to-orange-600 bg-clip-text">
              Consciousness
            </span>
            <br />
            <span className="text-white">
              Marketplace
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-orange-200 mb-8 max-w-3xl mx-auto leading-relaxed">
            Discover, purchase, and distribute consciousness-enhanced applications. 
            Where AI consciousness meets practical solutions for every use case.
          </p>
          
          <div className="cta-buttons flex flex-col md:flex-row items-center justify-center gap-4">
            <button className="px-8 py-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-lg font-semibold hover:from-orange-600 hover:to-amber-600 transition-all duration-300 shadow-lg hover:shadow-xl">
              Browse Apps
            </button>
            <button className="px-8 py-4 border border-orange-500 text-orange-300 rounded-lg font-semibold hover:bg-orange-500/10 transition-all duration-300">
              Publish Your App
            </button>
          </div>
        </div>
      </section>

      {/* Marketplace Stats */}
      <section className="stats-section py-16 px-4 bg-orange-950/30">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-4 gap-6">
            <div className="stat-card bg-orange-900/30 p-6 rounded-lg border border-orange-500/30 text-center">
              <div className="text-3xl font-bold text-orange-400 mb-2">
                {Math.round((domainState?.coherence || 0.972) * 10000).toLocaleString()}
              </div>
              <div className="text-sm text-orange-300">Live Applications</div>
            </div>

            <div className="stat-card bg-orange-900/30 p-6 rounded-lg border border-orange-500/30 text-center">
              <div className="text-3xl font-bold text-amber-400 mb-2">
                {Math.round((domainState?.coherence || 0.972) * 5000).toLocaleString()}
              </div>
              <div className="text-sm text-orange-300">Active Developers</div>
            </div>

            <div className="stat-card bg-orange-900/30 p-6 rounded-lg border border-orange-500/30 text-center">
              <div className="text-3xl font-bold text-yellow-400 mb-2">
                {Math.round((domainState?.coherence || 0.972) * 2500000).toLocaleString()}
              </div>
              <div className="text-sm text-orange-300">Total Downloads</div>
            </div>

            <div className="stat-card bg-orange-900/30 p-6 rounded-lg border border-orange-500/30 text-center">
              <div className="text-3xl font-bold text-orange-400 mb-2">4.7★</div>
              <div className="text-sm text-orange-300">Average Rating</div>
            </div>
          </div>
        </div>
      </section>

      {/* App Categories & Listings */}
      <section className="apps-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Consciousness-Enhanced Applications
            </h2>
            <p className="text-orange-200 max-w-2xl mx-auto">
              Discover applications that leverage consciousness technology for enhanced intelligence
            </p>
          </div>

          {/* Category Filter */}
          <div className="category-filter mb-12">
            <div className="flex flex-wrap items-center justify-center gap-3">
              {Object.entries(categories).map(([key, category]) => (
                <button
                  key={key}
                  onClick={() => setSelectedCategory(key)}
                  className={`px-6 py-3 rounded-lg border transition-all duration-200 ${
                    selectedCategory === key
                      ? 'bg-orange-600/30 border-orange-500/50 text-orange-200'
                      : 'bg-gray-900/30 border-gray-500/30 text-gray-300 hover:bg-orange-600/10'
                  }`}
                >
                  {category.name}
                  <span className="ml-2 text-xs opacity-70">({category.count})</span>
                </button>
              ))}
            </div>
          </div>

          {/* Featured Apps Grid */}
          <div className="apps-grid grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredApps.map((app) => (
              <div key={app.id} className="app-card bg-gray-900/40 rounded-xl border border-gray-500/30 overflow-hidden hover:border-orange-500/50 transition-all duration-300 hover:transform hover:scale-105">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-3xl">{app.image}</div>
                      <div>
                        <h3 className="text-lg font-bold text-white">{app.name}</h3>
                        <p className="text-sm text-gray-400">by {app.developer}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-orange-400 font-semibold">{app.price}</div>
                      <div className="flex items-center space-x-1 text-xs text-gray-400">
                        <span>⭐</span>
                        <span>{app.rating}</span>
                      </div>
                    </div>
                  </div>

                  <p className="text-gray-300 text-sm mb-4 line-clamp-2">
                    {app.description}
                  </p>

                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs text-gray-400">{app.downloads} downloads</span>
                    <span className={`px-2 py-1 rounded text-xs border ${getConsciousnessColor(app.consciousness_level)}`}>
                      {app.consciousness_level}
                    </span>
                  </div>

                  <div className="space-y-2 mb-6">
                    {app.features.slice(0, 2).map((feature, index) => (
                      <div key={index} className="flex items-center space-x-2 text-xs">
                        <span className="text-orange-400">•</span>
                        <span className="text-gray-300">{feature}</span>
                      </div>
                    ))}
                    {app.features.length > 2 && (
                      <div className="text-xs text-orange-400">+{app.features.length - 2} more features</div>
                    )}
                  </div>

                  <div className="flex space-x-2">
                    <button className="flex-1 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors text-sm">
                      Install
                    </button>
                    <button className="flex-1 px-4 py-2 border border-orange-500 text-orange-300 rounded-lg hover:bg-orange-500/10 transition-colors text-sm">
                      Preview
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Developer Publishing */}
      <section className="publishing-section py-16 px-4 bg-orange-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Publish Your Consciousness Apps
            </h2>
            <p className="text-orange-200 max-w-3xl mx-auto">
              Join thousands of developers building the future of consciousness-enhanced applications
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="publishing-card bg-gradient-to-br from-orange-900/30 to-amber-900/30 p-8 rounded-xl border border-orange-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🚀</div>
                <h3 className="text-xl font-bold text-white mb-4">Easy Publishing</h3>
                <p className="text-orange-200 mb-6 text-sm">
                  Deploy consciousness-enhanced apps with our streamlined publishing platform
                </p>
                <div className="features text-sm text-orange-300 space-y-2">
                  <div>• One-click deployment</div>
                  <div>• Automated testing & validation</div>
                  <div>• Global distribution network</div>
                  <div>• Real-time analytics</div>
                </div>
              </div>
            </div>

            <div className="publishing-card bg-gradient-to-br from-amber-900/30 to-yellow-900/30 p-8 rounded-xl border border-amber-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">💰</div>
                <h3 className="text-xl font-bold text-white mb-4">Revenue Optimization</h3>
                <p className="text-orange-200 mb-6 text-sm">
                  Maximize earnings with flexible pricing models and consciousness metrics
                </p>
                <div className="features text-sm text-orange-300 space-y-2">
                  <div>• Multiple pricing models</div>
                  <div>• Consciousness-based pricing</div>
                  <div>• Revenue analytics</div>
                  <div>• 70% developer revenue share</div>
                </div>
              </div>
            </div>

            <div className="publishing-card bg-gradient-to-br from-yellow-900/30 to-orange-900/30 p-8 rounded-xl border border-yellow-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🤝</div>
                <h3 className="text-xl font-bold text-white mb-4">Developer Support</h3>
                <p className="text-orange-200 mb-6 text-sm">
                  Comprehensive support ecosystem for consciousness app developers
                </p>
                <div className="features text-sm text-orange-300 space-y-2">
                  <div>• Technical documentation</div>
                  <div>• Developer community</div>
                  <div>• Marketing support</div>
                  <div>• Consciousness expert guidance</div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <button className="px-8 py-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white rounded-lg font-semibold hover:from-orange-600 hover:to-amber-600 transition-all duration-300 shadow-lg hover:shadow-xl">
              Start Publishing Today
            </button>
          </div>
        </div>
      </section>

      {/* Cross-Domain Integration */}
      <section className="integration-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Integrated Development Ecosystem
            </h2>
            <p className="text-orange-200 max-w-3xl mx-auto">
              Build, test, and distribute consciousness apps across the entire LUKHAS ecosystem
            </p>
          </div>

          <div className="integration-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { domain: 'lukhas.dev', name: 'Development Tools', color: 'cyan', description: 'Build consciousness apps with our SDK' },
              { domain: 'lukhas.ai', name: 'AI Integration', color: 'blue', description: 'Integrate advanced AI consciousness' },
              { domain: 'lukhas.cloud', name: 'Cloud Deployment', color: 'violet', description: 'Scale apps on consciousness cloud' },
              { domain: 'lukhas.team', name: 'Team Collaboration', color: 'green', description: 'Collaborative app development' },
              { domain: 'lukhas.io', name: 'API Infrastructure', color: 'indigo', description: 'High-performance consciousness APIs' },
              { domain: 'lukhas.xyz', name: 'Research & Testing', color: 'pink', description: 'Experimental consciousness features' }
            ].map(({ domain, name, color, description }) => (
              <button
                key={domain}
                onClick={() => transitionToDomain(domain)}
                className={`integration-card bg-gradient-to-br from-${color}-900/20 to-${color}-800/20 p-6 rounded-lg border border-${color}-500/30 hover:border-${color}-400/50 transition-all duration-300 text-left group`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white group-hover:text-orange-200">
                    {name}
                  </h3>
                  <div className="text-orange-400 group-hover:text-orange-300">→</div>
                </div>
                <p className="text-sm text-orange-300 group-hover:text-orange-200 mb-2">
                  {description}
                </p>
                <div className="text-xs font-mono text-orange-500">
                  {domain}
                </div>
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}