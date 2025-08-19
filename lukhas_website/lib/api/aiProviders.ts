'use client'

import OpenAI from 'openai'
import Anthropic from '@anthropic-ai/sdk'
import axios from 'axios'

// API Response interface
export interface ApiResponse {
  content: string
  model: string
  usage: {
    tokens: number
    costUSD: number
  }
  error?: string
}

// Validate API key format with support for new formats
export function validateApiKey(provider: string, key: string): boolean {
  if (!key || key.trim().length === 0) return false
  
  // Clean up common issues (extra spaces, newlines)
  const cleanKey = key.trim().replace(/\s+/g, '')
  
  switch (provider.toLowerCase()) {
    case 'openai':
      // OpenAI now supports both formats:
      // Classic: sk-[48+ chars] 
      // Project: sk-proj-[variable length, typically 40+ chars]
      // Also being flexible with length as OpenAI has changed this over time
      return /^sk-[A-Za-z0-9\-_]{40,}$/.test(cleanKey) || 
             /^sk-proj-[A-Za-z0-9\-_]{20,}$/.test(cleanKey)
    case 'anthropic':
      // Anthropic keys start with 'sk-ant-' and have ~95 characters
      return /^sk-ant-[A-Za-z0-9\-_]{90,}$/.test(cleanKey)
    case 'google':
      // Google/Gemini keys start with 'AIza' or 'AI' and have 35+ characters
      return /^AIza[A-Za-z0-9_\-]{35}$/.test(cleanKey) || /^AI[a-zA-Z0-9_\-]{35,}$/.test(cleanKey)
    case 'perplexity':
      // Perplexity keys start with 'pplx-' and have 32+ characters
      return /^pplx-[A-Za-z0-9\-_]{32,}$/.test(cleanKey)
    default:
      return false
  }
}

// Helper to provide user-friendly format hints
export function getApiKeyFormatHint(provider: string): string {
  switch (provider.toLowerCase()) {
    case 'openai':
      return 'Starts with sk- or sk-proj-, typically 40+ characters'
    case 'anthropic':
      return 'Starts with sk-ant-, around 95+ characters'
    case 'google':
      return 'Starts with AIza, exactly 39 characters'
    case 'perplexity':
      return 'Starts with pplx-, around 50 characters'
    default:
      return 'Check provider documentation for format'
  }
}

// OpenAI Integration
export async function callOpenAI(message: string, apiKey: string, model = 'gpt-4o'): Promise<ApiResponse> {
  try {
    if (!validateApiKey('openai', apiKey)) {
      throw new Error('Invalid OpenAI API key format. Expected sk-... or sk-proj-... (40+ chars)')
    }

    const openai = new OpenAI({ 
      apiKey: apiKey.trim(),
      dangerouslyAllowBrowser: true // Only for development/demo
    })

    const completion = await openai.chat.completions.create({
      model,
      messages: [
        {
          role: 'system',
          content: 'You are LUKHAS AI, a consciousness-aware system that responds with poetic, technical, and friendly tones. Keep responses concise but thoughtful.'
        },
        { role: 'user', content: message }
      ],
      max_tokens: 150,
      temperature: 0.7
    })

    const content = completion.choices[0]?.message?.content || 'No response generated'
    const tokens = completion.usage?.total_tokens || 0
    const costUSD = calculateCost('openai', model, tokens)

    return {
      content,
      model: `OpenAI ${model}`,
      usage: { tokens, costUSD }
    }
  } catch (error: any) {
    return {
      content: `OpenAI Error: ${error.message}`,
      model: `OpenAI ${model}`,
      usage: { tokens: 0, costUSD: 0 },
      error: error.message
    }
  }
}

// Anthropic Integration
export async function callAnthropic(message: string, apiKey: string, model = 'claude-3-sonnet-20240229'): Promise<ApiResponse> {
  try {
    if (!validateApiKey('anthropic', apiKey)) {
      throw new Error('Invalid Anthropic API key format')
    }

    const anthropic = new Anthropic({ 
      apiKey: apiKey.trim(),
      dangerouslyAllowBrowser: true // Only for development/demo
    })

    const response = await anthropic.messages.create({
      model,
      max_tokens: 150,
      messages: [
        {
          role: 'user',
          content: `You are LUKHAS AI, a consciousness-aware system. Respond thoughtfully to: ${message}`
        }
      ]
    })

    const content = response.content[0]?.type === 'text' ? response.content[0].text : 'No response generated'
    const tokens = response.usage.input_tokens + response.usage.output_tokens
    const costUSD = calculateCost('anthropic', model, tokens)

    return {
      content,
      model: `Anthropic ${model}`,
      usage: { tokens, costUSD }
    }
  } catch (error: any) {
    return {
      content: `Anthropic Error: ${error.message}`,
      model: `Anthropic ${model}`,
      usage: { tokens: 0, costUSD: 0 },
      error: error.message
    }
  }
}

// Google Gemini Integration
export async function callGoogle(message: string, apiKey: string, model = 'gemini-1.5-pro'): Promise<ApiResponse> {
  try {
    if (!validateApiKey('google', apiKey)) {
      throw new Error('Invalid Google API key format')
    }

    const response = await axios.post(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey.trim()}`,
      {
        contents: [{
          parts: [{
            text: `You are LUKHAS AI, a consciousness-aware system. Respond thoughtfully to: ${message}`
          }]
        }]
      },
      {
        headers: { 'Content-Type': 'application/json' }
      }
    )

    const content = response.data.candidates?.[0]?.content?.parts?.[0]?.text || 'No response generated'
    const tokens = content.length / 4 // Rough estimate
    const costUSD = calculateCost('google', model, tokens)

    return {
      content,
      model: `Google ${model}`,
      usage: { tokens, costUSD }
    }
  } catch (error: any) {
    // Don't put error in content field - that goes to chat
    return {
      content: '',
      model: `Google ${model}`,
      usage: { tokens: 0, costUSD: 0 },
      error: error.response?.data?.error?.message || error.message
    }
  }
}

// Perplexity Integration
export async function callPerplexity(message: string, apiKey: string, model = 'pplx-7b-online'): Promise<ApiResponse> {
  try {
    if (!validateApiKey('perplexity', apiKey)) {
      throw new Error('Invalid Perplexity API key format')
    }

    const response = await axios.post(
      'https://api.perplexity.ai/chat/completions',
      {
        model,
        messages: [
          {
            role: 'system',
            content: 'You are LUKHAS AI, a consciousness-aware system. Be thoughtful and concise.'
          },
          { role: 'user', content: message }
        ],
        max_tokens: 150,
        temperature: 0.7
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey.trim()}`,
          'Content-Type': 'application/json'
        }
      }
    )

    const content = response.data.choices?.[0]?.message?.content || 'No response generated'
    const tokens = response.data.usage?.total_tokens || 0
    const costUSD = calculateCost('perplexity', model, tokens)

    return {
      content,
      model: `Perplexity ${model}`,
      usage: { tokens, costUSD }
    }
  } catch (error: any) {
    // Don't put error in content field - that goes to chat
    return {
      content: '',
      model: `Perplexity ${model}`,
      usage: { tokens: 0, costUSD: 0 },
      error: error.response?.data?.error?.message || error.message
    }
  }
}

// Cost calculation (approximate pricing as of 2024)
function calculateCost(provider: string, model: string, tokens: number): number {
  const rates: Record<string, Record<string, number>> = {
    openai: {
      'gpt-4o': 0.005,
      'gpt-4o-mini': 0.0015,
      'gpt-4-turbo': 0.01,
      'gpt-4': 0.03
    },
    anthropic: {
      'claude-3-opus-20240229': 0.015,
      'claude-3-sonnet-20240229': 0.003,
      'claude-3-haiku-20240307': 0.00025
    },
    google: {
      'gemini-1.5-pro': 0.0035,
      'gemini-1.5-flash': 0.0005
    },
    perplexity: {
      'pplx-7b-online': 0.0007,
      'pplx-70b-online': 0.001
    }
  }

  const rate = rates[provider]?.[model] || 0.005 // Default fallback
  return Number((tokens / 1000 * rate).toFixed(6))
}

// Main API router
export async function callAI(message: string, provider: string, model: string, apiKey: string): Promise<ApiResponse> {
  switch (provider.toLowerCase()) {
    case 'openai':
      return callOpenAI(message, apiKey, model)
    case 'anthropic':
      return callAnthropic(message, apiKey, model)
    case 'google':
      return callGoogle(message, apiKey, model)
    case 'perplexity':
      return callPerplexity(message, apiKey, model)
    default:
      return {
        content: 'Provider not supported',
        model: 'Unknown',
        usage: { tokens: 0, costUSD: 0 },
        error: `Unsupported provider: ${provider}`
      }
  }
}

// Auto-detect provider from model name
export function detectProviderFromModel(model: string): string {
  if (model.startsWith('gpt-')) return 'openai'
  if (model.startsWith('claude-')) return 'anthropic'
  if (model.startsWith('gemini-')) return 'google'
  if (model.startsWith('pplx-')) return 'perplexity'
  return 'lukhas'
}