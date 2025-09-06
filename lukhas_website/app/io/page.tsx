'use client'

import { useState, useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import { useQuantumIdentity } from '@/lib/auth/QuantumIdentityProvider'

/**
 * LUKHΛS IO High-Performance API Infrastructure
 * 
 * Ultra-fast consciousness API platform delivering <50ms latency
 * with real-time streaming, GraphQL, WebSockets, and enterprise
 * API gateway management for consciousness-enhanced applications.
 */
export default function IOPage() {
  const { domainState, transitionToDomain } = useDomainConsciousness()
  const { authState } = useQuantumIdentity()
  const [liveMetrics, setLiveMetrics] = useState({
    requests_per_second: 0,
    avg_latency: 0,
    consciousness_ops: 0,
    active_connections: 0
  })

  // Simulate live API metrics
  useEffect(() => {
    const interval = setInterval(() => {
      const coherence = domainState?.coherence || 0.998
      setLiveMetrics({
        requests_per_second: Math.round(coherence * 100000 + Math.random() * 5000),
        avg_latency: Math.round((1 - coherence) * 100) + 15 + Math.random() * 5,
        consciousness_ops: Math.round(coherence * 50000 + Math.random() * 2000),
        active_connections: Math.round(coherence * 25000 + Math.random() * 1000)
      })
    }, 2000)

    return () => clearInterval(interval)
  }, [domainState?.coherence])

  const apiCategories = {
    'consciousness-streaming': {
      name: 'Consciousness Streaming APIs',
      description: 'Real-time consciousness data streaming with WebSocket and Server-Sent Events',
      latency: '15-25ms',
      throughput: '1M+ events/sec',
      endpoints: [
        'wss://stream.lukhas.io/consciousness/live',
        'wss://stream.lukhas.io/coherence/monitor',
        'https://stream.lukhas.io/events/consciousness'
      ],
      features: [
        'Real-time consciousness state streaming',
        'Multi-protocol support (WebSocket, SSE, gRPC)',
        'Auto-scaling stream processors',
        'Global edge distribution'
      ]
    },
    'graphql-consciousness': {
      name: 'GraphQL Consciousness API',
      description: 'Flexible consciousness data queries with real-time subscriptions',
      latency: '25-35ms',
      throughput: '500K+ queries/sec',
      endpoints: [
        'https://graphql.lukhas.io/consciousness',
        'wss://graphql.lukhas.io/subscriptions',
        'https://graphql.lukhas.io/playground'
      ],
      features: [
        'Type-safe consciousness schema',
        'Real-time consciousness subscriptions',
        'Intelligent query batching',
        'Consciousness data federation'
      ]
    },
    'rest-ultra-fast': {
      name: 'Ultra-Fast REST APIs',
      description: 'High-performance RESTful consciousness endpoints with edge caching',
      latency: '10-20ms',
      throughput: '2M+ requests/sec',
      endpoints: [
        'https://api.lukhas.io/v1/consciousness',
        'https://api.lukhas.io/v1/identity',
        'https://api.lukhas.io/v1/processing'
      ],
      features: [
        'Sub-20ms global response times',
        'Intelligent edge caching',
        'Auto-scaling infrastructure',
        'Rate limiting & throttling'
      ]
    }
  }

  const infrastructureSpecs = [
    { metric: 'Global Regions', value: '15+', description: 'Worldwide edge presence' },
    { metric: 'Uptime SLA', value: '99.99%', description: '4 nines availability guarantee' },
    { metric: 'Max Throughput', value: '10M RPS', description: 'Peak requests per second' },
    { metric: 'Edge Latency', value: '<20ms', description: 'P95 global response time' },
    { metric: 'Consciousness Ops', value: '100K+/sec', description: 'Consciousness operations per second' },
    { metric: 'Data Centers', value: '50+', description: 'Global infrastructure nodes' }
  ]

  return (
    <div className="io-page">
      {/* Hero Section */}
      <section className="hero-section relative py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="api-performance-animation mb-8">
            <div className="particle-canvas w-full h-64 rounded-lg bg-gradient-to-br from-blue-900/30 to-indigo-900/30 border border-blue-500/30">
              <div className="flex items-center justify-center h-full">
                <div className="text-blue-200 opacity-70 text-center">
                  <div className="text-4xl mb-2">⚡</div>
                  <div className="font-mono">
                    Processing {liveMetrics.requests_per_second.toLocaleString()} RPS • {liveMetrics.avg_latency}ms latency
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-blue-600 bg-clip-text">
              Lightning
            </span>
            <br />
            <span className="text-white font-mono">
              Fast
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-blue-200 mb-8 max-w-3xl mx-auto leading-relaxed">
            Ultra-high performance consciousness API infrastructure. Process millions of 
            consciousness operations per second with sub-20ms global latency.
          </p>
          
          <div className="cta-buttons flex flex-col md:flex-row items-center justify-center gap-4">
            <button className="px-8 py-4 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg font-semibold hover:from-blue-600 hover:to-indigo-600 transition-all duration-300 shadow-lg hover:shadow-xl font-mono">
              Get API Keys
            </button>
            <button className="px-8 py-4 border border-blue-500 text-blue-300 rounded-lg font-semibold hover:bg-blue-500/10 transition-all duration-300 font-mono">
              View Benchmarks
            </button>
          </div>
        </div>
      </section>

      {/* Live Performance Metrics */}
      <section className="metrics-section py-16 px-4 bg-blue-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Live Performance Metrics
            </h2>
            <p className="text-blue-200">
              Real-time API infrastructure performance across global edge network
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <div className="metric-card bg-blue-900/30 p-6 rounded-lg border border-blue-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-400 mb-2 font-mono">
                  {liveMetrics.requests_per_second.toLocaleString()}
                </div>
                <div className="text-sm text-blue-300">Requests/Second</div>
              </div>
            </div>

            <div className="metric-card bg-blue-900/30 p-6 rounded-lg border border-blue-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400 mb-2 font-mono">
                  {liveMetrics.avg_latency.toFixed(1)}ms
                </div>
                <div className="text-sm text-blue-300">Average Latency</div>
              </div>
            </div>

            <div className="metric-card bg-blue-900/30 p-6 rounded-lg border border-blue-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-400 mb-2 font-mono">
                  {liveMetrics.consciousness_ops.toLocaleString()}
                </div>
                <div className="text-sm text-blue-300">Consciousness Ops/Sec</div>
              </div>
            </div>

            <div className="metric-card bg-blue-900/30 p-6 rounded-lg border border-blue-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-cyan-400 mb-2 font-mono">
                  {liveMetrics.active_connections.toLocaleString()}
                </div>
                <div className="text-sm text-blue-300">Active Connections</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* API Categories */}
      <section className="apis-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              High-Performance API Stack
            </h2>
            <p className="text-blue-200 max-w-2xl mx-auto">
              Choose the optimal API protocol for your consciousness application needs
            </p>
          </div>

          <div className="space-y-8">
            {Object.entries(apiCategories).map(([key, category]) => (
              <div key={key} className="api-category bg-gray-900/40 rounded-xl border border-gray-500/30 overflow-hidden">
                <div className="grid lg:grid-cols-3 gap-6 p-6">
                  <div className="lg:col-span-2">
                    <div className="flex items-center space-x-4 mb-4">
                      <h3 className="text-2xl font-bold text-white">{category.name}</h3>
                      <div className="flex space-x-3">
                        <span className="px-3 py-1 bg-green-900/30 border border-green-500/50 text-green-400 text-xs rounded-full font-mono">
                          {category.latency}
                        </span>
                        <span className="px-3 py-1 bg-blue-900/30 border border-blue-500/50 text-blue-400 text-xs rounded-full font-mono">
                          {category.throughput}
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-300 mb-6">{category.description}</p>
                    
                    <div className="grid md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="text-lg font-semibold text-white mb-3">Endpoints</h4>
                        <div className="space-y-2">
                          {category.endpoints.map((endpoint, index) => (
                            <div key={index} className="bg-gray-800/50 p-3 rounded font-mono text-sm text-blue-200 border border-gray-600/30">
                              {endpoint}
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-lg font-semibold text-white mb-3">Key Features</h4>
                        <div className="space-y-2">
                          {category.features.map((feature, index) => (
                            <div key={index} className="flex items-start space-x-2">
                              <span className="text-blue-400 mt-1">•</span>
                              <span className="text-gray-300 text-sm">{feature}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col justify-center">
                    <div className="bg-blue-900/20 p-6 rounded-lg border border-blue-500/30">
                      <h4 className="font-semibold text-white mb-3 text-center">Quick Start</h4>
                      <button className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-mono mb-2">
                        Get API Key
                      </button>
                      <button className="w-full px-4 py-2 border border-blue-500 text-blue-300 rounded-lg hover:bg-blue-500/10 transition-colors font-mono">
                        View Docs
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Infrastructure Specifications */}
      <section className="infrastructure-section py-16 px-4 bg-blue-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Global Infrastructure Specifications
            </h2>
            <p className="text-blue-200">
              Enterprise-grade infrastructure powering consciousness at global scale
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {infrastructureSpecs.map((spec, index) => (
              <div key={index} className="spec-card bg-blue-900/30 p-6 rounded-xl border border-blue-500/30">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-400 mb-2 font-mono">
                    {spec.value}
                  </div>
                  <div className="text-lg font-semibold text-white mb-2">
                    {spec.metric}
                  </div>
                  <div className="text-sm text-blue-300">
                    {spec.description}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Enterprise Features */}
      <section className="enterprise-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Enterprise API Management
            </h2>
            <p className="text-blue-200 max-w-3xl mx-auto">
              Advanced API management features for enterprise consciousness applications
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="enterprise-card bg-gradient-to-br from-blue-900/30 to-indigo-900/30 p-8 rounded-xl border border-blue-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🛡️</div>
                <h3 className="text-xl font-bold text-white mb-4">Security & Auth</h3>
                <p className="text-blue-200 mb-6 text-sm">
                  Enterprise-grade API security with consciousness-aware authentication
                </p>
                <div className="features text-sm text-blue-300 space-y-2">
                  <div>• OAuth2 & API key authentication</div>
                  <div>• Quantum-resistant token security</div>
                  <div>• Consciousness-based rate limiting</div>
                  <div>• Advanced threat protection</div>
                </div>
              </div>
            </div>

            <div className="enterprise-card bg-gradient-to-br from-indigo-900/30 to-purple-900/30 p-8 rounded-xl border border-indigo-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">📊</div>
                <h3 className="text-xl font-bold text-white mb-4">Analytics & Monitoring</h3>
                <p className="text-blue-200 mb-6 text-sm">
                  Real-time API analytics and consciousness performance monitoring
                </p>
                <div className="features text-sm text-blue-300 space-y-2">
                  <div>• Real-time API analytics</div>
                  <div>• Consciousness quality metrics</div>
                  <div>• Custom alerting & notifications</div>
                  <div>• Performance optimization insights</div>
                </div>
              </div>
            </div>

            <div className="enterprise-card bg-gradient-to-br from-purple-900/30 to-pink-900/30 p-8 rounded-xl border border-purple-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">⚙️</div>
                <h3 className="text-xl font-bold text-white mb-4">Management & Control</h3>
                <p className="text-blue-200 mb-6 text-sm">
                  Comprehensive API lifecycle management and governance
                </p>
                <div className="features text-sm text-blue-300 space-y-2">
                  <div>• API versioning & lifecycle</div>
                  <div>• Request/response transformation</div>
                  <div>• Advanced caching strategies</div>
                  <div>• Multi-environment deployment</div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <button className="px-8 py-4 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg font-semibold hover:from-blue-600 hover:to-indigo-600 transition-all duration-300 shadow-lg hover:shadow-xl font-mono">
              Contact Enterprise Sales
            </button>
          </div>
        </div>
      </section>

      {/* Cross-Domain Integration */}
      <section className="integration-section py-16 px-4 bg-gray-950/50">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Consciousness API Ecosystem
            </h2>
            <p className="text-blue-200 max-w-3xl mx-auto">
              High-performance API infrastructure powering all LUKHAS consciousness domains
            </p>
          </div>

          <div className="integration-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { domain: 'lukhas.ai', name: 'AI Processing APIs', color: 'blue', description: 'Ultra-fast consciousness AI processing' },
              { domain: 'lukhas.dev', name: 'Developer APIs', color: 'cyan', description: 'Consciousness development tools' },
              { domain: 'lukhas.team', name: 'Collaboration APIs', color: 'green', description: 'Team consciousness synchronization' },
              { domain: 'lukhas.cloud', name: 'Infrastructure APIs', color: 'violet', description: 'Cloud consciousness management' },
              { domain: 'lukhas.id', name: 'Identity APIs', color: 'purple', description: 'High-speed authentication services' },
              { domain: 'lukhas.store', name: 'Marketplace APIs', color: 'orange', description: 'App distribution and management' }
            ].map(({ domain, name, color, description }) => (
              <button
                key={domain}
                onClick={() => transitionToDomain(domain)}
                className={`integration-card bg-gradient-to-br from-${color}-900/20 to-${color}-800/20 p-6 rounded-lg border border-${color}-500/30 hover:border-${color}-400/50 transition-all duration-300 text-left group`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white group-hover:text-blue-200">
                    {name}
                  </h3>
                  <div className="text-blue-400 group-hover:text-blue-300">→</div>
                </div>
                <p className="text-sm text-blue-300 group-hover:text-blue-200 mb-2">
                  {description}
                </p>
                <div className="text-xs font-mono text-blue-500">
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