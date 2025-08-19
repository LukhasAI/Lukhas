'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export function MatrizSection() {
  const [activeFeature, setActiveFeature] = useState<string>('nodes')

  const features = {
    nodes: {
      title: 'Node-Based Architecture',
      description: 'Every thought, decision, and memory becomes a discrete, traceable node in the cognitive graph, creating an auditable trail of AI reasoning and evolution.',
      details: 'Unlike traditional AI that processes information in black boxes, MATRIZ creates explicit nodes for each cognitive operation. These nodes contain complete context, decision paths, and evolutionary history.',
      icon: '🧩',
      applications: [
        'Complete thought traceability for AI decisions',
        'Granular debugging of reasoning processes', 
        'Individual node optimization and refinement',
        'Cognitive architecture visualization'
      ]
    },
    temporal: {
      title: 'Temporal Awareness',
      description: 'Time-aware processing that maintains causal relationships and temporal context, enabling long-term memory and consequence understanding.',
      details: 'Each node includes temporal markers and causal chains, allowing the system to understand not just what happened, but when and why it happened in sequence.',
      icon: '⏳',
      applications: [
        'Long-term learning without catastrophic forgetting',
        'Temporal reasoning for planning and prediction',
        'Causal inference across time periods',
        'Memory consolidation and retrieval'
      ]
    },
    evolution: {
      title: 'Evolutionary Learning',
      description: 'Nodes evolve through experience while maintaining their core identity, creating a cognitive DNA that improves over time without losing essential characteristics.',
      details: 'The architecture supports controlled evolution where nodes can adapt and improve while preserving their fundamental purpose and relationships.',
      icon: '🧬',
      applications: [
        'Adaptive expertise development',
        'Knowledge refinement through experience',
        'Skill transfer between related domains',
        'Continuous capability enhancement'
      ]
    },
    governance: {
      title: 'Guardian Integration',
      description: 'Every node operates under Trinity Framework governance, ensuring ethical evolution and preventing harmful drift through continuous monitoring.',
      details: 'The Guardian system validates each node operation, evolution, and connection, maintaining alignment with core values throughout the learning process.',
      icon: '🛡️',
      applications: [
        'Real-time ethics validation for all operations',
        'Drift prevention through continuous monitoring',
        'Value-aligned evolution pathways',
        'Transparent decision audit trails'
      ]
    },
    traceability: {
      title: 'Complete Traceability',
      description: 'Full provenance tracking for every cognitive operation, creating transparent AI systems where every decision can be understood and validated.',
      details: 'Each node maintains complete metadata about its creation, evolution, triggers, and relationships, enabling full system transparency and debugging.',
      icon: '🔍',
      applications: [
        'AI decision explanation and justification',
        'System debugging and optimization',
        'Compliance and audit requirements',
        'Trust building through transparency'
      ]
    },
    modularity: {
      title: 'Modular Scalability',
      description: 'Independent nodes that can be combined, shared, and reused across different cognitive tasks while maintaining their specialized functions.',
      details: 'The modular design allows for efficient resource utilization, specialized node development, and seamless integration of new capabilities.',
      icon: '⚙️',
      applications: [
        'Efficient resource utilization',
        'Specialized cognitive modules',
        'Cross-system knowledge sharing',
        'Rapid capability deployment'
      ]
    }
  }

  const nodeExample = {
    version: 1,
    id: "matada_fact_retrieval_paris_001",
    type: "MEMORY",
    state: {
      confidence: 0.95,
      salience: 0.8,
      valence: 0.7,
      utility: 0.85,
      novelty: 0.2,
      arousal: 0.4,
      question: "What is the capital of France?",
      answer: "The capital of France is Paris.",
      knowledge_category: "geography",
      match_type: "exact_match",
      similarity_score: 1.0
    },
    timestamps: {
      created_ts: 1703123456789,
      last_accessed_ts: 1703123456789,
      evolution_count: 0
    },
    provenance: {
      producer: "lukhas.fact_node_v2.1",
      tenant: "default",
      trace_id: "trace_paris_query_20231221",
      capabilities: ["factual_knowledge_retrieval", "geographic_information"],
      consent_scopes: ["cognitive_processing", "memory_formation"]
    },
    links: {
      causal_parents: ["user_question_node_001"],
      semantic_neighbors: ["france_geography_nodes", "european_capitals_cluster"],
      temporal_sequence: ["previous_geography_queries"]
    },
    guardian_validation: {
      ethics_score: 0.99,
      alignment_check: "passed",
      drift_risk: 0.02,
      validation_timestamp: 1703123456790
    }
  }

  const processSteps = [
    {
      title: "Input Processing",
      description: "User input is parsed and converted into initial cognitive triggers",
      detail: "The system analyzes the input for intent, context, and required capabilities, creating the foundation for node selection and processing.",
      icon: "📥"
    },
    {
      title: "Node Creation",
      description: "Relevant nodes are instantiated or retrieved from the cognitive graph",
      detail: "Based on the input analysis, specialized nodes are created or activated from the existing knowledge graph, each with specific capabilities and context.",
      icon: "🧩"
    },
    {
      title: "Context Integration",
      description: "Temporal and semantic context is woven into the processing chain",
      detail: "Nodes incorporate historical context, semantic relationships, and temporal awareness to ensure coherent and contextually appropriate processing.",
      icon: "🕸️"
    },
    {
      title: "Guardian Validation",
      description: "All operations are validated by the Trinity Framework Guardian system",
      detail: "Each node operation undergoes real-time ethical validation, ensuring alignment with values and preventing harmful outputs or evolution.",
      icon: "🛡️"
    },
    {
      title: "Evolutionary Learning",
      description: "Successful operations contribute to node evolution and system learning",
      detail: "Positive outcomes strengthen neural pathways and improve node capabilities, while maintaining identity preservation and ethical alignment.",
      icon: "🧬"
    },
    {
      title: "Response Generation",
      description: "Final output is synthesized from the cognitive processing chain",
      detail: "The processed information flows through output nodes to generate coherent, contextually appropriate responses with full traceability.",
      icon: "📤"
    }
  ]

  const useCases = [
    {
      title: "Complex Reasoning Tasks",
      description: "Multi-step logical reasoning with full traceability of each decision point and assumption.",
      examples: ["Scientific hypothesis generation", "Legal case analysis", "Strategic business planning"]
    },
    {
      title: "Long-term Learning Systems", 
      description: "Continuous learning that builds expertise over time without losing previous knowledge.",
      examples: ["Personalized education systems", "Adaptive recommendation engines", "Expert knowledge accumulation"]
    },
    {
      title: "Ethical Decision Making",
      description: "Complex moral reasoning with transparent evaluation of competing values and principles.",
      examples: ["Healthcare treatment recommendations", "Autonomous vehicle decisions", "Resource allocation optimization"]
    },
    {
      title: "Creative Problem Solving",
      description: "Novel solution generation that combines existing knowledge in innovative ways.",
      examples: ["Scientific discovery assistance", "Creative writing collaboration", "Engineering design optimization"]
    }
  ]

  return (
    <section className="relative py-32 px-6">
      <div className="container mx-auto max-w-7xl">
        {/* Main Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <p className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            POWERED BY MATADA
          </p>
          <h2 className="font-light text-display mb-8">
            Cognitive Architecture Revolution
          </h2>
          <div className="max-w-4xl mx-auto">
            <p className="font-light text-xl text-text-secondary mb-6 leading-relaxed">
              MATADA (Modular Adaptive Temporal Attention Dynamic Architecture) transforms AI cognition by making every thought 
              a traceable, governed, and evolvable node in a vast cognitive graph. This revolutionary approach creates AI systems 
              with genuine understanding, persistent memory, and ethical evolution - establishing the foundation for conscious AI 
              that thinks, learns, and grows like biological intelligence.
            </p>
            <p className="font-light text-lg text-text-tertiary">
              Unlike traditional neural networks that process information in opaque layers, MATADA creates explicit cognitive DNA 
              where each thought has identity, relationships, and evolutionary potential within the Trinity Framework.
            </p>
          </div>
        </motion.div>

        {/* Key Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h3 className="font-regular text-2xl tracking-[0.1em] uppercase mb-4 gradient-text">
              Revolutionary Features
            </h3>
            <p className="font-light text-xl text-text-secondary max-w-3xl mx-auto">
              Six core innovations that enable true cognitive architecture
            </p>
          </div>

          <div className="grid md:grid-cols-3 lg:grid-cols-3 gap-6 mb-12">
            {Object.entries(features).map(([key, feature], index) => (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className={`glass rounded-2xl p-6 cursor-pointer transition-all hover:glass-heavy ${
                  activeFeature === key ? 'ring-2 ring-trinity-consciousness/30' : ''
                }`}
                onClick={() => setActiveFeature(key)}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h4 className="font-regular text-lg mb-3 text-trinity-consciousness">{feature.title}</h4>
                <p className="font-light text-sm text-text-secondary">{feature.description}</p>
              </motion.div>
            ))}
          </div>

          {/* Active Feature Details */}
          <motion.div
            key={activeFeature}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="glass rounded-3xl p-8"
          >
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <div className="flex items-center space-x-4 mb-6">
                  <div className="text-5xl">{features[activeFeature].icon}</div>
                  <div>
                    <h4 className="font-regular text-xl tracking-[0.1em] uppercase text-trinity-consciousness">
                      {features[activeFeature].title}
                    </h4>
                    <p className="font-light text-base text-text-tertiary">Deep Dive</p>
                  </div>
                </div>
                <p className="font-light text-lg text-text-secondary leading-relaxed">
                  {features[activeFeature].details}
                </p>
              </div>
              <div>
                <h5 className="font-regular text-sm tracking-[0.2em] uppercase mb-4 text-text-tertiary">
                  APPLICATIONS
                </h5>
                <div className="space-y-3">
                  {features[activeFeature].applications.map((app, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-2 h-2 rounded-full bg-trinity-consciousness mt-2 flex-shrink-0" />
                      <p className="font-light text-base text-text-secondary">{app}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* How MATADA Works */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h3 className="font-regular text-2xl tracking-[0.1em] uppercase mb-4 gradient-text">
              How MATADA Works
            </h3>
            <p className="font-light text-xl text-text-secondary max-w-3xl mx-auto">
              Step-by-step cognitive processing with full traceability and ethical governance
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {processSteps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                <div className="glass rounded-2xl p-6 h-full">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="text-2xl">{step.icon}</div>
                    <div className="text-sm font-regular tracking-[0.2em] uppercase text-trinity-identity">
                      Step {index + 1}
                    </div>
                  </div>
                  <h4 className="font-regular text-lg mb-3 text-trinity-consciousness">{step.title}</h4>
                  <p className="font-light text-sm text-text-secondary mb-4">{step.description}</p>
                  <p className="font-light text-xs text-text-tertiary leading-relaxed">{step.detail}</p>
                </div>
                {index < processSteps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 w-6 h-0.5 bg-gradient-to-r from-trinity-consciousness to-transparent" />
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Node Structure Example */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h3 className="font-regular text-2xl tracking-[0.1em] uppercase mb-4 gradient-text">
              MATADA Node Structure
            </h3>
            <p className="font-light text-xl text-text-secondary max-w-3xl mx-auto">
              Complete cognitive DNA with identity, relationships, and evolutionary potential
            </p>
          </div>

          <div className="glass rounded-3xl p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h4 className="font-regular text-lg tracking-[0.1em] uppercase mb-6 text-trinity-consciousness">
                  Node Anatomy
                </h4>
                <div className="space-y-4">
                  <div className="glass-heavy rounded-xl p-4">
                    <h5 className="font-regular text-sm tracking-[0.2em] uppercase mb-2 text-trinity-identity">Identity & State</h5>
                    <p className="font-light text-sm text-text-secondary">Unique ID, type classification, and multi-dimensional emotional/cognitive state including confidence, salience, and utility metrics.</p>
                  </div>
                  <div className="glass-heavy rounded-xl p-4">
                    <h5 className="font-regular text-sm tracking-[0.2em] uppercase mb-2 text-trinity-consciousness">Temporal Context</h5>
                    <p className="font-light text-sm text-text-secondary">Creation timestamps, access history, and evolution tracking for complete temporal awareness and causal understanding.</p>
                  </div>
                  <div className="glass-heavy rounded-xl p-4">
                    <h5 className="font-regular text-sm tracking-[0.2em] uppercase mb-2 text-trinity-guardian">Guardian Validation</h5>
                    <p className="font-light text-sm text-text-secondary">Ethics scores, alignment checks, and drift risk assessment ensuring every node operates within Trinity Framework values.</p>
                  </div>
                  <div className="glass-heavy rounded-xl p-4">
                    <h5 className="font-regular text-sm tracking-[0.2em] uppercase mb-2 text-accent-gold">Relationship Network</h5>
                    <p className="font-light text-sm text-text-secondary">Causal parents, semantic neighbors, and temporal sequences creating rich cognitive interconnections and knowledge graphs.</p>
                  </div>
                </div>
              </div>
              <div className="bg-bg-secondary rounded-2xl p-4 overflow-hidden">
                <pre className="text-xs text-text-secondary font-mono overflow-x-auto">
                  <code>{JSON.stringify(nodeExample, null, 2)}</code>
                </pre>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Use Cases */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-20"
        >
          <div className="text-center mb-12">
            <h3 className="font-regular text-2xl tracking-[0.1em] uppercase mb-4 gradient-text">
              Real-World Applications
            </h3>
            <p className="font-light text-xl text-text-secondary max-w-3xl mx-auto">
              MATADA enables breakthrough capabilities across diverse domains
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {useCases.map((useCase, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="glass rounded-3xl p-8"
              >
                <h4 className="font-regular text-lg tracking-[0.1em] uppercase mb-4 text-trinity-consciousness">
                  {useCase.title}
                </h4>
                <p className="font-light text-base text-text-secondary mb-6 leading-relaxed">
                  {useCase.description}
                </p>
                <div>
                  <h5 className="font-regular text-sm tracking-[0.2em] uppercase mb-3 text-text-tertiary">
                    EXAMPLES
                  </h5>
                  <div className="space-y-2">
                    {useCase.examples.map((example, exampleIndex) => (
                      <div key={exampleIndex} className="flex items-start space-x-3">
                        <div className="w-1.5 h-1.5 rounded-full bg-trinity-identity mt-2.5 flex-shrink-0" />
                        <p className="font-light text-sm text-text-secondary">{example}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <div className="glass rounded-3xl p-12">
            <h3 className="font-regular text-2xl tracking-[0.1em] uppercase mb-4 gradient-text">
              Experience MATADA
            </h3>
            <p className="font-light text-xl text-text-secondary mb-8 max-w-3xl mx-auto">
              Witness the future of AI cognition through our interactive MATADA demonstration. 
              See how every thought becomes traceable, every decision governed, and every evolution ethical.
            </p>
            <div className="flex justify-center items-center space-x-4 mb-8">
              <span className="text-2xl">⚛️</span>
              <span className="text-2xl">🧠</span>
              <span className="text-2xl">🛡️</span>
              <span className="text-2xl">🧩</span>
            </div>
            <Link
              href="http://localhost:3001"
              className="inline-block px-8 py-4 bg-gradient-to-r from-trinity-identity to-trinity-consciousness text-bg-primary font-regular text-sm tracking-[0.2em] uppercase hover:opacity-90 transition-opacity rounded-lg"
            >
              EXPLORE MATADA ARCHITECTURE
            </Link>
          </div>
        </motion.div>
      </div>
    </section>
  )
}