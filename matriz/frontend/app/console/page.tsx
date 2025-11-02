'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import {
  Terminal, Database, GitBranch, Shield, Brain, Cpu,
  Globe, Book, Github, ExternalLink, Lock, Zap,
  Activity, Users, Code, Cloud
} from 'lucide-react'

export default function ConsolePage() {
  const products = [
    {
      title: 'MATADA Core',
      description: 'Access the core MATADA consciousness processing engine',
      icon: Brain,
      status: 'active',
      link: '#',
      color: 'text-trinity-consciousness',
      bgColor: 'bg-blue-600/10',
    },
    {
      title: 'VIVOX System',
      description: 'VIVOX consciousness and awareness platform',
      icon: Cpu,
      status: 'active',
      link: '#',
      color: 'text-trinity-identity',
      bgColor: 'bg-purple-600/10',
    },
    {
      title: 'Guardian Monitor',
      description: 'Real-time ethics validation and drift detection',
      icon: Shield,
      status: 'active',
      link: '#',
      color: 'text-trinity-guardian',
      bgColor: 'bg-green-600/10',
    },
    {
      title: 'API Gateway',
      description: 'RESTful API access to LUKHAS services',
      icon: Cloud,
      status: 'active',
      link: '/api',
      color: 'text-accent-gold',
      bgColor: 'bg-yellow-600/10',
    },
    {
      title: 'Development Tools',
      description: 'SDKs, libraries, and development resources',
      icon: Code,
      status: 'active',
      link: 'https://github.com/LukhasAI',
      external: true,
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      title: 'Documentation',
      description: 'Complete technical documentation and guides',
      icon: Book,
      status: 'active',
      link: '/docs',
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
  ]

  const metrics = [
    { label: 'System Status', value: 'Operational', status: 'success' },
    { label: 'API Latency', value: '<100ms', status: 'success' },
    { label: 'Active Agents', value: '25', status: 'success' },
    { label: 'Drift Score', value: '0.03', status: 'success' },
  ]

  const resources = [
    { name: 'GitHub Repository', url: 'https://github.com/LukhasAI', icon: Github },
    { name: 'API Documentation', url: '/api/docs', icon: Book },
    { name: 'Wiki & Guides', url: '#', icon: Globe },
    { name: 'Community Forum', url: '#', icon: Users },
  ]

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-black text-white pt-20">
        {/* Hero Section */}
        <section className="relative py-20 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center mb-12"
            >
              <h1 className="font-ultralight text-5xl md:text-7xl mb-6">
                <span className="gradient-text">LUKHAS Console</span>
              </h1>
              <p className="font-thin text-xl max-w-3xl mx-auto text-primary-light/80">
                Your gateway to the LUKHAS AI ecosystem. Access tools, monitor systems, and manage your AI services.
              </p>
            </motion.div>

            {/* System Metrics */}
            <div className="grid md:grid-cols-4 gap-4 mb-12">
              {metrics.map((metric, index) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                  className="glass-panel p-6 rounded-lg text-center"
                >
                  <div className="text-xs font-regular uppercase tracking-wider text-neutral-gray mb-2">
                    {metric.label}
                  </div>
                  <div className={`text-2xl font-thin ${
                    metric.status === 'success' ? 'text-green-500' : 'text-yellow-500'
                  }`}>
                    {metric.value}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Products Grid */}
        <section className="py-12 px-6">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-8 text-center">
              PRODUCTS & SERVICES
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product, index) => {
                const Icon = product.icon
                return (
                  <motion.div
                    key={product.title}
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.05 * index }}
                    viewport={{ once: true }}
                  >
                    <Link href={product.link} target={product.external ? '_blank' : undefined}>
                      <div className="glass-panel p-8 rounded-xl hover:border-white/30 transition-all cursor-pointer group h-full">
                        <div className="flex items-start justify-between mb-4">
                          <div className={`p-3 rounded-lg ${product.bgColor}`}>
                            <Icon className={`w-8 h-8 ${product.color}`} strokeWidth={1.5} />
                          </div>
                          {product.external && (
                            <ExternalLink className="w-4 h-4 text-neutral-gray opacity-0 group-hover:opacity-100 transition-opacity" />
                          )}
                        </div>
                        <h3 className="font-regular text-xl mb-3">{product.title}</h3>
                        <p className="text-sm text-primary-light/60 mb-4">{product.description}</p>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            product.status === 'active' ? 'bg-green-500' : 'bg-yellow-500'
                          }`} />
                          <span className="text-xs text-neutral-gray uppercase">
                            {product.status}
                          </span>
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </section>

        {/* Terminal Section */}
        <section className="py-12 px-6">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="glass-panel p-8 rounded-xl"
            >
              <div className="flex items-center mb-6">
                <Terminal className="w-5 h-5 mr-3 text-trinity-consciousness" />
                <h3 className="font-regular text-lg">Quick Start</h3>
              </div>
              <div className="bg-black/50 rounded-lg p-6 font-mono text-sm">
                <div className="text-neutral-gray mb-2"># Install LUKHAS CLI</div>
                <div className="text-green-500 mb-4">npm install -g @lukhas/cli</div>

                <div className="text-neutral-gray mb-2"># Initialize a new project</div>
                <div className="text-green-500 mb-4">lukhas init my-consciousness-app</div>

                <div className="text-neutral-gray mb-2"># Start development server</div>
                <div className="text-green-500">lukhas dev</div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Resources Section */}
        <section className="py-12 px-6 mb-20">
          <div className="max-w-7xl mx-auto">
            <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-8 text-center">
              DEVELOPER RESOURCES
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {resources.map((resource, index) => {
                const Icon = resource.icon
                return (
                  <motion.div
                    key={resource.name}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.05 * index }}
                    viewport={{ once: true }}
                  >
                    <Link href={resource.url} target={resource.url.startsWith('http') ? '_blank' : undefined}>
                      <div className="glass-panel p-6 rounded-lg hover:border-white/30 transition-all cursor-pointer group">
                        <div className="flex items-center space-x-3">
                          <Icon className="w-5 h-5 text-trinity-consciousness" strokeWidth={1.5} />
                          <span className="font-regular text-sm">{resource.name}</span>
                          <ExternalLink className="w-3 h-3 text-neutral-gray opacity-0 group-hover:opacity-100 transition-opacity ml-auto" />
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </section>

        {/* Activity Monitor */}
        <section className="py-12 px-6 bg-gradient-to-t from-black to-gray-900/20">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="glass-panel p-8 rounded-xl"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                  <Activity className="w-5 h-5 mr-3 text-trinity-consciousness" />
                  <h3 className="font-regular text-lg">System Activity</h3>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-xs text-neutral-gray uppercase">Live</span>
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <div className="text-xs font-regular uppercase tracking-wider text-neutral-gray mb-2">
                    Processing Rate
                  </div>
                  <div className="text-2xl font-thin">2.4M ops/sec</div>
                  <div className="mt-2 h-1 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-trinity-identity to-trinity-consciousness" style={{ width: '75%' }} />
                  </div>
                </div>

                <div>
                  <div className="text-xs font-regular uppercase tracking-wider text-neutral-gray mb-2">
                    Memory Usage
                  </div>
                  <div className="text-2xl font-thin">64.3%</div>
                  <div className="mt-2 h-1 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-trinity-consciousness to-trinity-guardian" style={{ width: '64.3%' }} />
                  </div>
                </div>

                <div>
                  <div className="text-xs font-regular uppercase tracking-wider text-neutral-gray mb-2">
                    Guardian Score
                  </div>
                  <div className="text-2xl font-thin text-green-500">0.97</div>
                  <div className="mt-2 h-1 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-green-500" style={{ width: '97%' }} />
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="font-thin text-3xl mb-8">Need help getting started?</h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/docs">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-primary-dark font-regular tracking-wider uppercase rounded-lg"
                >
                  Read Documentation
                </motion.button>
              </Link>
              <Link href="mailto:support@lukhas.ai">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-8 py-4 border border-white/30 font-regular tracking-wider uppercase hover:bg-white hover:text-black transition-all rounded-lg"
                >
                  Contact Support
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
