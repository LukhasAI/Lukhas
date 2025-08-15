'use client'

import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef, useState } from 'react'

interface ProcessStep {
  id: string
  number: string
  title: string
  description: string
  color: string
  icon: string
  details: string[]
  code?: string
}

const processSteps: ProcessStep[] = [
  {
    id: 'input',
    number: '01',
    title: 'USER INPUT',
    description: 'Query enters the system with full context and user intent',
    color: 'neutral-gray',
    icon: '📝',
    details: [
      'Natural language processing',
      'Context extraction',
      'Intent parsing',
      'Query vectorization'
    ],
    code: `// Example query
const userQuery = {
  text: "Analyze market trends for Q4",
  context: "financial_analysis",
  priority: "high"
}`
  },
  {
    id: 'analysis',
    number: '02',
    title: 'INTENT ANALYSIS',
    description: 'MATADA analyzes the deep intent and emotional context',
    color: 'trinity-identity',
    icon: '⚛️',
    details: [
      'Semantic understanding',
      'Emotional tone detection',
      'Context graph building',
      'Intent classification'
    ],
    code: `// Intent analysis
const analysis = {
  intent: "data_analysis",
  emotion: "urgency",
  complexity: "moderate",
  domain: "finance"
}`
  },
  {
    id: 'selection',
    number: '03',
    title: 'NODE SELECTION',
    description: 'Appropriate cognitive nodes are selected and activated',
    color: 'trinity-consciousness',
    icon: '🧠',
    details: [
      'Node capability matching',
      'Resource availability check',
      'Load balancing',
      'Optimal path finding'
    ],
    code: `// Node selection
const selectedNodes = [
  "financial_analyzer",
  "data_processor", 
  "pattern_detector"
]`
  },
  {
    id: 'processing',
    number: '04',
    title: 'PROCESSING',
    description: 'Selected nodes process with full contextual awareness',
    color: 'accent-gold',
    icon: '⚙️',
    details: [
      'Parallel processing',
      'Context preservation',
      'Memory integration',
      'Cross-node communication'
    ],
    code: `// Processing pipeline
await Promise.all([
  nodes.analyze(data),
  nodes.crossReference(context),
  nodes.validateResults()
])`
  },
  {
    id: 'validation',
    number: '05',
    title: 'VALIDATION',
    description: 'Guardian validates ethical alignment and accuracy',
    color: 'trinity-guardian',
    icon: '🛡️',
    details: [
      'Ethical compliance check',
      'Accuracy validation',
      'Bias detection',
      'Risk assessment'
    ],
    code: `// Guardian validation
const validation = {
  ethicsScore: 0.95,
  accuracyCheck: "passed",
  biasDetected: false,
  riskLevel: "low"
}`
  },
  {
    id: 'evolution',
    number: '06',
    title: 'EVOLUTION',
    description: 'System learns and evolves from the interaction',
    color: 'trinity-consciousness',
    icon: '🌱',
    details: [
      'Pattern recognition',
      'Memory consolidation',
      'Model fine-tuning',
      'Capability expansion'
    ],
    code: `// Learning update
system.learn({
  pattern: queryPattern,
  response: processedResult,
  feedback: userSatisfaction
})`
  },
  {
    id: 'response',
    number: '07',
    title: 'RESPONSE',
    description: 'Traceable response delivered with full audit trail',
    color: 'primary-light',
    icon: '📊',
    details: [
      'Response synthesis',
      'Audit trail generation',
      'Confidence scoring',
      'Delivery optimization'
    ],
    code: `// Response with audit
const response = {
  answer: processedResult,
  confidence: 0.97,
  auditTrail: stepHistory,
  sources: referencedData
}`
  }
]

export default function HowItWorks() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  const [activeStep, setActiveStep] = useState<string>('input')
  const [hoveredStep, setHoveredStep] = useState<string | null>(null)

  return (
    <section id="how-it-works" className="relative py-32 px-6" ref={ref}>
      <div className="container mx-auto max-w-7xl">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-accent-gold mb-4">
            HOW IT WORKS
          </h2>
          <p className="font-thin text-4xl max-w-4xl mx-auto">
            A transparent, traceable journey from input to intelligent response
          </p>
        </motion.div>

        {/* Process Timeline */}
        <div className="relative">
          {/* Background Timeline Line */}
          <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-gradient-to-b from-trinity-identity via-trinity-consciousness to-trinity-guardian opacity-30"></div>

          {/* Process Steps */}
          <div className="space-y-24">
            {processSteps.map((step, index) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ duration: 0.8, delay: index * 0.2 }}
                className={`relative flex items-center ${
                  index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'
                }`}
                onMouseEnter={() => setHoveredStep(step.id)}
                onMouseLeave={() => setHoveredStep(null)}
                onClick={() => setActiveStep(step.id)}
              >
                {/* Step Content */}
                <div className={`w-5/12 ${index % 2 === 0 ? 'pr-12 text-right' : 'pl-12 text-left'}`}>
                  <motion.div
                    className={`glass-panel p-8 rounded-2xl cursor-pointer transition-all duration-300 hover-lift ${
                      activeStep === step.id ? 'ring-2 ring-white/20' : ''
                    } ${hoveredStep === step.id ? `${step.color}-glow` : ''}`}
                    whileHover={{ scale: 1.02 }}
                  >
                    {/* Step Header */}
                    <div className={`flex items-center ${index % 2 === 0 ? 'justify-end' : 'justify-start'} mb-4`}>
                      <span className="text-6xl mr-4">{step.icon}</span>
                      <div>
                        <p className={`font-regular text-sm tracking-[0.2em] uppercase text-${step.color} mb-1`}>
                          STEP {step.number}
                        </p>
                        <h3 className="font-regular text-xl tracking-[0.1em] uppercase">
                          {step.title}
                        </h3>
                      </div>
                    </div>

                    {/* Step Description */}
                    <p className="font-thin text-lg mb-6 text-neutral-gray">
                      {step.description}
                    </p>

                    {/* Step Details */}
                    <div className="space-y-2">
                      {step.details.map((detail, detailIndex) => (
                        <motion.div
                          key={detailIndex}
                          initial={{ opacity: 0, x: 10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: detailIndex * 0.1 }}
                          className={`flex items-center ${index % 2 === 0 ? 'justify-end' : 'justify-start'} space-x-3`}
                        >
                          {index % 2 !== 0 && (
                            <div className={`w-2 h-2 rounded-full bg-${step.color}`} />
                          )}
                          <p className="font-thin text-sm">{detail}</p>
                          {index % 2 === 0 && (
                            <div className={`w-2 h-2 rounded-full bg-${step.color}`} />
                          )}
                        </motion.div>
                      ))}
                    </div>

                    {/* Code Example */}
                    {step.code && activeStep === step.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        transition={{ duration: 0.3 }}
                        className="mt-6 p-4 bg-black/50 rounded-lg overflow-hidden"
                      >
                        <pre className="text-xs text-primary-light font-mono overflow-x-auto">
                          <code>{step.code}</code>
                        </pre>
                      </motion.div>
                    )}
                  </motion.div>
                </div>

                {/* Timeline Node */}
                <div className="absolute left-1/2 transform -translate-x-1/2 z-10">
                  <motion.div
                    className={`w-6 h-6 rounded-full bg-${step.color} border-4 border-primary-dark transition-all duration-300 ${
                      activeStep === step.id ? 'scale-150' : 'scale-100'
                    } ${hoveredStep === step.id ? `${step.color}-glow` : ''}`}
                    whileHover={{ scale: 1.5 }}
                  />
                </div>

                {/* Empty Space for Alternating Layout */}
                <div className="w-5/12"></div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Interactive Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 1.4 }}
          className="mt-32 glass-panel p-12 rounded-2xl text-center"
        >
          <h3 className="font-regular text-2xl tracking-[0.1em] uppercase mb-6 gradient-text">
            THE RESULT
          </h3>
          <p className="font-thin text-xl max-w-4xl mx-auto mb-8">
            Every response is backed by transparent reasoning, ethical validation, and continuous learning. 
            MATADA doesn't just answer—it thinks, validates, and evolves with each interaction.
          </p>
          
          {/* Key Benefits */}
          <div className="grid md:grid-cols-3 gap-8 mt-12">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-trinity-identity/20 flex items-center justify-center trinity-identity-glow">
                <span className="text-2xl">🎯</span>
              </div>
              <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-2">PRECISION</h4>
              <p className="font-thin text-sm text-neutral-gray">Contextually aware responses with 97% accuracy</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-trinity-guardian/20 flex items-center justify-center trinity-guardian-glow">
                <span className="text-2xl">🔒</span>
              </div>
              <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-2">TRUST</h4>
              <p className="font-thin text-sm text-neutral-gray">Full audit trails and ethical validation</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-trinity-consciousness/20 flex items-center justify-center trinity-consciousness-glow">
                <span className="text-2xl">📈</span>
              </div>
              <h4 className="font-regular text-sm tracking-[0.2em] uppercase mb-2">EVOLUTION</h4>
              <p className="font-thin text-sm text-neutral-gray">Continuous learning and improvement</p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}