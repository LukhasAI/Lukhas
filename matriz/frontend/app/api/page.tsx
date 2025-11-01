'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import Navigation from '@/components/Navigation'
import Footer from '@/components/Footer'
import {
  Code, Server, Zap, Shield, Book, ExternalLink,
  Brain, Database, Lock, Globe, Terminal, Activity,
  ArrowRight, Copy, CheckCircle, Settings
} from 'lucide-react'

export default function APIPage() {
  const apiEndpoints = [
    {
      category: "Consciousness",
      description: "Core consciousness processing and awareness APIs",
      endpoints: [
        {
          method: "POST",
          path: "/v1/consciousness/process",
          description: "Process queries with full awareness and context",
          features: ["Trinity Framework integration", "Memory persistence", "Ethical validation"]
        },
        {
          method: "GET",
          path: "/v1/consciousness/state",
          description: "Retrieve current consciousness state and metrics",
          features: ["Real-time status", "Health indicators", "Performance metrics"]
        },
        {
          method: "POST",
          path: "/v1/consciousness/dream",
          description: "Initiate dream processing for complex analysis",
          features: ["Background processing", "Insight generation", "Memory consolidation"]
        }
      ],
      icon: Brain,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10"
    },
    {
      category: "Memory",
      description: "Fold-based memory management and retrieval",
      endpoints: [
        {
          method: "POST",
          path: "/v1/memory/folds",
          description: "Create memory folds with causal relationships",
          features: ["Causal chain preservation", "Cascade prevention", "Temporal indexing"]
        },
        {
          method: "GET",
          path: "/v1/memory/recall",
          description: "Retrieve memories with contextual relevance",
          features: ["Semantic search", "Context awareness", "Relevance scoring"]
        },
        {
          method: "DELETE",
          path: "/v1/memory/prune",
          description: "Intelligent memory cleanup and optimization",
          features: ["Smart pruning", "Compression", "Retention policies"]
        }
      ],
      icon: Database,
      color: "text-green-400",
      bgColor: "bg-green-500/10"
    },
    {
      category: "Guardian",
      description: "Ethics validation and safety monitoring",
      endpoints: [
        {
          method: "POST",
          path: "/v1/guardian/validate",
          description: "Validate operations against ethical frameworks",
          features: ["Constitutional AI", "Multi-framework validation", "Drift detection"]
        },
        {
          method: "GET",
          path: "/v1/guardian/drift",
          description: "Monitor system drift and ethical alignment",
          features: ["Real-time monitoring", "Threshold alerting", "Automatic correction"]
        },
        {
          method: "POST",
          path: "/v1/guardian/audit",
          description: "Generate comprehensive audit trails",
          features: ["Complete provenance", "Decision tracking", "Compliance reporting"]
        }
      ],
      icon: Shield,
      color: "text-red-400",
      bgColor: "bg-red-500/10"
    }
  ]

  const sdks = [
    {
      language: "Python",
      status: "Stable",
      version: "v1.2.0",
      install: "pip install lukhas-ai",
      docs: "/docs/python",
      example: `from lukhas import LukhasAI

ai = LukhasAI(api_key="your-key")
response = await ai.consciousness.process(
    query="Explain quantum consciousness",
    context={"depth": "academic"}
)`
    },
    {
      language: "JavaScript",
      status: "Stable",
      version: "v1.1.0",
      install: "npm install @lukhas/ai",
      docs: "/docs/javascript",
      example: `import { LukhasAI } from '@lukhas/ai';

const ai = new LukhasAI({ apiKey: 'your-key' });
const response = await ai.consciousness.process({
  query: 'Explain quantum consciousness',
  context: { depth: 'academic' }
});`
    },
    {
      language: "Rust",
      status: "Beta",
      version: "v0.8.0",
      install: "cargo add lukhas-rs",
      docs: "/docs/rust",
      example: `use lukhas::{LukhasAI, ProcessRequest};

let ai = LukhasAI::new("your-key");
let response = ai.consciousness().process(
    ProcessRequest::new("Explain quantum consciousness")
        .with_context("depth", "academic")
).await?;`
    },
    {
      language: "Go",
      status: "Beta",
      version: "v0.6.0",
      install: "go get github.com/lukhas/lukhas-go",
      docs: "/docs/go",
      example: `import "github.com/lukhas/lukhas-go"

client := lukhas.New("your-key")
response, err := client.Consciousness.Process(ctx, &lukhas.ProcessRequest{
    Query: "Explain quantum consciousness",
    Context: map[string]string{"depth": "academic"},
})`
    }
  ]

  const features = [
    {
      title: "Trinity Framework Integration",
      description: "Full access to Identity, Consciousness, and Guardian systems",
      icon: Settings,
      metrics: ["Sub-100ms authentication", "99.7% memory consistency", "Real-time ethics validation"]
    },
    {
      title: "Real-time Processing",
      description: "Live consciousness processing with WebSocket streaming",
      icon: Activity,
      metrics: ["142ms average response", "2.4M+ ops/second", "99.99% uptime"]
    },
    {
      title: "Quantum-Safe Security",
      description: "Post-quantum cryptography and secure communication",
      icon: Lock,
      metrics: ["CRYSTALS-Kyber encryption", "Forward secrecy", "Zero-knowledge proofs"]
    },
    {
      title: "Global Distribution",
      description: "Edge processing with consciousness state synchronization",
      icon: Globe,
      metrics: ["25 edge locations", "Consciousness sync", "Regional compliance"]
    }
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
                <Server className="w-16 h-16 text-trinity-consciousness" strokeWidth={1} />
              </div>
              <h1 className="font-ultralight text-6xl md:text-8xl mb-8">
                <span className="gradient-text">LUKHAS API</span>
              </h1>
              <p className="font-light text-2xl max-w-4xl mx-auto text-primary-light/80 leading-relaxed">
                Consciousness-aware APIs for building AI applications with Trinity Framework integration,
                quantum-safe security, and ethical governance.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center mt-12">
                <Link href="/docs">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-blue-400 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
                  >
                    <Book className="w-5 h-5" strokeWidth={1.5} />
                    <span>View Documentation</span>
                  </motion.button>
                </Link>
                <Link href="/console">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-primary-light/20 text-primary-light rounded-xl hover:bg-primary-light/5 transition-all duration-300 flex items-center space-x-2"
                  >
                    <Terminal className="w-5 h-5" strokeWidth={1.5} />
                    <span>Developer Console</span>
                  </motion.button>
                </Link>
              </div>
            </motion.div>

            {/* API Features */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map((feature, index) => {
                const IconComponent = feature.icon;
                return (
                  <motion.div
                    key={feature.title}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 * index }}
                    className="glass-panel p-6 rounded-xl"
                  >
                    <div className="flex items-center space-x-3 mb-4">
                      <IconComponent className="w-6 h-6 text-trinity-consciousness" strokeWidth={1.5} />
                      <h3 className="font-medium text-lg">{feature.title}</h3>
                    </div>
                    <p className="text-sm text-primary-light/70 mb-4">
                      {feature.description}
                    </p>
                    <ul className="space-y-1">
                      {feature.metrics.map((metric, idx) => (
                        <li key={idx} className="text-xs text-trinity-consciousness">
                          • {metric}
                        </li>
                      ))}
                    </ul>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* API Endpoints */}
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
                API Endpoints
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Comprehensive consciousness processing APIs with Trinity Framework integration
              </p>
            </motion.div>

            <div className="space-y-12">
              {apiEndpoints.map((category, index) => {
                const IconComponent = category.icon;
                return (
                  <motion.div
                    key={category.category}
                    initial={{ opacity: 0, y: 50 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.2 }}
                    className="glass-panel p-8 rounded-2xl"
                  >
                    <div className="flex items-center space-x-4 mb-6">
                      <div className={`p-3 rounded-lg ${category.bgColor}`}>
                        <IconComponent className={`w-8 h-8 ${category.color}`} strokeWidth={1.5} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-2xl text-trinity-consciousness">
                          {category.category} API
                        </h3>
                        <p className="text-primary-light/70">
                          {category.description}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {category.endpoints.map((endpoint, idx) => (
                        <div key={idx} className="border border-white/10 rounded-lg p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <div className="flex items-center space-x-3 mb-2">
                                <span className={`px-2 py-1 text-xs rounded font-mono ${
                                  endpoint.method === 'GET' ? 'bg-green-500/20 text-green-400' :
                                  endpoint.method === 'POST' ? 'bg-blue-500/20 text-blue-400' :
                                  'bg-red-500/20 text-red-400'
                                }`}>
                                  {endpoint.method}
                                </span>
                                <code className="font-mono text-sm text-primary-light">
                                  {endpoint.path}
                                </code>
                              </div>
                              <p className="text-primary-light/70 mb-3">
                                {endpoint.description}
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {endpoint.features.map((feature, featureIdx) => (
                                  <span key={featureIdx} className="px-2 py-1 bg-white/5 text-xs rounded">
                                    {feature}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <ArrowRight className="w-5 h-5 text-primary-light/40 mt-2" strokeWidth={1.5} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </section>

        {/* SDKs */}
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
                Official SDKs
              </h2>
              <p className="text-lg md:text-xl text-primary-light/70 max-w-3xl mx-auto">
                Native language integrations for seamless consciousness API access
              </p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-8">
              {sdks.map((sdk, index) => (
                <motion.div
                  key={sdk.language}
                  initial={{ opacity: 0, y: 50 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                  className="glass-panel rounded-2xl overflow-hidden"
                >
                  <div className="p-6 border-b border-white/10">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-xl">{sdk.language}</h3>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs rounded ${
                          sdk.status === 'Stable' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {sdk.status}
                        </span>
                        <span className="text-xs text-primary-light/60">{sdk.version}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <Terminal className="w-4 h-4 text-trinity-consciousness" strokeWidth={1.5} />
                      <code className="text-primary-light/80">{sdk.install}</code>
                      <Copy className="w-4 h-4 text-primary-light/40 hover:text-primary-light cursor-pointer" strokeWidth={1.5} />
                    </div>
                  </div>
                  <div className="p-6">
                    <h4 className="font-medium mb-3">Quick Start Example</h4>
                    <div className="bg-black/50 rounded-lg p-4 font-mono text-sm overflow-x-auto">
                      <pre className="text-primary-light/80 whitespace-pre-wrap">
                        {sdk.example}
                      </pre>
                    </div>
                    <div className="mt-4">
                      <Link href={sdk.docs}>
                        <button className="text-trinity-consciousness hover:text-trinity-consciousness/80 text-sm flex items-center space-x-1">
                          <span>View Documentation</span>
                          <ExternalLink className="w-3 h-3" strokeWidth={1.5} />
                        </button>
                      </Link>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Rate Limits & Authentication */}
        <section className="py-16 px-6">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8 }}
              className="grid md:grid-cols-2 gap-8"
            >
              {/* Authentication */}
              <div className="glass-panel p-8 rounded-2xl">
                <div className="flex items-center space-x-3 mb-6">
                  <Lock className="w-6 h-6 text-trinity-guardian" strokeWidth={1.5} />
                  <h3 className="font-semibold text-xl">Authentication</h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">API Key Authentication</h4>
                    <code className="text-sm bg-black/50 px-3 py-2 rounded block">
                      Authorization: Bearer lukhas_sk_...
                    </code>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Trinity Framework Integration</h4>
                    <ul className="text-sm text-primary-light/70 space-y-1">
                      <li>• Identity-aware request processing</li>
                      <li>• Consciousness state preservation</li>
                      <li>• Guardian ethics validation</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* Rate Limits */}
              <div className="glass-panel p-8 rounded-2xl">
                <div className="flex items-center space-x-3 mb-6">
                  <Zap className="w-6 h-6 text-trinity-consciousness" strokeWidth={1.5} />
                  <h3 className="font-semibold text-xl">Rate Limits</h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium mb-2">Request Limits</h4>
                    <ul className="text-sm text-primary-light/70 space-y-1">
                      <li>• Free: 1,000 requests/month</li>
                      <li>• Pro: 10,000 requests/month</li>
                      <li>• Enterprise: Unlimited</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Performance</h4>
                    <ul className="text-sm text-primary-light/70 space-y-1">
                      <li>• 142ms average response time</li>
                      <li>• 99.99% uptime SLA</li>
                      <li>• Global edge processing</li>
                    </ul>
                  </div>
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
                Ready to Build with Consciousness?
              </h2>
              <p className="text-lg text-primary-light/70 mb-8 leading-relaxed">
                Start building AI applications with consciousness-aware processing,
                ethical governance, and quantum-safe security.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/console">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 bg-gradient-to-r from-blue-400 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all duration-300"
                  >
                    Get API Key
                  </motion.button>
                </Link>
                <Link href="/docs">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="px-8 py-4 border border-primary-light/20 text-primary-light rounded-xl hover:bg-primary-light/5 transition-all duration-300"
                  >
                    Read API Docs
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
