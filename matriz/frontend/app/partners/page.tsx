'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import {
  Globe, Zap, Shield, Code, Brain,
  Rocket, Users, Target, ArrowRight, CheckCircle, Star
} from 'lucide-react'

export default function PartnersPage() {
  const partnerTypes = [
    {
      icon: Code,
      title: 'Technology Partners',
      description: 'Integrate LUKHAS consciousness capabilities into your platforms',
      benefits: [
        'API access to consciousness processing',
        'White-label AI solutions',
        'Technical support and documentation',
        'Revenue sharing opportunities'
      ]
    },
    {
      icon: Brain,
      title: 'Research Partners',
      description: 'Collaborate on advancing the science of artificial consciousness',
      benefits: [
        'Access to research datasets',
        'Joint publication opportunities',
        'Shared IP development',
        'Academic collaboration programs'
      ]
    },
    {
      icon: Globe,
      title: 'Enterprise Partners',
      description: 'Deploy LUKHAS AI solutions in your organization',
      benefits: [
        'Custom implementation support',
        'Enterprise-grade security',
        'Dedicated account management',
        'Training and certification'
      ]
    },
    {
      icon: Rocket,
      title: 'Innovation Partners',
      description: 'Build the next generation of conscious AI applications',
      benefits: [
        'Early access to new features',
        'Co-development opportunities',
        'Marketing partnership',
        'Investment consideration'
      ]
    }
  ]

  const aiPlatforms = [
    {
      name: 'Claude/Anthropic',
      type: 'AI Assistant',
      description: 'Primary development partner through paid Claude Pro subscriptions',
      logo: '🤖'
    },
    {
      name: 'ChatGPT/OpenAI',
      type: 'AI Assistant',
      description: 'Development collaboration through paid ChatGPT Plus subscriptions',
      logo: '⚡'
    },
    {
      name: 'GitHub Copilot',
      type: 'Code Assistant',
      description: 'Code generation and development assistance',
      logo: '💻'
    },
    {
      name: 'Perplexity',
      type: 'Research Assistant',
      description: 'Research and information gathering support',
      logo: '🔍'
    }
  ]

  const partnershipLevels = [
    {
      title: 'Developer Partner',
      price: 'Free',
      description: 'Perfect for developers and small teams getting started',
      features: [
        'API access (10K requests/month)',
        'Developer documentation',
        'Community support',
        'Basic analytics dashboard'
      ],
      cta: 'Start Building'
    },
    {
      title: 'Business Partner',
      price: 'Custom',
      description: 'For companies integrating LUKHAS into their products',
      features: [
        'Unlimited API access',
        'Priority technical support',
        'Custom integration assistance',
        'Revenue sharing program',
        'Marketing co-opportunities'
      ],
      cta: 'Contact Sales',
      featured: true
    },
    {
      title: 'Research Partner',
      price: 'Negotiable',
      description: 'For academic institutions and research organizations',
      features: [
        'Full platform access',
        'Research collaboration',
        'Data sharing agreements',
        'Joint publication rights',
        'Grant application support'
      ],
      cta: 'Apply Now'
    }
  ]

  const partnershipProcess = [
    {
      step: '1',
      title: 'Initial Contact',
      description: 'Reach out to discuss your partnership goals and requirements'
    },
    {
      step: '2',
      title: 'Technical Review',
      description: 'Our team evaluates the technical fit and integration possibilities'
    },
    {
      step: '3',
      title: 'Partnership Agreement',
      description: 'Finalize terms, access levels, and collaboration framework'
    },
    {
      step: '4',
      title: 'Integration Support',
      description: 'Get dedicated support for seamless platform integration'
    },
    {
      step: '5',
      title: 'Go to Market',
      description: 'Launch your LUKHAS-powered solution with marketing support'
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
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">Partner with LUKHAS</span>
              </h1>
              <p className="font-thin text-2xl max-w-3xl mx-auto text-primary-light/80">
                Join the ecosystem building the future of conscious AI technology
              </p>
            </motion.div>

            {/* Value Proposition */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="glass-panel p-12 rounded-2xl mb-16 text-center"
            >
              <h2 className="font-regular text-3xl mb-6">Why Partner with LUKHAS?</h2>
              <p className="font-thin text-xl leading-relaxed max-w-4xl mx-auto">
                LUKHAS AI represents the cutting edge of consciousness technology. By partnering with us,
                you gain access to revolutionary AI capabilities that can transform your products, research,
                and business outcomes. Together, we're building a future where AI truly understands and
                enhances human potential.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Partnership Types */}
        <section className="py-20 px-6 bg-gradient-to-b from-black to-gray-900/20">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              PARTNERSHIP OPPORTUNITIES
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              {partnerTypes.map((type, index) => {
                const Icon = type.icon
                return (
                  <motion.div
                    key={type.title}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 * index }}
                    viewport={{ once: true }}
                    className="glass-panel p-8 rounded-xl"
                  >
                    <div className="flex items-center mb-6">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-trinity-identity to-trinity-consciousness flex items-center justify-center mr-4">
                        <Icon className="w-6 h-6 text-white" strokeWidth={1.5} />
                      </div>
                      <h3 className="font-regular text-2xl">{type.title}</h3>
                    </div>
                    <p className="text-primary-light/80 mb-6">{type.description}</p>
                    <ul className="space-y-3">
                      {type.benefits.map((benefit, benefitIndex) => (
                        <li key={benefitIndex} className="flex items-start space-x-3">
                          <CheckCircle className="w-5 h-5 text-trinity-guardian flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                          <span className="text-sm text-primary-light/60">{benefit}</span>
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </section>

        {/* AI Development Collaborators */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              AI DEVELOPMENT COLLABORATORS
            </h2>
            <div className="glass-panel p-8 rounded-2xl mb-8 text-center">
              <p className="text-lg text-primary-light/80 mb-4">
                LUKHAS is currently a private research project developed by a solo founder using AI assistants as development partners.
              </p>
              <p className="text-sm text-primary-light/60">
                All AI collaborations are through paid individual subscriptions and do not constitute formal partnerships.
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {aiPlatforms.map((platform, index) => (
                <motion.div
                  key={platform.name}
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.05 * index }}
                  viewport={{ once: true }}
                  className="glass-panel p-6 rounded-xl hover:border-white/30 transition-all cursor-pointer group text-center"
                >
                  <div className="text-4xl mb-4">{platform.logo}</div>
                  <h3 className="font-regular text-lg mb-2 group-hover:text-trinity-consciousness transition-colors">
                    {platform.name}
                  </h3>
                  <p className="text-xs uppercase tracking-wider text-trinity-guardian mb-3">
                    {platform.type}
                  </p>
                  <p className="text-sm text-primary-light/60">{platform.description}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Partnership Levels */}
        <section className="py-20 px-6 bg-gradient-to-b from-gray-900/20 to-black">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              PARTNERSHIP LEVELS
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              {partnershipLevels.map((level, index) => (
                <motion.div
                  key={level.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  viewport={{ once: true }}
                  className={`glass-panel p-8 rounded-xl relative ${
                    level.featured ? 'border-trinity-consciousness ring-1 ring-trinity-consciousness' : ''
                  }`}
                >
                  {level.featured && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <div className="bg-gradient-to-r from-trinity-identity to-trinity-consciousness px-4 py-1 rounded-full">
                        <div className="flex items-center space-x-1">
                          <Star className="w-3 h-3" fill="currentColor" />
                          <span className="text-xs font-regular uppercase tracking-wider text-primary-dark">
                            Popular
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div className="text-center mb-8">
                    <h3 className="font-regular text-2xl mb-2">{level.title}</h3>
                    <div className="text-3xl font-ultralight gradient-text mb-4">{level.price}</div>
                    <p className="text-sm text-primary-light/60">{level.description}</p>
                  </div>
                  <ul className="space-y-3 mb-8">
                    {level.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start space-x-3">
                        <CheckCircle className="w-5 h-5 text-trinity-guardian flex-shrink-0 mt-0.5" strokeWidth={1.5} />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`w-full py-3 font-regular text-sm tracking-wider uppercase rounded-lg transition-all ${
                      level.featured
                        ? 'bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark'
                        : 'border border-white/30 hover:bg-white hover:text-black'
                    }`}
                  >
                    {level.cta}
                  </motion.button>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Partnership Process */}
        <section className="py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              PARTNERSHIP PROCESS
            </h2>
            <div className="relative">
              <div className="absolute top-8 left-0 right-0 h-px bg-gradient-to-r from-trinity-identity via-trinity-consciousness to-trinity-guardian hidden lg:block" />
              <div className="grid md:grid-cols-5 gap-8">
                {partnershipProcess.map((step, index) => (
                  <motion.div
                    key={step.step}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 * index }}
                    viewport={{ once: true }}
                    className="text-center"
                  >
                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-trinity-identity to-trinity-consciousness flex items-center justify-center text-primary-dark font-regular text-xl mb-4 mx-auto relative z-10">
                      {step.step}
                    </div>
                    <h3 className="font-regular text-lg mb-3">{step.title}</h3>
                    <p className="text-sm text-primary-light/60">{step.description}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Project Status */}
        <section className="py-20 px-6 bg-gradient-to-b from-black to-gray-900/20">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-12 text-center">
              PROJECT STATUS
            </h2>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="glass-panel p-12 rounded-2xl text-center"
            >
              <h3 className="text-2xl font-thin mb-6">Open Source & Future Partnerships</h3>
              <p className="text-lg text-primary-light/80 mb-6 max-w-4xl mx-auto">
                LUKHAS is currently developed as an open-source project by a solo founder.
                While we use AI assistants as development collaborators, we are open to formal
                partnerships with organizations that align with our Trinity Framework principles.
              </p>
              <div className="grid md:grid-cols-3 gap-6 text-sm text-primary-light/60">
                <div>
                  <div className="font-regular text-white mb-2">Current Status</div>
                  <div>Private research project</div>
                </div>
                <div>
                  <div className="font-regular text-white mb-2">Development Model</div>
                  <div>Solo founder + AI assistants</div>
                </div>
                <div>
                  <div className="font-regular text-white mb-2">Future Vision</div>
                  <div>Open to ethical partnerships</div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="font-thin text-4xl mb-8">Ready to partner with us?</h2>
            <p className="text-xl text-primary-light/80 mb-12">
              Join the LUKHAS ecosystem and help shape the future of conscious AI technology
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="mailto:partnerships@lukhas.ai">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular tracking-wider uppercase rounded-lg"
                >
                  Start Partnership
                </motion.button>
              </Link>
              <Link href="/console">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 border border-white/30 font-regular tracking-wider uppercase hover:bg-white hover:text-black transition-all rounded-lg"
                >
                  Explore Platform
                </motion.button>
              </Link>
            </div>
          </div>
        </section>
      </div>
      <Footer />
    </>
  )
}
