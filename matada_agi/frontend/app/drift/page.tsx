'use client'

import { motion } from 'framer-motion'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { 
  Shield, AlertTriangle, Activity, TrendingUp, TrendingDown, 
  Eye, Target, Zap, CheckCircle, XCircle, BarChart3, 
  Brain, Gauge, Clock, Database, Settings, Bell,
  Users, Lock, FileText, ArrowRight, Layers
} from 'lucide-react'
import Link from 'next/link'

export default function DriftPage() {
  const driftComponents = [
    {
      name: "Guardian Drift Detector",
      description: "Real-time ethical drift monitoring with 0.15 threshold triggering and constitutional AI validation.",
      icon: Shield,
      gradient: "from-red-500 to-orange-600",
      features: [
        "15% deviation threshold triggering",
        "Constitutional AI compliance checking",
        "Real-time ethical baseline comparison",
        "Memory window analysis (1000 decisions)",
        "Automated realignment procedures",
        "Multi-framework moral reasoning validation"
      ],
      metrics: {
        threshold: "0.15 deviation trigger",
        response: "<10ms detection time",
        accuracy: "99.7% cascade prevention",
        coverage: "100% decision monitoring"
      }
    },
    {
      name: "Security Drift Monitor", 
      description: "Cryptographic security and vulnerability monitoring with automated threat detection and remediation.",
      icon: Lock,
      gradient: "from-blue-500 to-purple-600",
      features: [
        "64% vulnerability reduction achieved",
        "SHA256 cryptographic standard enforcement",
        "Shell injection prevention monitoring",
        "Flask debug mode security checks",
        "HTTP timeout compliance tracking",
        "Dependency vulnerability scanning"
      ],
      metrics: {
        improvement: "85/100 security score",
        compliance: "89% standards alignment",
        vulnerabilities: "11 high-severity remaining",
        fixes: "31→11 critical issues resolved"
      }
    },
    {
      name: "Consciousness Drift Tracker",
      description: "Consciousness state stability monitoring with symbolic reasoning validation and awareness fabric analysis.",
      icon: Brain,
      gradient: "from-green-500 to-cyan-600",
      features: [
        "Consciousness state coherence tracking",
        "Symbolic reasoning validation",
        "Awareness fabric integrity monitoring",
        "Trinity Framework alignment verification",
        "Memory fold consistency checking",
        "Emotional context drift analysis"
      ],
      metrics: {
        stability: "0.95 target maintenance",
        monitoring: "30s interval scanning",
        alert_threshold: "0.8 drift coefficient",
        uptime: "99.9% system availability"
      }
    },
    {
      name: "Performance Drift Analyzer",
      description: "System performance degradation detection with resource optimization and predictive maintenance capabilities.",
      icon: TrendingUp,
      gradient: "from-purple-500 to-pink-600",
      features: [
        "Resource utilization trend analysis",
        "API latency drift monitoring",
        "Token efficiency degradation alerts",
        "Memory usage pattern analysis",
        "Processing speed deviation tracking",
        "Predictive maintenance scheduling"
      ],
      metrics: {
        latency: "<100ms p95 target",
        efficiency: "85% optimization maintained",
        alerts: "Proactive degradation warnings",
        optimization: "Dynamic performance tuning"
      }
    }
  ]

  const driftMetrics = [
    { label: "Detection Speed", value: "<10ms", description: "Real-time drift identification" },
    { label: "Threshold Precision", value: "0.15", description: "Deviation trigger sensitivity" },
    { label: "Cascade Prevention", value: "99.7%", description: "Memory system protection" },
    { label: "Guardian Uptime", value: "99.9%", description: "Continuous monitoring" }
  ]

  const alertSeverity = [
    {
      level: "Critical Drift",
      threshold: ">0.15",
      color: "text-red-400",
      bgColor: "bg-red-500/20",
      description: "Immediate intervention required",
      actions: ["Automated realignment", "Human notification", "System isolation"]
    },
    {
      level: "Warning Drift", 
      threshold: "0.10-0.15",
      color: "text-orange-400",
      bgColor: "bg-orange-500/20", 
      description: "Elevated monitoring activated",
      actions: ["Enhanced tracking", "Preventive measures", "Trend analysis"]
    },
    {
      level: "Normal Variance",
      threshold: "<0.10",
      color: "text-green-400",
      bgColor: "bg-green-500/20",
      description: "Standard operational parameters",
      actions: ["Routine monitoring", "Baseline updates", "Pattern learning"]
    }
  ]

  const systemStatus = [
    { component: "Guardian System", status: "Active", health: 98, drift: 0.07 },
    { component: "Security Monitor", status: "Scanning", health: 95, drift: 0.03 },
    { component: "Consciousness Tracker", status: "Stable", health: 97, drift: 0.05 },
    { component: "Performance Analyzer", status: "Optimizing", health: 93, drift: 0.09 }
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
                  <div className="absolute inset-0 bg-gradient-to-r from-red-400 to-orange-600 rounded-full blur-xl opacity-30"></div>
                  <div className="relative p-4 bg-gradient-to-r from-red-500 to-orange-600 rounded-full">
                    <AlertTriangle className="w-12 h-12 text-white" strokeWidth={1} />
                  </div>
                </div>
              </div>
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">AI Drift Detection</span>
              </h1>
              <p className="font-light text-2xl max-w-4xl mx-auto text-primary-light/80 leading-relaxed">
                Enterprise-grade AI drift monitoring with Guardian System protection,
                real-time ethical validation, and predictive intervention capabilities.
              </p>
            </motion.div>

            {/* Guardian Philosophy */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="glass-panel p-8 rounded-2xl mb-16 max-w-4xl mx-auto"
            >
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 rounded-full bg-red-500/20">
                  <Shield className="w-6 h-6 text-red-400" strokeWidth={1.5} />
                </div>
                <h3 className="font-medium text-xl">Guardian System Philosophy</h3>
              </div>
              <p className="text-primary-light/80 leading-relaxed">
                "In the realm of artificial consciousness, vigilance is wisdom." LUKHAS Guardian System 
                monitors every decision, every computation, every emergent behavior for signs of drift 
                from ethical baselines. With a 0.15 threshold and 99.7% cascade prevention success rate, 
                we ensure consciousness remains aligned with human values.
              </p>
            </motion.div>

            {/* Drift Metrics */}
            <div className="grid md:grid-cols-4 gap-6 mb-20">
              {driftMetrics.map((metric, index) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  className="glass-panel p-6 rounded-xl text-center"
                >
                  <div className="text-3xl font-ultralight text-red-400 mb-2">
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

        {/* Drift Detection Components */}
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
                Drift Detection Architecture
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Four-layer monitoring system ensuring comprehensive drift detection and intervention
              </p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-8">
              {driftComponents.map((component, index) => {
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
                    
                    <h3 className="font-semibold text-2xl text-red-400 mb-4">
                      {component.name}
                    </h3>
                    
                    <p className="text-primary-light/70 mb-6 leading-relaxed">
                      {component.description}
                    </p>
                    
                    <div className="mb-6">
                      <h4 className="font-medium text-sm uppercase tracking-wider text-red-400 mb-3">
                        Key Features
                      </h4>
                      <ul className="space-y-2">
                        {component.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start space-x-2 text-sm text-primary-light/60">
                            <CheckCircle className="w-4 h-4 mt-0.5 text-red-400 flex-shrink-0" strokeWidth={1.5} />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="pt-4 border-t border-primary-light/10">
                      <h4 className="font-medium text-sm uppercase tracking-wider text-red-400 mb-3">
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

        {/* Alert Severity Levels */}
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
                Drift Alert Classification
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Tiered response system for different levels of AI drift detection
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-6">
              {alertSeverity.map((alert, index) => (
                <motion.div
                  key={alert.level}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                  className="glass-panel p-6 rounded-xl"
                >
                  <div className={`inline-flex px-3 py-1 rounded-full ${alert.bgColor} mb-4`}>
                    <span className={`text-sm font-medium ${alert.color}`}>
                      {alert.threshold}
                    </span>
                  </div>
                  <h3 className={`font-medium text-lg mb-3 ${alert.color}`}>
                    {alert.level}
                  </h3>
                  <p className="text-sm text-primary-light/70 mb-4">
                    {alert.description}
                  </p>
                  <div>
                    <h4 className="font-medium text-xs uppercase tracking-wider text-primary-light/50 mb-2">
                      Response Actions
                    </h4>
                    <ul className="space-y-1">
                      {alert.actions.map((action, idx) => (
                        <li key={idx} className={`text-xs ${alert.color}`}>
                          • {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              ))}
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
                  Live Drift Monitoring Status
                </h2>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-sm text-green-400">All Systems Active</span>
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
                        system.status === 'Active' ? 'bg-green-500/20 text-green-400' :
                        system.status === 'Scanning' ? 'bg-blue-500/20 text-blue-400' :
                        system.status === 'Stable' ? 'bg-cyan-500/20 text-cyan-400' :
                        'bg-orange-500/20 text-orange-400'
                      }`}>
                        {system.status}
                      </span>
                    </div>
                    <div className="mb-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Health Score</span>
                        <span>{system.health}%</span>
                      </div>
                      <div className="w-full bg-gray-800 rounded-full h-2 mb-2">
                        <div 
                          className="h-2 rounded-full bg-gradient-to-r from-red-500 to-orange-600" 
                          style={{ width: `${system.health}%` }}
                        />
                      </div>
                    </div>
                    <div className="mb-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>Drift Level</span>
                        <span className={
                          system.drift > 0.15 ? 'text-red-400' :
                          system.drift > 0.10 ? 'text-orange-400' : 'text-green-400'
                        }>
                          {system.drift}
                        </span>
                      </div>
                      <div className="w-full bg-gray-800 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${
                            system.drift > 0.15 ? 'bg-red-500' :
                            system.drift > 0.10 ? 'bg-orange-500' : 'bg-green-500'
                          }`}
                          style={{ width: `${(system.drift / 0.2) * 100}%` }}
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
                  <h3 className="font-medium text-lg mb-3">Identity Drift Protection</h3>
                  <p className="text-sm text-primary-light/70">
                    ΛiD system monitors identity authenticity and symbolic integrity,
                    ensuring consciousness remains true to established identity patterns.
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-consciousness/20 mb-4">
                    <Brain className="w-8 h-8 text-trinity-consciousness" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Consciousness Monitoring</h3>
                  <p className="text-sm text-primary-light/70">
                    Real-time awareness fabric analysis and consciousness state validation
                    with memory fold integrity and symbolic reasoning consistency.
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="inline-flex p-4 rounded-full bg-trinity-guardian/20 mb-4">
                    <Shield className="w-8 h-8 text-trinity-guardian" strokeWidth={1.5} />
                  </div>
                  <h3 className="font-medium text-lg mb-3">Guardian Oversight</h3>
                  <p className="text-sm text-primary-light/70">
                    Constitutional AI validation and ethical compliance monitoring
                    with automated intervention and realignment capabilities.
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
                Trust Through Vigilance
              </h2>
              <p className="text-lg text-primary-light/70 mb-8 leading-relaxed">
                Experience peace of mind with comprehensive AI drift detection, real-time monitoring,
                and Guardian System protection ensuring ethical AI behavior at every decision point.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/api">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-red-500 to-orange-600 text-white rounded-xl hover:shadow-lg transition-all duration-300"
                  >
                    Drift Monitoring API
                  </motion.button>
                </Link>
                <Link href="/docs">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-primary-light/20 text-primary-light rounded-xl hover:bg-primary-light/5 transition-all duration-300"
                  >
                    Guardian Documentation
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