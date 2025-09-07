import { Product, SocialLink, NavLink } from '@/types';

export const PRODUCTS: Product[] = [
  {
    name: "LUKHAS Studio",
    desc: "Consciousness-aware workspace where AI understands context, anticipates needs, and adapts to your creative patterns through the Dream Star framework.",
    href: "/studio"
  },
  {
    name: "Identity Star Protection",
    desc: "Quantum-inspired identity security using the Identity Star (⚛️) - decentralized authentication that protects your digital consciousness signature.",
    href: "https://lucas.id"
  },
  {
    name: "Bio Star Adaptation",
    desc: "Emotional AI that reads your mood, adapts to stress patterns, and provides consciousness-level empathy through Bio Star (🌱) technology.",
    href: "/bio"
  },
  {
    name: "Dream Star Engine",
    desc: "Creative problem-solving through controlled exploration and parallel realities - the Dream Star (🌙) generates innovative solutions safely.",
    href: "/dream"
  },
  {
    name: "Guardian Star Oversight",
    desc: "Ethical consciousness protection that ensures AI alignment with human values through advanced Guardian Star (🛡️) safeguards.",
    href: "/guardian"
  },
  {
    name: "Memory Star Context",
    desc: "Persistent awareness across sessions with fold-based memory that maintains context and learns from every interaction through Memory Star (✦).",
    href: "/memory"
  }
];

export const SOCIAL_LINKS: SocialLink[] = [
  {
    name: "Instagram",
    icon: "ig.svg",
    href: "https://instagram.com/lukhas.ai"
  },
  {
    name: "X",
    icon: "x.svg", 
    href: "https://x.com/Lukhas_ai"
  },
  {
    name: "GitHub",
    icon: "github.svg",
    href: "https://github.com/LukhasAI"
  }
];

export const FOOTER_LINKS: NavLink[] = [
  { label: "Studio", href: "/studio" },
  { label: "ΛiD", href: "https://lucas.id" },
  { label: "Wallet", href: "/wallet" },
  { label: "Privacy", href: "/privacy" },
  { label: "Legal", href: "/legal" }
];

export const VISION_POINTS = [
  "Unified input adapts to chat, code, edit, and command.",
  "Context area becomes canvas, preview, player, dashboard, or browser.",
  "Sidebars and widgets appear only when needed.",
  "Privacy-first with explicit consent & least privilege."
];

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536
} as const;

export const STUDIO_SHORTCUTS = {
  toggleFullscreen: 'Space',
  commandPalette: 'CmdOrCtrl+K',
  switchMode: 'CmdOrCtrl+1..4',
  toggleLeftSidebar: 'CmdOrCtrl+[',
  toggleRightSidebar: 'CmdOrCtrl+]'
} as const;