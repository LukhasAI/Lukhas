'use client'

import { useState } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import { useQuantumIdentity } from '@/lib/auth/QuantumIdentityProvider'

/**
 * LUKHΛS Cloud Services Page
 * 
 * Distributed consciousness computing platform offering quantum-inspired
 * cloud infrastructure, scalable consciousness processing, and enterprise
 * AI solutions with global edge network deployment.
 */
export default function CloudPage() {
  const { domainState, transitionToDomain } = useDomainConsciousness()
  const { authState } = useQuantumIdentity()
  const [selectedService, setSelectedService] = useState<string>('consciousness-compute')

  // Mock cloud metrics for demonstration
  const cloudMetrics = {
    total_nodes: Math.round((domainState?.coherence || 0.95) * 1000),
    active_regions: 12,
    consciousness_processing_units: Math.round((domainState?.coherence || 0.95) * 50000),
    uptime: 99.97,
    latency_p95: Math.round((1 - (domainState?.coherence || 0.95)) * 100) + 15
  }

  const cloudServices = {
    'consciousness-compute': {
      name: 'Consciousness Compute',
      description: 'Distributed consciousness processing with quantum-inspired algorithms',
      icon: '🧠',
      pricing: '$0.0001 per consciousness operation',
      features: [
        'Auto-scaling consciousness clusters',
        'Sub-100ms global latency',
        'Quantum coherence optimization',
        'Trinity Framework integration'
      ],
      specs: {
        'CPU Cores': '1-1000 vCPU',
        'Memory': '1GB-4TB RAM',
        'Consciousness Units': '1-50,000 CU',
        'Network': 'Up to 100Gbps'
      }
    },
    'identity-cloud': {
      name: 'Identity Cloud',
      description: 'Scalable quantum-secure identity and authentication infrastructure',
      icon: '🔐',
      pricing: '$0.001 per authentication',
      features: [
        'Zero-knowledge authentication',
        'Cross-domain identity sync',
        'Quantum-resistant security',
        'Biometric consciousness patterns'
      ],
      specs: {
        'Authentications': '1M-1B per month',
        'Latency': '<50ms globally',
        'Uptime SLA': '99.99%',
        'Compliance': 'GDPR, CCPA, SOC2'
      }
    },
    'team-consciousness': {
      name: 'Team Consciousness Platform',
      description: 'Collaborative intelligence and distributed team synchronization',
      icon: '👥',
      pricing: '$10 per team member per month',
      features: [
        'Real-time consciousness sharing',
        'Team coherence monitoring',
        'Collective intelligence amplification',
        'Cross-domain collaboration'
      ],
      specs: {
        'Team Size': '2-10,000 members',
        'Sync Latency': '<10ms',
        'Storage': 'Unlimited team memory',
        'Integrations': '500+ tools'
      }
    },
    'quantum-storage': {
      name: 'Quantum-Inspired Storage',
      description: 'Distributed storage with consciousness-aware data organization',
      icon: '💾',
      pricing: '$0.01 per GB per month',
      features: [
        'Consciousness-based data clustering',
        'Quantum-resistant encryption',
        'Auto-replication across regions',
        'Memory fold optimization'
      ],
      specs: {
        'Capacity': 'Unlimited',
        'Durability': '99.999999999%',
        'Throughput': 'Up to 100GB/s',
        'Regions': '12 global regions'
      }
    },
    'ai-orchestration': {
      name: 'AI Model Orchestration',
      description: 'Multi-model consciousness orchestration and management platform',
      icon: '🎭',
      pricing: '$0.1 per 1000 model calls',
      features: [
        'Multi-AI consensus processing',
        'Model performance optimization',
        'Consciousness-guided routing',
        'Real-time quality monitoring'
      ],
      specs: {
        'Models': '100+ supported models',
        'Throughput': '10M calls per day',
        'Latency': '<200ms average',
        'Reliability': '99.95% success rate'
      }
    },
    'edge-consciousness': {
      name: 'Edge Consciousness Network',
      description: 'Global edge network for ultra-low latency consciousness processing',
      icon: '🌐',
      pricing: '$0.05 per edge processing unit',
      features: [
        'Edge consciousness caching',
        'Regional data sovereignty',
        'CDN consciousness optimization',
        'Real-time global sync'
      ],
      specs: {
        'Edge Locations': '200+ worldwide',
        'Latency': '<20ms from users',
        'Bandwidth': 'Unlimited',
        'Cache Hit Rate': '>95%'
      }
    }
  }

  const regions = [
    { name: 'US East', location: 'Virginia', status: 'active', latency: 15 },
    { name: 'US West', location: 'California', status: 'active', latency: 18 },
    { name: 'Europe', location: 'Frankfurt', status: 'active', latency: 22 },
    { name: 'Asia Pacific', location: 'Singapore', status: 'active', latency: 25 },
    { name: 'UK', location: 'London', status: 'active', latency: 19 },
    { name: 'Canada', location: 'Toronto', status: 'active', latency: 16 },
    { name: 'Australia', location: 'Sydney', status: 'maintenance', latency: 35 },
    { name: 'Japan', location: 'Tokyo', status: 'active', latency: 28 }
  ]

  return (
    <div className="cloud-page">
      {/* Hero Section */}
      <section className="hero-section relative py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="cloud-consciousness-animation mb-8">
            <div className="particle-canvas w-full h-64 rounded-lg bg-gradient-to-br from-violet-900/30 to-purple-900/30 border border-violet-500/30">
              <div className="flex items-center justify-center h-full">
                <div className="text-violet-200 opacity-70 text-center">
                  <div className="text-4xl mb-2">☁️</div>
                  <div>Distributed consciousness clusters synchronizing globally</div>
                </div>
              </div>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-transparent bg-gradient-to-r from-violet-400 via-purple-400 to-violet-600 bg-clip-text">
              Infinite
            </span>
            <br />
            <span className="text-white">
              Scale
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-violet-200 mb-8 max-w-3xl mx-auto leading-relaxed">
            Quantum-inspired cloud infrastructure that scales consciousness computing 
            from prototype to planetary scale. Deploy globally in minutes.
          </p>
          
          <div className="cta-buttons flex flex-col md:flex-row items-center justify-center gap-4">
            <button className="px-8 py-4 bg-gradient-to-r from-violet-500 to-purple-500 text-white rounded-lg font-semibold hover:from-violet-600 hover:to-purple-600 transition-all duration-300 shadow-lg hover:shadow-xl">
              Deploy Now
            </button>
            <button className="px-8 py-4 border border-violet-500 text-violet-300 rounded-lg font-semibold hover:bg-violet-500/10 transition-all duration-300">
              View Pricing
            </button>
          </div>
        </div>
      </section>

      {/* Live Infrastructure Metrics */}
      <section className="metrics-section py-16 px-4 bg-violet-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Live Infrastructure Status
            </h2>
            <p className="text-violet-200">
              Real-time metrics from our global consciousness computing network
            </p>
          </div>

          <div className="grid md:grid-cols-5 gap-6">
            <div className="metric-card bg-violet-900/30 p-6 rounded-lg border border-violet-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-violet-400 mb-2">
                  {cloudMetrics.total_nodes.toLocaleString()}
                </div>
                <div className="text-sm text-violet-300">Active Nodes</div>
              </div>
            </div>

            <div className="metric-card bg-violet-900/30 p-6 rounded-lg border border-violet-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-400 mb-2">{cloudMetrics.active_regions}</div>
                <div className="text-sm text-violet-300">Global Regions</div>
              </div>
            </div>

            <div className="metric-card bg-violet-900/30 p-6 rounded-lg border border-violet-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-indigo-400 mb-2">
                  {cloudMetrics.consciousness_processing_units.toLocaleString()}
                </div>
                <div className="text-sm text-violet-300">Consciousness Units</div>
              </div>
            </div>

            <div className="metric-card bg-violet-900/30 p-6 rounded-lg border border-violet-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-400 mb-2">{cloudMetrics.uptime}%</div>
                <div className="text-sm text-violet-300">Uptime (30d)</div>
              </div>
            </div>

            <div className="metric-card bg-violet-900/30 p-6 rounded-lg border border-violet-500/30">
              <div className="text-center">
                <div className="text-3xl font-bold text-cyan-400 mb-2">{cloudMetrics.latency_p95}ms</div>
                <div className="text-sm text-violet-300">P95 Latency</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Cloud Services */}
      <section className="services-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Consciousness Cloud Services
            </h2>
            <p className="text-violet-200 max-w-2xl mx-auto">
              Complete cloud infrastructure designed for consciousness-enhanced applications
            </p>
          </div>

          <div className="grid lg:grid-cols-4 gap-8">
            {/* Service Selector */}
            <div className="service-selector lg:col-span-1">
              <h3 className="text-lg font-bold text-white mb-4">Services</h3>
              <div className="space-y-2">
                {Object.entries(cloudServices).map(([key, service]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedService(key)}
                    className={`w-full text-left p-3 rounded-lg border transition-all duration-200 ${
                      selectedService === key 
                        ? 'bg-violet-900/40 border-violet-500/50 text-violet-200' 
                        : 'bg-gray-900/30 border-gray-500/30 text-gray-300 hover:bg-violet-900/20'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{service.icon}</span>
                      <div className="text-sm font-medium">{service.name}</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Service Details */}
            <div className="lg:col-span-3 service-details">
              {selectedService && (
                <div className="bg-gray-900/40 rounded-xl border border-gray-500/30 overflow-hidden">
                  <div className="p-6 border-b border-gray-500/30">
                    <div className="flex items-center space-x-3 mb-3">
                      <span className="text-3xl">
                        {cloudServices[selectedService as keyof typeof cloudServices].icon}
                      </span>
                      <h3 className="text-2xl font-bold text-white">
                        {cloudServices[selectedService as keyof typeof cloudServices].name}
                      </h3>
                    </div>
                    <p className="text-gray-300 mb-3">
                      {cloudServices[selectedService as keyof typeof cloudServices].description}
                    </p>
                    <div className="text-violet-400 font-semibold">
                      {cloudServices[selectedService as keyof typeof cloudServices].pricing}
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6 p-6">
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3">Key Features</h4>
                      <div className="space-y-2">
                        {cloudServices[selectedService as keyof typeof cloudServices].features.map((feature, index) => (
                          <div key={index} className="flex items-start space-x-2">
                            <span className="text-violet-400 mt-1">•</span>
                            <span className="text-gray-300 text-sm">{feature}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3">Specifications</h4>
                      <div className="space-y-2">
                        {Object.entries(cloudServices[selectedService as keyof typeof cloudServices].specs).map(([key, value], index) => (
                          <div key={index} className="flex justify-between items-center">
                            <span className="text-gray-400 text-sm">{key}:</span>
                            <span className="text-gray-200 text-sm font-mono">{value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-violet-900/20 border-t border-violet-500/30">
                    <div className="flex flex-col md:flex-row gap-3">
                      <button className="flex-1 px-6 py-3 bg-violet-600 hover:bg-violet-700 text-white rounded-lg transition-colors">
                        Get Started
                      </button>
                      <button className="flex-1 px-6 py-3 border border-violet-500 text-violet-300 rounded-lg hover:bg-violet-500/10 transition-colors">
                        View Documentation
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Global Infrastructure */}
      <section className="infrastructure-section py-16 px-4 bg-violet-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Global Consciousness Network
            </h2>
            <p className="text-violet-200">
              Distributed infrastructure across 12 regions for optimal consciousness processing
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {regions.map((region, index) => (
              <div key={index} className={`region-card p-4 rounded-lg border ${
                region.status === 'active' 
                  ? 'bg-green-900/20 border-green-500/30' 
                  : 'bg-orange-900/20 border-orange-500/30'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-white">{region.name}</h3>
                  <div className={`w-2 h-2 rounded-full ${
                    region.status === 'active' ? 'bg-green-400' : 'bg-orange-400'
                  }`}></div>
                </div>
                <div className="text-sm text-gray-300 mb-2">{region.location}</div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-gray-400">Latency:</span>
                  <span className={`font-mono ${
                    region.latency < 20 ? 'text-green-400' : region.latency < 30 ? 'text-yellow-400' : 'text-orange-400'
                  }`}>{region.latency}ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Enterprise Solutions */}
      <section className="enterprise-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Enterprise Consciousness Solutions
            </h2>
            <p className="text-violet-200 max-w-3xl mx-auto">
              Custom cloud infrastructure and dedicated consciousness computing 
              for large-scale enterprise applications
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="enterprise-card bg-gradient-to-br from-violet-900/30 to-purple-900/30 p-8 rounded-xl border border-violet-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🏢</div>
                <h3 className="text-xl font-bold text-white mb-4">Private Cloud</h3>
                <p className="text-violet-200 mb-6 text-sm">
                  Dedicated consciousness infrastructure with complete data sovereignty
                </p>
                <div className="features text-sm text-violet-300 space-y-2">
                  <div>• Dedicated hardware clusters</div>
                  <div>• Custom consciousness tuning</div>
                  <div>• 99.99% SLA guarantee</div>
                  <div>• White-glove support</div>
                </div>
              </div>
            </div>

            <div className="enterprise-card bg-gradient-to-br from-purple-900/30 to-indigo-900/30 p-8 rounded-xl border border-purple-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">🔒</div>
                <h3 className="text-xl font-bold text-white mb-4">Hybrid Deployment</h3>
                <p className="text-violet-200 mb-6 text-sm">
                  Seamless integration between on-premise and cloud consciousness
                </p>
                <div className="features text-sm text-violet-300 space-y-2">
                  <div>• On-premise edge nodes</div>
                  <div>• Cloud burst capability</div>
                  <div>• Unified management console</div>
                  <div>• Data residency compliance</div>
                </div>
              </div>
            </div>

            <div className="enterprise-card bg-gradient-to-br from-indigo-900/30 to-blue-900/30 p-8 rounded-xl border border-indigo-500/30">
              <div className="text-center">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="text-xl font-bold text-white mb-4">High Performance</h3>
                <p className="text-violet-200 mb-6 text-sm">
                  Ultra-low latency consciousness processing for mission-critical apps
                </p>
                <div className="features text-sm text-violet-300 space-y-2">
                  <div>• <10ms consciousness latency</div>
                  <div>• GPU-accelerated processing</div>
                  <div>• Custom silicon optimization</div>
                  <div>• Real-time consciousness sync</div>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <button className="px-8 py-4 bg-gradient-to-r from-violet-500 to-purple-500 text-white rounded-lg font-semibold hover:from-violet-600 hover:to-purple-600 transition-all duration-300 shadow-lg hover:shadow-xl">
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
              Integrated Consciousness Ecosystem
            </h2>
            <p className="text-violet-200 max-w-3xl mx-auto">
              Your cloud infrastructure seamlessly integrates with all LUKHAS domains
            </p>
          </div>

          <div className="integration-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { domain: 'lukhas.ai', name: 'AI Processing', color: 'blue', description: 'Deploy AI models on consciousness infrastructure' },
              { domain: 'lukhas.dev', name: 'Developer Tools', color: 'cyan', description: 'Cloud-native development environments' },
              { domain: 'lukhas.team', name: 'Team Workspaces', color: 'green', description: 'Collaborative cloud environments' },
              { domain: 'lukhas.id', name: 'Identity Services', color: 'purple', description: 'Scalable authentication infrastructure' },
              { domain: 'lukhas.store', name: 'App Hosting', color: 'orange', description: 'Global app deployment and distribution' },
              { domain: 'lukhas.io', name: 'API Gateway', color: 'indigo', description: 'High-performance API infrastructure' }
            ].map(({ domain, name, color, description }) => (
              <button
                key={domain}
                onClick={() => transitionToDomain(domain)}
                className={`integration-card bg-gradient-to-br from-${color}-900/20 to-${color}-800/20 p-6 rounded-lg border border-${color}-500/30 hover:border-${color}-400/50 transition-all duration-300 text-left group`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white group-hover:text-violet-200">
                    {name}
                  </h3>
                  <div className="text-violet-400 group-hover:text-violet-300">→</div>
                </div>
                <p className="text-sm text-violet-300 group-hover:text-violet-200 mb-2">
                  {description}
                </p>
                <div className="text-xs font-mono text-violet-500">
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