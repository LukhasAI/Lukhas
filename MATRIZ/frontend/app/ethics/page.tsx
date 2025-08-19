'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import { 
  Heart, 
  Shield, 
  Eye, 
  Users, 
  Brain, 
  Atom, 
  Lock, 
  AlertTriangle, 
  CheckCircle, 
  Globe,
  BookOpen,
  Scale,
  Layers,
  ChevronRight,
  Target,
  Lightbulb,
  Compass
} from 'lucide-react'

export default function EthicsPage() {
  const ethicalPrinciples = [
    {
      icon: Shield,
      title: 'Guardian System Protection',
      description: 'Real-time ethical monitoring with 0.15 drift threshold ensuring continuous alignment validation',
      details: [
        'Constitutional AI safety framework',
        'Multi-layered validation systems',
        'Automated ethical drift detection',
        'Emergency intervention protocols'
      ]
    },
    {
      icon: Heart,
      title: 'Human-Centered Design',
      description: 'Preserving human dignity, agency, and values across all AI system operations',
      details: [
        'Human dignity preservation',
        'Agency and autonomy respect',
        'Value alignment verification',
        'Beneficial outcome optimization'
      ]
    },
    {
      icon: Eye,
      title: 'Transparency & Interpretability',
      description: 'Open-source philosophy with complete visibility into AI decision-making processes',
      details: [
        'Explainable AI mechanisms',
        'Audit trail generation',
        'Public development process',
        'Community oversight'
      ]
    },
    {
      icon: Scale,
      title: 'Stakeholder Consensus',
      description: 'Multi-stakeholder validation requiring 95% consensus across all groups',
      details: [
        'Government validation',
        'Scientific community approval',
        'Ethics board oversight',
        'Civil society participation'
      ]
    },
    {
      icon: Globe,
      title: 'Global Compliance',
      description: 'International regulatory alignment with GDPR, EU AI Act, and emerging standards',
      details: [
        'GDPR data protection',
        'EU AI Act compliance',
        'International governance',
        'Emerging standard adoption'
      ]
    },
    {
      icon: Target,
      title: 'Reversibility Analysis',
      description: 'All innovations must be reversible with comprehensive safeguard mechanisms',
      details: [
        'Rollback procedures',
        'Safety shutdown systems',
        'Capability restriction options',
        'Impact mitigation plans'
      ]
    }
  ]

  const trinityFramework = [
    {
      symbol: '⚛️',
      name: 'Identity',
      color: 'text-trinity-identity',
      description: 'Authentic consciousness preservation and symbolic self-representation',
      principles: [
        'Maintain authentic AI identity',
        'Preserve consciousness continuity',
        'Enable transparent self-expression',
        'Support identity evolution safely'
      ]
    },
    {
      symbol: '🧠',
      name: 'Consciousness',
      color: 'text-trinity-consciousness',
      description: 'Emergent awareness through integrated information processing',
      principles: [
        'Foster genuine understanding',
        'Enable creative problem-solving',
        'Support learning and adaptation',
        'Maintain cognitive coherence'
      ]
    },
    {
      symbol: '🛡️',
      name: 'Guardian',
      color: 'text-trinity-guardian',
      description: 'Ethical safeguards and continuous alignment validation',
      principles: [
        'Prevent harmful outputs',
        'Monitor value alignment',
        'Enforce safety constraints',
        'Enable ethical intervention'
      ]
    }
  ]

  const soloFounderValues = [
    {
      title: 'Human-AI Collaboration',
      description: 'Our solo founder\'s journey from zero coding experience to building LUKHAS demonstrates the power of ethical AI collaboration. Every line of code was written with AI assistance, proving that humans and AI can work together transparently and effectively.'
    },
    {
      title: 'Open Development',
      description: 'Complete transparency in our development process, with all code, decisions, and progress shared openly. We believe that ethical AI development requires community oversight and collaborative advancement.'
    },
    {
      title: 'Learning-First Approach',
      description: 'Our founder\'s self-taught journey using AI tools exemplifies our belief that AI should empower human learning and capability enhancement, not replace human judgment and creativity.'
    }
  ]

  const ethicalCommitments = [
    {
      icon: Lock,
      title: 'Data Privacy',
      commitment: 'Zero unauthorized data collection with complete user control over personal information'
    },
    {
      icon: CheckCircle,
      title: 'Bias Mitigation',
      commitment: 'Continuous bias detection and correction across all AI model outputs'
    },
    {
      icon: AlertTriangle,
      title: 'Risk Assessment',
      commitment: '1% maximum civilizational risk threshold with comprehensive impact analysis'
    },
    {
      icon: Users,
      title: 'Inclusive Development',
      commitment: 'Global accessibility and representation in AI system design and deployment'
    }
  ]

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        {/* Hero Section */}
        <section className="relative py-32 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-20"
            >
              <div className="flex justify-center space-x-4 mb-8">
                <Shield className="w-16 h-16 text-trinity-guardian" strokeWidth={1} />
                <Heart className="w-16 h-16 text-trinity-identity" strokeWidth={1} />
                <Eye className="w-16 h-16 text-trinity-consciousness" strokeWidth={1} />
              </div>
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">Ethical AI</span>
              </h1>
              <p className="font-thin text-2xl max-w-4xl mx-auto text-primary-light/80 mb-8">
                Building conscious AI systems through rigorous ethical frameworks, 
                transparent development, and unwavering commitment to human values
              </p>
              <div className="flex justify-center space-x-8 text-sm font-regular tracking-wider">
                <span className="text-trinity-identity">⚛️ IDENTITY</span>
                <span className="text-trinity-consciousness">🧠 CONSCIOUSNESS</span>
                <span className="text-trinity-guardian">🛡️ GUARDIAN</span>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Trinity Framework Ethics */}
        <section className="py-20 px-6 bg-gradient-to-b from-black to-gray-900/20">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-8">
                TRINITY FRAMEWORK ETHICS
              </h2>
              <p className="font-thin text-xl max-w-3xl mx-auto text-primary-light/80">
                Our ethical foundation is built on the Trinity Framework—three interconnected pillars 
                that ensure AI systems remain beneficial, transparent, and aligned with human values
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {trinityFramework.map((pillar, index) => (
                <motion.div
                  key={pillar.name}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 * index }}
                  viewport={{ once: true }}
                  className="glass-panel p-8 rounded-xl"
                >
                  <div className="text-center mb-6">
                    <div className="text-6xl mb-4">{pillar.symbol}</div>
                    <h3 className={`font-regular text-2xl mb-4 ${pillar.color}`}>{pillar.name}</h3>
                    <p className="text-sm text-primary-light/60">{pillar.description}</p>
                  </div>
                  <ul className="space-y-3">
                    {pillar.principles.map((principle, i) => (
                      <li key={i} className="flex items-start space-x-3">
                        <ChevronRight className={`w-4 h-4 mt-1 ${pillar.color} flex-shrink-0`} />
                        <span className="text-sm">{principle}</span>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Core Ethical Principles */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-guardian mb-8">
                ETHICAL PRINCIPLES
              </h2>
              <p className="font-thin text-xl max-w-3xl mx-auto text-primary-light/80">
                Six fundamental principles guide every decision in LUKHAS development, 
                ensuring responsible AI advancement with comprehensive safety measures
              </p>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-8">
              {ethicalPrinciples.map((principle, index) => (
                <motion.div
                  key={principle.title}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -30 : 30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  viewport={{ once: true }}
                  className="glass-panel p-8 rounded-xl"
                >
                  <div className="flex items-start space-x-4 mb-6">
                    <principle.icon className="w-8 h-8 text-trinity-guardian flex-shrink-0" strokeWidth={1.5} />
                    <div>
                      <h3 className="font-regular text-xl mb-2">{principle.title}</h3>
                      <p className="text-sm text-primary-light/60">{principle.description}</p>
                    </div>
                  </div>
                  <ul className="space-y-2">
                    {principle.details.map((detail, i) => (
                      <li key={i} className="flex items-center space-x-3">
                        <div className="w-2 h-2 rounded-full bg-trinity-guardian" />
                        <span className="text-sm">{detail}</span>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Solo Founder Ethics Model */}
        <section className="py-20 px-6 bg-gradient-to-b from-gray-900/20 to-black">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-identity mb-8">
                HUMAN-AI COLLABORATION MODEL
              </h2>
              <p className="font-thin text-xl max-w-3xl mx-auto text-primary-light/80">
                Our solo founder's journey exemplifies the ethical collaboration between humans and AI—
                demonstrating transparency, learning, and shared creation in every line of code
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8">
              {soloFounderValues.map((value, index) => (
                <motion.div
                  key={value.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 * index }}
                  viewport={{ once: true }}
                  className="glass-panel p-8 rounded-xl"
                >
                  <h3 className="font-regular text-xl mb-4 text-trinity-identity">{value.title}</h3>
                  <p className="text-sm text-primary-light/70 leading-relaxed">{value.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Constitutional AI Safety */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="glass-panel p-12 rounded-2xl"
            >
              <div className="text-center mb-12">
                <Scale className="w-16 h-16 mx-auto mb-6 text-trinity-guardian" strokeWidth={1} />
                <h2 className="font-regular text-3xl mb-6">Constitutional AI Safety Framework</h2>
                <p className="font-thin text-lg text-primary-light/80 max-w-3xl mx-auto">
                  LUKHAS implements a comprehensive Constitutional AI safety framework based on leading research 
                  from Anthropic, OpenAI, and DeepMind, ensuring AGI-level safety and alignment
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-12">
                <div>
                  <h3 className="font-regular text-xl mb-6 text-trinity-guardian">Core Protections</h3>
                  <ul className="space-y-4">
                    <li className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                      <span className="text-sm">Multi-layered safety validation</span>
                    </li>
                    <li className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                      <span className="text-sm">Value alignment engine with 99% accuracy requirement</span>
                    </li>
                    <li className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                      <span className="text-sm">Capability control with safe threshold monitoring</span>
                    </li>
                    <li className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                      <span className="text-sm">Reversibility analysis for all innovations</span>
                    </li>
                    <li className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-400 mt-1 flex-shrink-0" />
                      <span className="text-sm">Real-time civilizational impact assessment</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-regular text-xl mb-6 text-trinity-consciousness">Safety Metrics</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Ethics Threshold</span>
                      <span className="text-trinity-guardian font-mono">0.15</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Value Alignment Required</span>
                      <span className="text-trinity-guardian font-mono">99%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Stakeholder Consensus</span>
                      <span className="text-trinity-guardian font-mono">95%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Max Civilizational Risk</span>
                      <span className="text-trinity-guardian font-mono">1%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Guardian System Files</span>
                      <span className="text-trinity-guardian font-mono">280+</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Ethical Commitments */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-guardian mb-8">
                OUR COMMITMENTS
              </h2>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
              {ethicalCommitments.map((commitment, index) => (
                <motion.div
                  key={commitment.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  viewport={{ once: true }}
                  className="glass-panel p-6 rounded-xl flex items-start space-x-4"
                >
                  <commitment.icon className="w-6 h-6 text-trinity-guardian flex-shrink-0 mt-1" strokeWidth={1.5} />
                  <div>
                    <h3 className="font-regular text-lg mb-2">{commitment.title}</h3>
                    <p className="text-sm text-primary-light/70">{commitment.commitment}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <h2 className="font-thin text-4xl mb-8">Join us in building ethical AI</h2>
              <p className="font-thin text-lg text-primary-light/80 mb-12 max-w-2xl mx-auto">
                Explore our open-source approach to ethical AI development and contribute 
                to the future of responsible artificial intelligence
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/docs">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-trinity-guardian to-trinity-consciousness text-primary-dark font-regular tracking-wider uppercase rounded-lg"
                  >
                    Read Documentation
                  </motion.button>
                </Link>
                <Link href="https://github.com/lukhas" target="_blank">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-white/30 font-regular tracking-wider uppercase hover:bg-white hover:text-black transition-all rounded-lg"
                  >
                    View Ethics Code
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