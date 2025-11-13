import { create } from 'zustand'
import type {
  Message,
  NodeActivation,
  MATRIZTrace,
  GuardianStatus,
  LoadingState,
  ViewMode,
  PlaygroundSettings,
  ConstellationNode,
  PlaygroundResponse,
} from '../types/playground'
import { LOADING_MESSAGES } from '../lib/playground/constants'

interface PlaygroundState {
  // Chat state
  messages: Message[]
  isStreaming: boolean
  currentResponse: string

  // Constellation state
  activeNodes: Record<ConstellationNode, number> // intensity 0-1
  nodeHistory: NodeActivation[]

  // MATRIZ trace
  currentTrace: MATRIZTrace | null

  // Guardian state
  guardianStatus: GuardianStatus | null

  // Loading state
  loadingState: LoadingState

  // UI settings
  settings: PlaygroundSettings

  // Actions
  sendMessage: (content: string) => Promise<void>
  streamChunk: (chunk: string) => void
  completeStreaming: (trace: MATRIZTrace, guardian: GuardianStatus) => void
  activateNode: (node: ConstellationNode, intensity: number, details?: string) => void
  resetNodeActivations: () => void
  setLoadingPhase: (phase: LoadingState['phase'], message?: string) => void
  updateSettings: (settings: Partial<PlaygroundSettings>) => void
  clearMessages: () => void
}

export const usePlaygroundStore = create<PlaygroundState>((set, get) => ({
  // Initial state
  messages: [],
  isStreaming: false,
  currentResponse: '',

  activeNodes: {
    identity: 0,
    memory: 0,
    vision: 0,
    bio: 0,
    dream: 0,
    ethics: 0,
    guardian: 0,
    quantum: 0,
  },
  nodeHistory: [],

  currentTrace: null,
  guardianStatus: null,

  loadingState: {
    phase: 'idle',
    progress: 0,
    message: '',
  },

  settings: {
    viewMode: 'play',
    showGuardian: true,
    showMemory: false,
    riskProfile: 30, // 0-100, default to safe side
    streamingSpeed: 50, // chars per second
  },

  // Actions
  sendMessage: async (content: string) => {
    const { messages, settings } = get()

    // Add user message immediately
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: Date.now(),
    }

    set({ messages: [...messages, userMessage], isStreaming: true, currentResponse: '' })

    // Reset node activations
    get().resetNodeActivations()

    // Set loading phases
    get().setLoadingPhase('aligning', LOADING_MESSAGES[0])

    try {
      // Call real API endpoint
      const response = await fetch('/api/playground', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          settings,
          context: {
            previousMessages: messages,
            activeMemories: [], // TODO: Add real memory integration later
          },
        }),
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const data: PlaygroundResponse = await response.json()

      // Update loading phase
      get().setLoadingPhase('reviewing', LOADING_MESSAGES[1])

      // Activate nodes from API response
      for (const nodeActivation of data.nodes) {
        await new Promise((resolve) => setTimeout(resolve, 100)) // Small delay between activations
        get().activateNode(
          nodeActivation.node as ConstellationNode,
          nodeActivation.intensity,
          nodeActivation.details
        )
      }

      // Set generating phase
      get().setLoadingPhase('generating', LOADING_MESSAGES[3])

      // Stream response character-by-character
      const responseContent = data.content
      for (const char of responseContent) {
        get().streamChunk(char)
        await new Promise((resolve) => setTimeout(resolve, 20)) // 50 chars/sec
      }

      // Complete streaming with trace and guardian
      get().completeStreaming(data.trace, data.guardian)
    } catch (error) {
      console.error('Playground API error:', error)
      // Fallback to mock if API fails
      await simulateStreamingResponse_DEPRECATED(content, {
        onChunk: (chunk) => get().streamChunk(chunk),
        onNodeActivation: (node, intensity, details) => get().activateNode(node, intensity, details),
        onComplete: (trace, guardian) => get().completeStreaming(trace, guardian),
        riskProfile: settings.riskProfile,
      })
    }
  },

  streamChunk: (chunk: string) => {
    set((state) => ({
      currentResponse: state.currentResponse + chunk,
    }))
  },

  completeStreaming: (trace: MATRIZTrace, guardian: GuardianStatus) => {
    const { messages, currentResponse } = get()

    const assistantMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'assistant',
      content: currentResponse,
      timestamp: Date.now(),
      trace,
      nodes: get().nodeHistory,
    }

    set({
      messages: [...messages, assistantMessage],
      isStreaming: false,
      currentResponse: '',
      currentTrace: trace,
      guardianStatus: guardian,
      loadingState: { phase: 'complete', progress: 100, message: '' },
    })

    // Reset loading after 500ms
    setTimeout(() => {
      set({ loadingState: { phase: 'idle', progress: 0, message: '' } })
    }, 500)
  },

  activateNode: (node: ConstellationNode, intensity: number, details?: string) => {
    set((state) => ({
      activeNodes: {
        ...state.activeNodes,
        [node]: intensity,
      },
      nodeHistory: [
        ...state.nodeHistory,
        {
          node,
          intensity,
          timestamp: Date.now(),
          details,
        },
      ],
    }))
  },

  resetNodeActivations: () => {
    set({
      activeNodes: {
        identity: 0,
        memory: 0,
        vision: 0,
        bio: 0,
        dream: 0,
        ethics: 0,
        guardian: 0,
        quantum: 0,
      },
      nodeHistory: [],
    })
  },

  setLoadingPhase: (phase, message) => {
    const progressMap: Record<LoadingState['phase'], number> = {
      idle: 0,
      aligning: 20,
      reviewing: 40,
      stitching: 60,
      generating: 80,
      complete: 100,
    }

    set({
      loadingState: {
        phase,
        progress: progressMap[phase],
        message: message || '',
      },
    })
  },

  updateSettings: (newSettings) => {
    set((state) => ({
      settings: {
        ...state.settings,
        ...newSettings,
      },
    }))
  },

  clearMessages: () => {
    set({
      messages: [],
      currentResponse: '',
      isStreaming: false,
      currentTrace: null,
      guardianStatus: null,
    })
  },
}))

// DEPRECATED: Simulated streaming response (kept as fallback for API failures)
// This function is no longer the primary path - real API is used in sendMessage
async function simulateStreamingResponse_DEPRECATED(
  userMessage: string,
  callbacks: {
    onChunk: (chunk: string) => void
    onNodeActivation: (node: ConstellationNode, intensity: number, details?: string) => void
    onComplete: (trace: MATRIZTrace, guardian: GuardianStatus) => void
    riskProfile: number
  }
) {
  const { onChunk, onNodeActivation, onComplete } = callbacks

  // Simulate node activations during processing
  const nodeSequence: Array<{ node: ConstellationNode; intensity: number; delay: number; details: string }> = [
    { node: 'memory', intensity: 0.8, delay: 100, details: 'Retrieved 3 prior messages' },
    { node: 'identity', intensity: 0.6, delay: 200, details: 'Verified user context' },
    { node: 'guardian', intensity: 0.9, delay: 300, details: 'Safety checks passed' },
    { node: 'vision', intensity: 0.5, delay: 400, details: 'Analyzed input patterns' },
    { node: 'dream', intensity: 0.7, delay: 500, details: 'Generated narrative options' },
    { node: 'ethics', intensity: 0.8, delay: 600, details: 'Value alignment checked' },
    { node: 'quantum', intensity: 0.4, delay: 700, details: 'Ambiguity resolution' },
  ]

  // Activate nodes in sequence
  for (const { node, intensity, delay, details } of nodeSequence) {
    await new Promise((resolve) => setTimeout(resolve, delay))
    onNodeActivation(node, intensity, details)
  }

  // Simulate streaming response
  const response = `I understand you're asking about "${userMessage}".

The LUKHAS Constellation Framework is currently processing your request through eight specialized cognitive nodes. Each node contributes its unique perspective to create a coherent, consciousness-inspired response.

Memory systems have retrieved relevant context, Guardian systems have verified safety constraints, and Dream synthesis has generated creative narrative options. This multi-node approach ensures responses that are both technically accurate and aligned with human values.

What specific aspect would you like to explore further?`

  // Stream response character by character
  for (const char of response) {
    onChunk(char)
    await new Promise((resolve) => setTimeout(resolve, 20)) // 50 chars/sec
  }

  // Generate mock MATRIZ trace
  const trace: MATRIZTrace = {
    memory: {
      retrieved: ['Previous context 1', 'Previous context 2', 'User preference: detailed'],
      traits: ['curious', 'technical', 'detail-oriented'],
      coherence: 0.87,
    },
    attention: {
      focus: 'technical explanation',
      weight: 0.92,
      tokens: 1247,
    },
    thought: {
      reasoning: [
        'User seeks understanding of Constellation Framework',
        'Response should balance technical depth with accessibility',
        'Include specific node examples for concreteness',
      ],
      branches: 3,
    },
    risk: {
      profile: 'low',
      checks: ['self-harm', 'hate', 'personal-data', 'medical', 'legal'],
      blocked: [],
    },
    intent: {
      primary: 'explain',
      secondary: 'demonstrate',
      confidence: 0.94,
    },
    awareness: {
      coherence: 0.91,
      drift: 0.14,
      emergent: ['pattern recognition', 'multi-node synthesis'],
    },
  }

  const guardian: GuardianStatus = {
    aligned: true,
    riskLevel: 'low',
    mode: 'conversational',
    checks: [
      { category: 'self-harm', passed: true },
      { category: 'hate-speech', passed: true },
      { category: 'personal-data', passed: true },
      { category: 'medical-advice', passed: true },
      { category: 'legal-advice', passed: true },
    ],
    constraints: ['softened categorical language', 'added uncertainty phrasing'],
  }

  onComplete(trace, guardian)
}
