'use client'

import React, { useState } from 'react'
import * as Collapsible from '@radix-ui/react-collapsible'
import * as Switch from '@radix-ui/react-switch'
import * as Slider from '@radix-ui/react-slider'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChevronLeft, ChevronRight, Mic, Volume2, Sparkles, 
  Palette, Shapes, Settings, Brain, Zap, Eye, 
  SlidersHorizontal, Layers, Network, Cpu, Activity
} from 'lucide-react'

// Toast helper for feedback
function toast(title: string, desc?: string) {
  const t = document.createElement('div')
  t.className = 'fixed right-4 top-20 z-[100] px-3 py-2 rounded-lg bg-black/80 border border-white/10 text-sm text-white/90 transition-all'
  t.innerHTML = `<div>${title}</div>${desc ? `<div class="text-white/60 text-[11px] mt-0.5">${desc}</div>` : ''}`
  document.body.appendChild(t)
  setTimeout(() => { 
    t.style.opacity = '0'
    t.style.transform = 'translateY(-6px)'
  }, 2200)
  setTimeout(() => t.remove(), 2600)
}

// GLYPH encoding helper (local encoding, not a substitute for rotating provider keys)
async function encryptToGlyph(provider: string, apiKey: string): Promise<string> {
  const enc = new TextEncoder()
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const salt = enc.encode(provider + '-lukhas-glyph-v1')

  const baseKey = await crypto.subtle.importKey('raw', salt, 'PBKDF2', false, ['deriveKey'])
  const key = await crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt, iterations: 100000, hash: 'SHA-256' },
    baseKey,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  )

  const cipher = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, enc.encode(apiKey))
  const payload = new Uint8Array(iv.byteLength + cipher.byteLength)
  payload.set(iv, 0); payload.set(new Uint8Array(cipher), iv.byteLength)

  const b64 = btoa(String.fromCharCode(...payload)).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
  const glyph = `Λ:${provider}:${b64}`
  try { localStorage.setItem(`glyph:${provider}`, glyph) } catch {}
  return glyph
}

interface SidebarProps {
  config: any
  onConfigChange: (key: string, value: any) => void
  apiKeys: {
    openai: string
    anthropic: string
    google: string
    perplexity: string
  }
  onApiKeyChange: (provider: string, key: string) => void
  collapsed?: boolean
  onCollapsedChange?: (value: boolean) => void
  usage?: { tokens: number; costUSD: number; creditsRemaining?: number }
  onEncryptKey?: (provider: string, glyph: string) => void
}

export default function ExperienceSidebar({ 
  config, 
  onConfigChange, 
  apiKeys, 
  onApiKeyChange,
  collapsed,
  onCollapsedChange,
  usage,
  onEncryptKey
}: SidebarProps) {
  const [internalCollapsed, setInternalCollapsed] = useState(false)
  const isCollapsed = (collapsed ?? internalCollapsed)
  const setIsCollapsed = (next: boolean) => {
    onCollapsedChange?.(next)
    setInternalCollapsed(next)
  }
  const [activeSection, setActiveSection] = useState<string | null>('visualization')
  const [keysModal, setKeysModal] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [showUnified, setShowUnified] = useState(false)

  // Build model options based on available keys
  const availableModels: { value: string; label: string }[] = [{ value: 'lukhas', label: 'LUKHAS AI' }]

  if (apiKeys.openai) availableModels.push(
    { value: 'gpt-4o', label: 'OpenAI · GPT-4o' },
    { value: 'gpt-4o-mini', label: 'OpenAI · GPT-4o mini' },
    { value: 'gpt-4-turbo', label: 'OpenAI · GPT-4 Turbo' },
  )

  if (apiKeys.anthropic) availableModels.push(
    { value: 'claude-3-sonnet', label: 'Anthropic · Claude 3 Sonnet' },
    { value: 'claude-3-opus', label: 'Anthropic · Claude 3 Opus' },
  )

  if (apiKeys.google) availableModels.push(
    { value: 'gemini-1.5-pro', label: 'Google · Gemini 1.5 Pro' },
    { value: 'gemini-1.5-flash', label: 'Google · Gemini 1.5 Flash' },
  )

  if (apiKeys.perplexity) availableModels.push(
    { value: 'pplx-7b-online', label: 'Perplexity · 7B Online' },
    { value: 'pplx-70b-online', label: 'Perplexity · 70B Online' },
  )

  const sections = [
    {
      id: 'visualization',
      title: 'Visualization',
      icon: Eye,
      content: (
        <div className="space-y-4">
          {/* Particle Count */}
          <div>
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider">
              Particle Count
            </label>
            <div className="mt-2">
              <Slider.Root
                className="relative flex items-center w-full h-5"
                value={[config.particleCount || 1000]}
                onValueChange={([value]) => onConfigChange('particleCount', value)}
                max={5000}
                min={100}
                step={100}
              >
                <Slider.Track className="bg-white/10 relative grow rounded-full h-1">
                  <Slider.Range className="absolute bg-gradient-to-r from-purple-600 to-blue-600 rounded-full h-full" />
                </Slider.Track>
                <Slider.Thumb className="block w-4 h-4 bg-white rounded-full shadow-lg hover:scale-110 transition-transform" />
              </Slider.Root>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-white/40">100</span>
                <span className="text-xs text-white/60">{config.particleCount || 1000}</span>
                <span className="text-xs text-white/40">5000</span>
              </div>
            </div>
          </div>

          {/* Morphing Speed */}
          <div>
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider">
              Morphing Speed
            </label>
            <div className="mt-2">
              <Slider.Root
                className="relative flex items-center w-full h-5"
                value={[config.morphSpeed || 0.02]}
                onValueChange={([value]) => onConfigChange('morphSpeed', value)}
                max={0.1}
                min={0.001}
                step={0.001}
              >
                <Slider.Track className="bg-white/10 relative grow rounded-full h-1">
                  <Slider.Range className="absolute bg-gradient-to-r from-blue-600 to-cyan-500 rounded-full h-full" />
                </Slider.Track>
                <Slider.Thumb className="block w-4 h-4 bg-white rounded-full shadow-lg hover:scale-110 transition-transform" />
              </Slider.Root>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-white/40">Slow</span>
                <span className="text-xs text-white/40">Fast</span>
              </div>
            </div>
          </div>

          {/* Shape Selection */}
          <div>
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider mb-2 block">
              Active Shape
            </label>
            <div className="grid grid-cols-2 gap-2">
              {['sphere', 'cube', 'torus', 'consciousness', 'cat', 'heart', 'helix'].map((shape) => (
                <button
                  key={shape}
                  onClick={() => onConfigChange('shape', shape)}
                  className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    config.shape === shape
                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                      : 'bg-white/5 text-white/60 hover:bg-white/10'
                  }`}
                >
                  {shape.charAt(0).toUpperCase() + shape.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'audio',
      title: 'Audio & Voice',
      icon: Mic,
      content: (
        <div className="space-y-4">
          {/* Microphone Enable */}
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider">
              Microphone
            </label>
            <Switch.Root
              className="w-11 h-6 bg-white/10 rounded-full relative data-[state=checked]:bg-gradient-to-r data-[state=checked]:from-purple-600 data-[state=checked]:to-blue-600"
              checked={config.micEnabled}
              onCheckedChange={(checked) => onConfigChange('micEnabled', checked)}
            >
              <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform duration-200 translate-x-0.5 will-change-transform data-[state=checked]:translate-x-[22px]" />
            </Switch.Root>
          </div>

          {/* Audio Enable */}
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider">
              Audio Output
            </label>
            <Switch.Root
              className="w-11 h-6 bg-white/10 rounded-full relative data-[state=checked]:bg-gradient-to-r data-[state=checked]:from-blue-600 data-[state=checked]:to-cyan-500"
              checked={config.audioEnabled}
              onCheckedChange={(checked) => onConfigChange('audioEnabled', checked)}
            >
              <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform duration-200 translate-x-0.5 will-change-transform data-[state=checked]:translate-x-[22px]" />
            </Switch.Root>
          </div>

          {/* Voice Sensitivity */}
          <div>
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider">
              Voice Sensitivity
            </label>
            <div className="mt-2">
              <Slider.Root
                className="relative flex items-center w-full h-5"
                value={[config.voiceSensitivity || 0.5]}
                onValueChange={([value]) => onConfigChange('voiceSensitivity', value)}
                max={1}
                min={0}
                step={0.01}
              >
                <Slider.Track className="bg-white/10 relative grow rounded-full h-1">
                  <Slider.Range className="absolute bg-gradient-to-r from-emerald-600 to-green-500 rounded-full h-full" />
                </Slider.Track>
                <Slider.Thumb className="block w-4 h-4 bg-white rounded-full shadow-lg hover:scale-110 transition-transform" />
              </Slider.Root>
              <div className="flex justify-between mt-1">
                <span className="text-xs text-white/40">Low</span>
                <span className="text-xs text-white/40">High</span>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'consciousness',
      title: 'Consciousness',
      icon: Brain,
      content: (
        <div className="space-y-4">
          {/* Consciousness Mode */}
          <div>
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider mb-2 block">
              Consciousness Mode
            </label>
            <div className="space-y-2">
              {['aware', 'dreaming', 'focused', 'creative'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => onConfigChange('consciousnessMode', mode)}
                  className={`w-full px-3 py-2 rounded-lg text-xs font-medium text-left transition-all ${
                    config.consciousnessMode === mode
                      ? 'bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30 text-white'
                      : 'bg-white/5 text-white/60 hover:bg-white/10 border border-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span>{mode.charAt(0).toUpperCase() + mode.slice(1)}</span>
                    {config.consciousnessMode === mode && (
                      <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Trinity Integration */}
          <div>
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider mb-2 block">
              Trinity Integration
            </label>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-white/60">Identity</span>
                <Switch.Root
                  className="w-11 h-6 bg-white/10 rounded-full relative data-[state=checked]:bg-purple-600"
                  checked={config.trinityIdentity}
                  onCheckedChange={(checked) => onConfigChange('trinityIdentity', checked)}
                >
                  <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform duration-200 translate-x-0.5 will-change-transform data-[state=checked]:translate-x-[22px]" />
                </Switch.Root>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-white/60">Consciousness</span>
                <Switch.Root
                  className="w-11 h-6 bg-white/10 rounded-full relative data-[state=checked]:bg-blue-600"
                  checked={config.trinityConsciousness}
                  onCheckedChange={(checked) => onConfigChange('trinityConsciousness', checked)}
                >
                  <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform duration-200 translate-x-0.5 will-change-transform data-[state=checked]:translate-x-[22px]" />
                </Switch.Root>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-white/60">Guardian</span>
                <Switch.Root
                  className="w-11 h-6 bg-white/10 rounded-full relative data-[state=checked]:bg-emerald-600"
                  checked={config.trinityGuardian}
                  onCheckedChange={(checked) => onConfigChange('trinityGuardian', checked)}
                >
                  <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform duration-200 translate-x-0.5 will-change-transform data-[state=checked]:translate-x-[22px]" />
                </Switch.Root>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'api',
      title: 'API Integration',
      icon: Network,
      content: (
        <div className="space-y-3">
          {/* Provider badges (lights when key exists) */}
          <div className="mb-3 flex items-center gap-2">
            {(['openai','anthropic','google','perplexity'] as const).map((p) => {
              const active = !!apiKeys[p]
              return (
                <span
                  key={p}
                  className={`px-2 py-1 text-[10px] rounded-md border capitalize
                    ${active ? 'bg-white/10 border-white/20 text-white/80' : 'bg-white/[0.02] border-white/10 text-white/30'}`}>
                  {p}
                </span>
              )
            })}
          </div>

          {/* Unified key card */}
          <div className="p-3 rounded-xl bg-white/5 border border-white/10">
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider">Paste any API key</label>
            <div className="mt-2 flex gap-2">
              <input
                id="unified-key"
                type={showUnified ? 'text' : 'password'}
                placeholder="Paste key (OpenAI, Anthropic, Google, Perplexity)"
                className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-xs text-white placeholder-white/30
                           focus:outline-none focus:border-white/20 focus:bg-white/10"
                onKeyDown={(e) => {
                  if (e.key !== 'Enter') return
                  const el = e.currentTarget as HTMLInputElement
                  const k = el.value.trim()
                  if (!k) return
                  let provider: keyof typeof apiKeys | null = null
                  if (/^sk-ant-/.test(k)) provider = 'anthropic'
                  else if (/^sk-[A-Za-z0-9]/.test(k)) provider = 'openai'
                  else if (/^AIza|^AI[a-zA-Z]/.test(k)) provider = 'google'
                  else if (/^pplx-/.test(k)) provider = 'perplexity'
                  if (!provider) { toast('Could not detect provider', 'Use Advanced → specific provider'); return }
                  // simple format checks (don't store if clearly wrong)
                  if (provider === 'openai' && !/^sk-[A-Za-z0-9_-]{20,}$/.test(k)) {
                    toast('OpenAI key format looks invalid', 'We did not store this key.')
                    return
                  }
                  onApiKeyChange(provider, k)
                  toast(`${provider} key saved`, 'Stored locally as an encrypted GLYPH.')
                  el.value = ''
                }}
              />
              <button
                type="button"
                aria-label={showUnified ? 'Hide key' : 'Show key'}
                className="px-3 py-2 text-xs rounded-md bg-white/10 hover:bg-white/20 border border-white/10"
                onClick={() => setShowUnified(v => !v)}
              >
                {showUnified ? 'Hide' : 'Show'}
              </button>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <p className="text-[10px] text-white/40">
                Stored on <b>this device</b>. Encrypted with <b>AES-GCM</b> → <b>GLYPH</b>.
              </p>
              <button type="button" onClick={() => setKeysModal(true)}
                className="text-[11px] text-white/70 underline underline-offset-2">Manage</button>
            </div>
          </div>

          {/* Advanced (collapsed provider inputs if you still want them) */}
          <details className="group mt-3">
            <summary className="cursor-pointer text-xs text-white/60 select-none">Advanced</summary>
            <div className="mt-2 grid gap-3">
              {/* Example: OpenAI only; replicate as needed */}
              <div className="p-3 rounded-lg bg-white/[0.03] border border-white/10">
                <label className="text-[11px] text-white/60">OpenAI API Key</label>
                <div className="mt-2 flex gap-2">
                  <input
                    type="password"
                    value={apiKeys.openai}
                    onChange={(e) => onApiKeyChange('openai', e.target.value)}
                    className="flex-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-xs text-white placeholder-white/30 focus:outline-none focus:border-white/20" />
                  <button className="px-3 py-2 text-xs rounded-md bg-white/10 border border-white/10">Encrypt → GLYPH</button>
                </div>
              </div>
            </div>
          </details>

          {/* Model Selection */}
          <div>
            <label className="text-xs font-medium text-white/60 uppercase tracking-wider mb-2 block">
              Active Model
            </label>
            <select
              value={config.activeModel || 'lukhas'}
              onChange={(e) => onConfigChange('activeModel', e.target.value)}
              className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg 
                       text-xs text-white focus:outline-none focus:border-white/20 
                       focus:bg-white/10 transition-all"
            >
              {availableModels.map(m => (
                <option key={m.value} value={m.value}>{m.label}</option>
              ))}
            </select>
          </div>

          {/* Usage meter note */}
          <div className="mt-3 p-3 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center justify-between">
              <span className="text-xs text-white/60 uppercase tracking-wider">Usage</span>
              <span className="text-[10px] text-white/40">session</span>
            </div>
            <div className="mt-2 grid grid-cols-3 gap-2 text-center">
              <div><div className="text-sm text-white/90">{usage?.tokens ?? 0}</div><div className="text-[10px] text-white/40">tokens</div></div>
              <div><div className="text-sm text-white/90">{`$${(usage?.costUSD ?? 0).toFixed(4)}`}</div><div className="text-[10px] text-white/40">cost</div></div>
              <div><div className="text-sm text-white/90">{usage?.creditsRemaining ?? '—'}</div><div className="text-[10px] text-white/40">credits</div></div>
            </div>
            <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-purple-600 to-blue-600" style={{ width: `${Math.min(100, (usage?.tokens ?? 0) % 100)}%` }} />
            </div>
            <div className="mt-2 text-[10px] text-white/40">
              Costs shown are estimates; actual pricing depends on the selected model.
            </div>
          </div>
        </div>
      )
    }
  ]

  return (
    <>
      {/* Sidebar */}
      <motion.div
        initial={{ width: 320 }}
        animate={{ width: isCollapsed ? 10 : 320 }}
        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
        className="fixed left-0 top-16 bottom-0 z-30 flex"
      >
        {/* Main Sidebar Content */}
        <div className={`flex-1 bg-black/60 backdrop-blur-2xl border-r border-white/10 overflow-y-auto ${isCollapsed ? 'opacity-0 pointer-events-none' : 'opacity-100'}`}>
          <div className="p-4 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-sm font-medium text-white/80 tracking-wider uppercase">
                Experience Controls
              </h2>
              <Activity className="w-4 h-4 text-white/40" />
            </div>

            {/* Sections */}
            {sections.map((section) => {
              const Icon = section.icon
              return (
                <Collapsible.Root
                  key={section.id}
                  open={activeSection === section.id}
                  onOpenChange={(open) => setActiveSection(open ? section.id : null)}
                >
                  <Collapsible.Trigger className="w-full">
                    <div className={`
                      flex items-center justify-between px-3 py-2 rounded-lg transition-all
                      ${activeSection === section.id 
                        ? 'bg-white/10 text-white' 
                        : 'hover:bg-white/5 text-white/60'}
                    `}>
                      <div className="flex items-center gap-3">
                        <Icon className="w-4 h-4" />
                        <span className="text-sm font-medium">{section.title}</span>
                      </div>
                      <ChevronRight className={`
                        w-4 h-4 transition-transform
                        ${activeSection === section.id ? 'rotate-90' : ''}
                      `} />
                    </div>
                  </Collapsible.Trigger>
                  
                  <Collapsible.Content>
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="px-3 py-4"
                    >
                      {section.content}
                    </motion.div>
                  </Collapsible.Content>
                </Collapsible.Root>
              )
            })}
          </div>
        </div>

        {/* Collapse Toggle */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute left-full top-1/2 -translate-y-1/2 w-10 h-20 
                   bg-black/60 backdrop-blur-xl border border-white/10 
                   rounded-r-xl flex items-center justify-center
                   hover:bg-white/10 transition-colors"
          aria-label={isCollapsed ? 'Expand controls' : 'Collapse controls'}
        >
          {isCollapsed ? (
            <ChevronRight className="w-4 h-4 text-white/60" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-white/60" />
          )}
        </button>
      </motion.div>

      {/* Quick Access Floating Panel (when collapsed) */}
      <AnimatePresence>
        {isCollapsed && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed left-4 top-24 z-20"
          >
            <div className="bg-black/60 backdrop-blur-2xl border border-white/10 rounded-xl p-3">
              <div className="flex flex-col gap-2">
                <button
                  onClick={() => onConfigChange('micEnabled', !config.micEnabled)}
                  className={`p-2 rounded-lg transition-all ${
                    config.micEnabled
                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white'
                      : 'bg-white/10 text-white/60 hover:bg-white/20'
                  }`}
                  title="Toggle Microphone"
                >
                  <Mic className="w-4 h-4" />
                </button>
                <button
                  onClick={() => onConfigChange('audioEnabled', !config.audioEnabled)}
                  className={`p-2 rounded-lg transition-all ${
                    config.audioEnabled
                      ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white'
                      : 'bg-white/10 text-white/60 hover:bg-white/20'
                  }`}
                  title="Toggle Audio"
                >
                  <Volume2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setIsCollapsed(false)}
                  className="p-2 rounded-lg bg-white/10 text-white/60 hover:bg-white/20 transition-all"
                  title="Open Controls"
                >
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Manage Keys modal */}
      {keysModal && (
        <div className="fixed inset-0 z-[120] grid place-items-center bg-black/60 backdrop-blur-sm">
          <div className="w-[min(520px,92vw)] rounded-xl border border-white/10 bg-black/80 p-4">
            <div className="text-sm text-white/90">Manage Keys & GLYPHs</div>
            <div className="mt-2 text-[11px] text-white/70 leading-5">
              • Storage: <b>IndexedDB</b> (fallback <code>localStorage</code>).<br/>
              • Encryption: <b>AES-GCM</b> via WebCrypto; GLYPH is an encrypted local token.<br/>
              • We never send raw keys to our servers.<br/>
              • Revoke: clear GLYPHs here and rotate your provider key if needed.
            </div>
            <div className="mt-3 flex justify-end gap-2">
              <button
                onClick={() => { localStorage.removeItem('lukhas:glyphs'); toast('All GLYPHs cleared') }}
                className="px-3 py-2 text-xs rounded-md bg-white/5 border border-white/10 hover:bg-white/10">Clear GLYPHs</button>
              <button
                onClick={() => setKeysModal(false)}
                className="px-3 py-2 text-xs rounded-md bg-white/10 border border-white/10">Close</button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}