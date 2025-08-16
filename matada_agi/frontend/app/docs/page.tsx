'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { ArrowLeft, Book, Code, Cpu, Database, GitBranch, Package, Terminal, Zap } from 'lucide-react'

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState('getting-started')

  const sections = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: <Zap className="w-5 h-5" />,
      content: `
        # Getting Started with MATADA

        MATADA is a revolutionary cognitive architecture that transforms AI through permanent, evolving nodes.

        ## Installation

        \`\`\`bash
        npm install @lukhas/matada
        # or
        yarn add @lukhas/matada
        \`\`\`

        ## Quick Start

        \`\`\`javascript
        import { MATADA } from '@lukhas/matada'

        const matada = new MATADA({
          trinity: {
            identity: true,
            consciousness: true,
            guardian: true
          }
        })

        await matada.initialize()
        \`\`\`
      `
    },
    {
      id: 'architecture',
      title: 'Architecture',
      icon: <Cpu className="w-5 h-5" />,
      content: `
        # System Architecture

        ## Core Components

        ### Node System
        Every computation creates a permanent node in the cognitive graph. Nodes contain:
        - **State**: Current values and computations
        - **Context**: Environmental and temporal information
        - **Connections**: Links to related nodes
        - **Evolution**: Mutation and adaptation rules

        ### Trinity Framework
        - **⚛️ Identity**: Self-awareness and authentication
        - **🧠 Consciousness**: Decision-making and reasoning
        - **🛡️ Guardian**: Ethics and safety protocols

        ### Memory Folds
        The fold-based memory system preserves causal chains with 99.7% cascade prevention.
      `
    },
    {
      id: 'api-reference',
      title: 'API Reference',
      icon: <Code className="w-5 h-5" />,
      content: `
        # API Reference

        ## Core Methods

        ### initialize()
        Initializes the MATADA system with configured parameters.

        \`\`\`javascript
        await matada.initialize({
          memoryLimit: 1000,
          driftThreshold: 0.15,
          ethicsLevel: 'strict'
        })
        \`\`\`

        ### createNode()
        Creates a new cognitive node in the graph.

        \`\`\`javascript
        const node = await matada.createNode({
          type: 'decision',
          confidence: 0.95,
          data: { /* node data */ }
        })
        \`\`\`

        ### evolve()
        Triggers evolution cycle for specified nodes.

        \`\`\`javascript
        await matada.evolve(nodeIds, {
          mutationRate: 0.1,
          selectionPressure: 0.7
        })
        \`\`\`
      `
    },
    {
      id: 'trinity-framework',
      title: 'Trinity Framework',
      icon: <GitBranch className="w-5 h-5" />,
      content: `
        # Trinity Framework

        ## Identity Module (⚛️)
        Manages authentication, authorization, and self-awareness.

        ### Features
        - OAuth2/OIDC integration
        - WebAuthn support
        - Namespace isolation
        - Tiered access control (T1-T5)

        ## Consciousness Module (🧠)
        Handles reasoning, decision-making, and awareness.

        ### Features
        - Multi-model orchestration
        - Context preservation
        - Dream state simulation
        - Quantum-inspired processing

        ## Guardian Module (🛡️)
        Ensures ethical behavior and system safety.

        ### Features
        - Drift detection (0.15 threshold)
        - Constitutional AI principles
        - Real-time ethics validation
        - Automatic repair mechanisms
      `
    },
    {
      id: 'memory-system',
      title: 'Memory System',
      icon: <Database className="w-5 h-5" />,
      content: `
        # Memory System

        ## Fold-Based Architecture

        The memory system uses a revolutionary fold-based approach:

        ### Key Concepts
        - **Memory Folds**: Compressed cognitive states
        - **Causal Chains**: Preserved relationships
        - **Cascade Prevention**: 99.7% success rate
        - **Temporal Decay**: Configurable retention

        ## Usage

        \`\`\`javascript
        // Create a memory fold
        const fold = await matada.memory.createFold({
          event: 'decision_made',
          weight: 0.8,
          connections: [nodeId1, nodeId2]
        })

        // Retrieve memory chain
        const chain = await matada.memory.getCausalChain(foldId)

        // Consolidate memories
        await matada.memory.consolidate({
          threshold: 0.6,
          maxFolds: 1000
        })
        \`\`\`
      `
    },
    {
      id: 'deployment',
      title: 'Deployment',
      icon: <Package className="w-5 h-5" />,
      content: `
        # Deployment Guide

        ## Docker Deployment

        \`\`\`dockerfile
        FROM node:18-alpine
        WORKDIR /app
        COPY . .
        RUN npm install
        EXPOSE 8080
        CMD ["npm", "start"]
        \`\`\`

        ## Kubernetes

        \`\`\`yaml
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: matada-deployment
        spec:
          replicas: 3
          selector:
            matchLabels:
              app: matada
          template:
            metadata:
              labels:
                app: matada
            spec:
              containers:
              - name: matada
                image: lukhas/matada:latest
                ports:
                - containerPort: 8080
        \`\`\`

        ## Environment Variables

        - \`MATADA_API_KEY\`: Your API key
        - \`DRIFT_THRESHOLD\`: Maximum drift (default: 0.15)
        - \`MEMORY_LIMIT\`: Max memory folds (default: 1000)
        - \`ETHICS_LEVEL\`: strict/moderate/lenient
      `
    }
  ]

  const renderMarkdown = (content: string) => {
    // Simple markdown rendering (in production, use a proper markdown parser)
    return content
      .split('\n')
      .map((line, i) => {
        if (line.startsWith('# ')) {
          return <h1 key={i} className="text-3xl font-thin mb-6 mt-8">{line.slice(2)}</h1>
        }
        if (line.startsWith('## ')) {
          return <h2 key={i} className="text-2xl font-thin mb-4 mt-6 text-trinity-consciousness">{line.slice(3)}</h2>
        }
        if (line.startsWith('### ')) {
          return <h3 key={i} className="text-xl font-regular mb-3 mt-4">{line.slice(4)}</h3>
        }
        if (line.startsWith('```')) {
          const lang = line.slice(3)
          return null // Start of code block
        }
        if (line.startsWith('- ')) {
          return <li key={i} className="ml-6 mb-2">{line.slice(2)}</li>
        }
        if (line.includes('`') && !line.startsWith('`')) {
          const parts = line.split('`')
          return (
            <p key={i} className="mb-4">
              {parts.map((part, j) => 
                j % 2 === 0 ? part : <code key={j} className="px-2 py-1 bg-white/10 rounded font-mono text-sm">{part}</code>
              )}
            </p>
          )
        }
        if (line.trim()) {
          return <p key={i} className="mb-4 text-primary-light/80">{line}</p>
        }
        return null
      })
  }

  return (
    <div className="min-h-screen bg-primary-dark text-primary-light">
      {/* Header */}
      <header className="glass-panel border-b border-white/10 py-6">
        <div className="container mx-auto max-w-7xl px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-6">
              <Link href="/" className="flex items-center space-x-2 hover:opacity-80 transition-opacity">
                <ArrowLeft className="w-5 h-5" />
                <span>Back</span>
              </Link>
              <h1 className="text-3xl font-ultralight tracking-[0.2em] gradient-text">
                DOCUMENTATION
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 hover:bg-white/10 rounded">
                <Book className="w-5 h-5" />
              </button>
              <button className="p-2 hover:bg-white/10 rounded">
                <Terminal className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto max-w-7xl px-6 py-12">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Sidebar */}
          <aside className="md:col-span-1">
            <nav className="sticky top-6 space-y-2">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                    activeSection === section.id
                      ? 'bg-trinity-consciousness/20 text-trinity-consciousness border-l-4 border-trinity-consciousness'
                      : 'hover:bg-white/5 text-primary-light/70 hover:text-primary-light'
                  }`}
                >
                  {section.icon}
                  <span className="font-regular text-sm">{section.title}</span>
                </button>
              ))}
            </nav>
          </aside>

          {/* Content */}
          <main className="md:col-span-3">
            <motion.div
              key={activeSection}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              className="glass-panel rounded-xl p-8"
            >
              <div className="prose prose-invert max-w-none">
                {renderMarkdown(sections.find(s => s.id === activeSection)?.content || '')}
              </div>

              {/* Code blocks (simplified) */}
              {activeSection === 'getting-started' && (
                <div className="mt-6 space-y-4">
                  <div className="bg-black/50 rounded-lg p-4 border border-white/10">
                    <pre className="font-mono text-sm text-trinity-consciousness">
{`npm install @lukhas/matada
# or
yarn add @lukhas/matada`}
                    </pre>
                  </div>
                  <div className="bg-black/50 rounded-lg p-4 border border-white/10">
                    <pre className="font-mono text-sm text-trinity-consciousness">
{`import { MATADA } from '@lukhas/matada'

const matada = new MATADA({
  trinity: {
    identity: true,
    consciousness: true,
    guardian: true
  }
})

await matada.initialize()`}
                    </pre>
                  </div>
                </div>
              )}
            </motion.div>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-8">
              {activeSection !== sections[0].id && (
                <button
                  onClick={() => {
                    const currentIndex = sections.findIndex(s => s.id === activeSection)
                    if (currentIndex > 0) {
                      setActiveSection(sections[currentIndex - 1].id)
                    }
                  }}
                  className="flex items-center space-x-2 px-4 py-2 glass-panel rounded-lg hover:bg-white/10 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Previous</span>
                </button>
              )}
              {activeSection !== sections[sections.length - 1].id && (
                <button
                  onClick={() => {
                    const currentIndex = sections.findIndex(s => s.id === activeSection)
                    if (currentIndex < sections.length - 1) {
                      setActiveSection(sections[currentIndex + 1].id)
                    }
                  }}
                  className="flex items-center space-x-2 px-4 py-2 glass-panel rounded-lg hover:bg-white/10 transition-colors ml-auto"
                >
                  <span>Next</span>
                  <ArrowLeft className="w-4 h-4 rotate-180" />
                </button>
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}