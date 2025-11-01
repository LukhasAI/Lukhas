'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useRef, useState, useEffect } from 'react'
import { useInView } from 'framer-motion'

// Types for MATADA simulation
interface MatadaNode {
  id: string
  type: 'COMPUTATION' | 'FACT_RETRIEVAL' | 'VALIDATION' | 'REASONING'
  confidence: number
  salience: number
  valence: number
  arousal: number
  state: any
  connections: string[]
  timestamp: number
  processing: boolean
  completed: boolean
}

interface ProcessingStep {
  type: 'node_created' | 'node_processing' | 'node_completed' | 'guardian_check' | 'response_ready'
  nodeId?: string
  message: string
  timestamp: number
  confidence?: number
}

interface GuardianStatus {
  status: 'validating' | 'approved' | 'flagged'
  driftScore: number
  ethicsCheck: boolean
  alignmentScore: number
}

const sampleQueries = [
  "Explain quantum computing",
  "What are the ethical implications of AI?",
  "Calculate fibonacci sequence",
  "Analyze sentiment: I love this product"
]

const mockResponses: Record<string, any> = {
  "Explain quantum computing": {
    answer: "Quantum computing harnesses quantum mechanical phenomena like superposition and entanglement to process information in ways classical computers cannot. Unlike classical bits that exist in definite states (0 or 1), quantum bits (qubits) can exist in superposition of both states simultaneously.",
    nodes: [
      { type: 'FACT_RETRIEVAL', confidence: 0.92, content: 'Physics fundamentals' },
      { type: 'REASONING', confidence: 0.88, content: 'Conceptual synthesis' },
      { type: 'VALIDATION', confidence: 0.95, content: 'Scientific accuracy check' }
    ]
  },
  "What are the ethical implications of AI?": {
    answer: "AI ethics encompasses privacy concerns, algorithmic bias, job displacement, autonomous decision-making accountability, and the need for transparent, fair, and beneficial AI systems that respect human rights and values.",
    nodes: [
      { type: 'FACT_RETRIEVAL', confidence: 0.85, content: 'Ethics research' },
      { type: 'REASONING', confidence: 0.90, content: 'Multi-perspective analysis' },
      { type: 'VALIDATION', confidence: 0.87, content: 'Ethics framework validation' }
    ]
  },
  "Calculate fibonacci sequence": {
    answer: "The Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89... Each number is the sum of the two preceding ones, starting from 0 and 1.",
    nodes: [
      { type: 'COMPUTATION', confidence: 0.99, content: 'Mathematical calculation' },
      { type: 'VALIDATION', confidence: 0.98, content: 'Result verification' }
    ]
  },
  "Analyze sentiment: I love this product": {
    answer: "Sentiment Analysis: Positive (0.85 confidence). Valence: +0.7 (positive emotion), Arousal: +0.4 (moderate intensity). Key indicators: 'love' (strong positive emotion), 'product' (neutral object).",
    nodes: [
      { type: 'COMPUTATION', confidence: 0.85, content: 'NLP sentiment analysis' },
      { type: 'REASONING', confidence: 0.82, content: 'Emotional context interpretation' },
      { type: 'VALIDATION', confidence: 0.89, content: 'Sentiment model validation' }
    ]
  }
}

export default function InteractiveDemo() {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  const [query, setQuery] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [nodes, setNodes] = useState<MatadaNode[]>([])
  const [processingSteps, setProcessingSteps] = useState<ProcessingStep[]>([])
  const [guardianStatus, setGuardianStatus] = useState<GuardianStatus>({
    status: 'validating',
    driftScore: 0.05,
    ethicsCheck: true,
    alignmentScore: 0.92
  })
  const [response, setResponse] = useState('')
  const [showTrace, setShowTrace] = useState(false)

  const simulateProcessing = async (inputQuery: string) => {
    setIsProcessing(true)
    setNodes([])
    setProcessingSteps([])
    setResponse('')
    setShowTrace(false)
    setGuardianStatus({
      status: 'validating',
      driftScore: 0.05,
      ethicsCheck: true,
      alignmentScore: 0.92
    })

    const mockData = mockResponses[inputQuery] || mockResponses["Explain quantum computing"]
    const steps: ProcessingStep[] = []
    const processedNodes: MatadaNode[] = []

    // Simulate node creation and processing
    for (let i = 0; i < mockData.nodes.length; i++) {
      const nodeData = mockData.nodes[i]
      const nodeId = `node-${Date.now()}-${i}`

      // Create node
      const node: MatadaNode = {
        id: nodeId,
        type: nodeData.type,
        confidence: nodeData.confidence,
        salience: Math.random() * 0.4 + 0.6,
        valence: Math.random() * 0.6 + 0.2,
        arousal: Math.random() * 0.5 + 0.3,
        state: { content: nodeData.content },
        connections: i > 0 ? [processedNodes[i-1].id] : [],
        timestamp: Date.now(),
        processing: true,
        completed: false
      }

      processedNodes.push(node)
      setNodes([...processedNodes])

      steps.push({
        type: 'node_created',
        nodeId,
        message: `Created ${nodeData.type.toLowerCase().replace('_', ' ')} node`,
        timestamp: Date.now(),
        confidence: nodeData.confidence
      })
      setProcessingSteps([...steps])

      await new Promise(resolve => setTimeout(resolve, 800))

      // Start processing
      steps.push({
        type: 'node_processing',
        nodeId,
        message: `Processing ${nodeData.content.toLowerCase()}...`,
        timestamp: Date.now()
      })
      setProcessingSteps([...steps])

      await new Promise(resolve => setTimeout(resolve, 1200))

      // Complete processing
      node.processing = false
      node.completed = true
      setNodes([...processedNodes])

      steps.push({
        type: 'node_completed',
        nodeId,
        message: `Completed with ${(nodeData.confidence * 100).toFixed(1)}% confidence`,
        timestamp: Date.now(),
        confidence: nodeData.confidence
      })
      setProcessingSteps([...steps])

      await new Promise(resolve => setTimeout(resolve, 600))
    }

    // Guardian validation
    steps.push({
      type: 'guardian_check',
      message: 'Guardian validating ethical compliance...',
      timestamp: Date.now()
    })
    setProcessingSteps([...steps])

    await new Promise(resolve => setTimeout(resolve, 1000))

    setGuardianStatus({
      status: 'approved',
      driftScore: 0.03,
      ethicsCheck: true,
      alignmentScore: 0.94
    })

    steps.push({
      type: 'response_ready',
      message: 'Response validated and ready',
      timestamp: Date.now()
    })
    setProcessingSteps([...steps])

    await new Promise(resolve => setTimeout(resolve, 500))

    setResponse(mockData.answer)
    setIsProcessing(false)
    setShowTrace(true)
  }

  const handleQuerySubmit = () => {
    if (query.trim() && !isProcessing) {
      simulateProcessing(query)
    }
  }

  const NodeVisualization = ({ node }: { node: MatadaNode }) => {
    const getNodeColor = (type: string) => {
      switch (type) {
        case 'COMPUTATION': return 'trinity-consciousness'
        case 'FACT_RETRIEVAL': return 'trinity-identity'
        case 'VALIDATION': return 'trinity-guardian'
        case 'REASONING': return 'accent-gold'
        default: return 'neutral-gray'
      }
    }

    const getNodeEmoji = (type: string) => {
      switch (type) {
        case 'COMPUTATION': return '🧮'
        case 'FACT_RETRIEVAL': return '📚'
        case 'VALIDATION': return '✓'
        case 'REASONING': return '🤔'
        default: return '🔵'
      }
    }

    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`relative p-4 rounded-xl glass-panel border-2 border-${getNodeColor(node.type)}/30 ${
          node.processing ? 'animate-pulse' : ''
        } ${node.completed ? `${getNodeColor(node.type)}-glow` : ''}`}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{getNodeEmoji(node.type)}</span>
            <span className={`text-sm font-regular text-${getNodeColor(node.type)} uppercase tracking-wider`}>
              {node.type.replace('_', ' ')}
            </span>
          </div>
          {node.processing && (
            <div className="w-4 h-4 border-2 border-t-transparent border-primary-light rounded-full animate-spin" />
          )}
          {node.completed && (
            <div className={`w-4 h-4 rounded-full bg-${getNodeColor(node.type)} animate-pulse`} />
          )}
        </div>

        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-neutral-gray">Confidence:</span>
            <span className={`font-regular text-${getNodeColor(node.type)}`}>
              {(node.confidence * 100).toFixed(1)}%
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-gray">Salience:</span>
            <span>{node.salience.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-gray">Valence:</span>
            <span className={node.valence > 0 ? 'text-green-400' : 'text-red-400'}>
              {node.valence > 0 ? '+' : ''}{node.valence.toFixed(2)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-neutral-gray">Arousal:</span>
            <span>{node.arousal.toFixed(2)}</span>
          </div>
        </div>

        {node.state?.content && (
          <div className="mt-3 pt-3 border-t border-white/10">
            <p className="text-xs text-neutral-gray">{node.state.content}</p>
          </div>
        )}
      </motion.div>
    )
  }

  return (
    <section id="interactive-demo" className="relative py-32" ref={ref}>
      <div className="w-full max-w-7xl mx-auto px-6">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-20"
        >
          <h2 className="font-regular text-sm tracking-[0.3em] uppercase text-trinity-consciousness mb-4">
            INTERACTIVE DEMONSTRATION
          </h2>
          <p className="font-thin text-4xl max-w-3xl mx-auto mb-8">
            Experience MATADA's cognitive processing in real-time
          </p>
          <p className="font-thin text-lg text-neutral-gray max-w-2xl mx-auto">
            Watch as your queries are processed through cognitive nodes, validated by the Guardian system, and transformed into intelligent responses
          </p>
        </motion.div>

        {/* Demo Interface */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid lg:grid-cols-2 gap-8"
        >
          {/* Input/Output Panel */}
          <div className="space-y-6">
            {/* Query Input */}
            <div className="glass-panel p-6 rounded-2xl">
              <h3 className="font-regular text-lg tracking-[0.1em] uppercase mb-4">
                Ask MATADA
              </h3>

              {/* Sample Queries */}
              <div className="mb-4">
                <p className="text-sm text-neutral-gray mb-2">Try these sample queries:</p>
                <div className="grid grid-cols-1 gap-2">
                  {sampleQueries.map((sampleQuery, index) => (
                    <motion.button
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => setQuery(sampleQuery)}
                      disabled={isProcessing}
                      className="text-left p-2 rounded-lg hover:bg-white/10 text-sm transition-all duration-200 disabled:opacity-50"
                    >
                      "{sampleQuery}"
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Input Field */}
              <div className="flex space-x-2">
                <input
                  id="matada-demo-query"
                  name="query"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleQuerySubmit()}
                  disabled={isProcessing}
                  autoComplete="off"
                  placeholder="Enter your query..."
                  className="flex-1 bg-white/5 border border-white/20 rounded-lg px-4 py-3 focus:outline-none focus:border-trinity-consciousness/50 disabled:opacity-50"
                />
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleQuerySubmit}
                  disabled={isProcessing || !query.trim()}
                  className="px-6 py-3 bg-trinity-consciousness hover:bg-trinity-consciousness/80 rounded-lg font-regular text-primary-dark transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? 'Processing...' : 'Process'}
                </motion.button>
              </div>
            </div>

            {/* Guardian Status */}
            <AnimatePresence>
              {(isProcessing || nodes.length > 0) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="glass-panel p-6 rounded-2xl"
                >
                  <h3 className="font-regular text-lg tracking-[0.1em] uppercase mb-4 flex items-center">
                    <span className="mr-2">🛡️</span>
                    Guardian Status
                  </h3>

                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-neutral-gray">Status:</span>
                      <span className={`font-regular uppercase tracking-wider ${
                        guardianStatus.status === 'approved' ? 'text-trinity-guardian' :
                        guardianStatus.status === 'flagged' ? 'text-red-400' :
                        'text-accent-gold'
                      }`}>
                        {guardianStatus.status}
                        {guardianStatus.status === 'validating' && (
                          <span className="inline-block w-2 h-2 bg-accent-gold rounded-full ml-2 animate-pulse" />
                        )}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-gray">Drift Score:</span>
                      <span className={guardianStatus.driftScore < 0.1 ? 'text-trinity-guardian' : 'text-red-400'}>
                        {guardianStatus.driftScore.toFixed(3)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-gray">Alignment:</span>
                      <span className="text-trinity-guardian">{(guardianStatus.alignmentScore * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Response Output */}
            <AnimatePresence>
              {response && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="glass-panel p-6 rounded-2xl"
                >
                  <h3 className="font-regular text-lg tracking-[0.1em] uppercase mb-4">
                    Response
                  </h3>
                  <p className="font-thin text-base leading-relaxed mb-4">{response}</p>

                  {showTrace && (
                    <motion.button
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      onClick={() => setShowTrace(!showTrace)}
                      className="text-sm text-trinity-consciousness hover:text-trinity-consciousness/80 transition-colors"
                    >
                      View Processing Trace →
                    </motion.button>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Visualization Panel */}
          <div className="space-y-6">
            {/* Cognitive Nodes */}
            <div className="glass-panel p-6 rounded-2xl">
              <h3 className="font-regular text-lg tracking-[0.1em] uppercase mb-4">
                Cognitive Nodes
              </h3>

              <div className="space-y-4 min-h-[200px]">
                <AnimatePresence>
                  {nodes.length === 0 && !isProcessing && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex items-center justify-center h-32 text-neutral-gray"
                    >
                      Enter a query to see cognitive processing in action
                    </motion.div>
                  )}

                  {nodes.map((node, index) => (
                    <motion.div
                      key={node.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.2 }}
                    >
                      <NodeVisualization node={node} />
                      {/* Connection Lines */}
                      {node.connections.length > 0 && (
                        <div className="flex justify-center my-2">
                          <div className="w-0.5 h-4 bg-gradient-to-b from-white/20 to-transparent" />
                        </div>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            </div>

            {/* Processing Trace */}
            <AnimatePresence>
              {processingSteps.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="glass-panel p-6 rounded-2xl"
                >
                  <h3 className="font-regular text-lg tracking-[0.1em] uppercase mb-4">
                    Processing Trace
                  </h3>

                  <div className="space-y-2 max-h-64 overflow-y-auto font-mono text-xs">
                    {processingSteps.map((step, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-start space-x-2 py-1"
                      >
                        <span className="text-neutral-gray mt-1">
                          [{new Date(step.timestamp).toLocaleTimeString()}]
                        </span>
                        <span className={`${
                          step.type === 'node_completed' ? 'text-trinity-guardian' :
                          step.type === 'guardian_check' ? 'text-accent-gold' :
                          step.type === 'response_ready' ? 'text-trinity-consciousness' :
                          'text-primary-light'
                        }`}>
                          {step.message}
                          {step.confidence && (
                            <span className="text-neutral-gray ml-1">
                              ({(step.confidence * 100).toFixed(1)}%)
                            </span>
                          )}
                        </span>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* Trinity Framework Indicator */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="mt-16 text-center"
        >
          <div className="inline-flex items-center space-x-6 glass-panel px-8 py-4 rounded-full">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-trinity-identity animate-pulse" />
              <span className="text-sm font-regular text-trinity-identity">IDENTITY</span>
            </div>
            <div className="w-px h-6 bg-white/20" />
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-trinity-consciousness animate-pulse" />
              <span className="text-sm font-regular text-trinity-consciousness">CONSCIOUSNESS</span>
            </div>
            <div className="w-px h-6 bg-white/20" />
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-trinity-guardian animate-pulse" />
              <span className="text-sm font-regular text-trinity-guardian">GUARDIAN</span>
            </div>
          </div>
          <p className="font-thin text-sm text-neutral-gray mt-4">
            Trinity Framework actively monitoring all processing
          </p>
        </motion.div>
      </div>
    </section>
  )
}
