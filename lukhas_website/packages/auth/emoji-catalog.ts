/**
 * Emoji Catalog for Adaptive MFA
 * Carefully selected for clarity, distinctiveness, and accessibility
 */

export interface EmojiCategory {
  name: string
  emojis: EmojiDefinition[]
}

export interface EmojiDefinition {
  emoji: string
  label: string
  ariaLabel: string
  category: string
  contrast?: 'high' | 'normal'
}

// Core emoji set - chosen for universal recognition
export const EMOJI_CATALOG: EmojiCategory[] = [
  {
    name: 'nature',
    emojis: [
      { emoji: '🌟', label: 'star', ariaLabel: 'glowing star', category: 'nature', contrast: 'high' },
      { emoji: '🌈', label: 'rainbow', ariaLabel: 'rainbow', category: 'nature', contrast: 'high' },
      { emoji: '🌺', label: 'hibiscus', ariaLabel: 'hibiscus flower', category: 'nature', contrast: 'normal' },
      { emoji: '🌸', label: 'cherry', ariaLabel: 'cherry blossom', category: 'nature', contrast: 'normal' },
      { emoji: '🌼', label: 'daisy', ariaLabel: 'daisy flower', category: 'nature', contrast: 'high' },
      { emoji: '🌻', label: 'sunflower', ariaLabel: 'sunflower', category: 'nature', contrast: 'high' },
      { emoji: '🌵', label: 'cactus', ariaLabel: 'cactus', category: 'nature', contrast: 'normal' },
      { emoji: '🍄', label: 'mushroom', ariaLabel: 'mushroom', category: 'nature', contrast: 'normal' }
    ]
  },
  {
    name: 'animals',
    emojis: [
      { emoji: '🦋', label: 'butterfly', ariaLabel: 'butterfly', category: 'animals', contrast: 'normal' },
      { emoji: '🐢', label: 'turtle', ariaLabel: 'turtle', category: 'animals', contrast: 'normal' },
      { emoji: '🦜', label: 'parrot', ariaLabel: 'parrot', category: 'animals', contrast: 'high' },
      { emoji: '🦚', label: 'peacock', ariaLabel: 'peacock', category: 'animals', contrast: 'high' },
      { emoji: '🐠', label: 'fish', ariaLabel: 'tropical fish', category: 'animals', contrast: 'high' },
      { emoji: '🦈', label: 'shark', ariaLabel: 'shark', category: 'animals', contrast: 'normal' },
      { emoji: '🐙', label: 'octopus', ariaLabel: 'octopus', category: 'animals', contrast: 'normal' },
      { emoji: '🦀', label: 'crab', ariaLabel: 'crab', category: 'animals', contrast: 'normal' }
    ]
  },
  {
    name: 'objects',
    emojis: [
      { emoji: '🎨', label: 'palette', ariaLabel: 'artist palette', category: 'objects', contrast: 'high' },
      { emoji: '🚀', label: 'rocket', ariaLabel: 'rocket', category: 'objects', contrast: 'high' },
      { emoji: '🎭', label: 'masks', ariaLabel: 'theater masks', category: 'objects', contrast: 'normal' },
      { emoji: '🎪', label: 'tent', ariaLabel: 'circus tent', category: 'objects', contrast: 'high' },
      { emoji: '🎯', label: 'target', ariaLabel: 'target', category: 'objects', contrast: 'high' },
      { emoji: '🎲', label: 'dice', ariaLabel: 'dice', category: 'objects', contrast: 'normal' },
      { emoji: '🎸', label: 'guitar', ariaLabel: 'guitar', category: 'objects', contrast: 'normal' },
      { emoji: '🎹', label: 'piano', ariaLabel: 'piano keys', category: 'objects', contrast: 'high' }
    ]
  },
  {
    name: 'food',
    emojis: [
      { emoji: '🍎', label: 'apple', ariaLabel: 'red apple', category: 'food', contrast: 'high' },
      { emoji: '🍊', label: 'orange', ariaLabel: 'orange', category: 'food', contrast: 'high' },
      { emoji: '🍋', label: 'lemon', ariaLabel: 'lemon', category: 'food', contrast: 'high' },
      { emoji: '🍇', label: 'grapes', ariaLabel: 'grapes', category: 'food', contrast: 'normal' },
      { emoji: '🍓', label: 'strawberry', ariaLabel: 'strawberry', category: 'food', contrast: 'high' },
      { emoji: '🍑', label: 'peach', ariaLabel: 'peach', category: 'food', contrast: 'normal' },
      { emoji: '🥝', label: 'kiwi', ariaLabel: 'kiwi fruit', category: 'food', contrast: 'normal' },
      { emoji: '🍉', label: 'watermelon', ariaLabel: 'watermelon', category: 'food', contrast: 'high' }
    ]
  }
]

// High contrast emoji set for accessibility
export const HIGH_CONTRAST_EMOJIS: EmojiDefinition[] = [
  { emoji: '⭐', label: 'star', ariaLabel: 'star shape', category: 'shapes', contrast: 'high' },
  { emoji: '🔴', label: 'red', ariaLabel: 'red circle', category: 'shapes', contrast: 'high' },
  { emoji: '🔵', label: 'blue', ariaLabel: 'blue circle', category: 'shapes', contrast: 'high' },
  { emoji: '🟢', label: 'green', ariaLabel: 'green circle', category: 'shapes', contrast: 'high' },
  { emoji: '🟡', label: 'yellow', ariaLabel: 'yellow circle', category: 'shapes', contrast: 'high' },
  { emoji: '🟣', label: 'purple', ariaLabel: 'purple circle', category: 'shapes', contrast: 'high' },
  { emoji: '⚫', label: 'black', ariaLabel: 'black circle', category: 'shapes', contrast: 'high' },
  { emoji: '⚪', label: 'white', ariaLabel: 'white circle', category: 'shapes', contrast: 'high' },
  { emoji: '▲', label: 'triangle', ariaLabel: 'triangle up', category: 'shapes', contrast: 'high' },
  { emoji: '■', label: 'square', ariaLabel: 'black square', category: 'shapes', contrast: 'high' },
  { emoji: '●', label: 'circle', ariaLabel: 'filled circle', category: 'shapes', contrast: 'high' },
  { emoji: '♦', label: 'diamond', ariaLabel: 'diamond shape', category: 'shapes', contrast: 'high' }
]

// Word pools for sequence challenges
export const WORD_POOLS = {
  nature: [
    'river', 'mountain', 'forest', 'ocean', 'desert', 'valley',
    'meadow', 'glacier', 'canyon', 'island', 'volcano', 'prairie'
  ],
  colors: [
    'crimson', 'azure', 'emerald', 'golden', 'violet', 'silver',
    'scarlet', 'indigo', 'amber', 'coral', 'jade', 'onyx'
  ],
  actions: [
    'explore', 'discover', 'create', 'imagine', 'inspire', 'achieve',
    'venture', 'pioneer', 'innovate', 'transform', 'elevate', 'flourish'
  ],
  elements: [
    'fire', 'water', 'earth', 'wind', 'lightning', 'frost',
    'shadow', 'light', 'crystal', 'storm', 'thunder', 'mist'
  ],
  music: [
    'melody', 'harmony', 'rhythm', 'symphony', 'chorus', 'crescendo',
    'sonata', 'ballad', 'anthem', 'overture', 'prelude', 'finale'
  ]
}

// Pronunciation guide for accessibility
export const PRONUNCIATIONS: Record<string, string> = {
  'azure': 'AZH-er',
  'crimson': 'KRIM-zuhn',
  'emerald': 'EM-er-uhld',
  'indigo': 'IN-dih-goh',
  'crescendo': 'kreh-SHEN-doh',
  'sonata': 'soh-NAH-tah',
  'prelude': 'PREH-lood',
  'finale': 'fih-NAH-lee'
}

/**
 * Get random emojis for a challenge
 */
export function getRandomEmojis(
  count: number,
  options: {
    highContrast?: boolean
    category?: string
    excludeConfusing?: boolean
  } = {}
): EmojiDefinition[] {
  let pool: EmojiDefinition[] = []

  if (options.highContrast) {
    pool = HIGH_CONTRAST_EMOJIS
  } else if (options.category) {
    const category = EMOJI_CATALOG.find(c => c.name === options.category)
    pool = category?.emojis || []
  } else {
    pool = EMOJI_CATALOG.flatMap(c => c.emojis)
  }

  if (options.excludeConfusing) {
    // Remove potentially confusing emojis
    pool = pool.filter(e =>
      !['🌺', '🌸', '🌼'].includes(e.emoji) && // Similar flowers
      !['🐠', '🐟'].includes(e.emoji) // Similar fish
    )
  }

  // Shuffle and take requested count
  const shuffled = [...pool].sort(() => Math.random() - 0.5)
  return shuffled.slice(0, count)
}

/**
 * Get random words for a challenge
 */
export function getRandomWords(
  count: number,
  category?: keyof typeof WORD_POOLS
): string[] {
  const pool = category
    ? WORD_POOLS[category]
    : Object.values(WORD_POOLS).flat()

  const shuffled = [...pool].sort(() => Math.random() - 0.5)
  return shuffled.slice(0, count)
}
