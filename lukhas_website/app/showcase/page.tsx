'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import NeuralBackgroundWrapper from '@/components/neural-background-wrapper'
import '@/styles/showcase.css'

export default function ShowcasePage() {
  const router = useRouter()
  
  useEffect(() => {
    document.title = 'LUKHΛS Quantum Domain Mesh — Interactive Showcase'
    // Add showcase body class to isolate from global styles
    document.body.classList.add('showcase-page')
    
    return () => {
      document.body.classList.remove('showcase-page')
    }
  }, [])

  const handleDomainClick = (domainKey: string) => {
    router.push(`/${domainKey}?skipState=true`)
  }
  
  const domains = [
    { key: 'ai', name: 'AI Platform', desc: 'Consciousness Technology Hub', color: 'bg-blue-600', status: '✅', coherence: '98.5' },
    { key: 'id', name: 'Identity Hub', desc: 'Zero-Knowledge Sovereignty', color: 'bg-purple-600', status: '✅', coherence: '99.2' },
    { key: 'team', name: 'Team Collaboration', desc: 'Collective Consciousness', color: 'bg-emerald-600', status: '✅', coherence: '97.3' },
    { key: 'dev', name: 'Developer Tools', desc: 'AI-Assisted Development', color: 'bg-orange-600', status: '✅', coherence: '99.5' },
    { key: 'io', name: 'API Infrastructure', desc: 'High-Performance APIs', color: 'bg-indigo-600', status: '✅', coherence: '99.8' },
    { key: 'store', name: 'App Marketplace', desc: 'Consciousness Apps', color: 'bg-amber-600', status: '✅', coherence: '97.2' },
    { key: 'cloud', name: 'Cloud Platform', desc: 'Scalable Infrastructure', color: 'bg-cyan-600', status: '✅', coherence: '96.5' },
    { key: 'eu', name: 'European Operations', desc: 'GDPR Compliance', color: 'bg-green-600', status: '✅', coherence: '98.8' },
    { key: 'us', name: 'US Enterprise', desc: 'SOC2 Compliance', color: 'bg-red-600', status: '✅', coherence: '98.2' },
    { key: 'xyz', name: 'Experimental', desc: 'Cutting-Edge R&D', color: 'bg-pink-600', status: '✅', coherence: '89.0' },
    { key: 'com', name: 'Corporate Solutions', desc: 'Executive Platforms', color: 'bg-violet-600', status: '✅', coherence: '97.5' }
  ]

  return (
    <>
      <NeuralBackgroundWrapper mode="showcase" />
      {/* Showcase isolated container */}
      <div className="showcase-container min-h-screen bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20 p-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-4">
              LUKHΛS Quantum Domain Mesh
            </h1>
            <p className="text-blue-200 text-lg">
              Interactive showcase of all 11 consciousness domains
            </p>
            <div className="text-sm text-gray-400 mt-2">
              🌐 Quantum Coherence: 95.2% | 🧠 Active Domains: 11/11 | ⚛️ Cross-Domain Sync: Active
            </div>
          </div>

          {/* Domain Grid */}
          <div className="showcase-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {domains.map((domain) => (
              <div
                key={domain.key}
                className="showcase-domain-card bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 hover:border-white/30 transition-all cursor-pointer group hover:scale-105 p-6"
                onClick={() => handleDomainClick(domain.key)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-3 h-3 rounded-full ${domain.color}`}></div>
                  <span className="text-green-400 text-sm">{domain.status}</span>
                </div>
                
                <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-blue-300 transition-colors">
                  lukhas.{domain.key}
                </h3>
                
                <p className="text-blue-200 font-medium mb-2">
                  {domain.name}
                </p>
                
                <p className="text-gray-400 text-sm mb-4">
                  {domain.desc}
                </p>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-500 text-xs">
                    Coherence: {domain.coherence}%
                  </span>
                  <div className="text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    →
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="text-center mt-12 text-gray-400">
            <p className="text-sm">
              Powered by MΛTRIZ Cognitive Architecture • Trinity Framework ⚛️🧠🛡️
            </p>
          </div>
        </div>
      </div>
    </>
  )
}