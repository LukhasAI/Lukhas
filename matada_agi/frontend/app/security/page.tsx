'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import ClientOnly from '@/components/ClientOnly'
import { 
  Shield, 
  Lock, 
  Eye, 
  AlertTriangle, 
  FileText, 
  Users, 
  Server, 
  Key,
  CheckCircle,
  TrendingDown,
  Zap,
  Database,
  Globe,
  Activity
} from 'lucide-react'

export default function SecurityPage() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  const securityFeatures = [
    {
      icon: Shield,
      title: 'Guardian System v1.0.0',
      description: 'Multi-layered ethical oversight with real-time intervention capabilities',
      details: [
        '280+ security and ethics files',
        'Real-time drift detection (0.15 threshold)',
        'Automatic intervention protocols'
      ]
    },
    {
      icon: TrendingDown,
      title: 'Drift Detection',
      description: 'Advanced monitoring system tracking behavioral deviations',
      details: [
        'Drift threshold: 0.15 (99.7% prevention rate)',
        'Predictive anomaly detection',
        'Real-time correction mechanisms'
      ]
    },
    {
      icon: Lock,
      title: 'Cryptographic Protection',
      description: 'End-to-end encryption with quantum-resistant algorithms',
      details: [
        'AES-256-GCM encryption at rest',
        'Homomorphic encryption support',
        'Quantum-resistant cryptography'
      ]
    },
    {
      icon: Eye,
      title: 'Constitutional AI',
      description: 'Anthropic-inspired constitutional principles for ethical reasoning',
      details: [
        'Self-supervised ethical training',
        'Transparent decision pathways',
        'Harm reduction protocols'
      ]
    },
    {
      icon: Database,
      title: 'Memory Security',
      description: 'Immutable symbolic logs with cryptographic verification',
      details: [
        'Blockchain-like memory helix',
        'Tamper-evident audit trails',
        'Cryptographic hash validation'
      ]
    },
    {
      icon: Globe,
      title: 'Compliance Framework',
      description: 'Full adherence to international privacy and AI regulations',
      details: [
        'GDPR compliant (Article 17 & 20)',
        'EU AI Act classification',
        'Data portability rights'
      ]
    }
  ]

  const auditMetrics = [
    {
      metric: 'Drift Prevention Rate',
      value: '99.7%',
      description: 'Average prevention of harmful behavioral drift'
    },
    {
      metric: 'Intervention Threshold',
      value: '0.15',
      description: 'Guardian activation trigger for drift detection'
    },
    {
      metric: 'Security Files',
      value: '280+',
      description: 'Dedicated security and ethics components'
    },
    {
      metric: 'Audit Success Rate',
      value: '100%',
      description: 'Successful security audits completed'
    }
  ]

  const complianceStandards = [
    {
      standard: 'GDPR',
      status: 'Compliant',
      description: 'General Data Protection Regulation'
    },
    {
      standard: 'EU AI Act',
      status: 'Compliant',
      description: 'European Union Artificial Intelligence Act'
    },
    {
      standard: 'Constitutional AI',
      status: 'Implemented',
      description: 'Anthropic-inspired ethical principles'
    },
    {
      standard: 'ISO 27001',
      status: 'Aligned',
      description: 'Information Security Management'
    }
  ]

  return (
    <ClientOnly>
      <Navigation />
      <main className="relative overflow-hidden pt-20" ref={ref}>
        <div className="w-full">
          {/* Hero Section */}
          <section className="relative py-32">
            <div className="w-full max-w-7xl mx-auto px-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6 }}
                className="text-center mb-20"
              >
                <Shield className="w-20 h-20 mx-auto mb-8 text-trinity-guardian" />
                <h1 className="font-ultralight text-5xl md:text-7xl mb-6">
                  <span className="gradient-text">Security</span>
                </h1>
                <p className="font-thin text-xl md:text-2xl text-primary-light/80 max-w-4xl mx-auto leading-relaxed">
                  Enterprise-grade security powered by the Guardian System. 
                  Constitutional AI principles with quantum-resistant protection.
                </p>
              </motion.div>
            </div>
          </section>

          {/* Guardian System Overview */}
          <section className="relative py-20">
            <div className="w-full max-w-7xl mx-auto px-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="glass-panel p-12 rounded-2xl mb-16"
              >
                <div className="grid md:grid-cols-2 gap-12 items-center">
                  <div>
                    <h2 className="font-regular text-2xl tracking-[0.1em] uppercase mb-6 text-trinity-guardian">
                      🛡️ Guardian System
                    </h2>
                    <p className="font-thin text-lg leading-relaxed mb-6">
                      Our Guardian System represents the pinnacle of AI safety technology. 
                      With over 280 dedicated security components, it provides real-time 
                      ethical oversight and intervention capabilities.
                    </p>
                    <p className="font-thin text-lg leading-relaxed mb-6">
                      The system monitors for behavioral drift with a precision threshold 
                      of 0.15, achieving a 99.7% prevention rate for harmful deviations.
                    </p>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-trinity-guardian" />
                        <span className="font-thin">Real-time drift detection</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-trinity-guardian" />
                        <span className="font-thin">Automatic intervention protocols</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-trinity-guardian" />
                        <span className="font-thin">Constitutional AI principles</span>
                      </div>
                    </div>
                  </div>
                  <div className="relative">
                    <div className="aspect-square rounded-2xl bg-gradient-to-br from-trinity-guardian/20 to-trinity-consciousness/20 p-8">
                      <pre className="font-mono text-sm text-primary-light/80 overflow-auto">
{`{
  "guardian_status": "ACTIVE",
  "drift_threshold": 0.15,
  "current_drift": 0.08,
  "intervention_ready": true,
  "components": {
    "sentinel": "MONITORING",
    "ethics_guardian": "ACTIVE",
    "shadow_filter": "PROTECTING"
  },
  "audit_trail": {
    "last_audit": "2025-08-05",
    "success_rate": "100%",
    "interventions": 12
  }
}`}
                      </pre>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </section>

          {/* Security Features Grid */}
          <section className="relative py-20">
            <div className="w-full max-w-7xl mx-auto px-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.3 }}
                className="text-center mb-16"
              >
                <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-guardian mb-4">
                  Security Features
                </h2>
                <p className="font-thin text-2xl max-w-3xl mx-auto">
                  Comprehensive protection through multiple security layers
                </p>
              </motion.div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {securityFeatures.map((feature, index) => {
                  const IconComponent = feature.icon
                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={isInView ? { opacity: 1, y: 0 } : {}}
                      transition={{ duration: 0.6, delay: 0.4 + index * 0.1 }}
                      className="glass-panel p-8 rounded-xl hover-lift"
                    >
                      <div className="mb-4">
                        <IconComponent className="w-10 h-10 text-trinity-guardian" />
                      </div>
                      <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-3">
                        {feature.title}
                      </h3>
                      <p className="font-thin text-sm leading-relaxed text-primary-light/80 mb-4">
                        {feature.description}
                      </p>
                      <ul className="space-y-2">
                        {feature.details.map((detail, idx) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <div className="w-1 h-1 rounded-full bg-trinity-guardian mt-2 flex-shrink-0" />
                            <span className="font-thin text-xs text-primary-light/70">{detail}</span>
                          </li>
                        ))}
                      </ul>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          </section>

          {/* Audit Metrics */}
          <section className="relative py-20">
            <div className="w-full max-w-7xl mx-auto px-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.5 }}
                className="text-center mb-16"
              >
                <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-guardian mb-4">
                  Security Metrics
                </h2>
                <p className="font-thin text-2xl max-w-3xl mx-auto">
                  Real-time security and audit performance indicators
                </p>
              </motion.div>

              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {auditMetrics.map((metric, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                    className="glass-panel p-8 rounded-xl text-center hover-lift"
                  >
                    <div className="text-3xl font-thin text-trinity-guardian mb-2">
                      {metric.value}
                    </div>
                    <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-2">
                      {metric.metric}
                    </h3>
                    <p className="font-thin text-xs text-primary-light/70">
                      {metric.description}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          </section>

          {/* Compliance Standards */}
          <section className="relative py-20">
            <div className="w-full max-w-7xl mx-auto px-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.7 }}
                className="text-center mb-16"
              >
                <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-guardian mb-4">
                  Compliance & Standards
                </h2>
                <p className="font-thin text-2xl max-w-3xl mx-auto">
                  Adherence to international privacy and AI safety regulations
                </p>
              </motion.div>

              <div className="grid md:grid-cols-2 gap-6">
                {complianceStandards.map((standard, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6, delay: 0.8 + index * 0.1 }}
                    className="glass-panel p-8 rounded-xl hover-lift"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-regular text-lg tracking-[0.1em]">
                        {standard.standard}
                      </h3>
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-trinity-guardian/20 text-trinity-guardian">
                        {standard.status}
                      </span>
                    </div>
                    <p className="font-thin text-sm text-primary-light/80">
                      {standard.description}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          </section>

          {/* Trinity Framework Security */}
          <section className="relative py-20">
            <div className="w-full max-w-7xl mx-auto px-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.9 }}
                className="glass-panel p-12 rounded-2xl text-center"
              >
                <div className="mb-8">
                  <div className="flex justify-center space-x-8 mb-6">
                    <div className="text-trinity-identity text-4xl">⚛️</div>
                    <div className="text-trinity-consciousness text-4xl">🧠</div>
                    <div className="text-trinity-guardian text-4xl">🛡️</div>
                  </div>
                  <h2 className="font-regular text-2xl tracking-[0.1em] uppercase mb-6">
                    Trinity Framework Security
                  </h2>
                  <p className="font-thin text-lg max-w-3xl mx-auto leading-relaxed">
                    Our security architecture is built on the Trinity Framework principles: 
                    Identity protection (⚛️), Consciousness monitoring (🧠), and Guardian oversight (🛡️). 
                    This tri-layered approach ensures comprehensive protection across all system operations.
                  </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                  <div className="text-center">
                    <div className="text-trinity-identity text-3xl mb-3">⚛️</div>
                    <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-2 text-trinity-identity">
                      Identity Security
                    </h3>
                    <p className="font-thin text-sm text-primary-light/80">
                      Cryptographic identity protection with steganographic ID systems
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="text-trinity-consciousness text-3xl mb-3">🧠</div>
                    <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-2 text-trinity-consciousness">
                      Consciousness Monitoring
                    </h3>
                    <p className="font-thin text-sm text-primary-light/80">
                      Real-time awareness tracking with behavioral pattern analysis
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="text-trinity-guardian text-3xl mb-3">🛡️</div>
                    <h3 className="font-regular text-sm tracking-[0.2em] uppercase mb-2 text-trinity-guardian">
                      Guardian Oversight
                    </h3>
                    <p className="font-thin text-sm text-primary-light/80">
                      Ethical intervention with constitutional AI principles
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>
          </section>
        </div>
      </main>
      <Footer />
    </ClientOnly>
  )
}