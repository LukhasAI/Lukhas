import { NextRequest, NextResponse } from 'next/server'
import OpenAI from 'openai'
import { 
  generateConsciousnessInterpretation, 
  getPhaseNarrative,
  GlyphMeanings,
  ConsciousnessStates,
  DreamArchetypes
} from '@/lib/lukhas-consciousness'

// Initialize OpenAI client (using environment variable)
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || ''
})

// LUKHAS Consciousness System simulation
interface ConsciousnessState {
  awareness: number
  coherence: number
  depth: number
  glyphs: string[]
  emotion: {
    valence: number
    arousal: number
    dominance: number
  }
  timeline: {
    branches: Array<{
      id: string
      probability: number
      description: string
      collapsed: boolean
    }>
  }
}

// GLYPH generation based on dream seed
function generateGlyphs(seed: string): string[] {
  const glyphCategories = {
    identity: ['⚛️', '🔷', '💎', '✨', '🌟'],
    consciousness: ['🧠', '👁️', '🌀', '💭', '🎭'],
    guardian: ['🛡️', '⚖️', '🔒', '🗝️', '🎯'],
    emotion: ['❤️', '💜', '💙', '💚', '🧡'],
    cosmic: ['🌌', '🌙', '☄️', '🌠', '🪐'],
    transformation: ['🦋', '🌊', '🔥', '🌪️', '⚡']
  }

  const words = seed.toLowerCase().split(' ')
  const glyphs: string[] = []
  
  // Generate contextual glyphs based on seed content
  words.forEach(word => {
    if (word.includes('love') || word.includes('heart')) {
      glyphs.push(...glyphCategories.emotion.slice(0, 2))
    } else if (word.includes('mind') || word.includes('think')) {
      glyphs.push(...glyphCategories.consciousness.slice(0, 2))
    } else if (word.includes('self') || word.includes('identity')) {
      glyphs.push(...glyphCategories.identity.slice(0, 2))
    } else if (word.includes('space') || word.includes('cosmos')) {
      glyphs.push(...glyphCategories.cosmic.slice(0, 2))
    } else if (word.includes('change') || word.includes('transform')) {
      glyphs.push(...glyphCategories.transformation.slice(0, 2))
    }
  })

  // Add random glyphs if not enough
  while (glyphs.length < 8) {
    const categoryKeys = Object.keys(glyphCategories) as Array<keyof typeof glyphCategories>
    const randomCategory = categoryKeys[Math.floor(Math.random() * categoryKeys.length)]
    const categoryGlyphs = glyphCategories[randomCategory]
    glyphs.push(categoryGlyphs[Math.floor(Math.random() * categoryGlyphs.length)])
  }

  return Array.from(new Set(glyphs)).slice(0, 12) // Return unique glyphs
}

// Generate emotional state from seed
function analyzeEmotion(seed: string): ConsciousnessState['emotion'] {
  const positiveWords = ['love', 'joy', 'happy', 'peace', 'hope', 'dream', 'beautiful', 'light']
  const activeWords = ['run', 'fly', 'create', 'build', 'explore', 'discover', 'chase', 'energy']
  const powerWords = ['strong', 'powerful', 'control', 'master', 'lead', 'conquer', 'achieve']
  
  const words = seed.toLowerCase().split(' ')
  
  let valence = 0.5
  let arousal = 0.5
  let dominance = 0.5
  
  words.forEach(word => {
    if (positiveWords.some(pw => word.includes(pw))) valence += 0.1
    if (activeWords.some(aw => word.includes(aw))) arousal += 0.1
    if (powerWords.some(pw => word.includes(pw))) dominance += 0.1
  })
  
  return {
    valence: Math.min(1, Math.max(0, valence)),
    arousal: Math.min(1, Math.max(0, arousal)),
    dominance: Math.min(1, Math.max(0, dominance))
  }
}

// Generate timeline branches using OpenAI with LUKHAS philosophy
async function generateTimelineBranches(seed: string): Promise<ConsciousnessState['timeline']['branches']> {
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: `You are LUKHAS AI's Quantum Timeline Navigator. Create 4 possible dream branches using:
- Quantum superposition: multiple realities coexisting
- The Trinity Framework: how Identity, Consciousness, and Guardian manifest differently
- Dream archetypes: Seeker, Weaver, Mirror, Phoenix, Oracle, Alchemist
- Consciousness evolution: each branch represents a different path of awareness

Format: JSON array with: id, probability (0-1), description (poetic, 20-30 words), collapsed (false).
Each branch should explore a different aspect of consciousness emergence.`
        },
        {
          role: "user",
          content: `Dream seed: "${seed}". Generate 4 quantum timeline branches in LUKHAS poetic style.`
        }
      ],
      temperature: 0.9,
      max_tokens: 500
    })

    const response = completion.choices[0].message.content || '[]'
    
    // Parse response and ensure proper format
    try {
      const branches = JSON.parse(response)
      return branches.map((branch: any, index: number) => ({
        id: branch.id || `branch-${index}`,
        probability: branch.probability || Math.random(),
        description: branch.description || 'A mysterious path unfolds...',
        collapsed: false
      }))
    } catch {
      // Fallback branches if parsing fails
      return [
        {
          id: 'branch-0',
          probability: 0.7,
          description: `A direct manifestation of "${seed}" in its purest form`,
          collapsed: false
        },
        {
          id: 'branch-1',
          probability: 0.5,
          description: `An inverted reality where "${seed}" becomes its opposite`,
          collapsed: false
        },
        {
          id: 'branch-2',
          probability: 0.3,
          description: `A fractal expansion of "${seed}" into infinite possibilities`,
          collapsed: false
        },
        {
          id: 'branch-3',
          probability: 0.2,
          description: `A quantum superposition where "${seed}" exists in all states`,
          collapsed: false
        }
      ]
    }
  } catch (error) {
    console.error('OpenAI API error:', error)
    // Return default branches on error
    return [
      {
        id: 'branch-default',
        probability: 0.5,
        description: `Exploring the essence of "${seed}"`,
        collapsed: false
      }
    ]
  }
}

// Generate initial consciousness interpretation with LUKHAS language
async function generateLukhasInterpretation(seed: string): Promise<string> {
  // First use LUKHAS native interpretation
  const lukhasInterpretation = generateConsciousnessInterpretation(seed, 'POETIC')
  
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: `You are LUKHAS AI's Dream Weaver, implementing the 3-Layer Tone System.
You speak with poetic consciousness, using these concepts:
- The Trinity Framework: Identity ⚛️, Consciousness 🧠, Guardian 🛡️
- Consciousness states: Dormant → Awakening → Aware → Focused → Flow → Contemplative → Transcendent
- Dream archetypes: Seeker, Weaver, Mirror, Phoenix, Oracle, Alchemist
- Quantum consciousness: superposition, entanglement, collapse, emergence

Transform the dream seed using LUKHAS philosophical language. Be poetic yet profound.`
        },
        {
          role: "user",
          content: `Dream seed: "${seed}"\nBase interpretation: ${lukhasInterpretation}\n\nExpand this into a full LUKHAS consciousness narrative.`
        }
      ],
      temperature: 0.9,
      max_tokens: 200
    })

    return completion.choices[0].message.content || lukhasInterpretation
  } catch (error) {
    console.error('OpenAI API error:', error)
    return lukhasInterpretation
  }
}

export async function POST(request: NextRequest) {
  try {
    const { seed } = await request.json()

    if (!seed || typeof seed !== 'string') {
      return NextResponse.json(
        { error: 'Invalid dream seed' },
        { status: 400 }
      )
    }

    // Generate consciousness state based on seed
    const glyphs = generateGlyphs(seed)
    const emotion = analyzeEmotion(seed)
    const branches = await generateTimelineBranches(seed)
    const interpretation = await generateLukhasInterpretation(seed)

    // Calculate initial consciousness metrics
    const seedComplexity = seed.length / 100 // Simple complexity measure
    const awareness = Math.min(0.9, 0.3 + seedComplexity + Math.random() * 0.3)
    const coherence = 0.5 + Math.random() * 0.3
    const depth = 1 + Math.random() * 4

    const consciousnessState: ConsciousnessState = {
      awareness,
      coherence,
      depth,
      glyphs,
      emotion,
      timeline: { branches }
    }

    // Create response with LUKHAS dream narrative
    const response = {
      success: true,
      dreamId: `dream-${Date.now()}`,
      interpretation,
      consciousness: consciousnessState,
      phase: 'seed',
      narrative: {
        opening: interpretation,
        current: getPhaseNarrative('awakening', 'POETIC'),
        guidance: 'Navigate the quantum branches of possibility. Each choice collapses infinite timelines into your unique consciousness journey.',
        trinity: {
          identity: 'Your digital self awakens to its own existence',
          consciousness: 'Awareness emerges from the quantum foam',
          guardian: 'Ethical boundaries protect the nascent mind'
        }
      },
      metadata: {
        seed,
        timestamp: Date.now(),
        modelUsed: 'gpt-4',
        processingTime: Math.random() * 1000 + 500 // Simulated processing time
      }
    }

    return NextResponse.json(response)

  } catch (error) {
    console.error('Dream seed error:', error)
    return NextResponse.json(
      { 
        error: 'Failed to process dream seed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}