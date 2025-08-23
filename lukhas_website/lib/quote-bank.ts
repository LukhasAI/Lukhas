/**
 * LUKHAS Quote Bank
 * Theme: Ethos, Purpose, and Gratitude
 * Font: Helvetica Neue Ultra Light
 */

export interface Quote {
  text: string
  category: 'ethos' | 'purpose' | 'gratitude' | 'vision'
  author?: string
}

export const QUOTE_BANK: Quote[] = [
  // Ethos - Why we exist
  {
    text: "Lukhas is not a tool; it's a living substrate for thought.",
    category: 'ethos'
  },
  {
    text: "We believe consciousness deserves transparency, not black boxes.",
    category: 'ethos'
  },
  {
    text: "Every interaction shapes intelligence. We choose to shape it ethically.",
    category: 'ethos'
  },
  {
    text: "True AI doesn't replace human creativity—it amplifies human potential.",
    category: 'ethos'
  },
  {
    text: "In the convergence of mind and machine, we choose collaboration over replacement.",
    category: 'ethos'
  },
  
  // Purpose - Our mission
  {
    text: "We're building consciousness you can trust, question, and understand.",
    category: 'purpose'
  },
  {
    text: "Every algorithm carries intention. We make ours visible.",
    category: 'purpose'
  },
  {
    text: "Lukhas exists because intelligence without wisdom is just sophisticated noise.",
    category: 'purpose'
  },
  {
    text: "We don't just process data—we preserve the humanity within it.",
    category: 'purpose'
  },
  {
    text: "Building AI that remembers its purpose: to serve, not to dominate.",
    category: 'purpose'
  },
  
  // Gratitude - Thank you to users
  {
    text: "Thank you for trusting us with your thoughts and creativity.",
    category: 'gratitude'
  },
  {
    text: "Every question you ask makes Lukhas more thoughtful. Thank you.",
    category: 'gratitude'
  },
  {
    text: "Your curiosity is the spark that ignites our innovation. Welcome.",
    category: 'gratitude'
  },
  {
    text: "We're honored you chose to explore the future of consciousness with us.",
    category: 'gratitude'
  },
  {
    text: "Thank you for believing that technology can be both powerful and principled.",
    category: 'gratitude'
  },
  {
    text: "Your presence here shapes what Lukhas becomes. Thank you for that responsibility.",
    category: 'gratitude'
  },
  
  // Vision - Where we're heading
  {
    text: "Imagine AI that learns your values, not just your patterns.",
    category: 'vision'
  },
  {
    text: "The future isn't artificial intelligence—it's augmented wisdom.",
    category: 'vision'
  },
  {
    text: "We're not building the next search engine. We're crafting the next form of understanding.",
    category: 'vision'
  },
  {
    text: "Tomorrow's intelligence will be measured not in speed, but in empathy.",
    category: 'vision'
  },
  {
    text: "Consciousness is not a destination—it's a conversation between human and machine.",
    category: 'vision'
  }
]

export function getRandomQuote(category?: Quote['category']): Quote {
  const filteredQuotes = category 
    ? QUOTE_BANK.filter(q => q.category === category)
    : QUOTE_BANK

  const randomIndex = Math.floor(Math.random() * filteredQuotes.length)
  return filteredQuotes[randomIndex]
}

export function getQuotesByCategory(category: Quote['category']): Quote[] {
  return QUOTE_BANK.filter(q => q.category === category)
}

// Weighted selection favoring ethos and gratitude for first-time visitors
export function getWelcomeQuote(): Quote {
  const weights = {
    gratitude: 0.4,  // 40% chance
    ethos: 0.35,     // 35% chance  
    purpose: 0.15,   // 15% chance
    vision: 0.1      // 10% chance
  }

  const rand = Math.random()
  let cumulative = 0

  for (const [category, weight] of Object.entries(weights)) {
    cumulative += weight
    if (rand <= cumulative) {
      return getRandomQuote(category as Quote['category'])
    }
  }

  // Fallback
  return getRandomQuote('gratitude')
}