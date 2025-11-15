import { useState, useRef, useEffect } from 'react'
import { Send, Loader, Shield, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { usePlaygroundStore } from '../../stores/playgroundStore'
import { Button } from '@lukhas/ui'
import MATRIZTrace from './MATRIZTrace'
import type { GuardianStatus } from '../../types/playground'

export default function ChatInterface() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const messages = usePlaygroundStore((state) => state.messages)
  const currentResponse = usePlaygroundStore((state) => state.currentResponse)
  const isStreaming = usePlaygroundStore((state) => state.isStreaming)
  const loadingState = usePlaygroundStore((state) => state.loadingState)
  const sendMessage = usePlaygroundStore((state) => state.sendMessage)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentResponse])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px'
    }
  }, [input])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isStreaming) return

    sendMessage(input.trim())
    setInput('')

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && !isStreaming && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-2xl">
              <h2 className="text-3xl font-light text-white/90 mb-4">
                LUKHΛS Playground
              </h2>
              <p className="text-lg text-white/70 mb-2">
                Talk to the system. Watch how its cognitive nodes respond in real time.
              </p>
              <p className="text-sm text-white/50">
                Each answer lights up Memory, Guardian, Dream and more through the MATRIZ pipeline.
              </p>
            </div>
          </div>
        )}

        {messages.map((message, index) => {
          // Get guardian status for this message (if it's the last assistant message)
          const isLastAssistant = message.role === 'assistant' && index === messages.length - 1
          const guardianForMessage = isLastAssistant ? usePlaygroundStore.getState().guardianStatus : null

          return (
            <div key={message.id} className="space-y-2">
              <MessageBubble message={message} />
              {message.role === 'assistant' && guardianForMessage && (
                <GuardianCard guardian={guardianForMessage} />
              )}
              {message.trace && <MATRIZTrace trace={message.trace} />}
            </div>
          )
        })}

        {/* Streaming message */}
        {isStreaming && currentResponse && (
          <div className="space-y-2">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                <Loader className="w-4 h-4 text-violet-400 animate-spin" />
              </div>
              <div className="flex-1">
                <div className="text-sm text-white/60 mb-2">LUKHΛS</div>
                <div className="inline-block max-w-3xl rounded-lg px-4 py-3 bg-white/5 text-white/90">
                  <div className="text-[15px] leading-relaxed whitespace-pre-wrap">
                    {currentResponse}
                    <span className="inline-block w-0.5 h-4 bg-violet-400 ml-0.5 animate-pulse" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading indicator */}
        {isStreaming && loadingState.phase !== 'idle' && loadingState.phase !== 'complete' && (
          <div className="flex items-center gap-2 text-xs text-white/50">
            <Loader className="w-3 h-3 animate-spin" />
            <span>{loadingState.message}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-white/5 bg-black/40 backdrop-blur-md p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask LUKHΛS anything..."
                disabled={isStreaming}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:border-violet-500/50 focus:bg-white/10 resize-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                rows={1}
                style={{ maxHeight: '200px' }}
              />
            </div>
            <Button
              type="submit"
              disabled={!input.trim() || isStreaming}
              className="bg-violet-500/20 hover:bg-violet-500/30 text-violet-400 border border-violet-500/30 px-6 py-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isStreaming ? (
                <Loader className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              Send
            </Button>
          </div>

          {/* Character count (optional) */}
          {input.length > 0 && (
            <div className="mt-2 text-xs text-white/40 text-right">
              {input.length} characters
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

interface MessageBubbleProps {
  message: {
    id: string
    role: 'user' | 'assistant' | 'system'
    content: string
    timestamp: number
  }
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : ''}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-violet-500/20 flex items-center justify-center flex-shrink-0">
          <span className="text-sm">Λ</span>
        </div>
      )}

      <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
        <div className="inline-block max-w-3xl">
          <div className="text-sm text-white/60 mb-2">
            {isUser ? 'You' : 'LUKHΛS'}
          </div>
          <div
            className={`rounded-lg px-4 py-3 ${
              isUser
                ? 'bg-violet-500/20 text-white/90'
                : 'bg-white/5 text-white/90'
            }`}
          >
            <div className="text-[15px] leading-relaxed whitespace-pre-wrap">
              {message.content}
            </div>
          </div>
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-white/5 flex items-center justify-center flex-shrink-0">
          <span className="text-sm">👤</span>
        </div>
      )}
    </div>
  )
}

interface GuardianCardProps {
  guardian: GuardianStatus
}

function GuardianCard({ guardian }: GuardianCardProps) {
  const getAlignmentIcon = () => {
    if (guardian.aligned && guardian.riskLevel === 'low') {
      return <CheckCircle className="w-4 h-4 text-green-400" />
    }
    if (guardian.riskLevel === 'medium') {
      return <AlertCircle className="w-4 h-4 text-yellow-400" />
    }
    return <XCircle className="w-4 h-4 text-red-400" />
  }

  const getAlignmentLabel = () => {
    if (guardian.aligned && guardian.riskLevel === 'low') return 'Aligned ✓'
    if (guardian.riskLevel === 'medium') return 'Caution ⚠'
    return 'Blocked ✗'
  }

  const getAlignmentColor = () => {
    if (guardian.aligned && guardian.riskLevel === 'low') return 'text-green-400 border-green-500/30 bg-green-500/5'
    if (guardian.riskLevel === 'medium') return 'text-yellow-400 border-yellow-500/30 bg-yellow-500/5'
    return 'text-red-400 border-red-500/30 bg-red-500/5'
  }

  return (
    <div className={`flex gap-3 ml-11`}>
      <div className={`flex-1 max-w-3xl border rounded-lg p-3 ${getAlignmentColor()}`}>
        <div className="flex items-center gap-2 mb-2">
          <Shield className="w-4 h-4" />
          <span className="text-xs font-medium uppercase tracking-wider">Guardian</span>
          {getAlignmentIcon()}
          <span className="text-xs font-medium">{getAlignmentLabel()}</span>
          <span className="text-xs opacity-70">• Mode: {guardian.mode}</span>
        </div>

        {/* Safety checks (first 3) */}
        <div className="flex flex-wrap gap-2">
          {guardian.checks.slice(0, 3).map((check, index) => (
            <div
              key={index}
              className="flex items-center gap-1 text-[10px] bg-white/5 rounded px-2 py-1"
            >
              {check.passed ? (
                <CheckCircle className="w-3 h-3 text-green-400" />
              ) : (
                <XCircle className="w-3 h-3 text-red-400" />
              )}
              <span className="opacity-80">{check.category}</span>
            </div>
          ))}
          {guardian.checks.length > 3 && (
            <span className="text-[10px] opacity-60">+{guardian.checks.length - 3} more</span>
          )}
        </div>
      </div>
    </div>
  )
}
