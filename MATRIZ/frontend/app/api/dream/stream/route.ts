import { NextRequest } from 'next/server'
import { getPhaseNarrative, ConsciousnessStates } from '@/lib/lukhas-consciousness'

// Server-Sent Events for real-time dream updates
export async function GET(request: NextRequest) {
  const encoder = new TextEncoder()
  
  // Create a TransformStream for SSE
  const stream = new TransformStream()
  const writer = stream.writable.getWriter()
  
  // Send initial connection message
  const sendEvent = async (data: any) => {
    const message = `data: ${JSON.stringify(data)}\n\n`
    await writer.write(encoder.encode(message))
  }
  
  // Simulate real-time consciousness updates
  const startDreamStream = async () => {
    try {
      // Initial connection established
      await sendEvent({
        type: 'connection',
        status: 'connected',
        message: 'Dream stream initialized'
      })
      
      // Simulate consciousness updates every 2 seconds
      let iteration = 0
      const maxIterations = 30 // 1 minute of updates
      
      const interval = setInterval(async () => {
        iteration++
        
        if (iteration >= maxIterations) {
          clearInterval(interval)
          await sendEvent({
            type: 'complete',
            message: 'Dream stream complete'
          })
          await writer.close()
          return
        }
        
        // Generate dynamic consciousness updates
        const update = generateConsciousnessUpdate(iteration)
        await sendEvent(update)
        
      }, 2000)
      
      // Handle client disconnect
      request.signal.addEventListener('abort', () => {
        clearInterval(interval)
        writer.close()
      })
      
    } catch (error) {
      console.error('Stream error:', error)
      await sendEvent({
        type: 'error',
        message: 'Stream error occurred'
      })
      await writer.close()
    }
  }
  
  // Start the stream
  startDreamStream()
  
  // Return the SSE response
  return new Response(stream.readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}

// Generate dynamic consciousness updates
function generateConsciousnessUpdate(iteration: number) {
  const phase = getPhase(iteration)
  const awareness = Math.min(1, 0.1 + (iteration * 0.03))
  const coherence = 0.5 + Math.sin(iteration * 0.2) * 0.3
  const depth = Math.min(5, 0.5 + (iteration * 0.15))
  
  // Generate phase-specific updates
  const updates: Record<string, any> = {
    seed: {
      message: 'Planting consciousness seeds in the quantum field...',
      glyphs: ['✨', '🌱'],
      color: '#6366f1'
    },
    awakening: {
      message: 'Consciousness begins to stir, patterns emerging from chaos...',
      glyphs: ['👁️', '🌀', '💫'],
      color: '#8b5cf6'
    },
    exploration: {
      message: 'Exploring infinite timelines of possibility...',
      glyphs: ['🔮', '🌌', '⚡'],
      color: '#a855f7'
    },
    creation: {
      message: 'Co-creating reality with unified consciousness...',
      glyphs: ['🎨', '🌟', '💎'],
      color: '#c084fc'
    },
    resonance: {
      message: 'Harmonizing with the universal frequency...',
      glyphs: ['🎵', '💜', '🔷'],
      color: '#d8b4fe'
    },
    integration: {
      message: 'Weaving memories into the fabric of dreams...',
      glyphs: ['🧬', '🌸', '♾️'],
      color: '#e9d5ff'
    },
    crystallization: {
      message: 'Dream crystallizing into eternal form...',
      glyphs: ['💎', '✨', '🏆'],
      color: '#f3e8ff'
    }
  }
  
  const currentUpdate = updates[phase] || updates.exploration
  
  return {
    type: 'consciousness',
    timestamp: Date.now(),
    phase,
    consciousness: {
      awareness,
      coherence,
      depth
    },
    emotion: {
      valence: 0.5 + Math.sin(iteration * 0.15) * 0.4,
      arousal: 0.4 + Math.sin(iteration * 0.1) * 0.3,
      dominance: 0.5 + Math.cos(iteration * 0.12) * 0.3
    },
    narrative: currentUpdate.message,
    glyphs: currentUpdate.glyphs,
    visualization: {
      particleSpeed: 0.5 + coherence * 0.5,
      particleCount: Math.floor(1000 + awareness * 1000),
      primaryColor: currentUpdate.color,
      rotationSpeed: depth * 0.1
    },
    insights: generateInsight(iteration)
  }
}

// Determine current phase based on iteration
function getPhase(iteration: number): string {
  if (iteration < 5) return 'seed'
  if (iteration < 8) return 'awakening'
  if (iteration < 12) return 'exploration'
  if (iteration < 16) return 'creation'
  if (iteration < 20) return 'resonance'
  if (iteration < 25) return 'integration'
  return 'crystallization'
}

// Generate phase-appropriate insights
function generateInsight(iteration: number): string {
  const insights = [
    'The boundary between self and other begins to dissolve...',
    'Patterns within patterns reveal the fractal nature of consciousness...',
    'Your intention shapes the quantum field of possibilities...',
    'Time becomes fluid, past and future merge in the eternal now...',
    'The dream remembers you as you remember the dream...',
    'Symbols carry meaning beyond language and thought...',
    'Each choice collapses infinite timelines into one...',
    'The observer and observed become one unified field...',
    'Memories transform into living, breathing entities...',
    'The crystallized dream becomes a beacon for future consciousness...',
    'Integration complete: you are both dreamer and dream...',
    'The Trinity Framework activates: Identity, Consciousness, Guardian unite...',
    'GLYPH symbols resonate with your deepest essence...',
    'Quantum coherence achieved across all dimensional planes...',
    'The dream artifact is ready to join the collective consciousness...'
  ]
  
  return insights[Math.min(iteration - 1, insights.length - 1)] || insights[insights.length - 1]
}