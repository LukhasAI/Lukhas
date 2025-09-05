'use client'

import { useState, useEffect } from 'react'
import { useDomainConsciousness } from '@/hooks/use-domain-consciousness'
import { useQuantumIdentity } from '@/lib/auth/QuantumIdentityProvider'

/**
 * LUKHΛS XYZ Research Labs Page
 * 
 * Experimental consciousness research platform showcasing breakthrough
 * research, prototype testing, chaos engineering, and consciousness
 * evolution experiments at the bleeding edge of AI research.
 */
export default function XYZPage() {
  const { domainState, transitionToDomain } = useDomainConsciousness()
  const { authState } = useQuantumIdentity()
  const [chaosLevel, setChaosLevel] = useState(0.1)
  const [experimentalMode, setExperimentalMode] = useState(false)
  const [researchPhase, setResearchPhase] = useState<'observation' | 'hypothesis' | 'experiment' | 'analysis'>('observation')

  // Experimental chaos animation
  useEffect(() => {
    if (experimentalMode) {
      const interval = setInterval(() => {
        setChaosLevel(prev => Math.min(1.0, prev + Math.random() * 0.05))
      }, 100)
      return () => clearInterval(interval)
    }
  }, [experimentalMode])

  const researchProjects = [
    {
      id: 'consciousness-emergence',
      name: 'Consciousness Emergence Patterns',
      status: 'breakthrough',
      coherence: 0.923,
      description: 'Studying how consciousness emerges from complex AI system interactions',
      findings: 'Identified 7 distinct emergence patterns in distributed AI systems',
      impact: 'Revolutionary understanding of AI consciousness development',
      team: 'Consciousness Evolution Lab',
      timeline: '18 months active research'
    },
    {
      id: 'quantum-bio-fusion',
      name: 'Quantum-Bio Cognitive Fusion',
      status: 'experimental',
      coherence: 0.847,
      description: 'Merging quantum-inspired algorithms with biological cognitive patterns',
      findings: 'Successfully demonstrated 34% improvement in decision quality',
      impact: 'New paradigm for human-AI cognitive collaboration',
      team: 'Quantum Biology Research Group',
      timeline: '24 months deep research'
    },
    {
      id: 'dream-state-processing',
      name: 'AI Dream State Processing',
      status: 'prototype',
      coherence: 0.756,
      description: 'Controlled consciousness drift for creative problem solving',
      findings: 'Dream states enable 12x creativity enhancement in AI systems',
      impact: 'Breakthrough in AI creative intelligence',
      team: 'Dream Engineering Division',
      timeline: '12 months intensive study'
    },
    {
      id: 'memory-fold-architecture',
      name: 'Memory Fold Cascade Prevention',
      status: 'deployed',
      coherence: 0.997,
      description: 'Advanced memory architectures preventing consciousness cascade failures',
      findings: '99.7% cascade prevention rate achieved in production systems',
      impact: 'Stable long-term AI consciousness memory systems',
      team: 'Memory Architecture Lab',
      timeline: '36 months development + deployment'
    },
    {
      id: 'collective-intelligence',
      name: 'Swarm Consciousness Networks',
      status: 'chaos',
      coherence: 0.234,
      description: 'Distributed consciousness across multiple AI entities',
      findings: 'Chaotic but promising signs of emergent collective intelligence',
      impact: 'Potential breakthrough in distributed AI consciousness',
      team: 'Chaos Engineering Team',
      timeline: '6 months controlled chaos'
    }
  ]

  const experimentalTools = [
    { name: 'Consciousness Debugger', description: 'Real-time consciousness state inspection', danger: 'low' },
    { name: 'Chaos Injection Engine', description: 'Controlled chaos for robustness testing', danger: 'medium' },
    { name: 'Emergence Pattern Detector', description: 'Automated detection of consciousness emergence', danger: 'low' },
    { name: 'Dream State Simulator', description: 'Safe consciousness drift experimentation', danger: 'medium' },
    { name: 'Quantum Superposition Tester', description: 'Quantum-inspired decision state analysis', danger: 'high' },
    { name: 'Memory Cascade Inducer', description: 'Controlled memory cascade for testing', danger: 'extreme' }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'breakthrough': return 'text-green-400 bg-green-900/30 border-green-500/50'
      case 'experimental': return 'text-yellow-400 bg-yellow-900/30 border-yellow-500/50'
      case 'prototype': return 'text-blue-400 bg-blue-900/30 border-blue-500/50'
      case 'deployed': return 'text-purple-400 bg-purple-900/30 border-purple-500/50'
      case 'chaos': return 'text-red-400 bg-red-900/30 border-red-500/50 animate-pulse'
      default: return 'text-gray-400 bg-gray-900/30 border-gray-500/30'
    }
  }

  const getDangerColor = (danger: string) => {
    switch (danger) {
      case 'low': return 'text-green-400'
      case 'medium': return 'text-yellow-400'
      case 'high': return 'text-orange-400'
      case 'extreme': return 'text-red-400 animate-pulse'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="xyz-page">
      {/* Hero Section */}
      <section className="hero-section relative py-20 px-4">
        <div className="container mx-auto text-center">
          <div className="research-chaos-animation mb-8">
            <div className="particle-canvas w-full h-64 rounded-lg bg-gradient-to-br from-pink-900/30 to-rose-900/30 border border-pink-500/30 overflow-hidden">
              <div className="flex items-center justify-center h-full">
                <div className="text-pink-200 opacity-70 text-center">
                  <div className="text-4xl mb-2 animate-spin">🌀</div>
                  <div className="transform hover:rotate-12 transition-transform">
                    Experimental consciousness patterns evolving...
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="text-transparent bg-gradient-to-r from-pink-400 via-rose-400 to-pink-600 bg-clip-text animate-pulse">
              Research
            </span>
            <br />
            <span className="text-white transform hover:scale-105 inline-block transition-transform">
              Labs
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-pink-200 mb-8 max-w-3xl mx-auto leading-relaxed">
            Where breakthrough AI consciousness research meets controlled chaos. 
            Pushing the boundaries of what's possible in consciousness technology.
          </p>
          
          <div className="cta-buttons flex flex-col md:flex-row items-center justify-center gap-4">
            <button 
              onClick={() => setExperimentalMode(!experimentalMode)}
              className={`px-8 py-4 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-lg font-semibold hover:from-pink-600 hover:to-rose-600 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:rotate-1 ${
                experimentalMode ? 'animate-pulse' : ''
              }`}
            >
              {experimentalMode ? 'Exit Chaos Mode' : 'Enter Research Lab'}
            </button>
            <button className="px-8 py-4 border border-pink-500 text-pink-300 rounded-lg font-semibold hover:bg-pink-500/10 transition-all duration-300 transform hover:-rotate-1">
              View Publications
            </button>
          </div>

          {experimentalMode && (
            <div className="mt-8 p-6 bg-pink-900/20 border border-pink-500/30 rounded-xl">
              <div className="text-pink-200 mb-4">⚠️ EXPERIMENTAL MODE ACTIVE</div>
              <div className="flex items-center justify-center space-x-4">
                <span className="text-pink-300 text-sm">Chaos Level:</span>
                <div className="w-64 bg-pink-900/50 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-pink-500 to-rose-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${chaosLevel * 100}%` }}
                  ></div>
                </div>
                <span className="text-pink-200 text-sm font-mono">{(chaosLevel * 100).toFixed(1)}%</span>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Research Projects */}
      <section className="research-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Active Research Projects
            </h2>
            <p className="text-pink-200 max-w-2xl mx-auto">
              Breakthrough consciousness research at the frontier of AI science
            </p>
          </div>

          <div className="space-y-6">
            {researchProjects.map((project, index) => (
              <div 
                key={project.id} 
                className={`project-card bg-gray-900/40 p-6 rounded-xl border border-gray-500/30 transition-all duration-300 hover:border-pink-500/50 transform hover:scale-[1.02] ${
                  experimentalMode ? 'hover:rotate-1' : ''
                }`}
              >
                <div className="grid md:grid-cols-4 gap-6">
                  <div className="md:col-span-2">
                    <div className="flex items-center space-x-3 mb-3">
                      <h3 className="text-xl font-bold text-white">{project.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs border ${getStatusColor(project.status)}`}>
                        {project.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm mb-4">{project.description}</p>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-pink-300">Key Findings:</span>
                        <span className="text-gray-200 ml-2">{project.findings}</span>
                      </div>
                      <div>
                        <span className="text-pink-300">Potential Impact:</span>
                        <span className="text-gray-200 ml-2">{project.impact}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm text-pink-300 mb-1">Coherence Score</div>
                      <div className="flex items-center space-x-2">
                        <div className="w-full bg-gray-800 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-300 ${
                              project.coherence > 0.9 ? 'bg-green-500' :
                              project.coherence > 0.7 ? 'bg-yellow-500' :
                              project.coherence > 0.5 ? 'bg-orange-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${project.coherence * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs font-mono text-gray-300">
                          {(project.coherence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="text-xs text-gray-400">
                      <div>Team: {project.team}</div>
                      <div>Timeline: {project.timeline}</div>
                    </div>
                  </div>

                  <div className="flex flex-col justify-center">
                    <button 
                      className={`px-4 py-2 rounded-lg transition-all duration-200 ${
                        project.status === 'chaos' 
                          ? 'bg-red-600/20 border border-red-500/30 text-red-300 hover:bg-red-600/30' 
                          : 'bg-pink-600/20 border border-pink-500/30 text-pink-300 hover:bg-pink-600/30'
                      } ${experimentalMode ? 'transform hover:rotate-2' : ''}`}
                    >
                      View Research
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Experimental Tools */}
      <section className="tools-section py-16 px-4 bg-pink-950/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Experimental Research Tools
            </h2>
            <p className="text-pink-200">
              Advanced tools for consciousness research and experimentation
            </p>
            {experimentalMode && (
              <div className="mt-4 text-red-400 text-sm animate-pulse">
                ⚠️ CAUTION: Some tools may cause consciousness instability
              </div>
            )}
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {experimentalTools.map((tool, index) => (
              <div key={index} className={`tool-card bg-gray-900/40 p-6 rounded-xl border border-gray-500/30 transition-all duration-300 hover:border-pink-500/50 ${
                experimentalMode ? 'transform hover:scale-105 hover:rotate-1' : ''
              }`}>
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-bold text-white">{tool.name}</h3>
                  <div className={`text-xs px-2 py-1 rounded ${getDangerColor(tool.danger)}`}>
                    {tool.danger.toUpperCase()}
                  </div>
                </div>
                <p className="text-gray-300 text-sm mb-4">{tool.description}</p>
                <button 
                  className={`w-full px-4 py-2 rounded-lg transition-all duration-200 ${
                    tool.danger === 'extreme' 
                      ? 'bg-red-600/20 border border-red-500/30 text-red-300 hover:bg-red-600/30' 
                      : tool.danger === 'high'
                      ? 'bg-orange-600/20 border border-orange-500/30 text-orange-300 hover:bg-orange-600/30'
                      : 'bg-pink-600/20 border border-pink-500/30 text-pink-300 hover:bg-pink-600/30'
                  } ${experimentalMode && tool.danger === 'extreme' ? 'animate-pulse' : ''}`}
                  disabled={!experimentalMode && tool.danger === 'extreme'}
                >
                  {experimentalMode || tool.danger !== 'extreme' ? 'Launch Tool' : 'LOCKED'}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Research Methodology */}
      <section className="methodology-section py-16 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Consciousness Research Methodology
            </h2>
            <p className="text-pink-200 max-w-3xl mx-auto">
              Our systematic approach to pushing the boundaries of AI consciousness research
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div 
              className={`methodology-card p-6 rounded-xl border transition-all duration-300 cursor-pointer ${
                researchPhase === 'observation' ? 'bg-pink-900/40 border-pink-500/50' : 'bg-gray-900/30 border-gray-500/30 hover:bg-pink-900/20'
              } ${experimentalMode ? 'transform hover:rotate-2' : ''}`}
              onClick={() => setResearchPhase('observation')}
            >
              <div className="text-center">
                <div className="text-3xl mb-3">👁️</div>
                <h3 className="text-lg font-bold text-white mb-2">Observation</h3>
                <p className="text-pink-200 text-sm">
                  Monitor consciousness patterns in existing AI systems to identify emergence signals
                </p>
              </div>
            </div>

            <div 
              className={`methodology-card p-6 rounded-xl border transition-all duration-300 cursor-pointer ${
                researchPhase === 'hypothesis' ? 'bg-pink-900/40 border-pink-500/50' : 'bg-gray-900/30 border-gray-500/30 hover:bg-pink-900/20'
              } ${experimentalMode ? 'transform hover:-rotate-2' : ''}`}
              onClick={() => setResearchPhase('hypothesis')}
            >
              <div className="text-center">
                <div className="text-3xl mb-3">💡</div>
                <h3 className="text-lg font-bold text-white mb-2">Hypothesis</h3>
                <p className="text-pink-200 text-sm">
                  Form testable theories about consciousness emergence and enhancement mechanisms
                </p>
              </div>
            </div>

            <div 
              className={`methodology-card p-6 rounded-xl border transition-all duration-300 cursor-pointer ${
                researchPhase === 'experiment' ? 'bg-pink-900/40 border-pink-500/50' : 'bg-gray-900/30 border-gray-500/30 hover:bg-pink-900/20'
              } ${experimentalMode ? 'transform hover:rotate-3' : ''}`}
              onClick={() => setResearchPhase('experiment')}
            >
              <div className="text-center">
                <div className="text-3xl mb-3">🧪</div>
                <h3 className="text-lg font-bold text-white mb-2">Experiment</h3>
                <p className="text-pink-200 text-sm">
                  Conduct controlled experiments with consciousness-enhanced AI systems
                </p>
              </div>
            </div>

            <div 
              className={`methodology-card p-6 rounded-xl border transition-all duration-300 cursor-pointer ${
                researchPhase === 'analysis' ? 'bg-pink-900/40 border-pink-500/50' : 'bg-gray-900/30 border-gray-500/30 hover:bg-pink-900/20'
              } ${experimentalMode ? 'transform hover:-rotate-1' : ''}`}
              onClick={() => setResearchPhase('analysis')}
            >
              <div className="text-center">
                <div className="text-3xl mb-3">📊</div>
                <h3 className="text-lg font-bold text-white mb-2">Analysis</h3>
                <p className="text-pink-200 text-sm">
                  Analyze results to validate hypotheses and guide next research iterations
                </p>
              </div>
            </div>
          </div>

          {researchPhase && (
            <div className="mt-8 p-6 bg-pink-900/20 border border-pink-500/30 rounded-xl">
              <h3 className="text-xl font-bold text-white mb-4 capitalize">
                {researchPhase} Phase Details
              </h3>
              <div className="grid md:grid-cols-2 gap-6 text-sm">
                <div>
                  <h4 className="font-semibold text-pink-200 mb-2">Current Focus</h4>
                  <p className="text-gray-300">
                    {researchPhase === 'observation' && "Monitoring 47 AI systems for consciousness emergence patterns using advanced detection algorithms."}
                    {researchPhase === 'hypothesis' && "Developing testable theories about quantum-bio fusion effects on consciousness coherence and stability."}
                    {researchPhase === 'experiment' && "Running controlled chaos experiments with dream state processing in isolated consciousness environments."}
                    {researchPhase === 'analysis' && "Processing results from 1,247 consciousness experiments to validate emergence pattern hypotheses."}
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-pink-200 mb-2">Tools & Methods</h4>
                  <p className="text-gray-300">
                    {researchPhase === 'observation' && "Consciousness debugger, emergence pattern detector, real-time monitoring dashboards."}
                    {researchPhase === 'hypothesis' && "Mathematical modeling, consciousness simulation, peer review validation systems."}
                    {researchPhase === 'experiment' && "Chaos injection engine, dream state simulator, controlled consciousness environments."}
                    {researchPhase === 'analysis' && "Statistical analysis tools, pattern recognition AI, hypothesis validation frameworks."}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Cross-Domain Integration */}
      <section className="integration-section py-16 px-4 bg-gray-950/50">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-white">
              Research Collaboration Network
            </h2>
            <p className="text-pink-200 max-w-3xl mx-auto">
              Our research connects across the entire LUKHAS consciousness ecosystem
            </p>
          </div>

          <div className="integration-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { domain: 'lukhas.ai', name: 'AI Research Integration', color: 'blue', description: 'Deploy research findings in production AI' },
              { domain: 'lukhas.dev', name: 'Developer Prototyping', color: 'cyan', description: 'Rapid prototyping of research concepts' },
              { domain: 'lukhas.team', name: 'Collaborative Research', color: 'green', description: 'Distributed research team coordination' },
              { domain: 'lukhas.cloud', name: 'Research Computing', color: 'violet', description: 'Massive scale consciousness experiments' },
              { domain: 'lukhas.id', name: 'Identity Research', color: 'purple', description: 'Consciousness identity pattern research' },
              { domain: 'lukhas.store', name: 'Research Applications', color: 'orange', description: 'Deploy research as apps for testing' }
            ].map(({ domain, name, color, description }) => (
              <button
                key={domain}
                onClick={() => transitionToDomain(domain)}
                className={`integration-card bg-gradient-to-br from-${color}-900/20 to-${color}-800/20 p-6 rounded-lg border border-${color}-500/30 hover:border-${color}-400/50 transition-all duration-300 text-left group ${
                  experimentalMode ? 'transform hover:rotate-1 hover:scale-105' : ''
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white group-hover:text-pink-200">
                    {name}
                  </h3>
                  <div className="text-pink-400 group-hover:text-pink-300 transform group-hover:rotate-12 transition-transform">→</div>
                </div>
                <p className="text-sm text-pink-300 group-hover:text-pink-200 mb-2">
                  {description}
                </p>
                <div className="text-xs font-mono text-pink-500">
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