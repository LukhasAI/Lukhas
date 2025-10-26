'use client'

import { useState, useEffect } from 'react'
import { X, Save, Eye, EyeOff, Check, AlertCircle } from 'lucide-react'

interface ProteusConfigProps {
  isOpen: boolean
  onClose: () => void
}

interface ApiConfig {
  openaiKey: string
  anthropicKey: string
  googleKey: string
  perplexityKey: string
  localEndpoint: string
}

interface VisualizationConfig {
  particleCount: number
  boundaryForce: number
  attractionStrength: number
  particleSize: number
  morphSpeed: number
  voiceIntensity: number
  colorScheme: 'consciousness' | 'identity' | 'guardian' | 'custom'
}

export default function ProteusConfig({ isOpen, onClose }: ProteusConfigProps) {
  const [showKeys, setShowKeys] = useState<{ [key: string]: boolean }>({
    openai: false,
    anthropic: false,
    google: false,
    perplexity: false,
  })
  
  const [apiConfig, setApiConfig] = useState<ApiConfig>({
    openaiKey: '',
    anthropicKey: '',
    googleKey: '',
    perplexityKey: '',
    localEndpoint: 'http://localhost:11434',
  })
  
  const [visualConfig, setVisualConfig] = useState<VisualizationConfig>({
    particleCount: 1000,
    boundaryForce: 0.15,
    attractionStrength: 0.5,
    particleSize: 0.5,
    morphSpeed: 1.0,
    voiceIntensity: 0.5,
    colorScheme: 'consciousness',
  })
  
  const [saved, setSaved] = useState(false)
  const [testing, setTesting] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<{ [key: string]: 'connected' | 'disconnected' | 'testing' }>({})

  useEffect(() => {
    // Load saved configuration from localStorage
    const savedApiConfig = localStorage.getItem('proteus_api_config')
    const savedVisualConfig = localStorage.getItem('proteus_visual_config')
    
    if (savedApiConfig) {
      setApiConfig(JSON.parse(savedApiConfig))
    }
    if (savedVisualConfig) {
      setVisualConfig(JSON.parse(savedVisualConfig))
    }
  }, [])

  const handleSave = () => {
    // Save to localStorage
    localStorage.setItem('proteus_api_config', JSON.stringify(apiConfig))
    localStorage.setItem('proteus_visual_config', JSON.stringify(visualConfig))
    
    // Send configuration to iframe
    window.postMessage({
      type: 'updateConfiguration',
      apiConfig,
      visualConfig,
    }, '*')
    
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const testConnection = async (provider: string) => {
    setConnectionStatus({ ...connectionStatus, [provider]: 'testing' })
    
    // Simulate API testing
    setTimeout(() => {
      const hasKey = 
        (provider === 'openai' && apiConfig.openaiKey) ||
        (provider === 'anthropic' && apiConfig.anthropicKey) ||
        (provider === 'google' && apiConfig.googleKey) ||
        (provider === 'perplexity' && apiConfig.perplexityKey) ||
        (provider === 'local' && apiConfig.localEndpoint)
      
      setConnectionStatus({
        ...connectionStatus,
        [provider]: hasKey ? 'connected' : 'disconnected',
      })
    }, 1000)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      <div className="relative bg-gray-900 border border-white/10 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <h2 className="text-xl font-thin tracking-[0.2em]">PR0T3US Configuration</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Content */}
        <div className="px-6 py-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* API Configuration */}
          <section className="mb-8">
            <h3 className="text-lg font-light mb-4 text-blue-400">API Configuration</h3>
            
            <div className="space-y-4">
              {/* OpenAI */}
              <div>
                <label className="block text-sm uppercase tracking-wider mb-2">OpenAI API Key</label>
                <div className="flex space-x-2">
                  <div className="relative flex-1">
                    <input
                      type={showKeys.openai ? 'text' : 'password'}
                      value={apiConfig.openaiKey}
                      onChange={(e) => setApiConfig({ ...apiConfig, openaiKey: e.target.value })}
                      className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 pr-10 focus:border-blue-400 focus:outline-none transition"
                      placeholder="sk-..."
                    />
                    <button
                      onClick={() => setShowKeys({ ...showKeys, openai: !showKeys.openai })}
                      className="absolute right-3 top-3 text-gray-400 hover:text-white"
                    >
                      {showKeys.openai ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  <button
                    onClick={() => testConnection('openai')}
                    className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition"
                  >
                    {connectionStatus.openai === 'testing' ? (
                      <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                    ) : connectionStatus.openai === 'connected' ? (
                      <Check className="w-4 h-4 text-green-400" />
                    ) : connectionStatus.openai === 'disconnected' ? (
                      <AlertCircle className="w-4 h-4 text-red-400" />
                    ) : (
                      'Test'
                    )}
                  </button>
                </div>
              </div>
              
              {/* Anthropic */}
              <div>
                <label className="block text-sm uppercase tracking-wider mb-2">Anthropic API Key</label>
                <div className="flex space-x-2">
                  <div className="relative flex-1">
                    <input
                      type={showKeys.anthropic ? 'text' : 'password'}
                      value={apiConfig.anthropicKey}
                      onChange={(e) => setApiConfig({ ...apiConfig, anthropicKey: e.target.value })}
                      className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 pr-10 focus:border-blue-400 focus:outline-none transition"
                      placeholder="sk-ant-..."
                    />
                    <button
                      onClick={() => setShowKeys({ ...showKeys, anthropic: !showKeys.anthropic })}
                      className="absolute right-3 top-3 text-gray-400 hover:text-white"
                    >
                      {showKeys.anthropic ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  <button
                    onClick={() => testConnection('anthropic')}
                    className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition"
                  >
                    {connectionStatus.anthropic === 'testing' ? (
                      <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                    ) : connectionStatus.anthropic === 'connected' ? (
                      <Check className="w-4 h-4 text-green-400" />
                    ) : connectionStatus.anthropic === 'disconnected' ? (
                      <AlertCircle className="w-4 h-4 text-red-400" />
                    ) : (
                      'Test'
                    )}
                  </button>
                </div>
              </div>
              
              {/* Local Endpoint */}
              <div>
                <label className="block text-sm uppercase tracking-wider mb-2">Local Endpoint (Ollama)</label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={apiConfig.localEndpoint}
                    onChange={(e) => setApiConfig({ ...apiConfig, localEndpoint: e.target.value })}
                    className="flex-1 bg-black/50 border border-white/10 rounded-lg px-4 py-3 focus:border-blue-400 focus:outline-none transition"
                    placeholder="http://localhost:11434"
                  />
                  <button
                    onClick={() => testConnection('local')}
                    className="px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition"
                  >
                    {connectionStatus.local === 'testing' ? (
                      <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                    ) : connectionStatus.local === 'connected' ? (
                      <Check className="w-4 h-4 text-green-400" />
                    ) : connectionStatus.local === 'disconnected' ? (
                      <AlertCircle className="w-4 h-4 text-red-400" />
                    ) : (
                      'Test'
                    )}
                  </button>
                </div>
              </div>
            </div>
          </section>
          
          {/* Visualization Settings */}
          <section className="mb-8">
            <h3 className="text-lg font-light mb-4 text-purple-400">Visualization Settings</h3>
            
            <div className="space-y-4">
              {/* Particle Count */}
              <div>
                <label className="block text-sm uppercase tracking-wider mb-2">
                  Particle Count: <span className="text-blue-400">{visualConfig.particleCount}</span>
                </label>
                <input
                  type="range"
                  min="100"
                  max="5000"
                  step="100"
                  value={visualConfig.particleCount}
                  onChange={(e) => setVisualConfig({ ...visualConfig, particleCount: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              {/* Morph Speed */}
              <div>
                <label className="block text-sm uppercase tracking-wider mb-2">
                  Morph Speed: <span className="text-blue-400">{visualConfig.morphSpeed.toFixed(1)}</span>
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="3.0"
                  step="0.1"
                  value={visualConfig.morphSpeed}
                  onChange={(e) => setVisualConfig({ ...visualConfig, morphSpeed: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              {/* Voice Intensity */}
              <div>
                <label className="block text-sm uppercase tracking-wider mb-2">
                  Voice Intensity: <span className="text-blue-400">{visualConfig.voiceIntensity.toFixed(1)}</span>
                </label>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.1"
                  value={visualConfig.voiceIntensity}
                  onChange={(e) => setVisualConfig({ ...visualConfig, voiceIntensity: parseFloat(e.target.value) })}
                  className="w-full"
                />
              </div>
              
              {/* Color Scheme */}
              <div>
                <label className="block text-sm uppercase tracking-wider mb-2">Color Scheme</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {['consciousness', 'identity', 'guardian', 'custom'].map((scheme) => (
                    <button
                      key={scheme}
                      onClick={() => setVisualConfig({ ...visualConfig, colorScheme: scheme as any })}
                      className={`px-4 py-2 rounded-lg border transition ${
                        visualConfig.colorScheme === scheme
                          ? 'bg-gradient-to-r from-purple-600 to-blue-600 border-transparent'
                          : 'bg-white/10 border-white/10 hover:bg-white/20'
                      }`}
                    >
                      {scheme.charAt(0).toUpperCase() + scheme.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>
          
          {/* Advanced Settings */}
          <section>
            <details className="group">
              <summary className="text-lg font-light mb-4 text-gray-400 cursor-pointer hover:text-white transition">
                Advanced Settings
              </summary>
              
              <div className="space-y-4 mt-4">
                {/* Boundary Force */}
                <div>
                  <label className="block text-sm uppercase tracking-wider mb-2">
                    Boundary Force: <span className="text-blue-400">{visualConfig.boundaryForce.toFixed(2)}</span>
                  </label>
                  <input
                    type="range"
                    min="0.01"
                    max="0.5"
                    step="0.01"
                    value={visualConfig.boundaryForce}
                    onChange={(e) => setVisualConfig({ ...visualConfig, boundaryForce: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>
                
                {/* Attraction Strength */}
                <div>
                  <label className="block text-sm uppercase tracking-wider mb-2">
                    Attraction Strength: <span className="text-blue-400">{visualConfig.attractionStrength.toFixed(1)}</span>
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="2.0"
                    step="0.1"
                    value={visualConfig.attractionStrength}
                    onChange={(e) => setVisualConfig({ ...visualConfig, attractionStrength: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>
                
                {/* Particle Size */}
                <div>
                  <label className="block text-sm uppercase tracking-wider mb-2">
                    Particle Size: <span className="text-blue-400">{visualConfig.particleSize.toFixed(1)}</span>
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="2.0"
                    step="0.1"
                    value={visualConfig.particleSize}
                    onChange={(e) => setVisualConfig({ ...visualConfig, particleSize: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>
              </div>
            </details>
          </section>
        </div>
        
        {/* Footer */}
        <div className="px-6 py-4 border-t border-white/10 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-6 py-2 border border-white/20 rounded-lg hover:bg-white/10 transition"
          >
            Cancel
          </button>
          
          <button
            onClick={handleSave}
            className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:opacity-90 transition flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>{saved ? 'Saved!' : 'Save Configuration'}</span>
          </button>
        </div>
      </div>
    </div>
  )
}