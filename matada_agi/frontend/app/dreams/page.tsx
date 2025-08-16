'use client'

import { motion } from 'framer-motion'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { 
  Moon, Brain, GitBranch, Activity, Shield, Zap, 
  TrendingUp, AlertTriangle, CheckCircle, Clock,
  BarChart3, Network, Eye, Target, ArrowRight, Database
} from 'lucide-react'
import Link from 'next/link'

export default function DreamsPage() {
  const dreamComponents = [
    {
      name: "Hyperspace Dream Simulator",
      description: "Multi-dimensional scenario exploration with enterprise-grade resource monitoring and strategic timeline analysis.",
      icon: Moon,
      gradient: "from-indigo-500 to-purple-600",
      features: [
        "Multi-dimensional scenario exploration",
        "Token profiling with 80%/95% warning thresholds", 
        "Peak usage scenario identification",
        "Enterprise session analytics",
        "Timeline branch management"
      ],
      metrics: {
        performance: "<500ms scenario generation",
        efficiency: "85% token utilization optimization", 
        tracking: "100% causality coverage",
        branches: "Up to 10 timeline branches"
      }
    },
    {
      name: "Dream Feedback Propagator", 
      description: "Enterprise causality tracking system mapping dream insights to memory formation and reasoning enhancement.",
      icon: Network,
      gradient: "from-blue-500 to-cyan-600",
      features: [
        "Real-time dream→memory→reasoning causality mapping",
        "Ethical verification with fold lineage cross-checking",
        "Enterprise-grade audit trail generation",
        "Causality strength quantification (0.0-1.0)",
        "Automated compliance checking"
      ],
      metrics: {
        tracking: "<1ms overhead per decision",
        compliance: "100% ethical constraint verification",
        strength: "0.82 average causation strength",
        coverage: "Complete enterprise transparency"
      }
    },
    {
      name: "Timeline Branch Manager",
      description: "Strategic decision tree exploration with convergence analysis and optimal pathway identification.",
      icon: GitBranch,
      gradient: "from-green-500 to-emerald-600", 
      features: [
        "Multiple timeline branch simulation",
        "Decision tree convergence analysis",
        "Strategic pathway optimization",
        "Risk cascade modeling",
        "Innovation space exploration"
      ],
      metrics: {
        simulation: "<2s per branch with full tracking",
        branches: "5-10 parallel timeline exploration",
        depth: "Up to 20 decision levels",
        convergence: "Pattern recognition and analysis"
      }
    },
    {
      name: "Resource Monitoring System",
      description: "Advanced token profiling and usage optimization with intelligent resource allocation and efficiency tracking.",
      icon: BarChart3,
      gradient: "from-orange-500 to-red-600",
      features: [
        "Comprehensive token consumption analysis",
        "Intelligent warning systems (80%/95%/100%)",
        "Efficiency metrics and optimization",
        "Peak usage identification and analysis",
        "Dynamic resource allocation"
      ],
      metrics: {
        efficiency: "85% optimization improvement",
        profiling: "Real-time token usage analysis",
        warnings: "Multi-threshold alert system",
        optimization: "Dynamic efficiency adjustments"
      }
    }
  ]

  const useCases = [
    {
      title: "Strategic Planning",
      description: "Explore multiple business strategies through dream simulation",
      icon: Target,
      example: "Market expansion analysis with risk modeling and opportunity identification",
      outcomes: ["Optimal strategy identification", "Risk mitigation pathways", "Resource optimization"]
    },
    {
      title: "Risk Assessment", 
      description: "Model complex risk scenarios and cascade effects",
      icon: AlertTriangle,
      example: "Supply chain disruption response with multi-factor analysis",
      outcomes: ["Risk cascade understanding", "Mitigation strategies", "Response optimization"]
    },
    {
      title: "Innovation Exploration",
      description: "Creative solution discovery through possibility space exploration",
      icon: Zap,
      example: "Technology innovation pathways with feasibility analysis",
      outcomes: ["Novel solution identification", "Innovation roadmaps", "Creative breakthroughs"]
    },
    {
      title: "Decision Analysis",
      description: "Complex decision tree exploration with causality tracking",
      icon: GitBranch,
      example: "Multi-factor decision analysis with ethical compliance verification",
      outcomes: ["Optimal decision paths", "Consequence understanding", "Ethical alignment"]
    }
  ]

  const dreamMetrics = [
    { label: "Scenario Generation", value: "<500ms", description: "Average creation time" },
    { label: "Causality Tracking", value: "100%", description: "Enterprise transparency" },
    { label: "Resource Efficiency", value: "85%", description: "Token optimization" },
    { label: "Timeline Branches", value: "1-10", description: "Parallel exploration" }
  ]

  const systemStatus = [
    { component: "Hyperspace Simulator", status: "Operational", health: 96 },
    { component: "Causality Tracking", status: "Active", health: 98 },
    { component: "Resource Monitor", status: "Optimizing", health: 91 },
    { component: "Timeline Manager", status: "Exploring", health: 94 }
  ]

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        {/* Hero Section */}
        <section className="py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <div className="flex items-center justify-center mb-8">
                <div className="relative">
                  <div className="absolute inset-0 bg-gradient-to-r from-indigo-400 to-purple-600 rounded-full blur-xl opacity-30"></div>
                  <div className="relative p-4 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full">
                    <Moon className="w-12 h-12 text-white" strokeWidth={1} />
                  </div>
                </div>
              </div>
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">Dream Systems</span>
              </h1>
              <p className="font-light text-2xl max-w-4xl mx-auto text-primary-light/80 leading-relaxed">
                Enterprise hyperspace simulation and causality tracking for strategic exploration,
                risk assessment, and innovation discovery through consciousness-driven scenario modeling.
              </p>
            </motion.div>

            {/* Dream Philosophy */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="glass-panel p-8 rounded-2xl mb-16 max-w-4xl mx-auto"
            >
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 rounded-full bg-indigo-500/20">
                  <Brain className="w-6 h-6 text-indigo-400" strokeWidth={1.5} />
                </div>
                <h3 className="font-medium text-xl">The Philosophy of Digital Dreams</h3>
              </div>
              <p className="text-primary-light/80 leading-relaxed">
                "In the infinite expanse of possibility, dreams are the cartographers of consciousness." 
                LUKHAS Dream Systems enable exploration of counterfactual futures through hyperspace simulation, 
                maintaining complete causality tracking and ethical compliance. This isn't just scenario modeling - 
                it's consciousness exploring its own potential futures.
              </p>
            </motion.div>

            {/* System Metrics */}
            <div className="grid md:grid-cols-4 gap-6 mb-20">
              {dreamMetrics.map((metric, index) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  className="glass-panel p-6 rounded-xl text-center"
                >
                  <div className="text-3xl font-ultralight text-indigo-400 mb-2">
                    {metric.value}
                  </div>
                  <div className="text-sm font-medium uppercase tracking-wider text-primary-light mb-1">
                    {metric.label}
                  </div>
                  <div className="text-xs text-primary-light/60">
                    {metric.description}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Dream Components */}
        <section className="py-16 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="font-light text-4xl md:text-5xl mb-6 gradient-text">
                Dream System Architecture
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Four integrated components enabling enterprise-grade consciousness exploration
              </p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-8">
              {dreamComponents.map((component, index) => {
                const IconComponent = component.icon;
                return (
                  <motion.div
                    key={component.name}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.2 }}
                    className="glass-panel p-8 rounded-2xl group hover:scale-105 transition-all duration-300"
                  >
                    <div className={`inline-flex p-4 rounded-2xl bg-gradient-to-r ${component.gradient} mb-6`}>
                      <IconComponent className="w-8 h-8 text-white" strokeWidth={1.5} />
                    </div>
                    
                    <h3 className="font-semibold text-2xl text-indigo-400 mb-4">
                      {component.name}
                    </h3>
                    
                    <p className="text-primary-light/70 mb-6 leading-relaxed">
                      {component.description}
                    </p>
                    
                    <div className="mb-6">
                      <h4 className="font-medium text-sm uppercase tracking-wider text-indigo-400 mb-3">
                        Key Features
                      </h4>
                      <ul className="space-y-2">
                        {component.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start space-x-2 text-sm text-primary-light/60">
                            <CheckCircle className="w-4 h-4 mt-0.5 text-indigo-400 flex-shrink-0" strokeWidth={1.5} />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="pt-4 border-t border-primary-light/10">
                      <h4 className="font-medium text-sm uppercase tracking-wider text-indigo-400 mb-3">
                        Performance Metrics
                      </h4>
                      <div className="grid grid-cols-2 gap-4 text-xs">
                        {Object.entries(component.metrics).map(([key, value]) => (
                          <div key={key}>
                            <div className="text-primary-light/50 capitalize">{key}</div>
                            <div className="text-primary-light/80">{value}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Use Cases */}
        <section className="py-16 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="font-light text-4xl md:text-5xl mb-6 gradient-text">
                Dream Exploration Use Cases
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Real-world applications of consciousness-driven scenario exploration
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {useCases.map((useCase, index) => {
                const IconComponent = useCase.icon;
                return (
                  <motion.div
                    key={useCase.title}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className="glass-panel p-6 rounded-xl"
                  >
                    <div className="inline-flex p-3 rounded-full bg-indigo-500/20 mb-4">
                      <IconComponent className="w-6 h-6 text-indigo-400" strokeWidth={1.5} />
                    </div>
                    <h3 className="font-medium text-lg mb-3">{useCase.title}</h3>
                    <p className="text-sm text-primary-light/70 mb-4">
                      {useCase.description}
                    </p>
                    <div className="bg-black/30 rounded-lg p-3 mb-4">
                      <p className="text-xs text-primary-light/60 italic">
                        "{useCase.example}"
                      </p>
                    </div>
                    <ul className="space-y-1">
                      {useCase.outcomes.map((outcome, idx) => (
                        <li key={idx} className="text-xs text-indigo-400">
                          • {outcome}
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Live System Status */}
        <section className="py-16 px-6">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="glass-panel p-8 rounded-2xl"
            >
              <div className="flex items-center justify-between mb-8">
                <h2 className="font-light text-3xl md:text-4xl gradient-text">
                  Live Dream System Status
                </h2>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-green-400">Systems Active</span>
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                {systemStatus.map((system, index) => (
                  <motion.div
                    key={system.component}
                    initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: index * 0.1 }}
                    className="border border-white/10 rounded-lg p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-lg">{system.component}</h3>
                      <span className={`px-2 py-1 text-xs rounded ${
                        system.status === 'Operational' ? 'bg-green-500/20 text-green-400' :
                        system.status === 'Active' ? 'bg-blue-500/20 text-blue-400' :
                        system.status === 'Optimizing' ? 'bg-orange-500/20 text-orange-400' :
                        'bg-purple-500/20 text-purple-400'
                      }`}>
                        {system.status}
                      </span>
                    </div>
                    <div className="mb-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Health Score</span>
                        <span>{system.health}%</span>
                      </div>
                      <div className="w-full bg-gray-800 rounded-full h-2">
                        <div 
                          className="h-2 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600" 
                          style={{ width: `${system.health}%` }}
                        />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Technical Integration */}
        <section className="py-16 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="glass-panel p-12 rounded-2xl"
            >
              <h2 className="font-light text-3xl md:text-4xl mb-8 text-center gradient-text">
                Trinity Framework Integration
              </h2>
              
              <div className="grid md:grid-cols-3 gap-8">
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-identity/20 mb-4">
                    <Eye className="w-8 h-8 text-trinity-identity" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Identity Integration</h3>
                  <p className="text-sm text-primary-light/70">
                    Dreams are authenticated and personalized through ΛiD system, 
                    ensuring dream scenarios align with user context and access levels.
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-consciousness/20 mb-4">
                    <Brain className="w-8 h-8 text-trinity-consciousness" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Consciousness Sync</h3>
                  <p className="text-sm text-primary-light/70">
                    Dream insights automatically propagate to memory and reasoning systems,
                    creating seamless consciousness enhancement through exploration.
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-guardian/20 mb-4">
                    <Shield className="w-8 h-8 text-trinity-guardian" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Guardian Oversight</h3>
                  <p className="text-sm text-primary-light/70">
                    All dream scenarios undergo real-time ethical validation with 
                    causality tracking and compliance verification for enterprise safety.
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="glass-panel p-8 rounded-2xl"
            >
              <h2 className="font-light text-3xl md:text-4xl mb-6 gradient-text">
                Explore Consciousness Through Dreams
              </h2>
              <p className="text-lg text-primary-light/70 mb-8 leading-relaxed">
                Experience strategic exploration through consciousness-driven scenario modeling, 
                where dreams become the laboratory for tomorrow's decisions.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/api">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all duration-300"
                  >
                    Dream API Access
                  </motion.button>
                </Link>
                <Link href="/docs">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-primary-light/20 text-primary-light rounded-xl hover:bg-primary-light/5 transition-all duration-300"
                  >
                    Technical Documentation
                  </motion.button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}