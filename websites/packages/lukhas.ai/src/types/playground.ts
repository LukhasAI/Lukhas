// Playground TypeScript Type Definitions

// Constellation Framework - 8 cognitive nodes
export type ConstellationNode =
  | 'identity'
  | 'memory'
  | 'vision'
  | 'bio'
  | 'dream'
  | 'ethics'
  | 'guardian'
  | 'quantum'

export interface ConstellationNodeConfig {
  id: ConstellationNode
  label: string
  icon: string  // Emoji or icon identifier
  color: string // RGB color string
  description: string
  pulseSpeed: number // Duration in seconds
}

export interface NodeActivation {
  node: ConstellationNode
  intensity: number // 0-1
  timestamp: number
  details?: string
}

// MATRIZ Cognitive Pipeline
export interface MATRIZTrace {
  memory: {
    retrieved: string[]
    traits: string[]
    coherence: number
  }
  attention: {
    focus: string
    weight: number
    tokens: number
  }
  thought: {
    reasoning: string[]
    branches: number
  }
  risk: {
    profile: 'low' | 'medium' | 'high'
    checks: string[]
    blocked: string[]
  }
  intent: {
    primary: string
    secondary: string
    confidence: number
  }
  awareness: {
    coherence: number
    drift: number
    emergent: string[]
  }
}

// Chat Messages
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  trace?: MATRIZTrace
  nodes?: NodeActivation[]
}

// Guardian System
export interface GuardianStatus {
  aligned: boolean
  riskLevel: 'low' | 'medium' | 'high'
  mode: 'conversational' | 'exploratory' | 'cautious'
  checks: {
    category: string
    passed: boolean
    details?: string
  }[]
  constraints: string[]
}

// Dream Mode
export interface DreamOutput {
  narrative: string
  symbols: SymbolicElement[]
  emotions: string[]
  driftScore: number
  convergence: string[]
  motifs: {
    name: string
    significance: number
    recurring: boolean
  }[]
}

export interface SymbolicElement {
  symbol: string
  meaning: string
  intensity: number
}

// Memory System
export interface MemoryAnchor {
  id: string
  timestamp: number
  label: string
  glyph: string
  driftScore: number
  symbols: SymbolicElement[]
  emotions: string[]
}

// UI State
export type ViewMode = 'play' | 'lab'

export interface PlaygroundSettings {
  viewMode: ViewMode
  showGuardian: boolean
  showMemory: boolean
  riskProfile: number // 0-100 slider value
  streamingSpeed: number // Characters per second
}

// API Request/Response
export interface PlaygroundRequest {
  message: string
  settings: PlaygroundSettings
  context: {
    previousMessages: Message[]
    activeMemories: MemoryAnchor[]
  }
}

export interface PlaygroundResponse {
  content: string
  trace: MATRIZTrace
  nodes: NodeActivation[]
  guardian: GuardianStatus
  metadata: {
    model: string
    tokens: number
    latency: number
  }
}

// Loading States
export type LoadingPhase =
  | 'idle'
  | 'aligning'      // "Aligning constellation..."
  | 'reviewing'     // "Guardian reviewing candidate responses..."
  | 'stitching'     // "MATRIZ: stitching Memory → Intent..."
  | 'generating'    // "Generating response..."
  | 'complete'

export interface LoadingState {
  phase: LoadingPhase
  progress: number // 0-100
  message: string
}
