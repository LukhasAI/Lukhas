'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  ChevronLeftIcon, 
  ChevronRightIcon,
  Bars3Icon,
  MagnifyingGlassIcon,
  CommandLineIcon,
  BoltIcon,
  CpuChipIcon,
  BeakerIcon,
  ChatBubbleLeftRightIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  PlusIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'

// Scene presets from visual_studio.json
const SCENE_PRESETS = {
  'ai_collab': {
    name: 'AI Collaboration',
    leftBar: ['model_selector'],
    canvas: 'chat_timeline',
    rightBar: ['unified_inbox']
  },
  'markets': {
    name: 'Markets + Docs',
    leftBar: ['dast_tracker'],
    canvas: 'dashboard',
    rightBar: ['stocks_panel', 'widgets_dock']
  },
  'work': {
    name: 'Work Mode',
    leftBar: ['files', 'vscode'],
    canvas: 'editor',
    rightBar: ['tasks', 'dast_tracker']
  },
  'play': {
    name: 'Play Mode',
    leftBar: ['agents'],
    canvas: 'media_board',
    rightBar: ['media', 'social']
  },
  'research': {
    name: 'Research',
    leftBar: ['models', 'datasets'],
    canvas: 'multi_agent',
    rightBar: ['samples', 'papers']
  }
}

// Canvas states
type CanvasState = 'chat_timeline' | 'preview' | 'player' | 'dashboard' | 'board' | 'editor' | 'media_board' | 'multi_agent'

// Input modes
type InputMode = 'chat' | 'email' | 'doc' | 'code' | 'command'

export default function StudioPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  
  // Layout state
  const [topBarVisible, setTopBarVisible] = useState(false)
  const [leftBarExpanded, setLeftBarExpanded] = useState(true)
  const [rightBarExpanded, setRightBarExpanded] = useState(true)
  const [canvasState, setCanvasState] = useState<CanvasState>('chat_timeline')
  const [currentScene, setCurrentScene] = useState('ai_collab')
  
  // Input state
  const [inputMode, setInputMode] = useState<InputMode>('chat')
  const [inputValue, setInputValue] = useState('')
  const [showCommandPalette, setShowCommandPalette] = useState(false)
  
  // Model selector state
  const [selectedModel, setSelectedModel] = useState('lukhas')
  const [showModelSelector, setShowModelSelector] = useState(false)
  
  // Check authentication
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // Check for session token
        const token = localStorage.getItem('lukhas_session')
        if (!token) {
          router.push('/login')
          return
        }
        setIsAuthenticated(true)
      } catch (error) {
        console.error('Auth check failed:', error)
        router.push('/login')
      } finally {
        setLoading(false)
      }
    }
    
    checkAuth()
  }, [router])
  
  // Auto-hide top bar
  useEffect(() => {
    let timeout: NodeJS.Timeout
    
    const handleMouseMove = (e: MouseEvent) => {
      if (e.clientY < 50) {
        setTopBarVisible(true)
        clearTimeout(timeout)
        timeout = setTimeout(() => setTopBarVisible(false), 1600)
      }
    }
    
    window.addEventListener('mousemove', handleMouseMove)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      clearTimeout(timeout)
    }
  }, [])
  
  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setShowCommandPalette(true)
      }
      
      // Scene switching
      if ((e.metaKey || e.ctrlKey) && e.key >= '1' && e.key <= '5') {
        e.preventDefault()
        const scenes = Object.keys(SCENE_PRESETS)
        const index = parseInt(e.key) - 1
        if (scenes[index]) {
          handleSceneChange(scenes[index])
        }
      }
      
      // Close modals with Escape
      if (e.key === 'Escape') {
        setShowCommandPalette(false)
        setShowModelSelector(false)
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])
  
  // Handle scene change
  const handleSceneChange = useCallback((sceneId: string) => {
    const scene = SCENE_PRESETS[sceneId]
    if (scene) {
      setCurrentScene(sceneId)
      setCanvasState(scene.canvas as CanvasState)
      // Update module visibility based on scene
    }
  }, [])
  
  // Handle input submission
  const handleInputSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim()) return
    
    // Process based on input mode
    switch (inputMode) {
      case 'chat':
        // Send to AI
        console.log('Chat:', inputValue)
        break
      case 'email':
        // Compose email
        console.log('Email:', inputValue)
        break
      case 'command':
        // Execute command
        console.log('Command:', inputValue)
        break
      default:
        break
    }
    
    setInputValue('')
  }, [inputValue, inputMode])
  
  // Detect input mode from content
  const detectInputMode = useCallback((value: string) => {
    if (value.startsWith('/')) {
      setInputMode('command')
    } else if (value.includes('@') && value.includes('.')) {
      setInputMode('email')
    } else if (value.includes('function') || value.includes('const') || value.includes('import')) {
      setInputMode('code')
    } else {
      setInputMode('chat')
    }
  }, [])
  
  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white">Loading studio...</div>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return null
  }
  
  return (
    <div className="min-h-screen bg-black text-white overflow-hidden">
      {/* Top Bar (auto-hide) */}
      <div 
        className={`fixed top-0 left-0 right-0 h-12 bg-black/80 backdrop-blur-xl border-b border-white/10 z-40 transition-transform duration-500 ${
          topBarVisible ? 'translate-y-0' : '-translate-y-full'
        }`}
        onMouseEnter={() => setTopBarVisible(true)}
      >
        <div className="h-full flex items-center justify-between px-4">
          <div className="flex items-center gap-4">
            {/* Logo */}
            <Link href="/" className="text-lg font-light tracking-[0.2em]">
              LUKHΛS
            </Link>
            
            {/* Scene Switcher */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-white/60">Scene:</span>
              <select 
                value={currentScene}
                onChange={(e) => handleSceneChange(e.target.value)}
                className="bg-white/10 border border-white/20 rounded px-2 py-1 text-sm"
              >
                {Object.entries(SCENE_PRESETS).map(([id, scene]) => (
                  <option key={id} value={id}>{scene.name}</option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Search */}
            <button className="text-white/60 hover:text-white">
              <MagnifyingGlassIcon className="w-5 h-5" />
            </button>
            
            {/* Profile Menu */}
            <button className="text-white/60 hover:text-white">
              <UserCircleIcon className="w-5 h-5" />
            </button>
            
            {/* Settings */}
            <button className="text-white/60 hover:text-white">
              <Cog6ToothIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Main Layout */}
      <div className="flex h-screen">
        {/* Left Bar */}
        <div className={`bg-black/40 backdrop-blur-xl border-r border-white/10 transition-all duration-500 ${
          leftBarExpanded ? 'w-80' : 'w-12'
        }`}>
          <div className="h-full flex flex-col">
            {/* Left Bar Header */}
            <div className="h-12 flex items-center justify-between px-3 border-b border-white/10">
              {leftBarExpanded && (
                <span className="text-sm font-light">Modules</span>
              )}
              <button
                onClick={() => setLeftBarExpanded(!leftBarExpanded)}
                className="text-white/60 hover:text-white"
              >
                <ChevronLeftIcon className={`w-5 h-5 transition-transform ${!leftBarExpanded ? 'rotate-180' : ''}`} />
              </button>
            </div>
            
            {/* Left Bar Content */}
            {leftBarExpanded && (
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {/* Model Selector */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-light">AI Model</span>
                    <BoltIcon className="w-4 h-4 text-white/60" />
                  </div>
                  <button
                    onClick={() => setShowModelSelector(true)}
                    className="w-full bg-white/10 hover:bg-white/20 rounded px-3 py-2 text-sm text-left"
                  >
                    {selectedModel === 'lukhas' ? 'LUKHΛS AI' : selectedModel.toUpperCase()}
                  </button>
                </div>
                
                {/* DAST Tracker Placeholder */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-light">DAST Tracker</span>
                    <CpuChipIcon className="w-4 h-4 text-white/60" />
                  </div>
                  <div className="text-xs text-white/40">
                    Live searches will appear here
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Canvas (Main Content Area) */}
        <div className="flex-1 flex flex-col">
          {/* Canvas Content */}
          <div className="flex-1 overflow-hidden relative">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900/10 to-purple-900/10" />
            
            {/* Canvas State Content */}
            <div className="relative h-full flex items-center justify-center">
              {canvasState === 'chat_timeline' && (
                <div className="max-w-3xl w-full px-8">
                  <div className="text-center mb-8">
                    <div className="text-6xl font-light tracking-[0.3em] mb-4 text-white/20">
                      LUKHΛS
                    </div>
                    <p className="text-white/60">Ready to assist. Type below or press Cmd+K for commands.</p>
                  </div>
                </div>
              )}
              
              {canvasState === 'dashboard' && (
                <div className="p-8">
                  <h2 className="text-2xl font-light mb-4">Dashboard</h2>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white/5 rounded-lg p-4">
                      <div className="text-sm text-white/60">Sessions</div>
                      <div className="text-2xl font-light">12</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-4">
                      <div className="text-sm text-white/60">Tokens Used</div>
                      <div className="text-2xl font-light">2.4k</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-4">
                      <div className="text-sm text-white/60">Tier</div>
                      <div className="text-2xl font-light">T2</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Unified Input (Bottom) */}
          <div className="border-t border-white/10 bg-black/60 backdrop-blur-xl">
            <form onSubmit={handleInputSubmit} className="p-4">
              <div className="flex items-center gap-3">
                {/* Mode Indicator */}
                <div className="text-xs text-white/40 min-w-[60px]">
                  {inputMode.toUpperCase()}
                </div>
                
                {/* Input Field */}
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => {
                    setInputValue(e.target.value)
                    detectInputMode(e.target.value)
                  }}
                  placeholder="Type to talk to Lukhas, draft an email, or write..."
                  className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-1 focus:ring-white/20"
                />
                
                {/* Send Button */}
                <button
                  type="submit"
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg hover:opacity-90 transition"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        </div>
        
        {/* Right Bar */}
        <div className={`bg-black/40 backdrop-blur-xl border-l border-white/10 transition-all duration-500 ${
          rightBarExpanded ? 'w-96' : 'w-12'
        }`}>
          <div className="h-full flex flex-col">
            {/* Right Bar Header */}
            <div className="h-12 flex items-center justify-between px-3 border-b border-white/10">
              <button
                onClick={() => setRightBarExpanded(!rightBarExpanded)}
                className="text-white/60 hover:text-white"
              >
                <ChevronRightIcon className={`w-5 h-5 transition-transform ${!rightBarExpanded ? 'rotate-180' : ''}`} />
              </button>
              {rightBarExpanded && (
                <span className="text-sm font-light">Activity</span>
              )}
            </div>
            
            {/* Right Bar Content */}
            {rightBarExpanded && (
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {/* Unified Inbox Placeholder */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-light">Unified Inbox</span>
                    <ChatBubbleLeftRightIcon className="w-4 h-4 text-white/60" />
                  </div>
                  <div className="text-xs text-white/40">
                    Email and messages will appear here
                  </div>
                </div>
                
                {/* Notifications Placeholder */}
                <div className="bg-white/5 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-light">Notifications</span>
                    <span className="text-xs bg-white/20 px-2 py-0.5 rounded">3</span>
                  </div>
                  <div className="space-y-2">
                    <div className="text-xs text-white/60">System update available</div>
                    <div className="text-xs text-white/60">New AI model: GPT-4 Turbo</div>
                    <div className="text-xs text-white/60">DAST search completed</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Command Palette Modal */}
      {showCommandPalette && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-32">
          <div 
            className="absolute inset-0 bg-black/70"
            onClick={() => setShowCommandPalette(false)}
          />
          <div className="relative w-full max-w-2xl bg-black/90 backdrop-blur-xl border border-white/20 rounded-lg overflow-hidden">
            <div className="p-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                <CommandLineIcon className="w-5 h-5 text-white/60" />
                <input
                  type="text"
                  placeholder="Type a command..."
                  className="flex-1 bg-transparent text-white placeholder-white/40 focus:outline-none"
                  autoFocus
                />
                <button
                  onClick={() => setShowCommandPalette(false)}
                  className="text-white/60 hover:text-white"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="p-4">
              <div className="text-xs text-white/40 mb-2">Quick Actions</div>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 hover:bg-white/10 rounded cursor-pointer">
                  <span className="text-sm">Start New Chat</span>
                  <kbd className="text-xs bg-white/10 px-2 py-1 rounded">Ctrl+N</kbd>
                </div>
                <div className="flex items-center justify-between p-2 hover:bg-white/10 rounded cursor-pointer">
                  <span className="text-sm">Search Research</span>
                  <kbd className="text-xs bg-white/10 px-2 py-1 rounded">Ctrl+K</kbd>
                </div>
                <div className="flex items-center justify-between p-2 hover:bg-white/10 rounded cursor-pointer">
                  <span className="text-sm">Open Settings</span>
                  <kbd className="text-xs bg-white/10 px-2 py-1 rounded">Ctrl+,</kbd>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Model Selector Modal */}
      {showModelSelector && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div 
            className="absolute inset-0 bg-black/70"
            onClick={() => setShowModelSelector(false)}
          />
          <div className="relative w-full max-w-md bg-black/90 backdrop-blur-xl border border-white/20 rounded-lg p-6">
            <h3 className="text-lg font-light mb-4">Select AI Model</h3>
            <div className="space-y-2">
              {['lukhas', 'openai', 'anthropic', 'perplexity', 'gemini'].map((model) => (
                <button
                  key={model}
                  onClick={() => {
                    setSelectedModel(model)
                    setShowModelSelector(false)
                  }}
                  className={`w-full p-3 rounded-lg text-left transition ${
                    selectedModel === model 
                      ? 'bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-600/50' 
                      : 'bg-white/5 hover:bg-white/10'
                  }`}
                >
                  <div className="font-medium">
                    {model === 'lukhas' ? 'LUKHΛS AI' : model.charAt(0).toUpperCase() + model.slice(1)}
                  </div>
                  <div className="text-xs text-white/60 mt-1">
                    {model === 'lukhas' && 'Default - Quantum-inspired consciousness'}
                    {model === 'openai' && 'GPT-4 and DALL-E models'}
                    {model === 'anthropic' && 'Claude 3 models'}
                    {model === 'perplexity' && 'Search-optimized AI'}
                    {model === 'gemini' && 'Google Gemini models'}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}