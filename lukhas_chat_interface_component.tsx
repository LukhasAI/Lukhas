'use client'

import React, { useState, useRef, useEffect } from 'react'
import TextareaAutosize from 'react-textarea-autosize'
import { Send, Paperclip, Sparkles, Bot, User, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

// Three-layer tone system from Plan1
function threeLayerTone(base: string, hint?: string) {
  const poetic = `${base}`
  const friendly = hint ? `${hint}` : 'Say the word — I\'ll shape the field to match.'
  const academic = 'Legibility and convergence are prioritized; complex silhouettes are approximated before true assets are added.'
  return `• Poetic: ${poetic}\n• Friendly: ${friendly}\n• Insight: ${academic}`
}

function generateLocalReply(txt: string): string {
  const t = txt.toLowerCase()
  // Known shapes
  if (t.match(/\btorus|donut\b/)) return threeLayerTone('A ring awakens; particles settle into an endless loop.', 'Switching to a torus now.')
  if (t.match(/\bcube|box\b/)) return threeLayerTone('Structure condenses into six quiet planes.', 'Forming a cube.')
  if (t.match(/\bsphere|orb|ball\b/)) return threeLayerTone('Symmetry blooms into a calm orb.', 'Centering into a sphere.')
  if (t.match(/\bhelix|spiral\b/)) return threeLayerTone('A spiral climbs; pitch matches your intent.', 'Evolving into a spiral.')
  if (t.match(/\bheart\b/)) return threeLayerTone('Warmth collects into a soft heartfield.', 'Shaping into a heart-like flow.')
  // Text
  if (t.match(/"([^"]+)"/) || t.includes('text:')) return threeLayerTone('Your words crystallize as a glyph.', 'Rendering your text and holding for legibility.')
  // Honest fallback for unknown shapes
  const asksShape = /\b(make|turn|render|form|shape)\b/.test(t)
  const mentionsNoun = /\b([a-z]{3,})\b/.test(t)
  const known = /(torus|donut|cube|box|sphere|orb|ball|helix|spiral|heart|conscious)/
  if (asksShape && mentionsNoun && !known.test(t)) {
    return threeLayerTone('I don\'t have that silhouette yet.', 'Shall I render the word as a glyph first, or would you like a simple approximation?')
  }
  // General personality
  return threeLayerTone('Understood. The field is listening.', 'Ask for a shape or say a word in quotes to see it drawn in particles.')
}

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  model?: string
}

interface ChatInterfaceProps {
  onSendMessage?: (message: string) => void
  selectedModel?: string
  isProcessing?: boolean
  onTyping?: () => void
  onMessage?: (message: Message) => void
  showInlineHistory?: boolean
}

export default function ChatInterface({ 
  onSendMessage, 
  selectedModel = 'LUKHAS',
  isProcessing = false,
  onTyping,
  onMessage,
  showInlineHistory = true
}: ChatInterfaceProps) {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault()
    
    if (!input.trim() || isProcessing) return

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      content: input.trim(),
      role: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    // Send message to parent component
    onSendMessage?.(input.trim())
    onMessage?.(userMessage)

    // Simulate response (in real app, this would come from API)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        content: generateLocalReply(input.trim()),
        role: 'assistant',
        timestamp: new Date(),
        model: selectedModel
      }
      setMessages(prev => [...prev, assistantMessage])
      setIsTyping(false)
      onMessage?.(assistantMessage)
    }, 2000)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const clearMessages = () => {
    setMessages([])
  }

  return (
    <>
      {/* Message History Overlay */}
      {showInlineHistory && (
        <AnimatePresence>
          {messages.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-24 left-4 right-4 md:left-auto md:right-8 md:w-[500px] max-h-[400px] overflow-y-auto 
                     bg-black/80 backdrop-blur-2xl border border-white/10 rounded-2xl p-4 z-40"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-white/60 tracking-wider uppercase">
                Conversation History
              </h3>
              <button
                onClick={clearMessages}
                className="p-1 rounded-lg hover:bg-white/10 transition-colors"
                title="Clear messages"
              >
                <X className="w-4 h-4 text-white/40" />
              </button>
            </div>
            
            <div className="space-y-3">
              {messages.map(message => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, x: message.role === 'user' ? 20 : -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex gap-3 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center
                                  ${message.role === 'user' 
                                    ? 'bg-gradient-to-br from-purple-600 to-blue-600' 
                                    : 'bg-gradient-to-br from-blue-600 to-cyan-500'}`}>
                      {message.role === 'user' ? (
                        <User className="w-4 h-4 text-white" />
                      ) : (
                        <Bot className="w-4 h-4 text-white" />
                      )}
                    </div>
                    
                    <div className={`px-4 py-2 rounded-2xl ${
                      message.role === 'user' 
                        ? 'bg-gradient-to-r from-purple-600/20 to-blue-600/20 border border-purple-500/30' 
                        : 'bg-white/5 border border-white/10'
                    }`}>
                      <p className="text-sm text-white/90 leading-relaxed">
                        {message.content}
                      </p>
                      {message.model && (
                        <p className="text-xs text-white/40 mt-1">
                          {message.model} • {message.timestamp.toLocaleTimeString()}
                        </p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-3"
                >
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-500 
                                flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="px-4 py-2 rounded-2xl bg-white/5 border border-white/10">
                    <div className="flex gap-1">
                      <motion.div
                        animate={{ opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="w-2 h-2 bg-white/60 rounded-full"
                      />
                      <motion.div
                        animate={{ opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                        className="w-2 h-2 bg-white/60 rounded-full"
                      />
                      <motion.div
                        animate={{ opacity: [0.4, 1, 0.4] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                        className="w-2 h-2 bg-white/60 rounded-full"
                      />
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
            
            <div ref={messagesEndRef} />
          </motion.div>
        )}
        </AnimatePresence>
      )}

      {/* Chat Input Bar */}
      <div className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-gradient-to-t from-black via-black/95 to-transparent">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            <div className="flex items-end gap-2 bg-black/60 backdrop-blur-2xl border border-white/10 
                          rounded-2xl px-4 py-3 shadow-2xl">
              {/* Attachment Button */}
              <button
                type="button"
                className="p-2 rounded-lg hover:bg-white/10 transition-colors mb-1"
                title="Attach file (coming soon)"
                disabled
              >
                <Paperclip className="w-5 h-5 text-white/40" />
              </button>

              {/* Text Input */}
              <div className="flex-1 relative">
                <TextareaAutosize
                  ref={inputRef}
                  value={input}
                  onChange={(e) => { setInput(e.target.value); onTyping?.() }}
                  onKeyDown={handleKeyDown}
                  placeholder={`Message ${selectedModel}...`}
                  className="w-full bg-transparent text-white placeholder-white/40 resize-none 
                           focus:outline-none leading-relaxed max-h-32"
                  maxRows={4}
                  disabled={isProcessing}
                />
                
                {/* Character Count */}
                <div className="absolute right-0 bottom-0 text-xs text-white/30">
                  {input.length > 0 && `${input.length}/4000`}
                </div>
              </div>

              {/* Send Button */}
              <button
                type="submit"
                disabled={!input.trim() || isProcessing}
                className={`p-2 rounded-lg transition-all mb-1 ${
                  input.trim() && !isProcessing
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-lg hover:shadow-purple-500/20' 
                    : 'bg-white/10 text-white/30 cursor-not-allowed'
                }`}
                title="Send message"
              >
                {isProcessing ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  >
                    <Sparkles className="w-5 h-5" />
                  </motion.div>
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>

            {/* Model Indicator */}
            <div className="absolute -top-8 left-4 flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-3 py-1 bg-black/60 backdrop-blur-xl 
                            border border-white/10 rounded-full">
                <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full animate-pulse" />
                <span className="text-xs text-white/60 font-medium tracking-wider uppercase">
                  {selectedModel} Active
                </span>
              </div>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}