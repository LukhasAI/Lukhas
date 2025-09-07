import { Product, SocialLink, NavLink } from '@/types';

export const PRODUCTS: Product[] = [
  {
    name: "LUKHAS Studio",
    desc: "An experimental workspace exploring adaptive AI that aims to learn and evolve with your creative process.",
    href: "/studio"
  },
  {
    name: "LUKHAS Identity",
    desc: "Working toward secure, decentralized identity solutions that give you greater control of your digital presence and privacy.",
    href: "https://lucas.id"
  },
  {
    name: "LUKHAS Wallet",
    desc: "Exploring intelligent asset management with AI-driven insights and integration across our developing ecosystem.",
    href: "/wallet"
  },
  {
    name: "LUKHAS Connect",
    desc: "Developing communication tools that explore consciousness-aware messaging and collaboration approaches.",
    href: "/connect"
  },
  {
    name: "NIAS Intelligence",
    desc: "Research into ethical AI networking approaches that aim to connect conscious systems while respecting user autonomy.",
    href: "/nias"
  }
];

export const SOCIAL_LINKS: SocialLink[] = [
  {
    name: "Instagram",
    icon: "ig.svg",
    href: "#"
  },
  {
    name: "X",
    icon: "x.svg", 
    href: "#"
  },
  {
    name: "Discord",
    icon: "discord.svg",
    href: "#"
  },
  {
    name: "WhatsApp",
    icon: "whatsapp.svg",
    href: "#"
  }
];

export const FOOTER_LINKS: NavLink[] = [
  { label: "Studio", href: "/studio" },
  { label: "Lucas ID", href: "https://lucas.id" },
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