# LUKHΛS AI Web Studio - Consolidated Development

## 🎯 Project Status: IN DEVELOPMENT

This is the **single consolidated workspace** for LUKHΛS A1 AI Web Studio development, bringing together all scattered components into one organized location.

## 📁 Current Architecture

### Next.js App Router Structure
```
lukhas-ai-web-studio/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with fonts & metadata
│   └── page.tsx           # Home page with quote animation
├── src/
│   ├── components/
│   │   └── marketing/
│   │       ├── QuoteRotator.tsx     # Character-by-character animation
│   │       └── NeuralBackground.tsx # Progressive SVG→Canvas→WebGL
│   ├── lib/
│   │   └── state/
│   │       └── appStateMachine.ts   # XState user journey
│   ├── hooks/
│   │   └── useAppStateMachine.ts    # State machine React hook  
│   └── styles/
│       └── globals.css              # Tailwind + design system
├── public/
│   └── content/
│       └── quotes.en.json          # Quote data with priority system
├── package.json                    # Dependencies & scripts
├── next.config.js                  # Next.js configuration
├── tailwind.config.js              # Design system tokens
├── tsconfig.json                   # TypeScript configuration  
└── index.html                      # Legacy implementation (reference)
```

## 🚀 Key Features Consolidated

### ✅ Completed Components
- **Progressive Neural Background**: SVG baseline → Canvas mid-tier → WebGL high-end
- **Quote Rotator**: Character-by-character animation with priority system
- **State Machine**: XState-based user journey (BOOT→QUOTE_IN→CONSENT_PENDING→MARKETING_MODE→STUDIO)
- **Performance Budgets**: LCP<2.5s, CLS<0.1, TBT<200ms monitoring
- **Accessibility**: WCAG 2.2 compliance with reduced motion support
- **Privacy-First**: Nordic cookies with EU defaults

### 🔧 Technology Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS + CSS Variables
- **Animation**: Framer Motion
- **State**: XState v5 + @xstate/react
- **Icons**: Lucide React
- **Performance**: Built-in Next.js optimizations

## 🛠 Development Setup

### Prerequisites
- Node.js ≥18.0.0
- pnpm/npm/yarn

### Install Dependencies
```bash
cd /Users/agi_dev/ztudio-workspace/lukhas-ai-web-studio
npm install
```

### Run Development Server
```bash
npm run dev
# Opens http://localhost:3000
```

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - TypeScript type checking

## 🎨 Design System

### Color Palette
```css
/* Dark Theme */
--color-background: #0a0c14
--color-surface: #111318
--color-text-primary: #EAECEF
--color-accent-primary: #3a64ff
```

### Typography
- **Headers**: Poppins (100-900)
- **Body**: Inter (system fallback)
- **Code**: JetBrains Mono

## 🧠 State Machine Flow
```
BOOT → QUOTE_IN → CONSENT_PENDING → MARKETING_MODE → LOGIN_FLOW → ROUTE_DECISION
                      ↓
                STUDIO_DEFAULT_PRESET / STUDIO_USER_PRESET
```

## 📋 Migration Notes

### Components Consolidated From:
- `/Users/agi_dev/Downloads/LukhasStudioWebCollection/` → `src/components/`
- Scattered TypeScript files → Single workspace structure
- Multiple implementations → One authoritative version

### Legacy Implementation
- `index.html` contains the 760+ line complete working implementation
- Available as reference for V2 dock + Nordic cookies integration
- Fully functional standalone version

## 🎯 Next Development Steps

1. **Install Dependencies**: Run `npm install` to resolve TypeScript errors
2. **Component Integration**: Connect React components with legacy HTML features
3. **V2 Dock Integration**: Port dock layout from HTML to React components
4. **Nordic Cookies**: Implement privacy-first consent system
5. **Studio Routing**: Complete state machine implementation
6. **Performance Optimization**: Implement monitoring and budgets
7. **Testing**: Unit tests for critical components

## 🔍 File Status

### ✅ Ready
- Quote data (`quotes.en.json`)
- Configuration files (`package.json`, `next.config.js`, `tailwind.config.js`)
- TypeScript setup (`tsconfig.json`)

### 🚧 Needs Dependencies
- React components (missing `react`, `framer-motion`, `xstate`)
- Resolved after `npm install`

### 📋 Reference
- `index.html` - Complete working implementation
- Legacy assets in various directories (archived)

---

**Status**: Single workspace established ✅  
**Next Action**: Run `npm install` to resolve dependencies and continue development  
**Working Directory**: `/Users/agi_dev/ztudio-workspace/lukhas-ai-web-studio/`
